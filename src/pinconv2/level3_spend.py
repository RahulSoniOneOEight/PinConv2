"""Level 3 production spend ledger.

Every production step records a line: what ran, which tool/provider, the quote,
the actual cost, and the running total. Local steps (ffmpeg, ShortGPT, local
OpenMontage render, QC) are $0; paid fal/Runware hero generation is reserved
and receipted against the $2.00 cap.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import Field

from .models import StrictModel, utc_now

CAP_USD = 2.00


class SpendEntry(StrictModel):
    id: str = Field(pattern=r"^L3-\d{3}$")
    step: str = Field(min_length=1, max_length=80)
    provider: str = Field(min_length=1, max_length=40)
    description: str = Field(min_length=1, max_length=300)
    quote_usd: float = Field(ge=0)
    actual_usd: float = Field(default=0, ge=0)
    status: str = Field(pattern=r"^(reserved|receipt|released|skipped)$")
    created_at: str = Field(default_factory=utc_now)


class Level3Ledger:
    def __init__(self, path: Path, cap_usd: float = CAP_USD) -> None:
        self.path = Path(path)
        self.cap = cap_usd
        self.entries: list[SpendEntry] = []
        if self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self.entries.append(SpendEntry.model_validate_json(line))

    def _append(self, entry: SpendEntry) -> SpendEntry:
        self.entries.append(entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(entry.model_dump_json() + "\n")
        return entry

    def _next_id(self) -> str:
        return f"L3-{len(self.entries) + 1:03d}"

    def spent(self) -> float:
        return round(
            sum(entry.actual_usd for entry in self.entries if entry.status == "receipt"), 2
        )

    def committed(self) -> float:
        reserved = sum(
            entry.quote_usd for entry in self.entries if entry.status == "reserved"
        )
        closed = sum(
            entry.quote_usd
            for entry in self.entries
            if entry.status in {"receipt", "released"} and entry.quote_usd > 0
        )
        return round(max(0.0, reserved - closed), 2)

    def remaining(self) -> float:
        return round(self.cap - self.spent() - self.committed(), 2)

    def zero(self, step: str, provider: str, description: str) -> SpendEntry:
        return self._append(
            SpendEntry(
                id=self._next_id(),
                step=step,
                provider=provider,
                description=description,
                quote_usd=0.0,
                actual_usd=0.0,
                status="receipt",
            )
        )

    def reserve(self, step: str, provider: str, description: str, quote_usd: float) -> SpendEntry:
        if quote_usd <= 0:
            raise ValueError("a paid step needs a positive quote")
        if quote_usd > self.remaining() + 0.0001:
            raise ValueError(f"quote ${quote_usd:.2f} exceeds remaining ${self.remaining():.2f}")
        return self._append(
            SpendEntry(
                id=self._next_id(),
                step=step,
                provider=provider,
                description=description,
                quote_usd=round(quote_usd, 4),
                status="reserved",
            )
        )

    def receipt(self, entry: SpendEntry, actual_usd: float) -> SpendEntry:
        if entry.status != "reserved":
            raise ValueError("receipt must follow a reservation")
        return self._append(
            entry.model_copy(
                update={
                    "id": self._next_id(),
                    "status": "receipt",
                    "actual_usd": round(actual_usd, 4),
                }
            )
        )

    def release(self, entry: SpendEntry, reason: str) -> SpendEntry:
        if entry.status != "reserved":
            raise ValueError("release must follow a reservation")
        return self._append(
            entry.model_copy(
                update={
                    "id": self._next_id(),
                    "status": "released",
                    "description": f"{entry.description} — released: {reason}"[:300],
                }
            )
        )

    def summary(self) -> dict[str, object]:
        return {
            "cap_usd": self.cap,
            "spent_usd": self.spent(),
            "committed_usd": self.committed(),
            "remaining_usd": self.remaining(),
            "within_cap": self.spent() + self.committed() <= self.cap + 0.0001,
            "entries": [entry.model_dump(mode="json") for entry in self.entries],
        }


def render_spend(ledger: Level3Ledger) -> str:
    summary = ledger.summary()
    lines = [
        "# Level 3 production spend",
        "",
        "| Cap | Spent | Committed | Remaining | Within cap |",
        "|---|---|---|---|---|",
        f"| ${summary['cap_usd']:.2f} | ${summary['spent_usd']:.2f} | "
        f"${summary['committed_usd']:.2f} | ${summary['remaining_usd']:.2f} | "
        f"{'yes' if summary['within_cap'] else 'NO'} |",
        "",
        "| ID | Step | Provider | Description | Quote | Actual | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for entry in ledger.entries:
        lines.append(
            f"| {entry.id} | {entry.step} | {entry.provider} | {entry.description} | "
            f"${entry.quote_usd:.2f} | ${entry.actual_usd:.2f} | {entry.status} |"
        )
    lines.extend(
        [
            "",
            "## Rules",
            "",
            "- Local ffmpeg / ShortGPT / OpenMontage render / QC = $0 lines.",
            "- fal/Runware hero generation is reserved, then receipted.",
            "- No step may exceed the $2.00 cap; quotes above remaining are refused.",
            "",
        ]
    )
    return "\n".join(lines)


def write_spend(ledger: Level3Ledger, root: Path) -> None:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / "LEVEL3-SPEND.md").write_text(render_spend(ledger), encoding="utf-8")
    (root / "level3-spend.json").write_text(
        json.dumps(ledger.summary(), indent=2) + "\n", encoding="utf-8"
    )
