"""Level 1 application service.

The CLI is a thin wrapper around these functions. Every function validates the
predecessor state, writes its record, and only then advances the project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .critique import build_resolution_inputs, critique_plan
from .errors import GateFailedError, NotFoundError, StoreError
from .fixtures import (
    FIXTURES,
    build_brief,
    build_concept_note,
    build_plan,
    build_research_pack,
)
from .fixtures.toffee_plan import revision_two_applied
from .models import (
    CheckLevel,
    CheckStatus,
    CritiqueReport,
    Disposition,
    Gate1Approval,
    Gate1Packet,
    InputResolution,
    ProductionPlan,
    Project,
    ProjectState,
    ResolutionMode,
    ResolutionReport,
    ResolutionStatus,
    ValidationReport,
)
from .preview import write_previews
from .render import (
    build_handoff,
    render_concept_note,
    render_gate_packet,
    render_production_plan,
)
from .store import ProjectStore
from .validators import validate_plan
from .workflow import advance as next_state
from .workflow import require_state

DEFAULT_PROJECT = "toffee-coffee-10s"


def _project(store: ProjectStore, project_id: str) -> Project:
    return store.load_project(project_id)


def init_project(store: ProjectStore, fixture: str = DEFAULT_PROJECT) -> Project:
    if fixture not in FIXTURES:
        raise NotFoundError(
            f"unknown fixture {fixture!r}; implemented fixtures: {', '.join(FIXTURES)}"
        )
    if store.project_dir(DEFAULT_PROJECT).joinpath("project.json").exists():
        raise StoreError(f"project already exists: {DEFAULT_PROJECT}")
    brief = build_brief()
    project = Project(
        id=DEFAULT_PROJECT,
        title=FIXTURES[fixture],
        state=ProjectState.INIT,
    )
    store.create_project(project)
    store.save_brief(brief)
    project = next_state(project, ProjectState.INTAKE)
    store.save_project(project)
    store.append_event(
        DEFAULT_PROJECT,
        "brief.normalised",
        {
            "content_family": brief.content_family.value,
            "duration_seconds": brief.duration_seconds,
            "fps": brief.fps,
            "must_have": len(brief.must_have),
        },
    )
    return project


def run_research(store: ProjectStore, project_id: str = DEFAULT_PROJECT) -> Project:
    project = _project(store, project_id)
    require_state(project, ProjectState.INTAKE)
    pack = build_research_pack()
    store.save_research(pack)
    project = next_state(project, ProjectState.RESEARCH)
    store.save_project(project)
    return project


def run_concept(store: ProjectStore, project_id: str = DEFAULT_PROJECT) -> Project:
    project = _project(store, project_id)
    require_state(project, ProjectState.RESEARCH)
    store.load_research(project_id)
    concept = build_concept_note()
    store.save_concept(concept)
    project = next_state(project, ProjectState.TREATMENT)
    store.save_project(project)
    return project


def run_plan(store: ProjectStore, project_id: str = DEFAULT_PROJECT) -> Project:
    project = _project(store, project_id)
    require_state(project, ProjectState.TREATMENT)
    store.load_brief(project_id)
    store.load_research(project_id)
    store.load_concept(project_id)
    plan = build_plan(project_id=project_id)
    store.save_plan(plan)
    project = store.set_plan_revision(project_id, plan.revision)
    project = next_state(project, ProjectState.SHOT_PLAN)
    store.save_project(project)
    return project


def run_validation(
    store: ProjectStore, project_id: str = DEFAULT_PROJECT, revision: int | None = None
) -> ValidationReport:
    project = _project(store, project_id)
    require_state(
        project,
        ProjectState.SHOT_PLAN,
        ProjectState.VALIDATED,
        ProjectState.INPUTS_UPDATED,
    )
    latest = store.latest_plan_revision(project_id)
    if revision is not None and revision != latest:
        raise GateFailedError(
            f"revision {revision} is not the latest plan revision ({latest})"
        )
    plan = store.load_plan(project_id, latest)
    brief = store.load_brief(project_id)
    report = validate_plan(plan, brief)
    store.save_validation(report)
    if project.state is not ProjectState.VALIDATED:
        project = next_state(project, ProjectState.VALIDATED)
        store.save_project(project)
    return report


def run_critique(
    store: ProjectStore, project_id: str = DEFAULT_PROJECT, revision: int | None = None
) -> CritiqueReport:
    project = _project(store, project_id)
    require_state(project, ProjectState.VALIDATED, ProjectState.CRITIQUED)
    latest = store.latest_plan_revision(project_id)
    if revision is not None and revision != latest:
        raise GateFailedError(
            f"revision {revision} is not the latest plan revision ({latest})"
        )
    plan = store.load_plan(project_id, latest)
    validation = store.load_validation(project_id, plan.revision)
    brief = store.load_brief(project_id)
    report = critique_plan(plan, brief, validation)
    store.save_critique(report)
    if project.state is not ProjectState.CRITIQUED:
        project = next_state(project, ProjectState.CRITIQUED)
        store.save_project(project)
    return report


def run_resolution(store: ProjectStore, project_id: str = DEFAULT_PROJECT) -> ProductionPlan:
    project = _project(store, project_id)
    require_state(project, ProjectState.CRITIQUED)
    plan = store.load_latest_plan(project_id)
    critique = store.load_critique(project_id, plan.revision)
    if not critique.top3:
        raise GateFailedError("critique has no high-impact inputs to resolve")
    if plan.revision >= 2:
        raise GateFailedError(
            "v0.1 supports one plan revision cycle; revision 2 is already written"
        )

    actions = build_resolution_inputs(critique)
    inputs = [
        InputResolution(
            id=f"IR-{index:02d}",
            critique_finding_id=str(action["finding_id"]),
            rank=int(action["rank"]),
            mode=ResolutionMode(str(action["mode"])),
            decision=str(action["decision"]),
            changes=[str(change) for change in action["changes"]],
            impacted_ids=[str(item) for item in action["impacted_ids"]],
            status=ResolutionStatus(str(action["status"])),
        )
        for index, action in enumerate(actions, start=1)
    ]

    new_plan = build_plan(
        project_id=project_id,
        revision=plan.revision + 1,
        applied=revision_two_applied(),
    )
    store.save_plan(new_plan)
    report = ResolutionReport(
        project_id=project_id,
        from_revision=plan.revision,
        to_revision=new_plan.revision,
        inputs=inputs,
        notes=(
            "Top three inputs resolved or escalated. The planner also applied the "
            "pack-capture fallback and the music/voice rights route as hardening; both "
            "remain Gate 1 conditions."
        ),
    )
    store.save_resolution(report)
    project = store.set_plan_revision(project_id, new_plan.revision)
    project = next_state(project, ProjectState.INPUTS_UPDATED)
    store.save_project(project)
    return new_plan


def _l1_check_failures(plan: ProductionPlan, validation: ValidationReport) -> list[str]:
    failures: list[str] = []
    for check in plan.checks:
        if check.level is not CheckLevel.L1:
            continue
        status = validation.check_status.get(check.id, CheckStatus.PENDING)
        if status is not CheckStatus.PASS:
            failures.append(f"{check.id} is {status.value} ({check.description})")
    return failures


def run_previews(
    store: ProjectStore, project_id: str = DEFAULT_PROJECT
) -> list[Path]:
    project = _project(store, project_id)
    require_state(
        project,
        ProjectState.SHOT_PLAN,
        ProjectState.VALIDATED,
        ProjectState.CRITIQUED,
        ProjectState.INPUTS_UPDATED,
        ProjectState.GATE1_READY,
        ProjectState.APPROVED,
    )
    plan = store.load_latest_plan(project_id)
    directory = store.project_dir(project_id) / "previews" / f"rev-{plan.revision:03d}"
    paths = write_previews(plan, directory)
    store.append_event(
        project_id,
        "previews.written",
        {
            "revision": plan.revision,
            "files": [path.name for path in paths],
        },
    )
    return paths


def build_gate_packet(
    store: ProjectStore, project_id: str = DEFAULT_PROJECT
) -> Gate1Packet:
    project = _project(store, project_id)
    require_state(project, ProjectState.CRITIQUED, ProjectState.GATE1_READY)
    plan = store.load_latest_plan(project_id)
    validation = store.load_validation(project_id, plan.revision)
    critique = store.load_critique(project_id, plan.revision)
    resolution = store.latest_resolution(project_id)

    blockers: list[str] = []
    if validation.plan_hash != plan.plan_hash():
        blockers.append("validation is bound to a different plan hash")
    if critique.plan_hash != plan.plan_hash():
        blockers.append("critique is bound to a different plan hash")
    if not validation.passed:
        blockers.extend(
            f"{finding.rule}: {finding.detail}" for finding in validation.failures
        )
    blockers.extend(
        f"{finding.id} ({finding.category}) is still open: {finding.observation}"
        for finding in critique.open_blockers
    )
    blockers.extend(_l1_check_failures(plan, validation))
    if critique.top3:
        covered = (
            {item.critique_finding_id for item in resolution.inputs}
            if resolution is not None
            else set()
        )
        missing = [finding_id for finding_id in critique.top3 if finding_id not in covered]
        if missing:
            blockers.append(f"top-three inputs have no resolution record: {missing}")

    conditions = [
        f"{finding.rule}: {finding.detail}" for finding in validation.warnings
    ]
    conditions.extend(
        f"{finding.id} ({finding.category}): {finding.observation}"
        for finding in critique.findings
        if finding.severity.value in {"medium", "low"}
        and finding.disposition is Disposition.OPEN
    )

    packet = Gate1Packet(
        project_id=project_id,
        plan_revision=plan.revision,
        plan_hash=plan.plan_hash(),
        validation_passed=validation.passed,
        ready_shots=[shot.id for shot in plan.shots if shot.status.value == "ready"],
        held_layers=[
            layer.id
            for layer in plan.layers
            if not layer.required
            or (
                layer.binding_ref is not None
                and layer.binding_kind.value == "copy"
                and plan.copy_map[layer.binding_ref].status.value == "held"
            )
        ],
        conditions=sorted(set(conditions)),
        blockers=sorted(set(blockers)),
        input_statuses=(
            {item.critique_finding_id: item.status.value for item in resolution.inputs}
            if resolution is not None
            else {}
        ),
    )
    store.save_packet(packet)
    if packet.blockers:
        raise GateFailedError(
            "Gate 1 is blocked:\n- " + "\n- ".join(packet.blockers)
        )
    project = next_state(project, ProjectState.GATE1_READY)
    store.save_project(project)
    return packet


def run_approval(
    store: ProjectStore,
    project_id: str,
    *,
    approver: str,
    role: str,
    scope: list[str] | None = None,
    conditions: list[str] | None = None,
    note: str | None = None,
) -> Gate1Approval:
    project = _project(store, project_id)
    require_state(project, ProjectState.GATE1_READY)
    plan = store.load_latest_plan(project_id)
    packet = store.load_packet(project_id, plan.revision)
    if packet.blockers:
        raise GateFailedError("Gate 1 packet still has blockers")
    if not packet.validation_passed:
        raise GateFailedError("Gate 1 requires a passing validation report")
    if packet.plan_hash != plan.plan_hash():
        raise GateFailedError("Gate 1 packet is bound to a different plan hash")

    approved_scope = scope or packet.ready_shots
    known_shots = {shot.id for shot in plan.shots}
    unknown = [item for item in approved_scope if item not in known_shots]
    if unknown:
        raise GateFailedError(f"approval scope contains unknown shots: {unknown}")
    if not approved_scope:
        raise GateFailedError("approval scope is empty")

    approval = Gate1Approval(
        project_id=project_id,
        plan_revision=plan.revision,
        plan_hash=plan.plan_hash(),
        approver=approver,
        approver_role=role,
        scope=approved_scope,
        conditions=sorted(set(packet.conditions + (conditions or []))),
        note=note,
    )
    store.save_approval(approval)
    store.save_packet(packet.model_copy(update={"approval": approval}))
    project = next_state(project, ProjectState.APPROVED)
    store.save_project(project)
    return approval


def run_export(store: ProjectStore, project_id: str = DEFAULT_PROJECT) -> list[Path]:
    project = _project(store, project_id)
    require_state(project, ProjectState.APPROVED)
    plan = store.load_latest_plan(project_id)
    approval = store.load_approval(project_id, plan.revision)
    if approval.plan_hash != plan.plan_hash():
        raise GateFailedError("approval is bound to a different plan hash")
    validation = store.load_validation(project_id, plan.revision)
    critique = store.load_critique(project_id, plan.revision)
    packet = store.load_packet(project_id, plan.revision)
    brief = store.load_brief(project_id)
    research = store.load_research(project_id)
    concept = store.load_concept(project_id)

    handoff = build_handoff(plan, approval, validation)
    paths = [
        store.write_export(
            project_id,
            plan.revision,
            "concept-note.md",
            render_concept_note(brief, research, concept),
        ),
        store.write_export(
            project_id,
            plan.revision,
            "production-plan.md",
            render_production_plan(
                brief, research, plan, validation, critique, approval
            ),
        ),
        store.write_export(
            project_id,
            plan.revision,
            "gate1-packet.md",
            render_gate_packet(packet, plan, validation, critique),
        ),
        store.write_export(
            project_id,
            plan.revision,
            "level2-handoff.json",
            handoff.model_dump_json(indent=2) + "\n",
        ),
        store.write_export(
            project_id,
            plan.revision,
            "production-plan.json",
            plan.model_dump_json(indent=2) + "\n",
        ),
        store.write_export(
            project_id,
            plan.revision,
            "concept-note.json",
            concept.model_dump_json(indent=2) + "\n",
        ),
        store.write_export(
            project_id,
            plan.revision,
            "research-pack.json",
            research.model_dump_json(indent=2) + "\n",
        ),
        store.write_export(
            project_id,
            plan.revision,
            "brief.md",
            f"# Brief\n\n{brief.source_text}\n",
        ),
    ]
    paths.extend(write_previews(plan, store.export_dir(project_id, plan.revision) / "previews"))
    store.append_event(
        project_id,
        "level1.exported",
        {
            "revision": plan.revision,
            "files": [path.name for path in paths],
            "approval_hash": approval.plan_hash,
        },
    )
    return paths


def status(store: ProjectStore, project_id: str = DEFAULT_PROJECT) -> dict[str, Any]:
    project = store.load_project(project_id)
    result: dict[str, Any] = {
        "project": project.id,
        "title": project.title,
        "state": project.state.value,
        "plan_revision": project.current_plan_revision,
    }
    if project.current_plan_revision:
        plan = store.load_plan(project_id, project.current_plan_revision)
        result["plan_hash"] = plan.plan_hash()
        try:
            validation = store.load_validation(project_id, plan.revision)
            result["validation"] = {
                "passed": validation.passed,
                "failures": [finding.rule for finding in validation.failures],
                "warnings": len(validation.warnings),
            }
        except NotFoundError:
            result["validation"] = None
        try:
            critique = store.load_critique(project_id, plan.revision)
            result["critique"] = {
                "findings": len(critique.findings),
                "top3": critique.top3,
            }
        except NotFoundError:
            result["critique"] = None
        try:
            packet = store.load_packet(project_id, plan.revision)
            result["gate1"] = {
                "blockers": packet.blockers,
                "ready_shots": packet.ready_shots,
                "approval": packet.approval.approver if packet.approval else None,
            }
        except NotFoundError:
            result["gate1"] = None
    return result


def run_all(store: ProjectStore, fixture: str = DEFAULT_PROJECT) -> dict[str, Any]:
    init_project(store, fixture)
    run_research(store)
    run_concept(store)
    run_plan(store)
    run_validation(store)
    run_critique(store)
    run_resolution(store)
    run_validation(store)
    run_critique(store)
    run_previews(store)
    build_gate_packet(store)
    return status(store)


def resolve_approved_revision(
    store: ProjectStore, project_id: str
) -> tuple[ProductionPlan, Gate1Approval]:
    plan = store.load_latest_plan(project_id)
    approval = store.load_approval(project_id, plan.revision)
    return plan, approval
