"""Stock-first sourcing agent with the AI-share guard."""

from __future__ import annotations

from pathlib import Path

from ...models import ProductionPlan
from ..models import Level2Plan
from ..stock_plan import (
    StockCandidate,
    StockPlan,
    build_stock_plan,
    fetch_and_rank,
)


class StockPlanAgent:
    def build(self, plan: ProductionPlan, level2: Level2Plan) -> StockPlan:
        return build_stock_plan(plan, level2)

    def fetch_and_rank(
        self, asset_id: str, kind: str, query: str, run_dir: Path
    ) -> list[StockCandidate]:
        return fetch_and_rank(asset_id, kind, query, run_dir)
