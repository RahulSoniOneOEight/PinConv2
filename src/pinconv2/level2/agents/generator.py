"""Generation specs, only where the truth class allows them."""

from __future__ import annotations

from ...models import Asset
from ..generation import assert_generation_allowed, build_generation_spec
from ..models import GenerationSpec, TruthClass


class GenerationPlanner:
    def plan(self, asset: Asset, truth_class: TruthClass, script: str) -> GenerationSpec:
        assert_generation_allowed(asset, truth_class)
        return build_generation_spec(asset, script)
