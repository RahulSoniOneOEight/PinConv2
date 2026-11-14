"""Human review pack and budget documents.

The reviewer judges against acceptance lines and previews, not against prose.
Every item carries a status badge, a cost, a rights state and a decision box.
"""

from __future__ import annotations

from ..models import ProductionPlan
from .docx import DocxBuilder
from .models import (
    AssetIntent,
    BudgetEstimate,
    BuildSheet,
    LayerMethodDecision,
    TaskStatus,
    VariantPackage,
)

_BADGE = {
    TaskStatus.PLANNED: "planned",
    TaskStatus.READY: "ready",
    TaskStatus.SOURCED: "sourced",
    TaskStatus.PROBED: "probed",
    TaskStatus.PROCESSED: "processed",
    TaskStatus.ACCEPTED: "ready",
    TaskStatus.BLOCKED: "blocked",
    TaskStatus.CONDITIONAL: "conditional",
}


def _money(value: float) -> str:
    return f"${value:,.2f}"


def budget_table_markdown(budget: BudgetEstimate) -> list[str]:
    rows = ["| Line | Estimate | Kind | Basis | USD |", "|---|---|---|---|---|"]
    for line in budget.lines:
        rows.append(
            f"| {line.line_id} {line.label} | {line.estimate_id or 'fallback'} | {line.kind} | "
            f"{line.basis} | {line.amount_usd:,.2f} |"
        )
    return rows


def budget_summary_markdown(budget: BudgetEstimate) -> list[str]:
    summary = budget.summary
    lines = [
        f"- Subtotal: **{_money(summary.subtotal_usd)}**",
        f"- Retry reserve ({summary.reserve_pct:.0f}%): {_money(summary.reserve_usd)}",
        f"- **Estimated total: {_money(summary.total_usd)}**",
        f"- Fallbacks: {_money(summary.fallback_usd)}",
        f"- **Worst case: {_money(summary.worst_usd)}**",
        f"- Cap: {_money(summary.cap_usd)}",
        f"- **Headroom: {_money(summary.headroom_usd)}**",
    ]
    if summary.unpriced_lines:
        lines.append(
            "- Unpriced fallbacks: "
            + ", ".join(summary.unpriced_lines)
            + ". These must become quotes or explicit zero-cost swaps at Gate 2A."
        )
    return lines


def render_budget(budget: BudgetEstimate, plan: ProductionPlan) -> str:
    lines = [
        f"# Level 2 budget — {plan.project_id} rev-{plan.revision:03d}",
        "",
        "**Status: operator estimate. No line is a verified quote and no money has been spent.**",
        "",
        *budget_table_markdown(budget),
        "",
        *budget_summary_markdown(budget),
        "",
        f"Raw per-asset estimates in the handoff: {_money(budget.raw_attributed_usd)}. "
        f"Dedupe saves {_money(budget.dedupe_savings_usd)} by charging the capture "
        "session and pack preparation once.",
        "",
    ]
    return "\n".join(lines)


def render_budget_docx(budget: BudgetEstimate, plan: ProductionPlan) -> DocxBuilder:
    builder = DocxBuilder()
    builder.heading(f"Level 2 budget — {plan.project_id} rev-{plan.revision:03d}")
    builder.paragraph("Status: operator estimate. No verified quote and no spend.", bold=True)
    builder.table(
        ["Line", "Method", "Kind", "Basis", "USD"],
        [
            [
                f"{line.line_id} {line.label}",
                line.dedupe_key or "—",
                line.kind,
                line.basis,
                f"{line.amount_usd:,.2f}",
            ]
            for line in budget.lines
        ],
    )
    summary = budget.summary
    for label, value in (
        ("Subtotal", summary.subtotal_usd),
        (f"Reserve ({summary.reserve_pct:.0f}%)", summary.reserve_usd),
        ("Estimated total", summary.total_usd),
        ("Fallbacks", summary.fallback_usd),
        ("Worst case", summary.worst_usd),
        ("Cap", summary.cap_usd),
        ("Headroom", summary.headroom_usd),
    ):
        builder.paragraph(f"{label}: {_money(value)}")
    builder.paragraph(
        f"Dedupe saves {_money(budget.dedupe_savings_usd)} against the raw "
        f"handoff total of {_money(budget.raw_attributed_usd)}."
    )
    return builder


