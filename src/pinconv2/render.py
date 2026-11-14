"""Markdown renderers and the Level 2 handoff.

The JSON records remain the source of truth. These functions render the exact
same revision for a human reader.
"""

from __future__ import annotations

from .models import (
    BriefRevision,
    CheckStatus,
    ConceptNote,
    CritiqueReport,
    Gate1Approval,
    Gate1Packet,
    HandoffAsset,
    HandoffShot,
    Level2Handoff,
    ProductionPlan,
    ResearchPack,
    RightsStatus,
    ValidationReport,
)


def _table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell.replace("|", "/") for cell in row) + " |")
    return "\n".join(lines)


def _bool(value: bool) -> str:
    return "yes" if value else "no"


def render_concept_note(
    brief: BriefRevision, research: ResearchPack, concept: ConceptNote
) -> str:
    lines: list[str] = [
        f"# Concept Note - {brief.title}",
        "",
        f"**Project:** {concept.project_id}  ",
        f"**Concept revision:** {concept.revision}  ",
        f"**Brief revision:** {concept.brief_revision}  ",
        f"**Content family:** {brief.content_family.value}  ",
        f"**Duration / frame:** {brief.duration_seconds:.1f}s, "
        f"{brief.fps} fps, {brief.aspect_ratio}",
        "",
        "## Brief",
        "",
        "> " + brief.source_text.replace("\n", " "),
        "",
        "## Audience",
        "",
        concept.audience_summary,
        "",
        "## Objective",
        "",
        concept.objective,
        "",
        "## Evidence",
        "",
        concept.evidence_summary,
        "",
        "### Sources",
        "",
        _table(
            ["ID", "Source", "Accessed", "Channels", "Reliability"],
            [
                [
                    source.id,
                    f"[{source.title}]({source.locator})"
                    if source.locator.startswith("http")
                    else source.title,
                    source.accessed_at,
                    ", ".join(source.channels),
                    source.reliability.value,
                ]
                for source in research.sources
            ],
        ),
        "",
        "### Findings",
        "",
        _table(
            ["ID", "Observation", "Decision", "Status", "Confidence"],
            [
                [
                    finding.id,
                    finding.observation,
                    finding.proposed_action,
                    finding.status.value,
                    str(finding.confidence),
                ]
                for finding in research.findings
            ],
        ),
        "",
        "## Concept options",
        "",
        _table(
            [
                "ID",
                "Concept",
                "Audience",
                "Clarity",
                "Distinct",
                "Quality",
                "Cost",
                "Revision",
                "Total",
            ],
            [
                [
                    option.id,
                    f"**{option.name}** - {option.one_liner}",
                    str(option.scores.audience_fit),
                    str(option.scores.clarity),
                    str(option.scores.distinctiveness),
                    str(option.scores.achievable_quality),
                    str(option.scores.cost_efficiency),
                    str(option.scores.revision_simplicity),
                    str(option.scores.total),
                ]
                for option in concept.options
            ],
        ),
        "",
        f"**Recommendation:** {concept.recommended_option_id}.",
        "",
    ]
    for option in concept.options:
        lines.extend(
            [
                f"### {option.id} - {option.name}",
                "",
                f"**Hook:** {option.hook}",
                "",
                option.treatment,
                "",
                f"**Visual style:** {option.visual_style}",
                "",
                f"**Sound:** {option.sound}",
                "",
                f"**Why:** {option.rationale}",
                "",
                "**Risks:** " + ("; ".join(option.risks) if option.risks else "none"),
                "",
            ]
        )
    lines.extend(
        [
            "## Hook options",
            "",
            _table(
                ["ID", "Hook", "Why", "Risk"],
                [
                    [hook.id, f"**{hook.text}**", hook.rationale, hook.risk or "none"]
                    for hook in concept.hooks
                ],
            ),
            "",
            "## Why this treatment",
            "",
            f"**Hook:** {concept.why_hook}",
            "",
            f"**Script:** {concept.why_script}",
            "",
            f"**Look:** {concept.why_look}",
            "",
            f"**Sound:** {concept.why_sound}",
            "",
            "## Decisions",
            "",
            _table(
                ["ID", "Decision", "Evidence", "Rationale"],
                [
                    [
                        decision.id,
                        decision.selected,
                        ", ".join(decision.finding_ids),
                        decision.rationale,
                    ]
                    for decision in concept.decisions
                ],
            ),
            "",
            "## Open questions",
            "",
        ]
    )
    lines.extend(f"- {question}" for question in concept.open_questions)
    lines.append("")
    return "\n".join(lines)


