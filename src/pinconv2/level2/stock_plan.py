"""Stock-first asset sourcing plan with an AI-generation share guard.

Level 2's main job is to turn the detailed brief into assets from the shared
stock sources (image, video, icon, sound). The rule for this project:

- original AI asset generation is capped at 40% of assets;
- everything else is licensed stock, processed with AI where needed.

This module builds the per-asset stock route, fetches a real candidate where a
key is available, and writes a reviewable plan plus an AI-share verdict.
"""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from pydantic import Field

from ..models import ProductionPlan, StrictModel
from .credentials import provider_key
from .models import Level2Plan

AI_GENERATION_MAX_PCT = 0.40
UA = "PinConv2/0.3 (stock plan)"

_STOCK_ROUTES = {
    "AS-05": ("pexels", "video", "pouring coffee hands"),
    "AS-06": ("pexels", "video", "pouring hot water coffee bloom"),
    "AS-07": ("pexels", "image", "warm kitchen coffee background"),
    "AS-08": ("pexels", "image", "cup of coffee on table"),
    "AS-09": ("generate", "voice", "warm Indian English narration"),
    "AS-10": ("ccmixter", "music", "coffee acoustic instrumental"),
    "AS-11": ("freesound", "sound", "water pouring"),
    "AS-12": ("generate", "sound", "brand sting"),
    "AS-13": ("supplied", "image", "use AS-02 pack image"),
    "AS-14": ("ccmixter", "music", "warm ambient instrumental"),
    "AS-15": ("generate", "voice", "synthetic narration fallback"),
}

_GROUP_BY_PROVIDER = {
    "generate": "generate",
    "supplied": "supplied",
    "ccmixter": "stock",
    "pexels": "stock",
    "freesound": "stock",
}

# Explore several sources per asset type; the best fit is used, the rest are backups.
SOURCE_MATRIX: dict[str, list[str]] = {
    "image": ["pexels", "unsplash", "openverse", "wikimedia"],
    "video": ["pexels", "wikimedia", "internet-archive"],
    "sound": ["freesound", "openverse", "wikimedia", "internet-archive"],
    "music": ["ccmixter"],
}


def _fit_score(kind: str, licence: str | None, probe: dict[str, Any]) -> int:
    score = 0
    width = int(probe.get("width") or 0)
    duration = float(probe.get("duration_seconds") or 0)
    if kind == "image":
        if width >= 1600:
            score += 40
        elif width >= 640:
            score += 25
        else:
            score += 10
    elif kind == "video":
        if width >= 1280:
            score += 40
        elif width >= 640:
            score += 25
        else:
            score += 10
        if duration >= 5:
            score += 20
    else:
        if duration >= 15:
            score += 40
        elif duration >= 5:
            score += 25
        else:
            score += 10
    upper = (licence or "").upper()
    if "CC0" in upper or "PD" in upper or "PUBLIC DOMAIN" in upper:
        score += 15
    elif "CC-BY" in upper or "CC BY" in upper:
        score += 10
    elif "PEXELS" in upper or "UNSPLASH" in upper:
        score += 8
    return score


