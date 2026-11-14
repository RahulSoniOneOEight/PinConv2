"""OpenMontage adapter.

OpenMontage owns orchestration, stock routes, the ledger and Remotion renders.
This adapter never calls it directly from planning: it requires an approved
ledger and a connected client, and it records a reservation before every job.

The MCP bridge lives in the agent runtime. A standalone Python CLI must inject
one with ``OpenMontageEngine.from_mcp``; without it every call fails closed.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

from ..errors import Level2Error
from ..licence_gate import ensure_usable, gate_candidate
from ..models import GenerationSpec, MethodCandidate, ProcessingOp
from .base import (
    EngineAdapter,
    GenerationResult,
    ProbeInfo,
    ProcessedAsset,
    SpendLedger,
)

Client = Callable[[str, dict[str, object]], dict[str, object]]


def _num(value: object, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


class EngineUnavailableError(Level2Error):
    """The provider is not connected in this environment."""


class OpenMontageEngine(EngineAdapter):
    name = "openmontage"

    def __init__(self, ledger: SpendLedger, client: Client | None = None) -> None:
        self.ledger = ledger
        self.client = client

    @property
    def available(self) -> bool:
        return self.client is not None and os.environ.get("OPENMONTAGE_ENABLED") == "1"

    @classmethod
    def from_mcp(cls, ledger: SpendLedger, caller: Client) -> OpenMontageEngine:
        """Build an engine from an MCP tool caller supplied by the runtime."""

        return cls(ledger, caller)

    def render(
        self,
        timeline: Path,
        destination: Path,
        *,
        estimate_usd: float,
        line_id: str,
    ) -> Path:
        result = self._submit(
            "render",
            {
                "timeline": str(timeline),
                "destination": str(destination),
                "estimate_usd": estimate_usd,
            },
            line_id,
        )
        return Path(str(result["path"]))

    def _submit(
        self, operation: str, payload: dict[str, object], line_id: str
    ) -> dict[str, object]:
        if self.client is None or not self.available:
            raise EngineUnavailableError(
                "OpenMontage is not connected; enable it and retry after Gate 2A"
            )
        reservation = self.ledger.reserve(
            line_id, _num(payload.get("estimate_usd", 0.0)), operation
        )
        try:
            result = self.client(operation, payload)
        except Exception:
            self.ledger.release(line_id, reservation.amount_usd, operation)
            raise
        self.ledger.receipt(line_id, _num(result.get("cost_usd", 0.0)), operation)
        return result

    def search(self, asset_id: str, query: str) -> list[MethodCandidate]:
        result = self._submit("stock.search", {"asset_id": asset_id, "query": query}, "search")
        candidates: list[MethodCandidate] = []
        raw = result.get("candidates", [])
        if isinstance(raw, list):
            for item in raw:
                candidate = MethodCandidate.model_validate(item)
                candidates.append(gate_candidate(candidate))
        return candidates

    def acquire(self, candidate: MethodCandidate) -> Path:
        ensure_usable(candidate)
        result = self._submit(
            "stock.acquire",
            {"candidate_id": candidate.candidate_id, "estimate_usd": candidate.cost_usd},
            candidate.candidate_id,
        )
        return Path(str(result["path"]))

    def generate(self, spec: GenerationSpec) -> GenerationResult:
        raise EngineUnavailableError("OpenMontage generation is disabled; use fal or Runware")

    def process(
        self, recipe: list[ProcessingOp], source: Path, destination: Path
    ) -> ProcessedAsset:
        raise EngineUnavailableError("OpenMontage processing is not wired; use the local engine")

    def probe(self, path: Path) -> ProbeInfo:
        raise EngineUnavailableError("probing belongs to the local engine")
