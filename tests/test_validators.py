from __future__ import annotations

from pinconv2.models import (
    BindingKind,
    Exactness,
    Layer,
    LayerRole,
    ProductionPlan,
    RightsRecord,
    RightsStatus,
    ValidationStatus,
)
from pinconv2.validators import validate_plan


def _rules(plan: ProductionPlan, brief) -> set[str]:
    report = validate_plan(plan, brief)
    return {finding.rule for finding in report.findings if finding.status is ValidationStatus.FAIL}


def test_v1_fails_exact_safe_area_and_budget(plan_v1, brief) -> None:
    rules = _rules(plan_v1, brief)
    assert "exact.critical" in rules
    assert "layer.safe_area" in rules
    assert "budget.cap" in rules
    assert "budget.worst_case" in rules


def test_v2_passes(plan_v2, brief) -> None:
    report = validate_plan(plan_v2, brief)
    assert report.passed
    assert not report.failures
    assert all(
        status.value in {"pass", "pending", "not_applicable"}
        for status in report.check_status.values()
    )


def test_v2_does_not_carry_the_offer_or_double_splash(plan_v2) -> None:
    assert "CP-04" not in plan_v2.copy_map
    assert "AS-12" not in plan_v2.asset_map
    assert "AS-04" not in plan_v2.asset_map
    assert plan_v2.budget.total_usd == 55.2
    assert plan_v2.budget.worst_case_usd == 57.2


def test_gap_between_shots_is_detected(plan_v2, brief) -> None:
    shots = [
        shot.model_copy(update={"end_frame": 49}) if shot.id == "SH-01" else shot
        for shot in plan_v2.shots
    ]
    broken = plan_v2.model_copy(update={"shots": shots})
    assert "timing.shots" in _rules(broken, brief)


def test_unverified_claim_is_detected(plan_v2, brief) -> None:
    copies = [
        block.model_copy(update={"claim_refs": ["CL-01"]}) if block.id == "CP-02" else block
        for block in plan_v2.copy_blocks
    ]
    broken = plan_v2.model_copy(update={"copy_blocks": copies})
    assert "exact.claims" in _rules(broken, brief)


def test_reference_only_asset_is_blocked(plan_v2, brief) -> None:
    assets = [
        asset.model_copy(
            update={
                "rights": RightsRecord(
                    status=RightsStatus.REFERENCE_ONLY,
                    commercial_use=False,
                )
            }
        )
        if asset.id == "AS-01"
        else asset
        for asset in plan_v2.assets
    ]
    broken = plan_v2.model_copy(update={"assets": assets})
    rules = _rules(broken, brief)
    assert "rights.reference" in rules or "layer.binding_exactness" in rules


def test_opaque_overlay_on_pack_label_is_blocked(plan_v2, brief) -> None:
    pack = plan_v2.layer_map["LY-021"]
    overlay = Layer(
        id="LY-099",
        shot_id="SH-02",
        start_frame=0,
        end_frame=75,
        role=LayerRole.EFFECT,
        z_order=90,
        rect=pack.protected_regions[0],
        fill="#000000",
        binding_kind=BindingKind.NONE,
        exactness=Exactness.ILLUSTRATIVE,
        non_occluding=False,
    )
    shots = [
        shot.model_copy(update={"layer_ids": [*shot.layer_ids, "LY-099"]})
        if shot.id == "SH-02"
        else shot
        for shot in plan_v2.shots
    ]
    broken = plan_v2.model_copy(
        update={"layers": [*plan_v2.layers, overlay], "shots": shots}
    )
    assert "layer.occlusion" in _rules(broken, brief)


def test_over_cap_budget_is_detected(plan_v2, brief) -> None:
    budget = plan_v2.budget.model_copy(update={"cap_usd": 10.0})
    broken = plan_v2.model_copy(update={"budget": budget})
    assert "budget.cap" in _rules(broken, brief)


def test_validation_is_deterministic(plan_v2, brief) -> None:
    first = validate_plan(plan_v2, brief)
    second = validate_plan(plan_v2, brief)
    assert first.plan_hash == second.plan_hash
    assert [item.rule for item in first.findings] == [item.rule for item in second.findings]


def test_blocked_essential_audio_is_detected(plan_v2, brief) -> None:
    assets = [
        asset.model_copy(
            update={
                "rights": RightsRecord(
                    status=RightsStatus.BLOCKED,
                    commercial_use=False,
                )
            }
        )
        if asset.id == "AS-07"
        else asset
        for asset in plan_v2.assets
    ]
    broken = plan_v2.model_copy(update={"assets": assets})
    rules = _rules(broken, brief)
    assert "rights.assets" in rules


def test_unknown_asset_dependency_is_detected(plan_v2, brief) -> None:
    assets = [
        asset.model_copy(update={"dependencies": ["AS-MISSING"]})
        if asset.id == "AS-03"
        else asset
        for asset in plan_v2.assets
    ]
    broken = plan_v2.model_copy(update={"assets": assets})
    assert "trace.dependencies" in _rules(broken, brief)


def test_unknown_alternate_dependency_is_detected(plan_v2, brief) -> None:
    alternates = [
        alternate.model_copy(update={"revised_dependencies": ["AS-MISSING"]})
        if alternate.id == "ALT-03"
        else alternate
        for alternate in plan_v2.alternates
    ]
    broken = plan_v2.model_copy(update={"alternates": alternates})
    assert "trace.dependencies" in _rules(broken, brief)


def test_split_estimate_lists_are_detected(plan_v2, brief) -> None:
    budget = plan_v2.budget.model_copy(
        update={"estimates": plan_v2.budget.estimates[:-1]}
    )
    broken = plan_v2.model_copy(update={"budget": budget})
    assert "budget.sync" in _rules(broken, brief)


def test_invalid_variant_override_is_detected(plan_v2, brief) -> None:
    from pinconv2.models import VariantOverride

    variant = VariantOverride(
        id="VO-01",
        deliverable_id="DP-99",
        reference_ids=["SH-99"],
        changes=["crop to 1:1"],
        check_ids=["AC-99"],
        approval_scope=["SH-99"],
    )
    broken = plan_v2.model_copy(update={"variant_overrides": [variant]})
    assert "trace.variants" in _rules(broken, brief)


def test_shot_asset_declaration_must_match_layers(plan_v2, brief) -> None:
    shots = [
        shot.model_copy(update={"asset_ids": ["AS-05"]}) if shot.id == "SH-02" else shot
        for shot in plan_v2.shots
    ]
    broken = plan_v2.model_copy(update={"shots": shots})
    assert "trace.shots" in _rules(broken, brief)


def test_checks_evaluate_their_own_rules(plan_v2, brief) -> None:
    report = validate_plan(plan_v2, brief)
    assert report.check_status["AC-01"].value == "pass"
    assert report.check_status["AC-04"].value == "pass"
    assert report.check_status["AC-08"].value == "pass"
    assert report.check_status["AC-13"].value == "pass"

    copies = [
        block.model_copy(update={"claim_refs": ["CL-01"]}) if block.id == "CP-02" else block
        for block in plan_v2.copy_blocks
    ]
    broken = validate_plan(
        plan_v2.model_copy(update={"copy_blocks": copies}), brief
    )
    assert broken.check_status["AC-08"].value == "fail"
    assert broken.check_status["AC-01"].value == "pass"
