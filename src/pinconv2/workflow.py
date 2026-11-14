"""Level 1 state machine.

Every command validates its predecessor state. A failed command must not move
the project forward.
"""

from __future__ import annotations

from .errors import InvalidTransitionError
from .models import Project, ProjectState, utc_now

ALLOWED_TRANSITIONS: dict[ProjectState, frozenset[ProjectState]] = {
    ProjectState.INIT: frozenset({ProjectState.INTAKE, ProjectState.FAILED}),
    ProjectState.INTAKE: frozenset({ProjectState.RESEARCH, ProjectState.FAILED}),
    ProjectState.RESEARCH: frozenset({ProjectState.TREATMENT, ProjectState.FAILED}),
    ProjectState.TREATMENT: frozenset({ProjectState.SHOT_PLAN, ProjectState.FAILED}),
    ProjectState.SHOT_PLAN: frozenset({ProjectState.VALIDATED, ProjectState.FAILED}),
    ProjectState.VALIDATED: frozenset({ProjectState.CRITIQUED, ProjectState.FAILED}),
    ProjectState.CRITIQUED: frozenset(
        {
            ProjectState.INPUTS_UPDATED,
            ProjectState.GATE1_READY,
            ProjectState.FAILED,
        }
    ),
    ProjectState.INPUTS_UPDATED: frozenset(
        {ProjectState.SHOT_PLAN, ProjectState.VALIDATED, ProjectState.FAILED}
    ),
    ProjectState.GATE1_READY: frozenset({ProjectState.APPROVED, ProjectState.FAILED}),
    ProjectState.APPROVED: frozenset({ProjectState.FAILED}),
    ProjectState.FAILED: frozenset(),
}


def require_state(project: Project, *states: ProjectState) -> None:
    if project.state not in states:
        expected = ", ".join(state.value for state in states)
        raise InvalidTransitionError(
            f"project {project.id} is {project.state.value}; expected one of: {expected}"
        )


def advance(project: Project, target: ProjectState) -> Project:
    allowed = ALLOWED_TRANSITIONS[project.state]
    if target not in allowed:
        raise InvalidTransitionError(
            f"cannot move {project.id} from {project.state.value} to {target.value}"
        )
    return project.model_copy(update={"state": target, "updated_at": utc_now()})


def fail(project: Project) -> Project:
    return project.model_copy(update={"state": ProjectState.FAILED, "updated_at": utc_now()})
