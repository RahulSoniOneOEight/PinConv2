"""Dependency graph, batches and critical path."""

from __future__ import annotations

from ...models import ProductionPlan
from ..flow_scheduler import build_flow, validate_flow
from ..models import AssetProductionTask, BuildSheet, FlowGraph


class FlowScheduler:
    def build(
        self,
        plan: ProductionPlan,
        tasks: list[AssetProductionTask],
        sheet: BuildSheet | None = None,
    ) -> FlowGraph:
        return build_flow(plan, tasks, sheet)

    def validate(self, plan: ProductionPlan, flow: FlowGraph) -> None:
        validate_flow(plan, flow)