def render_production_plan(
    brief: BriefRevision,
    research: ResearchPack,
    plan: ProductionPlan,
    validation: ValidationReport,
    critique: CritiqueReport,
    approval: Gate1Approval | None,
) -> str:
    deliverable = plan.deliverable
    lines: list[str] = [
        f"# Production Plan - {brief.title}",
        "",
        f"**Project:** {plan.project_id}  ",
        f"**Plan revision:** {plan.revision}  ",
        f"**Plan hash:** `{plan.plan_hash()}`  ",
        f"**Brief revision:** {plan.brief_revision}  ",
        f"**Validation:** {'PASS' if validation.passed else 'FAIL'}  ",
        "**Gate 1:** "
        + (
            f"approved by {approval.approver} ({approval.approver_role})"
            if approval
            else "not approved"
        ),
        "",
        "## 1. Deliverable",
        "",
        _table(
            ["Field", "Value"],
            [
                ["Format", f"{deliverable.width}x{deliverable.height}, {deliverable.aspect_ratio}"],
                ["Frame rate", f"{deliverable.fps} fps"],
                ["Frames", str(deliverable.frame_count)],
                ["Duration", f"{deliverable.duration_seconds:.2f}s"],
                ["Placement", f"{deliverable.platform} / {deliverable.placement}"],
                ["Captions", _bool(deliverable.sound_off_legible)],
                [
                    "Safe area",
                    f"top {deliverable.safe_area.top}, bottom "
                    f"{deliverable.safe_area.bottom}, left {deliverable.safe_area.left}, "
                    f"right {deliverable.safe_area.right}",
                ],
                [
                    "Caption rules",
                    f"{deliverable.caption_rules.max_lines} lines, "
                    f"{deliverable.caption_rules.max_chars_per_line} chars/line, "
                    f"{deliverable.caption_rules.max_cps} cps, "
                    f"{deliverable.caption_rules.min_hold_frames} frame minimum",
                ],
            ],
        ),
        "",
        "## 2. Must-have coverage",
        "",
        _table(
            ["ID", "Must-have", "Status", "Evidence"],
            [
                [item.id, item.text, item.status, ", ".join(item.satisfied_by)]
                for item in brief.must_have
            ],
        ),
        "",
        "## 3. Beat sheet",
        "",
        _table(
            ["Beat", "Frames", "Purpose", "Spoken", "On screen", "Emotion"],
            [
                [
                    beat.id,
                    f"[{beat.start_frame},{beat.end_frame})",
                    beat.purpose,
                    beat.spoken_line or "-",
                    beat.on_screen_copy or "-",
                    beat.emotion,
                ]
                for beat in plan.beats
            ],
        ),
        "",
        "## 4. Shot plan",
        "",
        _table(
            ["Shot", "Frames", "Time", "Picture", "Method", "Fallback", "Status"],
            [
                [
                    shot.id,
                    f"[{shot.start_frame},{shot.end_frame})",
                    f"{shot.start_frame / deliverable.fps:.2f}-"
                    f"{shot.end_frame / deliverable.fps:.2f}s",
                    f"{shot.framing} {shot.action}",
                    shot.method,
                    shot.fallback_method,
                    shot.status.value,
                ]
                for shot in plan.shots
            ],
        ),
        "",
        "## 5. Shot x Layer x Asset",
        "",
    ]

    for shot in plan.shots:
        lines.extend(
            [
                f"### {shot.id} - {shot.purpose}",
                "",
                f"**Framing:** {shot.framing}  ",
                f"**Movement:** {shot.movement}  ",
                f"**Lighting:** {shot.lighting}  ",
                f"**Palette:** {shot.palette}  ",
                f"**Continuity:** {shot.continuity}  ",
                f"**Transition in:** {shot.transition_in}",
                "",
            ]
        )
        layers = [
            plan.layer_map[layer_id]
            for layer_id in shot.layer_ids
            if layer_id in plan.layer_map
        ]
        lines.append(
            _table(
                ["Layer", "Role", "Frames", "Rect", "Binding", "Exact", "Req", "Protected"],
                [
                    [
                        layer.id,
                        layer.role.value,
                        f"{layer.start_frame}-{layer.end_frame}",
                        f"{layer.rect.x},{layer.rect.y},{layer.rect.w},{layer.rect.h}",
                        f"{layer.binding_kind.value}:{layer.binding_ref or '-'}",
                        layer.exactness.value,
                        _bool(layer.required),
                        _bool(layer.protected) if layer.protected else "-",
                    ]
                    for layer in layers
                ],
            )
        )
        lines.append("")

    lines.extend(
        [
            "## 6. Asset requirements",
            "",
            _table(
                [
                    "Asset",
                    "Name",
                    "Route",
                    "Rights",
                    "Exact",
                    "Specification",
                    "Estimate",
                    "Fallback",
                    "Used by",
                ],
                [
                    [
                        asset.id,
                        asset.name,
                        asset.route.value,
                        asset.rights.status.value,
                        asset.exactness.value,
                        f"{asset.tech.format}; "
                        + (
                            f"{asset.tech.width}x{asset.tech.height}"
                            if asset.tech.width and asset.tech.height
                            else "no fixed raster"
                        ),
                        (
                            f"{plan.estimate_map[asset.estimate_id].amount_usd:.2f}"
                            if asset.estimate_id and asset.estimate_id in plan.estimate_map
                            else "-"
                        ),
                        asset.fallback_asset_id or "-",
                        ", ".join(asset.used_by) or "-",
                    ]
                    for asset in plan.assets
                ],
            ),
            "",
            "## 7. Copy blocks",
            "",
            _table(
                ["Copy", "Role", "Status", "Text", "Exact data", "Claims"],
                [
                    [
                        block.id,
                        block.role.value,
                        block.status.value,
                        block.text,
                        ", ".join(block.exact_data_refs) or "-",
                        ", ".join(block.claim_refs) or "-",
                    ]
                    for block in plan.copy_blocks
                ],
            ),
            "",
            "## 8. Exact data register",
            "",
            _table(
                ["ID", "Field", "Value", "Status", "Source", "Notes"],
                [
                    [
                        item.id,
                        item.field.value,
                        item.value,
                        item.status.value,
                        item.source_id or "-",
                        item.notes or "-",
                    ]
                    for item in plan.exact_data
                ],
            ),
            "",
            "## 9. Claims register",
            "",
            _table(
                ["ID", "Claim", "Status", "Approved wording", "Limitation"],
                [
                    [
                        claim.id,
                        claim.text,
                        claim.status.value,
                        claim.approved_wording or "-",
                        claim.limitations or "-",
                    ]
                    for claim in plan.claims
                ],
            ),
            "",
            "## 10. Audio",
            "",
            _table(
                ["Cue", "Frames", "Kind", "Description", "Asset", "Level", "Essential"],
                [
                    [
                        cue.id,
                        f"[{cue.start_frame},{cue.end_frame})",
                        cue.kind.value,
                        cue.description,
                        cue.asset_id or "-",
                        f"{cue.level_db} dB" if cue.level_db is not None else "-",
                        _bool(cue.essential),
                    ]
                    for cue in plan.audio_cues
                ],
            ),
            "",
            "## 11. Transitions",
            "",
            _table(
                ["ID", "From", "To", "Frame", "Kind", "Frames"],
                [
                    [
                        transition.id,
                        transition.from_shot_id,
                        transition.to_shot_id,
                        str(transition.at_frame),
                        transition.kind,
                        str(transition.duration_frames),
                    ]
                    for transition in plan.transitions
                ],
            ),
            "",
            "## 12. Alternate routes",
            "",
            _table(
                ["ID", "Targets", "Trigger", "Preserved", "Cost delta", "Scope"],
                [
                    [
                        alternate.id,
                        ", ".join(alternate.target_ids),
                        alternate.trigger,
                        alternate.preserved,
                        f"{alternate.cost_delta_usd:.2f}",
                        ", ".join(alternate.approval_scope),
                    ]
                    for alternate in plan.alternates
                ],
            ),
            "",
            "## 13. Budget",
            "",
            _table(
                ["ID", "Item", "Kind", "Amount USD", "Basis", "Confidence"],
                [
                    [
                        estimate.id,
                        estimate.label,
                        estimate.kind.value,
                        f"{estimate.amount_usd:.2f}",
                        estimate.basis.value,
                        estimate.confidence,
                    ]
                    for estimate in plan.estimates
                ],
            ),
            "",
            _table(
                ["Budget line", "USD"],
                [
                    ["Shared", f"{plan.budget.shared_usd:.2f}"],
                    ["Shot", f"{plan.budget.shot_usd:.2f}"],
                    ["Variant", f"{plan.budget.variant_usd:.2f}"],
                    ["Subtotal", f"{plan.budget.subtotal_usd:.2f}"],
                    [
                        f"Retry reserve ({plan.budget.retry_reserve_pct:.0f}%)",
                        f"{plan.budget.reserve_usd:.2f}",
                    ],
                    ["Total", f"{plan.budget.total_usd:.2f}"],
                    ["Fallback", f"{plan.budget.fallback_usd:.2f}"],
                    ["Worst case", f"{plan.budget.worst_case_usd:.2f}"],
                    ["Cap", f"{plan.budget.cap_usd:.2f}"],
                ],
            ),
            "",
            "## 14. Acceptance checks",
            "",
            _table(
                ["ID", "Check", "Method", "Level", "Status", "Targets"],
                [
                    [
                        check.id,
                        check.description,
                        check.method.value,
                        check.level.value,
                        validation.check_status.get(check.id, CheckStatus.PENDING).value,
                        ", ".join(check.target_ids),
                    ]
                    for check in plan.checks
                ],
            ),
            "",
            "## 15. Holds",
            "",
            _table(
                ["ID", "Hold", "Reason", "Affects", "Evidence needed", "Owner"],
                [
                    [
                        item.id,
                        item.title,
                        item.reason,
                        ", ".join(item.affects),
                        item.required_evidence,
                        item.owner.value,
                    ]
                    for item in plan.held_items
                ],
            ),
            "",
            "## 16. Decisions",
            "",
            _table(
                ["ID", "Decision", "Evidence", "Rationale"],
                [
                    [
                        decision.id,
                        decision.selected,
                        ", ".join(decision.finding_ids),
                        decision.rationale,
                    ]
                    for decision in plan.decisions
                ],
            ),
            "",
            "## 17. Validation summary",
            "",
            f"**Passed:** {_bool(validation.passed)}  ",
            f"**Failures:** {len(validation.failures)}  ",
            f"**Warnings:** {len(validation.warnings)}",
            "",
            _table(
                ["ID", "Rule", "Target", "Status", "Detail"],
                [
                    [
                        finding.id,
                        finding.rule,
                        finding.target,
                        finding.status.value,
                        finding.detail,
                    ]
                    for finding in validation.findings
                    if finding.status.value in {"fail", "warn"}
                ]
                or [["-", "-", "-", "-", "No failures or warnings."]],
            ),
            "",
            "## 18. Critique and top three",
            "",
            critique.summary,
            "",
            _table(
                ["ID", "Category", "Severity", "Priority", "Owner", "Disposition", "Action"],
                [
                    [
                        finding.id,
                        finding.category,
                        finding.severity.value,
                        f"{finding.priority:.1f}",
                        finding.owner.value,
                        finding.disposition.value,
                        finding.proposed_action,
                    ]
                    for finding in critique.findings
                ]
                or [["-", "-", "-", "-", "-", "-", "No findings."]],
            ),
            "",
            "## 19. Gate 1 conditions",
            "",
        ]
    )
    if approval is not None:
        lines.extend(f"- {condition}" for condition in approval.conditions)
    else:
        lines.append("Not approved. Conditions are listed in the Gate 1 packet.")
    lines.extend(
        [
            "",
            "## 20. Research basis",
            "",
            _table(
                ["ID", "Source", "Accessed", "Reliability"],
                [
                    [
                        source.id,
                        source.title,
                        source.accessed_at,
                        source.reliability.value,
                    ]
                    for source in research.sources
                ],
            ),
            "",
        ]
    )
    return "\n".join(lines)


