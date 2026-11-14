"""Truth classification, derived only from approved Level 1 fields.

Level 2 may not invent a new taxonomy. Each layer gets one class and the rule
that produced it, so a reviewer can replay the decision.
"""

from __future__ import annotations

from ..models import Asset, AssetRoute, Exactness, Layer, LayerRole, ProductionPlan
from .models import TruthClass

PROOF_ROLES = {LayerRole.SUBJECT}
ATMOSPHERIC_ROLES = {LayerRole.BACKGROUND, LayerRole.EFFECT}


def classify(layer: Layer, asset: Asset | None) -> tuple[TruthClass, str]:
    """Return the truth class and the rule id that produced it."""

    if layer.exactness is Exactness.EXACT:
        return TruthClass.EXACT, "R1"
    if layer.exactness is Exactness.PROPOSED_COPY or layer.binding_kind.value == "copy":
        return TruthClass.EXACT_TEXT, "R2"
    if layer.role in PROOF_ROLES and asset is not None and asset.route is AssetRoute.TO_CAPTURE:
        return TruthClass.PROOF, "R3"
    if layer.role in ATMOSPHERIC_ROLES:
        return TruthClass.ATMOSPHERIC, "R4"
    return TruthClass.REPRESENTATIVE, "R5"


def classify_layer(layer: Layer, plan: ProductionPlan) -> tuple[TruthClass, str]:
    asset = plan.asset_map.get(layer.binding_ref or "")
    return classify(layer, asset)
