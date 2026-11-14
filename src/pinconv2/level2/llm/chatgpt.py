"""ChatGPT reviewer for vision, acceptance and semantic QC."""

from __future__ import annotations

import os

from .base import HttpReviewer


class ChatGptReviewer(HttpReviewer):
    def __init__(self, model: str | None = None) -> None:
        super().__init__(
            name="chatgpt",
            model=model or os.environ.get("OPENAI_MODEL", "gpt-5.6-sol"),
            endpoint=os.environ.get(
                "OPENAI_ENDPOINT", "https://api.openai.com/v1/chat/completions"
            ),
            api_key_env="OPENAI_API_KEY",
        )
