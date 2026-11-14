"""Deterministic quality control for a Level 2 build sheet.

These checks do not need media. They verify geometry, timing, bindings, method
policy, rights posture, captions and budget arithmetic. Visual QC runs later,
against processed assets, and is expected to fail until Gate 2A is approved.
"""

from __future__ import annotations

from ..models import ProductionPlan
from .models import (
    AssetIntent,
    BuildSheet,
    CheckState,
    LayerMethodDecision,
    Method,
    QcFinding,
    QcReport,
    QcVerdict,
    TaskStatus,
    TruthClass,
)

_NO_PROBE = {Method.M0, Method.M1}


def _verdict(findings: list[QcFinding]) -> QcVerdict:
    if any(finding.verdict is QcVerdict.FAIL for finding in findings):
        return QcVerdict.FAIL
    if any(finding.verdict is QcVerdict.WARN for finding in findings):
        return QcVerdict.WARN
    return QcVerdict.PASS


def _report(
    stage: str, findings: list[QcFinding], reviewer: str = "code:deterministic"
) -> QcReport:
    if not findings:
        findings = [
            QcFinding(
                id="QC-000",
                stage=stage,
                check="no_findings",
                target="run",
                verdict=QcVerdict.PASS,
                detail="no findings",
            )
        ]
    return QcReport(stage=stage, verdict=_verdict(findings), findings=findings, reviewer=reviewer)


def _finding(
    index: int,
    stage: str,
    check: str,
    target: str,
    verdict: QcVerdict,
    detail: str,
    remediation: str | None = None,
) -> QcFinding:
    return QcFinding(
        id=f"QC-{index:03d}",
        stage=stage,
        check=check,
        target=target,
        verdict=verdict,
        detail=detail,
        remediation=remediation,
    )


def technical_qc(plan: ProductionPlan, sheet: BuildSheet) -> QcReport:
    findings: list[QcFinding] = []
    index = 1

    def add(
        check: str, target: str, verdict: QcVerdict, detail: str, fix: str | None = None
    ) -> None:
        nonlocal index
        findings.append(_finding(index, "technical", check, target, verdict, detail, fix))
        index += 1

    if len(sheet.assets) != len(plan.assets):
        add(
            "asset_coverage",
            "build_sheet",
            QcVerdict.FAIL,
            f"{len(sheet.assets)} asset packages for {len(plan.assets)} approved assets",
        )
    else:
        add("asset_coverage", "build_sheet", QcVerdict.PASS, f"{len(sheet.assets)} assets")

    if len(sheet.shots) != len(plan.shots):
        add("shot_coverage", "build_sheet", QcVerdict.FAIL, "shot count mismatch")

    frame_count = sheet.timeline.frame_count
    if frame_count != plan.deliverable.frame_count:
        add(
            "timeline_length",
            "timeline",
            QcVerdict.FAIL,
            f"{frame_count} frames instead of {plan.deliverable.frame_count}",
        )
    else:
        add("timeline_length", "timeline", QcVerdict.PASS, f"{frame_count} frames")

    for shot in plan.shots:
        duration = shot.end_frame - shot.start_frame
        for layer_id in shot.layer_ids:
            layer = plan.layer_map[layer_id]
            if layer.start_frame < 0 or layer.end_frame > duration:
                add(
                    "layer_in_shot",
                    layer.id,
                    QcVerdict.FAIL,
                    f"{layer.start_frame}–{layer.end_frame} outside {shot.id} (0–{duration})",
                )
            if (
                layer.rect.right > plan.deliverable.width
                or layer.rect.bottom > plan.deliverable.height
            ):
                add(
                    "layer_in_canvas",
                    layer.id,
                    QcVerdict.FAIL,
                    "layer extends past the 16:9 canvas",
                )

    for variant in sheet.variants:
        if len(variant.resolutions) != len(plan.layers):
            add(
                "variant_resolution",
                variant.variant_id,
                QcVerdict.FAIL,
                f"{len(variant.resolutions)} of {len(plan.layers)} layers resolved",
            )
        else:
            add(
                "variant_resolution",
                variant.variant_id,
                QcVerdict.PASS,
                f"all {len(plan.layers)} layers resolved",
            )
        if variant.frame_count != plan.deliverable.frame_count:
            add(
                "variant_length",
                variant.variant_id,
                QcVerdict.FAIL,
                "variant length differs from the master",
            )

    captions = sum(1 for layer in plan.layers if layer.role.value == "caption")
    if captions == 0:
        add("captions", "timeline", QcVerdict.FAIL, "no caption layers")

    summary = sheet.manifest.budget
    if round(summary.subtotal_usd + summary.reserve_usd, 2) != summary.total_usd:
        add("budget_arithmetic", "manifest", QcVerdict.FAIL, "total does not reconcile")

    return _report("technical", findings)


