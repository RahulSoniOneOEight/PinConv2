"""Build sheet assembly and rendering.

The build sheet is pure data plus a readable view. It references the approved
Level 1 IDs, never re-derives a creative decision, and carries the resolved hash
of every part so a compositor can verify what they received.
"""

from __future__ import annotations

from collections.abc import Iterable

from ..models import Layer, ProductionPlan
from .models import (
    AssetIntent,
    AssetPackage,
    AssetProductionTask,
    BudgetEstimate,
    BuildSheet,
    BuildSheetManifest,
    Correction,
    LayerBinding,
    LayerMethodDecision,
    Method,
    ShotPackage,
    SourcingReport,
    TaskStatus,
    Timeline,
    TimelineEntry,
    VariantPackage,
)

_CAPTION_ROLES = {"caption"}


def _binding_method(layer_id: str, decisions: dict[str, LayerMethodDecision]) -> Method:
    decision = decisions.get(layer_id)
    if decision is None:
        raise KeyError(f"no method decision for {layer_id}")
    return decision.method


def build_asset_packages(
    plan: ProductionPlan,
    intents: list[AssetIntent],
    tasks: list[AssetProductionTask],
    sourcing: SourcingReport | None = None,
) -> list[AssetPackage]:
    task_map = {task.asset_id: task for task in tasks}
    intent_map = {intent.asset_id: intent for intent in intents}
    chosen = (
        {
            asset.asset_id: next(
                (
                    candidate
                    for candidate in asset.candidates
                    if candidate.candidate_id == asset.chosen_candidate
                ),
                None,
            )
            for asset in sourcing.assets
        }
        if sourcing is not None
        else {}
    )
    packages: list[AssetPackage] = []
    for asset in plan.assets:
        task = task_map[asset.id]
        intent = intent_map[asset.id]
        blockers = list(task.blockers)
        if intent.holds:
            blockers.extend(hold for hold in intent.holds if hold not in blockers)
        selected = chosen.get(asset.id)
        source = (
            f"stock:{selected.provider}:{selected.title}"
            if selected is not None
            else f"{task.source_strategy.value}:{asset.source or 'pending acquisition'}"
        )
        packages.append(
            AssetPackage(
                asset_id=asset.id,
                name=asset.name,
                truth_class=intent.truth_class,
                impact=intent.impact,
                methods=list(task.methods),
                source=source,
                processing=[f"{op.op}" for op in task.processing],
                bindings=list(asset.used_by),
                acceptance=asset.acceptance or asset.description,
                conditional=task.conditional,
                rights_status=asset.rights.status.value,
                hold=intent.holds[0] if intent.holds else None,
                status=task.status,
                blockers=sorted(set(blockers)),
            )
        )
    return packages


def _binding_for(
    layer: Layer,
    decisions: dict[str, LayerMethodDecision],
    status: TaskStatus,
) -> LayerBinding:
    decision = decisions[layer.id]
    if layer.binding_kind.value == "asset":
        transform = "asset transform per layer rect and allow-list"
    elif layer.binding_kind.value == "copy":
        transform = "text rendered from the approved copy block"
    else:
        transform = "procedural fill and effect"
    return LayerBinding(
        layer_id=layer.id,
        shot_id=layer.shot_id,
        asset_id=layer.binding_ref if layer.binding_kind.value == "asset" else None,
        copy_id=layer.binding_ref if layer.binding_kind.value == "copy" else None,
        method=decision.method,
        z_order=layer.z_order,
        start_frame=layer.start_frame,
        end_frame=layer.end_frame,
        transform=transform,
        status=status,
    )


def build_shot_packages(
    plan: ProductionPlan,
    decisions: list[LayerMethodDecision],
    tasks: list[AssetProductionTask],
    preview_paths: dict[str, str] | None = None,
) -> list[ShotPackage]:
    decision_map = {decision.layer_id: decision for decision in decisions}
    task_map = {task.asset_id: task for task in tasks}
    packages: list[ShotPackage] = []
    for shot in plan.shots:
        bindings: list[LayerBinding] = []
        blockers: set[str] = set()
        for layer_id in shot.layer_ids:
            layer = plan.layer_map[layer_id]
            if layer.binding_kind.value == "asset" and layer.binding_ref:
                task = task_map.get(layer.binding_ref)
                status = task.status if task is not None else TaskStatus.PLANNED
                if task is not None:
                    blockers.update(task.blockers)
            else:
                status = TaskStatus.PLANNED
            bindings.append(_binding_for(layer, decision_map, status))
        effects = sorted(
            {
                effect_id
                for layer_id in shot.layer_ids
                for effect_id in plan.layer_map[layer_id].effect_ids
            }
        )
        audio = [cue.id for cue in plan.audio_cues if cue.start_frame < shot.end_frame]
        ready = not blockers and all(
            binding.status in {TaskStatus.ACCEPTED, TaskStatus.PROCESSED}
            for binding in bindings
            if binding.asset_id is not None
        )
        packages.append(
            ShotPackage(
                shot_id=shot.id,
                start_frame=shot.start_frame,
                end_frame=shot.end_frame,
                method=shot.method,
                layers=bindings,
                effects=effects,
                audio=audio,
                checks=list(shot.check_ids),
                preview_path=(preview_paths or {}).get(shot.id),
                ready=ready,
                blockers=sorted(blockers),
            )
        )
    return packages


