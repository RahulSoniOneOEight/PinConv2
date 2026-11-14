"""End-to-end OpenMontage capability check through the MCP bridge.

Creates a separate $2 production, acquires one no-key NASA stock image through
Studio's ledger, renders a 2-second HyperFrames composition, copies both into the
Level 2 run, and records the receipts. It never attaches anything to the Blue
Tokai film.
"""

from __future__ import annotations

import hashlib
import shutil
import time
from pathlib import Path
from typing import Any

from ..models import StrictModel
from .errors import SpendNotAuthorisedError
from .mcp_bridge import MCPStdioClient
from .models import GatePacket, PacketStatus

PRODUCER_ID = "pinconv2-level2"


class OpenMontageCheck(StrictModel):
    project_id: str
    production_root: str
    stock_title: str
    stock_sha256: str
    stock_reference: str
    stock_local_copy: str | None = None
    render_reference: str
    render_local_copy: str | None = None
    render_sha256: str
    render_bytes: int
    render_duration_seconds: float
    render_verification: str
    budget_usd: float
    spent_usd: float
    note: str = "Capability test only; not attached to the Blue Tokai production."


def _wait(client: MCPStdioClient, project_id: str, job_id: str) -> dict[str, Any]:
    for _ in range(4):
        result = client.call_tool(
            "jobs",
            {
                "action": "wait",
                "projectId": project_id,
                "jobId": job_id,
                "waitMs": 30000,
            },
        )
        if result.get("state") in {"completed", "failed", "cancelled", "interrupted"}:
            return result
        time.sleep(1)
    return result


