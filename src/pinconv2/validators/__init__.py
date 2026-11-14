"""Deterministic plan validation."""

from __future__ import annotations

from datetime import datetime, timezone

from ..models import (
    BriefRevision,
    CheckMethod,
    CheckStatus,
    ProductionPlan,
    ValidationReport,
    ValidationStatus,
)
from .budget import validate_budget
from .common import FindingCollector, ValidationContext
from .exact_data import validate_exact_data
from .layers import validate_layers
from .rights import validate_rights
from .timing import validate_timing
from .traceability import validate_traceability


def validate_plan(
    plan: ProductionPlan, brief: BriefRevision, *, now: datetime | None = None
) -> ValidationReport:
    collector = FindingCollector()
    context = ValidationContext(
        plan=plan,
        brief=brief,
        now=now or datetime.now(timezone.utc),
        collector=collector,
    )
    validate_timing(context)
    validate_exact_data(context)
    validate_layers(context)
    validate_budget(context)
    validate_rights(context)
    validate_traceability(context)

    any_failure = any(
        finding.status is ValidationStatus.FAIL for finding in collector.items
    )
    check_status: dict[str, CheckStatus] = {}
    for check in plan.checks:
        if check.status is CheckStatus.NOT_APPLICABLE:
            check_status[check.id] = CheckStatus.NOT_APPLICABLE
        elif check.method is CheckMethod.STRUCTURAL:
            check_status[check.id] = (
                CheckStatus.FAIL if any_failure else CheckStatus.PASS
            )
        else:
            check_status[check.id] = CheckStatus.PENDING

    return ValidationReport(
        project_id=plan.project_id,
        plan_revision=plan.revision,
        plan_hash=plan.plan_hash(),
        findings=collector.items,
        check_status=check_status,
    )
