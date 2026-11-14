"""Deterministic fixtures used by the Level 1 acceptance run."""

from __future__ import annotations

from .toffee_concept import build_concept_note
from .toffee_plan import build_plan, revision_two_applied
from .toffee_research import build_brief, build_research_pack

FIXTURES = {"toffee-coffee-10s": "Toffee Coffee Roasters 10-second vertical ad"}

__all__ = [
    "FIXTURES",
    "build_brief",
    "build_concept_note",
    "build_plan",
    "build_research_pack",
    "revision_two_applied",
]
