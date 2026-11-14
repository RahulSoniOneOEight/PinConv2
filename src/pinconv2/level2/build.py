"""Post-approval build orchestration.

This is the only Level 2 entry point that can run a paid or local process. It
requires an approved Gate 2A, then processes whatever source files have been
imported into ``projects/<id>/inputs``. Missing sources stay blocked; nothing is
downloaded or generated implicitly.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from ..models import StrictModel, utc_now
from ..store import ProjectStore
from .engines.base import SpendLedger
from .engines.local import LocalEngine
from .errors import GateOrderError
from .models import GatePacket, PacketStatus, TaskStatus
from .store import Level2RunStore

_SOURCE_SUFFIXES = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".wav",
    ".mp3",
    ".mov",
    ".mp4",
    ".mxf",
)


class BuildEntry(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    status: str = Field(pattern=r"^(processed|blocked|conditional)$")
    detail: str = Field(min_length=1, max_length=500)
    output_path: str | None = None
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")


class BuildReport(StrictModel):
    run_id: str
    plan_hash: str
    approved_by: str
    processed: int = Field(ge=0)
    blocked: int = Field(ge=0)
    conditional: int = Field(ge=0)
    spent_usd: float = Field(ge=0)
    entries: list[BuildEntry] = Field(min_length=1)
    created_at: str = Field(default_factory=utc_now)


def _find_input(inputs_dir: Path, asset_id: str) -> Path | None:
    for suffix in _SOURCE_SUFFIXES:
        candidate = inputs_dir / f"{asset_id}{suffix}"
        if candidate.is_file():
            return candidate
    nested = inputs_dir / asset_id
    if nested.is_dir():
        for suffix in _SOURCE_SUFFIXES:
            matches = sorted(nested.glob(f"*{suffix}"))
            if matches:
                return matches[0]
    return None


def run_build(
    store: ProjectStore,
    project_id: str,
    revision: int,
    run_id: str,
) -> BuildReport:
    run = Level2RunStore(store.project_dir(project_id))
    level2 = run.read_level2(run_id)
    packet_path = run.run_dir(run_id) / "gate2" / "packet-2a.json"
    if not packet_path.is_file():
        raise GateOrderError("no Gate 2A packet; run level2 plan first")
    packet = GatePacket.model_validate_json(packet_path.read_text(encoding="utf-8"))
    if packet.status is not PacketStatus.APPROVED or not packet.approved_by:
        raise GateOrderError("Gate 2A is not approved; no build may start")

    ledger = SpendLedger(run.run_dir(run_id) / "spend-ledger.jsonl")
    engine = LocalEngine()
    inputs_dir = store.project_dir(project_id) / "inputs"
    output_dir = run.run_dir(run_id) / "processed"
    entries: list[BuildEntry] = []

    for task in level2.tasks:
        if task.conditional:
            entries.append(
                BuildEntry(
                    asset_id=task.asset_id,
                    status="conditional",
                    detail="conditional fallback; not acquired unless triggered",
                )
            )
            continue
        source = _find_input(inputs_dir, task.asset_id)
        if source is None:
            entries.append(
                BuildEntry(
                    asset_id=task.asset_id,
                    status="blocked",
                    detail="no imported source under project inputs",
                )
            )
            continue
        destination = output_dir / f"{task.asset_id}{source.suffix.lower()}"
        try:
            processed = engine.process(task.processing, source, destination)
        except Exception as error:  # the report must survive one bad asset
            entries.append(
                BuildEntry(
                    asset_id=task.asset_id,
                    status="blocked",
                    detail=f"processing failed: {error}",
                )
            )
            continue
        entries.append(
            BuildEntry(
                asset_id=task.asset_id,
                status="processed",
                detail="processed with the approved recipe",
                output_path=str(destination.relative_to(run.run_dir(run_id))),
                sha256=processed.sha256,
            )
        )

    report = BuildReport(
        run_id=run_id,
        plan_hash=level2.plan_hash,
        approved_by=packet.approved_by,
        processed=sum(1 for entry in entries if entry.status == "processed"),
        blocked=sum(1 for entry in entries if entry.status == "blocked"),
        conditional=sum(1 for entry in entries if entry.status == "conditional"),
        spent_usd=ledger.spent_usd(),
        entries=entries,
    )
    run.write_data(
        run_id,
        "spend-ledger.json",
        {
            "run_id": run_id,
            "currency": "USD",
            "cap_usd": level2.budget.summary.cap_usd,
            **ledger.summary(),
            "note": "Refreshed after the build pass from the canonical JSONL ledger.",
        },
    )
    run.write_json(run_id, "build-report.json", report)
    run.append_event(
        run_id,
        "level2.build",
        {
            "processed": report.processed,
            "blocked": report.blocked,
            "spent_usd": report.spent_usd,
        },
    )
    return report


def processed_status(report: BuildReport) -> TaskStatus:
    if report.processed == 0:
        return TaskStatus.BLOCKED
    if report.blocked:
        return TaskStatus.PROCESSED
    return TaskStatus.ACCEPTED