class StockRoute(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    name: str
    kind: str
    provider: str
    query: str
    group: str = Field(pattern=r"^(supplied|stock|generate)$")
    note: str = ""


class StockCandidate(StrictModel):
    asset_id: str
    provider: str
    kind: str = Field(default="", max_length=20)
    title: str
    creator: str | None = None
    licence: str | None = None
    page_url: str | None = None
    file_path: str | None = None
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    bytes: int = Field(default=0, ge=0)
    fit_score: int = Field(default=0, ge=0)
    used: bool = False
    evaluation: str = Field(default="", max_length=500)


class StockPlan(StrictModel):
    routes: list[StockRoute] = Field(min_length=1)
    candidates: list[StockCandidate] = Field(default_factory=list)
    total: int = Field(ge=0)
    supplied: int = Field(ge=0)
    stock: int = Field(ge=0)
    generated: int = Field(ge=0)
    ai_share_pct: float = Field(ge=0)
    within_ai_cap: bool


def build_stock_plan(plan: ProductionPlan, level2: Level2Plan) -> StockPlan:
    intent_map = {intent.asset_id: intent for intent in level2.intents}
    routes: list[StockRoute] = []
    for asset_id in sorted(level2.task_map()):
        intent = intent_map.get(asset_id)
        if intent is None:
            continue
        route = intent.route.value if hasattr(intent.route, "value") else str(intent.route)
        provider, kind, query = _STOCK_ROUTES.get(asset_id, (route, "image", intent.specification))
        group = _GROUP_BY_PROVIDER.get(provider, "stock")
        note = ""
        if intent.truth_class.value in {"exact", "exact_text"}:
            provider, group, note = "supplied", "supplied", "exact brand file stays supplied"
        elif provider == "generate":
            note = "AI-generated with disclosure; counted against the 40% cap"
        else:
            note = "licensed stock, AI-processed as needed"
        routes.append(
            StockRoute(
                asset_id=asset_id,
                name=intent.name,
                kind=kind,
                provider=provider,
                query=query,
                group=group,
                note=note,
            )
        )
    supplied = sum(1 for route in routes if route.group == "supplied")
    stock = sum(1 for route in routes if route.group == "stock")
    generated = sum(1 for route in routes if route.group == "generate")
    total = len(routes)
    ai_share_pct = round(generated / total * 100, 1) if total else 0.0
    return StockPlan(
        routes=routes,
        total=total,
        supplied=supplied,
        stock=stock,
        generated=generated,
        ai_share_pct=ai_share_pct,
        within_ai_cap=ai_share_pct <= AI_GENERATION_MAX_PCT * 100,
    )


def _get(url: str, headers: dict[str, str] | None = None) -> tuple[int, bytes]:
    request = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.status, response.read()


def _json(url: str, headers: dict[str, str] | None = None) -> tuple[int, Any]:
    status, body = _get(url, headers)
    return status, json.loads(body.decode("utf-8"))


def _download(url: str, destination: Path, headers: dict[str, str] | None = None) -> Path:
    status, body = _get(url, headers)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(body)
    return destination


def _record(
    asset_id: str,
    provider: str,
    *,
    title: str,
    creator: str | None,
    licence: str | None,
    page_url: str | None,
    path: Path | None,
) -> StockCandidate:
    payload = path.read_bytes() if path is not None else b""
    return StockCandidate(
        asset_id=asset_id,
        provider=provider,
        title=title[:300],
        creator=creator,
        licence=licence,
        page_url=page_url,
        file_path=str(path) if path is not None else None,
        sha256=hashlib.sha256(payload).hexdigest() if payload else None,
        bytes=len(payload),
    )


def fetch_stock_candidate(
    asset_id: str, provider: str, kind: str, query: str, run_dir: Path
) -> StockCandidate | None:
    """Fetch one real candidate for a stock route; None when no key or no result."""

    destination = run_dir / "stock-candidates"
    if provider == "pexels":
        key = provider_key("PEXELS_API_KEY")
        if not key:
            return None
        endpoint = "videos/search" if kind == "video" else "v1/search"
        status, payload = _json(
            f"https://api.pexels.com/{endpoint}?query={urllib.parse.quote(query)}&per_page=1",
            {"Authorization": key},
        )
        if kind == "video":
            videos = payload.get("videos", []) if isinstance(payload, dict) else []
            if not videos:
                return None
            item = videos[0]
            files = sorted(
                item.get("video_files", []), key=lambda entry: int(entry.get("width") or 0)
            )
            link = files[0].get("link") if files else None
            if not link:
                return None
            path = _download(link, destination / f"{asset_id}.mp4")
            return _record(
                asset_id,
                provider,
                title=f"Pexels video {item.get('id')}",
                creator=item.get("user", {}).get("name"),
                licence="Pexels License",
                page_url=item.get("url"),
                path=path,
            )
        photos = payload.get("photos", []) if isinstance(payload, dict) else []
        if not photos:
            return None
        item = photos[0]
        src = item.get("src") or {}
        link = src.get("large2x") or src.get("large") or src.get("medium")
        if not link:
            return None
        path = _download(link, destination / f"{asset_id}.jpg")
        return _record(
            asset_id,
            provider,
            title=f"Pexels photo {item.get('id')}",
            creator=item.get("photographer"),
            licence="Pexels License",
            page_url=item.get("url"),
            path=path,
        )
    if provider == "unsplash":
        key = provider_key("UNSPLASH_ACCESS_KEY")
        if not key:
            return None
        status, payload = _json(
            f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(query)}&per_page=1",
            {"Authorization": f"Client-ID {key}"},
        )
        results = payload.get("results", []) if isinstance(payload, dict) else []
        if not results:
            return None
        item = results[0]
        urls = item.get("urls") or {}
        link = urls.get("regular") or urls.get("small")
        if not link:
            return None
        path = _download(link, destination / f"{asset_id}.jpg")
        return _record(
            asset_id,
            provider,
            title=item.get("description") or item.get("alt_description") or "Unsplash photo",
            creator=(item.get("user") or {}).get("name"),
            licence="Unsplash License",
            page_url=(item.get("links") or {}).get("html"),
            path=path,
        )
    if provider == "freesound":
        key = provider_key("FREESOUND_API_KEY")
        if not key:
            return None
        status, payload = _json(
            "https://freesound.org/apiv2/search/text/?query="
            f"{urllib.parse.quote(query)}&fields=id,name,license,username,previews",
            {"Authorization": f"Token {key}"},
        )
        results = payload.get("results", []) if isinstance(payload, dict) else []
        if not results:
            return None
        item = results[0]
        previews = item.get("previews") or {}
        link = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
        if not link:
            return None
        path = _download(link, destination / f"{asset_id}.mp3")
        return _record(
            asset_id,
            provider,
            title=item.get("name"),
            creator=item.get("username"),
            licence=str(item.get("license")),
            page_url=f"https://freesound.org/s/{item.get('id')}/",
            path=path,
        )
    return None


