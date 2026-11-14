"""Static layout mockups for Level 1 review.

These are SVG wireframes, not renders. They show layer geometry, copy, protected
regions and the safe area so a human can inspect the plan before approving it.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from .models import (
    Layer,
    LayerRole,
    ProductionPlan,
    Rect,
    Shot,
)

ROLE_FILL = {
    LayerRole.BACKGROUND: "#1A0F0A",
    LayerRole.SUBJECT: "#5A2E1A",
    LayerRole.PRODUCT: "#8A4B2A",
    LayerRole.PACK_LABEL: "#C98A55",
    LayerRole.LOGO: "#E8C9A0",
    LayerRole.EFFECT: "#E8D5B5",
    LayerRole.CAPTION_PLATE: "#000000",
    LayerRole.GRADE: "#2A1710",
}


def _rect(rect: Rect, fill: str, opacity: float, extra: str = "") -> str:
    return (
        f'<rect x="{rect.x}" y="{rect.y}" width="{rect.w}" height="{rect.h}" '
        f'fill="{fill}" fill-opacity="{opacity:.2f}" {extra}/>'
    )


def _text(layer: Layer, plan: ProductionPlan) -> str:
    if layer.text_style is None or layer.binding_ref is None:
        return ""
    copy_block = plan.copy_map.get(layer.binding_ref)
    if copy_block is None:
        return ""
    style = layer.text_style
    lines = copy_block.text.split("\n")
    if len(lines) == 1 and style.max_lines > 1 and len(copy_block.text) > 18:
        words = copy_block.text.split()
        midpoint = max(1, len(words) // 2)
        lines = [" ".join(words[:midpoint]), " ".join(words[midpoint:])]
    line_height = style.size_px * style.line_height
    first_baseline = layer.rect.y + style.size_px * 0.82
    spans = []
    for index, line in enumerate(lines[: style.max_lines]):
        dy = 0 if index == 0 else line_height
        spans.append(f'<tspan x="{layer.rect.x}" dy="{dy:.1f}">{escape(line)}</tspan>')
    return (
        f'<text x="{layer.rect.x}" y="{first_baseline:.1f}" '
        f'font-family="{escape(style.font_family)}, Segoe UI, sans-serif" '
        f'font-size="{style.size_px}" font-weight="{style.weight}" '
        f'fill="{style.color}" text-anchor="start">' + "".join(spans) + "</text>"
    )


def _visual_label(layer: Layer) -> str:
    if layer.role in {LayerRole.BACKGROUND, LayerRole.EFFECT, LayerRole.CAPTION_PLATE}:
        return ""
    label = f"{layer.binding_ref or ''} {layer.role.value}".strip()
    return (
        f'<text x="{layer.rect.x + 16}" y="{layer.rect.y + 36}" '
        f'font-family="Inter, Segoe UI, sans-serif" font-size="26" '
        f'fill="#FFFFFF" fill-opacity="0.65">{escape(label)}</text>'
    )


def _canvas_markup(plan: ProductionPlan, shot: Shot) -> str:
    deliverable = plan.deliverable
    width = deliverable.width
    height = deliverable.height
    parts = [f'<rect x="0" y="0" width="{width}" height="{height}" fill="#0B0604"/>']
    layers = [plan.layer_map[layer_id] for layer_id in shot.layer_ids if layer_id in plan.layer_map]
    for layer in sorted(layers, key=lambda item: item.z_order):
        if layer.role is LayerRole.CAPTION_PLATE:
            parts.append(_rect(layer.rect, "#000000", layer.opacity))
        elif layer.role in ROLE_FILL:
            opacity = layer.opacity
            extra = 'rx="12"'
            if layer.role is LayerRole.EFFECT:
                opacity = min(opacity, 0.12)
                extra = 'rx="12" stroke="#E8D5B5" stroke-width="3" stroke-dasharray="18 12"'
            parts.append(_rect(layer.rect, ROLE_FILL[layer.role], opacity, extra))
            parts.append(_visual_label(layer))
        if layer.role.value in {
            "typography",
            "caption",
            "cta",
            "offer",
            "disclaimer",
        }:
            parts.append(_text(layer, plan))
        for region in layer.protected_regions:
            parts.append(
                f'<rect x="{region.x}" y="{region.y}" width="{region.w}" '
                f'height="{region.h}" fill="none" stroke="#FF7A59" '
                f'stroke-width="4" stroke-dasharray="16 10"/>'
            )
        if layer.protected:
            parts.append(
                f'<rect x="{layer.rect.x}" y="{layer.rect.y}" '
                f'width="{layer.rect.w}" height="{layer.rect.h}" fill="none" '
                f'stroke="#FF7A59" stroke-width="4" stroke-dasharray="16 10"/>'
            )

    safe = deliverable.safe_area
    parts.append(
        f'<rect x="{safe.left}" y="{safe.top}" '
        f'width="{width - safe.left - safe.right}" '
        f'height="{height - safe.top - safe.bottom}" fill="none" '
        f'stroke="#6BE3C2" stroke-width="3" stroke-dasharray="22 14" '
        f'stroke-opacity="0.85"/>'
    )
    parts.append(
        f'<text x="{safe.left + 8}" y="{safe.top + 34}" '
        f'font-family="Inter, Segoe UI, sans-serif" font-size="24" '
        f'fill="#6BE3C2" fill-opacity="0.9">safe area</text>'
    )
    return "".join(parts)


def render_shot_svg(plan: ProductionPlan, shot: Shot) -> str:
    deliverable = plan.deliverable
    width = deliverable.width
    height = deliverable.height
    header = 92
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height + header}" viewBox="0 0 {width} {height + header}">'
        f'<rect width="100%" height="100%" fill="#050302"/>'
        f'<text x="24" y="38" font-family="Inter, Segoe UI, sans-serif" '
        f'font-size="30" fill="#F7EBDD">{escape(shot.id)} - '
        f"{escape(shot.purpose)}</text>"
        f'<text x="24" y="72" font-family="Inter, Segoe UI, sans-serif" '
        f'font-size="22" fill="#9C8B7C">LAYOUT MOCKUP - NOT FINAL ART - frames '
        f"{shot.start_frame}-{shot.end_frame}</text>"
        f'<g transform="translate(0,{header})">{_canvas_markup(plan, shot)}</g>'
        "</svg>"
    )


def render_contact_sheet(plan: ProductionPlan) -> str:
    scale = 0.14 if len(plan.shots) > 4 else 0.22
    tile_width = int(plan.deliverable.width * scale)
    tile_height = int(plan.deliverable.height * scale)
    gap = 24
    left = 24
    top = 146
    total_width = left * 2 + len(plan.shots) * tile_width + (len(plan.shots) - 1) * gap
    total_height = top + tile_height + 48
    tiles = []
    for index, shot in enumerate(plan.shots):
        x = left + index * (tile_width + gap)
        tiles.append(
            f'<g transform="translate({x},{top})">'
            f'<svg width="{tile_width}" height="{tile_height}" '
            f'viewBox="0 0 {plan.deliverable.width} {plan.deliverable.height}">'
            f"{_canvas_markup(plan, shot)}</svg>"
            f'<text x="0" y="-18" font-family="Inter, Segoe UI, sans-serif" '
            f'font-size="22" fill="#F7EBDD">{escape(shot.id)} '
            f"{shot.start_frame}-{shot.end_frame}</text>"
            "</g>"
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" '
        f'height="{total_height}" viewBox="0 0 {total_width} {total_height}">'
        f'<rect width="100%" height="100%" fill="#050302"/>'
        f'<text x="{left}" y="42" font-family="Inter, Segoe UI, sans-serif" '
        f'font-size="30" fill="#F7EBDD">'
        f"{escape(plan.project_id.replace('-', ' ').title())} - contact sheet</text>"
        f'<text x="{left}" y="74" font-family="Inter, Segoe UI, sans-serif" '
        f'font-size="22" fill="#9C8B7C">LAYOUT MOCKUP - plan revision '
        f"{plan.revision} - {plan.plan_hash()[:12]}</text>" + "".join(tiles) + "</svg>"
    )


def write_previews(plan: ProductionPlan, directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for shot in plan.shots:
        path = directory / f"{shot.id}.svg"
        path.write_text(render_shot_svg(plan, shot), encoding="utf-8", newline="\n")
        paths.append(path)
    contact = directory / "contact-sheet.svg"
    contact.write_text(render_contact_sheet(plan), encoding="utf-8", newline="\n")
    paths.append(contact)
    return paths
