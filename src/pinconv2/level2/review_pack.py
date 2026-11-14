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
    ProviderSpendSummary,
    SourcingReport,
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
    if budget.mode == "lean":
        lines.append(
            f"- **Lean in-kind mode:** cash total $0.00, in-kind value "
            f"${budget.in_kind_usd:,.2f} across {len(budget.substitutions)} lines. "
            "Gate 2A approval covers these substitutions."
        )
        for item in budget.substitutions:
            lines.append(f"  - {item.estimate_id} {item.label}: {item.route} (risk: {item.risk})")
    if not summary.within_cap or not summary.worst_within_cap:
        overage = round(max(summary.total_usd, summary.worst_usd) - summary.cap_usd, 2)
        lines.append(
            f"- **BLOCKED: the plan is ${overage:,.2f} over the effective cap.** "
            "Gate 2A cannot be approved until the scope or the cap changes."
        )
    return lines


def render_budget(
    budget: BudgetEstimate,
    plan: ProductionPlan,
    provider: ProviderSpendSummary | None = None,
) -> str:
    lines = [
        f"# Level 2 budget — {plan.project_id} rev-{plan.revision:03d}",
        "",
        "**Status: operator estimate. No line is a verified quote and no money has been spent.**",
        "",
        *budget_table_markdown(budget),
        "",
        *budget_summary_markdown(budget),
        "",
    ]
    if provider is not None:
        lines.extend(
            [
                "## Provider spend (fal.ai + Runware)",
                "",
                f"- Cap: {_money(provider.cap_usd)} · per-job max: "
                f"{_money(provider.per_job_max_usd)}",
                f"- Spent: {_money(provider.spent_usd)} · committed: "
                f"{_money(provider.committed_usd)} · remaining: "
                f"{_money(provider.remaining_usd)} · calls: {provider.calls}",
                "- Every paid call must be quoted, authorised against this cap and receipted.",
                "",
            ]
        )
    if budget.mode == "lean":
        lines.append(
            f"Raw per-asset estimates in the handoff: {_money(budget.raw_attributed_usd)}. "
            f"Lean mode carries {_money(budget.in_kind_usd)} as in-kind across "
            f"{len(budget.substitutions)} lines; cash total is $0.00."
        )
    else:
        lines.append(
            f"Raw per-asset estimates in the handoff: {_money(budget.raw_attributed_usd)}. "
            f"Dedupe saves {_money(budget.dedupe_savings_usd)} by charging the capture "
            "session and pack preparation once."
        )
    lines.append("")
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
        ("In-kind value", budget.in_kind_usd),
    ):
        builder.paragraph(f"{label}: {_money(value)}")
    if budget.mode == "lean":
        builder.paragraph(
            f"Lean in-kind mode: cash $0.00, in-kind value {_money(budget.in_kind_usd)}. "
            "Gate 2A approval covers the substitutions listed in the review pack.",
            bold=True,
        )
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
    provider: ProviderSpendSummary | None = None,
    sourcing: SourcingReport | None = None,
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
        f"| fal+Runware cap | {_money(provider.cap_usd) if provider else 'not configured'} |",
        f"| fal+Runware remaining | {_money(provider.remaining_usd) if provider else 'n/a'} |",
        f"| Mode | {budget.mode} |",
        f"| In-kind value | {_money(budget.in_kind_usd)} |",
        "",
        "## Budget",
        "",
        *budget_table_markdown(budget),
        "",
        *budget_summary_markdown(budget),
        "",
        (
            f"Raw per-asset estimates: {_money(budget.raw_attributed_usd)}; lean mode "
            f"carries {_money(budget.in_kind_usd)} as in-kind."
            if budget.mode == "lean"
            else f"Raw per-asset estimates: {_money(budget.raw_attributed_usd)}; dedupe saves "
            f"{_money(budget.dedupe_savings_usd)}."
        ),
        "",
        "## Assets",
        "",
    ]
    intent_map = {intent.asset_id: intent for intent in intents}
    shot_by_layer = {decision.layer_id: decision.shot_id for decision in decisions}
    for asset in sheet.assets:
        intent = intent_map[asset.asset_id]
        badge = _BADGE.get(asset.status, asset.status.value)
        if budget.mode == "lean":
            cost = (
                f"$0.00 cash · {_money(intent.estimate_usd)} in-kind"
                if intent.estimate_usd
                else "$0.00 cash"
            )
        else:
            cost = _money(intent.estimate_usd)
        cost_ref = (
            f" ({intent.estimate_id})"
            if intent.estimate_id
            else " (fallback, unpriced)"
            if intent.scope != "approved"
            else ""
        )
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
                f"- Cost: {cost}{cost_ref}",
                f"- Acceptance: {asset.acceptance}",
                f"- Preview: {_asset_preview(asset, shot_by_layer)}",
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
    if provider is not None:
        lines.extend(
            [
                "",
                "## Provider spend",
                "",
                f"- Cap: {_money(provider.cap_usd)}; per-job max: "
                f"{_money(provider.per_job_max_usd)}",
                f"- Spent: {_money(provider.spent_usd)}; committed: "
                f"{_money(provider.committed_usd)}; remaining: "
                f"{_money(provider.remaining_usd)}",
            ]
        )
        for name, totals in sorted(provider.per_provider.items()):
            lines.append(f"- {name}: {_money(totals.spent_usd)} spent across {totals.calls} calls")

    lines.extend(
        [
            "",
            "## Previews",
            "",
            "| Shot | 16:9 | 9:16 |",
            "|---|---|---|",
        ]
    )
    for shot in sheet.shots:
        lines.append(
            f"| {shot.shot_id} | [16:9](build-sheet/previews/16x9/{shot.shot_id}.svg) | "
            f"[9:16](build-sheet/previews/9x16/{shot.shot_id}.svg) |"
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
                "- Cost: "
                + (
                    f"$0.00 cash · {_money(variant.cost_usd)} in-kind"
                    if budget.mode == "lean" and variant.cost_usd
                    else "$0.00 cash"
                    if budget.mode == "lean"
                    else _money(variant.cost_usd)
                ),
                f"- Status: {variant.check_status}",
                f"- Blockers: {', '.join(variant.blockers) or 'none'}",
                "",
            ]
        )
    decision_candidates = sum(len(decision.candidates) for decision in decisions)
    sourcing_candidates = (
        sum(len(asset.candidates) for asset in sourcing.assets)
        if sourcing is not None
        else 0
    )
    candidates = decision_candidates + sourcing_candidates
    sourcing_label = "discovery complete" if sourcing_candidates else "not run"
    if sourcing is not None:
        lines.extend(
            [
                "## Sourcing",
                "",
                "| Asset | Query | Status | Candidates | Chosen |",
                "|---|---|---|---|---|",
            ]
        )
        for sourcing_asset in sourcing.assets:
            lines.append(
                f"| {sourcing_asset.asset_id} | {sourcing_asset.query} | "
                f"{sourcing_asset.status} | {len(sourcing_asset.candidates)} | "
                f"{sourcing_asset.chosen_candidate or '—'} |"
            )
        for sourcing_asset in sourcing.assets:
            for candidate in sourcing_asset.candidates:
                if candidate.candidate_id != sourcing_asset.chosen_candidate:
                    continue
                lines.extend(
                    [
                        "",
                        f"Chosen for {sourcing_asset.asset_id}: **{candidate.title}** by "
                        f"{candidate.creator} · {candidate.licence_class.value} · "
                        f"fit {candidate.fit_score}",
                        f"- {candidate.attribution}",
                        f"- {candidate.page_url}",
                    ]
                )

    lines.extend(
        [
            "## Compliance",
            "",
            f"- Sourcing round: **{sourcing_label}**; {candidates} candidates "
            f"recorded ({sourcing_candidates} from sourcing).",
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
            ["Mode", budget.mode],
            ["In-kind value", _money(budget.in_kind_usd)],
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
        if budget.mode == "lean":
            builder.bullet(
                "Cost: $0.00 cash"
                + (f" · {_money(intent.estimate_usd)} in-kind" if intent.estimate_usd else "")
            )
        else:
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


def _asset_preview(asset: object, shot_by_layer: dict[str, str]) -> str:
    """Point a reviewer at the shot preview that contains the asset's first layer."""

    bindings = getattr(asset, "bindings", [])
    if not bindings:
        return "audio asset; no visual preview"
    shot_id = shot_by_layer.get(bindings[0])
    if shot_id is None:
        return "no visual preview"
    return f"build-sheet/previews/16x9/{shot_id}.svg"
