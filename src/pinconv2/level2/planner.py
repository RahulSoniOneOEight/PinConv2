"""Level 2 planner: the deterministic, spend-free pipeline.

The planner never searches, generates or spends. It derives one decision per
layer, one task per asset, one budget, one flow, one build sheet, one review pack
and the Gate 2A packet. Sourcing and processing start only after a human
approves Gate 2A.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from ..models import AssetRoute, Level2Handoff, ProductionPlan, StrictModel
from ..store import ProjectStore
from .agents import (
    AssetClassifier,
    BuildSheetBuilder,
    FlowScheduler,
    GenerationPlanner,
    HandoffValidator,
    ProcessingPlanner,
)
from .budget import build_budget
from .capture_planner import build_capture_plan, validate_capture_plan
from .catalogue import SOURCES
from .gate2 import evaluate_2a
from .handoff import asset_truth_class, build_intents
from .method_selector import (
    PROBE_METHODS,
    assert_method_allowed,
    select_asset_method,
    select_layer_method,
)
from .models import (
    AssetProductionTask,
    Batch,
    BudgetEstimate,
    BuildSheet,
    Correction,
    FlowSpec,
    GatePacket,
    LayerMethodDecision,
    Level2Plan,
    QcReport,
    RunState,
    SourceStrategy,
    TaskStatus,
)
from .preview import render_all
from .qc import run_qc
from .sound import build_sound_plan, validate_sound_plan
from .store import Level2RunStore
from .variants import resolve_variant, validate_variant


class Level2Outcome(StrictModel):
    level2: Level2Plan
    sheet: BuildSheet
    gate_2a: GatePacket
    qc: dict[str, QcReport] = Field(default_factory=dict)


def _holds_by_asset(handoff: Level2Handoff) -> dict[str, list[str]]:
    holds: dict[str, list[str]] = {}
    for item in handoff.held_items:
        for target in item.affects:
            if target.startswith("AS-"):
                holds.setdefault(target, []).append(item.id)
    return {asset: sorted(set(values)) for asset, values in holds.items()}


def _voice_script(plan: ProductionPlan) -> str:
    for cue in plan.audio_cues:
        if cue.kind.value == "vo":
            marker = "Canonical read:"
            return (
                cue.description.split(marker, 1)[1].strip()
                if marker in cue.description
                else cue.description
            )
    return "Approved narration."


def _task_status(
    asset_id: str, asset: object, holds: list[str], conditional: bool
) -> tuple[TaskStatus, list[str]]:
    from ..models import Asset

    assert isinstance(asset, Asset)
    blockers = list(holds)
    if conditional:
        blockers.append("conditional fallback")
        return TaskStatus.CONDITIONAL, blockers
    if asset.rights.status.value == "needs_approval":
        return TaskStatus.BLOCKED, blockers
    return TaskStatus.PLANNED, blockers


def _batch_for(strategy: SourceStrategy) -> Batch:
    if strategy in {SourceStrategy.SUPPLIED, SourceStrategy.OWNED}:
        return Batch.B1
    if strategy is SourceStrategy.CAPTURE:
        return Batch.B2
    if strategy is SourceStrategy.PROCEDURAL:
        return Batch.B3
    return Batch.B4


def _build_tasks(
    plan: ProductionPlan,
    budget: BudgetEstimate,
    handoff: Level2Handoff,
    capture_id: str,
) -> list[AssetProductionTask]:
    conditional_assets = {
        asset.fallback_asset_id for asset in plan.assets if asset.fallback_asset_id
    }
    holds = _holds_by_asset(handoff)
    tasks: list[AssetProductionTask] = []

    for asset in plan.assets:
        strategy, method, _ = select_asset_method(asset)
        assert_method_allowed(
            asset_truth_class(asset),
            method,
            asset.id,
            disclosed=asset.rights.disclosure_required,
            original_capture=asset.route is AssetRoute.TO_CAPTURE,
        )
        recipe = ProcessingPlanner().plan(asset, method, strategy)
        conditional = asset.id in conditional_assets
        status, blockers = _task_status(asset.id, asset, holds.get(asset.id, []), conditional)
        dependencies = list(asset.dependencies)
        if asset.route is AssetRoute.TO_CAPTURE:
            dependencies.insert(0, capture_id)
        generation = (
            GenerationPlanner().plan(asset, asset_truth_class(asset), _voice_script(plan))
            if strategy is SourceStrategy.GENERATE
            else None
        )
        line_ids = [
            line.line_id
            for line in budget.lines
            if line.asset_id == asset.id or asset.id in line.asset_ids
        ]
        tasks.append(
            AssetProductionTask(
                task_id=f"APT-{asset.id}",
                asset_id=asset.id,
                source_strategy=strategy,
                methods=[method],
                processing=recipe,
                generation=generation,
                capture_ref=capture_id if asset.route is AssetRoute.TO_CAPTURE else None,
                budget_line_ids=line_ids,
                flow=FlowSpec(
                    batch=_batch_for(strategy),
                    dependencies=dependencies,
                    stage="capture" if strategy is SourceStrategy.CAPTURE else "prepare",
                    critical_path=False,
                ),
                acceptance=asset.acceptance or asset.description,
                probe_required=method in PROBE_METHODS,
                conditional=conditional,
                status=status,
                blockers=sorted(set(blockers)),
            )
        )
    return tasks


def _write_supporting(
    run: Level2RunStore,
    run_id: str,
    plan: ProductionPlan,
    level2: Level2Plan,
    sheet: BuildSheet,
    reports: dict[str, QcReport],
    gate_2a: GatePacket,
) -> None:
    blocked_sources = [source.id for source in SOURCES if source.licence_class.value == "BLOCKED"]
    manual_only = [source.id for source in SOURCES if not source.scriptable]
    aggregators = [source.id for source in SOURCES if source.aggregator]
    run.write_data(
        run_id,
        "licence-gate-report.json",
        {
            "blocked_sources": sorted(blocked_sources),
            "manual_only_sources": sorted(manual_only),
            "aggregators": sorted(aggregators),
            "candidates": [],
            "note": "No sourcing round has run. Candidate licences are unverified.",
        },
    )

    rights = {
        "run_id": run_id,
        "plan_hash": plan.plan_hash(),
        "assets": [
            {
                "asset_id": asset.asset_id,
                "status": asset.rights_status,
                "licence_name": plan.asset_map[asset.asset_id].rights.licence_name,
                "commercial_use": plan.asset_map[asset.asset_id].rights.commercial_use,
                "modification": plan.asset_map[asset.asset_id].rights.modification,
                "attribution": plan.asset_map[asset.asset_id].rights.attribution,
                "hold": asset.hold,
                "conditional": asset.conditional,
            }
            for asset in sheet.assets
        ],
        "attributions": [],
        "note": "No CC BY candidate is in the package yet.",
    }
    run.write_data(run_id, "rights-manifest.json", rights)

    from .engines.base import SpendLedger

    ledger_path = run.run_dir(run_id) / "spend-ledger.jsonl"
    if not ledger_path.is_file():
        run.write_text(run_id, "spend-ledger.jsonl", "")
    ledger = SpendLedger(ledger_path)
    ledger_view: dict[str, object] = {
        "run_id": run_id,
        "currency": "USD",
        "cap_usd": level2.budget.summary.cap_usd,
        **ledger.summary(),
        "note": "Empty until Gate 2A approval. No paid call has been made.",
    }
    run.write_data(run_id, "spend-ledger.json", ledger_view)

    run.write_data(run_id, "blockers.json", level2.blockers)

    run.write_data(
        run_id,
        "catalogue-resolutions.json",
        {
            "run_id": run_id,
            "sourcing_round": "not_run",
            "candidates": [],
            "resolutions": [],
            "note": (
                "No sourcing round has run. Each future candidate records provider, "
                "licence, origin verification, attribution and cost here."
            ),
        },
    )

    for stage, report in reports.items():
        run.write_json(run_id, f"qc/{stage}.json", report)

    run.write_json(run_id, "gate2/packet-2a.json", gate_2a)


def plan_level2(
    store: ProjectStore,
    project_id: str,
    revision: int,
    run_id: str = "rev-002",
    corrections: list[Correction] | None = None,
) -> Level2Outcome:
    project = store.load_project(project_id)
    if project.state.value != "approved":
        raise ValueError("Level 2 needs an approved Level 1 project")
    inputs = HandoffValidator().validate(store, project_id, revision)
    plan = inputs.plan
    run = Level2RunStore(store.project_dir(project_id))

    holds = _holds_by_asset(inputs.handoff)
    scores = AssetClassifier().score(plan, inputs.brief)
    decisions: list[LayerMethodDecision] = []
    for layer in plan.layers:
        asset = (
            plan.asset_map.get(layer.binding_ref or "")
            if layer.binding_kind.value == "asset"
            else None
        )
        copy_block = (
            plan.copy_map.get(layer.binding_ref or "")
            if layer.binding_kind.value == "copy"
            else None
        )
        score, impact, signals = scores[layer.id]
        decisions.append(
            select_layer_method(
                layer,
                asset,
                copy_block,
                holds=holds.get(asset.id, []) if asset is not None else [],
                impact_score=score,
                impact=impact,
                impact_signals=signals,
            )
        )

    intents = build_intents(inputs, decisions)
    budget = build_budget(plan, intents)
    capture = build_capture_plan(plan, inputs.handoff)
    validate_capture_plan(plan, capture)
    sound = build_sound_plan(plan)
    validate_sound_plan(plan, sound)

    variants = [resolve_variant(plan, variant) for variant in inputs.handoff.variants]
    for variant in variants:
        validate_variant(plan, variant)

    tasks = _build_tasks(plan, budget, inputs.handoff, capture.session_id)

    previews_16 = render_all(plan)
    previews_9 = render_all(plan, inputs.handoff.variants[0]) if inputs.handoff.variants else {}
    for shot_id, svg in previews_16.items():
        run.write_text(run_id, f"build-sheet/previews/16x9/{shot_id}.svg", svg)
    for shot_id, svg in previews_9.items():
        run.write_text(run_id, f"build-sheet/previews/9x16/{shot_id}.svg", svg)
    preview_paths = {shot_id: f"previews/16x9/{shot_id}.svg" for shot_id in previews_16}

    sheet = BuildSheetBuilder().build(
        plan,
        intents,
        decisions,
        tasks,
        variants,
        budget,
        run_id=run_id,
        source_plan_hash=plan.plan_hash(),
        bundle_hash=inputs.approval.bundle_hash,
        packet_hash=inputs.approval.packet_hash,
        preview_paths=preview_paths,
        corrections=corrections,
    )
    scheduler = FlowScheduler()
    flow = scheduler.build(plan, tasks, sheet)
    scheduler.validate(plan, flow)

    blockers = [
        f"{item.id} {item.title} — owner {item.owner.value}" for item in inputs.handoff.held_items
    ]
    blockers.extend(blocker for variant in variants for blocker in variant.blockers)
    blockers.extend(
        f"{line.line_id} {line.label} is unpriced" for line in budget.lines if line.unpriced
    )
    blockers.append("Gate 2A approval required before any paid call")

    level2 = Level2Plan(
        run_id=run_id,
        project_id=project_id,
        plan_revision=revision,
        plan_hash=plan.plan_hash(),
        state=RunState.QUOTED,
        intents=intents,
        decisions=decisions,
        tasks=tasks,
        capture=capture,
        sound=sound,
        budget=budget,
        flow=flow,
        variants=variants,
        blockers=sorted(set(blockers)),
    )

    run.write_json(run_id, "run.json", level2)
    run.write_data(
        run_id,
        "asset-intents.json",
        [intent.model_dump(mode="json") for intent in intents],
    )
    run.write_data(
        run_id,
        "layer-method-decisions.json",
        [decision.model_dump(mode="json") for decision in decisions],
    )
    run.write_data(
        run_id,
        "asset-production-tasks.json",
        [task.model_dump(mode="json") for task in tasks],
    )
    run.write_json(run_id, "capture-plan.json", capture)
    run.write_json(run_id, "sound-plan.json", sound)
    run.write_json(run_id, "budget-estimate.json", budget)
    run.write_json(run_id, "flow.json", flow)
    run.write_data(
        run_id,
        "variants.json",
        [variant.model_dump(mode="json") for variant in variants],
    )

    sheet = run.write_build_sheet(run_id, sheet, plan)
    run.write_documents(run_id, plan, level2, sheet)

    reports = run_qc(plan, sheet, intents, decisions)
    gate_2a = evaluate_2a(
        plan,
        level2,
        sheet,
        decisions,
        reports,
        expected_bundle_hash=inputs.approval.bundle_hash,
        expected_packet_hash=inputs.approval.packet_hash,
    )
    _write_supporting(run, run_id, plan, level2, sheet, reports, gate_2a)

    run.append_event(
        run_id,
        "level2.planned",
        {
            "plan_hash": plan.plan_hash(),
            "assets": len(intents),
            "layers": len(decisions),
            "total_usd": level2.budget.summary.total_usd,
            "worst_usd": level2.budget.summary.worst_usd,
            "gate2a": gate_2a.status.value,
        },
    )

    return Level2Outcome(level2=level2, sheet=sheet, gate_2a=gate_2a, qc=reports)


def apply_corrections(
    store: ProjectStore,
    project_id: str,
    revision: int,
    base_run_id: str,
    corrections_path: Path,
) -> Level2Outcome:
    """Build a new run that carries accepted corrections.

    The planner is deterministic, so the new run re-derives every decision and
    records the accepted instructions in the build sheet for the next production
    pass. Creative changes are refused here and routed back to Level 1.
    """

    from .corrections import (
        load_corrections,
        next_run_id,
        validate_corrections,
        write_jsonl,
    )
    from .errors import Level2Error
    from .models import CorrectionStatus

    plan = store.load_plan(project_id, revision)
    run = Level2RunStore(store.project_dir(project_id))
    if not (run.run_dir(base_run_id) / "run.json").is_file():
        raise Level2Error(f"base run does not exist: {base_run_id}")
    base = run.read_level2(base_run_id)
    if base.plan_hash != plan.plan_hash():
        raise Level2Error("the base run is bound to a different plan hash")
    items = load_corrections(corrections_path)
    summary = validate_corrections(items, plan)
    if summary.creative_escalations:
        raise Level2Error(
            "creative corrections must return to Level 1: "
            + ", ".join(summary.creative_escalations)
        )
    accepted = [
        item.model_copy(
            update={
                "status": CorrectionStatus.REJECTED
                if item.decision.value == "reject"
                else CorrectionStatus.ACCEPTED
            }
        )
        for item in items
    ]
    new_run = next_run_id(base_run_id)
    outcome = plan_level2(store, project_id, revision, new_run, corrections=accepted)
    write_jsonl(run.run_dir(new_run) / "corrections.jsonl", accepted)
    run.append_event(
        new_run,
        "level2.corrections_applied",
        {
            "from_run": base_run_id,
            "items": [item.id for item in accepted],
            "affected": summary.affected_items,
        },
    )
    return outcome
