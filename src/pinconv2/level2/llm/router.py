"""Reviewer routing.

Code owns classification, arithmetic and hashes. Models review candidate fit,
probe acceptance, prompt language and semantic consistency. The independent Gate
2 reviewer is read-only.
"""

from __future__ import annotations

from .base import Reviewer
from .chatgpt import ChatGptReviewer
from .deepseek import DeepSeekReviewer

_ROUTES = {
    "candidate_scoring": "chatgpt",
    "probe_review": "chatgpt",
    "prompt_refinement": "chatgpt",
    "semantic_consistency": "chatgpt",
    "method_review": "deepseek",
    "budget_review": "deepseek",
    "gate2_review": "deepseek",
}


def reviewer_for(job: str) -> Reviewer:
    route = _ROUTES.get(job)
    if route == "chatgpt":
        return ChatGptReviewer()
    if route == "deepseek":
        return DeepSeekReviewer()
    raise KeyError(f"no reviewer route for {job!r}")


def routes() -> dict[str, str]:
    return dict(_ROUTES)
