"""Typed Level 2 contracts.

The records in this module are the source of truth for a Level 2 run. Every
number that reaches a build sheet or a budget document is derived from these
records, and every record points back to the approved Level 1 IDs it serves.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any

from pydantic import Field, model_validator

from ..models import (
    SafeArea,
    StrictModel,
    VariantEffectOverride,
    VariantLayerOverride,
    content_hash,
    utc_now,
)

# ---------------------------------------------------------------------------
# enums
# ---------------------------------------------------------------------------


class RunState(str, Enum):
    HANDOFF_VALIDATED = "handoff_validated"
    METHOD_PLANNED = "method_planned"
    CAPTURE_PLANNED = "capture_planned"
    QUOTED = "quoted"
    BUDGET_APPROVED = "budget_approved"
    SOURCING = "sourcing"
    PROBES_PASSED = "probes_passed"
    ASSETS_PROCESSED = "assets_processed"
    SHOT_PACKAGES_READY = "shot_packages_ready"
    GATE2_READY = "gate2_ready"
    ROUGH_CUT_REVIEWED = "rough_cut_reviewed"
    APPROVED = "approved"
    BLOCKED = "blocked"


class TruthClass(str, Enum):
    EXACT = "exact"
    EXACT_TEXT = "exact_text"
    PROOF = "proof"
    REPRESENTATIVE = "representative"
    ATMOSPHERIC = "atmospheric"
    EDITORIAL = "editorial"


class Impact(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Method(str, Enum):
    M0 = "M0"
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"
    M4 = "M4"
    M5 = "M5"
    M6 = "M6"
    M7 = "M7"
    M8 = "M8"


class SourceStrategy(str, Enum):
    SUPPLIED = "supplied"
    OWNED = "owned"
    STOCK = "stock"
    CAPTURE = "capture"
    GENERATE = "generate"
    PROCEDURAL = "procedural"


class LicenceClass(str, Enum):
    PD = "PD"
    CC0 = "CC0"
    CC_BY = "CC-BY"
    CC_BY_SA = "CC-BY-SA"
    CC_BY_NC = "CC-BY-NC"
    CC_BY_ND = "CC-BY-ND"
    PROPRIETARY_FREE = "PROPRIETARY-FREE"
    EDITORIAL = "EDITORIAL"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class GateVerdict(str, Enum):
    PASS = "pass"
    HOLD = "hold"
    BLOCK = "block"


class TaskStatus(str, Enum):
    PLANNED = "planned"
    READY = "ready"
    SOURCED = "sourced"
    PROBED = "probed"
    PROCESSED = "processed"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"
    CONDITIONAL = "conditional"


class PickMode(str, Enum):
    HUMAN = "human"
    AUTOMATIC = "automatic"
    PENDING = "pending"


class Batch(str, Enum):
    B0 = "B0"
    B1 = "B1"
    B2 = "B2"
    B3 = "B3"
    B4 = "B4"
    B5 = "B5"


class PacketStatus(str, Enum):
    READY = "ready_for_approval"
    APPROVED = "approved"
    BLOCKED = "blocked"


class GateName(str, Enum):
    GATE_2A = "2a"
    GATE_2B = "2b"
    GATE_2C = "2c"


class CheckState(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class CorrectionDecision(str, Enum):
    APPROVE = "approve"
    CHANGE = "change"
    REJECT = "reject"


class CorrectionStatus(str, Enum):
    OPEN = "open"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    APPLIED = "applied"
    SUPERSEDED = "superseded"


class QcVerdict(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


# ---------------------------------------------------------------------------
# planning records
# ---------------------------------------------------------------------------


class AssetIntent(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    name: str = Field(min_length=1, max_length=200)
    route: str = Field(min_length=1, max_length=40)
    truth_class: TruthClass
    impact: Impact
    scope: str = Field(pattern=r"^(approved|conditional_fallback)$")
    exactness: str = Field(min_length=1, max_length=40)
    specification: str = Field(min_length=1, max_length=1000)
    acceptance: str = Field(min_length=1, max_length=1000)
    estimate_id: str | None = Field(default=None, pattern=r"^ES-\d{2}$")
    estimate_usd: float = Field(ge=0)
    fallback_asset_id: str | None = Field(default=None, pattern=r"^AS-\d{2}$")
    dependencies: list[str] = Field(default_factory=list)
    rights_status: str = Field(min_length=1, max_length=40)
    holds: list[str] = Field(default_factory=list)
    used_by: list[str] = Field(default_factory=list)
    disclosure_required: bool = False
    notes: str | None = Field(default=None, max_length=1000)


class MethodCandidate(StrictModel):
    candidate_id: str = Field(pattern=r"^CND-[A-Z0-9-]+$")
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    provider: str = Field(min_length=1, max_length=100)
    url: str = Field(min_length=1, max_length=1000)
    licence_class: LicenceClass
    licence_url: str | None = Field(default=None, max_length=1000)
    attribution: str | None = Field(default=None, max_length=500)
    origin_verified: bool = False
    scriptable: bool = True
    fit_score: int = Field(ge=0, le=100)
    technical_match: bool = True
    cost_usd: float = Field(ge=0)
    preview_path: str | None = None
    gate_verdict: GateVerdict = GateVerdict.HOLD
    gate_reasons: list[str] = Field(default_factory=list)


class LayerMethodDecision(StrictModel):
    layer_id: str = Field(pattern=r"^LY-\d{3}$")
    shot_id: str = Field(pattern=r"^SH-\d{2}$")
    role: str = Field(min_length=1, max_length=40)
    truth_class: TruthClass
    truth_class_rule: str = Field(pattern=r"^R[1-5]$")
    impact_score: int = Field(ge=0, le=9)
    impact: Impact
    impact_signals: list[str] = Field(default_factory=list)
    method: Method
    method_reason: str = Field(min_length=1, max_length=80)
    method_note: str = Field(min_length=1, max_length=500)
    asset_id: str | None = Field(default=None, pattern=r"^AS-\d{2}$")
    candidates: list[MethodCandidate] = Field(default_factory=list)
    chosen_candidate: str | None = None
    fallback_method: Method
    probe_required: bool = False
    probe_id: str | None = None
    pick_mode: PickMode = PickMode.PENDING
    rights_gate: GateVerdict = GateVerdict.HOLD
    cost_usd: float = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def probe_follows_method(self) -> LayerMethodDecision:
        needs_probe = self.method in {
            Method.M2,
            Method.M3,
            Method.M4,
            Method.M5,
            Method.M6,
            Method.M7,
        }
        if self.probe_required != needs_probe:
            raise ValueError(f"{self.layer_id}: probe_required must be {needs_probe}")
        if self.chosen_candidate and self.chosen_candidate not in {
            candidate.candidate_id for candidate in self.candidates
        }:
            raise ValueError(f"{self.layer_id}: chosen candidate is not in the list")
        return self


class ProcessingOp(StrictModel):
    op: str = Field(min_length=1, max_length=40)
    params: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def op_is_known(self) -> ProcessingOp:
        if self.op not in ALLOWED_OPS:
            raise ValueError(f"unknown processing op: {self.op}")
        return self


ALLOWED_OPS = frozenset(
    {
        "trim",
        "crop",
        "scale",
        "pad",
        "conform",
        "speed_ramp",
        "stabilise",
        "denoise",
        "sharpen",
        "grade",
        "alpha_cutout",
        "despill",
        "mask_generate",
        "composite",
        "text_render",
        "loudness_norm",
        "resample",
        "channel_map",
        "fade",
        "encode",
    }
)


class GenerationSpec(StrictModel):
    provider: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=200)
    prompt: str = Field(min_length=1, max_length=4000)
    negative_prompt: str | None = Field(default=None, max_length=2000)
    seed: int | None = None
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    duration_seconds: float | None = Field(default=None, gt=0)
    reference_images: list[str] = Field(default_factory=list)
    disclosure_required: bool = True
    disclosure_text: str | None = Field(default=None, max_length=200)
    cost_usd: float = Field(default=0, ge=0)
    budget_line_id: str | None = None


class FlowSpec(StrictModel):
    batch: Batch
    dependencies: list[str] = Field(default_factory=list)
    stage: str = Field(min_length=1, max_length=40)
    critical_path: bool = False


class AssetProductionTask(StrictModel):
    task_id: str = Field(pattern=r"^APT-AS-\d{2}$")
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    source_strategy: SourceStrategy
    methods: list[Method] = Field(min_length=1)
    processing: list[ProcessingOp] = Field(default_factory=list)
    generation: GenerationSpec | None = None
    capture_ref: str | None = None
    budget_line_ids: list[str] = Field(default_factory=list)
    flow: FlowSpec
    acceptance: str = Field(min_length=1, max_length=1000)
    probe_required: bool = False
    conditional: bool = False
    status: TaskStatus = TaskStatus.PLANNED
    blockers: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def generation_matches_strategy(self) -> AssetProductionTask:
        if self.source_strategy is SourceStrategy.GENERATE and self.generation is None:
            raise ValueError(f"{self.task_id}: generate strategy needs a generation spec")
        if self.source_strategy is not SourceStrategy.GENERATE and self.generation is not None:
            raise ValueError(f"{self.task_id}: only generated assets carry a generation spec")
        return self


class CaptureMember(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    role: str = Field(min_length=1, max_length=120)
    frame_rate: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=500)


class CaptureSessionPlan(StrictModel):
    session_id: str = Field(pattern=r"^CAP-\d{2}$")
    members: list[CaptureMember] = Field(min_length=1)
    foley: list[str] = Field(default_factory=list)
    marginal_items: list[str] = Field(default_factory=list)
    studio: str = Field(min_length=1, max_length=200)
    hand_model_release: str = Field(min_length=1, max_length=200)
    release_hold: str = Field(pattern=r"^HI-\d{2}$")
    cost_usd: float = Field(ge=0)
    estimate_id: str = Field(pattern=r"^ES-\d{2}$")
    shot_list: list[str] = Field(min_length=1)
    colour_target: str = Field(min_length=1, max_length=200)
    audio_rig: str = Field(min_length=1, max_length=200)
    acceptance: str = Field(min_length=1, max_length=1000)

    def covers(self, asset_id: str) -> bool:
        return any(member.asset_id == asset_id for member in self.members)


class SoundCuePlan(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    kind: str = Field(min_length=1, max_length=40)
    method: Method
    description: str = Field(min_length=1, max_length=500)
    in_frame: int = Field(ge=0)
    out_frame: int = Field(gt=0)
    edit_points: list[int] = Field(default_factory=list)
    loudness_target: str = Field(default="lufs=-16,tp=-1.0", max_length=100)
    content_id_risk: str = Field(default="low", pattern=r"^(low|medium|high)$")
    disclosure_required: bool = False
    hold: str | None = Field(default=None, pattern=r"^HI-\d{2}$")


class SoundPlan(StrictModel):
    cues: list[SoundCuePlan] = Field(min_length=1)
    master_loudness: str = Field(default="lufs=-16,tp=-1.0", max_length=100)
    sound_off_message: str = Field(min_length=1, max_length=300)
    notes: str | None = Field(default=None, max_length=1000)


# ---------------------------------------------------------------------------
# budget
# ---------------------------------------------------------------------------


class BudgetLine(StrictModel):
    line_id: str = Field(pattern=r"^BL-\d{3}$")
    label: str = Field(min_length=1, max_length=200)
    estimate_id: str | None = Field(default=None, pattern=r"^ES-\d{2}$")
    asset_id: str | None = Field(default=None, pattern=r"^AS-\d{2}$")
    asset_ids: list[str] = Field(default_factory=list)
    kind: str = Field(pattern=r"^(acquisition|capture|processing|project|variant|fallback)$")
    amount_usd: float = Field(ge=0)
    basis: str = Field(pattern=r"^(verified_quote|operator_estimate)$")
    quote_ref: str | None = Field(default=None, max_length=200)
    quote_expires_at: str | None = None
    dedupe_key: str | None = Field(default=None, max_length=100)
    in_worst_case: bool = False
    unpriced: bool = False
    notes: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def quote_is_specific(self) -> BudgetLine:
        if self.basis == "verified_quote" and not self.quote_ref:
            raise ValueError(f"{self.line_id}: a verified quote needs a reference")
        if self.unpriced and self.amount_usd != 0:
            raise ValueError(f"{self.line_id}: an unpriced line must be zero")
        return self


class BudgetSummary(StrictModel):
    currency: str = Field(default="USD", min_length=3, max_length=3)
    cap_usd: float = Field(gt=0)
    reserve_pct: float = Field(ge=0, le=50)
    subtotal_usd: float = Field(ge=0)
    reserve_usd: float = Field(ge=0)
    total_usd: float = Field(ge=0)
    fallback_usd: float = Field(ge=0)
    worst_usd: float = Field(ge=0)
    headroom_usd: float
    within_cap: bool
    worst_within_cap: bool
    verified_quote_usd: float = Field(default=0, ge=0)
    operator_estimate_usd: float = Field(default=0, ge=0)
    unpriced_lines: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def arithmetic_holds(self) -> BudgetSummary:
        if round(self.subtotal_usd + self.reserve_usd, 2) != self.total_usd:
            raise ValueError("budget total must equal subtotal plus reserve")
        if round(self.total_usd + self.fallback_usd, 2) != self.worst_usd:
            raise ValueError("worst case must equal total plus fallbacks")
        if round(self.cap_usd - self.worst_usd, 2) != self.headroom_usd:
            raise ValueError("headroom must equal cap minus worst case")
        return self


class BudgetEstimate(StrictModel):
    lines: list[BudgetLine] = Field(min_length=1)
    summary: BudgetSummary
    raw_attributed_usd: float = Field(default=0, ge=0)
    dedupe_savings_usd: float = Field(default=0, ge=0)
    created_at: str = Field(default_factory=utc_now)

    def line_map(self) -> dict[str, BudgetLine]:
        return {line.line_id: line for line in self.lines}


# ---------------------------------------------------------------------------
# flow
# ---------------------------------------------------------------------------


class FlowNode(StrictModel):
    node_id: str = Field(min_length=1, max_length=40)
    kind: str = Field(pattern=r"^(asset|capture|shot|variant|audio)$")
    batch: Batch
    dependencies: list[str] = Field(default_factory=list)
    critical_path: bool = False
    duration_frames: int = Field(default=0, ge=0)


class FlowGraph(StrictModel):
    nodes: list[FlowNode] = Field(min_length=1)
    batches: dict[str, list[str]] = Field(default_factory=dict)
    critical_path: list[str] = Field(default_factory=list)
    acyclic: bool


# ---------------------------------------------------------------------------
# build sheet
# ---------------------------------------------------------------------------


class Correction(StrictModel):
    id: str = Field(pattern=r"^COR-\d{3}$")
    item_kind: str = Field(pattern=r"^(asset|layer|shot|variant|budget)$")
    item_id: str = Field(min_length=2, max_length=20)
    decision: CorrectionDecision
    instruction: str = Field(min_length=1, max_length=1000)
    reason: str = Field(min_length=1, max_length=1000)
    requested_by: str = Field(min_length=2, max_length=200)
    created_at: str = Field(default_factory=utc_now)
    status: CorrectionStatus = CorrectionStatus.OPEN
    affects: list[str] = Field(default_factory=list)


class FileDigest(StrictModel):
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    bytes: int = Field(ge=0)


class LayerBinding(StrictModel):
    layer_id: str = Field(pattern=r"^LY-\d{3}$")
    shot_id: str = Field(pattern=r"^SH-\d{2}$")
    asset_id: str | None = Field(default=None, pattern=r"^AS-\d{2}$")
    copy_id: str | None = Field(default=None, pattern=r"^CP-\d{2}$")
    method: Method
    z_order: int = Field(ge=0)
    start_frame: int = Field(ge=0)
    end_frame: int = Field(gt=0)
    transform: str = Field(min_length=1, max_length=200)
    status: TaskStatus


class AssetPackage(StrictModel):
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    name: str = Field(min_length=1, max_length=200)
    truth_class: TruthClass
    impact: Impact
    methods: list[Method] = Field(min_length=1)
    source: str = Field(min_length=1, max_length=300)
    processing: list[str] = Field(default_factory=list)
    output_path: str | None = None
    output_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    bindings: list[str] = Field(default_factory=list)
    acceptance: str = Field(min_length=1, max_length=1000)
    probe_id: str | None = None
    rights_status: str = Field(min_length=1, max_length=40)
    hold: str | None = None
    conditional: bool = False
    status: TaskStatus
    blockers: list[str] = Field(default_factory=list)


class ShotPackage(StrictModel):
    shot_id: str = Field(pattern=r"^SH-\d{2}$")
    start_frame: int = Field(ge=0)
    end_frame: int = Field(gt=0)
    method: str = Field(min_length=1, max_length=300)
    layers: list[LayerBinding] = Field(min_length=1)
    effects: list[str] = Field(default_factory=list)
    audio: list[str] = Field(default_factory=list)
    checks: list[str] = Field(default_factory=list)
    preview_path: str | None = None
    ready: bool = False
    blockers: list[str] = Field(default_factory=list)


class VariantLayerResolution(StrictModel):
    layer_id: str = Field(pattern=r"^LY-\d{3}$")
    resolution: str = Field(pattern=r"^(override|carried|missing)$")
    notes: str | None = Field(default=None, max_length=300)


class VariantPackage(StrictModel):
    variant_id: str = Field(min_length=1, max_length=20)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    fps: int = Field(gt=0)
    frame_count: int = Field(gt=0)
    safe_area: SafeArea
    safe_area_basis: str = Field(min_length=1, max_length=300)
    resolutions: list[VariantLayerResolution] = Field(min_length=1)
    layer_overrides: list[VariantLayerOverride] = Field(default_factory=list)
    effect_masks: list[VariantEffectOverride] = Field(default_factory=list)
    effect_overrides: list[str] = Field(default_factory=list)
    cost_usd: float = Field(ge=0)
    check_ids: list[str] = Field(default_factory=list)
    check_status: str = Field(default="pending", pattern=r"^(pending|pass|fail)$")
    ready: bool = False
    blockers: list[str] = Field(default_factory=list)


class TimelineEntry(StrictModel):
    entry_id: str = Field(pattern=r"^TL-\d{3}$")
    track: str = Field(pattern=r"^(layer|audio|caption)$")
    ref_id: str = Field(min_length=1, max_length=20)
    shot_id: str | None = Field(default=None, pattern=r"^SH-\d{2}$")
    start_frame: int = Field(ge=0)
    end_frame: int = Field(gt=0)
    note: str | None = Field(default=None, max_length=300)


class Timeline(StrictModel):
    fps: int = Field(gt=0)
    frame_count: int = Field(gt=0)
    entries: list[TimelineEntry] = Field(min_length=1)
    caption_files: dict[str, str] = Field(default_factory=dict)


class BuildSheetManifest(StrictModel):
    schema_version: str = Field(default="2.0", pattern=r"^\d+\.\d+$")
    run_id: str = Field(min_length=1, max_length=40)
    project_id: str = Field(min_length=1, max_length=80)
    plan_revision: int = Field(ge=1)
    source_plan_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    bundle_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    packet_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    generated_at: str = Field(default_factory=utc_now)
    parts: dict[str, FileDigest] = Field(default_factory=dict)
    counts: dict[str, int] = Field(default_factory=dict)
    budget: BudgetSummary


class BuildSheet(StrictModel):
    manifest: BuildSheetManifest
    assets: list[AssetPackage] = Field(min_length=1)
    shots: list[ShotPackage] = Field(min_length=1)
    variants: list[VariantPackage] = Field(default_factory=list)
    timeline: Timeline
    corrections: list[Correction] = Field(default_factory=list)

    def asset_map(self) -> dict[str, AssetPackage]:
        return {asset.asset_id: asset for asset in self.assets}

    def sheet_hash(self) -> str:
        return content_hash(self)


# ---------------------------------------------------------------------------
# probes, corrections and QC
# ---------------------------------------------------------------------------


class ProbeRecord(StrictModel):
    probe_id: str = Field(pattern=r"^PR-[A-Z0-9-]+$")
    asset_id: str = Field(pattern=r"^AS-\d{2}$")
    layer_ids: list[str] = Field(min_length=1)
    method: Method
    sample_path: str | None = None
    acceptance_ref: str = Field(min_length=1, max_length=200)
    verdict: GateVerdict = GateVerdict.HOLD
    reviewer: str = Field(default="pending", max_length=100)
    reviewed_at: str | None = None
    expires_at: str | None = None
    notes: str | None = Field(default=None, max_length=500)


class QcFinding(StrictModel):
    id: str = Field(pattern=r"^QC-\d{3}$")
    stage: str = Field(pattern=r"^(technical|visual|semantic|rights|budget)$")
    check: str = Field(min_length=1, max_length=80)
    target: str = Field(min_length=1, max_length=100)
    verdict: QcVerdict
    detail: str = Field(min_length=1, max_length=1000)
    remediation: str | None = Field(default=None, max_length=500)


class QcReport(StrictModel):
    stage: str = Field(pattern=r"^(technical|visual|semantic|rights|budget)$")
    verdict: QcVerdict
    findings: list[QcFinding] = Field(min_length=1)
    reviewer: str = Field(min_length=1, max_length=100)
    created_at: str = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def verdict_matches_findings(self) -> QcReport:
        worst = QcVerdict.PASS
        for finding in self.findings:
            if finding.verdict is QcVerdict.FAIL:
                worst = QcVerdict.FAIL
                break
            if finding.verdict is QcVerdict.WARN:
                worst = QcVerdict.WARN
        if self.verdict is not worst:
            raise ValueError("QC verdict must match the worst finding")
        return self


class GateCheck(StrictModel):
    id: str = Field(pattern=r"^G2[ABC]-\d{2}$")
    name: str = Field(min_length=1, max_length=100)
    state: CheckState
    detail: str = Field(min_length=1, max_length=1000)
    evidence: str | None = Field(default=None, max_length=300)


class GatePacket(StrictModel):
    gate: GateName
    run_id: str = Field(min_length=1, max_length=40)
    project_id: str = Field(min_length=1, max_length=80)
    plan_revision: int = Field(ge=1)
    plan_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    status: PacketStatus
    checks: list[GateCheck] = Field(min_length=1)
    blockers: list[str] = Field(default_factory=list)
    summary: str = Field(min_length=1, max_length=1000)
    approved_by: str | None = Field(default=None, max_length=200)
    approved_at: str | None = None
    approval_evidence: str | None = Field(default=None, max_length=300)
    created_at: str = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def blocked_packets_explain_themselves(self) -> GatePacket:
        if self.status is PacketStatus.BLOCKED and not self.blockers:
            raise ValueError("a blocked packet needs at least one blocker")
        if self.status is PacketStatus.APPROVED and not self.approved_by:
            raise ValueError("an approved packet needs an approver")
        return self


class Level2Plan(StrictModel):
    run_id: str = Field(min_length=1, max_length=40)
    project_id: str = Field(min_length=1, max_length=80)
    plan_revision: int = Field(ge=1)
    plan_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    state: RunState
    intents: list[AssetIntent] = Field(min_length=1)
    decisions: list[LayerMethodDecision] = Field(min_length=1)
    tasks: list[AssetProductionTask] = Field(min_length=1)
    capture: CaptureSessionPlan
    sound: SoundPlan
    budget: BudgetEstimate
    flow: FlowGraph
    variants: list[VariantPackage] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)

    def decision_map(self) -> dict[str, LayerMethodDecision]:
        return {decision.layer_id: decision for decision in self.decisions}

    def task_map(self) -> dict[str, AssetProductionTask]:
        return {task.asset_id: task for task in self.tasks}

    def intent_map(self) -> dict[str, AssetIntent]:
        return {intent.asset_id: intent for intent in self.intents}


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
