"""Rights, consent and disclosure checks."""

from __future__ import annotations

from ..models import (
    Asset,
    BindingKind,
    RightsStatus,
    Severity,
)
from .common import ValidationContext

PEOPLE_HINTS = ("person", "model", "actor", "talent", "voice", "hand")


def _required_assets(context: ValidationContext) -> set[str]:
    required: set[str] = set()
    for layer in context.plan.layers:
        if not layer.required:
            continue
        if layer.binding_kind is BindingKind.ASSET and layer.binding_ref:
            required.add(layer.binding_ref)
    asset_map = context.plan.asset_map
    for cue in context.plan.audio_cues:
        if cue.essential and cue.asset_id and cue.asset_id in asset_map:
            required.add(cue.asset_id)
    return required


def _check_asset(context: ValidationContext, asset: Asset) -> None:
    status = asset.rights.status
    if status in {RightsStatus.BLOCKED, RightsStatus.REFERENCE_ONLY}:
        context.fail(
            "rights.assets",
            asset.id,
            Severity.BLOCKER,
            f"required asset is {status.value}: {asset.name}",
            "Replace it with cleared or commissioned media.",
        )
    elif status is RightsStatus.UNKNOWN:
        context.warn(
            "rights.assets",
            asset.id,
            f"rights are unknown for {asset.name}",
            "Identify a licence and record commercial-use status before Level 2.",
        )
    elif status is RightsStatus.NEEDS_APPROVAL:
        context.warn(
            "rights.assets",
            asset.id,
            f"rights need approval for {asset.name}",
            "Obtain brand or licence approval before the asset enters a render.",
        )

    if asset.rights.ai_generated and not asset.rights.disclosure_required:
        context.fail(
            "rights.disclosure",
            asset.id,
            Severity.HIGH,
            "AI-generated asset has no disclosure decision",
            "Record whether a disclosure label is required.",
        )

    name = asset.name.lower()
    if any(hint in name for hint in PEOPLE_HINTS) and asset.rights.consent_ref is None:
        context.warn(
            "rights.consent",
            asset.id,
            f"{asset.name} implies a person or voice but has no consent record",
            "Record a model or performer release before production.",
        )


def validate_rights(context: ValidationContext) -> None:
    plan = context.plan
    required = _required_assets(context)

    with context.group(
        "rights.assets", "assets", "every required asset has a rights position"
    ):
        for asset_id in sorted(required):
            asset = plan.asset_map.get(asset_id)
            if asset is None:
                context.fail(
                    "rights.assets",
                    asset_id,
                    Severity.BLOCKER,
                    "required asset does not exist",
                    "Create the asset requirement.",
                )
                continue
            _check_asset(context, asset)

    with context.group(
        "rights.audio", "audio", "every essential audio cue resolves to an asset"
    ):
        for cue in plan.audio_cues:
            if not cue.essential:
                continue
            if cue.asset_id is None:
                context.fail(
                    "rights.audio",
                    cue.id,
                    Severity.HIGH,
                    "essential cue has no asset",
                    "Create an asset requirement or mark the cue optional.",
                )
            elif cue.asset_id not in plan.asset_map:
                context.fail(
                    "rights.audio",
                    cue.id,
                    Severity.HIGH,
                    f"essential cue references unknown asset {cue.asset_id}",
                    "Create the asset requirement.",
                )

    with context.group(
        "rights.reference", "sources", "reference media is not bound as production asset"
    ):
        for layer in plan.layers:
            if layer.binding_kind is not BindingKind.ASSET or not layer.binding_ref:
                continue
            asset = plan.asset_map.get(layer.binding_ref)
            if asset and asset.rights.status is RightsStatus.REFERENCE_ONLY:
                context.fail(
                    "rights.reference",
                    layer.id,
                    Severity.BLOCKER,
                    f"reference-only asset {asset.id} is bound to a production layer",
                    "Use the reference for inspiration only and source cleared media.",
                )

    with context.group(
        "rights.disclosure", "assets", "synthetic media carries a disclosure decision"
    ):
        required_ids = _required_assets(context)
        for asset in plan.assets:
            if asset.id not in required_ids:
                continue
            if asset.rights.ai_generated and asset.rights.disclosure_required:
                has_label_target = any(
                    "disclos" in check.description.lower()
                    or "ai" in check.description.lower().split()
                    for check in plan.checks
                )
                if not has_label_target:
                    context.warn(
                        "rights.disclosure",
                        asset.id,
                        "asset needs a disclosure label but no check covers it",
                        "Add an acceptance check for the disclosure label.",
                    )

    with context.group(
        "rights.attribution", "assets", "cleared assets carry attribution where required"
    ):
        for asset in plan.assets:
            if (
                asset.rights.status is RightsStatus.CLEARED
                and asset.rights.attribution
                and not any(
                    "attribution" in layer.allowed_edits for layer in plan.layers
                )
            ):
                context.warn(
                    "rights.attribution",
                    asset.id,
                    "asset requires attribution but no layer records it",
                    "Add attribution to the end card or caption.",
                )
