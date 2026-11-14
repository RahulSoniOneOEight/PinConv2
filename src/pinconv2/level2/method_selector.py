"""Method selection for assets and layers.

Selection is deterministic: truth class and impact decide the allowed methods,
the approved route decides the strategy, and the matrix refuses substitutions
that would fake an exact product or a proof moment.
"""

from __future__ import annotations

from ..models import Asset, AssetRoute, CopyBlock, CopyStatus, Layer, LayerRole
from .errors import MethodMatrixError
from .models import (
    GateVerdict,
    Impact,
    LayerMethodDecision,
    Method,
    PickMode,
    SourceStrategy,
    TruthClass,
)
from .truth import classify

_MATRIX: dict[TruthClass, set[Method]] = {
    TruthClass.EXACT: {Method.M0, Method.M4, Method.M6},
    TruthClass.EXACT_TEXT: {Method.M0, Method.M4},
    TruthClass.PROOF: {Method.M2, Method.M6},
    TruthClass.REPRESENTATIVE: {
        Method.M0,
        Method.M1,
        Method.M2,
        Method.M3,
        Method.M4,
        Method.M5,
        Method.M6,
        Method.M7,
    },
    TruthClass.ATMOSPHERIC: {
        Method.M0,
        Method.M1,
        Method.M2,
        Method.M3,
        Method.M4,
        Method.M5,
        Method.M6,
        Method.M7,
    },
    TruthClass.EDITORIAL: {Method.M4, Method.M6},
}

PROBE_METHODS = {
    Method.M2,
    Method.M3,
    Method.M4,
    Method.M5,
    Method.M6,
    Method.M7,
}


def allowed_methods(truth_class: TruthClass) -> set[Method]:
    return set(_MATRIX[truth_class])


def assert_method_allowed(
    truth_class: TruthClass,
    method: Method,
    target: str,
    *,
    disclosed: bool = False,
    original_capture: bool = False,
) -> None:
    if method not in _MATRIX[truth_class]:
        raise MethodMatrixError(f"{target}: {truth_class.value} cannot use {method.value}")
    if truth_class is TruthClass.EXACT and method is Method.M6 and not original_capture:
        raise MethodMatrixError(
            f"{target}: exact M6 is only allowed when capturing the original object"
        )
    if truth_class is TruthClass.REPRESENTATIVE and method is Method.M7 and not disclosed:
        raise MethodMatrixError(f"{target}: representative M7 needs a disclosure flag")


def strategy_for(asset: Asset) -> tuple[SourceStrategy, Method, str]:
    if asset.route is AssetRoute.SUPPLIED:
        return SourceStrategy.SUPPLIED, Method.M0, "class_requires_supplied"
    if asset.route is AssetRoute.OWNED:
        return SourceStrategy.OWNED, Method.M0, "owned_asset"
    if asset.route is AssetRoute.TO_SOURCE:
        return SourceStrategy.STOCK, Method.M1, "library_required"
    if asset.route is AssetRoute.TO_CAPTURE:
        return SourceStrategy.CAPTURE, Method.M6, "capture_required"
    if asset.route is AssetRoute.TO_CREATE:
        return SourceStrategy.SUPPLIED, Method.M0, "performer_required"
    if asset.route is AssetRoute.TO_GENERATE:
        return SourceStrategy.GENERATE, Method.M7, "generated_fallback"
    raise MethodMatrixError(f"{asset.id}: unsupported route {asset.route.value}")


def select_asset_method(asset: Asset) -> tuple[SourceStrategy, Method, str]:
    strategy, method, reason = strategy_for(asset)
    truth_class = _asset_class(asset)
    assert_method_allowed(
        truth_class,
        method,
        asset.id,
        disclosed=asset.rights.disclosure_required,
        original_capture=asset.route is AssetRoute.TO_CAPTURE,
    )
    return strategy, method, reason


def _asset_class(asset: Asset) -> TruthClass:
    if asset.exactness.value == "exact":
        return TruthClass.EXACT
    if asset.route is AssetRoute.TO_CAPTURE:
        return TruthClass.PROOF
    if any(word in asset.name.lower() for word in ("music", "sting", "background")):
        return TruthClass.ATMOSPHERIC
    return TruthClass.REPRESENTATIVE


