from __future__ import annotations

import pytest
from pydantic import ValidationError

from pinconv2.models import (
    CaptionRules,
    CheckLevel,
    CheckMethod,
    DataStatus,
    DeliverableProfile,
    ExactData,
    ExactField,
    Layer,
    LayerRole,
    Rect,
    SafeArea,
    TextStyle,
)


def test_frame_count_must_match_duration() -> None:
    with pytest.raises(ValidationError):
        DeliverableProfile(
            id="DP-01",
            platform="test",
            placement="test",
            width=1080,
            height=1920,
            fps=25,
            frame_count=240,
            duration_seconds=10,
            aspect_ratio="9:16",
            safe_area=SafeArea(top=0, bottom=0, left=0, right=0),
            caption_rules=CaptionRules(
                max_lines=2, max_chars_per_line=30, max_cps=17, min_hold_frames=20
            ),
            variant_id="test",
            sound_off_legible=True,
        )


def test_text_layer_needs_copy_and_style() -> None:
    with pytest.raises(ValidationError):
        Layer(
            id="LY-001",
            shot_id="SH-01",
            start_frame=0,
            end_frame=25,
            role=LayerRole.CAPTION,
            z_order=1,
            rect=Rect(x=0, y=0, w=100, h=100),
            binding_kind="copy",
        )


def test_text_layer_with_copy_and_style_is_valid() -> None:
    layer = Layer(
        id="LY-001",
        shot_id="SH-01",
        start_frame=0,
        end_frame=25,
        role=LayerRole.CAPTION,
        z_order=1,
        rect=Rect(x=0, y=0, w=100, h=100),
        text_style=TextStyle(
            font_family="Inter", size_px=32, weight=700, color="#FFFFFF"
        ),
        binding_kind="copy",
        binding_ref="CP-01",
    )
    assert layer.duration_frames == 25


def test_exact_data_approval_needs_an_approver() -> None:
    with pytest.raises(ValidationError):
        ExactData(
            id="ED-01",
            field=ExactField.PRICE,
            value="Rs 499",
            status=DataStatus.APPROVED,
        )


def test_observed_exact_data_needs_a_source() -> None:
    with pytest.raises(ValidationError):
        ExactData(
            id="ED-01",
            field=ExactField.PRICE,
            value="Rs 499",
            status=DataStatus.OBSERVED,
        )


def test_check_enums_exist_for_handoff() -> None:
    assert CheckMethod.RENDER_PIXEL.value == "render_pixel"
    assert CheckLevel.L2.value == "level_2"
