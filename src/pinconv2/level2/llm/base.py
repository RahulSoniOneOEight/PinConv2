"""LLM reviewer contract.

Models propose; code validates. A reviewer receives a bounded packet and returns
a structured verdict. No reviewer can write a hash, a price or an approval.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Protocol

from pydantic import Field

from ...models import StrictModel

DEFAULT_TIMEOUT = 60


class ReviewRequest(StrictModel):
    job: str = Field(min_length=1, max_length=60)
    system: str = Field(min_length=1, max_length=4000)
    content: str = Field(min_length=1, max_length=60000)
    max_tokens: int = Field(default=1200, ge=128, le=8000)


class ReviewResponse(StrictModel):
    reviewer: str
    model: str
    verdict: str = Field(pattern=r"^(pass|warn|fail|unavailable)$")
    findings: list[str] = Field(default_factory=list)
    raw: str | None = Field(default=None, max_length=8000)


class Reviewer(Protocol):
    name: str
    model: str

    @property
    def available(self) -> bool: ...

    def review(self, request: ReviewRequest) -> ReviewResponse: ...


class HttpReviewer:
    """OpenAI-compatible chat completion reviewer."""

    def __init__(
        self,
        *,
        name: str,
        model: str,
        endpoint: str,
        api_key_env: str,
    ) -> None:
        self.name = name
        self.model = model
        self.endpoint = endpoint
        self.api_key_env = api_key_env

    @property
    def available(self) -> bool:
        return bool(os.environ.get(self.api_key_env))

    def review(self, request: ReviewRequest) -> ReviewResponse:
        key = os.environ.get(self.api_key_env)
        if not key:
            return ReviewResponse(
                reviewer=self.name,
                model=self.model,
                verdict="unavailable",
                findings=[f"{self.api_key_env} is not set"],
            )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": request.content},
            ],
            "max_tokens": request.max_tokens,
            "temperature": 0,
        }
        http_request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=DEFAULT_TIMEOUT) as response:
                body = json.loads(response.read().decode("utf-8"))
        except OSError as error:
            return ReviewResponse(
                reviewer=self.name,
                model=self.model,
                verdict="unavailable",
                findings=[f"request failed: {error}"],
            )
        content = (
            body.get("choices", [{}])[0].get("message", {}).get("content", "")
            if isinstance(body, dict)
            else ""
        )
        lowered = content.lower()
        verdict = "warn"
        if "verdict: pass" in lowered:
            verdict = "pass"
        elif "verdict: fail" in lowered:
            verdict = "fail"
        return ReviewResponse(
            reviewer=self.name,
            model=self.model,
            verdict=verdict,
            findings=[content[:4000]] if content else [],
            raw=content[:8000],
        )
