"""Independent, fresh-context critique of a production plan.

The critique does not read the planner's reasoning. It inspects the plan and the
brief, ranks findings, and returns the three inputs that most improve the plan.
"""

from __future__ import annotations

from typing import Any

from .models import (
    CRITICAL_EXACT_FIELDS,
    TEXT_LAYER_ROLES,
    BindingKind,
    BriefRevision,
    CopyStatus,
    CritiqueFinding,
    CritiqueReport,
    DataStatus,
    Disposition,
    Owner,
    ProductionPlan,
    RightsStatus,
    Severity,
    ValidationReport,
)


def _safe_rect(plan: ProductionPlan) -> tuple[int, int, int, int]:
    area = plan.deliverable.safe_area
    return (
        area.left,
        area.top,
        plan.deliverable.width - area.right,
        plan.deliverable.height - area.bottom,
    )


def _priority_key(finding: CritiqueFinding) -> tuple[float, str]:
    return (-finding.priority, finding.id)


def critique_plan(
    plan: ProductionPlan,
    brief: BriefRevision,
    validation: ValidationReport | None = None,
) -> CritiqueReport:
    findings: list[CritiqueFinding] = []

    def add(
        category: str,
        severity: Severity,
        observation: str,
        evidence: str,
        proposed_action: str,
        impact: int,
        confidence: int,
        effort: int,
        blocking_weight: int,
        target_ids: list[str],
        owner: Owner,
    ) -> None:
        findings.append(
            CritiqueFinding(
                id=f"CF-{len(findings) + 1:02d}",
                category=category,
                severity=severity,
                observation=observation,
                evidence=evidence,
                proposed_action=proposed_action,
                impact=impact,
                confidence=confidence,
                effort=effort,
                blocking_weight=blocking_weight,
                target_ids=target_ids,
                owner=owner,
            )
        )

    # 1. Safe area -------------------------------------------------------
    left, top, right, bottom = _safe_rect(plan)
    unsafe = []
    for layer in plan.layers:
        if layer.role not in TEXT_LAYER_ROLES:
            continue
        rect = layer.rect
        if rect.x < left or rect.y < top or rect.right > right or rect.bottom > bottom:
            unsafe.append(layer)
    if unsafe:
        add(
            category="safe_area",
            severity=Severity.HIGH,
            observation=(
                f"{len(unsafe)} text layers cross the platform safe area, so captions "
                "or headlines can sit under the interface or be cropped."
            ),
            evidence=(
                f"Safe rect is x{left}-{right}, y{top}-{bottom}. "
                + "; ".join(
                    f"{layer.id} {layer.role.value} at "
                    f"{layer.rect.x},{layer.rect.y},{layer.rect.w},{layer.rect.h}"
                    for layer in unsafe
                )
            ),
            proposed_action=(
                "Move the affected text above the bottom inset and inside the side "
                "insets, then rerun the structural validator."
            ),
            impact=4,
            confidence=5,
            effort=1,
            blocking_weight=2,
            target_ids=[layer.id for layer in unsafe],
            owner=Owner.PLANNER,
        )

    # 2. Unapproved commercial data -------------------------------------
    exact_map = plan.exact_map
    copy_map = plan.copy_map
    commercial_targets: list[str] = []
    commercial_copy: list[str] = []
    commercial_values: list[str] = []
    for layer in plan.layers:
        if not layer.required or layer.binding_kind is not BindingKind.COPY:
            continue
        copy_block = copy_map.get(layer.binding_ref or "")
        if copy_block is None:
            continue
        critical = [
            exact_map[exact_id]
            for exact_id in copy_block.exact_data_refs
            if exact_id in exact_map
            and exact_map[exact_id].field in CRITICAL_EXACT_FIELDS
            and exact_map[exact_id].status is not DataStatus.APPROVED
        ]
        if copy_block.status is CopyStatus.HELD or critical:
            commercial_targets.append(layer.id)
            commercial_copy.append(copy_block.id)
            commercial_values.extend(
                f"{record.field.value}={record.value} ({record.status.value})"
                for record in critical
            )
    if commercial_targets:
        add(
            category="commercial_data",
            severity=Severity.BLOCKER,
            observation=(
                "The ready cut requires price, promotion or another commercial value "
                "that has been observed but not approved."
            ),
            evidence=(
                f"Layers {sorted(set(commercial_targets))} use copy "
                f"{sorted(set(commercial_copy))} with {sorted(set(commercial_values))}."
            ),
            proposed_action=(
                "Remove the commercial layers from the ready cut, record a held item, "
                "and ask the brand to approve the exact value and terms."
            ),
            impact=5,
            confidence=5,
            effort=2,
            blocking_weight=3,
            target_ids=sorted(set(commercial_targets + commercial_copy)),
            owner=Owner.HUMAN,
        )

    # 3. Budget ---------------------------------------------------------
    budget = plan.budget
    if budget.total_usd > budget.cap_usd:
        largest = sorted(plan.estimates, key=lambda item: item.amount_usd, reverse=True)[:3]
        add(
            category="budget",
            severity=Severity.HIGH,
            observation=(
                f"The estimated production total is {budget.total_usd:.2f} "
                f"{budget.currency} against a {budget.cap_usd:.2f} cap, before any "
                "fallback is triggered."
            ),
            evidence=(
                f"Shared {budget.shared_usd:.2f} + shot {budget.shot_usd:.2f} + "
                f"variant {budget.variant_usd:.2f} + {budget.retry_reserve_pct:.0f}% "
                f"reserve {budget.reserve_usd:.2f}. Largest: "
                + ", ".join(f"{item.id} {item.amount_usd:.2f}" for item in largest)
            ),
            proposed_action=(
                "Remove a redundant route or lower the estimate so total plus the "
                "critical fallback fits the cap."
            ),
            impact=4,
            confidence=5,
            effort=2,
            blocking_weight=2,
            target_ids=[estimate.id for estimate in plan.estimates],
            owner=Owner.PLANNER,
        )

    # 4. Text density ---------------------------------------------------
    for shot in plan.shots:
        copy_layers = [
            plan.layer_map[layer_id]
            for layer_id in shot.layer_ids
            if layer_id in plan.layer_map and plan.layer_map[layer_id].role in TEXT_LAYER_ROLES
        ]
        if shot.duration_frames < 90 and len(copy_layers) > 2:
            add(
                category="text_density",
                severity=Severity.HIGH,
                observation=(
                    f"{shot.id} carries {len(copy_layers)} text layers in "
                    f"{shot.duration_frames / plan.deliverable.fps:.1f}s."
                ),
                evidence=", ".join(f"{layer.id}:{layer.role.value}" for layer in copy_layers),
                proposed_action=(
                    "Keep the headline and caption; move the third message to another "
                    "shot or remove it."
                ),
                impact=4,
                confidence=4,
                effort=2,
                blocking_weight=2,
                target_ids=[shot.id] + [layer.id for layer in copy_layers],
                owner=Owner.PLANNER,
            )

    # 5. Missing fallback for an exact asset ----------------------------
    for asset in plan.assets:
        if asset.exactness.value != "exact":
            continue
        required = any(
            layer.required
            and layer.binding_kind is BindingKind.ASSET
            and layer.binding_ref == asset.id
            for layer in plan.layers
        )
        if not required or not asset.fallback_required:
            continue
        has_alternate = asset.fallback_asset_id is not None or any(
            asset.id in alternate.target_ids for alternate in plan.alternates
        )
        has_hold = any(asset.id in item.affects for item in plan.held_items)
        if not has_alternate:
            add(
                category="missing_fallback",
                severity=Severity.MEDIUM,
                observation=(
                    f"Critical exact asset {asset.id} has no executable alternate route"
                    + ("; a hold exists but Level 2 still has no fallback." if has_hold else ".")
                ),
                evidence=f"{asset.name}; route {asset.route.value}",
                proposed_action=(
                    "Add a viable capture or supplied-asset fallback, and keep the "
                    "hold as a separate condition."
                ),
                impact=3,
                confidence=4,
                effort=2,
                blocking_weight=2,
                target_ids=[asset.id],
                owner=Owner.PLANNER,
            )

    # 6. Unknown rights -------------------------------------------------
    for asset in plan.assets:
        if asset.rights.status is not RightsStatus.UNKNOWN:
            continue
        required = any(
            layer.required
            and layer.binding_kind is BindingKind.ASSET
            and layer.binding_ref == asset.id
            for layer in plan.layers
        ) or any(cue.essential and cue.asset_id == asset.id for cue in plan.audio_cues)
        if required:
            add(
                category="rights_unknown",
                severity=Severity.MEDIUM,
                observation=f"Required asset {asset.id} has no identified licence.",
                evidence=f"{asset.name}; rights status unknown",
                proposed_action=(
                    "Select a licensable track or asset, record the licence, and name a fallback."
                ),
                impact=3,
                confidence=4,
                effort=2,
                blocking_weight=2,
                target_ids=[asset.id],
                owner=Owner.PLANNER,
            )

    # 7. Reading speed --------------------------------------------------
    for layer in plan.layers:
        if layer.role not in TEXT_LAYER_ROLES or layer.binding_ref is None:
            continue
        copy_block = copy_map.get(layer.binding_ref)
        if copy_block is None:
            continue
        seconds = layer.duration_frames / plan.deliverable.fps
        cps = len(copy_block.text) / seconds if seconds > 0 else 999
        if cps > plan.deliverable.caption_rules.max_cps:
            add(
                category="reading_speed",
                severity=Severity.HIGH,
                observation=(f"{copy_block.id} reads at {cps:.1f} characters per second."),
                evidence=f"Layer {layer.id}, {layer.duration_frames} frames",
                proposed_action="Shorten the copy or hold it longer.",
                impact=4,
                confidence=4,
                effort=1,
                blocking_weight=2,
                target_ids=[layer.id, copy_block.id],
                owner=Owner.PLANNER,
            )

    # 8. Hook timing ----------------------------------------------------
    first_shot = min(plan.shots, key=lambda shot: shot.start_frame)
    hook_layers = []
    for layer_id in first_shot.layer_ids:
        hook_layer = plan.layer_map.get(layer_id)
        if (
            hook_layer is None
            or hook_layer.role.value != "typography"
            or not hook_layer.binding_ref
        ):
            continue
        copy_block = plan.copy_map.get(hook_layer.binding_ref)
        if copy_block is not None and copy_block.role.value == "hook":
            hook_layers.append(hook_layer)
    if not hook_layers or min(layer.start_frame for layer in hook_layers) > 25:
        add(
            category="hook_timing",
            severity=Severity.MEDIUM,
            observation="The first shot does not land a hook in the first second.",
            evidence=(
                f"First shot {first_shot.id}, hook layers {[layer.id for layer in hook_layers]}"
            ),
            proposed_action="Place the hook copy by frame 25 of the first shot.",
            impact=4,
            confidence=3,
            effort=1,
            blocking_weight=2,
            target_ids=[first_shot.id],
            owner=Owner.PLANNER,
        )

    # 9. Product visibility ---------------------------------------------
    product_layers = [layer for layer in plan.layers if layer.role.value == "product"]
    if not product_layers:
        add(
            category="product_visibility",
            severity=Severity.HIGH,
            observation="The plan has no product layer.",
            evidence="No layer role is 'product'.",
            proposed_action="Add a product layer bound to exact pack art.",
            impact=5,
            confidence=5,
            effort=2,
            blocking_weight=3,
            target_ids=[brief.project_id],
            owner=Owner.PLANNER,
        )
    else:
        first_product = min(
            plan.shot_map[layer.shot_id].start_frame + layer.start_frame for layer in product_layers
        )
        if first_product > plan.deliverable.frame_count // 2:
            add(
                category="product_visibility",
                severity=Severity.MEDIUM,
                observation="The product appears after the halfway point.",
                evidence=f"First product frame {first_product}.",
                proposed_action="Move the pack reveal earlier.",
                impact=4,
                confidence=3,
                effort=2,
                blocking_weight=2,
                target_ids=[layer.id for layer in product_layers],
                owner=Owner.PLANNER,
            )

    # Validation cross-check -------------------------------------------
    if validation is not None:
        for finding in validation.findings:
            if finding.status.value != "fail":
                continue
            if finding.rule in {
                "layer.safe_area",
                "exact.critical",
                "budget.cap",
                "budget.worst_case",
            }:
                continue
            if not any(finding.target in item.target_ids for item in findings):
                add(
                    category="validator_failure",
                    severity=Severity.HIGH,
                    observation=f"Structural validator failed: {finding.rule}.",
                    evidence=finding.detail,
                    proposed_action=finding.remediation,
                    impact=4,
                    confidence=5,
                    effort=2,
                    blocking_weight=2,
                    target_ids=[finding.target],
                    owner=Owner.PLANNER,
                )

    ranked = sorted(findings, key=_priority_key)
    top3 = [finding.id for finding in ranked[:3]]
    if not findings:
        summary = (
            "No material findings. The ready plan has no unapproved commercial layer, "
            "no safe-area violation, no over-cap estimate and no unknown rights on a "
            "required asset. Remaining warnings are Gate 1 conditions."
        )
    else:
        summary = (
            f"{len(findings)} findings. The three highest-impact inputs are "
            + ", ".join(f"{finding.id} ({finding.category})" for finding in ranked[:3])
            + ". The critic reviewed the plan artifact, not the planner's reasoning."
        )

    return CritiqueReport(
        project_id=plan.project_id,
        plan_revision=plan.revision,
        plan_hash=plan.plan_hash(),
        summary=summary,
        findings=findings,
        top3=top3,
    )


