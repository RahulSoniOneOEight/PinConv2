"""Sourcing runner: find, gate and preview real library assets.

The planner records what should be sourced; this stage actually searches a
direct source, downloads a preview, probes it, applies the licence gate, and
writes a sourcing record. Acquiring the final file into ``sourced/`` still
requires Gate 2A approval.
"""

from __future__ import annotations

import json
import re
import subprocess
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path

from ..store import ProjectStore
from .engines.local import LocalEngine
from .errors import SpendNotAuthorisedError
from .gate2 import evaluate_2a
from .licence_gate import classify_licence, gate_candidate
from .models import (
    AssetSourcing,
    GatePacket,
    LicenceClass,
    MethodCandidate,
    PacketStatus,
    ProviderSpendSummary,
    QcReport,
    SourcingCandidate,
    SourcingReport,
)
from .store import Level2RunStore

_UA = "PinConv2/0.1 (production planning; local operator)"
_MAX_BYTES = 30 * 1024 * 1024

Fetcher = Callable[[str], list[dict[str, object]]]
Downloader = Callable[[str, Path], Path]


def require_openmontage_gate(gate: GatePacket | None) -> None:
    """OpenMontage stock/render work is film sourcing, so it needs Gate 2A."""

    if gate is None or gate.status is not PacketStatus.APPROVED:
        raise SpendNotAuthorisedError(
            "OpenMontage stock or render work needs an approved Gate 2A"
        )


DEFAULT_QUERIES = {
    "AS-10": "coffee acoustic instrumental",
    "AS-14": "warm ambient instrumental",
}

_VOCAL_TAGS = ("vocal", "pell", "spoken", "acappella", "acapella")


def _fetch_ccmixter(query: str, limit: int = 5) -> list[dict[str, object]]:
    url = (
        "https://ccmixter.org/api/query?f=json&lic=by&limit="
        f"{limit}&search={urllib.parse.quote(query)}"
    )
    request = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload if isinstance(payload, list) else []


def _download(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; PinConv2/0.1)",
            "Referer": "https://ccmixter.org/",
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read(_MAX_BYTES + 1)
    if len(data) > _MAX_BYTES:
        raise ValueError(f"preview is larger than {_MAX_BYTES} bytes")
    destination.write_bytes(data)
    return destination


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:60] or "candidate"


def _is_vocal(title: str, tags: str) -> bool:
    text = f"{title} {tags}".lower()
    if "instrumental" in text:
        return False
    return any(tag in text for tag in _VOCAL_TAGS)


def _fit_score(title: str, tags: str, duration: float | None) -> int:
    text = f"{title} {tags}".lower()
    score = 50
    if "instrumental" in text or not any(tag in text for tag in _VOCAL_TAGS):
        score += 15
    if "instrumental" in text:
        score += 5
    if any(word in text for word in ("warm", "acoustic", "coffee", "chill", "ambient")):
        score += 10
    if duration is not None and duration >= 15:
        score += 10
    if "loop" in text:
        score += 5
    score += 5  # direct source, not an aggregator
    return min(score, 100)


def _licence_label(licence_url: str, licence_name: str) -> str:
    url = licence_url.lower()
    if "/by/4.0" in url:
        return "CC BY 4.0"
    if "/by/3.0" in url:
        return "CC BY 3.0"
    if "cc0" in url:
        return "CC0"
    return licence_name or "CC BY"


