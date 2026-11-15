"""Gap report: what awaits the user, what the agent can resolve, what is obsolete.

This separates the remaining work into three buckets so Gate 2A is not blocked
on the wrong thing.
"""

from __future__ import annotations

from pydantic import Field

from ..models import ProductionPlan, StrictModel, utc_now
from .models import Level2Plan
from .stock_plan import StockPlan

_AWAITS_USER = {"HI-01", "HI-02", "HI-03", "HI-05", "AC-16"}
_AGENT_RESOLVABLE = {"BL-011", "BL-012", "visual_media", "capture_route"}
_OBSOLETE = {"HI-04", "capture", "set_build", "owned_foley", "owned_sting", "voice_session"}


class Gap(StrictModel):
    ref: str
    item: str
    category: str = Field(pattern=r"^(awaiting_user|agent_resolvable|obsolete)$")
    detail: str


class GapReport(StrictModel):
    awaiting_user: list[Gap] = Field(default_factory=list)
    agent_resolvable: list[Gap] = Field(default_factory=list)
    obsolete: list[Gap] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


def evaluate_gaps(plan: ProductionPlan, level2: Level2Plan, stock: StockPlan) -> GapReport:
    report = GapReport()
    for blocker in level2.blockers:
        code = blocker.split(" ", 1)[0].rstrip(":")
        if code in _OBSOLETE:
            report.obsolete.append(
                Gap(
                    ref=code,
                    item=blocker,
                    category="obsolete",
                    detail="no in-house production: replaced by stock / AI generation / "
                    "AI enhancement",
                )
            )
        elif code in _AWAITS_USER:
            report.awaiting_user.append(
                Gap(
                    ref=code,
                    item=blocker,
                    category="awaiting_user",
                    detail="needs a named-human decision or a user-supplied file",
                )
            )
        elif code in _AGENT_RESOLVABLE or code.startswith("BL-"):
            report.agent_resolvable.append(
                Gap(
                    ref=code,
                    item=blocker,
                    category="agent_resolvable",
                    detail="can be priced or resolved by the agent",
                )
            )
        else:
            report.awaiting_user.append(
                Gap(ref=code, item=blocker, category="awaiting_user", detail="owner decision")
            )

    for intent in level2.intents:
        if intent.route == "supplied" and intent.rights_status == "needs_approval":
            report.awaiting_user.append(
                Gap(
                    ref=intent.asset_id,
                    item=f"{intent.asset_id} {intent.name}",
                    category="awaiting_user",
                    detail="user-supplied brand file + advertising rights (HI-02)",
                )
            )

    # Routes that the no-in-house policy replaces with stock/AI.
    for route in stock.routes:
        if route.group in {"stock", "generate"} and route.asset_id in {
            "AS-05",
            "AS-06",
            "AS-07",
            "AS-08",
            "AS-09",
            "AS-11",
            "AS-12",
            "AS-13",
        }:
            report.agent_resolvable.append(
                Gap(
                    ref=route.asset_id,
                    item=f"{route.asset_id} {route.name}",
                    category="agent_resolvable",
                    detail=f"source via {route.group} ({route.provider})",
                )
            )
    return report


def render_gaps(report: GapReport) -> str:
    lines = [
        "# User-input gaps and agent-resolvable work",
        "",
        "Separates what still needs the user, what the agent can resolve, and",
        "what is obsolete under the no in-house production policy.",
        "",
    ]
    sections = [
        ("## Awaiting user input", report.awaiting_user),
        ("## Agent-resolvable", report.agent_resolvable),
        ("## Obsolete under no in-house production", report.obsolete),
    ]
    for heading, gaps in sections:
        lines.append(heading)
        lines.append("")
        if gaps:
            lines.append("| Ref | Item | Detail |")
            lines.append("|---|---|---|")
            for gap in gaps:
                lines.append(f"| `{gap.ref}` | {gap.item} | {gap.detail} |")
        else:
            lines.append("none")
        lines.append("")
    lines.extend(
        [
            "## What the agent can correct now",
            "",
            "- Price BL-011 and BL-012 as $0 stock / AI-TTS, or quote within the $2 cap.",
            "- Replace capture/owned routes with stock, AI generation or AI enhancement.",
            "- Run visual QC once processed media exists.",
            "",
            "## What only the user can provide",
            "",
            "- Logo + four pack files and advertising rights (HI-02).",
            "- Brand typeface (HI-05) and price/hero pack size (HI-01).",
            "- Voice/music licence acceptance (HI-03).",
            "- 9:16 safe-area template (AC-16).",
            "- Gate 2A approval.",
            "",
        ]
    )
    return "\n".join(lines)