def _fallback_method(truth_class: TruthClass) -> Method:
    if truth_class is TruthClass.EXACT_TEXT:
        return Method.M4
    if truth_class is TruthClass.EXACT:
        return Method.M0
    if truth_class is TruthClass.PROOF:
        return Method.M6
    return Method.M4


def _rights_gate(asset: Asset | None) -> GateVerdict:
    if asset is None:
        return GateVerdict.PASS
    status = asset.rights.status.value
    if status == "cleared":
        return GateVerdict.PASS
    if status == "needs_approval":
        return GateVerdict.HOLD
    return GateVerdict.BLOCK


def _note_for(method: Method, asset: Asset | None, layer: Layer) -> str:
    if method is Method.M4 and layer.role is LayerRole.TYPOGRAPHY:
        return "Text rendered from the approved copy block; typeface pending the brand hold."
    if method is Method.M4 and layer.role is LayerRole.CAPTION_PLATE:
        return "Plate rendered procedurally from the approved fill and geometry."
    if method is Method.M4 and layer.role is LayerRole.EFFECT:
        return "Steam plate simulated in-house; no third-party effect media."
    if method is Method.M6:
        return "Captured on the single demonstration session; no stock substitution allowed."
    if method is Method.M0 and asset is not None:
        return (
            f"Use the approved {asset.id} source as supplied; edits limited to "
            "the layer allow-list."
        )
    if method is Method.M1:
        return "Library track selected and licensed; edit points recorded in the sound plan."
    return "Method selected by the truth-class matrix."


def pick_mode(impact: Impact) -> PickMode:
    return PickMode.AUTOMATIC if impact is Impact.LOW else PickMode.HUMAN


def select_layer_method(
    layer: Layer,
    asset: Asset | None,
    copy_block: CopyBlock | None,
    *,
    holds: list[str],
    impact_score: int,
    impact: Impact,
    impact_signals: list[str],
) -> LayerMethodDecision:
    truth_class, rule = classify(layer, asset)

    if truth_class is TruthClass.EXACT_TEXT:
        method = Method.M4
        reason = "procedural_only"
    elif truth_class is TruthClass.EXACT:
        method = Method.M0
        reason = "class_requires_supplied"
    elif truth_class is TruthClass.PROOF:
        method = Method.M6
        reason = "capture_required"
    elif layer.role is LayerRole.EFFECT or layer.role is LayerRole.CAPTION_PLATE:
        method = Method.M4
        reason = "procedural_only"
    elif (
        layer.role is LayerRole.BACKGROUND and asset is not None and asset.route is AssetRoute.OWNED
    ):
        method = Method.M0
        reason = "owned_plate"
    elif asset is not None and asset.route is AssetRoute.TO_SOURCE:
        method = Method.M1
        reason = "library_required"
    elif asset is not None:
        method = Method.M0
        reason = "reuse_existing_asset"
    else:
        method = Method.M4
        reason = "procedural_only"

    disclosed = asset.rights.disclosure_required if asset is not None else False
    assert_method_allowed(truth_class, method, layer.id, disclosed=disclosed)

    hold_list = set(holds)
    if layer.role is LayerRole.TYPOGRAPHY:
        hold_list.add("HI-05")
    if copy_block is not None and copy_block.status is CopyStatus.PROPOSED:
        hold_list.add("copy_pending")
    if copy_block is not None and copy_block.status is CopyStatus.HELD:
        hold_list.add("copy_held")

    gate = _rights_gate(asset)
    if layer.role is LayerRole.TYPOGRAPHY and gate is GateVerdict.PASS:
        gate = GateVerdict.HOLD

    fallback = _fallback_method(truth_class)
    assert_method_allowed(
        truth_class,
        fallback,
        f"{layer.id}.fallback",
        disclosed=disclosed,
    )

    return LayerMethodDecision(
        layer_id=layer.id,
        shot_id=layer.shot_id,
        role=layer.role.value,
        truth_class=truth_class,
        truth_class_rule=rule,
        impact_score=impact_score,
        impact=impact,
        impact_signals=impact_signals,
        method=method,
        method_reason=reason,
        method_note=_note_for(method, asset, layer),
        asset_id=layer.binding_ref if layer.binding_kind.value == "asset" else None,
        fallback_method=fallback,
        probe_required=method in PROBE_METHODS,
        pick_mode=pick_mode(impact),
        rights_gate=gate,
        notes=", ".join(sorted(hold_list)) if hold_list else None,
    )
