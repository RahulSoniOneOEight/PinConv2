"""DeepSeek reviewer (independent Gate 2 review)."""

from __future__ import annotations

import os

from .base import HttpReviewer


class DeepSeekReviewer(HttpReviewer):
    def __init__(self, model: str | None = None) -> None:
        super().__init__(
            name="deepseek",
            model=model or os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
            endpoint=os.environ.get(
                "DEEPSEEK_ENDPOINT", "https://api.deepseek.com/chat/completions"
            ),
            api_key_env="DEEPSEEK_API_KEY",
        )
