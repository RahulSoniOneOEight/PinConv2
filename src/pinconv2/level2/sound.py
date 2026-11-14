"""Sound plan.

The mix is planned from the approved audio cues: voice, music, pour SFX and the
brand sting, with edit points, loudness targets and disclosure.
"""

from __future__ import annotations

from ..models import AudioKind, ProductionPlan
from .errors import Level2Error
from .models import Method, SoundCuePlan, SoundPlan

MUSIC_LIFT_FRAME = 275
MUSIC_RESOLVE_FRAME = 445


def build_sound_plan(plan: ProductionPlan) -> SoundPlan:
    cues: list[SoundCuePlan] = []
    for cue in plan.audio_cues:
        asset = plan.asset_map.get(cue.asset_id or "")
        if asset is None:
            raise Level2Error(f"{cue.id} references an unknown asset")
        if cue.kind is AudioKind.VO:
            method = Method.M0
            edit_points = [0, cue.end_frame]
            hold = "HI-03"
        elif cue.kind is AudioKind.MUSIC:
            method = Method.M1
            edit_points = [MUSIC_LIFT_FRAME, MUSIC_RESOLVE_FRAME]
            hold = "HI-03"
        else:
            method = Method.M0
            edit_points = [cue.start_frame, cue.end_frame]
            hold = None
        cues.append(
            SoundCuePlan(
                asset_id=asset.id,
                kind=cue.kind.value,
                method=method,
                description=cue.description,
                in_frame=cue.start_frame,
                out_frame=cue.end_frame,
                edit_points=edit_points,
                content_id_risk="medium" if cue.kind is AudioKind.MUSIC else "low",
                disclosure_required=asset.rights.disclosure_required,
                hold=hold,
            )
        )

    fallback_voice = plan.asset_map.get("AS-15")
    if fallback_voice is not None:
        cues.append(
            SoundCuePlan(
                asset_id="AS-15",
                kind="vo",
                method=Method.M7,
                description=(
                    "Disclosed synthetic narration fallback, used only if the "
                    "performer release cannot be cleared."
                ),
                in_frame=0,
                out_frame=500,
                edit_points=[0, 500],
                content_id_risk="low",
                disclosure_required=True,
                hold="HI-03",
            )
        )
    fallback_music = plan.asset_map.get("AS-14")
    if fallback_music is not None:
        cues.append(
            SoundCuePlan(
                asset_id="AS-14",
                kind="music",
                method=Method.M1,
                description="Second licensed bed with the same lift and resolve points.",
                in_frame=0,
                out_frame=500,
                edit_points=[MUSIC_LIFT_FRAME, MUSIC_RESOLVE_FRAME],
                content_id_risk="medium",
                hold="HI-03",
            )
        )

    return SoundPlan(
        cues=cues,
        master_loudness="lufs=-16,tp=-1.0",
        sound_off_message=("Captions must carry the message without sound, per MH-07."),
        notes=(
            "Dialogue stays intelligible with the bed ducked; the pour is foley from "
            "the single capture session, not a stock effect."
        ),
    )


def validate_sound_plan(plan: ProductionPlan, sound: SoundPlan) -> None:
    known = set(plan.asset_map)
    for cue in sound.cues:
        if cue.asset_id not in known:
            raise Level2Error(f"sound cue references unknown asset {cue.asset_id}")
        if cue.out_frame <= cue.in_frame:
            raise Level2Error(f"{cue.asset_id}: sound cue ends before it starts")
    music = [cue for cue in sound.cues if cue.kind == "music"]
    if not music:
        raise Level2Error("the sound plan needs a music bed")
    if not any(cue.edit_points == [MUSIC_LIFT_FRAME, MUSIC_RESOLVE_FRAME] for cue in music):
        raise Level2Error("the music bed must carry the approved lift and resolve points")
