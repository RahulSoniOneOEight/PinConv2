"""Level 1 outcome-detail gates.

These checks enforce the review standard in ``docs/level1-detail-standard.md``.
They are deliberately conservative: they do not reject a defensible planning
choice, but they refuse a research pack or plan that leaves an executor to
invent basic evidence or production instructions.
"""

from __future__ import annotations

from .models import (
    Exactness,
    FindingStatus,
    ProductionPlan,
    ResearchPack,
)


def research_quality_issues(pack: ResearchPack) -> list[str]:
    """Return reasons a research pack is too thin to support a Level 1 plan."""

    issues: list[str] = []
    if len(pack.questions) < 5:
        issues.append("research needs at least five decision-relevant questions")
    if len(pack.sources) < 5:
        issues.append("research needs at least five cited sources")
    if len(pack.findings) < 8:
        issues.append("research needs at least eight findings")

    source_ids = {source.id for source in pack.sources}
    finding_ids = {finding.id for finding in pack.findings}
    for question in pack.questions:
        if not question.finding_ids:
            issues.append(f"{question.id} has no linked finding")
        for finding_id in question.finding_ids:
            if finding_id not in finding_ids:
                issues.append(f"{question.id} references unknown finding {finding_id}")

    for finding in pack.findings:
        if finding.source_id not in source_ids:
            issues.append(f"{finding.id} references unknown source {finding.source_id}")
        if not finding.evidence_locator.strip():
            issues.append(f"{finding.id} has no evidence locator")
        if finding.status is FindingStatus.VERIFIED and finding.confidence < 3:
            issues.append(f"{finding.id} is verified with confidence below 3")

    if pack.effect_assessments:
        selected = [effect for effect in pack.effect_assessments if effect.selected]
        rejected = [effect for effect in pack.effect_assessments if not effect.selected]
        if not selected:
            issues.append("effect research selects no effect")
        if not rejected:
            issues.append("effect research records no rejected alternative")
        seen_effects: set[str] = set()
        for effect in pack.effect_assessments:
            if effect.id in seen_effects:
                issues.append(f"duplicate effect assessment {effect.id}")
            seen_effects.add(effect.id)
            if not effect.finding_ids:
                issues.append(f"{effect.id} has no linked finding")
            for finding_id in effect.finding_ids:
                if finding_id not in finding_ids:
                    issues.append(f"{effect.id} references unknown finding {finding_id}")
            if effect.selected and not effect.fallback.strip():
                issues.append(f"{effect.id} has no fallback")
            if effect.selected and not effect.rights_safety.strip():
                issues.append(f"{effect.id} has no rights or safety position")

    if not any(source.reliability.value == "primary" for source in pack.sources):
        issues.append("research has no primary source")
    if not any(finding.status is FindingStatus.ASSUMPTION for finding in pack.findings):
        issues.append("research does not label any working assumption")
    return issues


def plan_detail_issues(plan: ProductionPlan, research: ResearchPack | None = None) -> list[str]:
    """Return reasons a plan cannot be executed without inventing a decision."""

    issues: list[str] = []
    for shot in plan.shots:
        if not shot.asset_ids:
            issues.append(f"{shot.id} declares no asset")
        if len(shot.layer_ids) < 4:
            issues.append(f"{shot.id} has fewer than four executable layers")
        layers = [
            plan.layer_map[layer_id] for layer_id in shot.layer_ids if layer_id in plan.layer_map
        ]
        if not any(layer.role.value == "background" for layer in layers):
            issues.append(f"{shot.id} has no background layer")
        if plan.detail_level == "full":
            if not shot.lens_intent:
                issues.append(f"{shot.id} has no lens intent")
            if not shot.acceptance:
                issues.append(f"{shot.id} has no observable acceptance condition")
            if shot.handles_frames < 2:
                issues.append(f"{shot.id} has no editorial handles")
            if not shot.audio_ids:
                issues.append(f"{shot.id} has no audio cue links")
            if shot.production_ready and shot.rights_readiness != "cleared":
                issues.append(f"{shot.id} is production-ready before rights clearance")

    if not any(layer.role.value == "product" for layer in plan.layers):
        issues.append("plan has no product layer")

    if plan.detail_level == "full":
        for beat in plan.beats:
            if not beat.asset_ids:
                issues.append(f"{beat.id} has no asset references")
            for asset_id in beat.asset_ids:
                if asset_id not in plan.asset_map:
                    issues.append(f"{beat.id} references unknown asset {asset_id}")

    for layer in plan.layers:
        if not layer.allowed_edits:
            issues.append(f"{layer.id} has no allowed-edit rule")
        if plan.detail_level == "full":
            if not layer.acceptance:
                issues.append(f"{layer.id} has no rendered acceptance condition")
            if layer.effect and not layer.effect_spec:
                issues.append(f"{layer.id} has an effect with no effect specification")
        if layer.exactness is Exactness.EXACT and layer.binding_kind.value == "asset":
            asset = plan.asset_map.get(layer.binding_ref or "")
            if asset is None or asset.exactness is not Exactness.EXACT:
                issues.append(f"{layer.id} is exact but does not bind an exact asset")

    for asset in plan.assets:
        if not asset.description.strip():
            issues.append(f"{asset.id} has no visual or audio brief")
        if not asset.source:
            issues.append(f"{asset.id} has no source or production route")
        if plan.detail_level == "full" and not asset.acceptance:
            issues.append(f"{asset.id} has no acceptance condition")
        if asset.route.value == "to_generate" and not asset.generation_spec:
            issues.append(f"{asset.id} is generated with no specification")
        if plan.detail_level == "full" and asset.fallback_required:
            has_alternate = asset.fallback_asset_id is not None or any(
                asset.id in alternate.target_ids for alternate in plan.alternates
            )
            if not has_alternate:
                issues.append(f"{asset.id} requires a fallback but has none")

    selected_research: set[str] = set()
    if research is not None:
        selected_research = {effect.id for effect in research.effect_assessments if effect.selected}

    for effect in plan.effects:
        if not effect.fallback.strip():
            issues.append(f"{effect.id} has no fallback")
        if not effect.acceptance.strip():
            issues.append(f"{effect.id} has no acceptance condition")
        if not effect.rights_or_safety.strip():
            issues.append(f"{effect.id} has no rights or safety position")
        if research is not None and effect.research_ref not in selected_research:
            issues.append(
                f"{effect.id} references {effect.research_ref}, "
                "which is not a selected research effect"
            )
        for asset_id in effect.asset_ids:
            if asset_id not in plan.asset_map:
                issues.append(f"{effect.id} references unknown asset {asset_id}")

    if plan.detail_level == "full" and not plan.effects:
        issues.append("full-detail plan does not select any effects")

    for variant in plan.variant_overrides:
        if variant.width and variant.height:
            if not variant.layer_overrides:
                issues.append(f"{variant.id} has dimensions but no layer overrides")
            if not variant.safe_area_basis:
                issues.append(f"{variant.id} has no safe-area basis")
            if variant.cost_estimate_id is None:
                issues.append(f"{variant.id} has no cost estimate reference")

    return issues
