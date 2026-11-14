"""Impact scoring.

Impact decides how much sourcing effort a layer earns. It is a pure function of
the approved plan and brief:

* ``MH`` only counts a direct reference (layer, bound asset or bound copy block),
  never a shot-level mention. A shot-level match makes every layer high.
* ``t3`` uses the global timeline (shot start + layer start), not shot-local
  frames. Shot-local frames make every layer look like it opens the film.
"""

from __future__ import annotations

from ..models import BriefRevision, Layer, ProductionPlan, Shot
from .models import Impact, LayerMethodDecision

FIRST_THREE_SECONDS = 75
LONG_LAYER_FRAMES = 50
AREA_SHARE = 0.25

_IMPACT_ORDER = {Impact.LOW: 0, Impact.MEDIUM: 1, Impact.HIGH: 2}


def direct_must_have_targets(brief: BriefRevision) -> set[str]:
    targets: set[str] = set()
    for must_have in brief.must_have:
        for target in must_have.satisfied_by:
            if not target.startswith("SH-"):
                targets.add(target)
    return targets


def score_layer(
    layer: Layer,
    shot: Shot,
    plan: ProductionPlan,
    brief: BriefRevision,
) -> tuple[int, Impact, list[str]]:
    targets = direct_must_have_targets(brief)
    bound = layer.binding_ref if layer.binding_kind.value in {"asset", "copy"} else None
    signals: list[str] = []
    score = 0

    if layer.id in targets or (bound is not None and bound in targets):
        score += 3
        signals.append("MH")
    if shot.start_frame + layer.start_frame < FIRST_THREE_SECONDS:
        score += 2
        signals.append("t3")
    if layer.exactness.value in {"exact", "proposed_copy"}:
        score += 2
        signals.append("data")
    frame_area = plan.deliverable.width * plan.deliverable.height
    if layer.rect.w * layer.rect.h >= AREA_SHARE * frame_area:
        score += 1
        signals.append("area")
    if layer.duration_frames > LONG_LAYER_FRAMES:
        score += 1
        signals.append("dur")

    if score >= 5:
        impact = Impact.HIGH
    elif score >= 3:
        impact = Impact.MEDIUM
    else:
        impact = Impact.LOW
    return score, impact, signals


def asset_impact(asset_id: str, decisions: list[LayerMethodDecision]) -> Impact:
    """An asset inherits the highest impact of the layers that bind to it."""

    impacts = [decision.impact for decision in decisions if decision.asset_id == asset_id]
    if not impacts:
        return Impact.LOW
    return max(impacts, key=lambda impact: _IMPACT_ORDER[impact])