def _stockcheck_fetch(
    asset_id: str, provider: str, kind: str, query: str, run_dir: Path
) -> StockCandidate | None:
    from . import stockcheck as sc

    root = run_dir / "stock-candidates"
    media_type = "video" if kind == "video" else "audio" if kind in {"sound", "music"} else "image"
    if provider == "openverse":
        item = sc._openverse(media_type, query, root)
    elif provider == "wikimedia":
        item = sc._wikimedia(media_type, query, root)
    elif provider == "internet-archive":
        item = sc._archive(media_type, query, root)
    elif provider == "nasa":
        item = sc._nasa_image(query, root)
    else:
        return None
    if item.status != "ok" or item.file_path is None:
        return None
    probe = item.probe or {}
    candidate = StockCandidate(
        asset_id=asset_id,
        provider=provider,
        kind=kind,
        title=item.title or "untitled",
        creator=item.creator,
        licence=item.licence_class or item.licence,
        page_url=item.page_url,
        file_path=item.file_path,
        sha256=item.sha256,
        bytes=item.bytes,
    )
    candidate = candidate.model_copy(
        update={"fit_score": _fit_score(kind, candidate.licence, probe)}
    )
    if item.licence_class in {"CC-BY-SA", "CC-BY-NC", "CC-BY-ND", "UNKNOWN"} or not item.paid_ok:
        candidate = candidate.model_copy(
            update={
                "evaluation": "excluded: licence not paid-ok or unresolved",
                "fit_score": 0,
            }
        )
    return candidate


def _finalize(candidate: StockCandidate, kind: str) -> StockCandidate:
    from .engines.local import LocalEngine

    candidate = candidate.model_copy(update={"kind": kind})
    if not candidate.file_path or not Path(candidate.file_path).is_file():
        return candidate
    try:
        probe = LocalEngine().probe(Path(candidate.file_path)).model_dump()
    except Exception:
        probe = {}
    if candidate.fit_score == 0 and candidate.provider not in {
        "openverse",
        "wikimedia",
        "internet-archive",
    }:
        candidate = candidate.model_copy(
            update={"fit_score": _fit_score(kind, candidate.licence, probe)}
        )
    return candidate


