"""Capture session planning.

One session carries every proof asset plus foley and marginal extras, so the
demonstration costs once rather than once per asset.
"""

from __future__ import annotations

from ..models import AssetRoute, Level2Handoff, ProductionPlan
from .errors import Level2Error
from .models import CaptureMember, CaptureSessionPlan

SESSION_ID = "CAP-01"
CAPTURE_ESTIMATE = "ES-06"


def build_capture_plan(
    plan: ProductionPlan, handoff: Level2Handoff, *, lean: bool = False
) -> CaptureSessionPlan:
    capture_assets = [asset for asset in plan.assets if asset.route is AssetRoute.TO_CAPTURE]
    if not capture_assets:
        raise Level2Error("no capture assets in the approved plan")

    roles = {
        "AS-05": ("pack tear, anchor and pour demonstration", 25),
        "AS-06": ("hot water pour and bloom, 50 fps for the ramp", 50),
        "AS-08": ("finished cup with live steam", 25),
        "AS-13": ("conditional captured pack fallback, four angles", 25),
    }
    members = [
        CaptureMember(
            asset_id=asset.id,
            role=roles.get(asset.id, (asset.description, 25))[0],
            frame_rate=roles.get(asset.id, ("", 25))[1],
            notes="Conditional: shoot only if the schedule allows."
            if asset.id == "AS-13"
            else None,
        )
        for asset in capture_assets
    ]

    estimate = plan.estimate_map.get(CAPTURE_ESTIMATE)
    if estimate is None:
        raise Level2Error("the capture estimate ES-06 is missing")

    return CaptureSessionPlan(
        session_id=SESSION_ID,
        members=members,
        foley=["pack tear", "filter seat and anchor", "water pour", "cup set-down"],
        marginal_items=[
            "second angle on the steep pour",
            "steam plate reference for FX-01 and FX-05",
            "room tone for the mix",
        ],
        studio=(
            "Self-operated location with phone/DSLR and practical light (lean mode)"
            if lean
            else "Studio TBC by the producer"
        ),
        hand_model_release="Pending signed release",
        release_hold="HI-04",
        cost_usd=0.0 if lean else estimate.amount_usd,
        in_kind_usd=estimate.amount_usd if lean else 0.0,
        estimate_id=estimate.id,
        shot_list=["SH-02", "SH-03", "SH-05"],
        colour_target="Warm 3200K practical light, neutral grade, no baked look",
        audio_rig="Close-mic foley plus 30 seconds of room tone",
        acceptance=(
            "Tear, anchor and pour are visible in one continuous take; the pack label "
            "stays legible; the finished cup shows live steam."
        ),
    )


def validate_capture_plan(plan: ProductionPlan, session: CaptureSessionPlan) -> None:
    required = {asset.id for asset in plan.assets if asset.route is AssetRoute.TO_CAPTURE}
    covered = {member.asset_id for member in session.members}
    missing = required - covered
    if missing:
        raise Level2Error(f"capture session misses {sorted(missing)}")
    if len(session.members) < 3:
        raise Level2Error("the capture session needs the demonstration, pour and cup")
    if session.cost_usd <= 0 and session.in_kind_usd <= 0:
        raise Level2Error("the capture session must carry a cost or an in-kind value")