def render_gate_packet(
    packet: Gate1Packet,
    plan: ProductionPlan,
    validation: ValidationReport,
    critique: CritiqueReport,
) -> str:
    lines = [
        "# Gate 1 packet",
        "",
        f"**Project:** {packet.project_id}  ",
        f"**Plan revision:** {packet.plan_revision}  ",
        f"**Plan hash:** `{packet.plan_hash}`  ",
        f"**Validation:** {'PASS' if packet.validation_passed else 'FAIL'}  ",
        "**Approval:** "
        + (
            f"{packet.approval.approver} ({packet.approval.approver_role})"
            if packet.approval
            else "pending a named human"
        ),
        "",
        "## Ready shots",
        "",
    ]
    lines.extend(f"- {shot_id}" for shot_id in packet.ready_shots or ["none"])
    lines.extend(["", "## Held layers", ""])
    lines.extend(f"- {layer_id}" for layer_id in packet.held_layers or ["none"])
    lines.extend(["", "## Conditions", ""])
    lines.extend(f"- {condition}" for condition in packet.conditions or ["none"])
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in packet.blockers or ["none"])
    lines.extend(["", "## Top-three input status", ""])
    lines.extend(
        f"- {finding_id}: {status}"
        for finding_id, status in packet.input_statuses.items()
    )
    if not packet.input_statuses:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Evidence",
            "",
            f"- Validation findings: {len(validation.findings)} "
            f"({len(validation.failures)} fail, {len(validation.warnings)} warn)",
            f"- Critique findings: {len(critique.findings)}",
            f"- Shots in plan: {len(plan.shots)}",
            f"- Assets in plan: {len(plan.assets)}",
            "",
            "Approval is bound to the plan revision and hash above. A changed plan "
            "creates a new revision and invalidates this packet.",
            "",
        ]
    )
    return "\n".join(lines)


