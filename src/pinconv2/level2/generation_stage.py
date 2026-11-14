"""Generation stage: paid media generation behind Gate 2A and the governor.

The stage is deliberately separate from ``run_build``: processing imported files
is local, while generation spends money. It loads the approved Gate 2A packet,
the project provider budget and the OpenMontage engine supplied by the caller,
then reserves and receipts every job through ``ProviderGovernor``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field

from ..models import StrictModel, utc_now
from ..store import ProjectStore
from .agents.generator import GenerationAgent
from .errors import GateOrderError
from .governance import ProviderGovernor
from .models import (
    GatePacket,
    GenerationSpec,
    PacketStatus,
    ProviderBudget,
    SourceStrategy,
)
from .store import Level2RunStore


class GenerationEntry(StrictModel):
    task_id: str
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    status: str = Field(pattern=r"^(generated|blocked|skipped)$")
    detail: str = Field(min_length=1, max_length=500)
    path: str | None = None
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    job_id: str | None = None
    cost_usd: float = Field(default=0, ge=0)


class GenerationReport(StrictModel):
    run_id: str
    plan_hash: str
    approved_by: str
    generated: int = Field(ge=0)
    blocked: int = Field(ge=0)
    skipped: int = Field(ge=0)
    spent_usd: float = Field(ge=0)
    entries: list[GenerationEntry] = Field(min_length=1)
    created_at: str = Field(default_factory=utc_now)


def _approved_packet(run_dir: Path) -> GatePacket:
    path = run_dir / "gate2" / "packet-2a.json"
    if not path.is_file():
        raise GateOrderError("no Gate 2A packet; run level2 plan first")
    packet = GatePacket.model_validate_json(path.read_text(encoding="utf-8"))
    if packet.status is not PacketStatus.APPROVED or not packet.approved_by:
        raise GateOrderError("Gate 2A is not approved; no generation may start")
    return packet


def run_generation(
    store: ProjectStore,
    project_id: str,
    revision: int,
    run_id: str,
    *,
    engine: Any,
    include_conditional: bool = False,
    assets: set[str] | None = None,
) -> GenerationReport:
    """Generate approved tasks with an injected engine and provider governor."""

    run = Level2RunStore(store.project_dir(project_id))
    level2 = run.read_level2(run_id)
    run_dir = run.run_dir(run_id)
    packet = _approved_packet(run_dir)
    budget_path = run_dir / "provider-budget.json"
    if not budget_path.is_file():
        raise GateOrderError("no provider budget; run level2 plan first")
    budget = ProviderBudget.model_validate_json(budget_path.read_text(encoding="utf-8"))
    governor = ProviderGovernor(run_dir / "provider-spend.jsonl", budget, gate=packet)
    agent = GenerationAgent(engine, governor)

    entries: list[GenerationEntry] = []
    for task in level2.tasks:
        spec: GenerationSpec | None = task.generation
        if spec is None or task.source_strategy is not SourceStrategy.GENERATE:
            continue
        if assets is not None and task.asset_id not in assets:
            continue
        if task.conditional and not include_conditional:
            entries.append(
                GenerationEntry(
                    task_id=task.task_id,
                    asset_id=task.asset_id,
                    status="skipped",
                    detail="conditional fallback; not generated unless triggered",
                )
            )
            continue
        if spec.cost_usd <= 0:
            entries.append(
                GenerationEntry(
                    task_id=task.task_id,
                    asset_id=task.asset_id,
                    status="blocked",
                    detail="generation has no positive quote; price it before spending",
                )
            )
            continue
        try:
            result = agent.run(spec, task.task_id)
        except Exception as error:  # keep the report complete
            entries.append(
                GenerationEntry(
                    task_id=task.task_id,
                    asset_id=task.asset_id,
                    status="blocked",
                    detail=f"generation failed: {error}"[:500],
                )
            )
            continue
        entries.append(
            GenerationEntry(
                task_id=task.task_id,
                asset_id=task.asset_id,
                status="generated",
                detail="generated through the OpenMontage engine and provider governor",
                path=result.path,
                sha256=result.sha256,
                job_id=result.job_id,
                cost_usd=result.cost_usd,
            )
        )

    report = GenerationReport(
        run_id=run_id,
        plan_hash=level2.plan_hash,
        approved_by=packet.approved_by or "",
        generated=sum(1 for entry in entries if entry.status == "generated"),
        blocked=sum(1 for entry in entries if entry.status == "blocked"),
        skipped=sum(1 for entry in entries if entry.status == "skipped"),
        spent_usd=governor.spent(),
        entries=entries,
    )
    run.write_json(run_id, "generation-report.json", report)
    run.write_data(
        run_id,
        "provider-spend.json",
        governor.summary().model_dump(mode="json"),
    )
    run.append_event(
        run_id,
        "level2.generated",
        {
            "generated": report.generated,
            "blocked": report.blocked,
            "skipped": report.skipped,
            "spent_usd": report.spent_usd,
        },
    )
    return report