def semantic_qc(
    plan: ProductionPlan,
    decisions: list[LayerMethodDecision],
    intents: list[AssetIntent],
) -> QcReport:
    findings: list[QcFinding] = []
    index = 1

    def add(
        check: str, target: str, verdict: QcVerdict, detail: str, fix: str | None = None
    ) -> None:
        nonlocal index
        findings.append(_finding(index, "semantic", check, target, verdict, detail, fix))
        index += 1

    intent_map = {intent.asset_id: intent for intent in intents}
    for decision in decisions:
        if decision.truth_class in {TruthClass.EXACT, TruthClass.EXACT_TEXT}:
            allowed = {Method.M0, Method.M4}
            intent = intent_map.get(decision.asset_id or "")
            if intent is not None and intent.route == "to_capture":
                allowed.add(Method.M6)
            if decision.method not in allowed:
                add(
                    "exact_method",
                    decision.layer_id,
                    QcVerdict.FAIL,
                    f"exact material used {decision.method.value}",
                )
        if decision.truth_class is TruthClass.PROOF and decision.method not in {
            Method.M6,
            Method.M2,
        }:
            add(
                "proof_method",
                decision.layer_id,
                QcVerdict.FAIL,
                f"proof material used {decision.method.value}",
            )
        if decision.method not in _NO_PROBE and not decision.probe_required:
            add(
                "probe_planned",
                decision.layer_id,
                QcVerdict.FAIL,
                f"{decision.method.value} needs a probe",
            )
        if decision.impact.value in {"high", "medium"} and decision.pick_mode.value != "human":
            add(
                "human_pick",
                decision.layer_id,
                QcVerdict.FAIL,
                "high or medium impact needs a human pick",
            )
        if decision.asset_id is not None:
            intent = intent_map.get(decision.asset_id)
            if (
                intent is not None
                and decision.truth_class is not intent.truth_class
                and not (
                    decision.truth_class is TruthClass.EXACT_TEXT
                    and intent.truth_class is TruthClass.EXACT
                )
            ):
                add(
                    "class_consistency",
                    decision.layer_id,
                    QcVerdict.WARN,
                    f"layer {decision.truth_class.value} vs asset {intent.truth_class.value}",
                )

    for must_have in plan.checks:
        if not must_have.id.startswith("AC-"):
            continue
        for target in must_have.target_ids:
            if target.startswith("AS-") and target not in plan.asset_map:
                add("check_target", must_have.id, QcVerdict.FAIL, f"unknown target {target}")

    for intent in intents:
        if intent.disclosure_required and intent.route != "to_generate":
            add(
                "disclosure",
                intent.asset_id,
                QcVerdict.WARN,
                "disclosure is flagged outside a generated asset",
            )

    caption_layers = [layer for layer in plan.layers if layer.role.value == "caption"]
    if len(caption_layers) < len(plan.shots):
        add(
            "sound_off",
            "captions",
            QcVerdict.FAIL,
            "a sound-off cut needs a caption for every shot",
        )

    cta = plan.copy_map.get("CP-05")
    if cta is not None and cta.status.value != "approved":
        add(
            "cta_copy",
            "CP-05",
            QcVerdict.WARN,
            "CTA copy is still proposed; ED-04 is pending",
            "Approve ED-04 before publishing.",
        )

    return _report("semantic", findings)


