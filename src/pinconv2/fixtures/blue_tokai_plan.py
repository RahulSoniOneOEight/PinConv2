"""Executable Shot x Layer x Asset fixture for the Blue Tokai 20-second ad.

Revision 1 intentionally carries three realistic defects: a caption outside the
safe area, a required price layer bound to observed commercial data, and a
redundant stock insert that pushes the plan over cap. Revision 2 removes or
fixes those defects and is the revision offered at Gate 1.
"""

from __future__ import annotations

from ..models import (
    AcceptanceCheck,
    AlternateRoute,
    Asset,
    AssetRoute,
    AssetStatus,
    AudioCue,
    AudioKind,
    Beat,
    BindingKind,
    BudgetPlan,
    CaptionRules,
    CheckLevel,
    CheckMethod,
    Claim,
    CopyBlock,
    CopyRole,
    CopyStatus,
    DeliverableProfile,
    Estimate,
    EstimateBasis,
    EstimateKind,
    ExactData,
    Exactness,
    HeldItem,
    Keyframe,
    Layer,
    LayerRole,
    Owner,
    ProductionPlan,
    Rect,
    RightsRecord,
    RightsStatus,
    SafeArea,
    Shot,
    ShotStatus,
    TechSpec,
    TextStyle,
    Transition,
)
from .blue_tokai_concept import blue_tokai_decisions
from .blue_tokai_research import (
    ATTIKAN_URL,
    LOGO_URL,
    MIXED_BAG_URL,
    PROJECT_ID,
    SEETHARGUNDU_URL,
    VIENNA_URL,
    build_blue_tokai_claims,
    build_blue_tokai_exact_data,
)

APPLIED_REVISION_TWO = frozenset(
    {"safe_area", "commercial", "budget", "text_density", "fallback", "rights"}
)

ASSET_DEPENDENCIES = {
    "AS-05": ["AS-02"],
    "AS-06": ["AS-05"],
    "AS-08": ["AS-06"],
    "AS-13": ["AS-02"],
    "AS-15": ["AS-09"],
}

ASSET_ACCEPTANCE = {
    "AS-01": "Logo edges clean at end-card size; proportions and colour match the supplied master.",
    "AS-02": (
        "Front title, ‘Light to Dark Roasts’ and Blue Tokai mark readable at phone "
        "scale; no label crop."
    ),
    "AS-03": "Vienna name and dark-roast descriptor readable; no label crop.",
    "AS-04": "Attikan name and medium-dark descriptor readable; no label crop.",
    "AS-17": "Seethargundu name and light-roast descriptor readable; no label crop.",
    "AS-05": (
        "Tear, open and anchor actions are physically correct and match the brand instructions."
    ),
    "AS-06": (
        "Water visibly contacts the coffee bed; bloom and drip read in macro; no spill "
        "or continuity break."
    ),
    "AS-07": "Full-canvas background holds a consistent grade across all six shots.",
    "AS-08": (
        "Finished cup matches the brewed colour; rim clean; steam visible without "
        "obscuring the pack."
    ),
    "AS-09": "Performer release present; intelligible read; no claim beyond the canonical script.",
    "AS-10": (
        "Licence covers paid YouTube; 20-second edit supports the 275 range lift and 445 resolve."
    ),
    "AS-11": "Pour sound syncs to the water action without a phasing artefact.",
    "AS-12": "Sting lands under the end card and does not mask the VO.",
    "AS-13": (
        "Physical pack label is square to camera and at least as legible as the supplied image."
    ),
    "AS-14": "Fallback bed matches the primary tempo and emotional resolve.",
    "AS-15": "Synthetic read matches the canonical script and carries the disclosure decision.",
    "AS-16": "Stock insert matches the brew action and does not introduce a different cup or pack.",
}


def revision_two_applied() -> frozenset[str]:
    return APPLIED_REVISION_TWO


def _r(x: int, y: int, w: int, h: int) -> Rect:
    return Rect(x=x, y=y, w=w, h=h)


def _text(
    layer_id: str,
    shot_id: str,
    start: int,
    end: int,
    role: LayerRole,
    rect: Rect,
    copy_id: str,
    size: int,
    z: int,
    *,
    protected: bool = False,
    color: str = "#132A3A",
    weight: int = 700,
    align: str = "left",
    motion: list[Keyframe] | None = None,
) -> Layer:
    return Layer(
        id=layer_id,
        shot_id=shot_id,
        start_frame=start,
        end_frame=end,
        role=role,
        z_order=z,
        rect=rect,
        text_style=TextStyle(
            font_family="Inter",
            size_px=size,
            weight=weight,
            color=color,
            align=align,
            line_height=1.08,
            tracking=-1,
            max_lines=2,
        ),
        protected=protected,
        binding_kind=BindingKind.COPY,
        binding_ref=copy_id,
        exactness=Exactness.PROPOSED_COPY,
        required=True,
        motion=motion or [],
        acceptance=(
            f"{copy_id} renders exactly, inside the safe area, with no clipping or "
            "unintended line break at final phone scale."
        ),
        allowed_edits=(
            ["none without renewed approval"]
            if protected
            else ["position within safe area", "size within 10 percent", "colour grade"]
        ),
    )


def _visual(
    layer_id: str,
    shot_id: str,
    start: int,
    end: int,
    role: LayerRole,
    rect: Rect,
    asset_id: str,
    z: int,
    *,
    exactness: Exactness = Exactness.ILLUSTRATIVE,
    opacity: float = 1.0,
    protected_regions: list[Rect] | None = None,
    motion: list[Keyframe] | None = None,
    effect: str | None = None,
    effect_spec: str | None = None,
    non_occluding: bool = False,
    protected: bool = False,
    acceptance: str | None = None,
) -> Layer:
    return Layer(
        id=layer_id,
        shot_id=shot_id,
        start_frame=start,
        end_frame=end,
        role=role,
        z_order=z,
        rect=rect,
        opacity=opacity,
        motion=motion or [],
        effect=effect,
        effect_spec=effect_spec,
        non_occluding=non_occluding,
        protected=protected,
        protected_regions=protected_regions or [],
        binding_kind=BindingKind.ASSET,
        binding_ref=asset_id,
        exactness=exactness,
        required=True,
        acceptance=acceptance
        or (
            f"{asset_id} reads clearly in the {role.value} layer; the protected "
            "region remains unobstructed at final phone scale."
        ),
        allowed_edits=["colour grade", "timing within 4 frames", "crop within 5 percent"],
    )


def _plate(layer_id: str, shot_id: str, end: int, z: int = 25, rect: Rect | None = None) -> Layer:
    return Layer(
        id=layer_id,
        shot_id=shot_id,
        start_frame=0,
        end_frame=end,
        role=LayerRole.CAPTION_PLATE,
        z_order=z,
        rect=rect or _r(110, 880, 1320, 110),
        opacity=0.88,
        fill="#F7F3EC",
        binding_kind=BindingKind.NONE,
        exactness=Exactness.ILLUSTRATIVE,
        acceptance=(
            "Plate provides contrast behind the copy and does not cover any protected "
            "product region."
        ),
        allowed_edits=["height", "opacity"],
    )


