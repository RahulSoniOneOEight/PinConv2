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
    BudgetSubstitution,
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


_LEAN_ROUTES: dict[str, tuple[str, str]] = {
    "ES-01": (
        "CC0/CC BY library track with attribution",
        "Licence availability and Content ID review",
    ),
    "ES-02": (
        "Operator/team records the approved read in-house",
        "Voice quality; performer release HI-03 still required",
    ),
    "ES-03": ("In-house edit and compositing", "Schedule and operator hours"),
    "ES-04": ("In-house grade from a deterministic LUT", "Colour quality vs a paid colorist"),
    "ES-05": ("Supplied pack files cut out in-house", "Label edge quality"),
    "ES-06": (
        "Self-operated capture with phone/DSLR and practical light",
        "Premium capture quality and hand model release HI-04",
    ),
    "ES-07": ("Range packs prepared in-house", "Label edge quality"),
    "ES-08": ("End card built in Remotion", "Type layout approval HI-05"),
    "ES-09": ("Self-captured pack fallback", "Same as the capture session"),
    "ES-11": ("In-house 9:16 rebuild", "AC-16 safe area still pending"),
}


def build_budget(
    plan: ProductionPlan,
    intents: list[AssetIntent],
    cap_usd: float | None = None,
    lean: bool = False,
) -> BudgetEstimate:
    effective_cap = (
        plan.budget.cap_usd if cap_usd is None else min(plan.budget.cap_usd, cap_usd)
    )
    if effective_cap <= 0:
        raise BudgetError("the effective budget cap must be positive")
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

    original_amounts = {line.line_id: line.amount_usd for line in lines}
    if lean:
        lines = [
            line.model_copy(
                update={
                    "amount_usd": 0.0,
                    "notes": f"in-kind: {_LEAN_ROUTES.get(line.estimate_id or '', ('', ''))[0]}",
                }
            )
            for line in lines
        ]

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
    cap = effective_cap

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
    substitutions: list[BudgetSubstitution] = []
    if lean:
        for line in lines:
            amount = original_amounts.get(line.line_id, 0.0)
            if amount <= 0 or not line.estimate_id:
                continue
            route, risk = _LEAN_ROUTES.get(
                line.estimate_id, ("In-house zero-cash route", "Requires operator approval")
            )
            substitutions.append(
                BudgetSubstitution(
                    id=f"BS-{len(substitutions) + 1:02d}",
                    estimate_id=line.estimate_id,
                    label=line.label,
                    cash_usd=0.0,
                    in_kind_usd=amount,
                    route=route,
                    risk=risk,
                )
            )
    raw = round(
        sum(intent.estimate_usd for intent in intents if intent.scope == "approved"),
        2,
    )

    result = BudgetEstimate(
        lines=lines,
        summary=summary,
        raw_attributed_usd=raw,
        dedupe_savings_usd=0.0 if lean else round(max(raw - attributed, 0.0), 2),
        mode="lean" if lean else "approved",
        in_kind_usd=round(sum(item.in_kind_usd for item in substitutions), 2),
        substitutions=substitutions,
    )
    validate_budget(plan, result, effective_cap, lean=lean)
    return result


def validate_budget(
    plan: ProductionPlan,
    budget: BudgetEstimate,
    effective_cap: float | None = None,
    *,
    lean: bool = False,
) -> None:
    summary = budget.summary
    if lean:
        if summary.subtotal_usd != 0 or summary.total_usd != 0:
            raise BudgetError("a lean budget must carry zero cash")
        if effective_cap is not None and summary.cap_usd != effective_cap:
            raise BudgetError("the lean budget cap does not match the effective cap")
        return
    checks = [
        ("subtotal", summary.subtotal_usd, plan.budget.subtotal_usd),
        ("reserve", summary.reserve_usd, plan.budget.reserve_usd),
        ("total", summary.total_usd, plan.budget.total_usd),
        ("worst", summary.worst_usd, plan.budget.worst_case_usd),
    ]
    if effective_cap is not None:
        checks.append(("cap", summary.cap_usd, effective_cap))
    for label, actual, expected in checks:
        if round(actual, 2) != round(expected, 2):
            raise BudgetError(
                f"budget {label} is {actual:.2f} but the approved plan says {expected:.2f}"
            )
    # Exceeding the cap blocks Gate 2A; it must not abort planning, otherwise the
    # user never sees the variance or the way back under the cap.
    keys = [line.dedupe_key for line in budget.lines if line.dedupe_key]
    if len(keys) != len(set(keys)):
        raise BudgetError("a shared line was charged more than once")
