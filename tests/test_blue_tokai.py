from __future__ import annotations

from pathlib import Path

from pinconv2.fixtures.blue_tokai_concept import build_blue_tokai_concept
from pinconv2.fixtures.blue_tokai_plan import (
    build_blue_tokai_plan,
    revision_two_applied,
)
from pinconv2.fixtures.blue_tokai_research import (
    PROJECT_ID,
    build_blue_tokai_brief,
    build_blue_tokai_research,
)
from pinconv2.models import Exactness, ProjectState
from pinconv2.quality import plan_detail_issues, research_quality_issues
from pinconv2.service import run_all
from pinconv2.store import ProjectStore
from pinconv2.validators import validate_plan


def test_blue_tokai_research_is_decision_ready() -> None:
    assert research_quality_issues(build_blue_tokai_research()) == []


def test_blue_tokai_plan_is_full_detail_and_valid() -> None:
    plan = build_blue_tokai_plan(
        revision=2,
        applied=revision_two_applied(),
    )
    assert plan.detail_level == "full"
    assert plan_detail_issues(plan) == []
    assert validate_plan(plan, build_blue_tokai_brief()).passed
    assert all(
        layer.exactness is Exactness.PROPOSED_COPY
        for layer in plan.layers
        if layer.binding_kind.value == "copy"
    )
    assert {asset.id for asset in plan.assets} >= {"AS-02", "AS-03", "AS-04", "AS-17"}
    assert not [
        asset
        for asset in plan.assets
        if asset.fallback_required and asset.fallback_asset_id is None
    ]


def test_blue_tokai_run_reaches_gate1_ready(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    result = run_all(store, PROJECT_ID)
    assert result["state"] == ProjectState.GATE1_READY.value
    assert result["plan_revision"] == 2
    assert result["validation"]["passed"] is True
    assert result["gate1"]["blockers"] == []
    assert result["gate1"]["ready_shots"] == [
        "SH-01",
        "SH-02",
        "SH-03",
        "SH-04",
        "SH-05",
        "SH-06",
    ]
    assert result["gate1"]["approval"] is None
    assert build_blue_tokai_concept().canonical_script