def fetch_and_rank(asset_id: str, kind: str, query: str, run_dir: Path) -> list[StockCandidate]:
    """Fetch from every source for the asset type; mark the best as used."""

    candidates: list[StockCandidate] = []
    for provider in SOURCE_MATRIX.get(kind, ["pexels"]):
        candidate = None
        if provider in {"pexels", "unsplash", "freesound"}:
            candidate = fetch_stock_candidate(asset_id, provider, kind, query, run_dir)
        else:
            candidate = _stockcheck_fetch(asset_id, provider, kind, query, run_dir)
        if candidate is None:
            continue
        candidate = _finalize(candidate, kind)
        if candidate.evaluation.startswith("excluded"):
            continue
        candidates.append(candidate)
    candidates.sort(key=lambda item: item.fit_score, reverse=True)
    if candidates:
        candidates[0] = candidates[0].model_copy(
            update={"used": True, "evaluation": "best fit — selected"}
        )
        for entry in candidates[1:]:
            entry = entry.model_copy(
                update={
                    "used": False,
                    "evaluation": entry.evaluation or "backup — lower fit or alternate source",
                }
            )
    return candidates


def render_stock_plan(plan: StockPlan) -> str:
    lines = [
        "# Stock sourcing plan with AI-share guard",
        "",
        "Level 2 acquires assets from the shared stock sources; original AI",
        "generation is capped at 40% of assets.",
        "",
        "| Assets | Supplied | Stock | AI-generated | AI share | Within 40% cap |",
        "|---|---|---|---|---|---|",
        f"| {plan.total} | {plan.supplied} | {plan.stock} | {plan.generated} | "
        f"{plan.ai_share_pct}% | {'yes' if plan.within_ai_cap else 'NO'} |",
        "",
        "## Asset routes",
        "",
        "| Asset | What | Kind | Provider | Query | Route | Note |",
        "|---|---|---|---|---|---|---|",
    ]
    for route in plan.routes:
        lines.append(
            f"| `{route.asset_id}` | {route.name} | {route.kind} | {route.provider} | "
            f"{route.query} | {route.group} | {route.note} |"
        )
    if plan.candidates:
        used = [candidate for candidate in plan.candidates if candidate.used]
        backup = [candidate for candidate in plan.candidates if not candidate.used]
        lines.extend(
            [
                "",
                "## Final selected candidates",
                "",
                "| Asset | Provider | Title | Creator | Licence | Fit | Source | File |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        for candidate in used:
            file = Path(candidate.file_path).name if candidate.file_path else "—"
            lines.append(
                f"| {candidate.asset_id} | {candidate.provider} | {candidate.title} | "
                f"{candidate.creator or '—'} | {candidate.licence or '—'} | "
                f"{candidate.fit_score} | {candidate.page_url or '—'} | {file} |"
            )
        lines.extend(
            [
                "",
                f"Backup candidates ({len(backup)}): reported in `ANNEX-SOURCED-NOT-USED.md`.",
                "",
            ]
        )
    else:
        lines.extend(["", "## Final selected candidates", "", "None fetched yet.", ""])
    lines.extend(
        [
            "",
            "## Rules",
            "",
            "- exact product/pack/logo stays supplied; never stock or generated.",
            "- Pexels and Unsplash are both fetched and scored for every image asset;",
            "  the higher fit is selected and the other is reported as a backup.",
            "- AI generation is only for voice, sting and disclosed fallbacks, and",
            "  stays within 40% of assets.",
            "- Stock assets may be AI-processed (grade, upscale, relight, retime);",
            "  processing is not generation and does not count against the 40%.",
            "",
        ]
    )
    return "\n".join(lines)


def render_annex(candidates: list[StockCandidate]) -> str:
    lines = [
        "# Annex — sourced but not used",
        "",
        "Candidates that were fetched and evaluated but not selected. Each shows",
        "why it was kept as a backup.",
        "",
        "| Asset | Provider | Title | Licence | Fit | Why not used |",
        "|---|---|---|---|---|---|",
    ]
    for candidate in candidates:
        if candidate.used:
            continue
        lines.append(
            f"| {candidate.asset_id} | {candidate.provider} | {candidate.title} | "
            f"{candidate.licence or '—'} | {candidate.fit_score} | "
            f"{candidate.evaluation or 'backup'} |"
        )
    if not any(not candidate.used for candidate in candidates):
        lines.append("| — | — | no backups were sourced | — | — | — |")
    lines.extend(
        [
            "",
            "## Video sources available but not selected",
            "",
            "Video is explored through Pexels, Wikimedia Commons and Internet",
            "Archive. Pexels is the primary; Wikimedia and Internet Archive are",
            "probed as backups and reported here when they return a usable result.",
            "",
        ]
    )
    return "\n".join(lines)
