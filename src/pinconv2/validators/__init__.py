"""Deterministic plan validation."""

from __future__ import annotations

from datetime import datetime, timezone

from ..models import (
    BriefRevision,
    CheckMethod,
    CheckStatus,
    ProductionPlan,
    Severity,
    ValidationFinding,
    ValidationReport,
    ValidationStatus,
)
from .budget import validate_budget
from .common import FindingCollector, ValidationContext
from .effects import validate_effects
from .exact_data import validate_exact_data
from .layers import validate_layers
from .rights import validate_rights
from .timing import validate_timing
from .traceability import validate_traceability
from .variants import validate_variants


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
    validate_effects(context)
    validate_variants(context)
    validate_traceability(context)

    by_rule: dict[str, list[ValidationFinding]] = {}
    for finding in collector.items:
        by_rule.setdefault(finding.rule, []).append(finding)

    check_status: dict[str, CheckStatus] = {}
    for check in plan.checks:
        if check.status is CheckStatus.NOT_APPLICABLE:
            check_status[check.id] = CheckStatus.NOT_APPLICABLE
            continue
        if check.method is not CheckMethod.STRUCTURAL:
            check_status[check.id] = CheckStatus.PENDING
            continue
        missing = [rule for rule in check.rule_refs if rule not in by_rule]
        if missing:
            collector.add(
                "validation.check_evidence",
                check.id,
                Severity.HIGH,
                ValidationStatus.FAIL,
                f"check references rules with no evidence: {', '.join(missing)}",
                "Point the check at rules the validator actually runs.",
            )
            check_status[check.id] = CheckStatus.FAIL
            continue
        relevant = [finding for rule in check.rule_refs for finding in by_rule.get(rule, [])]
        if any(finding.status is ValidationStatus.FAIL for finding in relevant):
            check_status[check.id] = CheckStatus.FAIL
        elif any(finding.status is ValidationStatus.WARN for finding in relevant):
            check_status[check.id] = CheckStatus.PENDING
        else:
            check_status[check.id] = CheckStatus.PASS

    return ValidationReport(
        project_id=plan.project_id,
        plan_revision=plan.revision,
        plan_hash=plan.plan_hash(),
        findings=collector.items,
        check_status=check_status,
    )
