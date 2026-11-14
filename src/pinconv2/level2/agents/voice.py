"""Voice agent: disclosed Edge TTS fallback and transcription checks."""

from __future__ import annotations

from pathlib import Path

from ..engines.shortgpt import ShortGptEngine, VoiceResult


class VoiceAgent:
    def __init__(self, engine: ShortGptEngine | None = None) -> None:
        self.engine = engine or ShortGptEngine()

    def sample(self, text: str, destination: Path, voice: str) -> VoiceResult:
        return self.engine.synth(text, destination, voice=voice)

    def transcribe(self, audio: Path) -> dict[str, object]:
        return self.engine.transcribe(audio)