def collect_candidates(
    asset_id: str,
    query: str,
    preview_dir: Path,
    *,
    limit: int = 5,
    fetch: Fetcher = _fetch_ccmixter,
    download: Downloader = _download,
    engine: LocalEngine | None = None,
) -> list[SourcingCandidate]:
    engine = engine or LocalEngine()
    candidates: list[SourcingCandidate] = []
    items = fetch(f"{query}")[:limit]
    for index, item in enumerate(items, start=1):
        title = str(item.get("upload_name", "")).strip()
        tags = str(item.get("upload_tags", "")).strip()
        creator = str(item.get("user_name", "")).strip() or "unknown"
        page_url = str(item.get("file_page_url", "")).strip()
        licence_url = str(item.get("license_url", "")).strip()
        licence_name = str(item.get("license_name", "")).strip()
        files = item.get("files") or []
        file_url = None
        if isinstance(files, list) and files and isinstance(files[0], dict):
            file_url = str(files[0].get("download_url") or "") or None
        if not title or not page_url:
            continue
        if _is_vocal(title, tags):
            continue
        licence = classify_licence(f"{licence_name} {licence_url}")
        if licence in {
            LicenceClass.BLOCKED,
            LicenceClass.CC_BY_NC,
            LicenceClass.CC_BY_ND,
            LicenceClass.CC_BY_SA,
            LicenceClass.UNKNOWN,
        }:
            continue
        candidate_id = f"CND-{asset_id.replace('-', '')}-{index:02d}"
        preview: Path | None = None
        duration: float | None = None
        version = _licence_label(licence_url, licence_name)
        attribution = f'"{title}" by {creator} ({version})'
        method_candidate = MethodCandidate(
            candidate_id=candidate_id,
            asset_id=asset_id,
            provider="ccmixter",
            url=page_url,
            licence_class=licence,
            licence_url=licence_url or None,
            attribution=attribution,
            origin_verified=True,
            scriptable=True,
            fit_score=_fit_score(title, tags, duration),
            cost_usd=0.0,
            preview_path=str(preview) if preview else None,
        )
        gated = gate_candidate(method_candidate)
        candidates.append(
            SourcingCandidate(
                candidate_id=gated.candidate_id,
                asset_id=asset_id,
                provider=gated.provider,
                title=title,
                creator=creator,
                page_url=gated.url,
                file_url=file_url,
                licence_class=gated.licence_class,
                licence_url=gated.licence_url,
                attribution=gated.attribution,
                duration_seconds=duration,
                preview_path=gated.preview_path,
                fit_score=gated.fit_score,
                gate_verdict=gated.gate_verdict,
                gate_reasons=gated.gate_reasons,
                scriptable=gated.scriptable,
            )
        )
    candidates.sort(key=lambda item: item.fit_score, reverse=True)
    for source_candidate in list(candidates):
        if not source_candidate.file_url:
            continue
        suffix = (
            Path(urllib.parse.urlparse(source_candidate.file_url).path).suffix or ".mp3"
        )
        target = preview_dir / (
            f"{source_candidate.candidate_id}-{_slug(source_candidate.title)}{suffix}"
        )
        try:
            if not target.is_file():
                if suffix.lower() == ".mp3":
                    full = preview_dir / (
                        f"{source_candidate.candidate_id}-"
                        f"{_slug(source_candidate.title)}-full.mp3"
                    )
                    download(source_candidate.file_url, full)
                    subprocess.run(
                        [
                            "ffmpeg",
                            "-y",
                            "-i",
                            str(full),
                            "-t",
                            "20",
                            "-ac",
                            "1",
                            "-b:a",
                            "96k",
                            str(target),
                        ],
                        check=True,
                        capture_output=True,
                    )
                    full.unlink(missing_ok=True)
                else:
                    download(source_candidate.file_url, target)
            duration = None
            if engine.available:
                duration = engine.probe(target).duration_seconds
            update: dict[str, object] = {"preview_path": f"sourcing/{target.name}"}
            if duration is not None:
                update["duration_seconds"] = duration
                if duration >= 15:
                    update["fit_score"] = min(source_candidate.fit_score + 10, 100)
            candidates[candidates.index(source_candidate)] = source_candidate.model_copy(
                update=update
            )
        except Exception:
            continue
    candidates.sort(key=lambda item: item.fit_score, reverse=True)
    return candidates


def _read_reports(run: Level2RunStore, run_id: str) -> dict[str, QcReport]:
    reports: dict[str, QcReport] = {}
    for stage in ("technical", "semantic", "rights", "budget", "visual"):
        path = run.run_dir(run_id) / "qc" / f"{stage}.json"
        if path.is_file():
            reports[stage] = QcReport.model_validate_json(path.read_text(encoding="utf-8"))
    return reports


def _provider(run: Level2RunStore, run_id: str) -> ProviderSpendSummary | None:
    path = run.run_dir(run_id) / "provider-spend.json"
    if not path.is_file():
        return None
    return ProviderSpendSummary.model_validate_json(path.read_text(encoding="utf-8"))


