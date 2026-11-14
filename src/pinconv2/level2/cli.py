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
        outcome = plan_level2(store, project_id, revision, run_id)
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
                    "subtotal": summary.subtotal_usd,
                    "reserve": summary.reserve_usd,
                    "total": summary.total_usd,
                    "worst": summary.worst_usd,
                    "cap": summary.cap_usd,
                    "headroom": summary.headroom_usd,
                },
                "gate_2a": outcome.gate_2a.status.value,
                "qc": {stage: report.verdict.value for stage, report in outcome.qc.items()},
                "run_dir": str(run.run_dir(run_id)),
            }
        )
        return 0

    level2 = run.read_level2(run_id)
    sheet = run.read_build_sheet(run_id)

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
