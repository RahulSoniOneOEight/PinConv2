"""Command-line interface for Level 1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .errors import PinConvError
from .fixtures import FIXTURES
from .service import (
    DEFAULT_PROJECT,
    build_gate_packet,
    init_project,
    run_all,
    run_approval,
    run_concept,
    run_critique,
    run_export,
    run_plan,
    run_previews,
    run_research,
    run_resolution,
    run_validation,
    status,
)
from .store import ProjectStore


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", default=DEFAULT_PROJECT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pinconv2",
        description="PinConv2 Level 1: research and production planning",
    )
    parser.add_argument(
        "--data-dir",
        default="projects",
        help="project root (default: projects)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create the Level 1 project from a fixture")
    init.add_argument("--fixture", default=DEFAULT_PROJECT, choices=sorted(FIXTURES))

    for name, help_text in [
        ("research", "record the research pack"),
        ("concept", "write the concept note"),
        ("plan", "write the executable production plan"),
        ("resolve-inputs", "apply the top-three critique inputs and create revision 2"),
        ("gate1", "assemble and check the Gate 1 packet"),
        ("previews", "write static SVG layout mockups for the latest plan"),
        ("export", "export the approved concept note, plan and handoff"),
        ("status", "show project state and latest hashes"),
    ]:
        command = sub.add_parser(name, help=help_text)
        _common(command)

    validate = sub.add_parser("validate", help="run deterministic plan validation")
    _common(validate)
    validate.add_argument("--revision", type=int, default=None)

    critique = sub.add_parser("critique", help="run the independent critique")
    _common(critique)
    critique.add_argument("--revision", type=int, default=None)

    approve = sub.add_parser("approve", help="record a named human Gate 1 approval")
    _common(approve)
    approve.add_argument("--reviewer", required=True)
    approve.add_argument("--role", required=True)
    approve.add_argument(
        "--evidence",
        required=True,
        help="ticket, email or signed-note reference for the human decision",
    )
    approve.add_argument(
        "--confirm",
        required=True,
        choices=["APPROVE"],
        help="type APPROVE to confirm this is a human decision",
    )
    approve.add_argument(
        "--channel",
        required=True,
        help="where the human decision happened (cli, email, signed-file, meeting)",
    )
    approve.add_argument(
        "--scope",
        default=None,
        help="comma-separated shot ids; defaults to the ready shots",
    )
    approve.add_argument(
        "--approve-exact-data",
        default=None,
        help="comma-separated exact-data ids, or 'all' for every pending value",
    )
    approve.add_argument(
        "--approve-variants",
        default=None,
        help="comma-separated variant ids, or 'all' for every ready variant",
    )
    approve.add_argument("--condition", action="append", default=[])
    approve.add_argument("--note", default=None)

    run_all_parser = sub.add_parser(
        "run-all",
        help="run init through Gate 1 packet; stops before human approval",
    )
    run_all_parser.add_argument("--fixture", default=DEFAULT_PROJECT, choices=sorted(FIXTURES))

    level2 = sub.add_parser("level2", help="Level 2 asset production planning")
    level2_sub = level2.add_subparsers(dest="level2_command", required=True)
    for name, help_text in [
        ("ingest", "validate the approved handoff and print its hashes"),
        ("plan", "derive decisions, budget, flow, build sheet and Gate 2A packet"),
        ("budget", "print the Level 2 budget estimate"),
        ("review", "print the review pack paths"),
        ("qc", "print deterministic QC verdicts"),
        ("status", "show the Level 2 run state"),
        ("credentials", "show which provider credentials are available"),
        ("stockcheck", "fetch and probe one item from each stock source"),
        ("voice", "render a disclosed Edge TTS sample for the fallback voice"),
        ("omcheck", "run a separate OpenMontage stock and render capability check"),
        ("om-source", "search OpenMontage stock candidates for one film asset"),
        ("stock-plan", "build the stock sourcing plan and fetch stock candidates"),
        ("build", "process imported sources after Gate 2A approval"),
        ("correct", "validate typed corrections and open a new run"),
    ]:
        command = level2_sub.add_parser(name, help=help_text)
        _common(command)
        command.add_argument("--revision", type=int, default=None)
        command.add_argument("--run", default=None)
    level2_sub.choices["plan"].add_argument(
        "--cap",
        type=float,
        default=None,
        help="operator spend cap in USD; cannot exceed the approved cap silently",
    )
    level2_sub.choices["plan"].add_argument(
        "--lean",
        action="store_true",
        help="zero-cash in-kind production mode; substitutions need Gate 2A approval",
    )
    level2_sub.choices["plan"].add_argument(
        "--provider-cap",
        type=float,
        default=None,
        help="shared fal.ai + Runware production cap in USD",
    )
    level2_sub.choices["plan"].add_argument(
        "--per-job-cap",
        type=float,
        default=0.5,
        help="maximum quote for any single provider job",
    )
    stockcheck = level2_sub.add_parser(
        "stockcheck", help="fetch and probe one item from each stock source"
    )
    _common(stockcheck)
    stockcheck.add_argument("--revision", type=int, default=None)
    stockcheck.add_argument("--run", default=None)
    stockcheck.add_argument("--query", default="coffee")
    stockcheck.add_argument("--media-dir", default="dist/stock-check")

    voice = level2_sub.add_parser(
        "voice", help="render a disclosed Edge TTS sample for the fallback voice"
    )
    _common(voice)
    voice.add_argument("--revision", type=int, default=None)
    voice.add_argument("--run", default=None)
    voice.add_argument("--text", default=None)
    voice.add_argument("--voice", default="en-IN-NeerjaNeural")
    voice.add_argument("--transcribe", action="store_true")

    omcheck = level2_sub.add_parser(
        "omcheck", help="run a separate OpenMontage stock and render capability check"
    )
    _common(omcheck)
    omcheck.add_argument("--revision", type=int, default=None)
    omcheck.add_argument("--run", default=None)
    omcheck.add_argument("--query", default="coffee")
    omcheck.add_argument("--budget", type=float, default=2.0)

    omsource = level2_sub.add_parser(
        "om-source", help="search OpenMontage stock candidates for one film asset"
    )
    _common(omsource)
    omsource.add_argument("--revision", type=int, default=None)
    omsource.add_argument("--run", default=None)
    omsource.add_argument("--asset", default="AS-14")
    omsource.add_argument("--query", default="warm acoustic coffee instrumental")
    omsource.add_argument("--kind", default="audio")
    omsource.add_argument("--route", default="openverse.stock")
    omsource.add_argument("--limit", type=int, default=5)
    omsource.add_argument("--attempt", default="1")

    stockplan = level2_sub.add_parser(
        "stock-plan", help="build the stock sourcing plan and fetch stock candidates"
    )
    _common(stockplan)
    stockplan.add_argument("--revision", type=int, default=None)
    stockplan.add_argument("--run", default=None)
    level2_sub.add_parser("spend", help="show fal.ai/Runware budget and spend")
    spend = level2_sub.choices["spend"]
    _common(spend)
    spend.add_argument("--revision", type=int, default=None)
    spend.add_argument("--run", default=None)

    source = level2_sub.add_parser("source", help="search, gate and preview music candidates")
    _common(source)
    source.add_argument("--revision", type=int, default=None)
    source.add_argument("--run", default=None)
    source.add_argument("--asset", action="append", default=[])
    source.add_argument("--limit", type=int, default=5)
    source.add_argument(
        "--openmontage",
        action="store_true",
        help="also run an OpenMontage stock search for one representative asset",
    )
    source.add_argument("--om-asset", default="AS-07")
    source.add_argument("--om-attempt", default="1")
    correct = level2_sub.choices["correct"]
    correct.add_argument("--input", required=True, help="corrections.jsonl")
    correct.add_argument("--new-run", default=None)
    correct.add_argument(
        "--apply",
        action="store_true",
        help="build a new run that carries the accepted corrections",
    )

    gate = level2_sub.add_parser("gate", help="inspect or record a Gate 2 decision")
    _common(gate)
    gate.add_argument("--revision", type=int, default=None)
    gate.add_argument("--run", default=None)
    gate.add_argument("--gate", required=True, choices=["2a", "2b", "2c"])
    gate.add_argument("--approve", action="store_true")
    gate.add_argument("--reviewer", default=None)
    gate.add_argument("--role", default=None)
    gate.add_argument("--evidence", default=None)
    gate.add_argument("--confirm", default="")
    gate.add_argument("--deliverable", action="append", default=[])
    gate.add_argument("--captions-ok", action="store_true")
    gate.add_argument("--reviewer-name", default=None)

    return parser


def _print(value: object) -> None:
    if isinstance(value, str):
        print(value)
    else:
        print(json.dumps(value, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = ProjectStore(Path(args.data_dir))
    project = getattr(args, "project", DEFAULT_PROJECT)
    try:
        if args.command == "level2":
            from .level2.cli import run_level2_command

            return run_level2_command(store, args)
        if args.command == "init":
            created = init_project(store, args.fixture)
            _print(
                {
                    "project": created.id,
                    "state": created.state.value,
                    "title": created.title,
                }
            )
        elif args.command == "research":
            result = run_research(store, project)
            _print({"state": result.state.value})
        elif args.command == "concept":
            result = run_concept(store, project)
            _print({"state": result.state.value})
        elif args.command == "plan":
            result = run_plan(store, project)
            _print({"state": result.state.value})
        elif args.command == "validate":
            validation_report = run_validation(store, project, args.revision)
            _print(
                {
                    "plan_revision": validation_report.plan_revision,
                    "plan_hash": validation_report.plan_hash,
                    "passed": validation_report.passed,
                    "failures": [
                        {
                            "rule": finding.rule,
                            "target": finding.target,
                            "detail": finding.detail,
                        }
                        for finding in validation_report.failures
                    ],
                    "warnings": len(validation_report.warnings),
                }
            )
            return 0 if validation_report.passed else 1
        elif args.command == "critique":
            critique_report = run_critique(store, project, args.revision)
            _print(
                {
                    "plan_revision": critique_report.plan_revision,
                    "plan_hash": critique_report.plan_hash,
                    "findings": [
                        {
                            "id": finding.id,
                            "category": finding.category,
                            "severity": finding.severity.value,
                            "priority": finding.priority,
                            "owner": finding.owner.value,
                        }
                        for finding in critique_report.findings
                    ],
                    "top3": critique_report.top3,
                }
            )
        elif args.command == "resolve-inputs":
            plan = run_resolution(store, project)
            _print(
                {
                    "plan_revision": plan.revision,
                    "plan_hash": plan.plan_hash(),
                }
            )
        elif args.command == "gate1":
            packet = build_gate_packet(store, project)
            _print(
                {
                    "plan_revision": packet.plan_revision,
                    "plan_hash": packet.plan_hash,
                    "validation_passed": packet.validation_passed,
                    "ready_shots": packet.ready_shots,
                    "conditions": packet.conditions,
                    "blockers": packet.blockers,
                }
            )
        elif args.command == "approve":
            approved_exact: list[str] | None = None
            if args.approve_exact_data == "all":
                plan_revision = store.latest_plan_revision(project)
                packet = store.load_packet(project, plan_revision)
                approved_exact = list(packet.exact_data_pending)
            elif args.approve_exact_data:
                approved_exact = [
                    item.strip() for item in args.approve_exact_data.split(",") if item.strip()
                ]
            approved_variants: list[str] | None = None
            if args.approve_variants == "all":
                plan_revision = store.latest_plan_revision(project)
                packet = store.load_packet(project, plan_revision)
                approved_variants = list(packet.ready_variants)
            elif args.approve_variants:
                approved_variants = [
                    item.strip() for item in args.approve_variants.split(",") if item.strip()
                ]
            approval = run_approval(
                store,
                project,
                approver=args.reviewer,
                role=args.role,
                evidence=args.evidence,
                actor_kind="human",
                human_confirmation=args.confirm,
                channel=args.channel,
                scope=[item.strip() for item in args.scope.split(",")] if args.scope else None,
                approved_exact_data=approved_exact,
                approved_variants=approved_variants,
                conditions=list(args.condition),
                note=args.note,
            )
            _print(
                {
                    "approved": True,
                    "plan_revision": approval.plan_revision,
                    "plan_hash": approval.plan_hash,
                    "bundle_hash": approval.bundle_hash,
                    "packet_hash": approval.packet_hash,
                    "approver": approval.approver,
                    "scope": approval.scope,
                    "approved_exact_data": approval.approved_exact_data,
                    "approved_variants": approval.approved_variants,
                }
            )
        elif args.command == "previews":
            paths = run_previews(store, project)
            _print([str(path) for path in paths])
        elif args.command == "export":
            paths = run_export(store, project)
            _print([str(path) for path in paths])
        elif args.command == "status":
            _print(status(store, project))
        elif args.command == "run-all":
            _print(run_all(store, args.fixture))
        return 0
    except PinConvError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
