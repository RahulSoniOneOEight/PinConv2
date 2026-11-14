"""fal.ai and Runware adapters, governed by the provider budget.

These are the only paid production providers. Every call is quoted, reserved
and receipted through the ProviderGovernor, so the $2 cap is enforced before a
request leaves the machine.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

from ..errors import Level2Error, MethodMatrixError
from ..governance import ProviderGovernor
from ..models import GenerationSpec, MethodCandidate, ProcessingOp
from .base import EngineAdapter, GenerationResult, ProbeInfo, ProcessedAsset

Client = Callable[[str, dict[str, object]], dict[str, object]]


class ProviderUnavailableError(Level2Error):
    """No credential or connection for this provider."""


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


class FalRunwareEngine(EngineAdapter):
    name = "fal-runware"

    def __init__(
        self,
        provider: str,
        governor: ProviderGovernor,
        client: Client | None = None,
    ) -> None:
        if provider not in {"fal", "runware"}:
            raise ValueError(f"unknown provider {provider!r}")
        self.provider = provider
        self.governor = governor
        self.client = client

    @property
    def available(self) -> bool:
        env = "FAL_KEY" if self.provider == "fal" else "RUNWARE_API_KEY"
        return self.client is not None and bool(os.environ.get(env))

    def generate(self, spec: GenerationSpec) -> GenerationResult:
        if not spec.disclosure_required:
            raise MethodMatrixError("generated media must carry a disclosure")
        if not self.available:
            raise ProviderUnavailableError(
                f"{self.provider} is not connected; add its key and retry after Gate 2A"
            )
        work_item = spec.budget_line_id or "generation"
        reservation = self.governor.reserve(self.provider, spec.cost_usd, work_item)
        try:
            result = (
                self.client(
                    "generate",
                    {
                        "provider": self.provider,
                        "model": spec.model,
                        "prompt": spec.prompt,
                        "seed": spec.seed,
                        "estimate_usd": spec.cost_usd,
                    },
                )
                if self.client is not None
                else {}
            )
        except Exception as error:
            self.governor.release(reservation, f"failed: {error}")
            raise
        actual = _num(result.get("cost_usd", 0.0))
        job_id = str(result.get("job_id", reservation.id))
        self.governor.receipt(reservation, actual, job_id)
        return GenerationResult(
            provider=self.provider,
            job_id=job_id,
            path=str(result.get("path")) if result.get("path") else None,
            sha256=str(result["sha256"]) if result.get("sha256") else None,
            cost_usd=actual,
            disclosed=True,
        )

    def search(self, asset_id: str, query: str) -> list[MethodCandidate]:
        raise ProviderUnavailableError(f"{self.provider} does not serve stock search")

    def acquire(self, candidate: MethodCandidate) -> Path:
        raise ProviderUnavailableError(f"{self.provider} does not acquire stock")

    def process(
        self, recipe: list[ProcessingOp], source: Path, destination: Path
    ) -> ProcessedAsset:
        raise ProviderUnavailableError(f"{self.provider} processing is not wired")

    def probe(self, path: Path) -> ProbeInfo:
        raise ProviderUnavailableError(f"{self.provider} does not probe local files")
