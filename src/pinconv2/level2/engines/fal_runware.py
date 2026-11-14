"""fal.ai and Runware adapters for generation and enhancement.

Both are paid providers. They share one guarded submission path: no approved
ledger, no job. A failed job releases its reservation instead of leaking it.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

from ..errors import Level2Error, MethodMatrixError
from ..models import GenerationSpec, MethodCandidate, ProcessingOp
from .base import EngineAdapter, GenerationResult, ProbeInfo, ProcessedAsset, SpendLedger

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


class ProviderUnavailableError(Level2Error):
    """No credential or connection for this provider."""


class FalRunwareEngine(EngineAdapter):
    name = "fal-runware"

    def __init__(
        self,
        provider: str,
        ledger: SpendLedger,
        client: Client | None = None,
    ) -> None:
        if provider not in {"fal", "runware"}:
            raise ValueError(f"unknown provider {provider!r}")
        self.provider = provider
        self.ledger = ledger
        self.client = client

    @property
    def available(self) -> bool:
        env = "FAL_KEY" if self.provider == "fal" else "RUNWARE_API_KEY"
        return self.client is not None and bool(os.environ.get(env))

    def _submit(
        self, operation: str, payload: dict[str, object], line_id: str
    ) -> dict[str, object]:
        if not self.available:
            raise ProviderUnavailableError(
                f"{self.provider} is not connected; add its key and retry after Gate 2A"
            )
        reservation = self.ledger.reserve(
            line_id, _num(payload.get("estimate_usd", 0.0)), operation
        )
        try:
            result = self.client(operation, payload) if self.client is not None else {}
        except Exception:
            self.ledger.release(line_id, reservation.amount_usd, operation)
            raise
        self.ledger.receipt(line_id, _num(result.get("cost_usd", 0.0)), operation)
        return result

    def search(self, asset_id: str, query: str) -> list[MethodCandidate]:
        raise ProviderUnavailableError(f"{self.provider} does not serve stock search")

    def acquire(self, candidate: MethodCandidate) -> Path:
        raise ProviderUnavailableError(f"{self.provider} does not acquire stock")

    def generate(self, spec: GenerationSpec) -> GenerationResult:
        if not spec.disclosure_required:
            raise MethodMatrixError("generated media must carry a disclosure")
        result = self._submit(
            "generate",
            {
                "provider": self.provider,
                "model": spec.model,
                "prompt": spec.prompt,
                "seed": spec.seed,
                "estimate_usd": spec.cost_usd,
            },
            spec.budget_line_id or "generation",
        )
        return GenerationResult(
            provider=self.provider,
            job_id=str(result["job_id"]),
            path=str(result.get("path")) if result.get("path") else None,
            sha256=str(result["sha256"]) if result.get("sha256") else None,
            cost_usd=_num(result.get("cost_usd", 0.0)),
            disclosed=bool(spec.disclosure_required),
        )

    def process(
        self, recipe: list[ProcessingOp], source: Path, destination: Path
    ) -> ProcessedAsset:
        raise ProviderUnavailableError(f"{self.provider} processing is not wired")

    def probe(self, path: Path) -> ProbeInfo:
        raise ProviderUnavailableError(f"{self.provider} does not probe local files")