def _rights_action(status: RightsStatus) -> str:
    return {
        RightsStatus.CLEARED: "Cleared. Keep any required attribution.",
        RightsStatus.NEEDS_APPROVAL: "Obtain written approval before render.",
        RightsStatus.UNKNOWN: "Identify a licence before render.",
        RightsStatus.BLOCKED: "Do not use.",
        RightsStatus.REFERENCE_ONLY: "Reference only; do not bind.",
        RightsStatus.NOT_APPLICABLE: "No media rights apply.",
    }[status]


def build_handoff(
    plan: ProductionPlan, approval: Gate1Approval, validation: ValidationReport
) -> Level2Handoff:
    approved = set(approval.scope)
    shots = [shot for shot in plan.shots if shot.id in approved]
    layers = [
        layer
        for layer in plan.layers
        if layer.shot_id in approved
    ]
    asset_ids = {
        layer.binding_ref
        for layer in layers
        if layer.binding_kind.value == "asset" and layer.binding_ref
    }
    asset_ids.update(
        cue.asset_id for cue in plan.audio_cues if cue.asset_id is not None
    )
    handoff_shots = [
        HandoffShot(
            shot_id=shot.id,
            start_frame=shot.start_frame,
            end_frame=shot.end_frame,
            method=shot.method,
            fallback_method=shot.fallback_method,
            layer_ids=shot.layer_ids,
            asset_ids=shot.asset_ids,
            check_ids=shot.check_ids,
        )
        for shot in shots
    ]
    handoff_assets: list[HandoffAsset] = []
    for asset_id in sorted(asset_ids):
        asset = plan.asset_map.get(asset_id)
        if asset is None:
            continue
        estimate = (
            plan.estimate_map[asset.estimate_id].amount_usd
            if asset.estimate_id and asset.estimate_id in plan.estimate_map
            else 0.0
        )
        specification = f"{asset.tech.format}"
        if asset.tech.width and asset.tech.height:
            specification += f", {asset.tech.width}x{asset.tech.height}"
        if asset.tech.transparency:
            specification += ", transparency"
        if asset.tech.notes:
            specification += f". {asset.tech.notes}"
        handoff_assets.append(
            HandoffAsset(
                asset_id=asset.id,
                name=asset.name,
                route=asset.route,
                rights_status=asset.rights.status,
                rights_action=_rights_action(asset.rights.status),
                exactness=asset.exactness,
                specification=specification,
                estimate_usd=estimate,
                fallback_asset_id=asset.fallback_asset_id,
            )
        )

    approved_exact: set[str] = set()
    for layer in layers:
        if layer.binding_kind.value != "copy" or not layer.binding_ref:
            continue
        copy_block = plan.copy_map.get(layer.binding_ref)
        if copy_block is None:
            continue
        for exact_id in copy_block.exact_data_refs:
            record = plan.exact_map.get(exact_id)
            if record is not None and record.status.value not in {"held", "rejected"}:
                approved_exact.add(exact_id)

    pending_checks = [
        check.id
        for check in plan.checks
        if validation.check_status.get(check.id) is CheckStatus.PENDING
    ]
    return Level2Handoff(
        project_id=plan.project_id,
        plan_revision=plan.revision,
        plan_hash=plan.plan_hash(),
        approval=approval,
        shots=handoff_shots,
        assets=handoff_assets,
        pending_checks=pending_checks,
        conditions=approval.conditions,
        exact_data_approved=sorted(approved_exact),
    )
