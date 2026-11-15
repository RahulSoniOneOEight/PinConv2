"""Free/local Level 3 rough cut.

Builds a 20-second 16:9 and 9:16 rough cut from the selected stock assets,
pack images and audio, using ffmpeg only. No paid provider is called.

The HyperFrames composition pass replaces this rough cut once the full layer
animation is authored in OpenMontage.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

from .level3_spend import Level3Ledger, write_spend

ROOT = Path(r"D:\pinconv2\projects\blue-tokai-easy-pour-20s\level2\runs\rev-002")
OUT = ROOT / "deliverables"
FONT = "C\\:/Windows/Fonts/arial.ttf"

SHOTS = [
    ("SH-01", 0.0, 3.0, "Specialty coffee", "stock-candidates/AS-07.jpg"),
    ("SH-02", 3.0, 6.4, "Tear, anchor, pour.", "stock-candidates/AS-05.mp4"),
    ("SH-03", 6.4, 11.0, "Just a mug and hot water.", "stock-candidates/AS-06.mp4"),
    ("SH-04", 11.0, 15.2, "Light to dark.", "stock-candidates/AS-07.jpg"),
    ("SH-05", 15.2, 17.8, "One mug. One cup.", "stock-candidates/AS-08.jpg"),
    ("SH-06", 17.8, 20.0, "Shop Easy Pour", "stock-candidates/AS-07.jpg"),
]


def _run(args: list[str]) -> None:
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:])


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _shot_clip(shot: tuple[str, float, float, str, str], width: int, height: int) -> Path:
    shot_id, start, end, text, relative = shot
    duration = end - start
    source = ROOT / relative
    target = OUT / "clips" / f"{shot_id}-{width}x{height}.mp4"
    target.parent.mkdir(parents=True, exist_ok=True)
    args = ["ffmpeg", "-y"]
    if source.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
        args += ["-loop", "1", "-i", str(source), "-t", f"{duration:.3f}"]
    else:
        args += ["-i", str(source), "-t", f"{duration:.3f}"]
    escaped = text.replace(",", chr(92) + ",")
    size = max(28, height // 24)
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},fps=25,"
        f"drawtext=fontfile='{FONT}':text='{escaped}':fontcolor=white:"
        f"fontsize={size}:x=(w-text_w)/2:y=h*0.82:"
        f"box=1:boxcolor=black@0.45:boxborderw=18"
    )
    args += [
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-r",
        "25",
        str(target),
    ]
    _run(args)
    return target


def _concat(clips: list[Path], target: Path) -> None:
    listing = OUT / "clips" / "concat.txt"
    listing.write_text(
        "\n".join(f"file '{clip.as_posix()}'" for clip in clips) + "\n",
        encoding="utf-8",
    )
    _run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(listing),
            "-c",
            "copy",
            str(target),
        ]
    )


def build() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    ledger_path = OUT / "level3-spend.jsonl"
    ledger_path.unlink(missing_ok=True)
    ledger = Level3Ledger(ledger_path)
    ledger.zero(
        "stock-sourcing",
        "stock",
        "selected stock candidates (Pixabay/Pexels/Openverse/ccMixter/Freesound)",
    )
    ledger.zero("asset-processing", "ffmpeg", "trim/scale/grade/encode per shot")
    ledger.zero("voice", "shortgpt", "Edge TTS voice sample")
    clips_169 = [_shot_clip(shot, 1920, 1080) for shot in SHOTS]
    clips_916 = [_shot_clip(shot, 1080, 1920) for shot in SHOTS]
    silent_169 = OUT / "rough-16x9-silent.mp4"
    silent_916 = OUT / "rough-9x16-silent.mp4"
    _concat(clips_169, silent_169)
    _concat(clips_916, silent_916)
    ledger.zero("shot-assembly", "ffmpeg", "6-shot 16:9 and 9:16 assembly")

    voice = ROOT / "generated" / "AS-09-male-take.mp3"
    music = ROOT / "sourcing" / "CND-AS10-02-lost-roamin.mp3"
    sfx = ROOT / "stock-candidates" / "AS-11.mp3"
    report: dict[str, Any] = {}
    for label, silent in (("16x9", silent_169), ("9x16", silent_916)):
        target = OUT / f"ROUGH-CUT-{label}.mp4"
        _run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(silent),
                "-i",
                str(voice),
                "-i",
                str(music),
                "-i",
                str(sfx),
                "-filter_complex",
                "[0:v]null[v];"
                "[1:a]volume=1.0[a1];"
                "[2:a]volume=0.22,atrim=0:20[a2];"
                "[3:a]adelay=6400|6400,volume=0.5[a3];"
                "[a1][a2][a3]amix=inputs=3:duration=longest,alimiter,loudnorm=I=-16:TP=-1:LRA=11[aout]",
                "-map",
                "[v]",
                "-map",
                "[aout]",
                "-t",
                "20",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-movflags",
                "+faststart",
                "-metadata",
                "title=ROUGH CUT - NOT FINAL",
                str(target),
            ]
        )
        ledger.zero(f"render-{label}", "ffmpeg", f"{label} rough cut with audio mix")
        report[label] = {
            "path": str(target),
            "bytes": target.stat().st_size,
            "sha256": _sha(target),
        }
    report["shots"] = [shot[0] for shot in SHOTS]
    report["note"] = (
        "Free/local rough cut: stock bases + text + voice/music/SFX. "
        "Pack overlays and HyperFrames animation are the next pass."
    )
    write_spend(ledger, OUT)
    (OUT / "ROUGH-CUT-REPORT.md").write_text(
        "# Level 3 rough cut\n\n"
        f"- 16:9: `{report['16x9']['path']}` (ROUGH CUT - NOT FINAL)\n"
        f"- 9:16: `{report['9x16']['path']}` (ROUGH CUT - NOT FINAL)\n"
        f"- Note: {report['note']}\n",
        encoding="utf-8",
    )
    return report


if __name__ == "__main__":
    import json

    print(json.dumps(build(), indent=2))
