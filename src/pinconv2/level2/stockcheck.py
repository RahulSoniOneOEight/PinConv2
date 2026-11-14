"""Live stock-source checks.

Fetches one item from each usable source, records the licence, downloads a
bounded sample, probes it with ffprobe, and writes a reviewable report. This is a
capability check, not an acquisition for the film: samples live under
``dist/stock-check`` and never enter the build sheet.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from pydantic import Field

from ..models import StrictModel, utc_now
from .credentials import provider_key
from .engines.local import LocalEngine
from .licence_gate import classify_licence
from .models import LicenceClass

UA = "PinConv2/0.1 (source capability check)"
TIMEOUT = 60
MAX_BYTES = 25 * 1024 * 1024

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")
VIDEO_SUFFIXES = (".mp4", ".webm", ".mov", ".m4v")
AUDIO_SUFFIXES = (".mp3", ".wav", ".ogg", ".m4a", ".flac")


class StockItem(StrictModel):
    provider: str
    media_type: str = Field(pattern=r"^(image|video|audio)$")
    query: str
    status: str = Field(
        pattern=r"^(ok|key_missing|http_error|no_result|download_failed|too_large)$"
    )
    http_status: int | None = None
    title: str | None = Field(default=None, max_length=300)
    creator: str | None = Field(default=None, max_length=300)
    licence: str | None = Field(default=None, max_length=200)
    licence_class: str | None = Field(default=None, max_length=40)
    paid_ok: bool = False
    attribution: str | None = Field(default=None, max_length=500)
    page_url: str | None = Field(default=None, max_length=1000)
    file_path: str | None = Field(default=None, max_length=1000)
    bytes: int = 0
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    probe: dict[str, object] = Field(default_factory=dict)
    note: str | None = Field(default=None, max_length=500)


class StockCheckReport(StrictModel):
    items: list[StockItem] = Field(min_length=1)
    created_at: str = Field(default_factory=utc_now)

    @property
    def ok_count(self) -> int:
        return sum(1 for item in self.items if item.status == "ok")


def _get(url: str, headers: dict[str, str] | None = None) -> tuple[int, bytes, str]:
    request = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})}
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.status, response.read(), response.headers.get("Content-Type", "")


def _json(url: str, headers: dict[str, str] | None = None) -> tuple[int, object]:
    status, body, _ = _get(url, headers)
    return status, json.loads(body.decode("utf-8"))


def _download(url: str, destination: Path, headers: dict[str, str] | None = None) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})}
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                length = response.headers.get("Content-Length")
                if length and int(length) > MAX_BYTES:
                    raise ValueError(f"file is {length} bytes, above the {MAX_BYTES} limit")
                body = response.read(MAX_BYTES + 1)
            break
        except urllib.error.HTTPError as error:
            if error.code in {429, 503} and attempt < 2:
                time.sleep(2 + attempt * 3)
                continue
            raise
    if len(body) > MAX_BYTES:
        raise ValueError(f"file is above the {MAX_BYTES} limit")
    destination.write_bytes(body)
    return destination


def _licence_info(text: str | None) -> tuple[str | None, bool]:
    if not text:
        return None, False
    upper = text.upper()
    if "PEXELS" in upper or "UNSPLASH" in upper:
        return LicenceClass.PROPRIETARY_FREE.value, True
    if "NASA" in upper:
        return LicenceClass.PD.value, True
    if "ITEM-SPECIFIC" in upper:
        return LicenceClass.UNKNOWN.value, False
    if upper.strip() == "BY":
        return LicenceClass.CC_BY.value, True
    licence = classify_licence(text)
    blocking = {
        LicenceClass.BLOCKED,
        LicenceClass.CC_BY_NC,
        LicenceClass.CC_BY_ND,
        LicenceClass.CC_BY_SA,
    }
    return licence.value, licence not in blocking


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:50] or "item"


def _suffix(url: str, allowed: tuple[str, ...], default: str) -> str:
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    return suffix if suffix in allowed else default


def _probe(path: Path) -> dict[str, object]:
    try:
        info = LocalEngine().probe(path)
        return info.model_dump(exclude={"path"})
    except Exception as error:  # noqa: BLE001
        return {"error": str(error)[:200]}


def _item(
    provider: str,
    media_type: str,
    query: str,
    *,
    title: str | None = None,
    creator: str | None = None,
    licence: str | None = None,
    page_url: str | None = None,
    file_url: str | None = None,
    headers: dict[str, str] | None = None,
    destination: Path,
    status: str = "ok",
    http_status: int | None = None,
    note: str | None = None,
) -> StockItem:
    licence_text = str(licence)[:200] if licence else None
    licence_class, paid_ok = _licence_info(licence_text)
    item = StockItem(
        provider=provider,
        media_type=media_type,
        query=query,
        status=status,
        http_status=http_status,
        title=str(title)[:300] if title else None,
        creator=str(creator)[:300] if creator else None,
        licence=licence_text,
        licence_class=licence_class,
        paid_ok=paid_ok,
        page_url=str(page_url)[:1000] if page_url else None,
        note=note,
    )
    if status != "ok" or not file_url:
        return item
    try:
        path = _download(file_url, destination, headers)
    except Exception as error:  # noqa: BLE001
        return item.model_copy(
            update={
                "status": "download_failed",
                "note": f"{type(error).__name__}: {error}"[:500],
                "http_status": http_status,
            }
        )
    payload = path.read_bytes()
    return item.model_copy(
        update={
            "file_path": str(path),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "probe": _probe(path),
        }
    )


def _openverse(media_type: str, query: str, root: Path) -> StockItem:
    endpoint = "images" if media_type == "image" else "audio"
    url = (
        f"https://api.openverse.org/v1/{endpoint}/?q={urllib.parse.quote(query)}"
        "&page_size=1&license=cc0,by"
    )
    try:
        status, payload = _json(url)
        results = payload.get("results", []) if isinstance(payload, dict) else []
        if not results:
            return StockItem(
                provider="openverse",
                media_type=media_type,
                query=query,
                status="no_result",
                http_status=status,
            )
        first = results[0]
        file_url = first.get("url")
        suffix = _suffix(
            file_url or "",
            IMAGE_SUFFIXES if media_type == "image" else AUDIO_SUFFIXES,
            ".jpg" if media_type == "image" else ".mp3",
        )
        return _item(
            "openverse",
            media_type,
            query,
            title=first.get("title"),
            creator=first.get("creator"),
            licence=str(first.get("license", "")).upper(),
            page_url=first.get("foreign_landing_url"),
            file_url=file_url,
            destination=root / f"openverse-{_slug(str(first.get('title', 'item')))}{suffix}",
            http_status=status,
            note="Aggregator; verify the licence at the origin page.",
        )
    except Exception as error:  # noqa: BLE001
        return StockItem(
            provider="openverse",
            media_type=media_type,
            query=query,
            status="http_error",
            note=f"{type(error).__name__}: {error}"[:500],
        )


def _wikimedia(media_type: str, query: str, root: Path) -> StockItem:
    gsr = query if media_type == "image" else f"filetype:{media_type} {query}"
    url = (
        "https://commons.wikimedia.org/w/api.php?action=query&format=json"
        "&generator=search&gsrnamespace=6&gsrlimit=1"
        f"&gsrsearch={urllib.parse.quote(gsr)}"
        "&prop=imageinfo&iiprop=url%7Cextmetadata"
    )
    try:
        status, payload = _json(url)
        pages = payload.get("query", {}).get("pages", {}) if isinstance(payload, dict) else {}
        if not pages:
            return StockItem(
                provider="wikimedia",
                media_type=media_type,
                query=query,
                status="no_result",
                http_status=status,
            )
        page = next(iter(pages.values()))
        info = (page.get("imageinfo") or [{}])[0]
        file_url = info.get("url")
        meta = info.get("extmetadata") or {}
        licence = (meta.get("LicenseShortName") or {}).get("value")
        artist = (meta.get("Artist") or {}).get("value")
        if artist:
            artist = re.sub(r"<[^>]+>", "", artist).strip()
        suffix = _suffix(
            file_url or "",
            IMAGE_SUFFIXES
            if media_type == "image"
            else VIDEO_SUFFIXES
            if media_type == "video"
            else AUDIO_SUFFIXES,
            ".jpg" if media_type == "image" else ".mp4" if media_type == "video" else ".ogg",
        )
        page_url = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(
            str(page.get("title", ""))
        )
        return _item(
            "wikimedia",
            media_type,
            query,
            title=page.get("title"),
            creator=artist,
            licence=licence,
            page_url=page_url,
            file_url=file_url,
            destination=root / f"wikimedia-{_slug(str(page.get('title', 'item')))}{suffix}",
            headers={"Referer": "https://commons.wikimedia.org/"},
            http_status=status,
            note="Aggregator; per-file licence on the file page.",
        )
    except Exception as error:  # noqa: BLE001
        return StockItem(
            provider="wikimedia",
            media_type=media_type,
            query=query,
            status="http_error",
            note=f"{type(error).__name__}: {error}"[:500],
        )


def _nasa_image(query: str, root: Path) -> StockItem:
    url = f"https://images-api.nasa.gov/search?q={urllib.parse.quote(query)}&media_type=image"
    try:
        status, payload = _json(url)
        items = payload.get("collection", {}).get("items", []) if isinstance(payload, dict) else []
        if not items:
            return StockItem(
                provider="nasa",
                media_type="image",
                query=query,
                status="no_result",
                http_status=status,
            )
        first = items[0]
        data = (first.get("data") or [{}])[0]
        links = first.get("links") or []
        file_url = links[0].get("href") if links else None
        return _item(
            "nasa",
            "image",
            query,
            title=data.get("title"),
            creator=data.get("center"),
            licence="NASA (mostly public domain)",
            page_url=f"https://images.nasa.gov/details/{data.get('nasa_id', '')}",
            file_url=file_url,
            destination=root
            / (
                f"nasa-{_slug(str(data.get('nasa_id', 'image')))}"
                f"{_suffix(file_url or '', IMAGE_SUFFIXES, '.jpg')}"
            ),
            http_status=status,
            note="Check partner/ESA exceptions.",
        )
    except Exception as error:  # noqa: BLE001
        return StockItem(
            provider="nasa",
            media_type="image",
            query=query,
            status="http_error",
            note=f"{type(error).__name__}: {error}"[:500],
        )


def _archive(media_type: str, query: str, root: Path) -> StockItem:
    mediatype = "audio" if media_type == "audio" else "movies"
    search = (
        "https://archive.org/advancedsearch.php?q="
        f"{urllib.parse.quote(f'{query} AND mediatype:{mediatype}')}"
        "&fl%5B%5D=identifier&rows=5&output=json"
    )
    try:
        status, payload = _json(search)
        docs = payload.get("response", {}).get("docs", []) if isinstance(payload, dict) else []
        if not docs:
            return StockItem(
                provider="internet-archive",
                media_type=media_type,
                query=query,
                status="no_result",
                http_status=status,
            )
        last_failure: StockItem | None = None
        for doc in docs[:5]:
            identifier = str(doc.get("identifier", ""))
            if not identifier:
                continue
            try:
                _, meta = _json(f"https://archive.org/metadata/{identifier}")
                files = meta.get("files", []) if isinstance(meta, dict) else []
                wanted = AUDIO_SUFFIXES if media_type == "audio" else VIDEO_SUFFIXES
                candidates = [
                    item
                    for item in files
                    if Path(str(item.get("name", ""))).suffix.lower() in wanted
                    and 0 < int(item.get("size") or 0) <= MAX_BYTES
                ]
                if not candidates:
                    continue
                candidates.sort(key=lambda item: int(item.get("size") or 0))
                chosen = candidates[0]
                name = str(chosen["name"])
                file_url = f"https://archive.org/download/{identifier}/{urllib.parse.quote(name)}"
                metadata = meta.get("metadata") if isinstance(meta, dict) else None
                creator = metadata.get("creator") if isinstance(metadata, dict) else None
                result = _item(
                    "internet-archive",
                    media_type,
                    query,
                    title=identifier,
                    creator=creator,
                    licence="Item-specific; verify the item page",
                    page_url=f"https://archive.org/details/{identifier}",
                    file_url=file_url,
                    destination=root / f"archive-{_slug(identifier)}{Path(name).suffix.lower()}",
                    headers={"Referer": f"https://archive.org/details/{identifier}"},
                    http_status=status,
                    note="Rights vary per item.",
                )
                if result.status == "ok":
                    return result
                last_failure = result
            except Exception as error:  # noqa: BLE001
                last_failure = StockItem(
                    provider="internet-archive",
                    media_type=media_type,
                    query=query,
                    status="http_error",
                    note=f"{type(error).__name__}: {error}"[:500],
                )
        if last_failure is not None:
            return last_failure
        return StockItem(
            provider="internet-archive",
            media_type=media_type,
            query=query,
            status="no_result",
            http_status=status,
            note="No item had a media file under the size limit.",
        )
    except Exception as error:  # noqa: BLE001
        return StockItem(
            provider="internet-archive",
            media_type=media_type,
            query=query,
            status="http_error",
            note=f"{type(error).__name__}: {error}"[:500],
        )


def _pexels(media_type: str, query: str, root: Path) -> StockItem:
    key = provider_key("PEXELS_API_KEY")
    if not key:
        return StockItem(
            provider="pexels",
            media_type=media_type,
            query=query,
            status="key_missing",
        )
    endpoint = "videos/search" if media_type == "video" else "v1/search"
    url = (
        f"https://api.pexels.com/{endpoint}?query={urllib.parse.quote(query)}&per_page=1"
        if media_type == "video"
        else f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=1"
    )
    try:
        status, payload = _json(url, {"Authorization": key})
        if media_type == "video":
            videos = payload.get("videos", []) if isinstance(payload, dict) else []
            if not videos:
                return StockItem(
                    provider="pexels",
                    media_type=media_type,
                    query=query,
                    status="no_result",
                    http_status=status,
                )
            first = videos[0]
            files = sorted(
                first.get("video_files", []),
                key=lambda item: int(item.get("width") or 0),
            )
            file_url = files[0].get("link") if files else None
            title = f"Pexels video {first.get('id')}"
            page_url = first.get("url")
        else:
            photos = payload.get("photos", []) if isinstance(payload, dict) else []
            if not photos:
                return StockItem(
                    provider="pexels",
                    media_type=media_type,
                    query=query,
                    status="no_result",
                    http_status=status,
                )
            first = photos[0]
            file_url = (first.get("src") or {}).get("medium")
            title = f"Pexels photo {first.get('id')}"
            page_url = first.get("url")
        suffix = _suffix(
            file_url or "",
            VIDEO_SUFFIXES if media_type == "video" else IMAGE_SUFFIXES,
            ".mp4" if media_type == "video" else ".jpg",
        )
        return _item(
            "pexels",
            media_type,
            query,
            title=title,
            creator=first.get("photographer") or first.get("user", {}).get("name"),
            licence="Pexels License",
            page_url=page_url,
            file_url=file_url,
            destination=root / f"pexels-{_slug(title)}{suffix}",
            http_status=status,
            note="Pexels link and download-event rules apply.",
        )
    except Exception as error:  # noqa: BLE001
        return StockItem(
            provider="pexels",
            media_type=media_type,
            query=query,
            status="http_error",
            note=f"{type(error).__name__}: {error}"[:500],
        )


def _unsplash(query: str, root: Path) -> StockItem:
    key = provider_key("UNSPLASH_ACCESS_KEY")
    if not key:
        return StockItem(
            provider="unsplash",
            media_type="image",
            query=query,
            status="key_missing",
        )
    url = f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(query)}&per_page=1"
    try:
        status, payload = _json(url, {"Authorization": f"Client-ID {key}"})
        results = payload.get("results", []) if isinstance(payload, dict) else []
        if not results:
            return StockItem(
                provider="unsplash",
                media_type="image",
                query=query,
                status="no_result",
                http_status=status,
            )
        first = results[0]
        file_url = (first.get("urls") or {}).get("small")
        return _item(
            "unsplash",
            "image",
            query,
            title=first.get("description") or first.get("alt_description"),
            creator=(first.get("user") or {}).get("name"),
            licence="Unsplash License",
            page_url=(first.get("links") or {}).get("html"),
            file_url=file_url,
            destination=root
            / (
                f"unsplash-{_slug(str(first.get('id', 'photo')))}"
                f"{_suffix(file_url or '', IMAGE_SUFFIXES, '.jpg')}"
            ),
            http_status=status,
            note="Download event must be fired on selection.",
        )
    except Exception as error:  # noqa: BLE001
        return StockItem(
            provider="unsplash",
            media_type="image",
            query=query,
            status="http_error",
            note=f"{type(error).__name__}: {error}"[:500],
        )


def _freesound(query: str, root: Path) -> StockItem:
    key = provider_key("FREESOUND_API_KEY")
    if not key:
        return StockItem(
            provider="freesound",
            media_type="audio",
            query=query,
            status="key_missing",
        )
    url = (
        "https://freesound.org/apiv2/search/text/?query="
        f"{urllib.parse.quote(query)}&fields=id,name,license,username,previews"
    )
    try:
        status, payload = _json(url, {"Authorization": f"Token {key}"})
        results = payload.get("results", []) if isinstance(payload, dict) else []
        if not results:
            return StockItem(
                provider="freesound",
                media_type="audio",
                query=query,
                status="no_result",
                http_status=status,
            )
        first = results[0]
        previews = first.get("previews") or {}
        file_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
        return _item(
            "freesound",
            "audio",
            query,
            title=first.get("name"),
            creator=first.get("username"),
            licence=str(first.get("license")),
            page_url=f"https://freesound.org/s/{first.get('id')}/",
            file_url=file_url,
            destination=root
            / (
                f"freesound-{_slug(str(first.get('name', 'sound')))}"
                f"{_suffix(file_url or '', AUDIO_SUFFIXES, '.mp3')}"
            ),
            http_status=status,
            note="Preview only; NC/ND must be filtered for commercial use.",
        )
    except Exception as error:  # noqa: BLE001
        return StockItem(
            provider="freesound",
            media_type="audio",
            query=query,
            status="http_error",
            note=f"{type(error).__name__}: {error}"[:500],
        )


def run_stock_check(root: Path, query: str = "coffee") -> StockCheckReport:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    items = [
        _openverse("image", query, root),
        _openverse("audio", query, root),
        _wikimedia("image", query, root),
        _wikimedia("video", query, root),
        _wikimedia("audio", query, root),
        _nasa_image(query, root),
        _archive("audio", query, root),
        _archive("video", query, root),
        _pexels("image", query, root),
        _pexels("video", query, root),
        _unsplash(query, root),
        _freesound(query, root),
    ]
    return StockCheckReport(items=items)


def render_stock_check(report: StockCheckReport) -> str:
    lines = [
        "# Stock fetch check",
        "",
        "One item fetched per source. Samples are capability checks, not film assets.",
        "",
        f"**{report.ok_count} of {len(report.items)} sources fetched and probed.**",
        "",
        "| Source | Type | Status | Licence | Paid? | File | Probe |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in report.items:
        probe = item.probe
        size = (
            f"{probe.get('width')}×{probe.get('height')}"
            if probe.get("width")
            else f"{probe.get('duration_seconds')}s"
            if probe.get("duration_seconds")
            else "—"
        )
        file = Path(item.file_path).name if item.file_path else "—"
        lines.append(
            f"| {item.provider} | {item.media_type} | {item.status} | "
            f"{item.licence_class or item.licence or '—'} | "
            f"{'yes' if item.paid_ok else 'NO'} | {file} | {size} |"
        )
    lines.extend(["", "## Details", ""])
    for item in report.items:
        lines.extend(
            [
                f"### {item.provider} — {item.media_type}",
                "",
                f"- Status: `{item.status}` (HTTP {item.http_status or '—'})",
                f"- Title: {item.title or '—'}",
                f"- Creator: {item.creator or '—'}",
                f"- Licence: {item.licence or '—'} ({item.licence_class or 'unknown'}; "
                f"paid use: {'yes' if item.paid_ok else 'no'})",
                f"- Page: {item.page_url or '—'}",
                f"- File: {item.file_path or '—'}",
                f"- SHA-256: `{item.sha256 or '—'}`",
                f"- Probe: {item.probe}",
                f"- Note: {item.note or '—'}",
                "",
            ]
        )
    return "\n".join(lines)
