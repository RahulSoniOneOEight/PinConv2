"""Command-line interface for Level 2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..errors import PinConvError
from ..models import ProductionPlan, utc_now
from ..service import DEFAULT_PROJECT
from ..store import ProjectStore
from .corrections import (
    load_corrections,
    next_run_id,
    validate_corrections,
    write_jsonl,
)
from .gate2 import approve_packet, evaluate_2b, evaluate_2c
from .handoff import load_approved_inputs
from .models import (
    GatePacket,
    Level2Plan,
    PacketStatus,
    QcReport,
    RunState,
)
from .planner import plan_level2
from .store import Level2RunStore


def _run_id(args: argparse.Namespace, revision: int) -> str:
    run = args.run
    return str(run) if run else f"rev-{revision:03d}"


def _revision(store: ProjectStore, project_id: str, args: argparse.Namespace) -> int:
    revision = args.revision
    return int(revision) if revision else store.latest_plan_revision(project_id)


def _print(value: object) -> None:
    if isinstance(value, str):
        print(value)
    else:
        print(json.dumps(value, indent=2, default=str))


def run_level2_command(store: ProjectStore, args: argparse.Namespace) -> int:
    project_id = str(args.project or DEFAULT_PROJECT)
    revision = _revision(store, project_id, args)
    run_id = _run_id(args, revision)
    run = Level2RunStore(store.project_dir(project_id))
    command = str(args.level2_command)

    if command == "ingest":
        inputs = load_approved_inputs(store, project_id, revision)
        _print(
            {
                "project": project_id,
                "revision": revision,
                "plan_hash": inputs.plan.plan_hash(),
                "bundle_hash": inputs.approval.bundle_hash,
                "packet_hash": inputs.approval.packet_hash,
                "approved_assets": len(inputs.handoff.assets),
                "plan_assets": len(inputs.plan.assets),
                "variants": [variant.variant_id for variant in inputs.handoff.variants],
                "approver": inputs.approval.approver,
            }
        )
        return 0

    if command == "plan":
        outcome = plan_level2(
            store,
            project_id,
            revision,
            run_id,
            cap_usd=getattr(args, "cap", None),
            lean=bool(getattr(args, "lean", False)),
            provider_cap_usd=getattr(args, "provider_cap", None),
            per_job_max_usd=float(getattr(args, "per_job_cap", 0.5)),
        )
        summary = outcome.level2.budget.summary
        _print(
            {
                "run": run_id,
                "state": outcome.level2.state.value,
                "assets": len(outcome.level2.intents),
                "layers": len(outcome.level2.decisions),
                "shots": len(outcome.sheet.shots),
                "variants": [variant.variant_id for variant in outcome.level2.variants],
                "budget": {
                    "mode": outcome.level2.budget.mode,
                    "subtotal": summary.subtotal_usd,
                    "reserve": summary.reserve_usd,
                    "total": summary.total_usd,
                    "worst": summary.worst_usd,
                    "cap": summary.cap_usd,
                    "headroom": summary.headroom_usd,
                    "in_kind": outcome.level2.budget.in_kind_usd,
                },
                "provider_budget": (
                    outcome.level2.provider_budget.model_dump(mode="json")
                    if outcome.level2.provider_budget is not None
                    else None
                ),
                "gate_2a": outcome.gate_2a.status.value,
                "qc": {stage: report.verdict.value for stage, report in outcome.qc.items()},
                "run_dir": str(run.run_dir(run_id)),
            }
        )
        return 0

    level2 = run.read_level2(run_id)
    sheet = run.read_build_sheet(run_id)

    if command == "om-source":
        from .openmontage_source import search_for_asset

        om_source = search_for_asset(
            str(args.asset),
            str(args.query),
            run.run_dir(run_id),
            run_id,
            route=str(args.route),
            kind=str(args.kind),
            limit=int(args.limit),
            attempt=str(args.attempt),
        )
        _print(
            {
                "asset_id": om_source.asset_id,
                "project_id": om_source.project_id,
                "job_id": om_source.job_id,
                "route": om_source.route,
                "candidates": len(om_source.candidates),
                "budget_usd": om_source.budget_usd,
                "spent_usd": om_source.spent_usd,
                "note": om_source.note,
            }
        )
        return 0

    if command == "omcheck":
        from .openmontage_check import run_openmontage_check

        check = run_openmontage_check(
            run.run_dir(run_id),
            run_id,
            query=str(args.query),
            budget_usd=float(args.budget),
            capability_check=True,
        )
        _print(
            {
                "project_id": check.project_id,
                "stock": check.stock_title,
                "stock_sha256": check.stock_sha256,
                "render": check.render_reference,
                "render_sha256": check.render_sha256,
                "verification": check.render_verification,
                "budget_usd": check.budget_usd,
                "spent_usd": check.spent_usd,
            }
        )
        return 0

    if command == "credentials":
        from .credentials import status_report

        _print(status_report())
        return 0

    if command == "stockcheck":
        from .stockcheck import render_stock_check, run_stock_check

        stock_report = run_stock_check(Path(str(args.media_dir)), str(args.query))
        run.write_data(run_id, "stock-check/stock-check.json", stock_report.model_dump(mode="json"))
        run.write_text(run_id, "stock-check/stock-check.md", render_stock_check(stock_report))
        _print(
            {
                "query": args.query,
                "ok": stock_report.ok_count,
                "total": len(stock_report.items),
                "report": str(run.run_dir(run_id) / "stock-check" / "stock-check.md"),
                "media_dir": str(Path(str(args.media_dir)).resolve()),
            }
        )
        return 0

    if command == "voice":
        from .agents import VoiceAgent

        plan = store.load_plan(project_id, revision)
        text = args.text
        if not text:
            cue = next((cue for cue in plan.audio_cues if cue.kind.value == "vo"), None)
            if cue is None:
                _print({"error": "no voice cue in the plan"})
                return 2
            text = cue.description.split("Canonical read:", 1)[-1].strip()
        destination = run.run_dir(run_id) / "generated" / "AS-15-edge-sample.mp3"
        result = VoiceAgent().sample(text, destination, str(args.voice))
        recorded = result.model_copy(update={"path": f"generated/{destination.name}"})
        run.write_json(run_id, "voice-sample.json", recorded)
        transcript = None
        if args.transcribe:
            from pathlib import Path as _Path

            transcript = VoiceAgent().transcribe(_Path(result.path))
            run.write_data(run_id, "transcription.json", transcript)
        run.write_data(
            run_id,
            "shortgpt-status.json",
            {
                "edge_tts": "working",
                "transcription": "working" if transcript else "available",
                "transcription_backend": ("cached faster-whisper tiny.en (local, no download)"),
                "sample_path": recorded.path,
                "duration_seconds": recorded.duration_seconds,
            },
        )
        _print(
            {
                "provider": result.provider,
                "voice": result.voice,
                "duration_seconds": result.duration_seconds,
                "bytes": result.bytes,
                "path": recorded.path,
                "disclosure": result.disclosure_text,
            }
        )
        return 0

    if command == "source":
        from .agents import SourcingAgent
        from .sourcing import DEFAULT_QUERIES

        selected = {
            asset_id: DEFAULT_QUERIES[asset_id]
            for asset_id in (args.asset or list(DEFAULT_QUERIES))
            if asset_id in DEFAULT_QUERIES
        }
        sourcing_report = SourcingAgent().discover(
            store,
            project_id,
            revision,
            run_id,
            queries=selected,
            limit=int(args.limit),
            openmontage=bool(args.openmontage),
            openmontage_asset=str(args.om_asset),
            openmontage_attempt=str(args.om_attempt),
        )
        om_path = run.run_dir(run_id) / "openmontage-sourcing.json"
        om_summary = (
            json.loads(om_path.read_text(encoding="utf-8"))
            if args.openmontage and om_path.is_file()
            else None
        )
        _print(
            {
                "run": run_id,
                "assets": [
                    {
                        "asset_id": asset.asset_id,
                        "status": asset.status,
                        "candidates": len(asset.candidates),
                        "chosen": asset.chosen_candidate,
                    }
                    for asset in sourcing_report.assets
                ],
                "openmontage": (
                    {
                        "asset_id": om_summary.get("asset_id"),
                        "project_id": om_summary.get("project_id"),
                        "job_id": om_summary.get("job_id"),
                        "route": om_summary.get("route"),
                        "candidates": len(om_summary.get("candidates", [])),
                        "budget_usd": om_summary.get("budget_usd"),
                        "spent_usd": om_summary.get("spent_usd"),
                    }
                    if om_summary
                    else None
                ),
                "report": str(run.run_dir(run_id) / "sourcing-report.md"),
            }
        )
        return 0

    if command == "build":
        from .build import run_build

        report = run_build(store, project_id, revision, run_id)
        _print(
            {
                "run": run_id,
                "processed": report.processed,
                "blocked": report.blocked,
                "conditional": report.conditional,
                "spent_usd": report.spent_usd,
                "report": str(run.run_dir(run_id) / "build-report.json"),
            }
        )
        return 0

    if command == "budget":
        from .review_pack import render_budget

        plan = store.load_plan(project_id, revision)
        _print(render_budget(level2.budget, plan))
        return 0

    if command == "review":
        _print(
            {
                "review_pack": str(run.run_dir(run_id) / "review-pack.md"),
                "review_docx": str(run.run_dir(run_id) / "review-pack.docx"),
                "budget": str(run.run_dir(run_id) / "budget-estimate.md"),
                "items": len(level2.intents) + len(level2.decisions),
            }
        )
        return 0

    if command == "qc":
        reports = {
            stage: QcReport.model_validate(
                json.loads(
                    (run.run_dir(run_id) / "qc" / f"{stage}.json").read_text(encoding="utf-8")
                )
            )
            for stage in ("technical", "semantic", "rights", "budget", "visual")
        }
        _print(
            {
                stage: {
                    "verdict": report.verdict.value,
                    "findings": len(report.findings),
                    "failures": [
                        finding.id for finding in report.findings if finding.verdict.value == "fail"
                    ],
                }
                for stage, report in reports.items()
            }
        )
        return 0

    if command == "spend":
        from .governance import open_governor

        if level2.provider_budget is None:
            _print({"error": "no provider budget configured for this run"})
            return 2
        governor = open_governor(run.run_dir(run_id), level2.provider_budget)
        _print(
            {
                "run": run_id,
                "providers": level2.provider_budget.providers,
                **governor.summary().model_dump(mode="json"),
            }
        )
        return 0

    if command == "status":
        _print(
            {
                "run": run_id,
                "state": level2.state.value,
                "plan_hash": level2.plan_hash,
                "assets": len(level2.intents),
                "layers": len(level2.decisions),
                "budget_total": level2.budget.summary.total_usd,
                "budget_worst": level2.budget.summary.worst_usd,
                "budget_cap": level2.budget.summary.cap_usd,
                "budget_mode": level2.budget.mode,
                "in_kind": level2.budget.in_kind_usd,
                "provider_cap": (
                    level2.provider_budget.cap_usd if level2.provider_budget is not None else None
                ),
                "blockers": len(level2.blockers),
                "gate_2a": _packet_status(run, run_id, "2a"),
            }
        )
        return 0

    if command == "gate":
        return _gate_command(store, run, run_id, project_id, revision, level2, sheet, args)

    if command == "correct":
        plan = store.load_plan(project_id, revision)
        return _correct_command(store, run, run_id, project_id, revision, plan, level2, args)

    raise PinConvError(f"unknown Level 2 command: {command}")


def _packet_status(run: Level2RunStore, run_id: str, gate: str) -> str:
    path = run.run_dir(run_id) / "gate2" / f"packet-{gate}.json"
    if not path.is_file():
        return "missing"
    packet = GatePacket.model_validate_json(path.read_text(encoding="utf-8"))
    return packet.status.value


def _gate_command(
    store: ProjectStore,
    run: Level2RunStore,
    run_id: str,
    project_id: str,
    revision: int,
    level2: object,
    sheet: object,
    args: argparse.Namespace,
) -> int:
    from .models import BuildSheet, GatePacket, Level2Plan

    assert isinstance(level2, Level2Plan)
    assert isinstance(sheet, BuildSheet)
    gate = str(args.gate)
    plan = store.load_plan(project_id, revision)

    if gate == "2a":
        packet = GatePacket.model_validate_json(
            (run.run_dir(run_id) / "gate2" / "packet-2a.json").read_text(encoding="utf-8")
        )
        if args.approve:
            approved = approve_packet(
                packet,
                approver=str(args.reviewer),
                role=str(args.role),
                evidence=str(args.evidence),
                confirmation=str(args.confirm),
            )
            run.write_json(run_id, "gate2/packet-2a.json", approved)
            run.write_json(
                run_id,
                "run.json",
                level2.model_copy(update={"state": RunState.BUDGET_APPROVED}),
            )
            run.append_event(
                run_id,
                "gate2a.approved",
                {"approver": approved.approved_by, "evidence": approved.approval_evidence},
            )
            _print(
                {
                    "gate": "2a",
                    "status": approved.status.value,
                    "approved_by": approved.approved_by,
                    "approved_at": approved.approved_at,
                }
            )
            return 0
        _print(
            {
                "gate": "2a",
                "status": packet.status.value,
                "checks": [
                    {"id": check.id, "name": check.name, "state": check.state.value}
                    for check in packet.checks
                ],
                "blockers": packet.blockers,
            }
        )
        return 0

    if gate == "2b":
        packet_2a = GatePacket.model_validate_json(
            (run.run_dir(run_id) / "gate2" / "packet-2a.json").read_text(encoding="utf-8")
        )
        if packet_2a.status is not PacketStatus.APPROVED:
            _print({"gate": "2b", "error": "Gate 2A is not approved"})
            return 2
        from .engines.base import SpendLedger

        ledger = SpendLedger(run.run_dir(run_id) / "spend-ledger.jsonl")
        reports = {
            stage: QcReport.model_validate(
                json.loads(
                    (run.run_dir(run_id) / "qc" / f"{stage}.json").read_text(encoding="utf-8")
                )
            )
            for stage in ("technical", "semantic", "rights", "budget", "visual")
        }
        packet = evaluate_2b(
            plan,
            level2,
            sheet,
            reports,
            packet_2a,
            receipts=ledger.receipts(),
            open_reservations=ledger.open_reservations(),
        )
        run.write_json(run_id, "gate2/packet-2b.json", packet)
        if args.approve:
            packet = approve_packet(
                packet,
                approver=str(args.reviewer),
                role=str(args.role),
                evidence=str(args.evidence),
                confirmation=str(args.confirm),
            )
            run.write_json(run_id, "gate2/packet-2b.json", packet)
            run.write_json(
                run_id,
                "run.json",
                level2.model_copy(update={"state": RunState.GATE2_READY}),
            )
        _print({"gate": "2b", "status": packet.status.value, "blockers": packet.blockers})
        return 0

    if gate == "2c":
        packet_2b = GatePacket.model_validate_json(
            (run.run_dir(run_id) / "gate2" / "packet-2b.json").read_text(encoding="utf-8")
        )
        if packet_2b.status is not PacketStatus.APPROVED:
            _print({"gate": "2c", "error": "Gate 2B is not approved"})
            return 2
        deliverables = [str(path) for path in args.deliverable if Path(str(path)).is_file()]
        packet = evaluate_2c(
            plan,
            level2,
            packet_2b,
            deliverables=deliverables,
            duration_ok=bool(deliverables),
            audio_ok=bool(deliverables),
            captions_ok=bool(args.captions_ok),
            reviewer=args.reviewer_name,
        )
        run.write_json(run_id, "gate2/packet-2c.json", packet)
        _print({"gate": "2c", "status": packet.status.value, "blockers": packet.blockers})
        return 0

    raise PinConvError(f"unknown gate: {gate}")


def _correct_command(
    store: ProjectStore,
    run: Level2RunStore,
    run_id: str,
    project_id: str,
    revision: int,
    plan: ProductionPlan,
    level2: Level2Plan,
    args: argparse.Namespace,
) -> int:
    if args.apply:
        from .planner import apply_corrections

        outcome = apply_corrections(store, project_id, revision, run_id, Path(str(args.input)))
        _print(
            {
                "target_run": outcome.level2.run_id,
                "state": outcome.level2.state.value,
                "assets": len(outcome.level2.intents),
                "layers": len(outcome.level2.decisions),
                "corrections": len(outcome.sheet.corrections),
                "gate_2a": outcome.gate_2a.status.value,
            }
        )
        return 0
    corrections = load_corrections(Path(str(args.input)))
    summary = validate_corrections(corrections, plan)
    target = next_run_id(run_id) if args.new_run is None else str(args.new_run)
    write_jsonl(run.run_dir(target) / "corrections.jsonl", corrections)
    run.append_event(
        run_id,
        "level2.corrections",
        {
            "target_run": target,
            "total": summary.total,
            "affected": summary.affected_items,
            "creative": summary.creative_escalations,
        },
    )
    _print(
        {
            "target_run": target,
            "total": summary.total,
            "affected_items": summary.affected_items,
            "creative_escalations": summary.creative_escalations,
            "note": "rev-002 is unchanged; re-plan the affected items into the new run.",
            "created_at": utc_now(),
        }
    )
    return 0
