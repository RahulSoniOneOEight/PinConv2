"""Typed Level 1 contracts.

The machine-readable records in this module are the source of truth for a
Level 1 run. Markdown notes and the Level 2 handoff are rendered from them.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def content_hash(value: BaseModel) -> str:
    """Hash a record without its creation timestamp.

    A plan revision must hash identically when rebuilt from the same inputs so
    that an approval cannot drift because a clock moved.
    """

    payload = value.model_dump(mode="json")
    payload.pop("created_at", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


# ---------------------------------------------------------------------------
# enums
# ---------------------------------------------------------------------------


class ProjectState(str, Enum):
    INIT = "init"
    INTAKE = "intake"
    RESEARCH = "research"
    TREATMENT = "treatment"
    SHOT_PLAN = "shot_plan"
    VALIDATED = "validated"
    CRITIQUED = "critiqued"
    INPUTS_UPDATED = "inputs_updated"
    GATE1_READY = "gate1_ready"
    APPROVED = "approved"
    FAILED = "failed"


class ContentFamily(str, Enum):
    AD = "ad"
    PRODUCT_SHOWCASE = "product_showcase"
    PROMO_REEL = "promo_reel"
    NARRATIVE_BRAND_FILM = "narrative_brand_film"
    EXPLAINER = "explainer"
    TUTORIAL = "tutorial"
    NURSERY_RHYME = "nursery_rhyme"
    ANIME_STORY = "anime_story"
    FLAT_2D_CARTOON = "flat_2d_cartoon"
    ENTERTAINMENT_SHORT = "entertainment_short"
    COMMENTARY = "commentary"
    DOCUMENTARY = "documentary"


class Tag(str, Enum):
    PREMIUM = "premium"
    WARM = "warm"
    PLAYFUL = "playful"
    URGENT = "urgent"
    CALM = "calm"
    INFORMATIVE = "informative"
    HUMOROUS = "humorous"
    CINEMATIC = "cinematic"


class Outcome(str, Enum):
    SELL = "sell"
    TELL = "tell"
    TEACH = "teach"
    ENTERTAIN = "entertain"


class ProductRole(str, Enum):
    HERO = "hero"
    SUPPORT = "support"
    ABSENT = "absent"


class QualityTier(str, Enum):
    DRAFT = "draft"
    STANDARD = "standard"
    PREMIUM = "premium"
    HERO = "hero"


class AssetReadiness(str, Enum):
    NONE = "none"
    PARTIAL = "partial"
    COMPLETE = "complete"


class EvidenceReliability(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    REFERENCE = "reference"
    ASSUMPTION = "assumption"


class FindingStatus(str, Enum):
    VERIFIED = "verified"
    ASSUMPTION = "assumption"
    UNVERIFIED = "unverified"
    STALE = "stale"
    HELD = "held"
    CONFLICT = "conflict"


class RightsStatus(str, Enum):
    CLEARED = "cleared"
    NEEDS_APPROVAL = "needs_approval"
    UNKNOWN = "unknown"
    BLOCKED = "blocked"
    REFERENCE_ONLY = "reference_only"
    NOT_APPLICABLE = "not_applicable"


class Exactness(str, Enum):
    EXACT = "exact"
    APPROVED_COPY = "approved_copy"
    ILLUSTRATIVE = "illustrative"


class CopyRole(str, Enum):
    HOOK = "hook"
    HEADLINE = "headline"
    SUBHEAD = "subhead"
    OFFER = "offer"
    CTA = "cta"
    CAPTION = "caption"
    DISCLAIMER = "disclaimer"
    LEGAL = "legal"


class CopyStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    HELD = "held"
    REJECTED = "rejected"


class ExactField(str, Enum):
    PRODUCT_NAME = "product_name"
    BRAND_NAME = "brand_name"
    ORIGIN = "origin"
    PRICE = "price"
    OFFER = "offer"
    PROMO_CODE = "promo_code"
    PACK_SIZE = "pack_size"
    CTA = "cta"
    CLAIM = "claim"
    LOGO = "logo"
    DISCLAIMER = "disclaimer"


class DataStatus(str, Enum):
    APPROVED = "approved"
    PROPOSED = "proposed"
    OBSERVED = "observed"
    HELD = "held"
    STALE = "stale"
    REJECTED = "rejected"


CRITICAL_EXACT_FIELDS: frozenset[ExactField] = frozenset(
    {
        ExactField.PRICE,
        ExactField.OFFER,
        ExactField.PROMO_CODE,
        ExactField.CLAIM,
        ExactField.PACK_SIZE,
    }
)


class ClaimStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    HELD = "held"
    REJECTED = "rejected"


class LayerRole(str, Enum):
    BACKGROUND = "background"
    SUBJECT = "subject"
    PRODUCT = "product"
    PACK_LABEL = "pack_label"
    LOGO = "logo"
    EFFECT = "effect"
    TYPOGRAPHY = "typography"
    CAPTION = "caption"
    CAPTION_PLATE = "caption_plate"
    CTA = "cta"
    OFFER = "offer"
    DISCLAIMER = "disclaimer"
    GRADE = "grade"


TEXT_LAYER_ROLES: frozenset[LayerRole] = frozenset(
    {
        LayerRole.TYPOGRAPHY,
        LayerRole.CAPTION,
        LayerRole.CTA,
        LayerRole.OFFER,
        LayerRole.DISCLAIMER,
    }
)

BOUND_VISUAL_ROLES: frozenset[LayerRole] = frozenset(
    {
        LayerRole.BACKGROUND,
        LayerRole.SUBJECT,
        LayerRole.PRODUCT,
        LayerRole.PACK_LABEL,
        LayerRole.LOGO,
    }
)

UNBOUND_ROLES: frozenset[LayerRole] = frozenset(
    {LayerRole.EFFECT, LayerRole.CAPTION_PLATE, LayerRole.GRADE}
)


class BindingKind(str, Enum):
    ASSET = "asset"
    COPY = "copy"
    NONE = "none"


class AssetRoute(str, Enum):
    OWNED = "owned"
    SUPPLIED = "supplied"
    TO_SOURCE = "to_source"
    TO_CAPTURE = "to_capture"
    TO_CREATE = "to_create"
    TO_GENERATE = "to_generate"


class AssetStatus(str, Enum):
    READY = "ready"
    PENDING = "pending"
    BLOCKED = "blocked"


class EstimateKind(str, Enum):
    SHARED = "shared"
    SHOT = "shot"
    VARIANT = "variant"
    FALLBACK = "fallback"


class EstimateBasis(str, Enum):
    OPERATOR_ESTIMATE = "operator_estimate"
    VERIFIED_QUOTE = "verified_quote"


class AudioKind(str, Enum):
    VO = "vo"
    MUSIC = "music"
    SFX = "sfx"
    AMBIENCE = "ambience"


class ShotStatus(str, Enum):
    READY = "ready"
    HELD = "held"
    BLOCKED = "blocked"


class CheckMethod(str, Enum):
    STRUCTURAL = "structural"
    STATIC_PREVIEW = "static_preview"
    RENDER_PIXEL = "render_pixel"
    AUDIO = "audio"
    HUMAN = "human"


class CheckLevel(str, Enum):
    L1 = "level_1"
    L2 = "level_2"


class CheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"
    NOT_APPLICABLE = "not_applicable"


class Severity(str, Enum):
    BLOCKER = "blocker"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


class Disposition(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    ACCEPTED = "accepted"


class Owner(str, Enum):
    PLANNER = "planner"
    HUMAN = "human"


class ResolutionMode(str, Enum):
    AUTO = "auto"
    HUMAN = "human"


class ResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    PENDING = "pending"


# ---------------------------------------------------------------------------
# geometry and brief
# ---------------------------------------------------------------------------


class Rect(StrictModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    w: int = Field(gt=0)
    h: int = Field(gt=0)

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h

    def within(self, width: int, height: int) -> bool:
        return self.right <= width and self.bottom <= height

    def contains(self, other: Rect) -> bool:
        return (
            self.x <= other.x
            and self.y <= other.y
            and self.right >= other.right
            and self.bottom >= other.bottom
        )

    def intersects(self, other: Rect) -> bool:
        return not (
            self.right <= other.x
            or other.right <= self.x
            or self.bottom <= other.y
            or other.bottom <= self.y
        )

    def intersection_area(self, other: Rect) -> int:
        if not self.intersects(other):
            return 0
        width = min(self.right, other.right) - max(self.x, other.x)
        height = min(self.bottom, other.bottom) - max(self.y, other.y)
        return max(width, 0) * max(height, 0)


class SafeArea(StrictModel):
    top: int = Field(ge=0)
    bottom: int = Field(ge=0)
    left: int = Field(ge=0)
    right: int = Field(ge=0)

    def rect(self, canvas_width: int, canvas_height: int) -> Rect:
        return Rect(
            x=self.left,
            y=self.top,
            w=canvas_width - self.left - self.right,
            h=canvas_height - self.top - self.bottom,
        )


class CaptionRules(StrictModel):
    max_lines: int = Field(ge=1, le=4)
    max_chars_per_line: int = Field(ge=8, le=80)
    max_cps: float = Field(gt=0, le=40)
    min_hold_frames: int = Field(ge=1)


class MustHave(StrictModel):
    id: str = Field(pattern=r"^MH-\d{2}$")
    text: str = Field(min_length=1, max_length=300)
    satisfied_by: list[str] = Field(default_factory=list)
    status: str = Field(default="partial", pattern=r"^(satisfied|partial|unmet)$")


class BriefRevision(StrictModel):
    project_id: str
    revision: int = Field(ge=1)
    source_text: str = Field(min_length=50, max_length=6000)
    title: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=1000)
    audience: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en", min_length=2, max_length=20)
    content_family: ContentFamily
    subject: str = Field(min_length=1, max_length=200)
    tones: list[Tag] = Field(min_length=1)
    outcome: Outcome
    product_role: ProductRole
    quality_tier: QualityTier
    asset_readiness: AssetReadiness
    series_pattern: str = Field(default="one-off", max_length=200)
    duration_seconds: float = Field(gt=0, le=600)
    fps: int = Field(ge=1, le=120)
    aspect_ratio: str = Field(pattern=r"^\d{1,2}:\d{1,2}$")
    platform: str = Field(min_length=1, max_length=100)
    placements: list[str] = Field(min_length=1)
    captions: bool
    cta: str | None = Field(default=None, max_length=120)
    budget_cap_usd: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    constraints: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    rights_notes: str | None = Field(default=None, max_length=2000)
    must_have: list[MustHave] = Field(min_length=1)
    classification_confidence: float = Field(default=0.8, ge=0, le=1)
    created_at: str = Field(default_factory=utc_now)


class DeliverableProfile(StrictModel):
    id: str = Field(pattern=r"^DP-\d{2}$")
    platform: str
    placement: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    fps: int = Field(gt=0)
    frame_count: int = Field(gt=0)
    duration_seconds: float = Field(gt=0)
    aspect_ratio: str
    safe_area: SafeArea
    caption_rules: CaptionRules
    cta_copy_id: str | None = None
    variant_id: str = Field(min_length=1)
    sound_off_legible: bool

    @model_validator(mode="after")
    def frames_match_duration(self) -> DeliverableProfile:
        expected = round(self.duration_seconds * self.fps)
        if self.frame_count != expected:
            raise ValueError(f"frame_count {self.frame_count} does not match {expected}")
        return self


# ---------------------------------------------------------------------------
# research
# ---------------------------------------------------------------------------


class ResearchQuestion(StrictModel):
    id: str = Field(pattern=r"^RQ-\d{2}$")
    question: str = Field(min_length=1, max_length=500)
    why_it_matters: str = Field(min_length=1, max_length=500)
    priority: int = Field(ge=1, le=5)
    status: str = Field(default="open", pattern=r"^(open|answered|blocked)$")
    finding_ids: list[str] = Field(default_factory=list)


class EvidenceSource(StrictModel):
    id: str = Field(pattern=r"^SRC-\d{2}$")
    title: str = Field(min_length=1, max_length=300)
    locator: str = Field(min_length=1, max_length=1000)
    accessed_at: str = Field(min_length=10)
    channels: list[str] = Field(min_length=1)
    reliability: EvidenceReliability
    notes: str | None = Field(default=None, max_length=2000)


class Finding(StrictModel):
    id: str = Field(pattern=r"^F-\d{2}$")
    stage: str = Field(min_length=1, max_length=40)
    observation: str = Field(min_length=1, max_length=2000)
    interpretation: str = Field(min_length=1, max_length=2000)
    proposed_action: str = Field(min_length=1, max_length=2000)
    source_id: str
    evidence_locator: str = Field(min_length=1, max_length=500)
    observed_at: str = Field(min_length=10)
    confidence: int = Field(ge=1, le=5)
    status: FindingStatus
    rights_status: RightsStatus
    impact: int = Field(ge=1, le=5)
    effort: int = Field(ge=1, le=5)
    linked_ids: list[str] = Field(default_factory=list)


class ResearchPack(StrictModel):
    project_id: str
    revision: int = Field(ge=1)
    questions: list[ResearchQuestion] = Field(min_length=1)
    sources: list[EvidenceSource] = Field(min_length=1)
    findings: list[Finding] = Field(min_length=1)
    synthesis: str = Field(min_length=1, max_length=4000)
    created_at: str = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def references_resolve(self) -> ResearchPack:
        source_ids = {source.id for source in self.sources}
        for finding in self.findings:
            if finding.source_id not in source_ids:
                raise ValueError(f"{finding.id} references unknown source {finding.source_id}")
        return self


# ---------------------------------------------------------------------------
# concept note
# ---------------------------------------------------------------------------


class ConceptScores(StrictModel):
    audience_fit: int = Field(ge=1, le=5)
    clarity: int = Field(ge=1, le=5)
    distinctiveness: int = Field(ge=1, le=5)
    achievable_quality: int = Field(ge=1, le=5)
    cost_efficiency: int = Field(ge=1, le=5)
    revision_simplicity: int = Field(ge=1, le=5)

    @property
    def total(self) -> int:
        return (
            self.audience_fit
            + self.clarity
            + self.distinctiveness
            + self.achievable_quality
            + self.cost_efficiency
            + self.revision_simplicity
        )


class ConceptOption(StrictModel):
    id: str = Field(pattern=r"^CO-\d{2}$")
    name: str = Field(min_length=1, max_length=120)
    one_liner: str = Field(min_length=1, max_length=300)
    hook: str = Field(min_length=1, max_length=200)
    treatment: str = Field(min_length=1, max_length=2000)
    visual_style: str = Field(min_length=1, max_length=1000)
    sound: str = Field(min_length=1, max_length=1000)
    scores: ConceptScores
    rationale: str = Field(min_length=1, max_length=2000)
    risks: list[str] = Field(default_factory=list)
    linked_finding_ids: list[str] = Field(default_factory=list)


class HookOption(StrictModel):
    id: str = Field(pattern=r"^HK-\d{2}$")
    text: str = Field(min_length=1, max_length=200)
    rationale: str = Field(min_length=1, max_length=1000)
    risk: str | None = Field(default=None, max_length=1000)


class Decision(StrictModel):
    id: str = Field(pattern=r"^DC-\d{2}$")
    finding_ids: list[str] = Field(min_length=1)
    selected: str = Field(min_length=1, max_length=500)
    alternatives: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1, max_length=1500)
    impacted_ids: list[str] = Field(default_factory=list)


class ConceptNote(StrictModel):
    project_id: str
    revision: int = Field(ge=1)
    brief_revision: int = Field(ge=1)
    audience_summary: str = Field(min_length=1, max_length=2000)
    objective: str = Field(min_length=1, max_length=1000)
    evidence_summary: str = Field(min_length=1, max_length=4000)
    options: list[ConceptOption] = Field(min_length=2)
    recommended_option_id: str
    hooks: list[HookOption] = Field(min_length=3, max_length=3)
    why_hook: str = Field(min_length=1, max_length=2000)
    why_script: str = Field(min_length=1, max_length=2000)
    why_look: str = Field(min_length=1, max_length=2000)
    why_sound: str = Field(min_length=1, max_length=2000)
    decisions: list[Decision] = Field(min_length=1)
    open_questions: list[str] = Field(default_factory=list)
    planned_look: str = Field(min_length=1, max_length=2000)
    created_at: str = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def recommendation_exists(self) -> ConceptNote:
        if self.recommended_option_id not in {option.id for option in self.options}:
            raise ValueError("recommended option does not exist")
        return self


# ---------------------------------------------------------------------------
# plan records
# ---------------------------------------------------------------------------


class CopyBlock(StrictModel):
    id: str = Field(pattern=r"^CP-\d{2}$")
    text: str = Field(min_length=1, max_length=300)
    role: CopyRole
    exact_data_refs: list[str] = Field(default_factory=list)
    claim_refs: list[str] = Field(default_factory=list)
    status: CopyStatus
    reading_frames: int = Field(gt=0)
    source: str | None = Field(default=None, max_length=300)
    notes: str | None = Field(default=None, max_length=1000)


class ExactData(StrictModel):
    id: str = Field(pattern=r"^ED-\d{2}$")
    field: ExactField
    value: str = Field(min_length=1, max_length=500)
    status: DataStatus
    source_id: str | None = None
    evidence_locator: str | None = Field(default=None, max_length=500)
    approved_by: str | None = Field(default=None, max_length=200)
    approved_at: str | None = None
    expires_at: str | None = None
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def approval_is_attributable(self) -> ExactData:
        if self.status is DataStatus.APPROVED and (
            not self.approved_by or not self.approved_at
        ):
            raise ValueError("approved exact data needs approved_by and approved_at")
        if self.status is DataStatus.OBSERVED and not self.source_id:
            raise ValueError("observed exact data needs a source")
        if self.status is DataStatus.STALE and not self.expires_at:
            raise ValueError("stale exact data needs expires_at")
        return self


class Claim(StrictModel):
    id: str = Field(pattern=r"^CL-\d{2}$")
    text: str = Field(min_length=1, max_length=500)
    status: ClaimStatus
    source_ids: list[str] = Field(default_factory=list)
    evidence_locator: str | None = Field(default=None, max_length=500)
    approved_wording: str | None = Field(default=None, max_length=500)
    limitations: str | None = Field(default=None, max_length=1000)
    used_in: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def verified_claims_have_evidence(self) -> Claim:
        if self.status is ClaimStatus.VERIFIED and not self.source_ids:
            raise ValueError("verified claim needs a source")
        return self


class Keyframe(StrictModel):
    frame: int = Field(ge=0)
    x: float | None = None
    y: float | None = None
    scale: float | None = Field(default=None, gt=0, le=10)
    opacity: float | None = Field(default=None, ge=0, le=1)
    easing: str = Field(default="linear", max_length=40)


class TextStyle(StrictModel):
    font_family: str = Field(min_length=1, max_length=100)
    size_px: int = Field(ge=8, le=400)
    weight: int = Field(ge=100, le=900)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    align: str = Field(default="left", pattern=r"^(left|center|right)$")
    line_height: float = Field(default=1.1, gt=0.5, le=3)
    tracking: float = Field(default=0, ge=-20, le=40)
    max_lines: int = Field(default=1, ge=1, le=4)


class Layer(StrictModel):
    id: str = Field(pattern=r"^LY-\d{3}$")
    shot_id: str
    start_frame: int = Field(ge=0)
    end_frame: int = Field(gt=0)
    role: LayerRole
    z_order: int = Field(ge=0)
    rect: Rect
    opacity: float = Field(default=1.0, ge=0, le=1)
    fill: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    text_style: TextStyle | None = None
    motion: list[Keyframe] = Field(default_factory=list)
    effect: str | None = Field(default=None, max_length=200)
    non_occluding: bool = False
    protected: bool = False
    protected_regions: list[Rect] = Field(default_factory=list)
    binding_kind: BindingKind
    binding_ref: str | None = None
    exactness: Exactness = Exactness.ILLUSTRATIVE
    required: bool = True
    allowed_edits: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def layer_is_executable(self) -> Layer:
        if self.end_frame <= self.start_frame:
            raise ValueError(f"{self.id} end_frame must be after start_frame")
        if self.binding_kind is BindingKind.NONE:
            if self.role not in UNBOUND_ROLES:
                raise ValueError(f"{self.id} needs an asset or copy binding")
            if not self.fill and not self.effect:
                raise ValueError(f"{self.id} needs a fill or effect")
        elif not self.binding_ref:
            raise ValueError(f"{self.id} needs binding_ref")
        if self.role in TEXT_LAYER_ROLES:
            if self.binding_kind is not BindingKind.COPY:
                raise ValueError(f"{self.id} text layers must bind to copy")
            if self.text_style is None:
                raise ValueError(f"{self.id} text layers need a text style")
        if self.role in BOUND_VISUAL_ROLES and self.binding_kind is not BindingKind.ASSET:
            raise ValueError(f"{self.id} visual layers must bind to an asset")
        for keyframe in self.motion:
            if keyframe.frame < self.start_frame or keyframe.frame > self.end_frame:
                raise ValueError(f"{self.id} keyframe outside layer range")
        return self

    @property
    def duration_frames(self) -> int:
        return self.end_frame - self.start_frame


class RightsRecord(StrictModel):
    status: RightsStatus
    licence_name: str | None = Field(default=None, max_length=200)
    licence_url: str | None = Field(default=None, max_length=1000)
    attribution: str | None = Field(default=None, max_length=500)
    commercial_use: bool | None = None
    modification: bool | None = None
    editorial_only: bool = False
    consent_ref: str | None = Field(default=None, max_length=300)
    ai_generated: bool = False
    disclosure_required: bool = False
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def cleared_rights_are_specific(self) -> RightsRecord:
        if self.status is RightsStatus.CLEARED:
            if self.commercial_use is not True:
                raise ValueError("cleared rights need commercial_use=true")
            if not self.licence_name:
                raise ValueError("cleared rights need a licence or ownership basis")
        if self.status is RightsStatus.REFERENCE_ONLY and self.commercial_use is True:
            raise ValueError("reference-only material cannot be commercially cleared")
        return self


class TechSpec(StrictModel):
    format: str = Field(min_length=1, max_length=100)
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    transparency: bool = False
    orientation: str = Field(default="any", pattern=r"^(any|portrait|landscape|square)$")
    fps: int | None = Field(default=None, gt=0, le=120)
    duration_frames: int | None = Field(default=None, gt=0)
    notes: str | None = Field(default=None, max_length=1000)


class Asset(StrictModel):
    id: str = Field(pattern=r"^AS-\d{2}$")
    version: str = Field(default="1.0", min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    route: AssetRoute
    source: str | None = Field(default=None, max_length=1000)
    generation_spec: str | None = Field(default=None, max_length=2000)
    rights: RightsRecord
    tech: TechSpec
    exactness: Exactness
    allowed_edits: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    estimate_id: str | None = None
    fallback_asset_id: str | None = None
    used_by: list[str] = Field(default_factory=list)
    status: AssetStatus = AssetStatus.PENDING
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def asset_is_sourceable(self) -> Asset:
        if self.route is AssetRoute.TO_GENERATE and not self.generation_spec:
            raise ValueError(f"{self.id} generation route needs a specification")
        if self.fallback_asset_id == self.id:
            raise ValueError(f"{self.id} cannot fall back to itself")
        return self


class Estimate(StrictModel):
    id: str = Field(pattern=r"^ES-\d{2}$")
    label: str = Field(min_length=1, max_length=200)
    amount_usd: float = Field(ge=0)
    kind: EstimateKind
    basis: EstimateBasis
    confidence: str = Field(default="medium", pattern=r"^(low|medium|high)$")
    notes: str | None = Field(default=None, max_length=500)


class BudgetPlan(StrictModel):
    cap_usd: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    estimates: list[Estimate] = Field(min_length=1)
    retry_reserve_pct: float = Field(default=15, ge=0, le=50)

    def total_for(self, kind: EstimateKind) -> float:
        return round(sum(item.amount_usd for item in self.estimates if item.kind is kind), 2)

    @property
    def shared_usd(self) -> float:
        return self.total_for(EstimateKind.SHARED)

    @property
    def shot_usd(self) -> float:
        return self.total_for(EstimateKind.SHOT)

    @property
    def variant_usd(self) -> float:
        return self.total_for(EstimateKind.VARIANT)

    @property
    def fallback_usd(self) -> float:
        return self.total_for(EstimateKind.FALLBACK)

    @property
    def subtotal_usd(self) -> float:
        return round(self.shared_usd + self.shot_usd + self.variant_usd, 2)

    @property
    def reserve_usd(self) -> float:
        return round(self.subtotal_usd * self.retry_reserve_pct / 100, 2)

    @property
    def total_usd(self) -> float:
        return round(self.subtotal_usd + self.reserve_usd, 2)

    @property
    def worst_case_usd(self) -> float:
        return round(self.total_usd + self.fallback_usd, 2)


class AudioCue(StrictModel):
    id: str = Field(pattern=r"^AU-\d{2}$")
    start_frame: int = Field(ge=0)
    end_frame: int = Field(gt=0)
    kind: AudioKind
    description: str = Field(min_length=1, max_length=500)
    asset_id: str | None = None
    level_db: float | None = Field(default=None, ge=-60, le=0)
    essential: bool = True
    notes: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def ends_after_start(self) -> AudioCue:
        if self.end_frame <= self.start_frame:
            raise ValueError(f"{self.id} end_frame must be after start_frame")
        return self


class Beat(StrictModel):
    id: str = Field(pattern=r"^BT-\d{2}$")
    start_frame: int = Field(ge=0)
    end_frame: int = Field(gt=0)
    purpose: str = Field(min_length=1, max_length=500)
    spoken_line: str | None = Field(default=None, max_length=300)
    on_screen_copy: str | None = Field(default=None, max_length=300)
    action: str = Field(min_length=1, max_length=1000)
    emotion: str = Field(min_length=1, max_length=200)
    audio_cue_ids: list[str] = Field(default_factory=list)
    copy_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def ends_after_start(self) -> Beat:
        if self.end_frame <= self.start_frame:
            raise ValueError(f"{self.id} end_frame must be after start_frame")
        return self


class Transition(StrictModel):
    id: str = Field(pattern=r"^TR-\d{2}$")
    from_shot_id: str
    to_shot_id: str
    at_frame: int = Field(ge=0)
    kind: str = Field(min_length=1, max_length=100)
    duration_frames: int = Field(ge=0, le=48)
    notes: str | None = Field(default=None, max_length=500)


class Shot(StrictModel):
    id: str = Field(pattern=r"^SH-\d{2}$")
    beat_ids: list[str] = Field(min_length=1)
    start_frame: int = Field(ge=0)
    end_frame: int = Field(gt=0)
    purpose: str = Field(min_length=1, max_length=500)
    framing: str = Field(min_length=1, max_length=500)
    movement: str = Field(min_length=1, max_length=500)
    subject: str = Field(min_length=1, max_length=500)
    action: str = Field(min_length=1, max_length=1000)
    expression: str = Field(min_length=1, max_length=500)
    lighting: str = Field(min_length=1, max_length=500)
    palette: str = Field(min_length=1, max_length=500)
    transition_in: str = Field(min_length=1, max_length=200)
    continuity: str = Field(min_length=1, max_length=1000)
    method: str = Field(min_length=1, max_length=1000)
    fallback_method: str = Field(min_length=1, max_length=1000)
    status: ShotStatus
    layer_ids: list[str] = Field(min_length=1)
    asset_ids: list[str] = Field(default_factory=list)
    check_ids: list[str] = Field(default_factory=list)
    estimate_ids: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def ends_after_start(self) -> Shot:
        if self.end_frame <= self.start_frame:
            raise ValueError(f"{self.id} end_frame must be after start_frame")
        return self

    @property
    def duration_frames(self) -> int:
        return self.end_frame - self.start_frame


class AcceptanceCheck(StrictModel):
    id: str = Field(pattern=r"^AC-\d{2}$")
    target_ids: list[str] = Field(min_length=1)
    description: str = Field(min_length=1, max_length=1000)
    method: CheckMethod
    level: CheckLevel
    status: CheckStatus = CheckStatus.PENDING
    evidence: str | None = Field(default=None, max_length=1000)
    notes: str | None = Field(default=None, max_length=1000)


class AlternateRoute(StrictModel):
    id: str = Field(pattern=r"^ALT-\d{2}$")
    target_ids: list[str] = Field(min_length=1)
    trigger: str = Field(min_length=1, max_length=500)
    preserved: str = Field(min_length=1, max_length=1000)
    revised_dependencies: list[str] = Field(default_factory=list)
    cost_delta_usd: float = 0
    cost_estimate_id: str | None = None
    approval_scope: list[str] = Field(min_length=1)
    status: str = Field(default="proposed", pattern=r"^(proposed|approved|rejected)$")


class HeldItem(StrictModel):
    id: str = Field(pattern=r"^HI-\d{2}$")
    title: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=1000)
    affects: list[str] = Field(min_length=1)
    required_evidence: str = Field(min_length=1, max_length=1000)
    owner: Owner


class ProductionPlan(StrictModel):
    project_id: str
    revision: int = Field(ge=1)
    brief_revision: int = Field(ge=1)
    deliverable: DeliverableProfile
    beats: list[Beat] = Field(min_length=1)
    shots: list[Shot] = Field(min_length=1)
    layers: list[Layer] = Field(min_length=1)
    copy_blocks: list[CopyBlock] = Field(min_length=1)
    exact_data: list[ExactData] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    assets: list[Asset] = Field(min_length=1)
    audio_cues: list[AudioCue] = Field(default_factory=list)
    transitions: list[Transition] = Field(default_factory=list)
    alternates: list[AlternateRoute] = Field(default_factory=list)
    estimates: list[Estimate] = Field(min_length=1)
    budget: BudgetPlan
    checks: list[AcceptanceCheck] = Field(min_length=1)
    held_items: list[HeldItem] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)

    def map_of(self, records: list[Any], attribute: str = "id") -> dict[str, Any]:
        return {getattr(record, attribute): record for record in records}

    @property
    def shot_map(self) -> dict[str, Shot]:
        return {shot.id: shot for shot in self.shots}

    @property
    def layer_map(self) -> dict[str, Layer]:
        return {layer.id: layer for layer in self.layers}

    @property
    def asset_map(self) -> dict[str, Asset]:
        return {asset.id: asset for asset in self.assets}

    @property
    def copy_map(self) -> dict[str, CopyBlock]:
        return {copy.id: copy for copy in self.copy_blocks}

    @property
    def exact_map(self) -> dict[str, ExactData]:
        return {item.id: item for item in self.exact_data}

    @property
    def claim_map(self) -> dict[str, Claim]:
        return {claim.id: claim for claim in self.claims}

    @property
    def check_map(self) -> dict[str, AcceptanceCheck]:
        return {check.id: check for check in self.checks}

    @property
    def estimate_map(self) -> dict[str, Estimate]:
        return {estimate.id: estimate for estimate in self.estimates}

    @property
    def beat_map(self) -> dict[str, Beat]:
        return {beat.id: beat for beat in self.beats}

    @property
    def audio_map(self) -> dict[str, AudioCue]:
        return {cue.id: cue for cue in self.audio_cues}

    def plan_hash(self) -> str:
        return content_hash(self)


# ---------------------------------------------------------------------------
# validation and critique
# ---------------------------------------------------------------------------


class ValidationFinding(StrictModel):
    id: str = Field(pattern=r"^V-\d{3}$")
    rule: str = Field(min_length=1, max_length=80)
    target: str = Field(min_length=1, max_length=200)
    severity: Severity
    status: ValidationStatus
    detail: str = Field(min_length=1, max_length=2000)
    remediation: str = Field(min_length=1, max_length=1000)


class ValidationReport(StrictModel):
    project_id: str
    plan_revision: int = Field(ge=1)
    plan_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    findings: list[ValidationFinding] = Field(min_length=1)
    check_status: dict[str, CheckStatus] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)

    @property
    def passed(self) -> bool:
        return not any(item.status is ValidationStatus.FAIL for item in self.findings)

    @property
    def failures(self) -> list[ValidationFinding]:
        return [item for item in self.findings if item.status is ValidationStatus.FAIL]

    @property
    def warnings(self) -> list[ValidationFinding]:
        return [item for item in self.findings if item.status is ValidationStatus.WARN]


class CritiqueFinding(StrictModel):
    id: str = Field(pattern=r"^CF-\d{2}$")
    category: str = Field(min_length=1, max_length=80)
    severity: Severity
    observation: str = Field(min_length=1, max_length=2000)
    evidence: str = Field(min_length=1, max_length=2000)
    proposed_action: str = Field(min_length=1, max_length=2000)
    impact: int = Field(ge=1, le=5)
    confidence: int = Field(ge=1, le=5)
    effort: int = Field(ge=1, le=5)
    blocking_weight: int = Field(ge=1, le=3)
    target_ids: list[str] = Field(min_length=1)
    owner: Owner
    disposition: Disposition = Disposition.OPEN
    resolution: str | None = Field(default=None, max_length=2000)

    @property
    def priority(self) -> float:
        return round(self.impact * self.confidence * self.blocking_weight / self.effort, 3)


class CritiqueReport(StrictModel):
    project_id: str
    plan_revision: int = Field(ge=1)
    plan_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    summary: str = Field(min_length=1, max_length=4000)
    findings: list[CritiqueFinding] = Field(default_factory=list)
    top3: list[str] = Field(default_factory=list, max_length=3)
    created_at: str = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def top3_references_findings(self) -> CritiqueReport:
        known = {finding.id for finding in self.findings}
        for finding_id in self.top3:
            if finding_id not in known:
                raise ValueError(f"top3 references unknown finding {finding_id}")
        return self

    @property
    def open_blockers(self) -> list[CritiqueFinding]:
        return [
            finding
            for finding in self.findings
            if finding.disposition is Disposition.OPEN
            and finding.severity in {Severity.BLOCKER, Severity.HIGH}
        ]


class InputResolution(StrictModel):
    id: str = Field(pattern=r"^IR-\d{2}$")
    critique_finding_id: str
    rank: int = Field(ge=1, le=3)
    mode: ResolutionMode
    decision: str = Field(min_length=1, max_length=1000)
    changes: list[str] = Field(min_length=1)
    impacted_ids: list[str] = Field(default_factory=list)
    status: ResolutionStatus


class ResolutionReport(StrictModel):
    project_id: str
    from_revision: int = Field(ge=1)
    to_revision: int = Field(ge=2)
    inputs: list[InputResolution] = Field(min_length=1)
    created_at: str = Field(default_factory=utc_now)
    notes: str | None = Field(default=None, max_length=2000)


class Gate1Approval(StrictModel):
    project_id: str
    plan_revision: int = Field(ge=1)
    plan_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    approver: str = Field(min_length=2, max_length=200)
    approver_role: str = Field(min_length=2, max_length=200)
    approved_at: str = Field(default_factory=utc_now)
    scope: list[str] = Field(min_length=1)
    conditions: list[str] = Field(default_factory=list)
    allowed_substitutions: list[str] = Field(default_factory=list)
    note: str | None = Field(default=None, max_length=2000)


class Gate1Packet(StrictModel):
    project_id: str
    plan_revision: int = Field(ge=1)
    plan_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    validation_passed: bool
    ready_shots: list[str]
    held_layers: list[str]
    conditions: list[str]
    blockers: list[str]
    input_statuses: dict[str, str]
    approval: Gate1Approval | None = None
    created_at: str = Field(default_factory=utc_now)


class HandoffShot(StrictModel):
    shot_id: str
    start_frame: int
    end_frame: int
    method: str
    fallback_method: str
    layer_ids: list[str]
    asset_ids: list[str]
    check_ids: list[str]


class HandoffAsset(StrictModel):
    asset_id: str
    name: str
    route: AssetRoute
    rights_status: RightsStatus
    rights_action: str
    exactness: Exactness
    specification: str
    estimate_usd: float
    fallback_asset_id: str | None


class Level2Handoff(StrictModel):
    project_id: str
    plan_revision: int = Field(ge=1)
    plan_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    approval: Gate1Approval
    shots: list[HandoffShot]
    assets: list[HandoffAsset]
    pending_checks: list[str]
    conditions: list[str]
    exact_data_approved: list[str]
    created_at: str = Field(default_factory=utc_now)


# ---------------------------------------------------------------------------
# project and events
# ---------------------------------------------------------------------------


class Project(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,60}$")
    title: str = Field(min_length=1, max_length=200)
    state: ProjectState
    current_plan_revision: int = Field(default=0, ge=0)
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)
