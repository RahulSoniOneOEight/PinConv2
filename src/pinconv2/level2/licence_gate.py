"""Licence and scriptability gate.

The gate runs before cost, quality or continuity. A source that cannot be used
commercially never reaches a candidate list, and an aggregator licence is never
taken at face value.
"""

from __future__ import annotations

from pydantic import Field

from ..models import StrictModel
from .catalogue import SOURCE_MAP, SourceEntry
from .errors import LicenceBlockedError
from .models import GateVerdict, LicenceClass, MethodCandidate

BLOCKING_CLASSES = {
    LicenceClass.BLOCKED,
    LicenceClass.CC_BY_NC,
    LicenceClass.CC_BY_ND,
    LicenceClass.CC_BY_SA,
    LicenceClass.EDITORIAL,
}


class GateDecision(StrictModel):
    verdict: GateVerdict
    reasons: list[str] = Field(default_factory=list)
    attribution_required: bool = False


def classify_licence(text: str) -> LicenceClass:
    """Map a licence string to the catalogue's licence classes."""

    normalised = text.upper().replace("_", "-")
    if "PUBLIC DOMAIN" in normalised or normalised.strip() in {"PD", "CC0"}:
        return LicenceClass.PD if "PUBLIC" in normalised else LicenceClass.CC0
    if "-NC" in normalised or " NC" in normalised or normalised.startswith("NC"):
        return LicenceClass.CC_BY_NC
    if "-ND" in normalised or " ND" in normalised:
        return LicenceClass.CC_BY_ND
    if "-SA" in normalised or " SA" in normalised:
        return LicenceClass.CC_BY_SA
    if "CC0" in normalised:
        return LicenceClass.CC0
    if "CC-BY" in normalised or "CC BY" in normalised:
        return LicenceClass.CC_BY
    if "/BY/" in normalised or "ATTRIBUTION" in normalised:
        return LicenceClass.CC_BY
    if "EDITORIAL" in normalised:
        return LicenceClass.EDITORIAL
    if "BLOCK" in normalised:
        return LicenceClass.BLOCKED
    if "UNKNOWN" in normalised or "VERIFY" in normalised:
        return LicenceClass.UNKNOWN
    if "PROPRIETARY" in normalised or "FREE" in normalised:
        return LicenceClass.PROPRIETARY_FREE
    return LicenceClass.UNKNOWN


def gate_entry(entry: SourceEntry, *, commercial: bool = True) -> GateDecision:
    reasons: list[str] = []

    if commercial and not entry.commercial_ok:
        reasons.append("source is not cleared for commercial output")
    if entry.licence_class is LicenceClass.BLOCKED:
        reasons.append(entry.blocked_reason or "source is on the block list")
        return GateDecision(verdict=GateVerdict.BLOCK, reasons=reasons)
    if entry.licence_class in BLOCKING_CLASSES:
        reasons.append(f"{entry.licence_class.value} cannot be used for paid output")
        return GateDecision(verdict=GateVerdict.BLOCK, reasons=reasons)
    if entry.licence_class is LicenceClass.UNKNOWN and entry.aggregator:
        reasons.append("aggregator licence is unverified; resolve at the origin")
        return GateDecision(verdict=GateVerdict.HOLD, reasons=reasons)
    if entry.licence_class is LicenceClass.UNKNOWN:
        reasons.append("licence is unverified")
        return GateDecision(verdict=GateVerdict.HOLD, reasons=reasons)
    if entry.attribution_required:
        reasons.append("attribution is mandatory")
    if not entry.scriptable:
        reasons.append("manual import only; never fetched by script")
    return GateDecision(
        verdict=GateVerdict.PASS,
        reasons=reasons,
        attribution_required=entry.attribution_required,
    )


def gate_candidate(
    candidate: MethodCandidate,
    *,
    entry: SourceEntry | None = None,
    commercial: bool = True,
) -> MethodCandidate:
    """Apply the licence, scriptability and origin checks to a candidate."""

    source = entry or SOURCE_MAP.get(candidate.provider)
    reasons: list[str] = []
    verdict = GateVerdict.PASS

    if source is None:
        return candidate.model_copy(
            update={
                "gate_verdict": GateVerdict.BLOCK,
                "gate_reasons": [f"unknown source: {candidate.provider}"],
            }
        )

    if candidate.licence_class is LicenceClass.BLOCKED:
        reasons.append("candidate licence is blocked")
        verdict = GateVerdict.BLOCK
    elif candidate.licence_class in BLOCKING_CLASSES:
        reasons.append(f"{candidate.licence_class.value} cannot be used for paid output")
        verdict = GateVerdict.BLOCK
    elif source.aggregator and not candidate.origin_verified:
        reasons.append("aggregator candidate needs origin verification")
        verdict = GateVerdict.HOLD
    elif candidate.licence_class is LicenceClass.UNKNOWN:
        reasons.append("candidate licence is unverified")
        verdict = GateVerdict.HOLD

    commercial_block = commercial and not source.commercial_ok
    verified_aggregator = (
        source.aggregator
        and candidate.origin_verified
        and candidate.licence_class not in BLOCKING_CLASSES
    )
    if commercial_block and not verified_aggregator and verdict is GateVerdict.PASS:
        reasons.append("source is not cleared for commercial output")
        verdict = GateVerdict.BLOCK

    if (
        source.attribution_required
        and candidate.licence_class is LicenceClass.CC_BY
        and not candidate.attribution
    ):
        reasons.append("CC BY needs an attribution line")
        if verdict is GateVerdict.PASS:
            verdict = GateVerdict.HOLD

    if not source.scriptable:
        reasons.append("manual import only; the candidate must arrive through import")

    return candidate.model_copy(update={"gate_verdict": verdict, "gate_reasons": reasons})


def ensure_usable(candidate: MethodCandidate) -> None:
    if candidate.gate_verdict is not GateVerdict.PASS:
        joined = "; ".join(candidate.gate_reasons) or "blocked by the licence gate"
        raise LicenceBlockedError(
            f"{candidate.candidate_id}: {candidate.gate_verdict.value}: {joined}"
        )


def attribution_line(candidate: MethodCandidate) -> str:
    """Return the attribution line a CC BY candidate needs on delivery."""

    if candidate.licence_class is not LicenceClass.CC_BY:
        return ""
    attribution = candidate.attribution or "attribution missing"
    return f"{attribution} — {candidate.url} ({candidate.licence_class.value})"
