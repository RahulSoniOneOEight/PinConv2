"""Budget arithmetic and reference checks."""

from __future__ import annotations

from ..models import EstimateKind, Severity
from .common import ValidationContext

TOLERANCE = 0.005


def validate_budget(context: ValidationContext) -> None:
    plan = context.plan
    budget = plan.budget
    brief = context.brief

    with context.group(
        "budget.cap_match", "budget", "the plan budget matches the approved brief cap"
    ):
        if abs(budget.cap_usd - brief.budget_cap_usd) > TOLERANCE:
            context.fail(
                "budget.cap_match",
                "budget",
                Severity.HIGH,
                f"plan cap {budget.cap_usd:.2f} differs from brief cap "
                f"{brief.budget_cap_usd:.2f}",
                "Use the brief cap or record a new approved brief revision.",
            )
        if budget.currency != brief.currency:
            context.fail(
                "budget.cap_match",
                "budget",
                Severity.HIGH,
                f"plan currency {budget.currency} differs from brief {brief.currency}",
                "Use one currency across the brief and plan.",
            )

    with context.group(
        "budget.cap",
        "budget",
        f"total {budget.total_usd:.2f} {budget.currency} is within "
        f"{budget.cap_usd:.2f}",
    ):
        if budget.total_usd > budget.cap_usd + TOLERANCE:
            context.fail(
                "budget.cap",
                "budget",
                Severity.HIGH,
                f"total {budget.total_usd:.2f} exceeds cap {budget.cap_usd:.2f}",
                "Remove a redundant route or raise the cap with human approval.",
            )

    with context.group(
        "budget.worst_case",
        "budget",
        f"worst case {budget.worst_case_usd:.2f} fits the cap",
    ):
        if budget.worst_case_usd > budget.cap_usd + TOLERANCE:
            context.fail(
                "budget.worst_case",
                "budget",
                Severity.HIGH,
                f"total plus fallback {budget.worst_case_usd:.2f} exceeds cap "
                f"{budget.cap_usd:.2f}",
                "Reduce the fallback cost or remove the redundant primary route.",
            )

    with context.group(
        "budget.references", "budget", "estimate references resolve and are typed"
    ):
        estimate_map = plan.estimate_map
        used_estimates: set[str] = set()
        for asset in plan.assets:
            if asset.estimate_id is None:
                continue
            used_estimates.add(asset.estimate_id)
            if asset.estimate_id not in estimate_map:
                context.fail(
                    "budget.references",
                    asset.id,
                    Severity.HIGH,
                    f"asset references unknown estimate {asset.estimate_id}",
                    "Create the estimate or remove the reference.",
                )
        for shot in plan.shots:
            for estimate_id in shot.estimate_ids:
                used_estimates.add(estimate_id)
                estimate = estimate_map.get(estimate_id)
                if estimate is None:
                    context.fail(
                        "budget.references",
                        shot.id,
                        Severity.HIGH,
                        f"shot references unknown estimate {estimate_id}",
                        "Create the estimate or remove the reference.",
                    )
                elif estimate.kind not in {EstimateKind.SHOT, EstimateKind.SHARED}:
                    context.fail(
                        "budget.references",
                        shot.id,
                        Severity.MEDIUM,
                        f"shot references {estimate.kind.value} estimate {estimate_id}",
                        "Shot work should reference a shot or shared estimate.",
                    )
        for estimate in plan.estimates:
            if estimate.id not in used_estimates:
                context.warn(
                    "budget.references",
                    estimate.id,
                    "estimate is not referenced by an asset or shot",
                    "Remove it or attach it to the work it prices.",
                )

    with context.group(
        "budget.reserve", "budget", "a retry reserve is present"
    ):
        if budget.reserve_usd <= 0:
            context.fail(
                "budget.reserve",
                "budget",
                Severity.MEDIUM,
                "no retry reserve is planned",
                "Add a reserve of at least 10% of the production subtotal.",
            )
        elif budget.retry_reserve_pct < 10:
            context.warn(
                "budget.reserve",
                "budget",
                f"retry reserve is {budget.retry_reserve_pct:.0f}%, below 10%",
                "Increase the reserve or record why the risk is lower.",
            )

    with context.group(
        "budget.basis", "budget", "every estimate declares its basis and confidence"
    ):
        for estimate in plan.estimates:
            if estimate.basis.value == "verified_quote" and not estimate.notes:
                context.warn(
                    "budget.basis",
                    estimate.id,
                    "verified quote has no reference in its notes",
                    "Record the quote reference or label it an operator estimate.",
                )