def rights_qc(
    plan: ProductionPlan,
    intents: list[AssetIntent],
    decisions: list[LayerMethodDecision],
) -> QcReport:
    findings: list[QcFinding] = []
    index = 1

    def add(
        check: str, target: str, verdict: QcVerdict, detail: str, fix: str | None = None
    ) -> None:
        nonlocal index
        findings.append(_finding(index, "rights", check, target, verdict, detail, fix))
        index += 1

    held = {intent.asset_id: intent.holds for intent in intents}
    for asset in plan.assets:
        if asset.rights.status.value == "cleared":
            if not asset.rights.licence_name:
                add("cleared_basis", asset.id, QcVerdict.FAIL, "cleared without a licence basis")
        elif asset.rights.status.value == "needs_approval":
            if not held.get(asset.id):
                add(
                    "hold_owner",
                    asset.id,
                    QcVerdict.FAIL,
                    "needs approval but no hold names an owner",
                )
        elif asset.rights.status.value == "reference_only":
            add("reference_only", asset.id, QcVerdict.FAIL, "reference-only media cannot ship")

    for decision in decisions:
        if decision.rights_gate.value == "block":
            add("rights_gate", decision.layer_id, QcVerdict.FAIL, "layer blocked by rights")

    if not any(decision.candidates for decision in decisions):
        add(
            "candidate_provenance",
            "run",
            QcVerdict.WARN,
            "no sourcing round has run yet; no candidate licence has been verified",
            "Run sourcing after Gate 2A and record origin verification.",
        )

    return _report("rights", findings)


def budget_qc(plan: ProductionPlan, sheet: BuildSheet) -> QcReport:
    findings: list[QcFinding] = []
    index = 1

    def add(
        check: str, target: str, verdict: QcVerdict, detail: str, fix: str | None = None
    ) -> None:
        nonlocal index
        findings.append(_finding(index, "budget", check, target, verdict, detail, fix))
        index += 1

    summary = sheet.manifest.budget
    add(
        "cap",
        "budget",
        QcVerdict.PASS if summary.within_cap else QcVerdict.FAIL,
        f"total {summary.total_usd:.2f} against cap {summary.cap_usd:.2f}",
    )
    add(
        "worst_case",
        "budget",
        QcVerdict.PASS if summary.worst_within_cap else QcVerdict.FAIL,
        f"worst {summary.worst_usd:.2f} against cap {summary.cap_usd:.2f}",
    )
    if summary.verified_quote_usd == 0:
        add(
            "quote_status",
            "budget",
            QcVerdict.WARN,
            "every line is an operator estimate; no verified quote yet",
            "Collect quotes at Gate 2A.",
        )
    if summary.unpriced_lines:
        add(
            "unpriced_fallbacks",
            ",".join(summary.unpriced_lines),
            QcVerdict.WARN,
            "fallback lines carry no price",
            "Price them or record an explicit zero-cost swap.",
        )
    return _report("budget", findings)


def visual_qc(sheet: BuildSheet) -> QcReport:
    findings: list[QcFinding] = []
    processed = [
        asset
        for asset in sheet.assets
        if asset.status in {TaskStatus.PROCESSED, TaskStatus.ACCEPTED}
    ]
    if not processed:
        findings.append(
            _finding(
                1,
                "visual",
                "media_available",
                "assets",
                QcVerdict.FAIL,
                "no processed media exists yet; visual QC cannot run",
                "Acquire and process assets after Gate 2A.",
            )
        )
    else:
        findings.append(
            _finding(
                1,
                "visual",
                "media_available",
                "assets",
                QcVerdict.WARN,
                f"{len(processed)} processed assets still need a vision review",
                "Run the vision reviewer against each processed asset.",
            )
        )
    return _report("visual", findings, reviewer="vision:pending")


def run_qc(
    plan: ProductionPlan,
    sheet: BuildSheet,
    intents: list[AssetIntent],
    decisions: list[LayerMethodDecision],
) -> dict[str, QcReport]:
    reports = [
        technical_qc(plan, sheet),
        semantic_qc(plan, decisions, intents),
        rights_qc(plan, intents, decisions),
        budget_qc(plan, sheet),
        visual_qc(sheet),
    ]
    return {report.stage: report for report in reports}


def gate_states(reports: dict[str, QcReport], stages: list[str]) -> list[CheckState]:
    states: list[CheckState] = []
    for stage in stages:
        report = reports[stage]
        if report.verdict is QcVerdict.FAIL:
            states.append(CheckState.FAIL)
        elif report.verdict is QcVerdict.WARN:
            states.append(CheckState.WARN)
        else:
            states.append(CheckState.PASS)
    return states
