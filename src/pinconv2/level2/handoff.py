"""Handoff ingestion and hash validation.

Level 2 refuses to plan against a plan, handoff, packet or approval that do not
belong to the same approved revision. The three hashes in the plan document are
recomputed here, not trusted.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import Field

from ..models import (
    Asset,
    AssetRoute,
    BriefRevision,
    Gate1Approval,
    Gate1Packet,
    Level2Handoff,
    ProductionPlan,
    StrictModel,
    content_hash,
)
from ..store import ProjectStore
from .errors import HandoffHashError
from .models import (
    AssetIntent,
    Impact,
    LayerMethodDecision,
    TruthClass,
)
from .truth import classify_layer

_IMPACT_ORDER = {Impact.LOW: 0, Impact.MEDIUM: 1, Impact.HIGH: 2}


class ApprovedInputs(StrictModel):
    plan: ProductionPlan
    handoff: Level2Handoff
    brief: BriefRevision
    packet: Gate1Packet
    approval: Gate1Approval


def recompute_bundle(store: ProjectStore, plan: ProductionPlan) -> tuple[dict[str, str], str]:
    project_id = plan.project_id
    brief = store.load_brief(project_id)
    research = store.load_research(project_id)
    concept = store.load_concept(project_id)
    validation = store.load_validation(project_id, plan.revision)
    critique = store.load_critique(project_id, plan.revision)
    hashes = {
        "brief": content_hash(brief),
        "research": content_hash(research),
        "concept": content_hash(concept),
        "plan": plan.plan_hash(),
        "validation": content_hash(validation),
        "critique": content_hash(critique),
    }
    resolution = store.latest_resolution(project_id)
    if resolution is not None and resolution.to_revision == plan.revision:
        hashes["resolution"] = content_hash(resolution)
    encoded = json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashes, hashlib.sha256(encoded).hexdigest()


def load_approved_inputs(store: ProjectStore, project_id: str, revision: int) -> ApprovedInputs:
    plan = store.load_plan(project_id, revision)
    handoff_path = store.export_dir(project_id, revision) / "level2-handoff.json"
    if not handoff_path.is_file():
        raise HandoffHashError(f"no Level 2 handoff exported for revision {revision}")
    handoff = Level2Handoff.model_validate_json(handoff_path.read_text(encoding="utf-8"))
    approval = store.load_approval(project_id, revision)
    packet = store.load_packet(project_id, revision)
    brief = store.load_brief(project_id)

    current_hash = plan.plan_hash()
    if handoff.plan_hash != current_hash:
        raise HandoffHashError("handoff is bound to a different plan hash")
    if approval.plan_hash != current_hash:
        raise HandoffHashError("approval is bound to a different plan hash")
    if handoff.approval.plan_hash != current_hash:
        raise HandoffHashError("the copied approval in the handoff is stale")
    if handoff.approval.approver != approval.approver:
        raise HandoffHashError("the handoff approver does not match the approval record")

    record_hashes, bundle_hash = recompute_bundle(store, plan)
    if record_hashes != approval.record_hashes:
        raise HandoffHashError("the brief, research, concept or plan changed after approval")
    if bundle_hash != approval.bundle_hash:
        raise HandoffHashError("the approval bundle hash no longer matches the records")
    packet_hash = content_hash(packet.model_copy(update={"approval": None}))
    if packet_hash != approval.packet_hash:
        raise HandoffHashError("the Gate 1 packet changed after approval")
    if not packet.validation_passed:
        raise HandoffHashError("the approved Gate 1 packet did not pass validation")

    return ApprovedInputs(
        plan=plan,
        handoff=handoff,
        brief=brief,
        packet=packet,
        approval=approval,
    )


def asset_truth_class(asset: Asset) -> TruthClass:
    if asset.exactness.value == "exact":
        return TruthClass.EXACT
    if asset.route is AssetRoute.TO_CAPTURE:
        return TruthClass.PROOF
    name = asset.name.lower()
    if any(word in name for word in ("music", "sting", "sound effect", "background")):
        return TruthClass.ATMOSPHERIC
    return TruthClass.REPRESENTATIVE


def _impact_from_decisions(asset_id: str, decisions: list[LayerMethodDecision]) -> Impact:
    impacts = [decision.impact for decision in decisions if decision.asset_id == asset_id]
    if not impacts:
        return Impact.LOW
    return max(impacts, key=lambda impact: _IMPACT_ORDER[impact])


def _tech_spec(asset: Asset) -> str:
    parts = [asset.tech.format]
    if asset.tech.width and asset.tech.height:
        parts.append(f"{asset.tech.width}x{asset.tech.height}")
    if asset.tech.fps:
        parts.append(f"{asset.tech.fps} fps")
    if asset.tech.duration_frames:
        parts.append(f"{asset.tech.duration_frames} frames")
    if asset.tech.transparency:
        parts.append("alpha")
    if asset.tech.notes:
        parts.append(asset.tech.notes)
    return ", ".join(parts)


def build_intents(
    inputs: ApprovedInputs, decisions: list[LayerMethodDecision]
) -> list[AssetIntent]:
    plan = inputs.plan
    handoff_assets = {asset.asset_id: asset for asset in inputs.handoff.assets}
    held = {item.id: item for item in inputs.handoff.held_items}
    fallback_targets = {asset.fallback_asset_id for asset in plan.assets if asset.fallback_asset_id}

    for asset in plan.assets:
        if asset.id not in handoff_assets and asset.id not in fallback_targets:
            raise HandoffHashError(
                f"{asset.id} is neither approved in the handoff nor a fallback target"
            )

    intents: list[AssetIntent] = []
    for asset in plan.assets:
        approved = asset.id in handoff_assets
        estimate = plan.estimate_map.get(asset.estimate_id or "")
        estimate_usd = (
            handoff_assets[asset.id].estimate_usd
            if approved
            else (estimate.amount_usd if estimate is not None else 0.0)
        )
        holds = [item.id for item in held.values() if asset.id in item.affects]
        rights_status = asset.rights.status.value
        intents.append(
            AssetIntent(
                asset_id=asset.id,
                name=asset.name,
                route=asset.route.value,
                truth_class=asset_truth_class(asset),
                impact=_impact_from_decisions(asset.id, decisions),
                scope="approved" if approved else "conditional_fallback",
                exactness=asset.exactness.value,
                specification=_tech_spec(asset),
                acceptance=asset.acceptance or asset.description,
                estimate_id=asset.estimate_id,
                estimate_usd=round(estimate_usd, 2),
                fallback_asset_id=asset.fallback_asset_id,
                dependencies=list(asset.dependencies),
                rights_status=rights_status,
                holds=sorted(holds),
                used_by=list(asset.used_by),
                disclosure_required=asset.rights.disclosure_required,
                notes=asset.notes,
            )
        )
    return intents


def layer_bindings(plan: ProductionPlan) -> dict[str, str]:
    """Map every asset-bound layer to its asset."""

    bindings: dict[str, str] = {}
    for layer in plan.layers:
        if layer.binding_kind.value == "asset" and layer.binding_ref:
            bindings[layer.id] = layer.binding_ref
    return bindings


def classify_all(plan: ProductionPlan) -> dict[str, tuple[TruthClass, str]]:
    return {layer.id: classify_layer(layer, plan) for layer in plan.layers}


def export_path(store: ProjectStore, project_id: str, revision: int, name: str) -> Path:
    return store.export_dir(project_id, revision) / name


class HandoffSummary(StrictModel):
    project_id: str
    plan_revision: int
    plan_hash: str
    bundle_hash: str
    packet_hash: str
    approved_assets: int
    conditional_assets: int
    approver: str
    approved_variants: list[str] = Field(default_factory=list)
