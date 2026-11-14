"""Cross-reference, coverage and readiness checks."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..models import (
    TEXT_LAYER_ROLES,
    Asset,
    BindingKind,
    Exactness,
    LayerRole,
    RightsStatus,
    Severity,
    ShotStatus,
)
from .common import ValidationContext


def _all_ids(context: ValidationContext) -> set[str]:
    plan = context.plan
    ids: set[str] = set()
    collections: list[Sequence[Any]] = [
        plan.shots,
        plan.beats,
        plan.layers,
        plan.copy_blocks,
        plan.exact_data,
        plan.claims,
        plan.assets,
        plan.audio_cues,
        plan.transitions,
        plan.alternates,
        plan.estimates,
        plan.checks,
        plan.held_items,
        plan.decisions,
    ]
    for collection in collections:
        for record in collection:
            ids.add(record.id)
    ids.add(plan.deliverable.id)
    ids.update(item.id for item in context.brief.must_have)
    return ids


def validate_traceability(context: ValidationContext) -> None:
    plan = context.plan
    known = _all_ids(context)
    layer_map = plan.layer_map
    asset_map = plan.asset_map
    check_map = plan.check_map

    with context.group("trace.ids", "plan", "record identifiers are unique"):
        seen: set[str] = set()
        collections: list[Sequence[Any]] = [
            plan.shots,
            plan.beats,
            plan.layers,
            plan.copy_blocks,
            plan.exact_data,
            plan.claims,
            plan.assets,
            plan.audio_cues,
            plan.transitions,
            plan.alternates,
            plan.estimates,
            plan.checks,
            plan.held_items,
            plan.decisions,
        ]
        for collection in collections:
            for record in collection:
                if record.id in seen:
                    context.fail(
                        "trace.ids",
                        record.id,
                        Severity.BLOCKER,
                        "duplicate identifier in the plan",
                        "Give every record a unique identifier.",
                    )
                seen.add(record.id)

    with context.group("trace.shots", "shots", "every shot reference resolves"):
        for shot in plan.shots:
            for beat_id in shot.beat_ids:
                if beat_id not in plan.beat_map:
                    context.fail(
                        "trace.shots",
                        shot.id,
                        Severity.BLOCKER,
                        f"unknown beat {beat_id}",
                        "Bind the shot to an existing beat.",
                    )
            for layer_id in shot.layer_ids:
                if layer_id not in layer_map:
                    context.fail(
                        "trace.shots",
                        shot.id,
                        Severity.BLOCKER,
                        f"unknown layer {layer_id}",
                        "Create the layer or remove the reference.",
                    )
            for asset_id in shot.asset_ids:
                if asset_id not in asset_map:
                    context.fail(
                        "trace.shots",
                        shot.id,
                        Severity.BLOCKER,
                        f"unknown asset {asset_id}",
                        "Create the asset requirement.",
                    )
            for check_id in shot.check_ids:
                if check_id not in check_map:
                    context.fail(
                        "trace.shots",
                        shot.id,
                        Severity.BLOCKER,
                        f"unknown acceptance check {check_id}",
                        "Create the check or remove the reference.",
                    )
            for estimate_id in shot.estimate_ids:
                if estimate_id not in plan.estimate_map:
                    context.fail(
                        "trace.shots",
                        shot.id,
                        Severity.BLOCKER,
                        f"unknown estimate {estimate_id}",
                        "Create the estimate or remove the reference.",
                    )
            if shot.fallback_method.strip().lower() == shot.method.strip().lower():
                context.fail(
                    "trace.shots",
                    shot.id,
                    Severity.MEDIUM,
                    "fallback method is identical to the primary method",
                    "Describe a genuinely different route.",
                )

    with context.group("trace.beats", "beats", "beats are used and resolve their cues"):
        used_beats: set[str] = set()
        for shot in plan.shots:
            used_beats.update(shot.beat_ids)
        for beat in plan.beats:
            if beat.id not in used_beats:
                context.warn(
                    "trace.beats",
                    beat.id,
                    "beat is not covered by any shot",
                    "Bind the beat to a shot or remove it.",
                )
            for cue_id in beat.audio_cue_ids:
                if cue_id not in plan.audio_map:
                    context.fail(
                        "trace.beats",
                        beat.id,
                        Severity.HIGH,
                        f"unknown audio cue {cue_id}",
                        "Create the cue or remove the reference.",
                    )
            for copy_id in beat.copy_ids:
                if copy_id not in plan.copy_map:
                    context.fail(
                        "trace.beats",
                        beat.id,
                        Severity.HIGH,
                        f"unknown copy block {copy_id}",
                        "Create the copy or remove the reference.",
                    )

    with context.group("trace.assets", "assets", "asset usage is recorded both ways"):
        actual_usage: dict[str, set[str]] = {asset.id: set() for asset in plan.assets}
        for layer in plan.layers:
            if layer.binding_kind is BindingKind.ASSET and layer.binding_ref in actual_usage:
                actual_usage[layer.binding_ref].add(layer.id)
        for cue in plan.audio_cues:
            if cue.asset_id in actual_usage:
                actual_usage[cue.asset_id].add(cue.id)
        for asset in plan.assets:
            declared = set(asset.used_by)
            actual = actual_usage[asset.id]
            if declared != actual:
                context.fail(
                    "trace.assets",
                    asset.id,
                    Severity.MEDIUM,
                    f"used_by {sorted(declared)} does not match actual usage {sorted(actual)}",
                    "Record every layer or cue that uses the asset.",
                )
            for reference in declared:
                if reference not in known:
                    context.fail(
                        "trace.assets",
                        asset.id,
                        Severity.HIGH,
                        f"used_by references unknown record {reference}",
                        "Fix the usage reference.",
                    )
            if asset.fallback_asset_id and asset.fallback_asset_id not in asset_map:
                context.fail(
                    "trace.assets",
                    asset.id,
                    Severity.HIGH,
                    f"fallback asset {asset.fallback_asset_id} does not exist",
                    "Create the fallback asset requirement.",
                )
            is_fallback = any(
                other.fallback_asset_id == asset.id for other in plan.assets
            ) or any(asset.id in alternate.target_ids for alternate in plan.alternates)
            if not actual and not is_fallback:
                context.warn(
                    "trace.assets",
                    asset.id,
                    "asset is not used by any layer or audio cue",
                    "Remove it or bind it to the work that needs it.",
                )

    with context.group(
        "trace.dependencies", "assets", "asset dependencies resolve and are acyclic"
    ):
        graph: dict[str, list[str]] = {}
        for asset in plan.assets:
            resolved: list[str] = []
            for dependency in asset.dependencies:
                if dependency == asset.id:
                    context.fail(
                        "trace.dependencies",
                        asset.id,
                        Severity.HIGH,
                        "asset depends on itself",
                        "Remove the self dependency.",
                    )
                elif dependency not in asset_map:
                    context.fail(
                        "trace.dependencies",
                        asset.id,
                        Severity.HIGH,
                        f"unknown dependency {dependency}",
                        "Create the dependency or remove the reference.",
                    )
                else:
                    resolved.append(dependency)
            graph[asset.id] = resolved

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str, path: list[str]) -> None:
            if node in visiting:
                context.fail(
                    "trace.dependencies",
                    node,
                    Severity.HIGH,
                    "dependency cycle: " + " -> ".join([*path, node]),
                    "Break the cycle.",
                )
                return
            if node in visited:
                return
            visiting.add(node)
            for dependency in graph.get(node, []):
                visit(dependency, [*path, node])
            visiting.remove(node)
            visited.add(node)

        for asset_id in graph:
            visit(asset_id, [])

        for alternate in plan.alternates:
            for dependency in alternate.revised_dependencies:
                if dependency not in known:
                    context.fail(
                        "trace.dependencies",
                        alternate.id,
                        Severity.HIGH,
                        f"alternate depends on unknown record {dependency}",
                        "Point the alternate at existing work.",
                    )

    with context.group("trace.checks", "checks", "acceptance checks target real work"):
        for check in plan.checks:
            for target in check.target_ids:
                if target not in known:
                    context.fail(
                        "trace.checks",
                        check.id,
                        Severity.HIGH,
                        f"unknown target {target}",
                        "Point the check at an existing record.",
                    )
        for shot in plan.shots:
            if not shot.check_ids:
                context.fail(
                    "trace.checks",
                    shot.id,
                    Severity.MEDIUM,
                    "shot has no acceptance check",
                    "Add an observable check for the shot.",
                )

    with context.group("trace.alternates", "alternates", "alternate routes are executable"):
        for alternate in plan.alternates:
            for target in alternate.target_ids:
                if target not in known:
                    context.fail(
                        "trace.alternates",
                        alternate.id,
                        Severity.HIGH,
                        f"unknown target {target}",
                        "Point the alternate at existing work.",
                    )
            if alternate.cost_estimate_id and alternate.cost_estimate_id not in plan.estimate_map:
                context.fail(
                    "trace.alternates",
                    alternate.id,
                    Severity.MEDIUM,
                    f"unknown cost estimate {alternate.cost_estimate_id}",
                    "Create the fallback estimate.",
                )
            for scope in alternate.approval_scope:
                if scope not in known:
                    context.fail(
                        "trace.alternates",
                        alternate.id,
                        Severity.MEDIUM,
                        f"unknown approval scope {scope}",
                        "Scope the alternate to existing shots or assets.",
                    )

    with context.group("trace.must_have", "brief", "every must-have is covered"):
        for item in context.brief.must_have:
            if item.status != "satisfied":
                context.fail(
                    "trace.must_have",
                    item.id,
                    Severity.BLOCKER,
                    f"must-have is {item.status}: {item.text}",
                    "Cover the must-have or record a human-approved scope change.",
                )
            if not item.satisfied_by:
                context.fail(
                    "trace.must_have",
                    item.id,
                    Severity.HIGH,
                    "must-have has no evidence target",
                    "Link it to a shot, layer, check or data record.",
                )
            for target in item.satisfied_by:
                if target not in known:
                    context.fail(
                        "trace.must_have",
                        item.id,
                        Severity.HIGH,
                        f"unknown evidence target {target}",
                        "Point the must-have at existing work.",
                    )

    with context.group("trace.held", "held", "held items are scoped and actionable"):
        for held in plan.held_items:
            for target in held.affects:
                if target not in known:
                    context.fail(
                        "trace.held",
                        held.id,
                        Severity.HIGH,
                        f"unknown affected record {target}",
                        "Point the hold at existing work.",
                    )
            if not held.required_evidence.strip():
                context.fail(
                    "trace.held",
                    held.id,
                    Severity.MEDIUM,
                    "held item does not state the evidence needed",
                    "Record what would clear the hold.",
                )

    with context.group("trace.shot_status", "shots", "shot status matches its blockers"):
        for shot in plan.shots:
            layers = [
                layer_map[layer_id]
                for layer_id in shot.layer_ids
                if layer_id in layer_map
            ]
            required_assets = {
                layer.binding_ref
                for layer in layers
                if layer.required
                and layer.binding_kind is BindingKind.ASSET
                and layer.binding_ref
            }
            blocking = False
            for asset_id in required_assets:
                blocking_asset: Asset | None = asset_map.get(asset_id)
                if blocking_asset and blocking_asset.rights.status in {
                    RightsStatus.BLOCKED,
                    RightsStatus.REFERENCE_ONLY,
                }:
                    blocking = True
            if shot.status is ShotStatus.READY and blocking:
                context.fail(
                    "trace.shot_status",
                    shot.id,
                    Severity.BLOCKER,
                    "shot is marked ready but a required asset is blocked",
                    "Mark the shot held or replace the asset.",
                )
            if shot.status is not ShotStatus.READY:
                covered = any(shot.id in item.affects for item in plan.held_items)
                if not covered:
                    context.warn(
                        "trace.shot_status",
                        shot.id,
                        f"shot is {shot.status.value} without a held-item explanation",
                        "Record the reason and the evidence needed to unblock it.",
                    )

    with context.group("trace.cta", "deliverable", "the deliverable CTA resolves"):
        cta_id = plan.deliverable.cta_copy_id
        if cta_id is not None and cta_id not in plan.copy_map:
            context.fail(
                "trace.cta",
                "deliverable",
                Severity.HIGH,
                f"CTA copy {cta_id} does not exist",
                "Create the CTA copy block or clear the field.",
            )
        if cta_id is not None:
            cta_layers = [
                layer
                for layer in plan.layers
                if layer.role is LayerRole.CTA and layer.binding_ref == cta_id
            ]
            if not cta_layers:
                context.fail(
                    "trace.cta",
                    "deliverable",
                    Severity.HIGH,
                    "CTA copy is not bound to a CTA layer",
                    "Bind the CTA copy to a visible layer.",
                )

    with context.group("trace.critical_assets", "assets", "critical assets have a route out"):
        for asset in plan.assets:
            used_by_required = any(
                layer.required
                and layer.binding_kind is BindingKind.ASSET
                and layer.binding_ref == asset.id
                for layer in plan.layers
            )
            if not used_by_required or asset.exactness is not Exactness.EXACT:
                continue
            has_alternate = asset.fallback_asset_id is not None or any(
                asset.id in alternate.target_ids for alternate in plan.alternates
            )
            has_hold = any(asset.id in item.affects for item in plan.held_items)
            if not has_alternate and not has_hold:
                context.warn(
                    "trace.critical_assets",
                    asset.id,
                    "critical exact asset has no fallback, alternate or hold",
                    "Add a viable alternate route or record a hold.",
                )

    with context.group("trace.layers", "layers", "required text and visuals are bound"):
        for layer in plan.layers:
            if layer.role in TEXT_LAYER_ROLES and layer.binding_kind is not BindingKind.COPY:
                context.fail(
                    "trace.layers",
                    layer.id,
                    Severity.BLOCKER,
                    "text layer does not bind a copy block",
                    "Bind it to copy so claims and exact data are checked.",
                )
