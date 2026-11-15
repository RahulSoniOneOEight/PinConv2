"""Processing agent: plan AI and deterministic processing per asset, priced."""

from __future__ import annotations

from typing import Any

from ...models import ProductionPlan
from ..models import BuildSheet, LayerMethodDecision, Level2Plan
from ..processing_plan import (
    ProcessingPlan,
    build_processing_plan,
    write_processing_plan,
)


class ProcessingAgent:
    def build(
        self,
        plan: ProductionPlan,
        level2: Level2Plan,
        sheet: BuildSheet,
        decisions: list[LayerMethodDecision],
        stock_plan: Any,
        run_dir: Any,
    ) -> ProcessingPlan:
        return build_processing_plan(plan, level2, sheet, decisions, stock_plan, run_dir)

    def write(
        self,
        run: Any,
        run_id: str,
        plan: ProductionPlan,
        level2: Level2Plan,
        sheet: BuildSheet,
        decisions: list[LayerMethodDecision],
        stock_plan: Any,
    ) -> ProcessingPlan:
        return write_processing_plan(run, run_id, plan, level2, sheet, decisions, stock_plan)
