"""Deterministic fixtures used by the Level 1 acceptance runs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..models import (
    BriefRevision,
    ConceptNote,
    ProductionPlan,
    ResearchPack,
)
from .blue_tokai_concept import build_blue_tokai_concept
from .blue_tokai_plan import build_blue_tokai_plan
from .blue_tokai_research import (
    PROJECT_ID as BLUE_TOKAI_PROJECT_ID,
)
from .blue_tokai_research import (
    build_blue_tokai_brief,
    build_blue_tokai_research,
)
from .toffee_concept import build_concept_note
from .toffee_plan import build_plan, revision_two_applied
from .toffee_research import (
    PROJECT_ID as TOFFEE_PROJECT_ID,
)
from .toffee_research import (
    build_brief,
    build_research_pack,
)

PlanBuilder = Callable[[str, int, frozenset[str]], ProductionPlan]


@dataclass(frozen=True)
class Fixture:
    project_id: str
    title: str
    brief: Callable[[], BriefRevision]
    research: Callable[[str], ResearchPack]
    concept: Callable[[str], ConceptNote]
    plan: PlanBuilder


def _toffee_plan(project_id: str, revision: int, applied: frozenset[str]) -> ProductionPlan:
    return build_plan(project_id=project_id, revision=revision, applied=applied)


def _toffee_research(project_id: str) -> ResearchPack:
    return build_research_pack().model_copy(update={"project_id": project_id})


def _toffee_concept(project_id: str) -> ConceptNote:
    return build_concept_note().model_copy(update={"project_id": project_id})


def _blue_research(project_id: str) -> ResearchPack:
    return build_blue_tokai_research().model_copy(update={"project_id": project_id})


def _blue_concept(project_id: str) -> ConceptNote:
    return build_blue_tokai_concept().model_copy(update={"project_id": project_id})


FIXTURES: dict[str, Fixture] = {
    TOFFEE_PROJECT_ID: Fixture(
        project_id=TOFFEE_PROJECT_ID,
        title="Toffee Coffee Roasters 10-second vertical ad",
        brief=build_brief,
        research=_toffee_research,
        concept=_toffee_concept,
        plan=_toffee_plan,
    ),
    BLUE_TOKAI_PROJECT_ID: Fixture(
        project_id=BLUE_TOKAI_PROJECT_ID,
        title="Blue Tokai Easy Pour 20-second YouTube ad",
        brief=build_blue_tokai_brief,
        research=_blue_research,
        concept=_blue_concept,
        plan=build_blue_tokai_plan,
    ),
}


def get_fixture(project_id: str) -> Fixture:
    if project_id not in FIXTURES:
        raise KeyError(project_id)
    return FIXTURES[project_id]


__all__ = [
    "FIXTURES",
    "Fixture",
    "build_brief",
    "build_concept_note",
    "build_plan",
    "build_research_pack",
    "get_fixture",
    "revision_two_applied",
]