def _copy_blocks(include_price: bool) -> list[CopyBlock]:
    blocks = [
        CopyBlock(
            id="CP-01",
            text="SPECIALTY COFFEE.",
            role=CopyRole.HOOK,
            claim_refs=["CL-01"],
            status=CopyStatus.PROPOSED,
            reading_frames=60,
        ),
        CopyBlock(
            id="CP-02",
            text="JUST A MUG AND HOT WATER.",
            role=CopyRole.HEADLINE,
            claim_refs=["CL-02"],
            status=CopyStatus.PROPOSED,
            reading_frames=100,
        ),
        CopyBlock(
            id="CP-03",
            text="TEAR. ANCHOR. POUR.",
            role=CopyRole.HEADLINE,
            status=CopyStatus.PROPOSED,
            reading_frames=70,
        ),
        CopyBlock(
            id="CP-04",
            text="LIGHT TO DARK.",
            role=CopyRole.HEADLINE,
            claim_refs=["CL-03"],
            status=CopyStatus.PROPOSED,
            reading_frames=80,
        ),
        CopyBlock(
            id="CP-05",
            text="Shop Easy Pour",
            role=CopyRole.CTA,
            exact_data_refs=["ED-04"],
            status=CopyStatus.PROPOSED,
            reading_frames=50,
        ),
        CopyBlock(
            id="CP-07",
            text="The filter is built into the sachet.",
            role=CopyRole.CAPTION,
            claim_refs=["CL-05"],
            status=CopyStatus.PROPOSED,
            reading_frames=65,
        ),
        CopyBlock(
            id="CP-08",
            text="Tear, anchor, pour.",
            role=CopyRole.CAPTION,
            status=CopyStatus.PROPOSED,
            reading_frames=70,
        ),
        CopyBlock(
            id="CP-09",
            text="Easy Pour Mixed Bag",
            role=CopyRole.CAPTION,
            exact_data_refs=["ED-01"],
            status=CopyStatus.PROPOSED,
            reading_frames=90,
        ),
        CopyBlock(
            id="CP-10",
            text="Seethargundu · Attikan · Vienna",
            role=CopyRole.CAPTION,
            claim_refs=["CL-04", "CL-06", "CL-07"],
            status=CopyStatus.PROPOSED,
            reading_frames=90,
        ),
        CopyBlock(
            id="CP-11",
            text="Blue Tokai Coffee Roasters",
            role=CopyRole.CAPTION,
            exact_data_refs=["ED-05"],
            status=CopyStatus.PROPOSED,
            reading_frames=50,
        ),
        CopyBlock(
            id="CP-12",
            text="Brew sequence compressed.",
            role=CopyRole.DISCLAIMER,
            status=CopyStatus.PROPOSED,
            reading_frames=55,
            notes=(
                "Required because the real method includes repeated pours and a two-minute "
                "steep; the whole action is compressed, not only the steep."
            ),
        ),
        CopyBlock(
            id="CP-13",
            text="One mug. One sachet. One cup.",
            role=CopyRole.HEADLINE,
            status=CopyStatus.PROPOSED,
            reading_frames=55,
        ),
    ]
    if include_price:
        blocks.append(
            CopyBlock(
                id="CP-06",
                text="MIXED BAG · ₹300",
                role=CopyRole.OFFER,
                exact_data_refs=["ED-02"],
                status=CopyStatus.HELD,
                reading_frames=55,
                notes="Observed price; hero pack size and advertising use are unconfirmed.",
            )
        )
    return blocks


def _rights_needs(licence: str, note: str, *, consent: str | None = None) -> RightsRecord:
    return RightsRecord(
        status=RightsStatus.NEEDS_APPROVAL,
        licence_name=licence,
        commercial_use=True,
        modification=True,
        consent_ref=consent,
        notes=note,
    )


def _owned(note: str) -> RightsRecord:
    return RightsRecord(
        status=RightsStatus.CLEARED,
        licence_name="In-house production asset",
        commercial_use=True,
        modification=True,
        notes=note,
    )


