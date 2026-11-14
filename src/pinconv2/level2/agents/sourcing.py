"""Sourcing agent: search, licence-gate, preview and record stock candidates."""

from __future__ import annotations

from pathlib import Path

from ...store import ProjectStore
from ..models import SourcingReport
from ..sourcing import DEFAULT_QUERIES, source_assets
from ..stockcheck import StockCheckReport, run_stock_check


class SourcingAgent:
    def discover(
        self,
        store: ProjectStore,
        project_id: str,
        revision: int,
        run_id: str,
        *,
        queries: dict[str, str] | None = None,
        limit: int = 5,
    ) -> SourcingReport:
        return source_assets(
            store,
            project_id,
            revision,
            run_id,
            queries=queries if queries is not None else DEFAULT_QUERIES,
            limit=limit,
        )

    def check_sources(
        self, media_dir: Path, query: str = "coffee"
    ) -> StockCheckReport:
        return run_stock_check(media_dir, query)
