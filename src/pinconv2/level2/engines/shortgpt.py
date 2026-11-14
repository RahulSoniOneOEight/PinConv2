"""ShortGPT adapter: Edge TTS and transcriptions only.

ShortGPT is installed at ``D:\\shortgpt`` with Edge TTS in its venv. This adapter
deliberately does not use ShortGPT's renderer or script generation: Level 2 uses
it for the disclosed synthetic-voice fallback and for transcription.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from pydantic import Field

from ...models import StrictModel
from ..errors import Level2Error
from .local import LocalEngine

DEFAULT_ROOT = Path(r"D:\shortgpt")
DEFAULT_VOICE = "en-IN-NeerjaNeural"


class EngineUnavailableError(Level2Error):
    """ShortGPT or one of its optional capabilities is not available."""


class VoiceResult(StrictModel):
    provider: str = "shortgpt:edge-tts"
    path: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    bytes: int = Field(ge=0)
    duration_seconds: float | None = None
    voice: str
    disclosure_required: bool = True
    disclosure_text: str = "Synthetic voice generated with Edge TTS"


class ShortGptEngine:
    name = "shortgpt"

    def __init__(
        self,
        root: Path = DEFAULT_ROOT,
        *,
        python: Path | None = None,
    ) -> None:
        self.root = Path(root)
        self.python = python or self.root / ".venv" / "Scripts" / "python.exe"

    @property
    def available(self) -> bool:
        return self.python.is_file() and (self.root / "shortGPT").is_dir()

    def synth(
        self,
        text: str,
        destination: Path,
        *,
        voice: str = DEFAULT_VOICE,
    ) -> VoiceResult:
        if not self.available:
            raise EngineUnavailableError(
                f"ShortGPT venv not found at {self.python}"
            )
        if not text.strip():
            raise EngineUnavailableError("voice text is empty")
        destination.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [
                str(self.python),
                "-m",
                "edge_tts",
                "--text",
                text,
                "--voice",
                voice,
                "--write-media",
                str(destination),
                "--no-progress",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
        if result.returncode != 0 or not destination.is_file():
            raise EngineUnavailableError(
                f"edge-tts failed: {(result.stderr or result.stdout).strip()[-600:]}"
            )
        payload = destination.read_bytes()
        duration = None
        try:
            duration = LocalEngine().probe(destination).duration_seconds
        except Exception:
            duration = None
        return VoiceResult(
            path=str(destination),
            sha256=hashlib.sha256(payload).hexdigest(),
            bytes=len(payload),
            duration_seconds=duration,
            voice=voice,
        )

    def transcribe(self, audio: Path) -> dict[str, object]:
        if not self.available:
            raise EngineUnavailableError("ShortGPT venv not found")
        if not audio.is_file():
            raise EngineUnavailableError(f"audio not found: {audio}")
        probe = subprocess.run(
            [
                str(self.python),
                "-c",
                "import importlib.util as u; print(bool(u.find_spec('whisper_timestamped')))",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        if "True" not in probe.stdout:
            raise EngineUnavailableError("whisper_timestamped is not installed")
        raise EngineUnavailableError(
            "transcription model is not downloaded; downloading it needs explicit "
            "owner approval (about 574 MB)"
        )