def build_resolution_inputs(report: CritiqueReport) -> list[dict[str, Any]]:
    """Map the top three findings to a planner action.

    Returned as plain dictionaries so the service can build typed records and
    keep the human-readable decision text in one place.
    """

    ranked = sorted(
        (finding for finding in report.findings if finding.id in report.top3),
        key=_priority_key,
    )
    result: list[dict[str, Any]] = []
    for rank, finding in enumerate(ranked, start=1):
        if finding.category == "commercial_data":
            mode, status = "human", "escalated"
            decision = (
                "Remove the commercial layer from the ready cut and hold the exact "
                "value and terms for a named brand decision."
            )
            changes = [
                "Removed the commercial layer and its held copy from the ready cut.",
                "Recorded a held item with the evidence needed to clear the value.",
            ]
        elif finding.category == "safe_area":
            mode, status = "auto", "resolved"
            decision = "Move every text layer inside the platform safe area."
            changes = [
                "Moved affected captions and headlines inside the safe insets.",
                "Re-ran the structural safe-area validator.",
            ]
        elif finding.category == "budget":
            mode, status = "auto", "resolved"
            decision = "Remove redundant routes so total plus fallback fits the cap."
            changes = [
                "Removed the redundant route and its estimate.",
                "Kept one costed fallback inside the cap.",
            ]
        elif finding.category == "text_density":
            mode, status = "auto", "resolved"
            decision = "Reduce the affected shot to a readable text stack."
            changes = ["Removed non-essential text from the shot."]
        elif finding.category == "rights_unknown":
            mode, status = "auto", "resolved"
            decision = "Name a licensable route and a fallback for the asset."
            changes = ["Recorded the licence route and a fallback requirement."]
        elif finding.category == "missing_fallback":
            mode, status = "auto", "resolved"
            decision = "Add a capture route and a no-hero-asset alternate."
            changes = ["Added the fallback asset and alternate route."]
        elif finding.category == "reading_speed":
            mode, status = "auto", "resolved"
            decision = "Shorten or extend the affected copy."
            changes = ["Adjusted the copy hold to the caption reading limit."]
        else:
            mode, status = "human", "escalated"
            decision = "Escalate the finding to Gate 1."
            changes = [finding.proposed_action]
        result.append(
            {
                "finding_id": finding.id,
                "rank": rank,
                "mode": mode,
                "status": status,
                "decision": decision,
                "changes": changes,
                "impacted_ids": finding.target_ids,
                "owner": finding.owner.value,
                "disposition": (
                    Disposition.ESCALATED.value
                    if status == "escalated"
                    else Disposition.RESOLVED.value
                ),
            }
        )
    return result
