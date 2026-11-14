"""Engine adapter contract and the spend ledger.

Every adapter goes through the same ledger: a reservation is written before a
paid call and a receipt after it. A ledger without Gate 2A authorisation refuses
to reserve, which is what keeps a dry run dry.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from pydantic import Field

from ...models import StrictModel, utc_now
from ..errors import SpendNotAuthorisedError
from ..models import GenerationSpec, MethodCandidate, ProcessingOp


class ProbeInfo(StrictModel):
    path: str
    codec: str
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    duration_seconds: float | None = None
    channels: int | None = None
    sample_rate: int | None = None


class ProcessedAsset(StrictModel):
    path: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    bytes: int = Field(ge=0)
    probe: ProbeInfo
    ops: list[str] = Field(default_factory=list)


class GenerationResult(StrictModel):
    provider: str
    job_id: str
    path: str | None = None
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    cost_usd: float = Field(ge=0)
    disclosed: bool


class LedgerEntry(StrictModel):
    entry_id: str = Field(pattern=r"^LE-\d{4}$")
    kind: str = Field(pattern=r"^(reservation|receipt|release)$")
    line_id: str
    amount_usd: float = Field(ge=0)
    reference: str
    created_at: str = Field(default_factory=utc_now)


class SpendLedger:
    """Append-only ledger with an explicit authorisation switch."""

    def __init__(self, path: Path, *, authorised: bool = False) -> None:
        self.path = Path(path)
        self.authorised = authorised
        self.entries: list[LedgerEntry] = []
        if self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self.entries.append(LedgerEntry.model_validate_json(line))

    def _append(self, kind: str, line_id: str, amount: float, reference: str) -> LedgerEntry:
        entry = LedgerEntry(
            entry_id=f"LE-{len(self.entries) + 1:04d}",
            kind=kind,
            line_id=line_id,
            amount_usd=round(amount, 2),
            reference=reference,
        )
        self.entries.append(entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(entry.model_dump(mode="json"), sort_keys=True) + "\n")
        return entry

    def reserve(self, line_id: str, amount: float, reference: str) -> LedgerEntry:
        if not self.authorised:
            raise SpendNotAuthorisedError("no reservation without an approved Gate 2A")
        return self._append("reservation", line_id, amount, reference)

    def receipt(self, line_id: str, amount: float, reference: str) -> LedgerEntry:
        return self._append("receipt", line_id, amount, reference)

    def release(self, line_id: str, amount: float, reference: str) -> LedgerEntry:
        return self._append("release", line_id, amount, reference)

    def open_reservations(self) -> int:
        open_count = 0
        for entry in self.entries:
            if entry.kind == "reservation":
                open_count += 1
            elif entry.kind in {"receipt", "release"} and open_count:
                open_count -= 1
        return open_count

    def spent_usd(self) -> float:
        return round(sum(entry.amount_usd for entry in self.entries if entry.kind == "receipt"), 2)

    def receipts(self) -> int:
        return sum(1 for entry in self.entries if entry.kind == "receipt")

    def summary(self) -> dict[str, object]:
        return {
            "entries": [entry.model_dump(mode="json") for entry in self.entries],
            "reservations": sum(1 for entry in self.entries if entry.kind == "reservation"),
            "receipts": self.receipts(),
            "releases": sum(1 for entry in self.entries if entry.kind == "release"),
            "open_reservations": self.open_reservations(),
            "spent_usd": self.spent_usd(),
        }


class EngineAdapter(Protocol):
    name: str

    def search(self, asset_id: str, query: str) -> list[MethodCandidate]: ...

    def acquire(self, candidate: MethodCandidate) -> Path: ...

    def generate(self, spec: GenerationSpec) -> GenerationResult: ...

    def process(
        self, recipe: list[ProcessingOp], source: Path, destination: Path
    ) -> ProcessedAsset: ...

    def probe(self, path: Path) -> ProbeInfo: ...