def _assets(*, budget_fixed: bool) -> list[Asset]:
    assets = [
        Asset(
            id="AS-01",
            name="Blue Tokai Coffee Roasters logo",
            description=(
                "Blue Tokai footer logo from the public storefront. This is an observed "
                "reference, not a supplied master; the brand must provide the production "
                "master and written paid-media approval."
            ),
            route=AssetRoute.SUPPLIED,
            source=LOGO_URL,
            rights=_rights_needs(
                "Brand logo advertising licence (pending)",
                "Observed public logo URL; paid-media use needs written approval.",
            ),
            tech=TechSpec(
                format="PNG",
                transparency=True,
                orientation="landscape",
                notes="Use the largest available master; do not upscale a thumbnail.",
            ),
            exactness=Exactness.EXACT,
            allowed_edits=["scale proportionally"],
            fallback_required=False,
            status=AssetStatus.PENDING,
            used_by=["LY-062"],
        ),
        Asset(
            id="AS-02",
            name="Easy Pour Mixed Bag pack",
            description=(
                "Front pack of Mixed | Light to Dark Roasts - Easy Pour. The title, "
                "roast descriptor and Blue Tokai mark must remain legible."
            ),
            route=AssetRoute.SUPPLIED,
            source=MIXED_BAG_URL,
            rights=_rights_needs(
                "Brand pack advertising licence (pending)",
                "Observed public product image; written advertising use is pending.",
            ),
            tech=TechSpec(
                format="JPEG",
                width=1800,
                height=1800,
                transparency=False,
                orientation="square",
                notes="Crop only to the pack edge; do not crop the front label.",
            ),
            exactness=Exactness.EXACT,
            allowed_edits=["background removal", "drop shadow", "colour match to grade"],
            estimate_id="ES-05",
            fallback_asset_id="AS-13",
            status=AssetStatus.PENDING,
            used_by=["LY-011", "LY-022", "LY-032", "LY-041", "LY-052", "LY-061"],
        ),
        Asset(
            id="AS-03",
            name="Easy Pour Vienna pack",
            description="Front pack of Vienna | Dark Roast - Easy Pour.",
            route=AssetRoute.SUPPLIED,
            source=VIENNA_URL,
            rights=_rights_needs(
                "Brand pack advertising licence (pending)",
                "Observed public product image; advertising use pending.",
            ),
            tech=TechSpec(
                format="JPEG",
                width=1800,
                height=1800,
                orientation="square",
                notes="Front pack only; keep the roast descriptor visible.",
            ),
            exactness=Exactness.EXACT,
            allowed_edits=["background removal", "colour match to grade"],
            estimate_id="ES-07",
            fallback_required=False,
            status=AssetStatus.PENDING,
            used_by=["LY-042"],
        ),
        Asset(
            id="AS-04",
            name="Easy Pour Attikan Estate pack",
            description="Front pack of Attikan Estate | Medium-Dark Roast - Easy Pour.",
            route=AssetRoute.SUPPLIED,
            source=ATTIKAN_URL,
            rights=_rights_needs(
                "Brand pack advertising licence (pending)",
                "Observed public product image; advertising use pending.",
            ),
            tech=TechSpec(
                format="JPEG",
                width=1800,
                height=1800,
                orientation="square",
                notes="Front pack only; keep the roast descriptor visible.",
            ),
            exactness=Exactness.EXACT,
            allowed_edits=["background removal", "colour match to grade"],
            estimate_id="ES-07",
            fallback_required=False,
            status=AssetStatus.PENDING,
            acceptance=("Attikan name and medium-dark descriptor readable; no label crop."),
            used_by=["LY-043"],
        ),
        Asset(
            id="AS-17",
            name="Easy Pour Seethargundu Estate pack",
            description="Front pack of Seethargundu Estate | Light Roast - Easy Pour.",
            route=AssetRoute.SUPPLIED,
            source=SEETHARGUNDU_URL,
            rights=_rights_needs(
                "Brand pack advertising licence (pending)",
                "Observed public product image; advertising use pending.",
            ),
            tech=TechSpec(
                format="JPEG",
                width=1800,
                height=1800,
                orientation="square",
                notes="Front pack only; keep the light-roast descriptor visible.",
            ),
            exactness=Exactness.EXACT,
            allowed_edits=["background removal", "colour match to grade"],
            estimate_id="ES-07",
            fallback_required=False,
            status=AssetStatus.PENDING,
            acceptance=("Seethargundu name and light-roast descriptor readable; no label crop."),
            used_by=["LY-047"],
        ),
        Asset(
            id="AS-05",
            name="Easy Pour brewing demonstration, hands",
            description=(
                "Controlled kitchen demonstration: lift the sachet, tear the outer pack, "
                "open the built-in filter, anchor it on a 180-200 ml mug. Hands only; "
                "no face required."
            ),
            route=AssetRoute.TO_CAPTURE,
            source="In-house food shoot",
            rights=_rights_needs(
                "Talent and hand release (pending)",
                "A performer's hands appear on camera.",
                consent="Hand model release pending",
            ),
            tech=TechSpec(
                format="ProRes 422 HQ",
                width=3840,
                height=2160,
                fps=25,
                duration_frames=170,
                notes="Shoot 4K for a 1080p master crop; 180-degree shutter.",
            ),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "speed within 10 percent", "colour grade"],
            estimate_id="ES-06",
            status=AssetStatus.PENDING,
            used_by=["LY-021"],
        ),
        Asset(
            id="AS-06",
            name="Hot water pour and bloom footage",
            description=(
                "Macro hot water hitting the coffee bed inside the anchored filter; "
                "visible bloom and drip into the mug."
            ),
            route=AssetRoute.TO_CAPTURE,
            source="In-house food shoot",
            rights=_rights_needs(
                "In-house capture approval (pending)",
                "Future capture; consent and set approval are not yet evidenced.",
            ),
            tech=TechSpec(
                format="ProRes 422 HQ",
                width=3840,
                height=2160,
                fps=50,
                duration_frames=140,
                notes="Source timebase 50 fps; conform to the 25 fps master at 50 percent speed.",
            ),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "retime", "colour grade"],
            estimate_id="ES-06",
            status=AssetStatus.PENDING,
            used_by=["LY-031"],
        ),
        Asset(
            id="AS-07",
            name="Warm kitchen background",
            description=(
                "Warm daylight kitchen counter with soft linen and a blue-grey wall. "
                "The background must not compete with the pack."
            ),
            route=AssetRoute.OWNED,
            source="In-house set build",
            rights=_owned("Owned set and lighting."),
            tech=TechSpec(
                format="PNG",
                width=1920,
                height=1080,
                orientation="landscape",
            ),
            exactness=Exactness.ILLUSTRATIVE,
            used_by=["LY-010", "LY-020", "LY-030", "LY-040", "LY-050", "LY-060"],
        ),
        Asset(
            id="AS-08",
            name="Finished cup of coffee",
            description=(
                "Finished cup of brewed Easy Pour coffee on the same counter, with a "
                "thin steam plume and a clean rim."
            ),
            route=AssetRoute.TO_CAPTURE,
            source="In-house food shoot",
            rights=_rights_needs(
                "In-house capture approval (pending)",
                "Future capture; the brewed cup must match the demonstrated method.",
            ),
            tech=TechSpec(
                format="ProRes 422 HQ",
                width=3840,
                height=2160,
                fps=25,
                duration_frames=90,
                notes="Shoot 4K; keep the cup rim and coffee surface in focus.",
            ),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "colour grade"],
            estimate_id="ES-06",
            status=AssetStatus.PENDING,
            used_by=["LY-051"],
        ),
        Asset(
            id="AS-09",
            name="Voice over, warm Indian English",
            description=(
                "Canonical narration: Specialty coffee. Just a mug and hot water. "
                "Tear, anchor, pour. Light to dark. One mug. One cup. Shop Easy Pour. "
                "Recorded by a human voice artist."
            ),
            route=AssetRoute.TO_CREATE,
            source="Voice artist session",
            rights=_rights_needs(
                "Performer release (pending)",
                "Recorded VO; synthetic narration is the disclosed fallback.",
                consent="Voice performer release pending",
            ),
            tech=TechSpec(
                format="WAV",
                fps=25,
                duration_frames=500,
                notes="48 kHz, 24-bit, dry studio recording; full 20-second read.",
            ),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "de-noise", "level"],
            estimate_id="ES-02",
            fallback_asset_id="AS-15",
            status=AssetStatus.PENDING,
            used_by=["AU-01"],
        ),
        Asset(
            id="AS-10",
            name="Music bed, 20 seconds",
            description=(
                "Restrained, warm electronic bed with a soft lift at the range reveal "
                "and a clean resolve under the end card."
            ),
            route=AssetRoute.TO_SOURCE,
            source="Production music library",
            rights=_rights_needs(
                "Library licence to be purchased",
                "One track licence for organic and paid YouTube.",
            ),
            tech=TechSpec(
                format="WAV",
                fps=25,
                duration_frames=500,
                notes="48 kHz, 24-bit, instrumental, loopable tail.",
            ),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "fade", "level"],
            estimate_id="ES-01",
            fallback_asset_id="AS-14",
            status=AssetStatus.PENDING,
            used_by=["AU-02"],
        ),
        Asset(
            id="AS-11",
            name="Water pour sound effect",
            description="Close, natural water pour with a soft filter-drip tail.",
            route=AssetRoute.OWNED,
            source="In-house sound design",
            rights=_owned("Recorded in-house."),
            tech=TechSpec(format="WAV", fps=25, duration_frames=85),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "level", "pitch"],
            used_by=["AU-03"],
        ),
        Asset(
            id="AS-12",
            name="Brand sting",
            description="Low, warm brand sting under the end card.",
            route=AssetRoute.OWNED,
            source="In-house sound design",
            rights=_owned("Synthesised in-house."),
            tech=TechSpec(format="WAV", fps=25, duration_frames=45),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "level"],
            used_by=["AU-04"],
        ),
        Asset(
            id="AS-13",
            name="Captured Mixed Bag fallback",
            description=(
                "In-house still of the physical Mixed Bag on the same counter, used if "
                "the brand image cannot be cleared or is below 1800 px."
            ),
            route=AssetRoute.TO_CAPTURE,
            source="In-house studio capture",
            rights=_rights_needs(
                "Brand pack capture approval (pending)",
                "Photographing the physical pack still needs brand approval.",
            ),
            tech=TechSpec(
                format="PNG",
                width=2400,
                height=2400,
                orientation="square",
                notes="Front label square to camera; four angles.",
            ),
            exactness=Exactness.EXACT,
            allowed_edits=["retouch", "shadow", "colour match"],
            estimate_id="ES-09",
            fallback_required=False,
            status=AssetStatus.PENDING,
            used_by=[],
        ),
        Asset(
            id="AS-14",
            name="Music fallback track",
            description="Second library bed with the same tempo, warmth and length.",
            route=AssetRoute.TO_SOURCE,
            source="Production music library",
            rights=_rights_needs(
                "Library licence to be purchased",
                "Fallback track licence.",
            ),
            tech=TechSpec(format="WAV", fps=25, duration_frames=500),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "fade", "level"],
            fallback_required=False,
            status=AssetStatus.PENDING,
            used_by=[],
        ),
        Asset(
            id="AS-15",
            name="Synthetic narration fallback",
            description="Disclosed synthetic narration used only if the human session fails.",
            route=AssetRoute.TO_GENERATE,
            generation_spec=(
                "Warm Indian English, measured pace, 20 seconds, no claim beyond the "
                "canonical script. Disclose synthetic voice in the delivery notes."
            ),
            source="Approved speech provider",
            rights=RightsRecord(
                status=RightsStatus.NEEDS_APPROVAL,
                licence_name="Provider terms and AI disclosure (pending)",
                commercial_use=True,
                modification=True,
                ai_generated=True,
                disclosure_required=True,
            ),
            tech=TechSpec(format="WAV", fps=25, duration_frames=500),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "level"],
            fallback_required=False,
            status=AssetStatus.PENDING,
            used_by=[],
        ),
    ]
    if not budget_fixed:
        assets.append(
            Asset(
                id="AS-16",
                name="Stock cafe pour insert",
                description="Licensed generic cafe pour insert; redundant with AS-06.",
                route=AssetRoute.TO_SOURCE,
                source="Stock library",
                rights=_rights_needs(
                    "Stock licence to be purchased",
                    "Generic stock insert; no product visible.",
                ),
                tech=TechSpec(
                    format="ProRes 422 HQ",
                    width=3840,
                    height=2160,
                    fps=25,
                    duration_frames=100,
                ),
                exactness=Exactness.ILLUSTRATIVE,
                allowed_edits=["crop", "trim", "grade"],
                estimate_id="ES-10",
                status=AssetStatus.PENDING,
                used_by=["LY-036"],
            )
        )
    assets = [
        asset.model_copy(
            update={
                "acceptance": asset.acceptance
                or ASSET_ACCEPTANCE.get(
                    asset.id, "Match the technical, rights and exactness records."
                ),
                "dependencies": asset.dependencies or ASSET_DEPENDENCIES.get(asset.id, []),
                "fallback_required": (
                    asset.fallback_required if asset.fallback_asset_id else False
                ),
            }
        )
        for asset in assets
    ]
    return assets


