"""Provider spend governance for fal.ai and Runware.

The project budget says what a plan may cost. This module is the harder guard:
it controls the only money the agent can actually spend — paid provider calls.
Every call is quoted, authorised, reserved, receipted and reconciled against a
shared cap, so a single job cannot eat the production budget and a failed job
cannot leak a reservation.
"""

from __future__ import annotations

import json
from pathlib import Path

from .errors import Level2Error, SpendNotAuthorisedError
from .models import (
    GatePacket,
    PacketStatus,
    ProviderBudget,
    ProviderSpendEntry,
    ProviderSpendSummary,
    ProviderTotals,
)

PROVIDERS = ("fal", "runware")
_EPSILON = 0.0001


class ProviderBudgetError(Level2Error):
    """A provider call would exceed its cap, per-job limit or authorisation."""


def _load(path: Path) -> list[ProviderSpendEntry]:
    if not path.is_file():
        return []
    entries: list[ProviderSpendEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(ProviderSpendEntry.model_validate_json(line))
    return entries


class ProviderGovernor:
    """Authorise and account for every fal/Runware call."""

    def __init__(
        self,
        path: Path,
        budget: ProviderBudget,
        *,
        gate: GatePacket | None = None,
    ) -> None:
        if budget.cap_usd <= 0:
            raise ProviderBudgetError("the provider cap must be positive")
        if budget.per_job_max_usd <= 0 or budget.per_job_max_usd > budget.cap_usd:
            raise ProviderBudgetError("the per-job cap must be within the provider cap")
        unknown = set(budget.providers) - set(PROVIDERS)
        if unknown:
            raise ProviderBudgetError(f"unknown providers: {sorted(unknown)}")
        self.path = Path(path)
        self.budget = budget
        self.gate = gate
        self.entries = _load(self.path)

    @property
    def approved(self) -> bool:
        return (
            self.gate is not None
            and self.gate.gate.value == "2a"
            and self.gate.status is PacketStatus.APPROVED
            and bool(self.gate.approved_by)
        )

    # -- arithmetic ------------------------------------------------------

    def spent(self) -> float:
        return round(sum(entry.actual_usd for entry in self.entries if entry.kind == "receipt"), 2)

    def _open_reservations(self) -> list[ProviderSpendEntry]:
        closed = {
            entry.reservation_id
            for entry in self.entries
            if entry.kind in {"receipt", "release"} and entry.reservation_id
        }
        return [
            entry
            for entry in self.entries
            if entry.kind == "reservation" and entry.id not in closed
        ]

    def committed(self) -> float:
        return round(sum(entry.quoted_usd for entry in self._open_reservations()), 2)

    def remaining(self) -> float:
        return round(self.budget.cap_usd - self.spent() - self.committed(), 2)

    def per_provider(self) -> dict[str, ProviderTotals]:
        totals: dict[str, ProviderTotals] = {}
        open_reservations = self._open_reservations()
        for provider in self.budget.providers:
            mine = [entry for entry in self.entries if entry.provider == provider]
            totals[provider] = ProviderTotals(
                provider=provider,
                quoted_usd=round(
                    sum(
                        entry.quoted_usd
                        for entry in open_reservations
                        if entry.provider == provider
                    ),
                    2,
                ),
                spent_usd=round(
                    sum(entry.actual_usd for entry in mine if entry.kind == "receipt"),
                    2,
                ),
                calls=sum(1 for entry in mine if entry.kind == "receipt"),
            )
        return totals

    def summary(self) -> ProviderSpendSummary:
        return ProviderSpendSummary(
            currency=self.budget.currency,
            cap_usd=self.budget.cap_usd,
            per_job_max_usd=self.budget.per_job_max_usd,
            committed_usd=self.committed(),
            spent_usd=self.spent(),
            remaining_usd=self.remaining(),
            calls=sum(1 for entry in self.entries if entry.kind == "receipt"),
            within_cap=self.spent() + self.committed() <= self.budget.cap_usd + _EPSILON,
            per_provider=self.per_provider(),
            entries=list(self.entries),
        )

    # -- lifecycle -------------------------------------------------------

    def _append(self, entry: ProviderSpendEntry) -> ProviderSpendEntry:
        self.entries.append(entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(entry.model_dump(mode="json"), sort_keys=True) + "\n")
        return entry

    def _next_id(self) -> str:
        return f"PS-{len(self.entries) + 1:04d}"

    def _is_closed(self, reservation_id: str) -> bool:
        return any(
            entry.kind in {"receipt", "release"} and entry.reservation_id == reservation_id
            for entry in self.entries
        )

    def reserve(self, provider: str, quote_usd: float, work_item: str) -> ProviderSpendEntry:
        if not self.approved:
            raise SpendNotAuthorisedError("no provider call before an approved Gate 2A")
        if provider not in self.budget.providers:
            raise ProviderBudgetError(f"{provider} is not an allowed provider")
        if quote_usd <= 0:
            raise ProviderBudgetError(
                "a paid call needs a positive quote; price the job before authorising it"
            )
        if quote_usd > self.budget.per_job_max_usd + _EPSILON:
            raise ProviderBudgetError(
                f"quote ${quote_usd:.2f} exceeds the per-job cap ${self.budget.per_job_max_usd:.2f}"
            )
        if quote_usd > self.remaining() + _EPSILON:
            raise ProviderBudgetError(
                f"quote ${quote_usd:.2f} exceeds the remaining "
                f"${self.remaining():.2f} of the ${self.budget.cap_usd:.2f} cap"
            )
        return self._append(
            ProviderSpendEntry(
                id=self._next_id(),
                kind="reservation",
                provider=provider,
                work_item=work_item,
                quoted_usd=round(quote_usd, 4),
                actual_usd=0.0,
                job_id=None,
            )
        )

    def receipt(
        self,
        reservation: ProviderSpendEntry,
        actual_usd: float,
        job_id: str,
    ) -> ProviderSpendEntry:
        if reservation.kind != "reservation":
            raise ProviderBudgetError("a receipt must follow a reservation")
        if reservation not in self.entries:
            raise ProviderBudgetError("the reservation does not belong to this ledger")
        if self._is_closed(reservation.id):
            raise ProviderBudgetError("this reservation is already receipted or released")
        if actual_usd < 0:
            raise ProviderBudgetError("a receipt cannot be negative")
        overage = round(actual_usd - reservation.quoted_usd, 4)
        if overage > max(0.01, reservation.quoted_usd * 0.10):
            raise ProviderBudgetError(
                f"actual ${actual_usd:.2f} exceeds the quote "
                f"${reservation.quoted_usd:.2f} by more than 10%; reconcile with the provider"
            )
        if actual_usd > self.remaining() + reservation.quoted_usd + _EPSILON:
            raise ProviderBudgetError("the receipt would exceed the provider cap")
        return self._append(
            ProviderSpendEntry(
                id=self._next_id(),
                kind="receipt",
                provider=reservation.provider,
                work_item=reservation.work_item,
                quoted_usd=reservation.quoted_usd,
                actual_usd=round(actual_usd, 4),
                job_id=job_id,
                reservation_id=reservation.id,
            )
        )

    def release(self, reservation: ProviderSpendEntry, reason: str) -> ProviderSpendEntry:
        if reservation.kind != "reservation":
            raise ProviderBudgetError("only a reservation can be released")
        if self._is_closed(reservation.id):
            raise ProviderBudgetError("this reservation is already receipted or released")
        return self._append(
            ProviderSpendEntry(
                id=self._next_id(),
                kind="release",
                provider=reservation.provider,
                work_item=f"{reservation.work_item}: {reason}"[:200],
                quoted_usd=reservation.quoted_usd,
                actual_usd=0.0,
                job_id=None,
                reservation_id=reservation.id,
            )
        )

    def write_view(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.summary().model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return path


def open_governor(run_dir: Path, budget: ProviderBudget) -> ProviderGovernor:
    """Open a governor whose authorisation comes from the Gate 2A packet."""

    packet_path = run_dir / "gate2" / "packet-2a.json"
    gate = (
        GatePacket.model_validate_json(packet_path.read_text(encoding="utf-8"))
        if packet_path.is_file()
        else None
    )
    return ProviderGovernor(run_dir / "provider-spend.jsonl", budget, gate=gate)


def empty_budget(cap_usd: float = 2.0, per_job_max_usd: float = 0.5) -> ProviderBudget:
    return ProviderBudget(
        currency="USD",
        cap_usd=cap_usd,
        per_job_max_usd=per_job_max_usd,
        providers=list(PROVIDERS),
        note=(
            "Shared fal.ai + Runware production cap. Every paid call is quoted, "
            "authorised against this cap and receipted."
        ),
    )
