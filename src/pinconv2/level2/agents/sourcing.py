"""Sourcing agent: search, licence-gate, preview and record stock candidates."""

from __future__ import annotations

from pathlib import Path

from ...store import ProjectStore
from ..models import SourcingReport
from ..openmontage_source import OpenMontageSearch, search_for_asset
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
        openmontage: bool = False,
        openmontage_asset: str = "AS-07",
        openmontage_attempt: str = "1",
    ) -> SourcingReport:
        return source_assets(
            store,
            project_id,
            revision,
            run_id,
            queries=queries if queries is not None else DEFAULT_QUERIES,
            limit=limit,
            openmontage=openmontage,
            openmontage_asset=openmontage_asset,
            openmontage_attempt=openmontage_attempt,
        )

    def check_sources(self, media_dir: Path, query: str = "coffee") -> StockCheckReport:
        return run_stock_check(media_dir, query)

    def openmontage_discover(
        self,
        asset_id: str,
        query: str,
        run_dir: Path,
        run_id: str,
        *,
        route: str = "nasa.stock",
        kind: str = "image",
        limit: int = 5,
        attempt: str = "1",
    ) -> OpenMontageSearch:
        return search_for_asset(
            asset_id,
            query,
            run_dir,
            run_id,
            route=route,
            kind=kind,
            limit=limit,
            attempt=attempt,
        )