def _invoke(
    client: MCPStdioClient,
    project_id: str,
    access: dict[str, str],
    request_id: str,
    reference: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    accepted = client.call_tool(
        "invoke",
        {
            "requestId": request_id,
            "reference": reference,
            "access": access,
            "input": payload,
        },
    )
    job = accepted.get("job") or {}
    job_id = job.get("id")
    if not job_id:
        raise RuntimeError(f"invoke did not return a job: {accepted}")
    return _wait(client, project_id, job_id)


def run_openmontage_check(
    run_dir: Path,
    run_id: str,
    *,
    query: str = "coffee",
    budget_usd: float = 2.0,
    gate: GatePacket | None = None,
    capability_check: bool = False,
) -> OpenMontageCheck:
    if gate is not None:
        if gate.status is not PacketStatus.APPROVED:
            raise SpendNotAuthorisedError(
                "OpenMontage stock or render work needs an approved Gate 2A"
            )
    elif not capability_check:
        raise SpendNotAuthorisedError(
            "OpenMontage work needs Gate 2A, or an explicit no-key capability check"
        )
    if capability_check and budget_usd > 2.0:
        raise SpendNotAuthorisedError("the capability check is bounded to the $2 operator cap")
    run_dir = Path(run_dir)
    copy_dir = run_dir / "openmontage"
    copy_dir.mkdir(parents=True, exist_ok=True)
    client = MCPStdioClient()
    try:
        created = client.call_tool(
            "production",
            {
                "action": "create",
                "requestId": f"pinconv2-l2-om-check-{run_id}",
                "title": f"PinConv2 Level 2 OpenMontage check {run_id}",
                "intent": (
                    "Capability check: acquire one no-key NASA stock image and render "
                    "a 2-second HyperFrames composition. Not for publication, not part "
                    "of the Blue Tokai film, no paid generation."
                ),
                "autonomy": "standard",
                "scope": {"kind": "focused", "narration": "none", "music": "none"},
                "budget": {"usd": budget_usd, "credits": None},
            },
        )
        project_id = str(created["projectId"])
        input_id = str(created["inputs"][0]["id"])
        root = Path(str(created["root"]))
        begun = client.call_tool(
            "production",
            {
                "action": "begin",
                "projectId": project_id,
                "producerId": PRODUCER_ID,
                "continuationId": input_id,
                "requestId": f"pinconv2-l2-om-begin-{run_id}",
            },
        )
        access = begun["access"]

        search = _invoke(
            client,
            project_id,
            access,
            f"pinconv2-l2-om-stock-search-{run_id}",
            "tool:media.stock-tool",
            {
                "action": "search",
                "route": "nasa.stock",
                "kind": "image",
                "query": query,
                "limit": 3,
            },
        )
        items = search.get("result", {}).get("output", {}).get("items", [])
        if not items:
            raise RuntimeError("NASA stock search returned no items")
        item = items[0]
        details = _invoke(
            client,
            project_id,
            access,
            f"pinconv2-l2-om-stock-details-{run_id}",
            "tool:media.stock-tool",
            {
                "action": "details",
                "route": "nasa.stock",
                "kind": "image",
                "id": item["id"],
            },
        )
        detail_items = details.get("result", {}).get("output", {}).get("items", [])
        renditions = detail_items[0].get("renditions", []) if detail_items else []
        medium = next(
            (entry for entry in renditions if "medium" in str(entry.get("id"))),
            renditions[0] if renditions else None,
        )
        if medium is None:
            raise RuntimeError("NASA item has no delivery rendition")

        acquired = _invoke(
            client,
            project_id,
            access,
            f"pinconv2-l2-om-stock-acquire-{run_id}",
            "tool:media.stock-tool",
            {
                "action": "acquire",
                "route": "nasa.stock",
                "kind": "image",
                "id": item["id"],
                "rendition": medium["id"],
                "usage": "PinConv2 Level 2 capability check; not for publication",
            },
        )
        asset = acquired.get("result", {}).get("output", {}).get("asset", {})
        attached = _invoke(
            client,
            project_id,
            access,
            f"pinconv2-l2-om-stock-attach-{run_id}",
            "tool:media.stock-tool",
            {
                "action": "attach",
                "id": asset.get("id"),
                "usage": "PinConv2 Level 2 capability check; not for publication",
            },
        )
        attach_result = attached.get("result", {})
        project_import = attach_result.get("projectImport") or (
            attach_result.get("output", {}).get("projectImport", {})
        )
        imported = (project_import.get("items") or [{}])[0]
        stock_reference = str(imported.get("reference", ""))
        stock_copy = None
        stock_hash = str(asset.get("id", ""))
        if stock_reference.startswith("project:"):
            source = root / stock_reference.removeprefix("project:")
            if source.is_file():
                target = copy_dir / "nasa-stock.jpg"
                shutil.copyfile(source, target)
                stock_copy = str(target)
                stock_hash = hashlib.sha256(target.read_bytes()).hexdigest()

        composition = f"project:scenes/om-check-{run_id}"
        _invoke(
            client,
            project_id,
            access,
            f"pinconv2-l2-om-scaffold-{run_id}",
            "tool:composition.scaffold-tool",
            {"outputDirectory": composition, "resolution": "landscape"},
        )
        source_reference = f"{composition}/index.html"
        read = client.call_tool(
            "workspace",
            {
                "projectId": project_id,
                "operation": {
                    "action": "read-source",
                    "reference": source_reference,
                },
            },
        )
        html = """<!DOCTYPE html>
<html lang="en" data-resolution="landscape">
  <head><meta charset="UTF-8"><style>
    * { margin:0; padding:0; box-sizing:border-box; }
    html, body { width:1920px; height:1080px; overflow:hidden; background:#0B0604; }
    #root { width:100%; height:100%; display:flex; align-items:center;
             justify-content:center; font-family:Inter, system-ui, sans-serif; }
    #title { color:#F7F3EC; font-size:76px; font-weight:600; letter-spacing:-0.03em; }
    #sub { color:#C98A55; font-size:30px; font-weight:500; margin-top:20px; }
    .wrap { text-align:center; }
  </style></head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="2"
         data-width="1920" data-height="1080" data-edit-fps="30/1">
      <div class="wrap">
        <div id="title" class="clip" data-start="0" data-duration="2"
             data-track-index="0">PinConv2 × OpenMontage</div>
        <div id="sub" class="clip" data-start="0" data-duration="2"
             data-track-index="1">local render check · no spend</div>
      </div>
    </div>
    <script>window.__timelines = { main: { seek() {}, play() {}, pause() {} } };</script>
  </body>
</html>"""
        client.call_tool(
            "workspace",
            {
                "requestId": f"pinconv2-l2-om-write-{run_id}",
                "access": access,
                "operation": {
                    "action": "write-source",
                    "reference": source_reference,
                    "expectedSha256": read["sha256"],
                    "text": html,
                },
            },
        )

        render_reference = f"project:deliverables/om-check-{run_id}.mp4"
        rendered = _invoke(
            client,
            project_id,
            access,
            f"pinconv2-l2-om-render-{run_id}",
            "tool:composition.render-tool",
            {
                "composition": composition,
                "projectRoot": "project:.",
                "output": render_reference,
                "quality": "draft",
                "fps": 30,
            },
        )
        output = rendered.get("result", {}).get("output", {})
        render_copy = None
        if str(output.get("path", "")).startswith("project:"):
            source = root / str(output["path"]).removeprefix("project:")
            if source.is_file():
                target = copy_dir / "render.mp4"
                shutil.copyfile(source, target)
                render_copy = str(target)

        production = client.call_tool("production", {"action": "read", "projectId": project_id})
        budget = production.get("budget", {})
        finished = client.call_tool(
            "production",
            {
                "action": "finish",
                "requestId": f"pinconv2-l2-om-finish-{run_id}",
                "state": "completed",
                "access": access,
            },
        )
        if finished.get("finished") != "completed":
            raise RuntimeError(f"OpenMontage finish did not complete: {finished}")
        check = OpenMontageCheck(
            project_id=project_id,
            production_root=str(root),
            stock_title=str(item.get("title", "")),
            stock_sha256=stock_hash,
            stock_reference=stock_reference,
            stock_local_copy=stock_copy,
            render_reference=render_reference,
            render_local_copy=render_copy,
            render_sha256=str(output.get("sha256", "")),
            render_bytes=int(output.get("bytes", 0)),
            render_duration_seconds=float(output.get("facts", {}).get("duration_s", 0)),
            render_verification=str(
                rendered.get("result", {}).get("verification", {}).get("status", "")
            ),
            budget_usd=float(budget.get("usd", 0)),
            spent_usd=float(budget.get("spentUsd", 0)),
        )
        (run_dir / "openmontage-check.json").write_text(
            check.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        return check
    finally:
        client.close()
