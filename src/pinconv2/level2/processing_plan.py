"""Processing and budget plan at the shot x layer x asset level.

After extensive multi-source sourcing selects the best candidate per asset, the
agent plans the processing each asset needs and prices it, so the whole trial
stays inside the $2.00 operator budget.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field

from ..models import ProductionPlan, StrictModel
from .asset_summary import build_rows
from .html_export import markdown_to_html
from .models import BuildSheet, LayerMethodDecision, Level2Plan

TRIAL_BUDGET_USD = 2.00

_OP_COST = {
    "alpha_cutout": 0.04,
    "grade": 0.03,
    "scale": 0.02,
    "crop": 0.02,
    "relight": 0.06,
    "upscale": 0.08,
    "encode": 0.01,
    "trim": 0.02,
    "stabilise": 0.05,
    "conform": 0.03,
    "speed_ramp": 0.04,
    "denoise": 0.04,
    "loudness_norm": 0.03,
    "resample": 0.02,
    "fade": 0.02,
    "tts": 0.08,
    "synth": 0.06,
}

_PROCESSING: dict[str, list[str]] = {
    "supplied": ["alpha_cutout", "grade", "scale", "encode"],
    "stock": [],
    "generate": [],
}

_STOCK_BY_KIND: dict[str, list[str]] = {
    "image": ["grade", "scale", "encode"],
    "video": ["trim", "stabilise", "conform", "grade", "scale", "encode"],
    "sound": ["trim", "denoise", "loudness_norm", "resample", "encode"],
    "music": ["trim", "fade", "loudness_norm", "resample", "encode"],
}

_GENERATE_BY_KIND: dict[str, list[str]] = {
    "voice": ["tts", "trim", "loudness_norm", "resample", "encode"],
    "sound": ["synth", "loudness_norm", "resample", "encode"],
    "image": ["upscale", "grade", "encode"],
}

# AI edits/enhancements applied to each asset. This is distinct from AI
# generation: edits are minor and do not count against the 40% generation cap.
_AI_PROCESSING: dict[str, str] = {
    "AS-01": (
        "AI background removal to alpha + edge cleanup; upscale only from a "
        "real master, never a thumbnail"
    ),
    "AS-05": (
        "AI stabilise + denoise; AI frame interpolation for the 50->25 conform; "
        "AI relight; inpaint stray objects"
    ),
    "AS-06": "AI stabilise + denoise; AI speed-ramp retime; AI relight; inpaint stray objects",
    "AS-07": "AI relight to the warm counter; AI inpaint distractions; crop to 1080p",
    "AS-08": "AI relight to the counter; AI background clean + cup-edge inpaint",
    "AS-09": (
        "AI generation: TTS voice (counts against the 40% allowance); AI denoise + loudness norm"
    ),
    "AS-02": "AI label-preserving background cutout; color/light normalize to the counter plates",
    "AS-03": "AI label-preserving background cutout; color/light normalize",
    "AS-04": "AI label-preserving background cutout; color/light normalize",
    "AS-17": "AI label-preserving background cutout; color/light normalize",
    "AS-13": "AI label-preserving cutout across the four angles",
    "AS-10": "AI loudness norm to -16 LUFS; AI loop tail; trim + fade",
    "AS-11": "AI denoise; trim to the pour; level-match to the mix",
    "AS-12": "AI generation: synthetic brand sting; loudness norm",
    "AS-14": "AI loudness norm to -16 LUFS; loop tail",
    "AS-15": "AI generation: TTS fallback; loudness norm",
}

_AI_GENERATED = {"AS-09", "AS-12", "AS-15"}


class ProcessingEntry(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    name: str
    group: str = Field(pattern=r"^(supplied|stock|generate)$")
    kind: str
    source: str
    shots: list[str] = Field(default_factory=list)
    layers: list[str] = Field(default_factory=list)
    ops: list[str] = Field(default_factory=list)
    ai_processing: str = Field(default="", max_length=400)
    ai_generation: bool = False
    cost_usd: float = Field(ge=0)


class ProcessingPlan(StrictModel):
    entries: list[ProcessingEntry] = Field(min_length=1)
    total_cost_usd: float = Field(ge=0)
    budget_usd: float = Field(ge=0)
    within_budget: bool


def _ops_for(group: str, kind: str) -> list[str]:
    if group == "supplied":
        return list(_PROCESSING["supplied"])
    if group == "stock":
        return list(_STOCK_BY_KIND.get(kind, ["grade", "encode"]))
    if group == "generate":
        return list(_GENERATE_BY_KIND.get(kind, ["upscale", "grade", "encode"]))
    return ["grade", "encode"]


def _cost(ops: list[str]) -> float:
    return round(sum(_OP_COST.get(op, 0.0) for op in ops), 2)


def build_processing_plan(
    plan: ProductionPlan,
    level2: Level2Plan,
    sheet: BuildSheet,
    decisions: list[LayerMethodDecision],
    stock_plan: Any,
    run_dir: Path,
) -> ProcessingPlan:
    rows = build_rows(plan, level2, sheet, decisions, run_dir)
    stock_routes = {route.asset_id: route for route in stock_plan.routes}
    selected = {
        candidate.asset_id: candidate for candidate in stock_plan.candidates if candidate.used
    }
    entries: list[ProcessingEntry] = []
    for row in rows:
        route = stock_routes.get(row["asset_id"])
        group = route.group if route is not None else row["route"]
        kind = route.kind if route is not None else "image"
        ops = _ops_for(group, kind)
        source = ""
        candidate = selected.get(row["asset_id"])
        if candidate is not None:
            source = f"{candidate.provider}: {candidate.title}"
        else:
            source = row["source"][:80]
        entries.append(
            ProcessingEntry(
                asset_id=row["asset_id"],
                name=row["name"],
                group=group,
                kind=kind,
                source=source,
                shots=row["shots"],
                layers=row["layers"],
                ops=ops,
                ai_processing=_AI_PROCESSING.get(row["asset_id"], ""),
                ai_generation=row["asset_id"] in _AI_GENERATED,
                cost_usd=_cost(ops),
            )
        )
    total = round(sum(entry.cost_usd for entry in entries), 2)
    return ProcessingPlan(
        entries=entries,
        total_cost_usd=total,
        budget_usd=TRIAL_BUDGET_USD,
        within_budget=total <= TRIAL_BUDGET_USD + 0.0001,
    )


def render_processing_plan(plan: ProcessingPlan) -> str:
    lines = [
        "# Processing plan — shot x layer x asset",
        "",
        "Each asset's required processing, its cost, and the trial budget. The",
        "trial run is capped at $2.00.",
        "",
        "| Total processing | Budget | Within budget |",
        "|---|---|---|",
        f"| ${plan.total_cost_usd:.2f} | ${plan.budget_usd:.2f} | "
        f"{'yes' if plan.within_budget else 'NO'} |",
        "",
        "| Asset | What | Route | Kind | Shots | Layers | Processing | Cost |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for entry in plan.entries:
        lines.append(
            f"| `{entry.asset_id}` | {entry.name} | {entry.group} | {entry.kind} | "
            f"{', '.join(entry.shots) or '—'} | {len(entry.layers)} | "
            f"{' → '.join(entry.ops)} | ${entry.cost_usd:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Processing detail",
            "",
        ]
    )
    for entry in plan.entries:
        lines.extend(
            [
                f"### {entry.asset_id} — {entry.name}",
                "",
                f"- Source: {entry.source}",
                f"- Processing: {' → '.join(entry.ops) or 'none'}",
                f"- AI: {entry.ai_processing or 'none'}",
                f"- AI generation: {'yes' if entry.ai_generation else 'no (edit only)'}",
                f"- Cost: ${entry.cost_usd:.2f}",
                "",
            ]
        )
    lines.extend(
        [
            "## AI processing vs AI generation",
            "",
            "AI **processing** is a minor edit/enhancement applied to an existing",
            "asset (relight, inpaint, denoise, retime, label cutout, loudness norm).",
            "It does not count against the 40% cap. AI **generation** creates new",
            "media and is limited to voice, sting and the narration fallback.",
            "",
            "| Asset | AI processing / generation | Generation? |",
            "|---|---|---|",
        ]
    )
    for entry in plan.entries:
        lines.append(
            f"| `{entry.asset_id}` | {entry.ai_processing or 'none'} | "
            f"{'yes' if entry.ai_generation else 'no'} |"
        )
    lines.extend(
        [
            "",
            "## Budget rule",
            "",
            "- Stock licensing is free or in-kind for CC0/CC-BY/Pexels/Pixabay/Unsplash.",
            "- AI generation is capped at 40% of assets and is disclosed.",
            "- Processing is priced per operation and kept within the $2 trial cap.",
            "",
        ]
    )
    return "\n".join(lines)


def write_processing_plan(
    run: Any,
    run_id: str,
    plan: ProductionPlan,
    level2: Level2Plan,
    sheet: BuildSheet,
    decisions: list[LayerMethodDecision],
    stock_plan: Any,
) -> ProcessingPlan:
    processing = build_processing_plan(
        plan, level2, sheet, decisions, stock_plan, run.run_dir(run_id)
    )
    markdown = render_processing_plan(processing)
    run.write_text(run_id, "PROCESSING-PLAN.md", markdown)
    run.write_text(
        run_id,
        "PROCESSING-PLAN.html",
        markdown_to_html(markdown, f"Processing plan - {plan.project_id}"),
    )
    run.write_json(run_id, "processing-plan.json", processing)
    return processing
