from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from pinconv2.preview import render_contact_sheet, render_shot_svg, write_previews


def test_shot_preview_is_valid_svg(plan_v2) -> None:
    svg = render_shot_svg(plan_v2, plan_v2.shots[0])
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert "ETHIOPIA" in svg
    assert "safe area" in svg
    assert "LAYOUT MOCKUP" in svg


def test_contact_sheet_contains_every_shot(plan_v2) -> None:
    svg = render_contact_sheet(plan_v2)
    ET.fromstring(svg)
    for shot in plan_v2.shots:
        assert shot.id in svg


def test_write_previews(tmp_path: Path, plan_v2) -> None:
    paths = write_previews(plan_v2, tmp_path)
    assert len(paths) == 5
    assert (tmp_path / "contact-sheet.svg").is_file()
    for shot in plan_v2.shots:
        assert (tmp_path / f"{shot.id}.svg").is_file()