def _estimates(*, budget_fixed: bool) -> list[Estimate]:
    estimates = [
        Estimate(
            id="ES-01",
            label="Music library licence",
            amount_usd=10,
            kind=EstimateKind.SHARED,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="medium",
        ),
        Estimate(
            id="ES-02",
            label="Voice artist session and edit",
            amount_usd=12,
            kind=EstimateKind.SHARED,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="medium",
        ),
        Estimate(
            id="ES-03",
            label="Edit, motion and compositing",
            amount_usd=15,
            kind=EstimateKind.SHARED,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="medium",
        ),
        Estimate(
            id="ES-04",
            label="Colour grade and finishing",
            amount_usd=5,
            kind=EstimateKind.SHARED,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="high",
        ),
        Estimate(
            id="ES-05",
            label="Mixed Bag pack preparation",
            amount_usd=4,
            kind=EstimateKind.SHOT,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="medium",
        ),
        Estimate(
            id="ES-06",
            label="Demo and finished-cup capture",
            amount_usd=18,
            kind=EstimateKind.SHOT,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="medium",
        ),
        Estimate(
            id="ES-07",
            label="Range pack preparation",
            amount_usd=3,
            kind=EstimateKind.SHOT,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="high",
        ),
        Estimate(
            id="ES-08",
            label="End-card build",
            amount_usd=3,
            kind=EstimateKind.SHOT,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="high",
        ),
        Estimate(
            id="ES-09",
            label="Captured pack fallback",
            amount_usd=5,
            kind=EstimateKind.FALLBACK,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="medium",
        ),
    ]
    if not budget_fixed:
        estimates.append(
            Estimate(
                id="ES-10",
                label="Redundant stock cafe insert",
                amount_usd=30,
                kind=EstimateKind.SHOT,
                basis=EstimateBasis.OPERATOR_ESTIMATE,
                confidence="low",
            )
        )
    return estimates


def _deliverable() -> DeliverableProfile:
    return DeliverableProfile(
        id="DP-01",
        platform="YouTube",
        placement="16:9 in-stream and Demand Gen master",
        width=1920,
        height=1080,
        fps=25,
        frame_count=500,
        duration_seconds=20.0,
        aspect_ratio="16:9",
        safe_area=SafeArea(top=70, bottom=90, left=80, right=80),
        caption_rules=CaptionRules(
            max_lines=2,
            max_chars_per_line=42,
            max_cps=16.0,
            min_hold_frames=36,
        ),
        cta_copy_id="CP-05",
        variant_id="hero-16x9",
        sound_off_legible=True,
        placement_safe_areas={
            "youtube_in_stream": SafeArea(top=70, bottom=90, left=80, right=80),
            "youtube_demand_gen": SafeArea(top=70, bottom=90, left=80, right=80),
        },
        delivery_codec="H.264 High Profile, AAC 320 kbps, MP4",
        colour_space="Rec.709 / sRGB web delivery",
        caption_mode=(
            "Burned-in campaign copy plus a separate SRT for accessibility captions; "
            "do not rely on platform auto-captions for the message."
        ),
        audio_target="-16 LUFS integrated, -1 dBTP true peak",
    )


def _beats() -> list[Beat]:
    return [
        Beat(
            id="BT-01",
            start_frame=0,
            end_frame=75,
            purpose="Name the category and show the product before the scroll decision.",
            spoken_line="Specialty coffee.",
            on_screen_copy="SPECIALTY COFFEE.",
            action="Pack lands in a warm kitchen; the filter benefit is named.",
            emotion="curiosity",
            audio_cue_ids=["AU-01", "AU-02"],
            copy_ids=["CP-01", "CP-07"],
        ),
        Beat(
            id="BT-02",
            start_frame=75,
            end_frame=160,
            purpose="Prove the sachet contains a real filter.",
            spoken_line="Tear, anchor, pour.",
            on_screen_copy="TEAR. ANCHOR. POUR.",
            action="Hands tear the sachet, open the filter and anchor it on the mug.",
            emotion="recognition",
            audio_cue_ids=["AU-01", "AU-02"],
            copy_ids=["CP-03", "CP-08"],
        ),
        Beat(
            id="BT-03",
            start_frame=160,
            end_frame=275,
            purpose="Show water hitting the grounds and coffee blooming.",
            spoken_line="Just a mug and hot water.",
            on_screen_copy="JUST A MUG AND HOT WATER.",
            action="Water pours through the filter; the bed blooms and drips.",
            emotion="proof",
            audio_cue_ids=["AU-01", "AU-02", "AU-03"],
            copy_ids=["CP-02", "CP-09"],
        ),
        Beat(
            id="BT-04",
            start_frame=275,
            end_frame=380,
            purpose="Make the light-to-dark range concrete.",
            spoken_line="Light to dark.",
            on_screen_copy="LIGHT TO DARK.",
            action="Mixed Bag, Seethargundu, Attikan and Vienna packs fan across the counter.",
            emotion="choice",
            audio_cue_ids=["AU-01", "AU-02"],
            copy_ids=["CP-04", "CP-10"],
        ),
        Beat(
            id="BT-05",
            start_frame=380,
            end_frame=445,
            purpose="Land the finished cup and the honest time compression.",
            spoken_line="One mug. One cup.",
            on_screen_copy="ONE MUG. ONE SACHET. ONE CUP.",
            action="Finished cup steams; a time-lapse cue resolves the brew.",
            emotion="satisfaction",
            audio_cue_ids=["AU-01", "AU-02"],
            copy_ids=["CP-13", "CP-12"],
        ),
        Beat(
            id="BT-06",
            start_frame=445,
            end_frame=500,
            purpose="Close on brand, Mixed Bag and a direct CTA.",
            spoken_line="Shop Easy Pour.",
            on_screen_copy="SHOP EASY POUR",
            action="Logo, Mixed Bag and CTA hold on the end card.",
            emotion="confidence",
            audio_cue_ids=["AU-01", "AU-02", "AU-04"],
            copy_ids=["CP-05", "CP-11"],
        ),
    ]


