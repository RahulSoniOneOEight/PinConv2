"""Commercial exactness, copy and claim checks."""

from __future__ import annotations

from ..models import (
    CRITICAL_EXACT_FIELDS,
    ClaimStatus,
    CopyStatus,
    DataStatus,
    Severity,
    ValidationStatus,
)
from .common import ValidationContext, parse_timestamp


def _copy_layers(context: ValidationContext) -> list[tuple[str, str, bool]]:
    """Return (layer_id, copy_id, required) for every copy-bound layer."""

    result: list[tuple[str, str, bool]] = []
    for layer in context.plan.layers:
        if layer.binding_kind.value == "copy" and layer.binding_ref:
            result.append((layer.id, layer.binding_ref, layer.required))
    return result


def validate_exact_data(context: ValidationContext) -> None:
    plan = context.plan
    exact = plan.exact_map
    claims = plan.claim_map
    copy_blocks = plan.copy_map

    referenced_exact: set[str] = set()
    referenced_claims: set[str] = set()
    used_copy: set[str] = set()

    with context.group("exact.references", "copy", "all copy references resolve"):
        for layer_id, copy_id, _ in _copy_layers(context):
            used_copy.add(copy_id)
            if copy_id not in copy_blocks:
                context.fail(
                    "exact.references",
                    layer_id,
                    Severity.BLOCKER,
                    f"copy layer references unknown block {copy_id}",
                    "Bind the layer to an existing copy block.",
                )
                continue
            copy_block = copy_blocks[copy_id]
            for exact_id in copy_block.exact_data_refs:
                referenced_exact.add(exact_id)
                if exact_id not in exact:
                    context.fail(
                        "exact.references",
                        copy_id,
                        Severity.BLOCKER,
                        f"copy references unknown exact data {exact_id}",
                        "Create the exact-data record or remove the reference.",
                    )
            for claim_id in copy_block.claim_refs:
                referenced_claims.add(claim_id)
                if claim_id not in claims:
                    context.fail(
                        "exact.references",
                        copy_id,
                        Severity.BLOCKER,
                        f"copy references unknown claim {claim_id}",
                        "Create the claim record or remove the reference.",
                    )

    with context.group(
        "exact.critical", "commercial", "no unapproved critical commercial data is required"
    ):
        for layer_id, copy_id, required in _copy_layers(context):
            bound_copy = copy_blocks.get(copy_id)
            if bound_copy is None:
                continue
            if required and bound_copy.status is CopyStatus.HELD:
                context.fail(
                    "exact.critical",
                    layer_id,
                    Severity.BLOCKER,
                    f"required layer uses held copy {bound_copy.id}: {bound_copy.text}",
                    "Remove the layer, provide approved copy, or mark it optional.",
                )
            for exact_id in bound_copy.exact_data_refs:
                record = exact.get(exact_id)
                if record is None:
                    continue
                expired = record.expires_at is not None and (
                    (parsed := parse_timestamp(record.expires_at)) is not None
                    and parsed <= context.now
                )
                if expired or record.status is DataStatus.STALE:
                    context.fail(
                        "exact.critical",
                        layer_id,
                        Severity.BLOCKER,
                        f"{record.field.value} data {record.id} is stale or expired",
                        "Refresh the value and reapprove it.",
                    )
                    continue
                if record.field in CRITICAL_EXACT_FIELDS:
                    if record.status is not DataStatus.APPROVED:
                        context.fail(
                            "exact.critical",
                            layer_id,
                            Severity.BLOCKER,
                            f"required {record.field.value} uses {record.status.value} "
                            f"data {record.id}; commercial terms need approval",
                            "Remove the commercial layer or obtain an approved value.",
                        )
                elif record.status in {DataStatus.HELD, DataStatus.REJECTED}:
                    context.fail(
                        "exact.critical",
                        layer_id,
                        Severity.BLOCKER,
                        f"required layer uses {record.status.value} "
                        f"{record.field.value} data {record.id}",
                        "Remove the layer or resolve the data hold.",
                    )
                elif record.status in {DataStatus.OBSERVED, DataStatus.PROPOSED}:
                    context.warn(
                        "exact.identifiers",
                        layer_id,
                        f"{record.field.value} {record.id} is {record.status.value}; "
                        "Gate 1 must approve this identifier or wording",
                        "Record the value in the Gate 1 scope before production.",
                    )

    with context.group("exact.claims", "claims", "all used claims are verified and worded"):
        for layer_id, copy_id, _ in _copy_layers(context):
            bound_copy = copy_blocks.get(copy_id)
            if bound_copy is None:
                continue
            for claim_id in bound_copy.claim_refs:
                claim = claims.get(claim_id)
                if claim is None:
                    continue
                if claim.status is not ClaimStatus.VERIFIED:
                    context.fail(
                        "exact.claims",
                        layer_id,
                        Severity.BLOCKER,
                        f"uses {claim.status.value} claim {claim.id}: {claim.text}",
                        "Verify the claim or remove it from the copy.",
                    )
                elif not claim.approved_wording:
                    context.fail(
                        "exact.claims",
                        layer_id,
                        Severity.BLOCKER,
                        f"claim {claim.id} has no approved advertising wording",
                        "Obtain approved wording or remove the claim.",
                    )
                elif " ".join(claim.approved_wording.split()).lower() not in " ".join(
                    bound_copy.text.split()
                ).lower():
                    context.warn(
                        "exact.claims",
                        layer_id,
                        f"copy does not contain the approved wording for {claim.id}",
                        "Use the approved wording or record a new approval.",
                    )

    with context.group("exact.orphans", "exact", "every exact record is accounted for"):
        for record in plan.exact_data:
            if record.id not in referenced_exact and record.status is DataStatus.APPROVED:
                context.warn(
                    "exact.orphans",
                    record.id,
                    "approved exact data is not used by any copy layer",
                    "Remove it or bind it to the layer that needs it.",
                )
        for copy_block in plan.copy_blocks:
            if copy_block.id not in used_copy:
                context.warn(
                    "exact.orphans",
                    copy_block.id,
                    "copy block is not used by any layer",
                    "Remove it or bind it to a layer.",
                )

    with context.group(
        "exact.attribution", "exact", "approved values carry an attributable approval"
    ):
        for record in plan.exact_data:
            if record.status is DataStatus.APPROVED and (
                not record.approved_by or not record.approved_at
            ):
                context.add(
                    "exact.attribution",
                    record.id,
                    Severity.BLOCKER,
                    ValidationStatus.FAIL,
                    "approved exact data lacks an approver or timestamp",
                    "Record who approved the value and when.",
                )
