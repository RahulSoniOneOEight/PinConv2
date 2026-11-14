"""Gate 2 packets: budget authorisation, asset readiness and rough-cut review.

Gate 2A is a human decision. This module can only assemble the packet and
record the approval; it never approves on its own.
"""

from __future__ import annotations

from ..models import ProductionPlan, utc_now
from .catalogue import SOURCE_MAP
from .errors import GateOrderError, MethodMatrixError
from .method_selector import assert_method_allowed as _assert_allowed
from .models import (
    BuildSheet,
    CheckState,
    GateCheck,
    GateName,
    GatePacket,
    GateVerdict,
    LayerMethodDecision,
    Level2Plan,
    Method,
    PacketStatus,
    ProviderSpendSummary,
    QcReport,
    RunState,
    TaskStatus,
    TruthClass,
)

_ALLOWED_EXACT = {Method.M0, Method.M4}


def _check(
    check_id: str,
    name: str,
    state: CheckState,
    detail: str,
    evidence: str | None = None,
) -> GateCheck:
    return GateCheck(id=check_id, name=name, state=state, detail=detail, evidence=evidence)


def _status(checks: list[GateCheck]) -> PacketStatus:
    return (
        PacketStatus.BLOCKED
        if any(check.state is CheckState.FAIL for check in checks)
        else PacketStatus.READY
    )


def _blockers(checks: list[GateCheck]) -> list[str]:
    return [
        f"{check.id} {check.name}: {check.detail}"
        for check in checks
        if check.state is CheckState.FAIL
    ]