def source_assets(
    store: ProjectStore,
    project_id: str,
    revision: int,
    run_id: str,
    *,
    queries: dict[str, str] | None = None,
    limit: int = 5,
    fetch: Fetcher = _fetch_ccmixter,
    download: Downloader = _download,
) -> SourcingReport:
    run = Level2RunStore(store.project_dir(project_id))
    level2 = run.read_level2(run_id)
    plan = store.load_plan(project_id, revision)
    query_map = {**DEFAULT_QUERIES, **(queries or {})}
    preview_dir = run.run_dir(run_id) / "sourcing"

    assets: list[AssetSourcing] = []
    used_pages: set[str] = set()
    for asset_id, query in query_map.items():
        if asset_id not in plan.asset_map:
            continue
        candidates = collect_candidates(
            asset_id, query, preview_dir, limit=limit, fetch=fetch, download=download
        )
        chosen = next(
            (
                item.candidate_id
                for item in candidates
                if item.gate_verdict.value == "pass" and item.page_url not in used_pages
            ),
            None,
        )
        if chosen is not None:
            chosen_item = next(
                item for item in candidates if item.candidate_id == chosen
            )
            used_pages.add(chosen_item.page_url)
        assets.append(
            AssetSourcing(
                asset_id=asset_id,
                query=query,
                status="discovered" if candidates else "empty",
                candidates=candidates,
                chosen_candidate=chosen,
                note=(
                    "Candidates are previews only; final acquisition needs Gate 2A."
                    if candidates
                    else "No commercial-use candidate passed the licence gate."
                ),
            )
        )

    report = SourcingReport(run_id=run_id, assets=assets)
    run.write_data(
        run_id,
        "asset-sourcing.json",
        report.model_dump(mode="json"),
    )
    updated = level2.model_copy(update={"sourcing": report})
    run.write_json(run_id, "run.json", updated)

    sheet = run.read_build_sheet(run_id)
    packet = evaluate_2a(
        plan,
        updated,
        sheet,
        updated.decisions,
        _read_reports(run, run_id),
        expected_bundle_hash=sheet.manifest.bundle_hash,
        expected_packet_hash=sheet.manifest.packet_hash,
        provider_summary=_provider(run, run_id),
    )
    run.write_json(run_id, "gate2/packet-2a.json", packet)
    run.write_text(run_id, "sourcing-report.md", render_sourcing(report))
    run.append_event(
        run_id,
        "level2.sourced",
        {
            "assets": len(report.assets),
            "candidates": sum(len(asset.candidates) for asset in report.assets),
            "gate2a": packet.status.value,
        },
    )
    return report


def render_sourcing(report: SourcingReport) -> str:
    lines = [
        "# Sourcing report",
        "",
        "Previews only. Final acquisition still needs an approved Gate 2A.",
        "",
        "| Asset | Query | Status | Candidates | Chosen |",
        "|---|---|---|---|---|",
    ]
    for asset in report.assets:
        lines.append(
            f"| {asset.asset_id} | {asset.query} | {asset.status} | "
            f"{len(asset.candidates)} | {asset.chosen_candidate or '—'} |"
        )
    for asset in report.assets:
        lines.extend(["", f"## {asset.asset_id}", ""])
        if not asset.candidates:
            lines.append("No candidate passed the licence gate.")
            continue
        lines.extend(
            [
                "| Candidate | Title | Creator | Licence | Duration | Fit | Gate | Preview |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        for item in asset.candidates:
            duration = f"{item.duration_seconds:.1f}s" if item.duration_seconds else "—"
            lines.append(
                f"| {item.candidate_id} | {item.title} | {item.creator} | "
                f"{item.licence_class.value} | {duration} | {item.fit_score} | "
                f"{item.gate_verdict.value} | "
                + (f"[preview]({item.preview_path})" if item.preview_path else "—")
            )
        chosen = next(
            (item for item in asset.candidates if item.candidate_id == asset.chosen_candidate),
            None,
        )
        if chosen is not None:
            lines.extend(
                [
                    "",
                    f"Chosen: **{chosen.title}** by {chosen.creator}.",
                    f"Attribution: {chosen.attribution}",
                    f"Source: {chosen.page_url}",
                ]
            )
    lines.append("")
    return "\n".join(lines)
