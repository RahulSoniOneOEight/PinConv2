"""Budget estimation with dedupe, reserve and cap control.

The approved estimates are already project-level lines. The handoff's per-asset
``estimate_usd`` is what double counts: three captures at $18 and three pack
preparations at $3. This module charges each shared line once and records the
saving instead of hiding it.
"""

from __future__ import annotations

from ..models import Estimate, ProductionPlan
from .errors import BudgetError
from .models import (
    AssetIntent,
    BudgetEstimate,
    BudgetLine,
    BudgetSummary,
)

_ACQUISITION = {"ES-01", "ES-02"}
_CAPTURE = {"ES-06"}
_PROCESSING = {"ES-05", "ES-07"}
_PROJECT = {"ES-03", "ES-04", "ES-08"}
_VARIANT = {"ES-11"}
_FALLBACK = {"ES-09"}


def _asset_members(plan: ProductionPlan) -> dict[str, list[str]]:
    members: dict[str, list[str]] = {}
    for asset in plan.assets:
        if asset.estimate_id:
            members.setdefault(asset.estimate_id, []).append(asset.id)
    return members


def _kind_for(estimate: Estimate) -> str:
    if estimate.kind.value == "fallback":
        return "fallback"
    if estimate.id in _ACQUISITION:
        return "acquisition"
    if estimate.id in _CAPTURE:
        return "capture"
    if estimate.id in _PROCESSING:
        return "processing"
    if estimate.id in _PROJECT:
        return "project"
    if estimate.id in _VARIANT:
        return "variant"
    raise BudgetError(f"{estimate.id}: no Level 2 budget kind")


def build_budget(plan: ProductionPlan, intents: list[AssetIntent]) -> BudgetEstimate:
    if [item.id for item in plan.estimates] != [item.id for item in plan.budget.estimates]:
        raise BudgetError("plan estimates and the budget estimate list disagree")

    lines: list[BudgetLine] = []
    assets_by_estimate = _asset_members(plan)
    for index, record in enumerate(plan.estimates, start=1):
        members = assets_by_estimate.get(record.id, [])
        lines.append(
            BudgetLine(
                line_id=f"BL-{index:03d}",
                label=record.label,
                estimate_id=record.id,
                asset_id=members[0] if members else None,
                asset_ids=members,
                kind=_kind_for(record),
                amount_usd=record.amount_usd,
                basis=record.basis.value,
                dedupe_key=f"{record.id}:{'session' if len(members) > 1 else 'line'}",
                in_worst_case=record.kind.value == "fallback",
                notes=record.notes,
            )
        )

    priced = {line.asset_id for line in lines if line.asset_id}
    next_index = len(lines) + 1
    for asset_id, note in (
        ("AS-14", "Gap B-2: second licensed bed, assumed under the same licence."),
        ("AS-15", "Gap B-1: synthetic narration fallback has no estimate or quote."),
    ):
        if asset_id in priced:
            continue
        lines.append(
            BudgetLine(
                line_id=f"BL-{next_index:03d}",
                label=f"{asset_id} fallback (unpriced)",
                asset_id=asset_id,
                asset_ids=[asset_id],
                kind="fallback",
                amount_usd=0.0,
                basis="operator_estimate",
                dedupe_key=f"fallback:{asset_id}",
                in_worst_case=True,
                unpriced=True,
                notes=note,
            )
        )
        next_index += 1

    subtotal_kinds = {"acquisition", "capture", "processing", "project", "variant"}
    subtotal = round(sum(line.amount_usd for line in lines if line.kind in subtotal_kinds), 2)
    fallback = round(sum(line.amount_usd for line in lines if line.kind == "fallback"), 2)
    reserve = round(subtotal * plan.budget.retry_reserve_pct / 100, 2)
    total = round(subtotal + reserve, 2)
    worst = round(total + fallback, 2)
    cap = plan.budget.cap_usd

    summary = BudgetSummary(
        currency=plan.budget.currency,
        cap_usd=cap,
        reserve_pct=plan.budget.retry_reserve_pct,
        subtotal_usd=subtotal,
        reserve_usd=reserve,
        total_usd=total,
        fallback_usd=fallback,
        worst_usd=worst,
        headroom_usd=round(cap - worst, 2),
        within_cap=total <= cap,
        worst_within_cap=worst <= cap,
        verified_quote_usd=round(
            sum(line.amount_usd for line in lines if line.basis == "verified_quote"), 2
        ),
        operator_estimate_usd=round(
            sum(line.amount_usd for line in lines if line.basis == "operator_estimate"), 2
        ),
        unpriced_lines=[line.line_id for line in lines if line.unpriced],
    )

    attributed = round(
        sum(
            line.amount_usd
            for line in lines
            if line.asset_id and line.kind in {"acquisition", "capture", "processing"}
        ),
        2,
    )
    raw = round(
        sum(intent.estimate_usd for intent in intents if intent.scope == "approved"),
        2,
    )

    result = BudgetEstimate(
        lines=lines,
        summary=summary,
        raw_attributed_usd=raw,
        dedupe_savings_usd=round(max(raw - attributed, 0.0), 2),
    )
    validate_budget(plan, result)
    return result


def validate_budget(plan: ProductionPlan, budget: BudgetEstimate) -> None:
    summary = budget.summary
    checks = [
        ("subtotal", summary.subtotal_usd, plan.budget.subtotal_usd),
        ("reserve", summary.reserve_usd, plan.budget.reserve_usd),
        ("total", summary.total_usd, plan.budget.total_usd),
        ("worst", summary.worst_usd, plan.budget.worst_case_usd),
        ("cap", summary.cap_usd, plan.budget.cap_usd),
    ]
    for label, actual, expected in checks:
        if round(actual, 2) != round(expected, 2):
            raise BudgetError(
                f"budget {label} is {actual:.2f} but the approved plan says {expected:.2f}"
            )
    if not summary.within_cap:
        raise BudgetError(f"estimated total {summary.total_usd:.2f} exceeds the cap")
    if not summary.worst_within_cap:
        raise BudgetError(f"worst case {summary.worst_usd:.2f} exceeds the cap")
    keys = [line.dedupe_key for line in budget.lines if line.dedupe_key]
    if len(keys) != len(set(keys)):
        raise BudgetError("a shared line was charged more than once")