def build_timeline(plan: ProductionPlan) -> Timeline:
    entries: list[TimelineEntry] = []
    index = 1
    for shot in plan.shots:
        for layer_id in shot.layer_ids:
            layer = plan.layer_map[layer_id]
            entries.append(
                TimelineEntry(
                    entry_id=f"TL-{index:03d}",
                    track="layer",
                    ref_id=layer.id,
                    shot_id=shot.id,
                    start_frame=shot.start_frame + layer.start_frame,
                    end_frame=shot.start_frame + layer.end_frame,
                    note=layer.role.value,
                )
            )
            index += 1
    for cue in plan.audio_cues:
        entries.append(
            TimelineEntry(
                entry_id=f"TL-{index:03d}",
                track="audio",
                ref_id=cue.id,
                start_frame=cue.start_frame,
                end_frame=cue.end_frame,
                note=cue.kind.value,
            )
        )
        index += 1
    for layer in plan.layers:
        if layer.role.value in _CAPTION_ROLES:
            shot = plan.shot_map[layer.shot_id]
            entries.append(
                TimelineEntry(
                    entry_id=f"TL-{index:03d}",
                    track="caption",
                    ref_id=layer.id,
                    shot_id=shot.id,
                    start_frame=shot.start_frame + layer.start_frame,
                    end_frame=shot.start_frame + layer.end_frame,
                    note=layer.binding_ref,
                )
            )
            index += 1
    return Timeline(
        fps=plan.deliverable.fps,
        frame_count=plan.deliverable.frame_count,
        entries=entries,
        caption_files={
            "16x9": "captions/captions-16x9.srt",
            "9x16": "captions/captions-9x16.srt",
        },
    )


def _srt_time(frame: int, fps: int) -> str:
    total_ms = round(frame * 1000 / fps)
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def render_captions(plan: ProductionPlan) -> dict[str, str]:
    blocks: list[tuple[int, int, str]] = []
    for shot in plan.shots:
        for layer_id in shot.layer_ids:
            layer = plan.layer_map[layer_id]
            if layer.role.value not in _CAPTION_ROLES:
                continue
            copy_block = plan.copy_map.get(layer.binding_ref or "")
            if copy_block is None:
                continue
            start = shot.start_frame + layer.start_frame
            end = shot.start_frame + layer.end_frame
            blocks.append((start, end, copy_block.text))
    blocks.sort(key=lambda item: item[0])
    lines: list[str] = []
    for index, (start, end, text) in enumerate(blocks, start=1):
        lines.append(str(index))
        lines.append(
            f"{_srt_time(start, plan.deliverable.fps)} --> {_srt_time(end, plan.deliverable.fps)}"
        )
        lines.append(text)
        lines.append("")
    content = "\n".join(lines).strip() + "\n"
    return {"captions-16x9.srt": content, "captions-9x16.srt": content}


def build_manifest(
    *,
    run_id: str,
    project_id: str,
    plan_revision: int,
    source_plan_hash: str,
    bundle_hash: str,
    packet_hash: str,
    assets: list[AssetPackage],
    shots: list[ShotPackage],
    variants: list[VariantPackage],
    plan: ProductionPlan,
    budget: BudgetEstimate,
) -> BuildSheetManifest:
    return BuildSheetManifest(
        run_id=run_id,
        project_id=project_id,
        plan_revision=plan_revision,
        source_plan_hash=source_plan_hash,
        bundle_hash=bundle_hash,
        packet_hash=packet_hash,
        parts={},
        counts={
            "assets": len(assets),
            "layers": len(plan.layers),
            "shots": len(shots),
            "effects": len(plan.effects),
            "variants": len(variants),
            "timeline_entries": sum(len(shot.layer_ids) for shot in plan.shots)
            + len(plan.audio_cues)
            + sum(1 for layer in plan.layers if layer.role.value in _CAPTION_ROLES),
        },
        budget=budget.summary,
    )


