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
from pinconv2.models import Exactness, ProjectState, Rect
from pinconv2.quality import plan_detail_issues, research_quality_issues
from pinconv2.service import run_all
from pinconv2.store import ProjectStore
from pinconv2.validators import validate_plan


def test_blue_tokai_research_is_decision_ready() -> None:
    assert research_quality_issues(build_blue_tokai_research()) == []


def test_blue_tokai_plan_is_full_detail_and_valid() -> None:
    research = build_blue_tokai_research()
    plan = build_blue_tokai_plan(
        revision=2,
        applied=revision_two_applied(),
    )
    assert plan.detail_level == "full"
    assert plan_detail_issues(plan, research) == []
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
    assert len(plan.effects) == 6
    selected = {effect.id for effect in research.effect_assessments if effect.selected}
    assert {effect.research_ref for effect in plan.effects} <= selected
    assert {effect.id for effect in plan.effects} == {
        effect_id for shot in plan.shots for effect_id in shot.effect_ids
    }
    assert {effect_id for layer in plan.layers for effect_id in layer.effect_ids} <= {
        effect.id for effect in plan.effects
    }


def test_blue_tokai_effect_selection_is_bound_to_research() -> None:
    research = build_blue_tokai_research()
    assert any(effect.selected for effect in research.effect_assessments)
    assert any(not effect.selected for effect in research.effect_assessments)
    plan = build_blue_tokai_plan(
        revision=2,
        applied=revision_two_applied(),
    )
    selected = {effect.id for effect in research.effect_assessments if effect.selected}
    assert {effect.research_ref for effect in plan.effects} <= selected


def test_effect_target_and_binding_are_validated() -> None:
    plan = build_blue_tokai_plan(
        revision=2,
        applied=revision_two_applied(),
    )
    broken_effects = [
        effect.model_copy(update={"target_shot": "SH-99"}) if effect.id == "FX-01" else effect
        for effect in plan.effects
    ]
    broken = plan.model_copy(update={"effects": broken_effects})
    rules = {finding.rule for finding in validate_plan(broken, build_blue_tokai_brief()).findings}
    assert "effect.references" in rules


def test_effect_timing_binding_and_protection_are_validated() -> None:
    plan = build_blue_tokai_plan(
        revision=2,
        applied=revision_two_applied(),
    )
    brief = build_blue_tokai_brief()

    timing_effects = [
        effect.model_copy(update={"duration_frames": 200}) if effect.id == "FX-06" else effect
        for effect in plan.effects
    ]
    timing = plan.model_copy(update={"effects": timing_effects})
    timing_rules = {finding.rule for finding in validate_plan(timing, brief).findings}
    assert "effect.timing" in timing_rules

    shot = plan.shot_map["SH-01"].model_copy(update={"effect_ids": []})
    shots = [shot if item.id == "SH-01" else item for item in plan.shots]
    unbound = plan.model_copy(update={"shots": shots})
    binding_rules = {finding.rule for finding in validate_plan(unbound, brief).findings}
    assert "effect.bindings" in binding_rules

    protection_effects = [
        effect.model_copy(update={"mask_region": Rect(x=1100, y=300, w=700, h=500)})
        if effect.id == "FX-01"
        else effect
        for effect in plan.effects
    ]
    protected = plan.model_copy(update={"effects": protection_effects})
    protection_rules = {finding.rule for finding in validate_plan(protected, brief).findings}
    assert "effect.protection" in protection_rules


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
