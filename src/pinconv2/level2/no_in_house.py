"""No in-house production policy.

Level 2 produces every asset through exactly three allowed ways:

1. licensed stock;
2. AI generation;
3. AI enhancement of stock.

There is no in-house production: no camera shoot, no set build, no in-house
voice session, no manual pack preparation. Editing, compositing, grade and
render are tool processing (OpenMontage / HyperFrames / ffmpeg), not production.
"""

from __future__ import annotations

from pydantic import Field

from ..models import ProductionPlan, StrictModel, utc_now
from .models import Level2Plan
from .stock_plan import StockPlan

# Each lean in-kind line and how it is replaced under the no-in-house rule.
_IN_HOUSE_REPLACEMENT = {
    "ES-01": ("stock", "licensed CC0/CC BY music track"),
    "ES-02": ("generate", "AI TTS voice (ShortGPT or fal/Runware)"),
    "ES-03": ("tool", "OpenMontage edit + compositing"),
    "ES-04": ("tool", "AI-enhanced grade or deterministic LUT"),
    "ES-05": ("enhance", "AI label-preserving cutout of the supplied pack"),
    "ES-06": ("stock", "stock pour/cup footage, AI-enhanced if needed"),
    "ES-07": ("enhance", "AI label-preserving cutout of the supplied packs"),
    "ES-08": ("generate", "HyperFrames end card + AI brand sting"),
    "ES-09": ("stock", "stock pack-fallback footage, AI-enhanced"),
    "ES-11": ("tool", "OpenMontage 9:16 re-edit"),
}


class NoInHouseFinding(StrictModel):
    line_id: str
    label: str
    method: str = Field(pattern=r"^(stock|generate|enhance|tool)$")
    note: str


class NoInHouseReport(StrictModel):
    status: str = Field(pattern=r"^(ready|blocked)$")
    findings: list[NoInHouseFinding] = Field(default_factory=list)
    generated_assets: list[str] = Field(default_factory=list)
    ai_share_pct: float = Field(ge=0)
    within_ai_cap: bool
    created_at: str = Field(default_factory=utc_now)


def evaluate_no_in_house(
    plan: ProductionPlan, level2: Level2Plan, stock: StockPlan
) -> NoInHouseReport:
    findings: list[NoInHouseFinding] = []
    substitutions = level2.budget.substitutions if level2.budget is not None else []
    for item in substitutions:
        replacement = _IN_HOUSE_REPLACEMENT.get(item.estimate_id)
        if replacement is None:
            continue
        method, note = replacement
        findings.append(
            NoInHouseFinding(
                line_id=item.estimate_id,
                label=item.label,
                method=method,
                note=note,
            )
        )
    generated = [route.asset_id for route in stock.routes if route.group == "generate"]
    generated = sorted(set(generated) | {"AS-09", "AS-12", "AS-15"})
    ai_share = round(len(generated) / max(len(stock.routes), 1) * 100, 1)
    return NoInHouseReport(
        status="ready" if stock.within_ai_cap else "blocked",
        findings=findings,
        generated_assets=generated,
        ai_share_pct=ai_share,
        within_ai_cap=stock.within_ai_cap,
    )


def render_no_in_house(report: NoInHouseReport) -> str:
    lines = [
        "# No in-house production policy",
        "",
        "Assets are produced only by: **licensed stock**, **AI generation**, or",
        "**AI enhancement of stock**. There is no camera shoot, set build, in-house",
        "voice session or manual pack preparation.",
        "",
        f"**Status:** `{report.status}` · AI share {report.ai_share_pct}% "
        f"(cap 40%) · generated: {', '.join(report.generated_assets) or 'none'}",
        "",
        "## In-kind line replacements",
        "",
        "| Line | Original line | Method | Replacement |",
        "|---|---|---|---|",
    ]
    for finding in report.findings:
        lines.append(
            f"| `{finding.line_id}` | {finding.label} | `{finding.method}` | {finding.note} |"
        )
    lines.extend(
        [
            "",
            "## Budget rule",
            "",
            "- `stock` — licensed, mostly free (CC0/CC BY/Pexels/Pixabay/Unsplash).",
            "- `enhance` — AI processing of stock; does not count against the 40% cap.",
            "- `generate` — original AI media; counted against the 40% cap and the",
            "  $2.00 provider budget (fal/Runware, $0.50 per job).",
            "- `tool` — OpenMontage / HyperFrames / ffmpeg processing, $0.",
            "",
        ]
    )
    return "\n".join(lines)
