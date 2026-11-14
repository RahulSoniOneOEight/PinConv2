"""Variant geometry validation.

A variant is executable only when it carries a real profile and, for a different
canvas, explicit per-layer and effect overrides.
"""

from __future__ import annotations

from ..models import TEXT_LAYER_ROLES, Severity
from .common import ValidationContext


def validate_variants(context: ValidationContext) -> None:
    plan = context.plan
    layer_map = plan.layer_map
    effect_map = plan.effect_map

    with context.group(
        "variant.dimensions", "variants", "variant profiles are internally coherent"
    ):
        for variant in plan.variant_overrides:
            if variant.width and variant.height and variant.aspect_ratio:
                w_ratio, h_ratio = (int(x) for x in variant.aspect_ratio.split(":"))
                if w_ratio * variant.height != h_ratio * variant.width:
                    context.fail(
                        "variant.dimensions",
                        variant.id,
                        Severity.BLOCKER,
                        f"dimensions do not match {variant.aspect_ratio}",
                        "Fix the variant canvas or aspect ratio.",
                    )
            if (
                variant.safe_area
                and variant.width
                and variant.height
                and (
                    variant.safe_area.left + variant.safe_area.right >= variant.width
                    or variant.safe_area.top + variant.safe_area.bottom >= variant.height
                )
            ):
                context.fail(
                    "variant.dimensions",
                    variant.id,
                    Severity.BLOCKER,
                    "safe area leaves no usable canvas",
                    "Reduce the insets.",
                )

    with context.group("variant.geometry", "variants", "a resized variant overrides every layer"):
        for variant in plan.variant_overrides:
            if not variant.width or not variant.height:
                continue
            if (
                variant.width == plan.deliverable.width
                and variant.height == plan.deliverable.height
            ):
                continue
            referenced_shots = {item for item in variant.reference_ids if item.startswith("SH-")}
            required_layers = {
                layer.id
                for shot in plan.shots
                if shot.id in referenced_shots
                for layer in (layer_map[i] for i in shot.layer_ids if i in layer_map)
            }
            overridden = {item.layer_id for item in variant.layer_overrides}
            missing = sorted(required_layers - overridden)
            if missing:
                context.fail(
                    "variant.geometry",
                    variant.id,
                    Severity.BLOCKER,
                    f"missing layer overrides: {', '.join(missing)}",
                    "Author every layer for the variant canvas.",
                )
            unknown = sorted(overridden - set(layer_map))
            if unknown:
                context.fail(
                    "variant.geometry",
                    variant.id,
                    Severity.HIGH,
                    f"unknown layer overrides: {', '.join(unknown)}",
                    "Remove or create the layer.",
                )

    with context.group("variant.layers", "variants", "variant layers fit the canvas and safe area"):
        for variant in plan.variant_overrides:
            if not variant.width or not variant.height:
                continue
            safe = (
                variant.safe_area.rect(variant.width, variant.height) if variant.safe_area else None
            )
            for override in variant.layer_overrides:
                layer = layer_map.get(override.layer_id)
                if layer is None:
                    continue
                if not override.rect.within(variant.width, variant.height):
                    context.fail(
                        "variant.layers",
                        override.layer_id,
                        Severity.BLOCKER,
                        "override rect falls outside the variant canvas",
                        "Reposition or resize the layer.",
                    )
                if safe and layer.role in TEXT_LAYER_ROLES and not safe.contains(override.rect):
                    context.fail(
                        "variant.layers",
                        override.layer_id,
                        Severity.HIGH,
                        "text override leaves the variant safe area",
                        "Move it inside the vertical safe area.",
                    )
                for region in override.protected_regions:
                    if not region.within(variant.width, variant.height):
                        context.fail(
                            "variant.layers",
                            override.layer_id,
                            Severity.HIGH,
                            "protected region leaves the variant canvas",
                            "Keep protection inside the variant.",
                        )

    with context.group("variant.effects", "variants", "variant effect masks fit the canvas"):
        for variant in plan.variant_overrides:
            for effect_override in variant.effect_overrides:
                effect = effect_map.get(effect_override.effect_id)
                if effect is None:
                    context.fail(
                        "variant.effects",
                        effect_override.effect_id,
                        Severity.HIGH,
                        "unknown effect in variant",
                        "Create the effect or remove the override.",
                    )
                    continue
                if (
                    effect_override.mask_region
                    and variant.width
                    and variant.height
                    and not effect_override.mask_region.within(variant.width, variant.height)
                ):
                    context.fail(
                        "variant.effects",
                        effect_override.effect_id,
                        Severity.HIGH,
                        "variant effect mask leaves the canvas",
                        "Reposition the mask.",
                    )
                if effect_override.mask_region:
                    for layer_override in variant.layer_overrides:
                        layer = layer_map.get(layer_override.layer_id)
                        if layer is None or layer.shot_id != effect.target_shot:
                            continue
                        if layer.role.value not in {"product", "pack_label", "logo"}:
                            continue
                        regions = list(layer_override.protected_regions)
                        if layer_override.protected:
                            regions.append(layer_override.rect)
                        for region in regions:
                            if effect_override.mask_region.intersects(region):
                                context.fail(
                                    "variant.effects",
                                    effect_override.effect_id,
                                    Severity.HIGH,
                                    "variant mask crosses protected region on "
                                    f"{layer_override.layer_id}",
                                    "Move or mask the effect so the label remains clear.",
                                )

    with context.group("variant.captions", "variants", "variant captions fit the declared rules"):
        for variant in plan.variant_overrides:
            if variant.caption_rules is None:
                continue
            for override in variant.layer_overrides:
                layer = layer_map.get(override.layer_id)
                if layer is None or layer.role not in TEXT_LAYER_ROLES:
                    continue
                if layer.binding_kind.value != "copy" or not layer.binding_ref:
                    continue
                copy = plan.copy_map.get(layer.binding_ref)
                if copy is None:
                    continue
                lines = max(1, -(-len(copy.text) // variant.caption_rules.max_chars_per_line))
                if lines > variant.caption_rules.max_lines:
                    context.fail(
                        "variant.captions",
                        layer.id,
                        Severity.MEDIUM,
                        f"text needs {lines} lines, variant allows "
                        f"{variant.caption_rules.max_lines}",
                        "Shorten the copy or change the variant layout.",
                    )

    with context.group("variant.basis", "variants", "variant safe areas declare their basis"):
        for variant in plan.variant_overrides:
            if variant.width and variant.height and not variant.safe_area_basis:
                context.warn(
                    "variant.basis",
                    variant.id,
                    "variant has no safe-area basis",
                    "Record whether the insets are an operator assumption or a placement spec.",
                )