def assemble(
    plan: ProductionPlan,
    intents: list[AssetIntent],
    decisions: list[LayerMethodDecision],
    tasks: list[AssetProductionTask],
    variants: list[VariantPackage],
    budget: BudgetEstimate,
    *,
    run_id: str,
    source_plan_hash: str,
    bundle_hash: str,
    packet_hash: str,
    preview_paths: dict[str, str] | None = None,
    corrections: list[Correction] | None = None,
    sourcing: SourcingReport | None = None,
) -> BuildSheet:
    assets = build_asset_packages(plan, intents, tasks, sourcing)
    shots = build_shot_packages(plan, decisions, tasks, preview_paths)
    manifest = build_manifest(
        run_id=run_id,
        project_id=plan.project_id,
        plan_revision=plan.revision,
        source_plan_hash=source_plan_hash,
        bundle_hash=bundle_hash,
        packet_hash=packet_hash,
        assets=assets,
        shots=shots,
        variants=variants,
        plan=plan,
        budget=budget,
    )
    return BuildSheet(
        manifest=manifest,
        assets=assets,
        shots=shots,
        variants=variants,
        timeline=build_timeline(plan),
        corrections=list(corrections or []),
    )


def render_build_sheet(sheet: BuildSheet, plan: ProductionPlan) -> str:
    manifest = sheet.manifest
    lines = [
        f"# Production build sheet — {manifest.project_id}",
        "",
        f"Run `{manifest.run_id}` · plan revision {manifest.plan_revision} · "
        f"schema {manifest.schema_version}",
        "",
        f"Source plan hash: `{manifest.source_plan_hash}`",
        "",
        "## Summary",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| Assets | {manifest.counts.get('assets', 0)} |",
        f"| Layers | {manifest.counts.get('layers', 0)} |",
        f"| Shots | {manifest.counts.get('shots', 0)} |",
        f"| Effects | {manifest.counts.get('effects', 0)} |",
        f"| Variants | {manifest.counts.get('variants', 0)} |",
        f"| Estimate | ${manifest.budget.total_usd:,.2f} |",
        f"| Worst case | ${manifest.budget.worst_usd:,.2f} |",
        f"| Cap | ${manifest.budget.cap_usd:,.2f} |",
        f"| Headroom | ${manifest.budget.headroom_usd:,.2f} |",
        "",
        "## Assets",
        "",
        "| Asset | Class | Impact | Method | Status | Rights | Hold |",
        "|---|---|---|---|---|---|---|",
    ]
    for asset in sheet.assets:
        methods = "/".join(method.value for method in asset.methods)
        lines.append(
            f"| `{asset.asset_id}` {asset.name} | {asset.truth_class.value} | "
            f"{asset.impact.value} | {methods} | {asset.status.value} | "
            f"{asset.rights_status} | {asset.hold or '—'} |"
        )
    lines.extend(["", "### Asset detail", ""])
    for asset in sheet.assets:
        lines.extend(
            [
                f"#### {asset.asset_id} · {asset.name}",
                "",
                f"- Source: {asset.source}",
                f"- Processing: {', '.join(asset.processing) or 'none'}",
                f"- Bindings: {', '.join(asset.bindings) or 'none'}",
                f"- Acceptance: {asset.acceptance}",
                f"- Status: `{asset.status.value}`",
                f"- Blockers: {', '.join(asset.blockers) or 'none'}",
                "",
            ]
        )
    lines.extend(["## Shots", ""])
    for shot in sheet.shots:
        lines.extend(
            [
                f"### {shot.shot_id} · frames {shot.start_frame}–{shot.end_frame}",
                "",
                f"- Method: {shot.method}",
                f"- Layers: {', '.join(binding.layer_id for binding in shot.layers)}",
                f"- Effects: {', '.join(shot.effects) or 'none'}",
                f"- Audio: {', '.join(shot.audio) or 'none'}",
                f"- Ready: {'yes' if shot.ready else 'no'}",
                f"- Blockers: {', '.join(shot.blockers) or 'none'}",
                "",
            ]
        )
    if sheet.variants:
        lines.extend(["## Variants", ""])
        for variant in sheet.variants:
            overrides = sum(1 for item in variant.resolutions if item.resolution == "override")
            lines.extend(
                [
                    f"### {variant.variant_id} · {variant.width}x{variant.height} "
                    f"@ {variant.fps} fps",
                    "",
                    f"- Frames: {variant.frame_count}",
                    f"- Layer overrides: {overrides} of {len(variant.resolutions)}",
                    f"- Effect overrides: {', '.join(variant.effect_overrides) or 'none'}",
                    f"- Safe area: {variant.safe_area.top}/{variant.safe_area.bottom}/"
                    f"{variant.safe_area.left}/{variant.safe_area.right}",
                    f"- Check status: `{variant.check_status}`",
                    f"- Ready: {'yes' if variant.ready else 'no'}",
                    f"- Blockers: {', '.join(variant.blockers) or 'none'}",
                    "",
                ]
            )
    lines.extend(["## Timeline", ""])
    for entry in sheet.timeline.entries:
        lines.append(
            f"- `{entry.entry_id}` {entry.track} {entry.ref_id} "
            f"{entry.start_frame}–{entry.end_frame}"
        )
    lines.append("")
    return "\n".join(lines)


def iter_asset_ids(sheet: BuildSheet) -> Iterable[str]:
    for asset in sheet.assets:
        yield asset.asset_id