def _layers(*, safe_fixed: bool, commercial_fixed: bool, budget_fixed: bool) -> list[Layer]:
    sh2_caption_y = 900 if safe_fixed else 1010
    layers: list[Layer] = [
        # SH-01 hook
        _visual("LY-010", "SH-01", 0, 75, LayerRole.BACKGROUND, _r(0, 0, 1920, 1080), "AS-07", 0),
        _visual(
            "LY-011",
            "SH-01",
            0,
            75,
            LayerRole.PRODUCT,
            _r(1080, 180, 700, 700),
            "AS-02",
            10,
            exactness=Exactness.EXACT,
            protected_regions=[_r(1150, 340, 560, 360)],
            motion=[
                Keyframe(frame=0, y=220, scale=0.94),
                Keyframe(frame=12, y=180, scale=1.0, easing="ease_out"),
            ],
        ),
        Layer(
            id="LY-012",
            shot_id="SH-01",
            start_frame=0,
            end_frame=75,
            role=LayerRole.EFFECT,
            z_order=8,
            rect=_r(900, 170, 760, 720),
            opacity=0.18,
            fill="#DCE8F0",
            effect="steam_drift",
            effect_spec=(
                "steam_drift: trigger f0; 75-frame loop; intensity 0.18; "
                "mask 900,170,760,720; non-occluding."
            ),
            acceptance="Steam moves slowly inside its mask and never crosses the pack label.",
            non_occluding=True,
            binding_kind=BindingKind.NONE,
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["opacity", "timing"],
        ),
        _text(
            "LY-013",
            "SH-01",
            0,
            75,
            LayerRole.TYPOGRAPHY,
            _r(120, 150, 1000, 180),
            "CP-01",
            86,
            20,
            protected=True,
        ),
        _plate("LY-014", "SH-01", 75),
        _text("LY-015", "SH-01", 0, 75, LayerRole.CAPTION, _r(120, 900, 1300, 70), "CP-07", 38, 30),
        # SH-02 tear and anchor
        _visual("LY-020", "SH-02", 0, 85, LayerRole.BACKGROUND, _r(0, 0, 1920, 1080), "AS-07", 0),
        _visual("LY-021", "SH-02", 0, 85, LayerRole.SUBJECT, _r(160, 70, 1040, 900), "AS-05", 10),
        _visual(
            "LY-022",
            "SH-02",
            0,
            85,
            LayerRole.PRODUCT,
            _r(1360, 120, 440, 440),
            "AS-02",
            12,
            exactness=Exactness.EXACT,
            protected_regions=[_r(1390, 240, 380, 220)],
        ),
        _text(
            "LY-023",
            "SH-02",
            0,
            85,
            LayerRole.TYPOGRAPHY,
            _r(120, 120, 900, 160),
            "CP-03",
            82,
            20,
            protected=True,
        ),
        _plate("LY-024", "SH-02", 85),
        _text(
            "LY-025",
            "SH-02",
            0,
            85,
            LayerRole.CAPTION,
            _r(120, sh2_caption_y, 1300, 70),
            "CP-08",
            38,
            30,
        ),
        # SH-03 pour and bloom
        _visual("LY-030", "SH-03", 0, 115, LayerRole.BACKGROUND, _r(0, 0, 1920, 1080), "AS-07", 0),
        _visual("LY-031", "SH-03", 0, 115, LayerRole.SUBJECT, _r(0, 70, 1200, 900), "AS-06", 10),
        _visual(
            "LY-032",
            "SH-03",
            0,
            115,
            LayerRole.PRODUCT,
            _r(1350, 180, 480, 480),
            "AS-02",
            12,
            exactness=Exactness.EXACT,
            protected_regions=[_r(1390, 300, 400, 260)],
        ),
        _text(
            "LY-033",
            "SH-03",
            0,
            115,
            LayerRole.TYPOGRAPHY,
            _r(120, 120, 1050, 160),
            "CP-02",
            78,
            20,
            protected=True,
        ),
        _plate("LY-034", "SH-03", 115),
        _text(
            "LY-035", "SH-03", 0, 115, LayerRole.CAPTION, _r(120, 900, 1300, 70), "CP-09", 38, 30
        ),
        # SH-04 range
        _visual("LY-040", "SH-04", 0, 105, LayerRole.BACKGROUND, _r(0, 0, 1920, 1080), "AS-07", 0),
        _visual(
            "LY-041",
            "SH-04",
            0,
            105,
            LayerRole.PRODUCT,
            _r(90, 230, 400, 430),
            "AS-02",
            10,
            exactness=Exactness.EXACT,
            protected_regions=[_r(115, 340, 350, 220)],
            motion=[
                Keyframe(frame=0, y=250, opacity=0.0),
                Keyframe(frame=10, y=230, opacity=1.0, easing="ease_out"),
            ],
        ),
        _visual(
            "LY-042",
            "SH-04",
            0,
            105,
            LayerRole.PRODUCT,
            _r(540, 230, 400, 430),
            "AS-03",
            11,
            exactness=Exactness.EXACT,
            protected_regions=[_r(565, 340, 350, 220)],
            motion=[
                Keyframe(frame=6, y=250, opacity=0.0),
                Keyframe(frame=16, y=230, opacity=1.0, easing="ease_out"),
            ],
        ),
        _visual(
            "LY-043",
            "SH-04",
            0,
            105,
            LayerRole.PRODUCT,
            _r(990, 230, 400, 430),
            "AS-04",
            12,
            exactness=Exactness.EXACT,
            protected_regions=[_r(1015, 340, 350, 220)],
            motion=[
                Keyframe(frame=12, y=250, opacity=0.0),
                Keyframe(frame=22, y=230, opacity=1.0, easing="ease_out"),
            ],
        ),
        _visual(
            "LY-047",
            "SH-04",
            0,
            105,
            LayerRole.PRODUCT,
            _r(1440, 230, 400, 430),
            "AS-17",
            13,
            exactness=Exactness.EXACT,
            protected_regions=[_r(1465, 340, 350, 220)],
            motion=[
                Keyframe(frame=18, y=250, opacity=0.0),
                Keyframe(frame=28, y=230, opacity=1.0, easing="ease_out"),
            ],
        ),
        _text(
            "LY-044",
            "SH-04",
            0,
            105,
            LayerRole.TYPOGRAPHY,
            _r(120, 120, 1200, 150),
            "CP-04",
            86,
            20,
            protected=True,
        ),
        _plate("LY-045", "SH-04", 105),
        _text(
            "LY-046", "SH-04", 0, 105, LayerRole.CAPTION, _r(120, 900, 1300, 70), "CP-10", 38, 30
        ),
        # SH-05 payoff
        _visual("LY-050", "SH-05", 0, 65, LayerRole.BACKGROUND, _r(0, 0, 1920, 1080), "AS-07", 0),
        _visual("LY-051", "SH-05", 0, 65, LayerRole.SUBJECT, _r(180, 140, 900, 850), "AS-08", 10),
        _visual(
            "LY-052",
            "SH-05",
            0,
            65,
            LayerRole.PRODUCT,
            _r(1280, 180, 500, 500),
            "AS-02",
            12,
            exactness=Exactness.EXACT,
            protected_regions=[_r(1320, 300, 420, 260)],
        ),
        _text(
            "LY-053",
            "SH-05",
            0,
            65,
            LayerRole.TYPOGRAPHY,
            _r(120, 700, 1000, 100),
            "CP-13",
            54,
            20,
            protected=True,
        ),
        _plate("LY-054", "SH-05", 65),
        _text("LY-055", "SH-05", 0, 65, LayerRole.CAPTION, _r(120, 900, 1000, 65), "CP-12", 30, 30),
        # SH-06 end card
        _visual("LY-060", "SH-06", 0, 55, LayerRole.BACKGROUND, _r(0, 0, 1920, 1080), "AS-07", 0),
        _visual(
            "LY-061",
            "SH-06",
            0,
            55,
            LayerRole.PRODUCT,
            _r(1180, 100, 600, 520),
            "AS-02",
            10,
            exactness=Exactness.EXACT,
            protected_regions=[_r(1220, 230, 520, 300)],
        ),
        _visual(
            "LY-062",
            "SH-06",
            0,
            55,
            LayerRole.LOGO,
            _r(150, 140, 520, 220),
            "AS-01",
            20,
            exactness=Exactness.EXACT,
            protected=True,
        ),
        _text(
            "LY-063",
            "SH-06",
            0,
            55,
            LayerRole.CTA,
            _r(150, 680, 900, 90),
            "CP-05",
            58,
            30,
            protected=True,
            motion=[
                Keyframe(frame=0, opacity=0.0),
                Keyframe(frame=6, opacity=1.0, easing="ease_out"),
            ],
        ),
        _plate("LY-064", "SH-06", 55, z=25, rect=_r(140, 650, 1320, 300)),
        _text(
            "LY-065",
            "SH-06",
            0,
            55,
            LayerRole.CAPTION,
            _r(150, 890, 1200, 60),
            "CP-11",
            34,
            40,
            motion=[
                Keyframe(frame=8, opacity=0.0),
                Keyframe(frame=14, opacity=1.0, easing="ease_out"),
            ],
        ),
    ]

    if not commercial_fixed:
        layers.append(
            _text(
                "LY-056",
                "SH-05",
                0,
                65,
                LayerRole.OFFER,
                _r(120, 810, 700, 60),
                "CP-06",
                34,
                35,
                protected=True,
            )
        )
    if not budget_fixed:
        layers.append(
            _visual("LY-036", "SH-03", 0, 115, LayerRole.SUBJECT, _r(0, 70, 1200, 900), "AS-16", 9)
        )
    return layers


