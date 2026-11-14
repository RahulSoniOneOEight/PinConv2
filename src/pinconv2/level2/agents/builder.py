"""Assemble the ready-to-assemble build sheet."""

from __future__ import annotations

from ...models import ProductionPlan
from ..build_sheet import assemble
from ..models import (
    AssetIntent,
    AssetProductionTask,
    BudgetEstimate,
    BuildSheet,
    Correction,
    LayerMethodDecision,
    SourcingReport,
    VariantPackage,
)


class BuildSheetBuilder:
    def build(
        self,
        plan: ProductionPlan,
        intents: list[AssetIntent],
        decisions: list[LayerMethodDecision],
        tasks: list[AssetProductionTask],
        variants: list[VariantPackage],
        budget: BudgetEstimate,
        *,
        run_id: str,
        source_plan_hash: str,
        bundle_hash: str,
        packet_hash: str,
        preview_paths: dict[str, str] | None = None,
        corrections: list[Correction] | None = None,
        sourcing: SourcingReport | None = None,
    ) -> BuildSheet:
        return assemble(
            plan,
            intents,
            decisions,
            tasks,
            variants,
            budget,
            run_id=run_id,
            source_plan_hash=source_plan_hash,
            bundle_hash=bundle_hash,
            packet_hash=packet_hash,
            preview_paths=preview_paths,
            corrections=corrections,
            sourcing=sourcing,
        )
