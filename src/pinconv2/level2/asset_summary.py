"""Asset-centric review outputs.

The review pack's main outcome is the shot x layer x asset table: what each
asset is, where it comes from, whether it is supplied, captured, stock or
generated, where the file can be opened, and the agent visual QC verdict.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..models import ProductionPlan
from .html_export import markdown_to_html
from .models import BuildSheet, LayerMethodDecision, Level2Plan

_ROUTE_GROUP = {
    "to_source": "stock",
    "to_capture": "capture",
    "to_generate": "generate",
    "to_create": "supplied",
}

_ACTION = {
    "to_create": "Record the approved voice artist and clear the release",
    "supplied": "Obtain rights and import the supplied file",
    "capture": "Shoot on the demonstration session and clear the release",
    "owned": "Use the owned in-house file",
    "stock": "Acquire the chosen licence after Gate 2A",
    "generate": "Use only as a disclosed fallback",
}


def load_asset_qc(run_dir: Path) -> dict[str, dict[str, Any]]:
    path = run_dir / "qc" / "assets.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("assets", payload if isinstance(payload, list) else [])
    reviewer = str(payload.get("reviewer", "")) if isinstance(payload, dict) else ""
    result = {}
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("asset_id"):
            continue
        item = dict(entry)
        item.setdefault("reviewer", reviewer)
        result[str(entry["asset_id"])] = item
    return result


def load_no_shoot(run_dir: Path) -> dict[str, dict[str, Any]]:
    path = run_dir / "no-shoot-plan.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(finding["asset_id"]): finding
        for finding in payload.get("findings", [])
        if isinstance(finding, dict) and finding.get("asset_id")
    }


def _chosen_preview(level2: Level2Plan) -> dict[str, str]:
    chosen: dict[str, str] = {}
    if level2.sourcing is None:
        return chosen
    for asset in level2.sourcing.assets:
        for candidate in asset.candidates:
            if candidate.candidate_id == asset.chosen_candidate and candidate.preview_path:
                chosen[asset.asset_id] = candidate.preview_path
    return chosen


def _access(asset_id: str, run_dir: Path, chosen: dict[str, str]) -> tuple[str, str]:
    for suffix in (".png", ".jpg", ".jpeg", ".webp"):
        candidate = run_dir / "qc" / "assets" / f"{asset_id}{suffix}"
        if candidate.is_file():
            return (
                f"qc/assets/{candidate.name}",
                f"[open]({candidate.relative_to(run_dir).as_posix()})",
            )
    if asset_id in chosen:
        path = chosen[asset_id].replace("\\", "/")
        return path, f"[preview]({path})"
    if asset_id == "AS-15":
        candidate = run_dir / "generated" / "AS-15-edge-sample.mp3"
        if candidate.is_file():
            return (
                "generated/AS-15-edge-sample.mp3",
                "[sample](generated/AS-15-edge-sample.mp3)",
            )
    return "", "not delivered"


def build_rows(
    plan: ProductionPlan,
    level2: Level2Plan,
    sheet: BuildSheet,
    decisions: list[LayerMethodDecision],
    run_dir: Path,
) -> list[dict[str, Any]]:
    asset_map = sheet.asset_map()
    intent_map = {intent.asset_id: intent for intent in level2.intents}
    decision_map = {decision.layer_id: decision for decision in decisions}
    chosen = _chosen_preview(level2)
    qc_map = load_asset_qc(run_dir)
    no_shoot_map = load_no_shoot(run_dir)

    bindings: dict[str, list[dict[str, Any]]] = {}
    for shot in sheet.shots:
        for binding in shot.layers:
            if not binding.asset_id:
                continue
            decision = decision_map[binding.layer_id]
            bindings.setdefault(binding.asset_id, []).append(
                {
                    "shot": shot.shot_id,
                    "layer": binding.layer_id,
                    "role": decision.role,
                    "method": binding.method.value,
                }
            )

    rows: list[dict[str, Any]] = []
    for asset_id in sorted(asset_map):
        asset = asset_map[asset_id]
        intent = intent_map[asset_id]
        entries = bindings.get(asset_id, [])
        shots = sorted({entry["shot"] for entry in entries})
        qc = qc_map.get(asset_id, {})
        no_shoot = no_shoot_map.get(asset_id, {})
        access_path, access_link = _access(asset_id, run_dir, chosen)
        raw_route = intent.route.value if hasattr(intent.route, "value") else str(intent.route)
        route = _ROUTE_GROUP.get(raw_route, raw_route)
        rows.append(
            {
                "asset_id": asset_id,
                "name": asset.name,
                "truth_class": asset.truth_class.value,
                "impact": asset.impact.value,
                "route": route,
                "route_raw": raw_route,
                "source": asset.source,
                "rights": asset.rights_status,
                "hold": asset.hold,
                "status": asset.status.value,
                "methods": [method.value for method in asset.methods],
                "shots": shots,
                "layers": [entry["layer"] for entry in entries],
                "layer_count": len(entries),
                "access_path": access_path,
                "access_link": access_link,
                "qc_verdict": str(qc.get("verdict", "not_run")),
                "qc_notes": str(qc.get("notes", "")),
                "qc_reviewer": str(qc.get("reviewer", "")),
                "action": _ACTION.get(raw_route, _ACTION.get(route, "Review the approved route")),
                "no_shoot_route": str(no_shoot.get("recommended_route", "")),
                "no_shoot_note": str(no_shoot.get("note", "")),
                "no_shoot_flagged": bool(no_shoot),
            }
        )
    return rows


def _qc_badge(verdict: str) -> str:
    return {
        "pass": "**pass**",
        "warn": "**warn**",
        "fail": "**fail**",
        "pending": "**pending**",
        "n/a": "n/a",
        "not_run": "not run",
    }.get(verdict, verdict)


def render_asset_summary(plan: ProductionPlan, rows: list[dict[str, Any]]) -> str:
    lines = [
        f"# Asset summary — {plan.project_id} rev-{plan.revision:03d}",
        "",
        "Every asset, the shots and layers that use it, its real source, where the",
        "file can be opened, and the agent visual QC verdict. This is the main",
        "review table for Level 2.",
        "",
        "## Coverage",
        "",
        "| Assets | Shots | Asset-bound layers | Supplied | Captured | Stock | Generated | Owned |",
        "|---|---|---|---|---|---|---|---|",
    ]
    routes = {row["route"] for row in rows}
    lines.append(
        f"| {len(rows)} | {len({shot for row in rows for shot in row['shots']})} | "
        f"{sum(row['layer_count'] for row in rows)} | "
        f"{sum(1 for row in rows if row['route'] == 'supplied')} | "
        f"{sum(1 for row in rows if row['route'] == 'capture')} | "
        f"{sum(1 for row in rows if row['route'] == 'stock')} | "
        f"{sum(1 for row in rows if row['route'] == 'generate')} | "
        f"{sum(1 for row in rows if row['route'] == 'owned')} |"
    )
    lines.extend(
        [
            "",
            "Routes present: " + ", ".join(sorted(routes)) + ".",
            "",
            "## Asset table",
            "",
            "Only asset-bound layers are counted here; copy and procedural layers are",
            "listed in `PRODUCTION-PLAN.md`.",
            "",
            "| Asset | What | Shots | Layers using it | Class | Route | No-shoot | "
            "Source | Rights | Status | Access | Visual QC |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['asset_id']}` | {row['name']} | {', '.join(row['shots']) or '—'} | "
            f"{row['layer_count']} | {row['truth_class']} | {row['route']} | "
            f"{row['no_shoot_route'] or 'keep'} | "
            f"{row['source'][:80]} | {row['rights']} | {row['status']} | "
            f"{row['access_link']} | {_qc_badge(row['qc_verdict'])} |"
        )
    lines.extend(["", "## Asset details", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['asset_id']} — {row['name']}",
                "",
                f"- Class / impact: `{row['truth_class']}` / `{row['impact']}`",
                f"- Shots: {', '.join(row['shots']) or '—'}",
                f"- Layers ({row['layer_count']}): {', '.join(row['layers']) or '—'}",
                f"- Route: `{row['route']}`",
                (
                    f"- No-shoot route: `{row['no_shoot_route']}` — {row['no_shoot_note']}"
                    if row["no_shoot_flagged"]
                    else "- No-shoot route: keep the current route"
                ),
                f"- Source: {row['source']}",
                f"- Rights: `{row['rights']}`"
                + (f" · hold `{row['hold']}`" if row["hold"] else ""),
                f"- Status: `{row['status']}`",
                f"- Methods: {', '.join(row['methods'])}",
                f"- Access: {row['access_link']}",
                f"- Visual QC: {_qc_badge(row['qc_verdict'])}"
                + (f" — {row['qc_notes']}" if row["qc_notes"] else ""),
                f"- Action: {row['action']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Reading this table",
            "",
            "- `Route` is the approved production route, not a suggestion.",
            "- `supplied` and `capture` must never be replaced by stock or generation.",
            "- `stock` and `generate` are only for atmospheric/representative material.",
            "- `Access` is the file or preview that was actually checked.",
            "- `Visual QC` is an agent verdict against the asset, not the shot preview.",
            "",
        ]
    )
    return "\n".join(lines)


def render_production_plan(
    plan: ProductionPlan,
    rows: list[dict[str, Any]],
    sheet: BuildSheet,
    level2: Level2Plan,
) -> str:
    lines = [
        f"# Production plan — {plan.project_id} rev-{plan.revision:03d}",
        "",
        f"**Run:** `{level2.run_id}` · **Plan hash:** `{plan.plan_hash()}`",
        "**Status:** Gate 2A `ready_for_approval`; no paid acquisition or generation yet.",
        "",
        "## Sequence",
        "",
        "| Shot | Frames | Layers | Assets | Ready | Blockers |",
        "|---|---|---|---|---|---|",
    ]
    for shot in sheet.shots:
        assets = sorted(
            {binding.asset_id for binding in shot.layers if binding.asset_id is not None}
        )
        lines.append(
            f"| {shot.shot_id} | {shot.start_frame}–{shot.end_frame} | "
            f"{len(shot.layers)} | {', '.join(assets) or 'procedural'} | "
            f"{'yes' if shot.ready else 'no'} | {', '.join(shot.blockers) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Asset queue",
            "",
            "| Order | Asset | Current route | Action | No-shoot route | Shots | "
            "Rights / hold | Gate |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    order = {"supplied": 0, "capture": 1, "stock": 2, "generate": 3, "owned": 4}
    for index, row in enumerate(
        sorted(rows, key=lambda item: (order.get(item["route"], 9), item["asset_id"])),
        start=1,
    ):
        gate = "Gate 2A" if row["route"] in {"stock", "generate"} else "Level 1 / rights"
        action = row["no_shoot_note"] if row["no_shoot_flagged"] else row["action"]
        lines.append(
            f"| {index} | `{row['asset_id']}` {row['name']} | {row['route']} | "
            f"{action} | {row['no_shoot_route'] or 'keep'} | "
            f"{', '.join(row['shots']) or '-'} | {row['rights']}"
            + (f" / `{row['hold']}`" if row["hold"] else "")
            + f" | {gate} |"
        )
    copy_by_layer = {
        binding.layer_id: binding.copy_id
        for shot in sheet.shots
        for binding in shot.layers
        if binding.copy_id
    }
    lines.extend(
        [
            "",
            "## Layer plan",
            "",
            "| Shot | Layer | Asset | Method | Class | Impact | Pick |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for decision in level2.decisions:
        asset_label = decision.asset_id or (
            f"copy:{copy_by_layer[decision.layer_id]}"
            if decision.layer_id in copy_by_layer
            else "procedural"
        )
        lines.append(
            f"| {decision.shot_id} | `{decision.layer_id}` | {asset_label} | "
            f"{decision.method.value} | {decision.truth_class.value} | "
            f"{decision.impact.value} ({decision.impact_score}) | "
            f"{decision.pick_mode.value} |"
        )
    lines.extend(
        [
            "",
            "## Production notes",
            "",
            "- Supplied brand files and proof captures are non-negotiable; stock and",
            "  generation are not substitutes.",
            "- Stock audio (`AS-10`, `AS-14`) is still a preview until Gate 2A and the",
            "  final licence.",
            "- `AS-15` is a disclosed fallback only; the Edge TTS sample is not an",
            "  approved final voice.",
            "- Every paid provider call is reserved and receipted through the",
            "  provider governor.",
            "",
        ]
    )
    return "\n".join(lines)


def render_visual_qc(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Asset visual QC",
        "",
        "Agent visual inspection of the available asset files. This checks the",
        "asset itself, not the shot storyboard preview.",
        "",
        "| Asset | Verdict | Reviewer | Note |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['asset_id']}` | {_qc_badge(row['qc_verdict'])} | "
            f"{row['qc_reviewer'] or '—'} | {row['qc_notes'] or '—'} |"
        )
    lines.extend(
        [
            "",
            "## Limits",
            "",
            "- Pending captures cannot be visually reviewed before the shoot.",
            "- Audio assets are marked `n/a`; they need audio QC, not visual QC.",
            "- A `warn` is a review decision, not an automatic rejection.",
            "",
        ]
    )
    return "\n".join(lines)


def write_asset_outputs(
    run: Any,
    run_id: str,
    plan: ProductionPlan,
    level2: Level2Plan,
    sheet: BuildSheet,
    decisions: list[LayerMethodDecision],
) -> dict[str, Any]:
    run_dir = run.run_dir(run_id)
    rows = build_rows(plan, level2, sheet, decisions, run_dir)
    summary = render_asset_summary(plan, rows)
    production = render_production_plan(plan, rows, sheet, level2)
    run.write_text(run_id, "ASSET-SUMMARY.md", summary)
    run.write_text(
        run_id,
        "ASSET-SUMMARY.html",
        markdown_to_html(summary, f"Asset summary - {plan.project_id}"),
    )
    run.write_data(run_id, "ASSET-SUMMARY.json", {"rows": rows})
    run.write_text(run_id, "qc/visual-assets.md", render_visual_qc(rows))
    run.write_text(run_id, "PRODUCTION-PLAN.md", production)
    run.write_text(
        run_id,
        "PRODUCTION-PLAN.html",
        markdown_to_html(production, f"Production plan - {plan.project_id}"),
    )
    return {"rows": rows, "summary": summary, "production": production}
