"""Shared validation context and helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..models import (
    BriefRevision,
    ProductionPlan,
    Severity,
    ValidationFinding,
    ValidationStatus,
)


def parse_timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


@dataclass
class FindingCollector:
    items: list[ValidationFinding] = field(default_factory=list)

    def add(
        self,
        rule: str,
        target: str,
        severity: Severity,
        status: ValidationStatus,
        detail: str,
        remediation: str = "No action required.",
    ) -> None:
        self.items.append(
            ValidationFinding(
                id=f"V-{len(self.items) + 1:03d}",
                rule=rule,
                target=target,
                severity=severity,
                status=status,
                detail=detail,
                remediation=remediation,
            )
        )


@dataclass(frozen=True)
class ValidationContext:
    plan: ProductionPlan
    brief: BriefRevision
    now: datetime
    collector: FindingCollector

    @contextmanager
    def group(self, rule: str, target: str, pass_detail: str) -> Iterator[None]:
        before = len(self.collector.items)
        yield
        if len(self.collector.items) == before:
            self.collector.add(
                rule, target, Severity.LOW, ValidationStatus.PASS, pass_detail
            )

    def add(
        self,
        rule: str,
        target: str,
        severity: Severity,
        status: ValidationStatus,
        detail: str,
        remediation: str,
    ) -> None:
        self.collector.add(rule, target, severity, status, detail, remediation)

    def fail(
        self, rule: str, target: str, severity: Severity, detail: str, remediation: str
    ) -> None:
        self.collector.add(rule, target, severity, ValidationStatus.FAIL, detail, remediation)

    def warn(self, rule: str, target: str, detail: str, remediation: str) -> None:
        self.collector.add(
            rule, target, Severity.MEDIUM, ValidationStatus.WARN, detail, remediation
        )