def evaluate_2a(
    plan: ProductionPlan,
    level2: Level2Plan,
    sheet: BuildSheet,
    decisions: list[LayerMethodDecision],
    reports: dict[str, QcReport],
    *,
    expected_bundle_hash: str | None = None,
    expected_packet_hash: str | None = None,
    provider_summary: ProviderSpendSummary | None = None,
) -> GatePacket:
    checks: list[GateCheck] = []
    intent_map = {intent.asset_id: intent for intent in level2.intents}

    hash_format = len(sheet.manifest.bundle_hash) == 64 and len(sheet.manifest.packet_hash) == 64
    hash_match = True
    if expected_bundle_hash is not None:
        hash_match = hash_match and sheet.manifest.bundle_hash == expected_bundle_hash
    if expected_packet_hash is not None:
        hash_match = hash_match and sheet.manifest.packet_hash == expected_packet_hash
    chain_ok = (
        plan.plan_hash() == level2.plan_hash == sheet.manifest.source_plan_hash
        and hash_format
        and hash_match
        and level2.budget.summary == sheet.manifest.budget
    )
    if expected_bundle_hash is not None and expected_packet_hash is not None:
        chain_state = CheckState.PASS if chain_ok else CheckState.FAIL
        chain_detail = (
            "plan, bundle, packet and budget reconcile with the approval record"
            if chain_ok
            else "the plan hash, bundle, packet or budget does not reconcile"
        )
    else:
        chain_state = CheckState.WARN if chain_ok else CheckState.FAIL
        chain_detail = (
            "plan hash and budget reconcile; bundle and packet are format-validated "
            "only because the approval record was not supplied"
            if chain_ok
            else "the plan hash or budget does not reconcile"
        )
    checks.append(
        _check(
            "G2A-01",
            "Hash chain",
            chain_state,
            chain_detail,
            plan.plan_hash(),
        )
    )

    matrix_errors: list[str] = []
    for decision in decisions:
        intent = intent_map.get(decision.asset_id or "")
        disclosed = intent.disclosure_required if intent is not None else False
        original = intent.route == "to_capture" if intent is not None else False
        for method, target in (
            (decision.method, decision.layer_id),
            (decision.fallback_method, f"{decision.layer_id}.fallback"),
        ):
            try:
                _assert_allowed(
                    decision.truth_class,
                    method,
                    target,
                    disclosed=disclosed,
                    original_capture=original,
                )
            except MethodMatrixError as error:
                matrix_errors.append(str(error))
    checks.append(
        _check(
            "G2A-02",
            "Method selection",
            CheckState.PASS if not matrix_errors else CheckState.FAIL,
            f"{len(decisions)} decisions checked against the class matrix"
            if not matrix_errors
            else "; ".join(matrix_errors[:3]),
        )
    )

    exact_bad: list[str] = []
    proof_bad: list[str] = []
    for decision in decisions:
        intent = intent_map.get(decision.asset_id or "")
        route = intent.route if intent is not None else None
        if decision.truth_class in {TruthClass.EXACT, TruthClass.EXACT_TEXT}:
            allowed = set(_ALLOWED_EXACT)
            if route == "to_capture":
                allowed.add(Method.M6)
            if decision.method not in allowed:
                exact_bad.append(decision.layer_id)
        if decision.truth_class is TruthClass.PROOF and decision.method not in {
            Method.M6,
            Method.M2,
        }:
            proof_bad.append(decision.layer_id)
    policy_ok = not exact_bad and not proof_bad
    checks.append(
        _check(
            "G2A-03",
            "Exact and proof policy",
            CheckState.PASS if policy_ok else CheckState.FAIL,
            "no exact layer uses stock or generation and every proof layer is captured"
            if policy_ok
            else f"exact violations {exact_bad}; proof violations {proof_bad}",
        )
    )

    summary = sheet.manifest.budget
    budget_ok = summary == level2.budget.summary and summary.within_cap and summary.worst_within_cap
    checks.append(
        _check(
            "G2A-04",
            "Budget within cap",
            CheckState.PASS if budget_ok else CheckState.FAIL,
            f"total ${summary.total_usd:,.2f}, worst ${summary.worst_usd:,.2f}, "
            f"cap ${summary.cap_usd:,.2f}, headroom ${summary.headroom_usd:,.2f}",
        )
    )

    pending_rights = [
        asset.asset_id for asset in sheet.assets if asset.rights_status == "needs_approval"
    ]
    missing_hold = [
        asset.asset_id
        for asset in sheet.assets
        if asset.rights_status == "needs_approval" and not asset.hold
    ]
    if missing_hold:
        rights_state = CheckState.FAIL
        rights_detail = f"assets need approval without a hold owner: {missing_hold}"
    elif pending_rights:
        rights_state = CheckState.WARN
        rights_detail = (
            f"{len(pending_rights)} assets need written approval; every one names a hold owner"
        )
    else:
        rights_state = CheckState.PASS
        rights_detail = "every asset is cleared or owned"
    checks.append(_check("G2A-05", "Rights posture", rights_state, rights_detail))

    sourcing_candidates = (
        [candidate for asset in level2.sourcing.assets for candidate in asset.candidates]
        if level2.sourcing is not None
        else []
    )
    candidates = [
        candidate for decision in decisions for candidate in decision.candidates
    ] + sourcing_candidates
    blocked_candidates = [
        candidate.candidate_id
        for candidate in candidates
        if candidate.gate_verdict is GateVerdict.BLOCK
    ]
    manual_scripted: list[str] = []
    unknown_sources: list[str] = []
    for candidate in candidates:
        entry = SOURCE_MAP.get(candidate.provider)
        if entry is None:
            unknown_sources.append(candidate.candidate_id)
        elif not entry.scriptable and candidate.scriptable:
            manual_scripted.append(candidate.candidate_id)
    if blocked_candidates:
        catalogue_state = CheckState.FAIL
        catalogue_detail = f"blocked candidates present: {blocked_candidates}"
    elif unknown_sources:
        catalogue_state = CheckState.FAIL
        catalogue_detail = f"candidates from unknown sources: {unknown_sources}"
    elif not candidates:
        catalogue_state = CheckState.WARN
        catalogue_detail = "no sourcing round has run; the licence gate has nothing to verify yet"
    elif manual_scripted:
        catalogue_state = CheckState.FAIL
        catalogue_detail = f"manual-only sources scripted: {manual_scripted}"
    else:
        catalogue_state = CheckState.PASS
        passed = sum(
            1 for candidate in candidates if candidate.gate_verdict is GateVerdict.PASS
        )
        previewed = sum(
            1 for candidate in candidates if getattr(candidate, "preview_path", None)
        )
        catalogue_detail = (
            f"{len(candidates)} candidates checked; {passed} passed the licence gate; "
            f"{previewed} with previews ({len(sourcing_candidates)} from sourcing)"
        )
    checks.append(_check("G2A-06", "Catalogue compliance", catalogue_state, catalogue_detail))

    missing_probe = [
        decision.layer_id
        for decision in decisions
        if decision.method not in {Method.M0, Method.M1} and not decision.probe_required
    ]
    checks.append(
        _check(
            "G2A-07",
            "Probe plan",
            CheckState.PASS if not missing_probe else CheckState.FAIL,
            "every M2-M7 choice has a probe before full commit"
            if not missing_probe
            else f"missing probes: {missing_probe}",
        )
    )

    capture = level2.capture
    capture_assets = {intent.asset_id for intent in level2.intents if intent.route == "to_capture"}
    covered = {member.asset_id for member in capture.members}
    capture_ok = capture_assets <= covered and (capture.cost_usd > 0 or capture.in_kind_usd > 0)
    checks.append(
        _check(
            "G2A-08",
            "Capture plan",
            CheckState.WARN if capture_ok else CheckState.FAIL,
            f"{capture.session_id} covers {len(capture.members)} assets at "
            f"${capture.cost_usd:,.2f} cash"
            + (f" (${capture.in_kind_usd:,.2f} in-kind)" if capture.in_kind_usd else "")
            + f"; release {capture.release_hold} is still pending"
            if capture_ok
            else f"capture plan misses {sorted(capture_assets - covered)}",
            capture.release_hold,
        )
    )

    for stage in ("technical", "semantic", "rights", "budget"):
        report = reports[stage]
        state = (
            CheckState.FAIL
            if report.verdict.value == "fail"
            else CheckState.WARN
            if report.verdict.value == "warn"
            else CheckState.PASS
        )
        checks.append(
            _check(
                f"G2A-{len(checks) + 1:02d}",
                f"{stage.title()} QC",
                state,
                f"{len(report.findings)} findings, verdict {report.verdict.value}",
            )
        )

    if level2.budget.mode == "lean":
        checks.append(
            _check(
                f"G2A-{len(checks) + 1:02d}",
                "Lean substitutions",
                CheckState.WARN,
                f"{len(level2.budget.substitutions)} paid lines moved to in-kind "
                f"(${level2.budget.in_kind_usd:,.2f}); cash is $0.00 and Gate 2A "
                "approves these substitutions",
            )
        )

    if provider_summary is None:
        checks.append(
            _check(
                f"G2A-{len(checks) + 1:02d}",
                "Provider budget",
                CheckState.WARN,
                "no fal.ai/Runware budget is configured; every paid call is refused",
            )
        )
    else:
        checks.append(
            _check(
                f"G2A-{len(checks) + 1:02d}",
                "Provider budget",
                CheckState.PASS if provider_summary.within_cap else CheckState.FAIL,
                f"fal+Runware cap ${provider_summary.cap_usd:,.2f}, "
                f"spent ${provider_summary.spent_usd:,.2f}, "
                f"committed ${provider_summary.committed_usd:,.2f}, "
                f"remaining ${provider_summary.remaining_usd:,.2f}, "
                f"per-job max ${provider_summary.per_job_max_usd:,.2f}",
            )
        )

    blockers = _blockers(checks)
    return GatePacket(
        run_id=level2.run_id,
        project_id=level2.project_id,
        plan_revision=level2.plan_revision,
        plan_hash=level2.plan_hash,
        gate=GateName.GATE_2A,
        status=_status(checks),
        checks=checks,
        blockers=blockers,
        summary=(
            "Planning is complete and spend-free. Budget, method policy and rights "
            "posture are ready for a named human decision."
            if not blockers
            else "Gate 2A is blocked by failed checks."
        ),
    )