def render_review(
    plan: ProductionPlan,
    intents: list[AssetIntent],
    decisions: list[LayerMethodDecision],
    budget: BudgetEstimate,
    sheet: BuildSheet,
    variants: list[VariantPackage],
) -> str:
    summary = budget.summary
    ready = sum(1 for asset in sheet.assets if asset.status is TaskStatus.ACCEPTED)
    blocked = sum(1 for asset in sheet.assets if asset.status is TaskStatus.BLOCKED)
    conditional = sum(1 for asset in sheet.assets if asset.status is TaskStatus.CONDITIONAL)
    lines = [
        f"# Gate 2 review — {plan.project_id}",
        "",
        "## How to use this pack",
        "",
        "1. Read the summary and the budget.",
        "2. Judge each asset and layer against its acceptance line and preview.",
        "3. Mark APPROVE / CHANGE / REJECT and write one instruction.",
        "4. Return the completed form; corrections become a new run, never an edit.",
        "",
        "```",
        "ID: AS-02",
        "Decision: APPROVE / CHANGE / REJECT",
        "Instruction: one concrete change",
        "Reason: why it matters",
        "Approver:",
        "Date:",
        "```",
        "",
        "## Summary",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| Assets | {len(sheet.assets)} |",
        f"| Layers | {len(decisions)} |",
        f"| Shots | {len(sheet.shots)} |",
        f"| Variants | {len(variants)} |",
        f"| Ready assets | {ready} |",
        f"| Blocked assets | {blocked} |",
        f"| Conditional assets | {conditional} |",
        f"| Estimated total | {_money(summary.total_usd)} |",
        f"| Worst case | {_money(summary.worst_usd)} |",
        f"| Cap | {_money(summary.cap_usd)} |",
        f"| Headroom | {_money(summary.headroom_usd)} |",
        "",
        "## Budget",
        "",
        *budget_table_markdown(budget),
        "",
        *budget_summary_markdown(budget),
        "",
        f"Raw per-asset estimates: {_money(budget.raw_attributed_usd)}; dedupe saves "
        f"{_money(budget.dedupe_savings_usd)}.",
        "",
        "## Assets",
        "",
    ]
    intent_map = {intent.asset_id: intent for intent in intents}
    for asset in sheet.assets:
        intent = intent_map[asset.asset_id]
        badge = _BADGE.get(asset.status, asset.status.value)
        lines.extend(
            [
                f"### {asset.asset_id} · {asset.name} · "
                f"{asset.truth_class.value} · {asset.impact.value}",
                "",
                f"- Status: **{badge}**",
                f"- Method: {'/'.join(method.value for method in asset.methods)}",
                f"- Source: {asset.source}",
                f"- Rights: {asset.rights_status}"
                + (f" · hold `{asset.hold}`" if asset.hold else ""),
                f"- Cost: {_money(intent.estimate_usd)} "
                f"({intent.estimate_id or 'fallback, unpriced'})",
                f"- Acceptance: {asset.acceptance}",
                f"- Preview: {asset.bindings[0] if asset.bindings else 'n/a'}",
                f"- Blockers: {', '.join(asset.blockers) or 'none'}",
                "- Decision: ☐ APPROVE  ☐ CHANGE  ☐ REJECT",
                "",
            ]
        )
    lines.extend(
        [
            "## Layers",
            "",
            "| Layer | Shot | Class | Impact | Method | Fallback | Probe | Pick |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for decision in decisions:
        lines.append(
            f"| `{decision.layer_id}` | {decision.shot_id} | {decision.truth_class.value} | "
            f"{decision.impact.value} ({decision.impact_score}) | {decision.method.value} | "
            f"{decision.fallback_method.value} | {'yes' if decision.probe_required else 'no'} | "
            f"{decision.pick_mode.value} |"
        )
    lines.extend(
        [
            "",
            "## Shots",
            "",
            "| Shot | Frames | Layers | Ready | Blockers |",
            "|---|---|---|---|---|",
        ]
    )
    for shot in sheet.shots:
        lines.append(
            f"| {shot.shot_id} | {shot.start_frame}–{shot.end_frame} | {len(shot.layers)} | "
            f"{'yes' if shot.ready else 'no'} | {', '.join(shot.blockers) or 'none'} |"
        )
    lines.extend(["", "## Variant", ""])
    for variant in variants:
        overrides = sum(1 for item in variant.resolutions if item.resolution == "override")
        lines.extend(
            [
                f"### {variant.variant_id} · {variant.width}x{variant.height} @ {variant.fps} fps",
                "",
                f"- Frames: {variant.frame_count}",
                f"- Layer overrides: {overrides} of {len(variant.resolutions)}",
                f"- Effect overrides: {', '.join(variant.effect_overrides) or 'none'}",
                f"- Safe area: {variant.safe_area.top}/{variant.safe_area.bottom}/"
                f"{variant.safe_area.left}/{variant.safe_area.right}",
                f"- Basis: {variant.safe_area_basis}",
                f"- Cost: {_money(variant.cost_usd)}",
                f"- Status: {variant.check_status}",
                f"- Blockers: {', '.join(variant.blockers) or 'none'}",
                "",
            ]
        )
    candidates = sum(len(decision.candidates) for decision in decisions)
    lines.extend(
        [
            "## Compliance",
            "",
            f"- Sourcing round: **not run**; {candidates} candidates recorded.",
            "- Licence gate: NC, ND, share-alike, BBC Sound Effects and GADM are "
            "excluded by the catalogue.",
            "- Manual-only sources are never fetched by script.",
            "- Aggregator licences (Openverse, IA, Wikimedia) must resolve at the origin.",
            "- Exact and proof material never uses stock or generation (G2A-03).",
            "",
            "## Correction log",
            "",
            "| ID | Item | Decision | Instruction | Status |",
            "|---|---|---|---|---|",
            "| — | — | — | — | — |",
            "",
        ]
    )
    return "\n".join(lines)


def render_review_docx(
    plan: ProductionPlan,
    intents: list[AssetIntent],
    decisions: list[LayerMethodDecision],
    budget: BudgetEstimate,
    sheet: BuildSheet,
) -> DocxBuilder:
    builder = DocxBuilder()
    builder.heading(f"Gate 2 review — {plan.project_id}")
    builder.paragraph(
        "Mark each item APPROVE, CHANGE or REJECT and return the form. "
        "Corrections create a new run; nothing is edited in place."
    )
    summary = budget.summary
    builder.heading("Summary", 2)
    builder.table(
        ["Item", "Value"],
        [
            ["Assets", str(len(sheet.assets))],
            ["Layers", str(len(decisions))],
            ["Shots", str(len(sheet.shots))],
            ["Estimated total", _money(summary.total_usd)],
            ["Worst case", _money(summary.worst_usd)],
            ["Cap", _money(summary.cap_usd)],
            ["Headroom", _money(summary.headroom_usd)],
        ],
    )
    builder.heading("Budget", 2)
    builder.table(
        ["Line", "Kind", "Basis", "USD"],
        [[line.label, line.kind, line.basis, f"{line.amount_usd:,.2f}"] for line in budget.lines],
    )
    builder.heading("Assets", 2)
    intent_map = {intent.asset_id: intent for intent in intents}
    for asset in sheet.assets:
        intent = intent_map[asset.asset_id]
        builder.heading(f"{asset.asset_id} · {asset.name}", 3)
        builder.bullet(f"Status: {_BADGE.get(asset.status, asset.status.value)}")
        builder.bullet(f"Method: {'/'.join(method.value for method in asset.methods)}")
        builder.bullet(f"Rights: {asset.rights_status}")
        builder.bullet(f"Cost: {_money(intent.estimate_usd)}")
        builder.bullet(f"Acceptance: {asset.acceptance}")
        builder.paragraph("Decision: ☐ APPROVE   ☐ CHANGE   ☐ REJECT")
    builder.heading("Layers", 2)
    builder.table(
        ["Layer", "Class", "Impact", "Method", "Fallback"],
        [
            [
                decision.layer_id,
                decision.truth_class.value,
                f"{decision.impact.value} ({decision.impact_score})",
                decision.method.value,
                decision.fallback_method.value,
            ]
            for decision in decisions
        ],
    )
    builder.heading("Correction form", 2)
    for label in ("ID", "Decision", "Instruction", "Reason", "Approver", "Date"):
        builder.paragraph(f"{label}: ______________________________")
    return builder


def render_feedback_form(plan: ProductionPlan, sheet: BuildSheet) -> str:
    """A fill-in form that mirrors every reviewable item exactly once."""

    lines = [
        f"# Gate 2 feedback form — {plan.project_id}",
        "",
        "Use one row per item. Leave a decision blank to accept the current plan.",
        "APPROVE keeps it, CHANGE opens a correction, REJECT blocks it.",
        "",
        "Approver: ______________________  Role: ______________________",
        "Date: ______________  Evidence/ticket: ______________________",
        "",
        "## Assets",
        "",
        "| ID | Item | Status | Decision | Instruction |",
        "|---|---|---|---|---|",
    ]
    for asset in sheet.assets:
        lines.append(
            f"| {asset.asset_id} | {asset.name} | {asset.status.value} | "
            "☐ APPROVE ☐ CHANGE ☐ REJECT | |"
        )
    lines.extend(
        [
            "",
            "## Layers",
            "",
            "| ID | Shot | Method | Decision | Instruction |",
            "|---|---|---|---|---|",
        ]
    )
    for shot in sheet.shots:
        for binding in shot.layers:
            lines.append(
                f"| {binding.layer_id} | {binding.shot_id} | {binding.method.value} | "
                "☐ APPROVE ☐ CHANGE ☐ REJECT | |"
            )
    lines.extend(
        [
            "",
            "## Free text",
            "",
            "- What must change before Gate 2B?",
            "",
            "  ______________________________________________________________",
            "",
            "- What is explicitly accepted as-is?",
            "",
            "  ______________________________________________________________",
            "",
            "Return this form with `corrections.jsonl`; each row becomes one typed",
            "correction and the plan is rebuilt into a new run.",
            "",
        ]
    )
    return "\n".join(lines)
