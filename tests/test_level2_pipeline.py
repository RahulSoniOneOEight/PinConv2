"""Level 2 acceptance tests against the approved Blue Tokai case."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from pinconv2.errors import PinConvError
from pinconv2.level2.corrections import (
    load_corrections,
    next_run_id,
    validate_corrections,
    write_jsonl,
)
from pinconv2.level2.errors import GateOrderError
from pinconv2.level2.gate2 import approve_packet, evaluate_2b, evaluate_2c
from pinconv2.level2.handoff import load_approved_inputs
from pinconv2.level2.models import (
    Correction,
    CorrectionDecision,
    Method,
    PacketStatus,
    QcVerdict,
    TaskStatus,
    TruthClass,
)
from pinconv2.level2.planner import plan_level2
from pinconv2.level2.store import Level2RunStore
from pinconv2.service import run_all, run_approval, run_export
from pinconv2.store import ProjectStore

PROJECT = "blue-tokai-easy-pour-20s"


@pytest.fixture(scope="module")
def approved(tmp_path_factory: pytest.TempPathFactory) -> SimpleNamespace:
    root = tmp_path_factory.mktemp("level2")
    store = ProjectStore(root / "projects")
    run_all(store, PROJECT)
    run_approval(
        store,
        PROJECT,
        approver="TestReviewer",
        role="Brand owner",
        evidence="pytest acceptance run",
        actor_kind="human",
        human_confirmation="APPROVE",
        channel="pytest",
        approved_variants=["VO-01"],
    )
    run_export(store, PROJECT)
    outcome = plan_level2(store, PROJECT, 2, "rev-002")
    return SimpleNamespace(
        store=store,
        outcome=outcome,
        run=Level2RunStore(store.project_dir(PROJECT)),
        project=PROJECT,
    )


def test_handoff_hash_chain(approved: SimpleNamespace) -> None:
    inputs = load_approved_inputs(approved.store, approved.project, 2)
    assert inputs.plan.plan_hash() == inputs.handoff.plan_hash
    assert inputs.approval.plan_hash == inputs.handoff.plan_hash
    assert inputs.approval.bundle_hash == inputs.handoff.approval.bundle_hash
    assert inputs.approval.approver == "TestReviewer"
    assert inputs.handoff.variants[0].variant_id == "VO-01"
    assert len(inputs.handoff.assets) == 13
    assert len(inputs.plan.assets) == 16


def test_counts_and_classes(approved: SimpleNamespace) -> None:
    outcome = approved.outcome
    assert len(outcome.level2.intents) == 16
    assert len(outcome.level2.decisions) == 38
    assert len(outcome.sheet.assets) == 16
    assert len(outcome.sheet.shots) == 6

    classes = [decision.truth_class for decision in outcome.level2.decisions]
    assert classes.count(TruthClass.EXACT) == 10
    assert classes.count(TruthClass.EXACT_TEXT) == 12
    assert classes.count(TruthClass.PROOF) == 3
    assert classes.count(TruthClass.ATMOSPHERIC) == 7
    assert classes.count(TruthClass.REPRESENTATIVE) == 6

    impact = [decision.impact.value for decision in outcome.level2.decisions]
    assert impact.count("high") == 18
    assert impact.count("medium") == 10
    assert impact.count("low") == 10


def test_method_policy(approved: SimpleNamespace) -> None:
    for decision in approved.outcome.level2.decisions:
        if decision.truth_class in {TruthClass.EXACT, TruthClass.EXACT_TEXT}:
            assert decision.method in {Method.M0, Method.M4, Method.M6}
            assert decision.method is not Method.M1
            assert decision.method is not Method.M5
            assert decision.method is not Method.M7
        if decision.truth_class is TruthClass.PROOF:
            assert decision.method is Method.M6
        if decision.method not in {Method.M0, Method.M1}:
            assert decision.probe_required is True


def test_budget_reconciles(approved: SimpleNamespace) -> None:
    budget = approved.outcome.level2.budget
    summary = budget.summary
    assert summary.subtotal_usd == 76.0
    assert summary.reserve_usd == 11.4
    assert summary.total_usd == 87.4
    assert summary.fallback_usd == 5.0
    assert summary.worst_usd == 92.4
    assert summary.cap_usd == 100.0
    assert summary.headroom_usd == 7.6
    assert summary.within_cap and summary.worst_within_cap
    assert budget.raw_attributed_usd == 89.0
    assert budget.dedupe_savings_usd == 42.0
    capture_lines = [line for line in budget.lines if line.estimate_id == "ES-06"]
    assert len(capture_lines) == 1
    assert capture_lines[0].amount_usd == 18.0
    assert len(capture_lines[0].asset_ids) == 3
    assert summary.unpriced_lines  # AS-14 and AS-15 are flagged, not hidden


def test_capture_and_sound(approved: SimpleNamespace) -> None:
    capture = approved.outcome.level2.capture
    covered = {member.asset_id for member in capture.members}
    assert {"AS-05", "AS-06", "AS-08", "AS-13"} <= covered
    assert capture.cost_usd == 18.0
    assert capture.release_hold == "HI-04"
    assert "pour" in " ".join(capture.foley).lower()

    sound = approved.outcome.level2.sound
    music = [cue for cue in sound.cues if cue.kind == "music"]
    assert music and music[0].edit_points == [275, 445]
    assert any(cue.asset_id == "AS-15" and cue.disclosure_required for cue in sound.cues)


def test_variant(approved: SimpleNamespace) -> None:
    variants = approved.outcome.level2.variants
    assert len(variants) == 1
    variant = variants[0]
    geometry = (variant.width, variant.height, variant.fps, variant.frame_count)
    assert geometry == (1080, 1920, 25, 500)
    assert len(variant.resolutions) == 38
    assert sum(1 for item in variant.resolutions if item.resolution == "override") == 38
    assert variant.effect_overrides == ["FX-01", "FX-02", "FX-03", "FX-05"]
    assert variant.cost_usd == 6.0
    assert variant.check_status == "pending"
    assert not variant.ready
    assert any("AC-16" in blocker for blocker in variant.blockers)
    assert len(variant.layer_overrides) == 38
    first = variant.layer_overrides[0]
    assert (first.rect.x, first.rect.y, first.rect.w, first.rect.h) == (0, 0, 1080, 1920)
    assert len(variant.effect_masks) == 4
    mask = variant.effect_masks[0]
    assert mask.mask_region.w == 110 and mask.mask_region.h == 900


def test_build_sheet_and_manifest(approved: SimpleNamespace) -> None:
    run = approved.run
    sheet = run.read_build_sheet("rev-002")
    assert sheet.manifest.counts["assets"] == 16
    assert sheet.manifest.counts["layers"] == 38
    assert sheet.manifest.counts["shots"] == 6
    assert sheet.timeline.frame_count == 500
    assert sheet.timeline.fps == 25

    for relative, digest in sheet.manifest.parts.items():
        path = run.run_dir("rev-002") / relative
        assert path.is_file(), relative
        assert run.digest(path).sha256 == digest.sha256

    captions = (
        run.run_dir("rev-002") / "build-sheet" / "captions" / "captions-16x9.srt"
    ).read_text(encoding="utf-8")
    assert captions.count("-->") == 6
    assert "Tear, anchor, pour" in captions

    variant_preview = (
        run.run_dir("rev-002") / "build-sheet" / "previews" / "9x16" / "SH-01.svg"
    ).read_text(encoding="utf-8")
    assert 'width="1080"' in variant_preview and 'height="1920"' in variant_preview


def test_asset_statuses(approved: SimpleNamespace) -> None:
    assets = {asset.asset_id: asset for asset in approved.outcome.sheet.assets}
    assert assets["AS-02"].status is TaskStatus.BLOCKED
    assert assets["AS-02"].hold == "HI-02"
    assert assets["AS-07"].status is TaskStatus.PLANNED
    assert assets["AS-13"].status is TaskStatus.CONDITIONAL
    assert assets["AS-15"].truth_class is TruthClass.REPRESENTATIVE
    assert assets["AS-01"].conditional is False


def test_qc_reports(approved: SimpleNamespace) -> None:
    reports = approved.outcome.qc
    assert reports["technical"].verdict is QcVerdict.PASS
    assert reports["semantic"].verdict is QcVerdict.WARN
    assert reports["visual"].verdict is QcVerdict.FAIL
    assert any("ED-04" in finding.detail for finding in reports["semantic"].findings)


def test_gate_2a_ready_and_2b_blocked(approved: SimpleNamespace) -> None:
    packet = approved.outcome.gate_2a
    assert packet.status is PacketStatus.READY
    assert packet.blockers == []
    assert any(check.id == "G2A-04" and check.state.value == "pass" for check in packet.checks)

    approved_2a = approve_packet(
        packet,
        approver="TestReviewer",
        role="Brand owner",
        evidence="pytest gate",
        confirmation="APPROVE",
    )
    assert approved_2a.status is PacketStatus.APPROVED

    packet_2b = evaluate_2b(
        approved.store.load_plan(PROJECT, 2),
        approved.outcome.level2,
        approved.outcome.sheet,
        approved.outcome.qc,
        approved_2a,
    )
    assert packet_2b.status is PacketStatus.BLOCKED
    assert any("asset coverage" in blocker.lower() for blocker in packet_2b.blockers)
    assert any("rights" in blocker.lower() for blocker in packet_2b.blockers)

    with pytest.raises(GateOrderError):
        evaluate_2c(
            approved.store.load_plan(PROJECT, 2),
            approved.outcome.level2,
            packet_2b,
            deliverables=[],
            duration_ok=False,
            audio_ok=False,
            captions_ok=False,
            reviewer=None,
        )


def test_review_pack_and_budget_docs(approved: SimpleNamespace) -> None:
    run = approved.run
    review = (run.run_dir("rev-002") / "review-pack.md").read_text(encoding="utf-8")
    assert "Gate 2 review" in review
    assert "AS-02" in review and "LY-012" in review
    assert "$87.40" in review
    assert "Decision: ☐ APPROVE" in review
    assert "Preview: build-sheet/previews/16x9/SH-01.svg" in review
    assert "## Previews" in review
    assert "[9:16](build-sheet/previews/9x16/SH-01.svg)" in review

    budget = (run.run_dir("rev-002") / "budget-estimate.md").read_text(encoding="utf-8")
    assert "$87.40" in budget and "$92.40" in budget and "$7.60" in budget

    for name in ("review-pack.docx", "budget-estimate.docx"):
        path = run.run_dir("rev-002") / name
        with zipfile.ZipFile(path) as archive:
            assert "word/document.xml" in archive.namelist()
            assert "word/styles.xml" in archive.namelist()
            assert "docProps/core.xml" in archive.namelist()

    review_html = (run.run_dir("rev-002") / "review-pack.html").read_text(encoding="utf-8")
    budget_html = (run.run_dir("rev-002") / "budget-estimate.html").read_text(encoding="utf-8")
    assert "<table>" in review_html and "AS-02" in review_html
    assert "Level 2 budget" in budget_html


def test_corrections_open_a_new_run(approved: SimpleNamespace) -> None:
    plan = approved.store.load_plan(PROJECT, 2)
    correction = Correction(
        id="COR-001",
        item_kind="asset",
        item_id="AS-10",
        decision=CorrectionDecision.CHANGE,
        instruction="Recut the lift six frames earlier",
        reason="Lift lands after the pack reveal",
        requested_by="TestReviewer",
    )
    summary = validate_corrections([correction], plan)
    assert summary.total == 1
    assert summary.affected_items == ["AS-10"]
    assert summary.creative_escalations == []
    assert next_run_id("rev-002") == "rev-003"

    path = approved.run.run_dir("rev-003") / "corrections.jsonl"
    write_jsonl(path, [correction])
    loaded = load_corrections(path)
    assert loaded[0].status.value == "open"
    assert approved.run.run_dir("rev-002").is_dir()

    creative = correction.model_copy(
        update={"id": "COR-002", "item_kind": "shot", "item_id": "SH-01"}
    )
    escalated = validate_corrections([creative], plan)
    assert escalated.creative_escalations == ["SH-01"]


def test_unknown_correction_is_refused(approved: SimpleNamespace) -> None:
    plan = approved.store.load_plan(PROJECT, 2)
    bad = Correction(
        id="COR-009",
        item_kind="asset",
        item_id="AS-99",
        decision=CorrectionDecision.APPROVE,
        instruction="approve",
        reason="test",
        requested_by="TestReviewer",
    )
    with pytest.raises(PinConvError):
        validate_corrections([bad], plan)


def test_paid_call_is_refused_before_gate(approved: SimpleNamespace) -> None:
    from pinconv2.level2.engines.base import SpendLedger
    from pinconv2.level2.errors import SpendNotAuthorisedError

    ledger = SpendLedger(approved.run.run_dir("rev-002") / "ledger-test.jsonl")
    with pytest.raises(SpendNotAuthorisedError):
        ledger.reserve("BL-001", 10.0, "music licence")

    authorised = SpendLedger(approved.run.run_dir("rev-002") / "ledger-test.jsonl", authorised=True)
    authorised.reserve("BL-001", 10.0, "music licence")
    authorised.receipt("BL-001", 10.0, "music licence")
    assert authorised.open_reservations() == 0
    assert authorised.spent_usd() == 10.0


def test_run_json_matches_outcome(approved: SimpleNamespace) -> None:
    stored = approved.run.read_level2("rev-002")
    assert stored.plan_hash == approved.outcome.level2.plan_hash
    assert stored.state.value == "quoted"
    assert len(stored.decisions) == 38
    raw = json.loads((approved.run.run_dir("rev-002") / "run.json").read_text(encoding="utf-8"))
    assert raw["plan_revision"] == 2
    assert raw["budget"]["summary"]["total_usd"] == 87.4


def test_gate_checks_are_not_vacuous(approved: SimpleNamespace) -> None:
    from pinconv2.level2.gate2 import evaluate_2a
    from pinconv2.level2.models import (
        CheckState,
        GateVerdict,
        LicenceClass,
        Method,
        MethodCandidate,
        TruthClass,
    )

    plan = approved.store.load_plan(PROJECT, 2)
    decisions = list(approved.outcome.level2.decisions)
    proof_index = next(
        index
        for index, decision in enumerate(decisions)
        if decision.truth_class is TruthClass.PROOF
    )
    decisions[proof_index] = decisions[proof_index].model_copy(
        update={"method": Method.M1, "probe_required": False}
    )
    packet = evaluate_2a(
        plan, approved.outcome.level2, approved.outcome.sheet, decisions, approved.outcome.qc
    )
    checks = {check.id: check for check in packet.checks}
    assert checks["G2A-02"].state is CheckState.FAIL
    assert checks["G2A-03"].state is CheckState.FAIL

    tampered = approved.outcome.level2.model_copy(update={"plan_hash": "0" * 64})
    hash_packet = evaluate_2a(
        plan,
        tampered,
        approved.outcome.sheet,
        approved.outcome.level2.decisions,
        approved.outcome.qc,
    )
    hash_checks = {check.id: check for check in hash_packet.checks}
    assert hash_checks["G2A-01"].state is CheckState.FAIL

    blocked = MethodCandidate(
        candidate_id="CND-LY010-01",
        asset_id="AS-10",
        provider="bbc-sound-effects",
        url="https://example.invalid/blocked",
        licence_class=LicenceClass.BLOCKED,
        fit_score=50,
        cost_usd=0,
        gate_verdict=GateVerdict.BLOCK,
    )
    with_candidate = [
        decision.model_copy(
            update={"candidates": [blocked], "chosen_candidate": blocked.candidate_id}
        )
        if decision.layer_id == "LY-010"
        else decision
        for decision in approved.outcome.level2.decisions
    ]
    catalogue_packet = evaluate_2a(
        plan,
        approved.outcome.level2,
        approved.outcome.sheet,
        with_candidate,
        approved.outcome.qc,
    )
    catalogue_checks = {check.id: check for check in catalogue_packet.checks}
    assert catalogue_checks["G2A-06"].state is CheckState.FAIL


def test_gate_2a_reads_sourcing_candidates(approved: SimpleNamespace) -> None:
    from pinconv2.level2.gate2 import evaluate_2a
    from pinconv2.level2.models import (
        AssetSourcing,
        CheckState,
        GateVerdict,
        LicenceClass,
        SourcingCandidate,
        SourcingReport,
    )

    candidate = SourcingCandidate(
        candidate_id="CND-AS10-01",
        asset_id="AS-10",
        provider="ccmixter",
        title="Warm Instrumental",
        creator="artist",
        page_url="https://ccmixter.org/files/a/1",
        licence_class=LicenceClass.CC_BY,
        licence_url="https://creativecommons.org/licenses/by/3.0/",
        attribution='"Warm Instrumental" by artist (CC BY 3.0)',
        fit_score=85,
        gate_verdict=GateVerdict.PASS,
    )
    report = SourcingReport(
        run_id="rev-002",
        assets=[
            AssetSourcing(
                asset_id="AS-10",
                query="warm",
                status="discovered",
                candidates=[candidate],
                chosen_candidate=candidate.candidate_id,
            )
        ],
    )
    level2 = approved.outcome.level2.model_copy(update={"sourcing": report})
    packet = evaluate_2a(
        approved.store.load_plan(PROJECT, 2),
        level2,
        approved.outcome.sheet,
        level2.decisions,
        approved.outcome.qc,
        expected_bundle_hash=approved.outcome.sheet.manifest.bundle_hash,
        expected_packet_hash=approved.outcome.sheet.manifest.packet_hash,
    )
    checks = {check.id: check for check in packet.checks}
    assert checks["G2A-06"].state is CheckState.PASS
    assert "from sourcing" in checks["G2A-06"].detail


def test_feedback_form_and_catalogue_resolutions(approved: SimpleNamespace) -> None:
    run_dir = approved.run.run_dir("rev-002")
    feedback = (run_dir / "feedback-form.md").read_text(encoding="utf-8")
    assert feedback.count("☐ APPROVE") == 16 + 38
    assert "## Assets" in feedback and "## Layers" in feedback

    resolutions = json.loads((run_dir / "catalogue-resolutions.json").read_text(encoding="utf-8"))
    assert resolutions["sourcing_round"] == "not_run"
    assert resolutions["candidates"] == []

    ledger_view = json.loads((run_dir / "spend-ledger.json").read_text(encoding="utf-8"))
    assert ledger_view["entries"] == []
    assert ledger_view["spent_usd"] == 0.0
    assert (run_dir / "spend-ledger.jsonl").read_text(encoding="utf-8") == ""

    review = (run_dir / "review-pack.md").read_text(encoding="utf-8")
    assert "Sourcing round: **not run**" in review
    assert "no sourcing round has run" not in review.lower()


def test_computed_critical_path_uses_the_capture_chain(approved: SimpleNamespace) -> None:
    flow = approved.outcome.level2.flow
    assert "CAP-01" in flow.critical_path
    assert any(node.startswith("AS-0") for node in flow.critical_path)
    assert flow.critical_path[-1] == "VO-01"


def test_apply_corrections_builds_a_new_run(approved: SimpleNamespace, tmp_path: Path) -> None:
    from pinconv2.level2.models import Correction, CorrectionDecision
    from pinconv2.level2.planner import apply_corrections

    path = tmp_path / "corrections.jsonl"
    correction = Correction(
        id="COR-101",
        item_kind="asset",
        item_id="AS-10",
        decision=CorrectionDecision.CHANGE,
        instruction="Recut the lift six frames earlier",
        reason="Lift lands after the pack reveal",
        requested_by="TestReviewer",
    )
    path.write_text(correction.model_dump_json() + "\n", encoding="utf-8")

    outcome = apply_corrections(approved.store, PROJECT, 2, "rev-002", path)
    assert outcome.level2.run_id == "rev-003"
    assert len(outcome.sheet.corrections) == 1
    assert outcome.sheet.corrections[0].id == "COR-101"
    assert "build-sheet/corrections.json" in outcome.sheet.manifest.parts
    assert (approved.run.run_dir("rev-003") / "corrections.jsonl").is_file()
    assert (approved.run.run_dir("rev-003") / "gate2" / "packet-2a.json").is_file()


def test_operator_cap_blocks_gate_2a(approved: SimpleNamespace) -> None:
    from pinconv2.level2.gate2 import evaluate_2a
    from pinconv2.level2.models import CheckState
    from pinconv2.level2.planner import plan_level2

    outcome = plan_level2(approved.store, PROJECT, 2, "rev-920", cap_usd=2.0)
    summary = outcome.level2.budget.summary
    assert summary.cap_usd == 2.0
    assert summary.total_usd == 87.4
    assert summary.worst_usd == 92.4
    assert summary.headroom_usd == -90.4
    assert summary.within_cap is False
    assert outcome.level2.state.value == "blocked"
    assert outcome.level2.budget_policy is not None
    assert outcome.level2.budget_policy.operator_cap_usd == 2.0
    assert outcome.gate_2a.status.value == "blocked"
    checks = {check.id: check for check in outcome.gate_2a.checks}
    assert checks["G2A-04"].state is CheckState.FAIL
    assert any("2.00" in blocker for blocker in outcome.gate_2a.blockers)
    policy = json.loads(
        (approved.run.run_dir("rev-920") / "budget-policy.json").read_text(encoding="utf-8")
    )
    assert policy["effective_cap_usd"] == 2.0
    assert policy["source"] == "operator_instruction"

    # The same plan still passes under the approved cap; the guard is the cap,
    # not a weakened budget model.
    baseline = evaluate_2a(
        approved.store.load_plan(PROJECT, 2),
        approved.outcome.level2,
        approved.outcome.sheet,
        approved.outcome.level2.decisions,
        approved.outcome.qc,
        expected_bundle_hash=approved.outcome.sheet.manifest.bundle_hash,
        expected_packet_hash=approved.outcome.sheet.manifest.packet_hash,
    )
    baseline_checks = {check.id: check for check in baseline.checks}
    assert baseline_checks["G2A-04"].state is CheckState.PASS


def test_lean_mode_fits_two_dollar_cap(approved: SimpleNamespace) -> None:
    from pinconv2.level2.models import CheckState
    from pinconv2.level2.planner import plan_level2

    outcome = plan_level2(
        approved.store,
        PROJECT,
        2,
        "rev-921",
        cap_usd=2.0,
        lean=True,
        provider_cap_usd=2.0,
        per_job_max_usd=0.5,
    )
    summary = outcome.level2.budget.summary
    assert summary.cap_usd == 2.0
    assert summary.total_usd == 0.0
    assert summary.worst_usd == 0.0
    assert summary.headroom_usd == 2.0
    assert summary.within_cap and summary.worst_within_cap
    assert outcome.level2.budget.mode == "lean"
    assert outcome.level2.budget.in_kind_usd == 81.0
    assert len(outcome.level2.budget.substitutions) == 10
    assert {item.estimate_id for item in outcome.level2.budget.substitutions} >= {
        "ES-01",
        "ES-02",
        "ES-06",
    }
    assert any("capture" in item.route.lower() for item in outcome.level2.budget.substitutions)
    assert outcome.level2.state.value == "quoted"
    assert outcome.gate_2a.status.value == "ready_for_approval"
    assert outcome.level2.capture.cost_usd == 0.0
    assert outcome.level2.capture.in_kind_usd == 18.0
    assert "Self-operated" in outcome.level2.capture.studio
    checks = {check.id: check for check in outcome.gate_2a.checks}
    assert checks["G2A-04"].state is CheckState.PASS
    assert checks["G2A-13"].state is CheckState.WARN
    assert "Lean substitutions" in checks["G2A-13"].name
    assert checks["G2A-14"].state is CheckState.PASS
    assert "fal+Runware cap $2.00" in checks["G2A-14"].detail
    assert "remaining $2.00" in checks["G2A-14"].detail
    assert outcome.level2.provider_budget is not None
    assert outcome.level2.provider_budget.cap_usd == 2.0
    assert outcome.level2.provider_budget.per_job_max_usd == 0.5

    baseline_methods = [decision.method for decision in approved.outcome.level2.decisions]
    lean_methods = [decision.method for decision in outcome.level2.decisions]
    assert baseline_methods == lean_methods

    review = (approved.run.run_dir("rev-921") / "review-pack.md").read_text(encoding="utf-8")
    assert "Cost: $0.00 cash · $4.00 in-kind (ES-05)" in review
    assert "Cost: $0.00 cash · $18.00 in-kind (ES-06)" in review
    assert "$0.00 cash · $6.00 in-kind" in review
    assert "Cost: $4.00 (ES-05)" not in review

    # The $2 guardrail still bites without lean mode.
    blocked = plan_level2(approved.store, PROJECT, 2, "rev-922", cap_usd=2.0)
    assert blocked.level2.state.value == "blocked"
    assert blocked.gate_2a.status.value == "blocked"


def test_operator_cap_cannot_exceed_the_approved_cap(
    approved: SimpleNamespace,
) -> None:
    from pinconv2.level2.planner import plan_level2

    outcome = plan_level2(approved.store, PROJECT, 2, "rev-923", cap_usd=500.0)
    assert outcome.level2.budget.summary.cap_usd == 100.0
    assert outcome.level2.budget.summary.within_cap is True
    assert outcome.level2.budget_policy is not None
    assert outcome.level2.budget_policy.operator_cap_usd == 500.0
    assert "approved cap was retained" in outcome.level2.budget_policy.note


def test_provider_cap_cannot_exceed_the_project_cap(
    approved: SimpleNamespace,
) -> None:
    from pinconv2.level2.errors import BudgetError
    from pinconv2.level2.planner import plan_level2

    with pytest.raises(BudgetError):
        plan_level2(
            approved.store,
            PROJECT,
            2,
            "rev-924",
            cap_usd=2.0,
            provider_cap_usd=5.0,
        )


def test_build_refuses_before_gate_2a(approved: SimpleNamespace) -> None:
    from pinconv2.level2.build import run_build

    with pytest.raises(GateOrderError):
        run_build(approved.store, approved.project, 2, "rev-002")


def test_build_after_approval_reports_blocked_sources(
    approved: SimpleNamespace, tmp_path: Path
) -> None:
    import shutil

    from pinconv2.level2.build import run_build
    from pinconv2.level2.models import GatePacket

    source = approved.run.run_dir("rev-002")
    target = approved.run.run_dir("rev-902")
    shutil.copytree(source, target)
    packet = GatePacket.model_validate_json(
        (target / "gate2" / "packet-2a.json").read_text(encoding="utf-8")
    )
    approved_packet = approve_packet(
        packet,
        approver="TestReviewer",
        role="Brand owner",
        evidence="pytest gate",
        confirmation="APPROVE",
    )
    approved.run.write_json("rev-902", "gate2/packet-2a.json", approved_packet)

    report = run_build(approved.store, approved.project, 2, "rev-902")
    assert report.approved_by == "TestReviewer"
    assert report.processed == 0
    assert report.blocked == 13
    assert report.conditional == 3
    assert report.spent_usd == 0.0
    assert all(entry.output_path is None for entry in report.entries)
    ledger_view = json.loads((target / "spend-ledger.json").read_text(encoding="utf-8"))
    assert ledger_view["spent_usd"] == 0.0
    assert ledger_view["entries"] == []
    shutil.rmtree(target, ignore_errors=True)
