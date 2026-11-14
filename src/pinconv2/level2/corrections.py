"""Typed corrections and the re-plan boundary.

A correction never edits an approved record. It is validated, logged against the
run it came from, and routed either to a new Level 2 run or back to Level 1 when
it would change creative intent.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import Field

from ..models import ProductionPlan, StrictModel
from .errors import Level2Error
from .models import Correction, CorrectionDecision, CorrectionStatus

_CREATIVE_KINDS = {"shot", "variant"}
_KIND_PREFIX = {
    "asset": "AS-",
    "layer": "LY-",
    "shot": "SH-",
    "variant": "VO-",
    "budget": "ES-",
}


class CorrectionSummary(StrictModel):
    total: int = Field(ge=0)
    open_items: int = Field(ge=0)
    affected_items: list[str] = Field(default_factory=list)
    creative_escalations: list[str] = Field(default_factory=list)
    accepted: list[str] = Field(default_factory=list)
    rejected: list[str] = Field(default_factory=list)


def parse_jsonl(text: str) -> list[Correction]:
    corrections: list[Correction] = []
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            corrections.append(Correction.model_validate_json(stripped))
        except ValueError as error:
            raise Level2Error(f"correction line {number} is invalid: {error}") from error
    if not corrections:
        raise Level2Error("the correction file is empty")
    return corrections


def load_corrections(path: Path) -> list[Correction]:
    if not path.is_file():
        raise Level2Error(f"no correction file at {path}")
    return parse_jsonl(path.read_text(encoding="utf-8"))


def validate_corrections(corrections: list[Correction], plan: ProductionPlan) -> CorrectionSummary:
    ids = [correction.id for correction in corrections]
    if len(ids) != len(set(ids)):
        raise Level2Error("correction ids must be unique")
    known = {
        "asset": set(plan.asset_map),
        "layer": set(plan.layer_map),
        "shot": set(plan.shot_map),
        "variant": {item.id for item in plan.variant_overrides},
        "budget": {estimate.id for estimate in plan.estimates},
    }
    affected: set[str] = set()
    creative: list[str] = []
    accepted: list[str] = []
    rejected: list[str] = []
    for correction in corrections:
        prefix = _KIND_PREFIX[correction.item_kind]
        if not correction.item_id.startswith(prefix):
            raise Level2Error(
                f"{correction.id}: {correction.item_id} is not a {correction.item_kind} id"
            )
        if correction.item_id not in known[correction.item_kind]:
            raise Level2Error(f"{correction.id}: unknown item {correction.item_id}")
        if correction.decision is CorrectionDecision.REJECT:
            rejected.append(correction.item_id)
            continue
        if (
            correction.decision is CorrectionDecision.CHANGE
            and correction.item_kind in _CREATIVE_KINDS
        ):
            creative.append(correction.item_id)
            continue
        accepted.append(correction.item_id)
        affected.update(correction.affects or [correction.item_id])

    return CorrectionSummary(
        total=len(corrections),
        open_items=sum(1 for item in corrections if item.status is CorrectionStatus.OPEN),
        affected_items=sorted(affected),
        creative_escalations=sorted(set(creative)),
        accepted=sorted(set(accepted)),
        rejected=sorted(set(rejected)),
    )


def next_run_id(run_id: str) -> str:
    if not run_id.startswith("rev-") or not run_id[4:].isdigit():
        raise Level2Error(f"cannot derive the next run from {run_id!r}")
    return f"rev-{int(run_id[4:]) + 1:03d}"


def write_jsonl(path: Path, corrections: list[Correction]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(
        json.dumps(item.model_dump(mode="json"), sort_keys=True) for item in corrections
    )
    path.write_text(payload + "\n", encoding="utf-8")
    return path
