"""Per-shot/layer source sheet.

The review pack says what an asset *is*; this sheet says where each layer's media
actually comes from, and which library candidate was chosen for audio. It is the
quickest way for a reviewer to see “this layer uses this source”.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..models import ProductionPlan
from .html_export import markdown_to_html
from .models import BuildSheet, Level2Plan, SourcingCandidate


def _candidate_map(level2: Level2Plan) -> dict[str, SourcingCandidate]:
    if level2.sourcing is None:
        return {}
    chosen: dict[str, SourcingCandidate] = {}
    for asset in level2.sourcing.assets:
        for candidate in asset.candidates:
            if candidate.candidate_id == asset.chosen_candidate:
                chosen[asset.asset_id] = candidate
    return chosen


def source_sheet_data(
    plan: ProductionPlan,
    level2: Level2Plan,
    sheet: BuildSheet,
    run_dir: Path | None = None,
) -> dict[str, Any]:
    assets = sheet.asset_map()
    decisions = level2.decision_map()
    chosen = _candidate_map(level2)
    layers: list[dict[str, Any]] = []
    for shot in sheet.shots:
        for binding in shot.layers:
            layer = plan.layer_map[binding.layer_id]
            asset = assets.get(binding.asset_id or "")
            if asset is not None:
                source = asset.source
                rights = asset.rights_status
                status = asset.status.value
            elif binding.copy_id:
                source = f"copy:{binding.copy_id}"
                rights = "n/a"
                status = "procedural"
            else:
                source = "procedural"
                rights = "n/a"
                status = "procedural"
            layers.append(
                {
                    "shot_id": shot.shot_id,
                    "layer_id": layer.id,
                    "role": layer.role.value,
                    "truth_class": decisions[layer.id].truth_class.value,
                    "method": binding.method.value,
                    "asset_id": binding.asset_id,
                    "copy_id": binding.copy_id,
                    "source": source,
                    "rights": rights,
                    "status": status,
                    "preview": f"build-sheet/previews/16x9/{shot.shot_id}.svg",
                }
            )

    audio: list[dict[str, Any]] = []
    for cue in plan.audio_cues:
        asset = assets.get(cue.asset_id or "")
        shots = [
            shot.id
            for shot in plan.shots
            if cue.start_frame < shot.end_frame and cue.end_frame > shot.start_frame
        ]
        candidate = chosen.get(cue.asset_id or "")
        audio.append(
            {
                "cue_id": cue.id,
                "asset_id": cue.asset_id,
                "kind": cue.kind.value,
                "start_frame": cue.start_frame,
                "end_frame": cue.end_frame,
                "shots": shots,
                "source": asset.source if asset else "—",
                "rights": asset.rights_status if asset else "—",
                "status": asset.status.value if asset else "—",
                "licence": candidate.licence_class.value if candidate else None,
                "attribution": candidate.attribution if candidate else None,
                "page_url": candidate.page_url if candidate else None,
                "preview": candidate.preview_path if candidate else None,
            }
        )

    primary_assets = {cue.asset_id for cue in plan.audio_cues}
    for index, sound_cue in enumerate(level2.sound.cues, start=1):
        if sound_cue.asset_id in primary_assets:
            continue
        asset = assets.get(sound_cue.asset_id)
        candidate = chosen.get(sound_cue.asset_id)
        preview = candidate.preview_path if candidate else None
        if (
            preview is None
            and sound_cue.asset_id == "AS-15"
            and run_dir is not None
            and (run_dir / "generated" / "AS-15-edge-sample.mp3").is_file()
        ):
            preview = "generated/AS-15-edge-sample.mp3"
        audio.append(
            {
                "cue_id": f"SF-{index:02d}",
                "asset_id": sound_cue.asset_id,
                "kind": sound_cue.kind,
                "start_frame": sound_cue.in_frame,
                "end_frame": sound_cue.out_frame,
                "shots": [shot.id for shot in plan.shots],
                "source": asset.source if asset else "generate",
                "rights": asset.rights_status if asset else "needs_approval",
                "status": asset.status.value if asset else "conditional",
                "licence": candidate.licence_class.value if candidate else None,
                "attribution": candidate.attribution if candidate else None,
                "page_url": candidate.page_url if candidate else None,
                "preview": preview,
            }
        )

    sourced: list[dict[str, Any]] = []
    for sourcing_asset in level2.sourcing.assets if level2.sourcing is not None else []:
        candidate = chosen.get(sourcing_asset.asset_id)
        if candidate is None:
            continue
        sourced.append(
            {
                "asset_id": sourcing_asset.asset_id,
                "query": sourcing_asset.query,
                "title": candidate.title,
                "creator": candidate.creator,
                "licence": candidate.licence_class.value,
                "attribution": candidate.attribution,
                "page_url": candidate.page_url,
                "preview": candidate.preview_path,
                "fit_score": candidate.fit_score,
                "gate": candidate.gate_verdict.value,
            }
        )

    return {
        "run_id": level2.run_id,
        "plan_hash": level2.plan_hash,
        "layer_count": len(layers),
        "audio_count": len(audio),
        "sourced_count": len(sourced),
        "layers": layers,
        "audio": audio,
        "sourced": sourced,
    }


def render_source_sheet(data: dict[str, Any]) -> str:
    lines = [
        f"# Asset source sheet — run {data['run_id']}",
        "",
        "Every layer, the asset it uses, and where that asset comes from.",
        "",
        f"- Layers: {data['layer_count']}",
        f"- Audio assets: {data['audio_count']}",
        f"- Sourced library assets: {data['sourced_count']}",
        "",
        "## Layers by shot",
        "",
        "| Shot | Layer | Role | Class | Method | Asset | Source | Rights | Status | Preview |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in data["layers"]:
        asset = row["asset_id"] or row["copy_id"] or "—"
        lines.append(
            f"| {row['shot_id']} | {row['layer_id']} | {row['role']} | "
            f"{row['truth_class']} | {row['method']} | {asset} | {row['source']} | "
            f"{row['rights']} | {row['status']} | [SVG]({row['preview']}) |"
        )

    lines.extend(
        [
            "",
            "## Audio assets",
            "",
            "| Cue | Asset | Kind | Frames | Shots | Source | Licence | Status | Preview |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in data["audio"]:
        lines.append(
            f"| {row['cue_id']} | {row['asset_id']} | {row['kind']} | "
            f"{row['start_frame']}–{row['end_frame']} | {', '.join(row['shots']) or '—'} | "
            f"{row['source']} | {row['licence'] or '—'} | {row['status']} | "
            + (f"[listen]({row['preview']})" if row["preview"] else "—")
        )

    if data["sourced"]:
        lines.extend(["", "## Sourced library candidates", ""])
        for row in data["sourced"]:
            lines.extend(
                [
                    f"### {row['asset_id']} — {row['title']}",
                    "",
                    f"- Creator: {row['creator']}",
                    f"- Licence: **{row['licence']}** · fit {row['fit_score']} "
                    f"· gate {row['gate']}",
                    f"- Attribution: {row['attribution']}",
                    f"- Source: {row['page_url']}",
                    f"- Preview: [listen]({row['preview']})" if row["preview"] else "- Preview: —",
                    "",
                ]
            )

    lines.extend(
        [
            "",
            "## Reading this sheet",
            "",
            "- `source` is the actual route: supplied, owned, capture, stock or procedural.",
            "- `exact` and `proof` layers must never show a stock source.",
            "- A selected library track is still a preview until Gate 2A and the final licence.",
            "",
        ]
    )
    return "\n".join(lines)


def write_source_sheet(
    run: Any, run_id: str, plan: ProductionPlan, level2: Level2Plan, sheet: BuildSheet
) -> dict[str, Any]:
    data = source_sheet_data(plan, level2, sheet, run.run_dir(run_id))
    markdown = render_source_sheet(data)
    run.write_text(run_id, "SOURCE-SHEET.md", markdown)
    run.write_text(
        run_id,
        "SOURCE-SHEET.html",
        markdown_to_html(markdown, f"Asset source sheet — run {run_id}"),
    )
    run.write_data(run_id, "SOURCE-SHEET.json", data)
    return data
