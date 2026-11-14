"""Truth class and impact classification."""

from __future__ import annotations

from ...models import BriefRevision, ProductionPlan
from ..impact import score_layer
from ..models import Impact, LayerMethodDecision, TruthClass
from ..truth import classify_layer


class AssetClassifier:
    def classify_layers(self, plan: ProductionPlan) -> dict[str, tuple[TruthClass, str]]:
        return {layer.id: classify_layer(layer, plan) for layer in plan.layers}

    def score(
        self, plan: ProductionPlan, brief: BriefRevision
    ) -> dict[str, tuple[int, Impact, list[str]]]:
        return {
            layer.id: score_layer(layer, plan.shot_map[layer.shot_id], plan, brief)
            for layer in plan.layers
        }

    def apply(self, decisions: list[LayerMethodDecision]) -> list[LayerMethodDecision]:
        return list(decisions)
