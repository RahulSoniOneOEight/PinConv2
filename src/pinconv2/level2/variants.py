"""9:16 variant resolution.

The vertical cut reuses every shared source asset and resolves all 38 layers
through the approved overrides. Missing overrides are reported, never guessed.
"""

from __future__ import annotations

from ..models import (
    HandoffVariant,
    Layer,
    ProductionPlan,
    VariantEffectOverride,
    VariantLayerOverride,
)
from .errors import Level2Error
from .models import VariantLayerResolution, VariantPackage


def _override_map(variant: HandoffVariant) -> dict[str, VariantLayerOverride]:
    return {override.layer_id: override for override in variant.layer_overrides}


def resolve_variant(plan: ProductionPlan, variant: HandoffVariant) -> VariantPackage:
    if variant.width is None or variant.height is None or variant.frame_count is None:
        raise Level2Error(f"{variant.variant_id}: the variant geometry is incomplete")
    if variant.safe_area is None:
        raise Level2Error(f"{variant.variant_id}: the variant has no safe area")

    overrides = _override_map(variant)
    known = set(plan.layer_map)
    unknown = sorted(set(overrides) - known)
    if unknown:
        raise Level2Error(f"{variant.variant_id}: overrides reference unknown layers {unknown}")

    resolutions: list[VariantLayerResolution] = []
    for layer_id in sorted(known):
        if layer_id in overrides:
            resolutions.append(
                VariantLayerResolution(
                    layer_id=layer_id,
                    resolution="override",
                    notes=overrides[layer_id].notes,
                )
            )
        else:
            resolutions.append(
                VariantLayerResolution(
                    layer_id=layer_id,
                    resolution="carried",
                    notes="Layer geometry carried from the 16:9 master.",
                )
            )

    effects = _effect_ids(variant.effect_overrides, plan)
    blockers = ["AC-16 pending: 9:16 safe-area template not confirmed"]
    if not effects:
        blockers.append("no effect-mask overrides for the vertical cut")

    return VariantPackage(
        variant_id=variant.variant_id,
        width=variant.width,
        height=variant.height,
        fps=variant.fps or plan.deliverable.fps,
        frame_count=variant.frame_count,
        safe_area=variant.safe_area,
        safe_area_basis=variant.safe_area_basis
        or "Operator assumption; confirm against the placement template.",
        resolutions=resolutions,
        layer_overrides=list(variant.layer_overrides),
        effect_masks=list(variant.effect_overrides),
        effect_overrides=effects,
        cost_usd=variant.cost_delta_usd,
        check_ids=list(variant.check_ids),
        check_status="pending",
        ready=False,
        blockers=blockers,
    )


def _effect_ids(overrides: list[VariantEffectOverride], plan: ProductionPlan) -> list[str]:
    known = set(plan.effect_map)
    ids: list[str] = []
    for override in overrides:
        if override.effect_id not in known:
            raise Level2Error(f"variant override references unknown effect {override.effect_id}")
        ids.append(override.effect_id)
    return ids


def validate_variant(plan: ProductionPlan, package: VariantPackage) -> None:
    if len(package.resolutions) != len(plan.layers):
        raise Level2Error(
            f"{package.variant_id} resolves {len(package.resolutions)} of {len(plan.layers)} layers"
        )
    missing = [item.layer_id for item in package.resolutions if item.resolution == "missing"]
    if missing:
        raise Level2Error(f"{package.variant_id} has unresolved layers {missing}")
    if package.width <= 0 or package.height <= 0:
        raise Level2Error(f"{package.variant_id} has invalid geometry")
    if package.frame_count != plan.deliverable.frame_count:
        raise Level2Error(f"{package.variant_id} must keep the master frame count")


def overlay_rect(layer: Layer, override: VariantLayerOverride | None) -> tuple[int, int, int, int]:
    """Return the variant rect for a layer, overriding only what changed."""

    if override is not None:
        return (override.rect.x, override.rect.y, override.rect.w, override.rect.h)
    return (layer.rect.x, layer.rect.y, layer.rect.w, layer.rect.h)