def _shots(*, layers: list[Layer], budget_fixed: bool) -> list[Shot]:
    def layer_ids(prefix: str) -> list[str]:
        return [layer.id for layer in layers if layer.shot_id == prefix]

    def assets_for(shot_id: str) -> list[str]:
        seen: list[str] = []
        for layer in layers:
            if (
                layer.shot_id == shot_id
                and layer.binding_kind is BindingKind.ASSET
                and layer.binding_ref
                and layer.binding_ref not in seen
            ):
                seen.append(layer.binding_ref)
        return seen

    return [
        Shot(
            id="SH-01",
            beat_ids=["BT-01"],
            start_frame=0,
            end_frame=75,
            purpose="Name the category and put the product in frame immediately.",
            framing="Medium-wide kitchen counter; pack at camera right, type left.",
            movement="A 12-frame pack settle; steam drifts across the negative space.",
            subject="Mixed Bag pack, mug and warm kitchen counter.",
            action="The pack lands; the category line holds.",
            expression="Confident, warm.",
            lighting="Soft window key from camera left; gentle fill on the label.",
            palette="Blue Tokai blue, cream, warm oak, black coffee.",
            transition_in="Cold open.",
            continuity="Same counter, mug and daylight for the whole film.",
            method="Live-action counter plate with product cut-out and kinetic type.",
            fallback_method="Static pack-on-counter still with a slow push-in and type fade.",
            lens_intent="35mm full-frame normal perspective; no wide distortion.",
            handles_frames=6,
            acceptance=(
                "Pack and SPECIALTY COFFEE are readable by frame 12; the label is clear "
                "of type and no text crosses the safe area."
            ),
            audio_ids=["AU-01", "AU-02"],
            status=ShotStatus.READY,
            layer_ids=layer_ids("SH-01"),
            asset_ids=assets_for("SH-01"),
            check_ids=["AC-01", "AC-02", "AC-03", "AC-14"],
            estimate_ids=["ES-05"],
        ),
        Shot(
            id="SH-02",
            beat_ids=["BT-02"],
            start_frame=75,
            end_frame=160,
            purpose="Prove the sachet has a built-in filter.",
            framing="Overhead close-up of hands, sachet and mug.",
            movement="Locked-off overhead; hands enter left and work in real time.",
            subject="Sachet, built-in paper filter and mug.",
            action="Tear, open, anchor; the filter seats on the mug rim.",
            expression="Tactile, unhurried.",
            lighting="Soft overhead key; no hand shadow across the filter.",
            palette="Kraft paper, cream filter, blue mug, warm counter.",
            transition_in="Match cut from the pack in SH-01.",
            continuity="Same mug and counter; hands enter from the left.",
            method="Real-time overhead food demonstration, one continuous take.",
            fallback_method="Stop-motion of the same steps at two frames per action.",
            lens_intent="50mm overhead, locked-off; hands fill the centre third.",
            handles_frames=4,
            acceptance=(
                "Tear, open and anchor are each visible and physically correct; the "
                "filter is seated on the mug rim by the last frame."
            ),
            audio_ids=["AU-01", "AU-02"],
            status=ShotStatus.READY,
            layer_ids=layer_ids("SH-02"),
            asset_ids=assets_for("SH-02"),
            check_ids=["AC-01", "AC-02", "AC-03", "AC-09", "AC-14"],
            estimate_ids=["ES-06"],
        ),
        Shot(
            id="SH-03",
            beat_ids=["BT-03"],
            start_frame=160,
            end_frame=275,
            purpose=(
                "Show water hitting the grounds; the edit compresses the repeated pours and steep."
            ),
            framing="Macro side profile of the filter over the mug.",
            movement="Slow push-in as the bloom rises; a 50 fps pour insert.",
            subject="Hot water, coffee bed and first drip.",
            action=(
                "First pour blooms the grounds; a short time-lapse carries the repeated "
                "pours and steep before the first drip resolves."
            ),
            expression="Appetite and craft.",
            lighting="Backlit steam with a warm edge on the water.",
            palette="Deep brown, copper, cream, blue rim.",
            transition_in="Cut on the kettle tilt from SH-02.",
            continuity="Mug rim and filter position match SH-02.",
            method="Macro live-action pour at 50 fps, finished at 25 fps.",
            fallback_method="Still macro pour plate with animated steam and a slow scale.",
            lens_intent="100mm macro; shallow depth, focus on the coffee bed and first drip.",
            handles_frames=5,
            acceptance=(
                "Water visibly contacts the grounds; bloom and first drip read; the "
                "filter stays anchored and the mug rim does not jump."
            ),
            audio_ids=["AU-01", "AU-02", "AU-03"],
            status=ShotStatus.READY,
            layer_ids=layer_ids("SH-03"),
            asset_ids=assets_for("SH-03"),
            check_ids=["AC-01", "AC-02", "AC-03", "AC-12", "AC-14"],
            estimate_ids=["ES-03", "ES-06"] + ([] if budget_fixed else ["ES-10"]),
        ),
        Shot(
            id="SH-04",
            beat_ids=["BT-04"],
            start_frame=275,
            end_frame=380,
            purpose="Make the light-to-dark range concrete with the named packs.",
            framing="Four-pack fan across the counter; type above.",
            movement="Packs settle in a shallow arc; no rotation.",
            subject="Mixed Bag, Seethargundu, Attikan and Vienna packs.",
            action="The four-pack fan lands and holds for label recognition.",
            expression="Abundance, choice.",
            lighting="Even warm key; each front label catches the same light.",
            palette="Blue, cream, roast-brown and copper.",
            transition_in="Whip pan from the brewing mug.",
            continuity="Same counter and daylight; packs face camera.",
            method="Product stills with a four-pack fan and a single camera move.",
            fallback_method=(
                "Captured four-pack still on the same counter with a slow scale; keep "
                "the light and dark endpoints."
            ),
            lens_intent="50mm at counter height; four packs share the same focal plane.",
            handles_frames=5,
            acceptance=(
                "All four pack names and roast descriptors are readable; the fan reads "
                "as light, medium-dark and dark with no label occluded."
            ),
            audio_ids=["AU-01", "AU-02"],
            status=ShotStatus.READY,
            layer_ids=layer_ids("SH-04"),
            asset_ids=assets_for("SH-04"),
            check_ids=["AC-01", "AC-02", "AC-03", "AC-12", "AC-14"],
            estimate_ids=["ES-07"],
        ),
        Shot(
            id="SH-05",
            beat_ids=["BT-05"],
            start_frame=380,
            end_frame=445,
            purpose="Land the finished cup and disclose the time compression.",
            framing="Finished cup at camera left; pack at right; type above.",
            movement="Slow push-in on the cup; steam rises.",
            subject="Finished cup of coffee and Mixed Bag pack.",
            action="The cup settles; the disclaimer holds under the frame.",
            expression="Satisfaction, calm.",
            lighting="Warm key on the crema; soft falloff behind.",
            palette="Coffee brown, cream, blue.",
            transition_in="Time-lapse resolve from the drip.",
            continuity="Same mug, counter and pack orientation.",
            method="Finished-cup live action with a time-lapse transition.",
            fallback_method="Still cup with animated steam and a type-only time card.",
            lens_intent="50mm at counter height; cup rim and crema in focus, pack soft behind.",
            handles_frames=5,
            acceptance=(
                "Finished cup reads as coffee, not a prop; the brew-sequence disclaimer "
                "is legible; pack label remains clear."
            ),
            audio_ids=["AU-01", "AU-02"],
            status=ShotStatus.READY,
            layer_ids=layer_ids("SH-05"),
            asset_ids=assets_for("SH-05"),
            check_ids=["AC-01", "AC-02", "AC-03", "AC-09", "AC-15", "AC-14"],
            estimate_ids=["ES-06"],
        ),
        Shot(
            id="SH-06",
            beat_ids=["BT-06"],
            start_frame=445,
            end_frame=500,
            purpose="Close on brand, hero pack and a direct purchase prompt.",
            framing="Cream end card; logo left, pack right, CTA and brand below.",
            movement="CTA and caption fade up over six frames; pack holds.",
            subject="Blue Tokai logo, Mixed Bag pack, Shop Easy Pour.",
            action="The end card holds for the final read.",
            expression="Clear, confident.",
            lighting="Even cream card with a soft pack shadow.",
            palette="Cream, Blue Tokai blue, pack colours.",
            transition_in="Cut from the finished cup.",
            continuity="Pack orientation matches SH-04 and SH-05.",
            method="End-card composite with supplied logo and pack.",
            fallback_method=(
                "Typographic end card with logo, scaled Mixed Bag pack and CTA; the pack "
                "remains mandatory even if the hero image is unavailable."
            ),
            lens_intent="35mm graphic end card; no camera movement after the settle.",
            handles_frames=4,
            acceptance=(
                "Logo, Mixed Bag pack, CTA and brand name are all readable in the final "
                "hold; no element is clipped by the end-card plate."
            ),
            audio_ids=["AU-01", "AU-02", "AU-04"],
            status=ShotStatus.READY,
            layer_ids=layer_ids("SH-06"),
            asset_ids=assets_for("SH-06"),
            check_ids=["AC-01", "AC-02", "AC-03", "AC-05", "AC-09", "AC-14"],
            estimate_ids=["ES-04", "ES-08"],
        ),
    ]


