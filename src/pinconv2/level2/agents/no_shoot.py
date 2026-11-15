"""No-shoot policy agent."""

from __future__ import annotations

from ...models import ProductionPlan
from ..models import Level2Plan
from ..no_shoot import NoShootReport, evaluate_no_shoot


class NoShootAgent:
    def evaluate(self, plan: ProductionPlan, level2: Level2Plan) -> NoShootReport:
        return evaluate_no_shoot(plan, level2)
