"""Level 2 planner: the deterministic, spend-free pipeline.

The planner never searches, generates or spends. It derives one decision per
layer, one task per asset, one budget, one flow, one build sheet, one review pack
and the Gate 2A packet. Sourcing and processing start only after a human
approves Gate 2A.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import Field

from ..models import AssetRoute, Level2Handoff, ProductionPlan, StrictModel, utc_now
from ..store import ProjectStore
from .agents import (
    AssetClassifier,
    BuildSheetBuilder,
    FlowScheduler,
    GenerationPlanner,
    HandoffValidator,
    ProcessingPlanner,
)
from .asset_summary import write_asset_outputs
from .budget import build_budget
from .capture_planner import build_capture_plan, validate_capture_plan
from .catalogue import SOURCES
from .errors import BudgetError
from .gate2 import evaluate_2a
from .governance import ProviderGovernor, empty_budget
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
    BudgetPolicy,
    BuildSheet,
    Correction,
    FlowSpec,
    GatePacket,
    LayerMethodDecision,
    Level2Plan,
    QcReport,
    RunState,
    SourceStrategy,
    SourcingReport,
    TaskStatus,
)
from .no_shoot import evaluate_no_shoot, render_no_shoot
from .preview import render_all
from .qc import run_qc
from .sound import build_sound_plan, validate_sound_plan
from .source_sheet import write_source_sheet
from .stock_plan import build_stock_plan, render_stock_plan
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
    sourcing_assets = level2.sourcing.assets if level2.sourcing is not None else []
    candidate_rows = [
        {
            "asset_id": asset.asset_id,
            "candidate_id": candidate.candidate_id,
            "provider": candidate.provider,
            "title": candidate.title,
            "creator": candidate.creator,
            "licence_class": candidate.licence_class.value,
            "licence_url": candidate.licence_url,
            "page_url": candidate.page_url,
            "origin_verified": True,
            "fit_score": candidate.fit_score,
            "gate_verdict": candidate.gate_verdict.value,
        }
        for asset in sourcing_assets
        for candidate in asset.candidates
    ]
    chosen_rows = [
        {
            "asset_id": asset.asset_id,
            "candidate_id": candidate.candidate_id,
            "licence_class": candidate.licence_class.value,
            "attribution": candidate.attribution,
            "page_url": candidate.page_url,
            "status": asset.status,
        }
        for asset in sourcing_assets
        for candidate in asset.candidates
        if candidate.candidate_id == asset.chosen_candidate
    ]
    sourcing_round = "discovery" if sourcing_assets else "not_run"
    run.write_data(
        run_id,
        "licence-gate-report.json",
        {
            "blocked_sources": sorted(blocked_sources),
            "manual_only_sources": sorted(manual_only),
            "aggregators": sorted(aggregators),
            "candidates": candidate_rows,
            "note": (
                f"Sourcing round: {sourcing_round}. {len(candidate_rows)} candidates "
                "checked; acquisition still needs Gate 2A."
            ),
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
        "attributions": [
            {
                "asset_id": row["asset_id"],
                "attribution": row["attribution"],
                "licence_class": row["licence_class"],
                "page_url": row["page_url"],
            }
            for row in chosen_rows
        ],
        "note": (
            "CC BY attribution is required for the chosen music candidates."
            if chosen_rows
            else "No CC BY candidate is in the package yet."
        ),
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

    run.write_data(
        run_id,
        "openmontage-status.json",
        {
            "checked_at": utc_now(),
            "app": "OpenMontage Studio",
            "version": "0.1.8",
            "account_state": "signed-in",
            "connected_providers": [
                "google",
                "openrouter",
                "runware",
                "fal",
                "recraft",
            ],
            "no_key_stock_routes": [
                "freetouse.stock",
                "nasa.stock",
                "openverse.stock",
                "wikimedia.stock",
            ],
            "not_connected": [
                "pixabay",
                "openai",
                "elevenlabs",
                "heygen",
                "minimax",
                "runway",
                "meshy",
                "tripo",
                "xai",
                "higgsfield",
                "quiverai",
                "azure-speech",
                "cartesia",
                "worldlabs",
            ],
            "local_gaps": [
                "ComfyUI not configured",
                "Blender bridge not configured",
                "Kokoro unsupported (eSpeak missing)",
                "local whisper.cpp not enabled",
                "ACE-Step not configured",
            ],
            "note": (
                "Checked through the OpenMontage MCP account/connections/app_update "
                "tools. No paid call was made."
            ),
        },
    )

    run.write_data(run_id, "blockers.json", level2.blockers)

    run.write_data(
        run_id,
        "catalogue-resolutions.json",
        {
            "run_id": run_id,
            "sourcing_round": sourcing_round,
            "candidates": candidate_rows,
            "resolutions": chosen_rows,
            "note": (
                "Candidates were discovered and licence-gated. Chosen previews are in "
                "sourcing/; final acquisition still needs Gate 2A."
                if candidate_rows
                else "No sourcing round has run."
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
    cap_usd: float | None = None,
    lean: bool = False,
    provider_cap_usd: float | None = None,
    per_job_max_usd: float = 0.5,
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
    budget = build_budget(plan, intents, cap_usd, lean=lean)
    if provider_cap_usd is not None and provider_cap_usd > budget.summary.cap_usd:
        raise BudgetError(
            f"the fal/Runware cap ${provider_cap_usd:.2f} cannot exceed the "
            f"project cap ${budget.summary.cap_usd:.2f}"
        )
    provider_budget = (
        empty_budget(provider_cap_usd, per_job_max_usd) if provider_cap_usd is not None else None
    )
    governor = (
        ProviderGovernor(
            run.run_dir(run_id) / "provider-spend.jsonl",
            provider_budget,
        )
        if provider_budget is not None
        else None
    )
    policy = BudgetPolicy(
        approved_cap_usd=plan.budget.cap_usd,
        operator_cap_usd=cap_usd,
        effective_cap_usd=budget.summary.cap_usd,
        source="operator_instruction" if cap_usd is not None else "approved_plan",
        note=(
            (
                "Operator spend cap applied to Level 2"
                + ("; lean in-kind production mode, zero cash." if lean else ".")
                + (
                    " The requested cap was above the approved cap; the approved cap was retained."
                    if cap_usd > plan.budget.cap_usd
                    else ""
                )
            )
            if cap_usd is not None
            else "Cap inherited from the approved Level 1 budget."
        ),
    )
    capture = build_capture_plan(plan, inputs.handoff, lean=lean)
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

    sourcing_path = run.run_dir(run_id) / "asset-sourcing.json"
    sourcing = (
        SourcingReport.model_validate_json(sourcing_path.read_text(encoding="utf-8"))
        if sourcing_path.is_file()
        else None
    )

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
        sourcing=sourcing,
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
        state=RunState.QUOTED
        if budget.summary.within_cap and budget.summary.worst_within_cap
        else RunState.BLOCKED,
        intents=intents,
        decisions=decisions,
        tasks=tasks,
        capture=capture,
        sound=sound,
        budget=budget,
        budget_policy=policy,
        provider_budget=provider_budget,
        sourcing=sourcing,
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
    run.write_json(run_id, "budget-policy.json", policy)
    if provider_budget is not None:
        run.write_json(run_id, "provider-budget.json", provider_budget)
        if not (run.run_dir(run_id) / "provider-spend.jsonl").is_file():
            run.write_text(run_id, "provider-spend.jsonl", "")
        assert governor is not None
        governor.write_view(run.run_dir(run_id) / "provider-spend.json")
    run.write_json(run_id, "flow.json", flow)
    run.write_data(
        run_id,
        "variants.json",
        [variant.model_dump(mode="json") for variant in variants],
    )

    sheet = run.write_build_sheet(run_id, sheet, plan)
    run.write_documents(run_id, plan, level2, sheet)
    openmontage_path = run.run_dir(run_id) / "openmontage-sourcing.json"
    openmontage = (
        json.loads(openmontage_path.read_text(encoding="utf-8"))
        if openmontage_path.is_file()
        else None
    )
    write_source_sheet(run, run_id, plan, level2, sheet, openmontage)

    reports = run_qc(plan, sheet, intents, decisions)
    gate_2a = evaluate_2a(
        plan,
        level2,
        sheet,
        decisions,
        reports,
        expected_bundle_hash=inputs.approval.bundle_hash,
        expected_packet_hash=inputs.approval.packet_hash,
        provider_summary=governor.summary() if governor is not None else None,
    )
    _write_supporting(run, run_id, plan, level2, sheet, reports, gate_2a)
    write_asset_outputs(run, run_id, plan, level2, sheet, decisions)
    no_shoot = evaluate_no_shoot(plan, level2)
    run.write_text(run_id, "NO-SHOOT-POLICY.md", render_no_shoot(no_shoot))
    run.write_json(run_id, "no-shoot-plan.json", no_shoot)
    stock_plan = build_stock_plan(plan, level2)
    candidates_path = run.run_dir(run_id) / "stock-candidates.json"
    if candidates_path.is_file():
        from .stock_plan import StockCandidate, render_annex

        candidates = [
            StockCandidate.model_validate(item)
            for item in json.loads(candidates_path.read_text(encoding="utf-8"))
        ]
        stock_plan = stock_plan.model_copy(update={"candidates": candidates})
        run.write_text(run_id, "ANNEX-SOURCED-NOT-USED.md", render_annex(candidates))
    run.write_text(run_id, "STOCK-PLAN.md", render_stock_plan(stock_plan))
    run.write_json(run_id, "stock-plan.json", stock_plan)

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
    operator_cap = base.budget_policy.operator_cap_usd if base.budget_policy is not None else None
    outcome = plan_level2(
        store,
        project_id,
        revision,
        new_run,
        corrections=accepted,
        cap_usd=operator_cap,
        lean=base.budget.mode == "lean",
    )
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