def _audio_cues() -> list[AudioCue]:
    return [
        AudioCue(
            id="AU-01",
            start_frame=0,
            end_frame=500,
            kind=AudioKind.VO,
            description=(
                "Canonical read: Specialty coffee. Just a mug and hot water. Tear, "
                "anchor, pour. Light to dark. One mug. One cup. Shop Easy Pour."
            ),
            asset_id="AS-09",
            level_db=-4.0,
            essential=True,
            notes=(
                "Line windows: 0-75, 75-160, 160-275, 275-380, 380-445, 445-500. "
                "Measured pace; no added claim. Mix target -16 LUFS integrated, -1 dBTP."
            ),
        ),
        AudioCue(
            id="AU-02",
            start_frame=0,
            end_frame=500,
            kind=AudioKind.MUSIC,
            description="Warm restrained bed; lift at 275, resolve under the end card.",
            asset_id="AS-10",
            level_db=-20.0,
            essential=True,
        ),
        AudioCue(
            id="AU-03",
            start_frame=160,
            end_frame=245,
            kind=AudioKind.SFX,
            description="Close water pour and filter drip.",
            asset_id="AS-11",
            level_db=-10.0,
            essential=True,
        ),
        AudioCue(
            id="AU-04",
            start_frame=440,
            end_frame=485,
            kind=AudioKind.SFX,
            description="Low brand sting under the end card.",
            asset_id="AS-12",
            level_db=-12.0,
            essential=True,
        ),
    ]


def _transitions() -> list[Transition]:
    return [
        Transition(
            id="TR-01",
            from_shot_id="SH-01",
            to_shot_id="SH-02",
            at_frame=75,
            kind="match cut on pack",
            duration_frames=5,
        ),
        Transition(
            id="TR-02",
            from_shot_id="SH-02",
            to_shot_id="SH-03",
            at_frame=160,
            kind="kettle tilt cut",
            duration_frames=4,
        ),
        Transition(
            id="TR-03",
            from_shot_id="SH-03",
            to_shot_id="SH-04",
            at_frame=275,
            kind="whip pan",
            duration_frames=6,
        ),
        Transition(
            id="TR-04",
            from_shot_id="SH-04",
            to_shot_id="SH-05",
            at_frame=380,
            kind="time-lapse resolve",
            duration_frames=8,
        ),
        Transition(
            id="TR-05",
            from_shot_id="SH-05",
            to_shot_id="SH-06",
            at_frame=445,
            kind="cut to cream",
            duration_frames=4,
        ),
    ]


def _checks() -> list[AcceptanceCheck]:
    return [
        AcceptanceCheck(
            id="AC-01",
            target_ids=["DP-01", "SH-01", "SH-02", "SH-03", "SH-04", "SH-05", "SH-06"],
            description="Timeline covers exactly 500 frames across six contiguous shots.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["timing.deliverable", "timing.shots", "timing.beats"],
        ),
        AcceptanceCheck(
            id="AC-02",
            target_ids=["SH-01", "SH-02", "SH-03", "SH-04", "SH-05", "SH-06"],
            description="All text sits inside the 1920x1080 safe area.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["layer.safe_area"],
        ),
        AcceptanceCheck(
            id="AC-03",
            target_ids=[
                "LY-011",
                "LY-022",
                "LY-032",
                "LY-041",
                "LY-042",
                "LY-043",
                "LY-047",
                "LY-052",
                "LY-061",
                "LY-062",
            ],
            description="Pack labels and the logo are not occluded by planned layers.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["layer.occlusion"],
        ),
        AcceptanceCheck(
            id="AC-04",
            target_ids=["ED-02", "ED-03"],
            description="No required layer depends on unapproved price or pack-size data.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["exact.critical"],
        ),
        AcceptanceCheck(
            id="AC-05",
            target_ids=["LY-062", "LY-063"],
            description="Logo and CTA remain legible at 50 percent scale on a phone.",
            method=CheckMethod.RENDER_PIXEL,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.brand_legibility"],
        ),
        AcceptanceCheck(
            id="AC-06",
            target_ids=["AU-01", "AU-02"],
            description="VO is intelligible and music sits at least 6 dB under it.",
            method=CheckMethod.AUDIO,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.audio"],
        ),
        AcceptanceCheck(
            id="AC-07",
            target_ids=["ED-01", "ED-04", "ED-05"],
            description="Exact data in final pixels matches the approved values.",
            method=CheckMethod.RENDER_PIXEL,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.exact_pixels"],
        ),
        AcceptanceCheck(
            id="AC-08",
            target_ids=["CL-01", "CL-02", "CL-03", "CL-04", "CL-05", "CL-06", "CL-07", "ED-04"],
            description="Every used claim is verified and every exact reference resolves.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["exact.references", "exact.claims"],
        ),
        AcceptanceCheck(
            id="AC-09",
            target_ids=["SH-02", "SH-05", "SH-06"],
            description="A sound-off viewer understands the product, benefit and brand.",
            method=CheckMethod.HUMAN,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.human_review"],
        ),
        AcceptanceCheck(
            id="AC-10",
            target_ids=[
                "AS-01",
                "AS-02",
                "AS-03",
                "AS-04",
                "AS-05",
                "AS-06",
                "AS-07",
                "AS-08",
                "AS-17",
            ],
            description=(
                "All picture assets are owned, supplied or commissioned; "
                "no reference footage is bound."
            ),
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["layer.binding_exactness", "rights.reference"],
        ),
        AcceptanceCheck(
            id="AC-11",
            target_ids=["DP-01"],
            description="Final file is 1920x1080, 25 fps, 20.0 s, H.264/AAC.",
            method=CheckMethod.RENDER_PIXEL,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.delivery"],
        ),
        AcceptanceCheck(
            id="AC-12",
            target_ids=["SH-01", "SH-03", "SH-04", "SH-06"],
            description="Contact sheet shows packs, labels and captions clear of platform UI.",
            method=CheckMethod.STATIC_PREVIEW,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.contact_sheet"],
        ),
        AcceptanceCheck(
            id="AC-13",
            target_ids=["DP-01"],
            description="Budget total plus fallback stays inside the approved cap.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["budget.cap", "budget.worst_case"],
        ),
        AcceptanceCheck(
            id="AC-14",
            target_ids=["SH-01", "SH-02", "SH-03", "SH-04", "SH-05", "SH-06"],
            description="Every shot has a primary and a genuinely different fallback method.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["trace.shots"],
        ),
        AcceptanceCheck(
            id="AC-15",
            target_ids=["CP-12", "SH-05"],
            description="The compressed brew sequence is disclosed on screen.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["exact.references"],
        ),
    ]


