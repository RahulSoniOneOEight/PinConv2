"""Static SVG previews for Level 2 review.

These are wireframes, not renders. They show geometry, copy, protected regions
and the safe area for both the 16:9 master and the approved 9:16 variant.
"""

from __future__ import annotations

from html import escape

from ..models import HandoffVariant, Layer, LayerRole, ProductionPlan, Rect
from .variants import overlay_rect

_ROLE_FILL = {
    LayerRole.BACKGROUND: "#1A0F0A",
    LayerRole.SUBJECT: "#5A2E1A",
    LayerRole.PRODUCT: "#8A4B2A",
    LayerRole.PACK_LABEL: "#C98A55",
    LayerRole.LOGO: "#E8C9A0",
    LayerRole.EFFECT: "#E8D5B5",
    LayerRole.CAPTION_PLATE: "#000000",
    LayerRole.GRADE: "#2A1710",
    LayerRole.TYPOGRAPHY: "#F7F3EC",
    LayerRole.CAPTION: "#F7F3EC",
    LayerRole.CTA: "#F7F3EC",
}


def _rect(rect: tuple[int, int, int, int], fill: str, opacity: float, extra: str = "") -> str:
    x, y, w, h = rect
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
        f'fill="{fill}" fill-opacity="{opacity:.2f}" {extra}/>'
    )


def _text(layer: Layer, plan: ProductionPlan, rect: tuple[int, int, int, int]) -> str:
    if layer.text_style is None or layer.binding_ref is None:
        return ""
    copy_block = plan.copy_map.get(layer.binding_ref)
    if copy_block is None:
        return ""
    x, y, _, _ = rect
    style = layer.text_style
    return (
        f'<text x="{x}" y="{y + style.size_px}" '
        f'font-family="{escape(style.font_family)}, Segoe UI, sans-serif" '
        f'font-size="{style.size_px}" font-weight="{style.weight}" '
        f'fill="{style.color}">{escape(copy_block.text[:60])}</text>'
    )


def render_shot(
    plan: ProductionPlan,
    shot_id: str,
    variant: HandoffVariant | None = None,
) -> str:
    shot = plan.shot_map[shot_id]
    if variant is not None:
        width = variant.width or plan.deliverable.width
        height = variant.height or plan.deliverable.height
        overrides = {item.layer_id: item for item in variant.layer_overrides}
        safe = variant.safe_area
    else:
        width = plan.deliverable.width
        height = plan.deliverable.height
        overrides = {}
        safe = plan.deliverable.safe_area

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#0B0604"/>',
    ]
    layers = sorted(
        (plan.layer_map[layer_id] for layer_id in shot.layer_ids),
        key=lambda layer: layer.z_order,
    )
    for layer in layers:
        rect = overlay_rect(layer, overrides.get(layer.id))
        fill = _ROLE_FILL.get(layer.role)
        if layer.role is LayerRole.CAPTION_PLATE:
            parts.append(_rect(rect, "#000000", min(layer.opacity, 0.55)))
        elif fill is not None:
            parts.append(_rect(rect, fill, min(layer.opacity, 0.85), 'rx="12"'))
        parts.append(_text(layer, plan, rect))
        if layer.protected:
            x, y, w, h = rect
            parts.append(
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
                f'stroke="#FF6B6B" stroke-width="3" stroke-dasharray="12 8"/>'
            )
    if safe is not None:
        parts.append(
            f'<rect x="{safe.left}" y="{safe.top}" '
            f'width="{width - safe.left - safe.right}" '
            f'height="{height - safe.top - safe.bottom}" fill="none" '
            f'stroke="#4ADE80" stroke-width="4" stroke-dasharray="16 10"/>'
        )
    label = variant.variant_id if variant is not None else "16:9"
    parts.append(
        f'<text x="24" y="{height - 24}" font-family="Inter, Segoe UI, sans-serif" '
        f'font-size="28" fill="#FFFFFF" fill-opacity="0.7">'
        f"{escape(shot_id)} · {escape(label)}</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def render_all(plan: ProductionPlan, variant: HandoffVariant | None = None) -> dict[str, str]:
    return {shot.id: render_shot(plan, shot.id, variant) for shot in plan.shots}


def protected_overlaps(plan: ProductionPlan, shot_id: str) -> list[str]:
    """Report layer pairs whose protected regions intersect another layer."""

    shot = plan.shot_map[shot_id]
    layers = [plan.layer_map[layer_id] for layer_id in shot.layer_ids]
    problems: list[str] = []
    for layer in layers:
        for region in layer.protected_regions:
            for other in layers:
                if other.id == layer.id or not other.protected:
                    continue
                other_rect = Rect(x=other.rect.x, y=other.rect.y, w=other.rect.w, h=other.rect.h)
                if region.intersects(other_rect):
                    problems.append(f"{layer.id} protected region overlaps {other.id}")
    return problems
