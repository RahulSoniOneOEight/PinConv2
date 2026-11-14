"""Licence, scriptability and acceptance evaluation for candidates."""

from __future__ import annotations

from ..catalogue import SOURCE_MAP
from ..licence_gate import attribution_line, ensure_usable, gate_candidate
from ..models import MethodCandidate


class SourceEvaluator:
    def evaluate(self, candidate: MethodCandidate) -> MethodCandidate:
        return gate_candidate(candidate, entry=SOURCE_MAP.get(candidate.provider))

    def require_usable(self, candidate: MethodCandidate) -> None:
        ensure_usable(candidate)

    def attribution(self, candidate: MethodCandidate) -> str:
        return attribution_line(candidate)