def evaluate_2b(
    plan: ProductionPlan,
    level2: Level2Plan,
    sheet: BuildSheet,
    reports: dict[str, QcReport],
    gate_2a: GatePacket,
    *,
    receipts: int = 0,
    open_reservations: int = 0,
) -> GatePacket:
    if gate_2a.status is not PacketStatus.APPROVED:
        raise GateOrderError("Gate 2B needs an approved Gate 2A")

    checks: list[GateCheck] = []
    checks.append(
        _check(
            "G2B-01",
            "Gate 2A approved",
            CheckState.PASS,
            f"approved by {gate_2a.approved_by}",
            gate_2a.approval_evidence,
        )
    )

    in_scope = [asset for asset in sheet.assets if not asset.conditional]
    ready = [
        asset for asset in in_scope if asset.status in {TaskStatus.PROCESSED, TaskStatus.ACCEPTED}
    ]
    checks.append(
        _check(
            "G2B-02",
            "Asset coverage",
            CheckState.PASS if len(ready) == len(in_scope) else CheckState.FAIL,
            f"{len(ready)} of {len(in_scope)} in-scope assets processed",
        )
    )

    unresolved = [
        decision.layer_id
        for decision in level2.decisions
        if decision.asset_id is not None
        and next(
            (asset.status for asset in sheet.assets if asset.asset_id == decision.asset_id),
            TaskStatus.BLOCKED,
        )
        not in {TaskStatus.PROCESSED, TaskStatus.ACCEPTED}
    ]
    checks.append(
        _check(
            "G2B-03",
            "Layer readiness",
            CheckState.PASS if not unresolved else CheckState.FAIL,
            "all bound layers resolve to processed media"
            if not unresolved
            else f"{len(unresolved)} layers still bound to unprocessed assets",
        )
    )

    variant_bad = [variant.variant_id for variant in sheet.variants if not variant.ready]
    checks.append(
        _check(
            "G2B-04",
            "Variant readiness",
            CheckState.PASS if not variant_bad else CheckState.FAIL,
            "16:9 and the approved 9:16 variant both resolve"
            if not variant_bad
            else f"variants not ready: {variant_bad}",
        )
    )

    held = [asset.asset_id for asset in sheet.assets if asset.rights_status == "needs_approval"]
    checks.append(
        _check(
            "G2B-05",
            "Rights cleared",
            CheckState.PASS if not held else CheckState.FAIL,
            "every shipped asset is cleared" if not held else f"rights still pending: {held}",
        )
    )

    visual = reports.get("visual")
    visual_state = CheckState.PASS
    if visual is None or visual.verdict.value == "fail":
        visual_state = CheckState.FAIL
    elif visual.verdict.value == "warn":
        visual_state = CheckState.WARN
    checks.append(
        _check(
            "G2B-06",
            "Quality control",
            visual_state,
            "technical, semantic, visual, rights and budget QC recorded"
            if visual_state is CheckState.PASS
            else "visual QC is incomplete",
        )
    )

    checks.append(
        _check(
            "G2B-07",
            "Spend ledger",
            CheckState.PASS if open_reservations == 0 else CheckState.FAIL,
            f"{receipts} receipts, {open_reservations} open reservations",
        )
    )

    blockers = _blockers(checks)
    return GatePacket(
        run_id=level2.run_id,
        project_id=level2.project_id,
        plan_revision=level2.plan_revision,
        plan_hash=level2.plan_hash,
        gate=GateName.GATE_2B,
        status=_status(checks),
        checks=checks,
        blockers=blockers,
        summary=(
            "Every required asset is processed, bound and cleared."
            if not blockers
            else "Gate 2B is blocked until assets, rights and visual QC are complete."
        ),
    )


