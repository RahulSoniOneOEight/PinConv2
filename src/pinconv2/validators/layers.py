"""Layer geometry, binding and readability checks."""

from __future__ import annotations

from ..models import (
    BOUND_VISUAL_ROLES,
    TEXT_LAYER_ROLES,
    BindingKind,
    Exactness,
    Layer,
    LayerRole,
    RightsStatus,
    Severity,
)
from .common import ValidationContext


def _canvas(context: ValidationContext) -> tuple[int, int]:
    return context.plan.deliverable.width, context.plan.deliverable.height


def _safe_rect(context: ValidationContext) -> tuple[int, int, int, int]:
    deliverable = context.plan.deliverable
    area = deliverable.safe_area
    return (
        area.left,
        area.top,
        deliverable.width - area.right,
        deliverable.height - area.bottom,
    )


def _inside_safe(context: ValidationContext, layer: Layer) -> bool:
    left, top, right, bottom = _safe_rect(context)
    rect = layer.rect
    return rect.x >= left and rect.y >= top and rect.right <= right and rect.bottom <= bottom


def validate_layers(context: ValidationContext) -> None:
    plan = context.plan
    asset_map = plan.asset_map
    copy_map = plan.copy_map
    width, height = _canvas(context)

    with context.group("layer.references", "layers", "shot, asset and copy bindings resolve"):
        for shot in plan.shots:
            for layer_id in shot.layer_ids:
                layer = plan.layer_map.get(layer_id)
                if layer is None:
                    context.fail(
                        "layer.references",
                        shot.id,
                        Severity.BLOCKER,
                        f"shot references unknown layer {layer_id}",
                        "Create the layer or remove the reference.",
                    )
                elif layer.shot_id != shot.id:
                    context.fail(
                        "layer.references",
                        layer.id,
                        Severity.BLOCKER,
                        f"layer belongs to {layer.shot_id}, listed on {shot.id}",
                        "Keep layer ownership and shot references consistent.",
                    )
        for layer in plan.layers:
            if layer.binding_kind is BindingKind.ASSET and layer.binding_ref not in asset_map:
                context.fail(
                    "layer.references",
                    layer.id,
                    Severity.BLOCKER,
                    f"asset binding {layer.binding_ref} does not resolve",
                    "Create the asset requirement or fix the binding.",
                )
            if layer.binding_kind is BindingKind.COPY and layer.binding_ref not in copy_map:
                context.fail(
                    "layer.references",
                    layer.id,
                    Severity.BLOCKER,
                    f"copy binding {layer.binding_ref} does not resolve",
                    "Create the copy block or fix the binding.",
                )
            for region in layer.protected_regions:
                if not region.within(width, height):
                    context.fail(
                        "layer.references",
                        layer.id,
                        Severity.HIGH,
                        "protected region falls outside the canvas",
                        "Keep protected regions inside the deliverable.",
                    )

    with context.group("layer.z_order", "layers", "z-order is unique inside each shot"):
        for shot in plan.shots:
            z_orders = [
                plan.layer_map[layer_id].z_order
                for layer_id in shot.layer_ids
                if layer_id in plan.layer_map
            ]
            if len(z_orders) != len(set(z_orders)):
                context.fail(
                    "layer.z_order",
                    shot.id,
                    Severity.HIGH,
                    "two layers share a z-order",
                    "Give every layer a deterministic stacking order.",
                )

    with context.group("layer.canvas", "layers", "every layer sits inside the canvas"):
        for layer in plan.layers:
            if not layer.rect.within(width, height):
                context.fail(
                    "layer.canvas",
                    layer.id,
                    Severity.BLOCKER,
                    f"rect {layer.rect.model_dump()} extends beyond {width}x{height}",
                    "Reposition or resize the layer.",
                )

    with context.group(
        "layer.safe_area", "text", "text and protected layers sit inside the platform safe area"
    ):
        for layer in plan.layers:
            is_text = layer.role in TEXT_LAYER_ROLES
            is_protected_visual = layer.protected and layer.role in {
                LayerRole.PRODUCT,
                LayerRole.PACK_LABEL,
                LayerRole.LOGO,
            }
            if is_text and not _inside_safe(context, layer):
                context.fail(
                    "layer.safe_area",
                    layer.id,
                    Severity.HIGH,
                    f"{layer.role.value} layer leaves the safe area "
                    f"({layer.rect.model_dump()})",
                    "Move the layer inside the platform safe area.",
                )
            if is_protected_visual and not _inside_safe(context, layer):
                context.warn(
                    "layer.safe_area",
                    layer.id,
                    f"protected {layer.role.value} layer crosses the safe area",
                    "Confirm the crop on the final placement.",
                )

    with context.group(
        "layer.background", "shots", "every shot has a full-canvas background"
    ):
        for shot in plan.shots:
            backgrounds = [
                plan.layer_map[layer_id]
                for layer_id in shot.layer_ids
                if layer_id in plan.layer_map
                and plan.layer_map[layer_id].role is LayerRole.BACKGROUND
            ]
            if not backgrounds:
                context.fail(
                    "layer.background",
                    shot.id,
                    Severity.HIGH,
                    "shot has no background layer",
                    "Add a full-canvas background.",
                )
                continue
            if not any(
                layer.rect.x == 0
                and layer.rect.y == 0
                and layer.rect.w == width
                and layer.rect.h == height
                for layer in backgrounds
            ):
                context.fail(
                    "layer.background",
                    shot.id,
                    Severity.MEDIUM,
                    "background does not cover the full canvas",
                    "Extend the background to 0,0,width,height.",
                )

    with context.group(
        "layer.occlusion", "protected", "protected regions are not covered by opaque layers"
    ):
        for shot in plan.shots:
            layers = sorted(
                (
                    plan.layer_map[layer_id]
                    for layer_id in shot.layer_ids
                    if layer_id in plan.layer_map
                ),
                key=lambda item: item.z_order,
            )
            for index, lower in enumerate(layers):
                if not lower.protected and not lower.protected_regions:
                    continue
                regions = list(lower.protected_regions)
                if lower.protected:
                    regions.append(lower.rect)
                for upper in layers[index + 1 :]:
                    if upper.non_occluding or upper.opacity < 0.15:
                        continue
                    if upper.role in {LayerRole.EFFECT, LayerRole.GRADE} and upper.non_occluding:
                        continue
                    for region in regions:
                        if upper.rect.intersects(region):
                            context.fail(
                                "layer.occlusion",
                                upper.id,
                                Severity.BLOCKER,
                                f"{upper.role.value} layer covers protected "
                                f"{lower.id} at {region.model_dump()}",
                                "Move the overlay, lower its opacity, or mark it non-occluding.",
                            )

    with context.group("layer.text_overlap", "text", "text layers do not overlap"):
        for shot in plan.shots:
            text_layers = [
                plan.layer_map[layer_id]
                for layer_id in shot.layer_ids
                if layer_id in plan.layer_map
                and plan.layer_map[layer_id].role in TEXT_LAYER_ROLES
            ]
            for first_index, first in enumerate(text_layers):
                for second in text_layers[first_index + 1 :]:
                    if first.rect.intersects(second.rect):
                        context.fail(
                            "layer.text_overlap",
                            first.id,
                            Severity.HIGH,
                            f"overlaps {second.id}",
                            "Separate the text layers or remove one.",
                        )

    with context.group(
        "layer.plates", "captions", "every caption sits on a readable plate"
    ):
        for shot in plan.shots:
            layers = [
                plan.layer_map[layer_id]
                for layer_id in shot.layer_ids
                if layer_id in plan.layer_map
            ]
            for layer in layers:
                if layer.role not in {LayerRole.CAPTION, LayerRole.CTA}:
                    continue
                plates = [
                    candidate
                    for candidate in layers
                    if candidate.role is LayerRole.CAPTION_PLATE
                    and candidate.z_order < layer.z_order
                    and candidate.rect.contains(layer.rect)
                ]
                if not plates:
                    context.warn(
                        "layer.plates",
                        layer.id,
                        "caption has no plate behind it",
                        "Add a caption plate or verify contrast on the preview.",
                    )

    with context.group(
        "layer.duration", "text", "text layers have a minimum readable duration"
    ):
        for layer in plan.layers:
            if layer.role in TEXT_LAYER_ROLES and layer.duration_frames < 15:
                context.fail(
                    "layer.duration",
                    layer.id,
                    Severity.MEDIUM,
                    f"text is visible for only {layer.duration_frames} frames",
                    "Extend the hold or remove the layer.",
                )

    with context.group(
        "layer.binding_exactness", "assets", "exact layers bind exact assets"
    ):
        for layer in plan.layers:
            if layer.binding_kind is not BindingKind.ASSET or not layer.binding_ref:
                continue
            asset = asset_map.get(layer.binding_ref)
            if asset is None:
                continue
            if layer.exactness is Exactness.EXACT and asset.exactness is not Exactness.EXACT:
                context.fail(
                    "layer.binding_exactness",
                    layer.id,
                    Severity.BLOCKER,
                    f"exact layer binds illustrative asset {asset.id}",
                    "Bind an exact asset or relax the layer exactness.",
                )
            if asset.rights.status is RightsStatus.REFERENCE_ONLY:
                context.fail(
                    "layer.binding_exactness",
                    layer.id,
                    Severity.BLOCKER,
                    f"layer uses reference-only asset {asset.id}",
                    "Replace the reference with cleared or commissioned media.",
                )

    with context.group(
        "layer.density", "shots", "copy density stays readable"
    ):
        for shot in plan.shots:
            copy_layers = [
                plan.layer_map[layer_id]
                for layer_id in shot.layer_ids
                if layer_id in plan.layer_map
                and plan.layer_map[layer_id].role in TEXT_LAYER_ROLES
            ]
            if shot.duration_frames < 90 and len(copy_layers) > 2:
                context.warn(
                    "layer.density",
                    shot.id,
                    f"{len(copy_layers)} text layers in {shot.duration_frames} frames",
                    "Reduce to two text layers or hold the shot longer.",
                )

    with context.group(
        "layer.caption_plates", "plates", "caption plates sit behind captions"
    ):
        for layer in plan.layers:
            if layer.role is not LayerRole.CAPTION_PLATE:
                continue
            if layer.z_order < 0:
                context.fail(
                    "layer.caption_plates",
                    layer.id,
                    Severity.LOW,
                    "plate has a negative z-order",
                    "Keep plates above the background and below text.",
                )

    with context.group(
        "layer.visual_binding", "visuals", "visual layers bind assets and text binds copy"
    ):
        for layer in plan.layers:
            if layer.role in BOUND_VISUAL_ROLES and layer.binding_kind is not BindingKind.ASSET:
                context.fail(
                    "layer.visual_binding",
                    layer.id,
                    Severity.BLOCKER,
                    "visual layer does not bind an asset",
                    "Bind the visual layer to an asset requirement.",
                )
