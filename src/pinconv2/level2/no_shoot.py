"""No-shoot production policy.

The production has no camera shoot. Every asset must therefore be one of:

- a supplied brand file;
- licensed stock;
- licensed stock with AI processing;
- AI-generated media with disclosure.

Capture routes are invalid. Proof-class assets cannot be produced without a
capture, so they must be reclassified to representative with disclosure, replaced
by stock/AI, or dropped. Exact product/pack/logo files remain supplied and may
never be stock or generated.
"""

from __future__ import annotations

from pydantic import Field

from ..models import AssetRoute, ProductionPlan, StrictModel, utc_now
from .models import Level2Plan, SourceStrategy, TruthClass

_NO_SHOOT_ROUTES = {
    "supplied": "keep the supplied brand file",
    "stock": "license stock",
    "stock_ai": "license stock and process with AI",
    "generate": "AI-generate with disclosure",
    "owned": "use an existing owned file, not a new shoot",
}

_CAPTURE_REPLACEMENT = {
    "AS-05": (
        "stock",
        "stock pour-over hands footage or AI-generated hands; "
        "reclassify proof to representative with disclosure",
    ),
    "AS-06": (
        "stock",
        "stock hot-water pour/bloom footage or AI-generated clip; "
        "reclassify proof to representative with disclosure",
    ),
    "AS-08": (
        "stock",
        "stock finished-cup footage or AI-generated cup; "
        "reclassify proof to representative with disclosure",
    ),
    "AS-13": ("supplied", "use the supplied AS-02 pack image; remove the capture fallback"),
    "AS-07": (
        "stock",
        "stock kitchen background or AI-generated background; atmospheric allows it",
    ),
    "AS-09": ("generate", "AI TTS voice (AS-15 route) or licensed voice; no camera shoot needed"),
    "AS-11": ("stock", "stock pour SFX or AI audio generation"),
    "AS-12": ("generate", "AI-generated or licensed brand sting"),
}


class NoShootFinding(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    current_route: str
    truth_class: str
    issue: str
    recommended_route: str
    note: str


class NoShootReport(StrictModel):
    status: str = Field(pattern=r"^(ready|blocked)$")
    findings: list[NoShootFinding] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


def evaluate_no_shoot(plan: ProductionPlan, level2: Level2Plan) -> NoShootReport:
    tasks = {task.asset_id: task for task in level2.tasks}
    findings: list[NoShootFinding] = []
    for intent in level2.intents:
        task = tasks.get(intent.asset_id)
        if task is None:
            continue
        route = intent.route.value if hasattr(intent.route, "value") else str(intent.route)
        source = str(getattr(task, "capture_ref", "") or "")
        source_text = f"{source} {intent.specification}".lower()
        no_shoot_required = (
            route == AssetRoute.TO_CAPTURE.value
            or "shoot" in source_text
            or "set build" in source_text
            or intent.asset_id == "AS-09"
            or (route == AssetRoute.OWNED.value and intent.asset_id in {"AS-07", "AS-11", "AS-12"})
        )
        capture_flagged = False
        if no_shoot_required:
            capture_flagged = True
            recommended, note = _CAPTURE_REPLACEMENT.get(
                intent.asset_id,
                ("stock", "replace the capture with licensed stock or disclosed generation"),
            )
            findings.append(
                NoShootFinding(
                    asset_id=intent.asset_id,
                    current_route=route,
                    truth_class=intent.truth_class.value,
                    issue=(
                        "capture, set build, owned production or recorded voice "
                        "is not allowed in a no-shoot production"
                    ),
                    recommended_route=recommended,
                    note=note,
                )
            )
        if (
            not capture_flagged
            and intent.truth_class is TruthClass.PROOF
            and task.source_strategy is SourceStrategy.CAPTURE
        ):
            findings.append(
                NoShootFinding(
                    asset_id=intent.asset_id,
                    current_route=route,
                    truth_class=intent.truth_class.value,
                    issue="proof requires a capture and cannot remain proof without one",
                    recommended_route="stock",
                    note="reclassify to representative with disclosure, or drop the proof claim",
                )
            )
        if intent.truth_class in {TruthClass.EXACT, TruthClass.PROOF} and route in {
            AssetRoute.TO_SOURCE.value,
            AssetRoute.TO_GENERATE.value,
        }:
            findings.append(
                NoShootFinding(
                    asset_id=intent.asset_id,
                    current_route=route,
                    truth_class=intent.truth_class.value,
                    issue="exact/proof material may not be stock or generated",
                    recommended_route="supplied",
                    note="use the real brand file or remove the claim",
                )
            )
    status = "blocked" if findings else "ready"
    return NoShootReport(status=status, findings=findings)


def render_no_shoot(report: NoShootReport) -> str:
    lines = [
        "# No-shoot production policy",
        "",
        "**Constraint:** there is no camera shoot. Assets are supplied brand files,",
        "licensed stock, licensed stock with AI processing, or AI-generated media",
        "with disclosure.",
        "",
        f"**Status:** `{report.status}`",
        "",
        "| Asset | Current route | Class | Issue | Recommended route | Note |",
        "|---|---|---|---|---|---|",
    ]
    for finding in report.findings:
        lines.append(
            f"| `{finding.asset_id}` | `{finding.current_route}` | "
            f"{finding.truth_class} | {finding.issue} | "
            f"`{finding.recommended_route}` | {finding.note} |"
        )
    lines.extend(
        [
            "",
            "## Rules",
            "",
            "- `exact` product/pack/logo stays supplied; never stock or generated.",
            "- `proof` cannot survive without a capture; reclassify to representative",
            "  with disclosure, replace with stock/AI, or drop the proof claim.",
            "- `atmospheric` and `representative` may use stock, stock + AI, or AI",
            "  generation with disclosure.",
            "- A human must approve any proof-to-representative change and any",
            "  synthetic replacement before Gate 2A.",
            "",
        ]
    )
    return "\n".join(lines)
