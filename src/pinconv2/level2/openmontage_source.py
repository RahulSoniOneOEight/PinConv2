"""OpenMontage-backed discovery for a representative film asset.

Search is read-only and pre-Gate 2A: it records Studio's candidates, job id and
ledger state without acquiring or attaching anything. Acquisition and generation
remain behind ``OpenMontageEngine``'s Gate 2A / spend-ledger checks.
"""

from __future__ import annotations

import hashlib
import time
import urllib.request
from pathlib import Path
from typing import Any

from pydantic import Field

from ..models import StrictModel, utc_now
from .mcp_bridge import MCPStdioClient

PRODUCER_ID = "pinconv2-level2"
UA = "PinConv2/0.2 (OpenMontage discovery)"
MAX_PREVIEW_BYTES = 20 * 1024 * 1024

_MAGIC = (
    b"\xff\xd8\xff",  # JPEG
    b"\x89PNG\r\n\x1a\n",  # PNG
    b"GIF87a",
    b"GIF89a",
    b"RIFF",  # WebP/WAV
    b"ID3",  # MP3
    b"OggS",
    b"\x1aE\xdf\xa3",  # WebM/Matroska
)


def _looks_like_media(payload: bytes) -> bool:
    return len(payload) >= 1024 and any(payload.startswith(magic) for magic in _MAGIC)


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
    bytes: int = Field(default=0, ge=0)
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")


class OpenMontageSearch(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    project_id: str
    job_id: str
    request_id: str | None = None
    attempt: str = "1"
    status: str = "completed"
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
            preview_bytes = 0
            preview_sha = None
            if preview_url:
                suffix = Path(str(preview_url).split("?")[0]).suffix or ".jpg"
                target = preview_dir / f"{asset_id}-{index:02d}{suffix}"
                try:
                    request = urllib.request.Request(str(preview_url), headers={"User-Agent": UA})
                    with urllib.request.urlopen(request, timeout=60) as response:
                        payload = response.read(MAX_PREVIEW_BYTES + 1)
                    if len(payload) <= MAX_PREVIEW_BYTES and _looks_like_media(payload):
                        target.write_bytes(payload)
                        preview_path = target.relative_to(run_dir).as_posix()
                        preview_bytes = len(payload)
                        preview_sha = hashlib.sha256(payload).hexdigest()
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
                    bytes=preview_bytes,
                    sha256=preview_sha,
                )
            )
        production = client.call_tool("production", {"action": "read", "projectId": project_id})
        budget = production.get("budget", {})
        finished = client.call_tool(
            "production",
            {
                "action": "finish",
                "requestId": f"pinconv2-l2-discovery-finish-{run_id}-{asset_id}-{attempt}",
                "state": "completed",
                "access": access,
            },
        )
        if finished.get("finished") != "completed":
            raise RuntimeError(f"OpenMontage finish did not complete: {finished}")
        status = str(waited.get("state", "unknown"))
        report = OpenMontageSearch(
            asset_id=asset_id,
            project_id=project_id,
            job_id=job_id,
            request_id=f"pinconv2-l2-discovery-search-{run_id}-{asset_id}-{attempt}",
            attempt=attempt,
            status=status,
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
