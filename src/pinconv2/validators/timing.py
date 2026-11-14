"""Timing and coverage checks."""

from __future__ import annotations

from ..models import LayerRole, Severity
from .common import ValidationContext


def validate_timing(context: ValidationContext) -> None:
    plan = context.plan
    deliverable = plan.deliverable

    with context.group(
        "timing.deliverable",
        deliverable.id,
        f"{deliverable.frame_count} frames at {deliverable.fps} fps "
        f"= {deliverable.frame_count / deliverable.fps:.3f}s",
    ):
        expected = round(deliverable.duration_seconds * deliverable.fps)
        if expected != deliverable.frame_count:
            context.fail(
                "timing.deliverable",
                deliverable.id,
                Severity.BLOCKER,
                f"frame count {deliverable.frame_count} does not match "
                f"{deliverable.duration_seconds}s x {deliverable.fps}fps = {expected}",
                "Fix the deliverable profile before planning shots.",
            )

    with context.group(
        "timing.shots",
        "timeline",
        f"{len(plan.shots)} half-open shots cover frames 0-{deliverable.frame_count}",
    ):
        ordered = sorted(plan.shots, key=lambda shot: shot.start_frame)
        cursor = 0
        for shot in ordered:
            if shot.start_frame != cursor:
                context.fail(
                    "timing.shots",
                    shot.id,
                    Severity.BLOCKER,
                    f"shot starts at {shot.start_frame}, expected {cursor}",
                    "Make shot ranges contiguous and half-open.",
                )
            if shot.end_frame <= shot.start_frame:
                context.fail(
                    "timing.shots",
                    shot.id,
                    Severity.BLOCKER,
                    "shot has a non-positive duration",
                    "Set end_frame after start_frame.",
                )
            cursor = shot.end_frame
        if cursor != deliverable.frame_count:
            context.fail(
                "timing.shots",
                "timeline",
                Severity.BLOCKER,
                f"shots end at frame {cursor}, deliverable has {deliverable.frame_count}",
                "Extend or trim the final shot to the exact deliverable length.",
            )

    with context.group(
        "timing.beats",
        "timeline",
        f"{len(plan.beats)} beats cover the full timeline",
    ):
        ordered_beats = sorted(plan.beats, key=lambda beat: beat.start_frame)
        cursor = 0
        for beat in ordered_beats:
            if beat.start_frame != cursor:
                context.fail(
                    "timing.beats",
                    beat.id,
                    Severity.HIGH,
                    f"beat starts at {beat.start_frame}, expected {cursor}",
                    "Make beats contiguous so every frame carries a purpose.",
                )
            cursor = beat.end_frame
        if cursor != deliverable.frame_count:
            context.fail(
                "timing.beats",
                "timeline",
                Severity.HIGH,
                f"beats end at frame {cursor}, deliverable has {deliverable.frame_count}",
                "Cover the full timeline with beats.",
            )

    shot_map = plan.shot_map
    with context.group("timing.layers", "layers", "every layer sits inside its shot"):
        for layer in plan.layers:
            shot_record = shot_map.get(layer.shot_id)
            if shot_record is None:
                context.fail(
                    "timing.layers",
                    layer.id,
                    Severity.BLOCKER,
                    f"layer references unknown shot {layer.shot_id}",
                    "Bind the layer to an existing shot.",
                )
                continue
            if layer.end_frame > shot_record.duration_frames:
                context.fail(
                    "timing.layers",
                    layer.id,
                    Severity.HIGH,
                    f"layer ends at shot frame {layer.end_frame}, shot is "
                    f"{shot_record.duration_frames} frames",
                    "Keep shot-relative layer timing inside the shot.",
                )

    with context.group(
        "timing.audio", "audio", f"{len(plan.audio_cues)} audio cues fit the timeline"
    ):
        for cue in plan.audio_cues:
            if cue.end_frame > deliverable.frame_count:
                context.fail(
                    "timing.audio",
                    cue.id,
                    Severity.HIGH,
                    f"cue ends at frame {cue.end_frame} outside the deliverable",
                    "Trim the cue to the timeline.",
                )

    caption_roles = {LayerRole.CAPTION, LayerRole.CTA, LayerRole.OFFER, LayerRole.DISCLAIMER}
    copy_map = plan.copy_map
    with context.group("timing.captions", "captions", "caption holds and reading speed fit"):
        for layer in plan.layers:
            if layer.role not in caption_roles or layer.binding_ref is None:
                continue
            copy_block = copy_map.get(layer.binding_ref)
            if copy_block is None:
                continue
            seconds = layer.duration_frames / deliverable.fps
            cps = len(copy_block.text) / seconds if seconds > 0 else 999
            if cps > deliverable.caption_rules.max_cps:
                context.fail(
                    "timing.captions",
                    layer.id,
                    Severity.HIGH,
                    f"caption reads at {cps:.1f} characters/second, limit is "
                    f"{deliverable.caption_rules.max_cps}",
                    "Shorten the copy or hold it longer.",
                )
            if layer.duration_frames < deliverable.caption_rules.min_hold_frames:
                context.fail(
                    "timing.captions",
                    layer.id,
                    Severity.MEDIUM,
                    f"caption holds for {layer.duration_frames} frames, minimum is "
                    f"{deliverable.caption_rules.min_hold_frames}",
                    "Extend the hold or remove the caption.",
                )

    with context.group(
        "timing.transitions", "transitions", "transitions sit on shot boundaries"
    ):
        for transition in plan.transitions:
            source = shot_map.get(transition.from_shot_id)
            target = shot_map.get(transition.to_shot_id)
            if source is None or target is None:
                context.fail(
                    "timing.transitions",
                    transition.id,
                    Severity.HIGH,
                    "transition references an unknown shot",
                    "Point the transition at existing shots.",
                )
                continue
            if source.end_frame != target.start_frame:
                context.fail(
                    "timing.transitions",
                    transition.id,
                    Severity.HIGH,
                    "transition joins shots that are not adjacent",
                    "Only transition between adjacent half-open ranges.",
                )
            if transition.at_frame != source.end_frame:
                context.fail(
                    "timing.transitions",
                    transition.id,
                    Severity.MEDIUM,
                    f"transition at frame {transition.at_frame}, boundary is "
                    f"{source.end_frame}",
                    "Place the transition on the shared boundary.",
                )
