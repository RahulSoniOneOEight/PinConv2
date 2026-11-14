"""Generation specs, only where the truth class allows them."""

from __future__ import annotations

from typing import Any, cast

from ...models import Asset
from ..engines.base import GenerationResult
from ..generation import assert_generation_allowed, build_generation_spec
from ..governance import ProviderBudgetError, ProviderGovernor
from ..models import GenerationSpec, TruthClass


class GenerationPlanner:
    def plan(self, asset: Asset, truth_class: TruthClass, script: str) -> GenerationSpec:
        assert_generation_allowed(asset, truth_class)
        return build_generation_spec(asset, script)


class GenerationAgent:
    """Run one paid generation through the governor and an injected engine."""

    def __init__(self, engine: Any, governor: ProviderGovernor) -> None:
        self.engine = engine
        self.governor = governor

    def run(self, spec: GenerationSpec, work_item: str) -> GenerationResult:
        if spec.cost_usd <= 0:
            raise ProviderBudgetError("a paid generation needs a positive quoted cost")
        reservation = self.governor.reserve(spec.provider, spec.cost_usd, work_item)
        try:
            result = self.engine.generate(spec)
        except Exception:
            self.governor.release(reservation, "generation failed")
            raise
        try:
            self.governor.receipt(reservation, result.cost_usd, result.job_id)
        except Exception:
            self.governor.release(reservation, "receipt failed")
            raise
        return cast(GenerationResult, result)
