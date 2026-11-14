"""OpenMontage-backed discovery for a representative film asset.

Search is read-only and pre-Gate 2A: it records Studio's candidates, job id and
ledger state without acquiring or attaching anything. Acquisition remains behind
``sourcing.require_openmontage_gate`` and the provider governor.
"""

from __future__ import annotations

import time
import urllib.request
from pathlib import Path
from typing import Any

from pydantic import Field

from ..models import StrictModel, utc_now
from .mcp_bridge import MCPStdioClient

PRODUCER_ID = "pinconv2-level2"
UA = "PinConv2/0.2 (OpenMontage discovery)"


class OpenMontageCandidate(StrictModel):
    source: str
    item_id: str
    title: str
    creator: str | None = None
    page_url: str | None = None
    preview_url: str | None = None
    preview_path: str | None = None
    licence: str | None = None
    duration_seconds: float | None = None


class OpenMontageSearch(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    project_id: str
    job_id: str
    route: str
    kind: str
    query: str
    candidates: list[OpenMontageCandidate] = Field(default_factory=list)
    budget_usd: float = Field(ge=0)
    spent_usd: float = Field(ge=0)
    note: str = "Search only; no acquisition and no film attachment."
    created_at: str = Field(default_factory=utc_now)


def _wait(client: MCPStdioClient, project_id: str, job_id: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
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


def search_for_asset(
    asset_id: str,
    query: str,
    run_dir: Path,
    run_id: str,
    *,
    route: str = "openverse.stock",
    kind: str = "audio",
    audio_category: str = "music",
    limit: int = 5,
    instrumental: bool = False,
    attempt: str = "1",
    budget_usd: float = 2.0,
) -> OpenMontageSearch:
    run_dir = Path(run_dir)
    if budget_usd <= 0 or budget_usd > 2.0:
        raise ValueError("OpenMontage discovery budget must be within $0-$2")
    client = MCPStdioClient()
    try:
        created = client.call_tool(
            "production",
            {
                "action": "create",
                "requestId": f"pinconv2-l2-discovery-{run_id}-{asset_id}-{attempt}",
                "title": f"PinConv2 discovery {asset_id} {run_id}",
                "intent": (
                    f"Search only for a representative {kind} candidate for {asset_id}. "
                    "Do not acquire, attach, publish or spend. This is discovery for "
                    "Blue Tokai Level 2."
                ),
                "autonomy": "standard",
                "scope": {"kind": "focused", "narration": "none", "music": "none"},
                "budget": {"usd": budget_usd, "credits": None},
            },
        )
        project_id = str(created["projectId"])
        input_id = str(created["inputs"][0]["id"])
        begun = client.call_tool(
            "production",
            {
                "action": "begin",
                "projectId": project_id,
                "producerId": PRODUCER_ID,
                "continuationId": input_id,
                "requestId": f"pinconv2-l2-discovery-begin-{run_id}-{asset_id}-{attempt}",
            },
        )
        access = begun["access"]
        search_input: dict[str, object] = {
            "action": "search",
            "route": route,
            "kind": kind,
            "query": query,
            "limit": limit,
        }
        if kind == "audio":
            search_input["audioCategory"] = audio_category
            search_input["musicUse"] = "commercial"
            if instrumental:
                search_input["instrumental"] = True
        accepted = client.call_tool(
            "invoke",
            {
                "requestId": f"pinconv2-l2-discovery-search-{run_id}-{asset_id}-{attempt}",
                "reference": "tool:media.stock-tool",
                "access": access,
                "input": search_input,
            },
        )
        job = accepted.get("job") or {}
        job_id = str(job.get("id", ""))
        waited = _wait(client, project_id, job_id)
        items = waited.get("result", {}).get("output", {}).get("items", [])
        preview_dir = run_dir / "openmontage" / "candidates"
        preview_dir.mkdir(parents=True, exist_ok=True)
        candidates: list[OpenMontageCandidate] = []
        for index, item in enumerate(items[:limit], start=1):
            preview_url = item.get("previewUrl")
            preview_path = None
            if preview_url:
                suffix = Path(str(preview_url).split("?")[0]).suffix or ".mp3"
                target = preview_dir / f"{asset_id}-{index:02d}{suffix}"
                try:
                    request = urllib.request.Request(str(preview_url), headers={"User-Agent": UA})
                    with urllib.request.urlopen(request, timeout=60) as response:
                        target.write_bytes(response.read(20 * 1024 * 1024))
                    preview_path = target.relative_to(run_dir).as_posix()
                except Exception:
                    preview_path = None
            rights = item.get("rights") or {}
            candidates.append(
                OpenMontageCandidate(
                    source=str(item.get("source", route)),
                    item_id=str(item.get("id", "")),
                    title=str(item.get("title", "untitled")),
                    creator=item.get("creator"),
                    page_url=item.get("pageUrl"),
                    preview_url=preview_url,
                    preview_path=preview_path,
                    licence=rights.get("summary"),
                    duration_seconds=item.get("durationS"),
                )
            )
        production = client.call_tool("production", {"action": "read", "projectId": project_id})
        budget = production.get("budget", {})
        client.call_tool(
            "production",
            {
                "action": "finish",
                "projectId": project_id,
                "producerId": PRODUCER_ID,
                "continuationId": input_id,
                "requestId": f"pinconv2-l2-discovery-finish-{run_id}-{asset_id}-{attempt}",
                "state": "completed",
                "access": access,
            },
        )
        report = OpenMontageSearch(
            asset_id=asset_id,
            project_id=project_id,
            job_id=job_id,
            route=route,
            kind=kind,
            query=query,
            candidates=candidates,
            budget_usd=float(budget.get("usd", 0)),
            spent_usd=float(budget.get("spentUsd", 0)),
        )
        (run_dir / "openmontage-sourcing.json").write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        return report
    finally:
        client.close()