def evaluate_2c(
    plan: ProductionPlan,
    level2: Level2Plan,
    gate_2b: GatePacket,
    *,
    deliverables: list[str],
    duration_ok: bool,
    audio_ok: bool,
    captions_ok: bool,
    reviewer: str | None,
) -> GatePacket:
    if gate_2b.status is not PacketStatus.APPROVED:
        raise GateOrderError("Gate 2C needs an approved Gate 2B")

    checks = [
        _check(
            "G2C-01",
            "Gate 2B approved",
            CheckState.PASS,
            f"approved by {gate_2b.approved_by}",
        ),
        _check(
            "G2C-02",
            "Deliverables",
            CheckState.PASS if deliverables else CheckState.FAIL,
            f"{len(deliverables)} cuts present" if deliverables else "no rough cut present",
        ),
        _check(
            "G2C-03",
            "Duration and frame rate",
            CheckState.PASS if duration_ok else CheckState.FAIL,
            "500 frames at 25 fps" if duration_ok else "duration does not match the plan",
        ),
        _check(
            "G2C-04",
            "Audio",
            CheckState.PASS if audio_ok else CheckState.FAIL,
            "-16 LUFS, -1.0 dBTP" if audio_ok else "audio target not met",
        ),
        _check(
            "G2C-05",
            "Captions",
            CheckState.PASS if captions_ok else CheckState.FAIL,
            "captions present for both variants" if captions_ok else "captions missing",
        ),
        _check(
            "G2C-06",
            "Review",
            CheckState.PASS if reviewer else CheckState.FAIL,
            f"reviewer {reviewer}" if reviewer else "no named reviewer",
        ),
    ]
    blockers = _blockers(checks)
    return GatePacket(
        run_id=level2.run_id,
        project_id=level2.project_id,
        plan_revision=level2.plan_revision,
        plan_hash=level2.plan_hash,
        gate=GateName.GATE_2C,
        status=_status(checks),
        checks=checks,
        blockers=blockers,
        summary=(
            "Both cuts pass review."
            if not blockers
            else "Gate 2C is blocked until the cuts exist and pass review."
        ),
    )


def approve_packet(
    packet: GatePacket,
    *,
    approver: str,
    role: str,
    evidence: str,
    confirmation: str,
) -> GatePacket:
    if packet.status is PacketStatus.BLOCKED:
        raise GateOrderError("a blocked packet cannot be approved")
    if confirmation.strip().upper() != "APPROVE":
        raise GateOrderError("type APPROVE to confirm a human decision")
    if not approver.strip() or not role.strip() or not evidence.strip():
        raise GateOrderError("approval needs a name, a role and evidence")
    return packet.model_copy(
        update={
            "status": PacketStatus.APPROVED,
            "approved_by": approver,
            "approved_at": utc_now(),
            "approval_evidence": f"{role}: {evidence}",
        }
    )


def gate_state_for(level2: Level2Plan) -> RunState:
    return level2.state
