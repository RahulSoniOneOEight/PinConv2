"""Effect planning validation.

An effect is valid only when it names a real target, fits the shot, resolves its
asset references, and is cross-linked from the shot and layer records it changes.
"""

from __future__ import annotations

from ..models import BindingKind, LayerRole, Severity
from .common import ValidationContext


def validate_effects(context: ValidationContext) -> None:
    plan = context.plan
    shot_map = plan.shot_map
    layer_map = plan.layer_map
    asset_map = plan.asset_map

    with context.group("effect.ids", "effects", "effect identifiers are unique"):
        seen: set[str] = set()
        for effect in plan.effects:
            if effect.id in seen:
                context.fail(
                    "effect.ids",
                    effect.id,
                    Severity.BLOCKER,
                    "duplicate effect identifier",
                    "Give every effect a unique ID.",
                )
            seen.add(effect.id)

    with context.group("effect.references", "effects", "effect targets resolve"):
        for effect in plan.effects:
            shot = shot_map.get(effect.target_shot)
            if shot is None:
                context.fail(
                    "effect.references",
                    effect.id,
                    Severity.BLOCKER,
                    f"unknown target shot {effect.target_shot}",
                    "Point the effect at an existing shot.",
                )
                continue
            if effect.target_layer:
                layer = layer_map.get(effect.target_layer)
                if layer is None:
                    context.fail(
                        "effect.references",
                        effect.id,
                        Severity.BLOCKER,
                        f"unknown target layer {effect.target_layer}",
                        "Create the layer or remove the target.",
                    )
                elif layer.shot_id != effect.target_shot:
                    context.fail(
                        "effect.references",
                        effect.id,
                        Severity.HIGH,
                        f"target layer {effect.target_layer} belongs to {layer.shot_id}",
                        "Keep the effect and target layer in the same shot.",
                    )
            for asset_id in effect.asset_ids:
                if asset_id not in asset_map:
                    context.fail(
                        "effect.references",
                        effect.id,
                        Severity.HIGH,
                        f"unknown effect asset {asset_id}",
                        "Create the asset requirement or remove the reference.",
                    )

    with context.group("effect.timing", "effects", "effect timing fits its shot"):
        for effect in plan.effects:
            shot = shot_map.get(effect.target_shot)
            if shot is None:
                continue
            if effect.trigger_frame < 0:
                context.fail(
                    "effect.timing",
                    effect.id,
                    Severity.HIGH,
                    "negative trigger frame",
                    "Start the effect at or after frame 0.",
                )
            if effect.end_frame > shot.duration_frames:
                context.fail(
                    "effect.timing",
                    effect.id,
                    Severity.HIGH,
                    f"effect ends at {effect.end_frame}, shot is {shot.duration_frames} frames",
                    "Trim the effect or move it to a longer shot.",
                )
            if effect.target_layer:
                layer = layer_map.get(effect.target_layer)
                if layer is not None and effect.end_frame > layer.end_frame:
                    context.fail(
                        "effect.timing",
                        effect.id,
                        Severity.HIGH,
                        f"effect ends at {effect.end_frame}, target layer "
                        f"{layer.id} ends at {layer.end_frame}",
                        "Extend the layer or trim the effect.",
                    )
            if effect.mask_region and not effect.mask_region.within(
                plan.deliverable.width, plan.deliverable.height
            ):
                context.fail(
                    "effect.timing",
                    effect.id,
                    Severity.HIGH,
                    "effect mask falls outside the canvas",
                    "Keep the mask inside the deliverable.",
                )

    with context.group("effect.bindings", "effects", "shots and layers declare their effects"):
        for effect in plan.effects:
            shot = shot_map.get(effect.target_shot)
            if shot is not None and effect.id not in shot.effect_ids:
                context.fail(
                    "effect.bindings",
                    effect.id,
                    Severity.MEDIUM,
                    f"effect is not declared on shot {effect.target_shot}",
                    "Add the effect ID to the shot record.",
                )
            if effect.target_layer:
                layer = layer_map.get(effect.target_layer)
                if layer is not None and effect.id not in layer.effect_ids:
                    context.fail(
                        "effect.bindings",
                        effect.id,
                        Severity.MEDIUM,
                        f"effect is not declared on layer {effect.target_layer}",
                        "Add the effect ID to the layer record.",
                    )
        for shot in plan.shots:
            for effect_id in shot.effect_ids:
                bound_effect = plan.effect_map.get(effect_id)
                if bound_effect is None:
                    context.fail(
                        "effect.bindings",
                        shot.id,
                        Severity.HIGH,
                        f"unknown effect {effect_id}",
                        "Create the effect or remove the reference.",
                    )
                elif bound_effect.target_shot != shot.id:
                    context.fail(
                        "effect.bindings",
                        shot.id,
                        Severity.HIGH,
                        f"effect {effect_id} targets {bound_effect.target_shot}",
                        "Point the effect at this shot or remove the reference.",
                    )
        for layer in plan.layers:
            for effect_id in layer.effect_ids:
                bound_effect = plan.effect_map.get(effect_id)
                if bound_effect is None:
                    context.fail(
                        "effect.bindings",
                        layer.id,
                        Severity.HIGH,
                        f"unknown effect {effect_id}",
                        "Create the effect or remove the reference.",
                    )
                elif bound_effect.target_layer != layer.id:
                    context.fail(
                        "effect.bindings",
                        layer.id,
                        Severity.HIGH,
                        f"effect {effect_id} targets {bound_effect.target_layer}",
                        "Point the effect at this layer or remove the reference.",
                    )

    with context.group(
        "effect.protection", "effects", "effects do not obscure exact protected content"
    ):
        for effect in plan.effects:
            if effect.mask_region is None:
                continue
            shot = shot_map.get(effect.target_shot)
            if shot is None:
                continue
            for layer_id in shot.layer_ids:
                layer = layer_map.get(layer_id)
                if layer is None or layer.binding_kind is not BindingKind.ASSET:
                    continue
                if layer.role not in {
                    LayerRole.PRODUCT,
                    LayerRole.PACK_LABEL,
                    LayerRole.LOGO,
                }:
                    continue
                regions = list(layer.protected_regions)
                if layer.protected:
                    regions.append(layer.rect)
                for region in regions:
                    if effect.mask_region.intersects(region):
                        context.fail(
                            "effect.protection",
                            effect.id,
                            Severity.HIGH,
                            f"effect mask crosses protected region on {layer.id}",
                            "Move or mask the effect so the exact label or logo remains clear.",
                        )