def _alternates() -> list[AlternateRoute]:
    return [
        AlternateRoute(
            id="ALT-01",
            target_ids=["AS-02"],
            trigger="Brand pack image is not cleared or is below 1800 px.",
            preserved="Exact Mixed Bag label, pack silhouette and end-card hero.",
            revised_dependencies=["AS-13"],
            cost_delta_usd=5,
            cost_estimate_id="ES-09",
            approval_scope=["SH-02", "SH-03", "SH-04", "SH-05", "SH-06"],
            switch_authority="Named brand producer plus planner",
        ),
        AlternateRoute(
            id="ALT-02",
            target_ids=["AS-06"],
            trigger=(
                "Macro pour footage fails; use a locked-off still of the anchored filter "
                "with animated water, steam and drip."
            ),
            preserved="Water-through-coffee proof and the finished cup.",
            revised_dependencies=["AS-02", "AS-05"],
            cost_delta_usd=0,
            approval_scope=["SH-03", "SH-05"],
            switch_authority="Named brand producer plus planner",
        ),
        AlternateRoute(
            id="ALT-03",
            target_ids=["CP-05"],
            trigger=(
                "Brand rejects ‘Shop Easy Pour’; use ‘Explore Easy Pour’ subject to a "
                "new exact-data approval."
            ),
            preserved="A direct purchase prompt on the end card.",
            revised_dependencies=[],
            cost_delta_usd=0,
            approval_scope=["SH-06"],
            switch_authority="Named brand producer",
        ),
        AlternateRoute(
            id="ALT-04",
            target_ids=["AS-10"],
            trigger="Music licence is not secured or the track does not fit.",
            preserved="Pace, warmth and a clean end-card resolve.",
            revised_dependencies=["AS-14"],
            cost_delta_usd=0,
            approval_scope=["SH-01", "SH-02", "SH-03", "SH-04", "SH-05", "SH-06"],
            switch_authority="Named brand producer plus editor",
        ),
    ]


def _held_items() -> list[HeldItem]:
    return [
        HeldItem(
            id="HI-01",
            title="Price and hero pack size",
            reason=(
                "The storefront price varies by pack size and the brief gives no "
                "approved commercial value."
            ),
            affects=["ED-02", "ED-03"],
            required_evidence=(
                "Brand-approved hero pack size and advertising price with a named approver."
            ),
            owner=Owner.HUMAN,
        ),
        HeldItem(
            id="HI-02",
            title="Brand pack and logo advertising rights",
            reason="Public product images and logo are not an advertising licence.",
            affects=["AS-01", "AS-02", "AS-03", "AS-04", "AS-13", "AS-17"],
            required_evidence=(
                "Written paid-media approval and high-resolution pack and logo masters."
            ),
            owner=Owner.HUMAN,
        ),
        HeldItem(
            id="HI-03",
            title="Voice and music licences",
            reason="No voice performer release or music licence has been supplied.",
            affects=["AS-09", "AS-10", "AS-14", "AS-15"],
            required_evidence=(
                "Signed performer release and a production-library licence covering paid YouTube."
            ),
            owner=Owner.HUMAN,
        ),
        HeldItem(
            id="HI-04",
            title="Demonstration and talent release",
            reason="Hands and a demonstration set appear on camera; no release is supplied.",
            affects=["AS-05", "AS-06", "AS-08"],
            required_evidence=(
                "Signed hand-model/performer release and approval to film the product "
                "demonstration."
            ),
            owner=Owner.HUMAN,
        ),
        HeldItem(
            id="HI-05",
            title="Brand typeface",
            reason="No Blue Tokai brand font was supplied; Inter is a placeholder.",
            affects=[
                "CP-01",
                "CP-02",
                "CP-03",
                "CP-04",
                "CP-05",
                "CP-07",
                "CP-08",
                "CP-09",
                "CP-10",
                "CP-11",
                "CP-12",
                "CP-13",
            ],
            required_evidence=(
                "Brand font files and typography guidance, or written approval to use "
                "Inter for this production."
            ),
            owner=Owner.HUMAN,
        ),
    ]


def build_blue_tokai_plan(
    project_id: str = PROJECT_ID,
    revision: int = 1,
    applied: frozenset[str] = frozenset(),
) -> ProductionPlan:
    safe_fixed = "safe_area" in applied
    commercial_fixed = "commercial" in applied
    budget_fixed = "budget" in applied
    if revision >= 2:
        safe_fixed = commercial_fixed = budget_fixed = True

    layers = _layers(
        safe_fixed=safe_fixed,
        commercial_fixed=commercial_fixed,
        budget_fixed=budget_fixed,
    )
    assets = _assets(budget_fixed=budget_fixed)
    estimates = _estimates(budget_fixed=budget_fixed)
    copy_blocks = _copy_blocks(include_price=not commercial_fixed)
    claims: list[Claim] = build_blue_tokai_claims()
    exact_data: list[ExactData] = build_blue_tokai_exact_data()
    shots = _shots(layers=layers, budget_fixed=budget_fixed)

    return ProductionPlan(
        project_id=project_id,
        revision=revision,
        brief_revision=1,
        detail_level="full",
        deliverable=_deliverable(),
        beats=_beats(),
        shots=shots,
        layers=layers,
        copy_blocks=copy_blocks,
        exact_data=exact_data,
        claims=claims,
        assets=assets,
        audio_cues=_audio_cues(),
        transitions=_transitions(),
        alternates=_alternates(),
        variant_overrides=[],
        estimates=estimates,
        budget=BudgetPlan(
            cap_usd=100.0,
            currency="USD",
            estimates=estimates,
            retry_reserve_pct=15,
        ),
        checks=_checks(),
        held_items=_held_items(),
        decisions=blue_tokai_decisions(),
        assumptions=[
            "The master is 16:9 because the brief asks for a YouTube ad.",
            "Safe insets are conservative operator assumptions pending placement preview.",
            "The real brew includes a two-minute steep; the film compresses it and discloses that.",
            "Public product image URLs are observed references, not cleared assets.",
            "Inter is a placeholder until Blue Tokai supplies its brand typeface.",
        ],
        open_questions=[
            "Which pack size is the hero?",
            "Which landing page receives the CTA?",
            "Will the brand supply cleared high-resolution pack and logo masters?",
            "Is a 9:16 Shorts variant required?",
        ],
    )
