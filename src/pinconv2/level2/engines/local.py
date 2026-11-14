"""Local, spend-free engine: ffmpeg and ffprobe."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from ..errors import RecipeError
from ..models import ProcessingOp
from .base import ProbeInfo, ProcessedAsset

_VIDEO_CODECS = {
    "prores_422hq": "prores_ks",
    "prores_422": "prores_ks",
    "h264": "libx264",
}
_AUDIO_CODECS = {"pcm_s24le": "pcm_s24le", "pcm_s16le": "pcm_s16le", "aac": "aac"}


class LocalEngine:
    name = "local"

    def __init__(self, ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe") -> None:
        self.ffmpeg = shutil.which(ffmpeg) or ffmpeg
        self.ffprobe = shutil.which(ffprobe) or ffprobe

    @property
    def available(self) -> bool:
        return shutil.which(self.ffmpeg) is not None and shutil.which(self.ffprobe) is not None

    def probe(self, path: Path) -> ProbeInfo:
        result = subprocess.run(
            [
                self.ffprobe,
                "-v",
                "error",
                "-print_format",
                "json",
                "-show_streams",
                "-show_format",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RecipeError(f"ffprobe failed for {path}: {result.stderr.strip()}")
        payload = json.loads(result.stdout or "{}")
        streams = payload.get("streams", [])
        video = next((item for item in streams if item.get("codec_type") == "video"), None)
        audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
        duration = payload.get("format", {}).get("duration")
        fps = None
        if video is not None and video.get("r_frame_rate"):
            numerator, _, denominator = video["r_frame_rate"].partition("/")
            try:
                fps = round(float(numerator) / float(denominator or 1), 3)
            except (ValueError, ZeroDivisionError):
                fps = None
        return ProbeInfo(
            path=str(path),
            codec=(video or audio or {}).get("codec_name", "unknown"),
            width=video.get("width") if video else None,
            height=video.get("height") if video else None,
            fps=fps,
            duration_seconds=round(float(duration), 3) if duration else None,
            channels=audio.get("channels") if audio else None,
            sample_rate=int(audio["sample_rate"]) if audio and audio.get("sample_rate") else None,
        )

    def process(
        self, recipe: list[ProcessingOp], source: Path, destination: Path
    ) -> ProcessedAsset:
        if not source.is_file():
            raise RecipeError(f"source does not exist: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        args = [self.ffmpeg, "-y", "-i", str(source)]
        filters: list[str] = []
        audio_filters: list[str] = []
        codec_args: list[str] = []
        is_audio = source.suffix.lower() in {".wav", ".mp3", ".flac", ".m4a"}

        for op in recipe:
            filters, audio_filters, codec_args = self._apply(
                op, filters, audio_filters, codec_args, is_audio
            )

        if not is_audio and filters:
            args += ["-vf", ",".join(filters)]
        if audio_filters:
            args += ["-af", ",".join(audio_filters)]
        args += codec_args
        args.append(str(destination))

        result = subprocess.run(args, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RecipeError(f"ffmpeg failed: {result.stderr.strip()[-800:]}")
        payload = destination.read_bytes()
        return ProcessedAsset(
            path=str(destination),
            sha256=hashlib.sha256(payload).hexdigest(),
            bytes=len(payload),
            probe=self.probe(destination),
            ops=[op.op for op in recipe],
        )

    def _apply(
        self,
        op: ProcessingOp,
        filters: list[str],
        audio_filters: list[str],
        codec_args: list[str],
        is_audio: bool,
    ) -> tuple[list[str], list[str], list[str]]:
        params = op.params
        if op.op == "scale":
            if is_audio:
                raise RecipeError("scale is not an audio op")
            width = int(params["width"])
            height = int(params["height"])
            filters.append(f"scale={width}:{height}")
        elif op.op == "conform":
            if is_audio:
                raise RecipeError("conform is not an audio op")
            filters.append(f"fps={int(params['fps'])}")
        elif op.op == "grade":
            if is_audio:
                raise RecipeError("grade is not an audio op")
            exposure = float(params.get("exposure", 0.0))
            filters.append(f"eq=brightness={exposure:.3f}")
        elif op.op == "loudness_norm":
            lufs = float(params.get("lufs", -16.0))
            peak = float(params.get("true_peak", -1.0))
            audio_filters.append(f"loudnorm=I={lufs}:TP={peak}:LRA=11")
            # loudnorm upsamples internally; pin the delivery rate back to 48 kHz.
            audio_filters.append("aresample=48000")
        elif op.op == "fade":
            audio_filters.append(f"afade=t=in:d={float(params.get('in_frames', 0)) / 25:.3f}")
        elif op.op == "resample":
            codec_args += ["-ar", str(int(params.get("sample_rate", 48000)))]
        elif op.op == "encode":
            codec = str(params.get("codec", "h264"))
            if codec in _AUDIO_CODECS:
                codec_args += ["-vn", "-c:a", _AUDIO_CODECS[codec]]
            elif codec in _VIDEO_CODECS:
                codec_args += ["-c:v", _VIDEO_CODECS[codec]]
                pix_fmt = params.get("pix_fmt")
                if pix_fmt:
                    codec_args += ["-pix_fmt", str(pix_fmt)]
                if codec.startswith("prores"):
                    codec_args += ["-profile:v", "3"]
            else:
                codec_args += ["-c:v", codec]
        elif op.op in {
            "trim",
            "crop",
            "stabilise",
            "speed_ramp",
            "denoise",
            "sharpen",
            "alpha_cutout",
            "despill",
            "mask_generate",
            "composite",
            "text_render",
            "channel_map",
            "pad",
        }:
            # These ops are planned and validated, but a full implementation belongs
            # to the processing phase after Gate 2A. Refusing is safer than guessing.
            raise RecipeError(f"{op.op} is not executed by the local dry-run engine")
        else:
            raise RecipeError(f"unknown op {op.op}")
        return filters, audio_filters, codec_args

    def assemble(self, clips: list[Path], destination: Path, audio: Path | None = None) -> Path:
        if not clips:
            raise RecipeError("no clips to assemble")
        destination.parent.mkdir(parents=True, exist_ok=True)
        list_file = destination.with_suffix(".concat.txt")
        list_file.write_text(
            "\n".join(f"file '{clip.as_posix()}'" for clip in clips) + "\n",
            encoding="utf-8",
        )
        args = [
            self.ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
        ]
        if audio is not None:
            args += ["-i", str(audio), "-map", "0:v", "-map", "1:a", "-shortest"]
        args += ["-c:v", "libx264", "-pix_fmt", "yuv420p", str(destination)]
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        list_file.unlink(missing_ok=True)
        if result.returncode != 0:
            raise RecipeError(f"assemble failed: {result.stderr.strip()[-800:]}")
        return destination
