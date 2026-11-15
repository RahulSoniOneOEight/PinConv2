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


class ProcessingEntry(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    name: str
    group: str = Field(pattern=r"^(supplied|stock|generate)$")
    kind: str
    source: str
    shots: list[str] = Field(default_factory=list)
    layers: list[str] = Field(default_factory=list)
    ops: list[str] = Field(default_factory=list)
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
                f"- Cost: ${entry.cost_usd:.2f}",
                "",
            ]
        )
    lines.extend(
        [
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
