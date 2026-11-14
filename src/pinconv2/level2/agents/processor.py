"""Declarative processing recipes per asset."""

from __future__ import annotations

from ...models import Asset
from ..models import Method, ProcessingOp, SourceStrategy
from ..recipes import describe, recipe_for_method, validate_recipe


class ProcessingPlanner:
    def plan(self, asset: Asset, method: Method, strategy: SourceStrategy) -> list[ProcessingOp]:
        return recipe_for_method(asset, method, strategy)

    def validate(self, asset: Asset, ops: list[ProcessingOp]) -> None:
        validate_recipe(asset, ops)

    def describe(self, ops: list[ProcessingOp]) -> list[str]:
        return describe(ops)
