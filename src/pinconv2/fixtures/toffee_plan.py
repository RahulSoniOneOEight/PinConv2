"""Executable Shot x Layer x Asset fixture for the Toffee test run.

Revision 1 intentionally carries three realistic planning defects: text outside
the safe area, a required offer bound to unapproved commercial data, and a
budget that includes both a created and a stock splash. Revision 2 applies the
critique fixes and is the revision offered at Gate 1.
"""

from __future__ import annotations

from ..models import (
    AcceptanceCheck,
    AlternateRoute,
    Asset,
    AssetRoute,
    AudioCue,
    AudioKind,
    Beat,
    BindingKind,
    BudgetPlan,
    CaptionRules,
    CheckLevel,
    CheckMethod,
    CopyBlock,
    CopyRole,
    CopyStatus,
    DeliverableProfile,
    Estimate,
    EstimateBasis,
    EstimateKind,
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
from .toffee_concept import toffee_decisions
from .toffee_research import (
    PROJECT_ID,
    build_claims,
    build_exact_data,
)

APPLIED_REVISION_TWO = frozenset(
    {"safe_area", "commercial", "budget", "fallback", "rights"}
)


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
    max_lines: int = 1,
    color: str = "#F7EBDD",
    weight: int = 700,
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
            align="left",
            line_height=1.08,
            tracking=-1,
            max_lines=max_lines,
        ),
        protected=protected,
        binding_kind=BindingKind.COPY,
        binding_ref=copy_id,
        exactness=Exactness.APPROVED_COPY,
        required=True,
        allowed_edits=(
            ["none without renewed approval"]
            if protected
            else ["position within safe area", "size within 15 percent", "colour grade"]
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
    non_occluding: bool = False,
    required: bool = True,
    protected: bool = False,
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
        non_occluding=non_occluding,
        protected=protected,
        protected_regions=protected_regions or [],
        binding_kind=BindingKind.ASSET,
        binding_ref=asset_id,
        exactness=exactness,
        required=required,
        allowed_edits=["colour grade", "timing within 4 frames"],
    )


def _plate(layer_id: str, shot_id: str, y: int, h: int, z: int, end: int) -> Layer:
    return Layer(
        id=layer_id,
        shot_id=shot_id,
        start_frame=0,
        end_frame=end,
        role=LayerRole.CAPTION_PLATE,
        z_order=z,
        rect=_r(60, y, 880, h),
        opacity=0.62,
        fill="#070403",
        binding_kind=BindingKind.NONE,
        exactness=Exactness.ILLUSTRATIVE,
        allowed_edits=["height", "opacity"],
    )


def _copy_blocks(include_offer: bool) -> list[CopyBlock]:
    blocks = [
        CopyBlock(
            id="CP-01",
            text="ETHIOPIA",
            role=CopyRole.HOOK,
            exact_data_refs=["ED-07"],
            status=CopyStatus.PROPOSED,
            reading_frames=40,
            notes="Origin word; Gate 1 approves the identifier.",
        ),
        CopyBlock(
            id="CP-02",
            text="SPECIALITY INSTANT COFFEE",
            role=CopyRole.HEADLINE,
            claim_refs=["CL-03"],
            status=CopyStatus.PROPOSED,
            reading_frames=70,
        ),
        CopyBlock(
            id="CP-03",
            text="IN AN INSTANT.",
            role=CopyRole.HEADLINE,
            status=CopyStatus.PROPOSED,
            reading_frames=70,
        ),
        CopyBlock(
            id="CP-05",
            text="Shop the Ethiopia range",
            role=CopyRole.CTA,
            exact_data_refs=["ED-05"],
            status=CopyStatus.PROPOSED,
            reading_frames=45,
            notes="Proposed CTA; exact wording needs Gate 1 approval.",
        ),
        CopyBlock(
            id="CP-11",
            text="Ethiopia.",
            role=CopyRole.CAPTION,
            exact_data_refs=["ED-07"],
            status=CopyStatus.PROPOSED,
            reading_frames=45,
        ),
        CopyBlock(
            id="CP-12",
            text="Speciality instant coffee.",
            role=CopyRole.CAPTION,
            claim_refs=["CL-03"],
            status=CopyStatus.PROPOSED,
            reading_frames=70,
        ),
        CopyBlock(
            id="CP-13",
            text="In an instant.",
            role=CopyRole.CAPTION,
            status=CopyStatus.PROPOSED,
            reading_frames=70,
        ),
        CopyBlock(
            id="CP-14",
            text="Toffee Coffee Roasters",
            role=CopyRole.CAPTION,
            exact_data_refs=["ED-06"],
            status=CopyStatus.PROPOSED,
            reading_frames=45,
        ),
    ]
    if include_offer:
        blocks.append(
            CopyBlock(
                id="CP-04",
                text="BUY 1 GET 1 - CODE BOGO",
                role=CopyRole.OFFER,
                exact_data_refs=["ED-03", "ED-04"],
                status=CopyStatus.HELD,
                reading_frames=60,
                notes="Observed storefront offer; terms and expiry unconfirmed.",
            )
        )
    return blocks


def _assets(
    *, budget_fixed: bool, fallback_fixed: bool, rights_fixed: bool
) -> list[Asset]:
    pack_rights = RightsRecord(
        status=RightsStatus.NEEDS_APPROVAL,
        licence_name="Brand-supplied artwork (pending)",
        commercial_use=True,
        modification=True,
        notes="Brand must supply pack art and confirm advertising use.",
    )
    logo_rights = RightsRecord(
        status=RightsStatus.NEEDS_APPROVAL,
        licence_name="Brand-supplied logo (pending)",
        commercial_use=True,
        modification=False,
        notes="Logo may not be redrawn or recoloured.",
    )
    owned = RightsRecord(
        status=RightsStatus.CLEARED,
        licence_name="In-house production asset",
        commercial_use=True,
        modification=True,
    )
    stock_pending = RightsStatus.NEEDS_APPROVAL
    music_rights = (
        RightsRecord(
            status=RightsStatus.NEEDS_APPROVAL,
            licence_name="Library licence to be purchased",
            licence_url="https://example.invalid/music-licence",
            commercial_use=True,
            modification=True,
            notes="One track licence; a second track is the fallback.",
        )
        if rights_fixed
        else RightsRecord(
            status=RightsStatus.UNKNOWN,
            notes="No track selected and no licence identified.",
        )
    )
    voice_rights = RightsRecord(
        status=RightsStatus.NEEDS_APPROVAL,
        licence_name="Performer release (pending)",
        commercial_use=True,
        modification=True,
        consent_ref="Talent release pending" if rights_fixed else None,
        notes="Recorded VO; synthetic narration is the disclosed fallback.",
    )

    assets = [
        Asset(
            id="AS-01",
            name="Ethiopia pack artwork",
            description=(
                "Front pack art for Ethiopia Speciality Instant Coffee, supplied by the "
                "brand with the label unobstructed and at least 2000 px on the long edge."
            ),
            route=AssetRoute.SUPPLIED,
            source="Brand pack file",
            rights=pack_rights,
            tech=TechSpec(
                format="PNG",
                width=2000,
                height=2000,
                transparency=True,
                orientation="square",
                notes="Pack silhouette on transparency; label at native resolution.",
            ),
            exactness=Exactness.EXACT,
            allowed_edits=["minor retouch", "drop shadow", "colour match to grade"],
            estimate_id="ES-05",
            fallback_asset_id="AS-06" if fallback_fixed else None,
            used_by=["LY-021", "LY-033", "LY-041"],
        ),
        Asset(
            id="AS-02",
            name="Toffee Coffee Roasters logo",
            description="Vector logo supplied by the brand, unmodified.",
            route=AssetRoute.SUPPLIED,
            source="Brand logo file",
            rights=logo_rights,
            tech=TechSpec(
                format="SVG",
                transparency=True,
                orientation="any",
                notes="Monochrome or full-colour version as supplied.",
            ),
            exactness=Exactness.EXACT,
            allowed_edits=["scale proportionally"],
            estimate_id="ES-05",
            fallback_required=False,
            used_by=["LY-042"],
        ),
        Asset(
            id="AS-03",
            name="Liquid and macro coffee pack",
            description=(
                "In-house 3D/compositing pack: dark coffee surface, steam element and a "
                "liquid ribbon that wraps the pack. Used as macro texture in SH-01 and "
                "as the payoff in SH-03."
            ),
            route=AssetRoute.TO_CREATE,
            source="In-house motion design",
            rights=owned,
            tech=TechSpec(
                format="PNG sequence",
                width=1080,
                height=1920,
                transparency=True,
                orientation="portrait",
                fps=25,
                duration_frames=100,
                notes="Render at 2x for punch-in headroom.",
            ),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["grade", "retime within 4 frames", "mask"],
            estimate_id="ES-06",
            used_by=(
                ["LY-011", "LY-031"] if budget_fixed else ["LY-031"]
            ),
        ),
        Asset(
            id="AS-05",
            name="Warm dark background",
            description=(
                "Near-black brown gradient with a soft copper vignette, authored in the "
                "composition at 1080x1920."
            ),
            route=AssetRoute.OWNED,
            source="In-house composition",
            rights=owned,
            tech=TechSpec(format="PNG", width=1080, height=1920, orientation="portrait"),
            exactness=Exactness.ILLUSTRATIVE,
            used_by=["LY-010", "LY-020", "LY-030", "LY-040"],
        ),
        Asset(
            id="AS-07",
            name="Music bed, 10 seconds",
            description=(
                "Warm restrained electronic bed with a lift at the pack reveal and a "
                "soft resolve at the close. One library licence."
            ),
            route=AssetRoute.TO_SOURCE,
            source="Production music library",
            rights=music_rights,
            tech=TechSpec(
                format="WAV",
                duration_frames=250,
                fps=25,
                notes="48 kHz, 24-bit, instrumental, loopable tail.",
            ),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "fade", "level"],
            estimate_id="ES-01",
            fallback_asset_id="AS-13" if rights_fixed else None,
            used_by=["AU-02"],
        ),
        Asset(
            id="AS-08",
            name="Voice over, warm Indian English",
            description=(
                "Sparse narration: Ethiopia. Speciality instant coffee. In an instant. "
                "Recorded by a human voice artist."
            ),
            route=AssetRoute.TO_CREATE,
            source="Voice artist session",
            rights=voice_rights,
            tech=TechSpec(
                format="WAV",
                duration_frames=230,
                fps=25,
                notes="48 kHz, 24-bit, dry studio recording.",
            ),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["trim", "de-noise", "level"],
            estimate_id="ES-02",
            fallback_asset_id="AS-14" if rights_fixed else None,
            used_by=["AU-01"],
        ),
        Asset(
            id="AS-09",
            name="Reveal whoosh",
            description="Short designed whoosh into the pack reveal.",
            route=AssetRoute.TO_CREATE,
            source="In-house sound design",
            rights=owned,
            tech=TechSpec(format="WAV", duration_frames=10, fps=25),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["level", "pitch"],
            used_by=["AU-03"],
        ),
        Asset(
            id="AS-10",
            name="Liquid splash",
            description="Designed liquid splash synced to the payoff beat.",
            route=AssetRoute.TO_CREATE,
            source="In-house sound design",
            rights=owned,
            tech=TechSpec(format="WAV", duration_frames=32, fps=25),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["level", "pitch"],
            used_by=["AU-04"],
        ),
        Asset(
            id="AS-11",
            name="Brand sting",
            description="Low brand sting under the end card.",
            route=AssetRoute.TO_CREATE,
            source="In-house sound design",
            rights=owned,
            tech=TechSpec(format="WAV", duration_frames=30, fps=25),
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["level", "pitch"],
            used_by=["AU-05"],
        ),
    ]

    if budget_fixed:
        assets.extend(
            [
                Asset(
                    id="AS-06",
                    name="Captured pack fallback",
                    description=(
                        "In-house photograph of the physical pack on a seamless warm "
                        "background, used if the brand pack file is missing or low-res."
                    ),
                    route=AssetRoute.TO_CAPTURE,
                    source="In-house studio capture",
                    rights=RightsRecord(
                        status=RightsStatus.NEEDS_APPROVAL,
                        licence_name="In-house capture of brand pack (approval pending)",
                        commercial_use=True,
                        modification=True,
                    ),
                    tech=TechSpec(
                        format="PNG",
                        width=2400,
                        height=2400,
                        transparency=True,
                        orientation="square",
                        notes="Four angles; front label must be square to camera.",
                    ),
                    exactness=Exactness.EXACT,
                    allowed_edits=["retouch", "shadow"],
                    estimate_id="ES-08",
                    used_by=[],
                ),
                Asset(
                    id="AS-13",
                    name="Music fallback track",
                    description="Second library bed with the same tempo and mood.",
                    route=AssetRoute.TO_SOURCE,
                    source="Production music library",
                    rights=RightsRecord(
                        status=RightsStatus.NEEDS_APPROVAL,
                        licence_name="Library licence to be purchased",
                        commercial_use=True,
                        modification=True,
                    ),
                    tech=TechSpec(format="WAV", duration_frames=250, fps=25),
                    exactness=Exactness.ILLUSTRATIVE,
                    allowed_edits=["trim", "fade", "level"],
                    used_by=[],
                ),
            ]
        )

    if rights_fixed:
        assets.append(
            Asset(
                id="AS-14",
                name="Synthetic narration fallback",
                description=(
                    "Disclosed synthetic narration used only if the human voice session "
                    "cannot be delivered."
                ),
                route=AssetRoute.TO_GENERATE,
                generation_spec=(
                    "Warm Indian English, measured pace, 9 seconds, no claim beyond the "
                    "approved script. Disclose synthetic voice in the delivery notes."
                ),
                source="Approved speech provider",
                rights=RightsRecord(
                    status=RightsStatus.NEEDS_APPROVAL,
                    licence_name="Provider terms and AI disclosure",
                    commercial_use=True,
                    modification=True,
                    ai_generated=True,
                    disclosure_required=True,
                ),
                tech=TechSpec(format="WAV", duration_frames=230, fps=25),
                exactness=Exactness.ILLUSTRATIVE,
                allowed_edits=["trim", "level"],
                used_by=[],
            )
        )

    if not budget_fixed:
        assets.extend(
            [
                Asset(
                    id="AS-04",
                    name="Stock bean macro",
                    description="Licensed macro plate of roasted coffee beans.",
                    route=AssetRoute.TO_SOURCE,
                    source="Stock library",
                    rights=RightsRecord(
                        status=stock_pending,
                        licence_name="Stock licence to be purchased",
                        commercial_use=True,
                        modification=True,
                    ),
                    tech=TechSpec(format="PNG", width=3000, height=4000, orientation="portrait"),
                    exactness=Exactness.ILLUSTRATIVE,
                    allowed_edits=["crop", "grade"],
                    estimate_id="ES-07",
                    fallback_asset_id="AS-03",
                    used_by=["LY-011"],
                ),
                Asset(
                    id="AS-12",
                    name="Stock liquid splash",
                    description="Licensed splash plate layered over the created liquid.",
                    route=AssetRoute.TO_SOURCE,
                    source="Stock library",
                    rights=RightsRecord(
                        status=stock_pending,
                        licence_name="Stock licence to be purchased",
                        commercial_use=True,
                        modification=True,
                    ),
                    tech=TechSpec(format="PNG sequence", width=1080, height=1920, fps=25),
                    exactness=Exactness.ILLUSTRATIVE,
                    allowed_edits=["crop", "grade", "retime"],
                    estimate_id="ES-09",
                    used_by=["LY-032"],
                ),
            ]
        )

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
            amount_usd=14,
            kind=EstimateKind.SHARED,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="medium",
        ),
        Estimate(
            id="ES-03",
            label="Motion design and compositing",
            amount_usd=8,
            kind=EstimateKind.SHARED,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="medium",
        ),
        Estimate(
            id="ES-04",
            label="Colour grade and finishing",
            amount_usd=3,
            kind=EstimateKind.SHARED,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="high",
        ),
        Estimate(
            id="ES-05",
            label="Pack and logo preparation",
            amount_usd=5,
            kind=EstimateKind.SHOT,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="medium",
        ),
        Estimate(
            id="ES-06",
            label="Liquid and macro pack",
            amount_usd=6,
            kind=EstimateKind.SHOT,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="medium",
        ),
        Estimate(
            id="ES-10",
            label="End-card build",
            amount_usd=2,
            kind=EstimateKind.SHOT,
            basis=EstimateBasis.OPERATOR_ESTIMATE,
            confidence="high",
        ),
    ]
    if budget_fixed:
        estimates.append(
            Estimate(
                id="ES-08",
                label="Pack capture fallback",
                amount_usd=2,
                kind=EstimateKind.FALLBACK,
                basis=EstimateBasis.OPERATOR_ESTIMATE,
                confidence="medium",
            )
        )
    else:
        estimates.extend(
            [
                Estimate(
                    id="ES-07",
                    label="Stock bean macro licence",
                    amount_usd=3,
                    kind=EstimateKind.SHOT,
                    basis=EstimateBasis.OPERATOR_ESTIMATE,
                    confidence="low",
                ),
                Estimate(
                    id="ES-09",
                    label="Stock splash licence",
                    amount_usd=8,
                    kind=EstimateKind.SHOT,
                    basis=EstimateBasis.OPERATOR_ESTIMATE,
                    confidence="low",
                ),
            ]
        )
    return estimates


def _budget(*, budget_fixed: bool) -> BudgetPlan:
    return BudgetPlan(
        cap_usd=60.0,
        currency="USD",
        estimates=_estimates(budget_fixed=budget_fixed),
        retry_reserve_pct=15,
    )


def _deliverable() -> DeliverableProfile:
    return DeliverableProfile(
        id="DP-01",
        platform="Instagram Reels / YouTube Shorts",
        placement="organic short video, 9:16",
        width=1080,
        height=1920,
        fps=25,
        frame_count=250,
        duration_seconds=10.0,
        aspect_ratio="9:16",
        safe_area=SafeArea(top=220, bottom=320, left=60, right=140),
        caption_rules=CaptionRules(
            max_lines=2,
            max_chars_per_line=32,
            max_cps=17.0,
            min_hold_frames=24,
        ),
        cta_copy_id="CP-05",
        variant_id="hero",
        sound_off_legible=True,
    )


def _beats(include_offer: bool) -> list[Beat]:
    third_copy = ["CP-03", "CP-13"] + (["CP-04"] if include_offer else [])
    return [
        Beat(
            id="BT-01",
            start_frame=0,
            end_frame=50,
            purpose="Stop the scroll with origin and texture.",
            spoken_line="Ethiopia.",
            on_screen_copy="ETHIOPIA",
            action="Macro coffee surface shimmers; steam drifts; the origin word lands.",
            emotion="intrigue",
            audio_cue_ids=["AU-01", "AU-02", "AU-03"],
            copy_ids=["CP-01", "CP-11"],
        ),
        Beat(
            id="BT-02",
            start_frame=50,
            end_frame=125,
            purpose="Reveal the pack and name the format.",
            spoken_line="Speciality instant coffee.",
            on_screen_copy="SPECIALITY INSTANT COFFEE",
            action="The pack rises into hero light; the label catches a single sweep.",
            emotion="recognition",
            audio_cue_ids=["AU-01", "AU-02"],
            copy_ids=["CP-02", "CP-12"],
        ),
        Beat(
            id="BT-03",
            start_frame=125,
            end_frame=200,
            purpose="Deliver the sensory payoff.",
            spoken_line="In an instant.",
            on_screen_copy="IN AN INSTANT.",
            action="Liquid wraps the pack; the splash peaks and falls.",
            emotion="appetite",
            audio_cue_ids=["AU-01", "AU-02", "AU-04"],
            copy_ids=third_copy,
        ),
        Beat(
            id="BT-04",
            start_frame=200,
            end_frame=250,
            purpose="Close on brand and CTA.",
            spoken_line="Toffee Coffee Roasters.",
            on_screen_copy="TOFFEE COFFEE ROASTERS",
            action="End card holds logo, pack and CTA.",
            emotion="confidence",
            audio_cue_ids=["AU-01", "AU-02", "AU-05"],
            copy_ids=["CP-05", "CP-14"],
        ),
    ]


def _layers(
    *, safe_fixed: bool, commercial_fixed: bool, budget_fixed: bool
) -> list[Layer]:
    sh2_caption_y = 1500 if safe_fixed else 1540
    sh2_plate_y = 1475 if safe_fixed else 1515
    sh3_caption_y = 1500 if safe_fixed else 1560
    sh3_plate_y = 1475 if safe_fixed else 1535
    sh4_cta_y = 1360 if safe_fixed else 1400
    sh4_caption_y = 1505 if safe_fixed else 1540
    sh4_plate_y = 1340 if safe_fixed else 1380

    layers: list[Layer] = [
        # SH-01 hook
        _visual(
            "LY-010",
            "SH-01",
            0,
            50,
            LayerRole.BACKGROUND,
            _r(0, 0, 1080, 1920),
            "AS-05",
            0,
        ),
        _visual(
            "LY-011",
            "SH-01",
            0,
            50,
            LayerRole.SUBJECT,
            _r(0, 240, 1080, 1300),
            "AS-03" if budget_fixed else "AS-04",
            5,
            opacity=0.55,
            motion=[
                Keyframe(frame=0, scale=1.0),
                Keyframe(frame=50, scale=1.06, easing="ease_out"),
            ],
        ),
        Layer(
            id="LY-012",
            shot_id="SH-01",
            start_frame=0,
            end_frame=50,
            role=LayerRole.EFFECT,
            z_order=8,
            rect=_r(200, 300, 680, 900),
            opacity=0.18,
            fill="#E8D5B5",
            effect="steam_drift",
            non_occluding=True,
            binding_kind=BindingKind.NONE,
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["opacity", "timing"],
        ),
        _text(
            "LY-013",
            "SH-01",
            0,
            50,
            LayerRole.TYPOGRAPHY,
            _r(80, 700, 860, 200),
            "CP-01",
            150,
            20,
            protected=True,
        ),
        _plate("LY-014", "SH-01", 1430, 150, 25, 50),
        _text(
            "LY-015",
            "SH-01",
            0,
            50,
            LayerRole.CAPTION,
            _r(80, 1450, 800, 100),
            "CP-11",
            52,
            30,
        ),
        # SH-02 reveal
        _visual(
            "LY-020",
            "SH-02",
            0,
            75,
            LayerRole.BACKGROUND,
            _r(0, 0, 1080, 1920),
            "AS-05",
            0,
        ),
        _visual(
            "LY-021",
            "SH-02",
            0,
            75,
            LayerRole.PRODUCT,
            _r(190, 480, 700, 900),
            "AS-01",
            10,
            exactness=Exactness.EXACT,
            protected_regions=[_r(260, 700, 560, 320)],
            motion=[
                Keyframe(frame=0, y=520, scale=0.96),
                Keyframe(frame=10, y=480, scale=1.0, easing="ease_out"),
            ],
        ),
        Layer(
            id="LY-022",
            shot_id="SH-02",
            start_frame=0,
            end_frame=75,
            role=LayerRole.EFFECT,
            z_order=15,
            rect=_r(160, 460, 760, 940),
            opacity=0.5,
            effect="light_sweep",
            non_occluding=True,
            motion=[
                Keyframe(frame=0, opacity=0.0),
                Keyframe(frame=8, opacity=0.55),
                Keyframe(frame=20, opacity=0.0),
            ],
            binding_kind=BindingKind.NONE,
            exactness=Exactness.ILLUSTRATIVE,
            allowed_edits=["opacity", "timing"],
        ),
        _text(
            "LY-023",
            "SH-02",
            0,
            75,
            LayerRole.TYPOGRAPHY,
            _r(80, 1330, 860, 130),
            "CP-02",
            58,
            20,
            protected=True,
            max_lines=2,
        ),
        _plate("LY-024", "SH-02", sh2_plate_y, 120, 25, 75),
        _text(
            "LY-025",
            "SH-02",
            0,
            75,
            LayerRole.CAPTION,
            _r(80, sh2_caption_y, 800, 80),
            "CP-12",
            44,
            30,
        ),
        # SH-03 payoff
        _visual(
            "LY-030",
            "SH-03",
            0,
            75,
            LayerRole.BACKGROUND,
            _r(0, 0, 1080, 1920),
            "AS-05",
            0,
        ),
        _visual(
            "LY-031",
            "SH-03",
            0,
            75,
            LayerRole.SUBJECT,
            _r(0, 700, 1080, 1100),
            "AS-03",
            5,
            opacity=0.8,
            motion=[
                Keyframe(frame=0, scale=1.0),
                Keyframe(frame=75, scale=1.08, easing="ease_out"),
            ],
        ),
        _visual(
            "LY-033",
            "SH-03",
            0,
            75,
            LayerRole.PRODUCT,
            _r(100, 300, 880, 1000),
            "AS-01",
            10,
            exactness=Exactness.EXACT,
            protected_regions=[_r(160, 520, 760, 360)],
            motion=[
                Keyframe(frame=0, scale=1.0),
                Keyframe(frame=75, scale=1.03, easing="ease_out"),
            ],
        ),
        _text(
            "LY-034",
            "SH-03",
            0,
            75,
            LayerRole.TYPOGRAPHY,
            _r(80, 1240, 860, 160),
            "CP-03",
            96,
            30,
            protected=True,
        ),
        _plate("LY-036", "SH-03", sh3_plate_y, 120, 40, 75),
        _text(
            "LY-037",
            "SH-03",
            0,
            75,
            LayerRole.CAPTION,
            _r(80, sh3_caption_y, 800, 90),
            "CP-13",
            44,
            45,
        ),
        # SH-04 close
        _visual(
            "LY-040",
            "SH-04",
            0,
            50,
            LayerRole.BACKGROUND,
            _r(0, 0, 1080, 1920),
            "AS-05",
            0,
        ),
        _visual(
            "LY-041",
            "SH-04",
            0,
            50,
            LayerRole.PRODUCT,
            _r(240, 560, 600, 760),
            "AS-01",
            10,
            exactness=Exactness.EXACT,
            protected_regions=[_r(300, 720, 480, 280)],
        ),
        _visual(
            "LY-042",
            "SH-04",
            0,
            50,
            LayerRole.LOGO,
            _r(340, 300, 400, 180),
            "AS-02",
            20,
            exactness=Exactness.EXACT,
            protected=True,
        ),
        _text(
            "LY-043",
            "SH-04",
            0,
            50,
            LayerRole.CTA,
            _r(140, sh4_cta_y, 800, 100),
            "CP-05",
            52,
            30,
            protected=True,
        ),
        _plate("LY-044", "SH-04", sh4_plate_y, 260, 25, 50),
        _text(
            "LY-045",
            "SH-04",
            0,
            50,
            LayerRole.CAPTION,
            _r(80, sh4_caption_y, 800, 80),
            "CP-14",
            42,
            40,
        ),
    ]

    if not budget_fixed:
        layers.append(
            _visual(
                "LY-032",
                "SH-03",
                0,
                75,
                LayerRole.SUBJECT,
                _r(0, 760, 1080, 1000),
                "AS-12",
                6,
                opacity=0.5,
            )
        )
    if not commercial_fixed:
        layers.append(
            _text(
                "LY-035",
                "SH-03",
                0,
                75,
                LayerRole.OFFER,
                _r(80, 1420, 860, 110),
                "CP-04",
                44,
                35,
                protected=True,
            )
        )

    return layers


def _shots(*, budget_fixed: bool, layers: list[Layer]) -> list[Shot]:
    def layer_ids(*prefixes: str) -> list[str]:
        return [
            layer.id
            for layer in layers
            if any(layer.id.startswith(prefix) for prefix in prefixes)
        ]

    return [
        Shot(
            id="SH-01",
            beat_ids=["BT-01"],
            start_frame=0,
            end_frame=50,
            purpose="Earn the next two seconds with origin and texture.",
            framing="Full-frame macro; type centered in the upper third.",
            movement="Slow push-in on the coffee surface; steam drifts right.",
            subject="Dark coffee surface, steam and the word ETHIOPIA.",
            action="The origin word lands on beat one and holds.",
            expression="Premium, quiet confidence.",
            lighting="Low-key warm key from the right; copper rim.",
            palette="Near-black brown, cream type, copper highlight.",
            transition_in="Cold open.",
            continuity="Coffee texture carries into the pack reveal.",
            method="Authored motion-graphics composite: macro plate, steam element, kinetic type.",
            fallback_method="Static macro still with a slow scale and a type fade.",
            status=ShotStatus.READY,
            layer_ids=layer_ids("LY-01"),
            asset_ids=["AS-05", "AS-03"] if budget_fixed else ["AS-05", "AS-04"],
            check_ids=["AC-01", "AC-02", "AC-14"],
            estimate_ids=[],
        ),
        Shot(
            id="SH-02",
            beat_ids=["BT-02"],
            start_frame=50,
            end_frame=125,
            purpose="Reveal the pack and name the format.",
            framing="Pack hero at center, label square to camera.",
            movement="Pack rises 40 px; a single light sweep crosses left to right.",
            subject="Ethiopia pack with an unobstructed label.",
            action="Pack settles; descriptor appears below.",
            expression="Assured, tactile.",
            lighting="Warm key on the pack; dark surround.",
            palette="Copper, cream, deep brown.",
            transition_in="Light wipe from SH-01.",
            continuity="Same warm grade and pack orientation as SH-03 and SH-04.",
            method="Pack hero composite with supplied art, light sweep and type.",
            fallback_method="Pack still on seamless background with a simple gradient.",
            status=ShotStatus.READY,
            layer_ids=layer_ids("LY-02"),
            asset_ids=["AS-05", "AS-01"],
            check_ids=["AC-01", "AC-03", "AC-09", "AC-12", "AC-14"],
            estimate_ids=["ES-05"],
        ),
        Shot(
            id="SH-03",
            beat_ids=["BT-03"],
            start_frame=125,
            end_frame=200,
            purpose="Deliver the sensory payoff and hold the label.",
            framing="Pack fills the frame; liquid wraps the lower half.",
            movement="Slow push-in; liquid peaks at frame 150 and falls.",
            subject="Pack, liquid ribbon and macro bubbles.",
            action="Splash peaks, then settles around the pack.",
            expression="Appetite and craft.",
            lighting="Backlit liquid with a warm edge.",
            palette="Caramel, copper, near-black.",
            transition_in="Match cut on the pack.",
            continuity="Pack label remains unobstructed; same pack scale direction.",
            method="Liquid and macro composite around the pack with type.",
            fallback_method="Pack hero still with an animated light sweep; no liquid simulation.",
            status=ShotStatus.READY,
            layer_ids=layer_ids("LY-03"),
            asset_ids=["AS-05", "AS-01", "AS-03"],
            check_ids=["AC-01", "AC-03", "AC-12", "AC-14"],
            estimate_ids=["ES-03", "ES-06"],
        ),
        Shot(
            id="SH-04",
            beat_ids=["BT-04"],
            start_frame=200,
            end_frame=250,
            purpose="Close on brand and a clear CTA.",
            framing="Logo top-center, pack center, CTA and caption below.",
            movement="Pack settles; CTA fades up on the final beat.",
            subject="Logo, pack and CTA.",
            action="End card holds for the final read.",
            expression="Confident, warm.",
            lighting="Even warm key; logo separated from background.",
            palette="Cream logo, copper pack, near-black ground.",
            transition_in="Splash wipe from SH-03.",
            continuity="Final pack orientation matches SH-02 and SH-03.",
            method="End-card composite: logo, pack, CTA and caption.",
            fallback_method="Typographic end card with logo and CTA if pack art is unavailable.",
            status=ShotStatus.READY,
            layer_ids=layer_ids("LY-04"),
            asset_ids=["AS-05", "AS-01", "AS-02"],
            check_ids=["AC-01", "AC-05", "AC-09", "AC-12", "AC-14"],
            estimate_ids=["ES-04", "ES-10"],
        ),
    ]


def _checks() -> list[AcceptanceCheck]:
    return [
        AcceptanceCheck(
            id="AC-01",
            target_ids=["DP-01", "SH-01", "SH-02", "SH-03", "SH-04"],
            description="Timeline covers exactly 250 frames across four contiguous shots.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["timing.deliverable", "timing.shots"],
        ),
        AcceptanceCheck(
            id="AC-02",
            target_ids=["SH-01", "SH-02", "SH-03", "SH-04"],
            description="All text sits inside the 1080x1920 safe area.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["layer.safe_area"],
        ),
        AcceptanceCheck(
            id="AC-03",
            target_ids=["LY-021", "LY-033", "LY-041", "LY-042"],
            description="Pack label and logo regions are not occluded by planned layers.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["layer.occlusion"],
        ),
        AcceptanceCheck(
            id="AC-04",
            target_ids=["ED-02", "ED-03", "ED-04"],
            description="No required layer depends on unapproved price or offer data.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["exact.critical"],
        ),
        AcceptanceCheck(
            id="AC-05",
            target_ids=["LY-042", "LY-043"],
            description="Brand and CTA are legible at 50 percent scale on a 1080x1920 phone.",
            method=CheckMethod.RENDER_PIXEL,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.brand_legibility"],
        ),
        AcceptanceCheck(
            id="AC-06",
            target_ids=["AU-01", "AU-02"],
            description="VO is intelligible and the music sits at least 6 dB under it.",
            method=CheckMethod.AUDIO,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.audio"],
        ),
        AcceptanceCheck(
            id="AC-07",
            target_ids=["ED-01", "ED-05"],
            description="Exact data in final pixels matches the approved values.",
            method=CheckMethod.RENDER_PIXEL,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.exact_pixels"],
        ),
        AcceptanceCheck(
            id="AC-08",
            target_ids=["CL-03", "ED-05"],
            description="Every used claim is verified and every exact reference resolves.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["exact.claims", "exact.references"],
        ),
        AcceptanceCheck(
            id="AC-09",
            target_ids=["SH-02", "SH-04"],
            description="A sound-off viewer understands the product and the brand.",
            method=CheckMethod.HUMAN,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.human_review"],
        ),
        AcceptanceCheck(
            id="AC-10",
            target_ids=["AS-01", "AS-02", "AS-03", "AS-05"],
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
            description="Final file is 1080x1920, 25 fps, 10.0 s, H.264/AAC.",
            method=CheckMethod.RENDER_PIXEL,
            level=CheckLevel.L2,
            rule_refs=["pending.level2.delivery"],
        ),
        AcceptanceCheck(
            id="AC-12",
            target_ids=["SH-02", "SH-03", "SH-04"],
            description="Contact sheet shows the pack clear of captions and platform UI.",
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
            target_ids=["SH-01", "SH-02", "SH-03", "SH-04"],
            description="Every shot has a primary and a genuinely different fallback method.",
            method=CheckMethod.STRUCTURAL,
            level=CheckLevel.L1,
            rule_refs=["trace.shots"],
        ),
    ]


def _alternates(*, fallback_fixed: bool) -> list[AlternateRoute]:
    alternates = [
        AlternateRoute(
            id="ALT-03",
            target_ids=["SH-03"],
            trigger="Liquid simulation overruns or reads poorly at phone size.",
            preserved="Sensory payoff and pack clarity.",
            revised_dependencies=["AS-01"],
            cost_delta_usd=0,
            approval_scope=["SH-03"],
        ),
        AlternateRoute(
            id="ALT-04",
            target_ids=["CP-05"],
            trigger="Brand rejects the proposed CTA wording.",
            preserved="Brand close with a direct CTA.",
            revised_dependencies=[],
            cost_delta_usd=0,
            approval_scope=["SH-04"],
        ),
    ]
    if fallback_fixed:
        alternates.extend(
            [
                AlternateRoute(
                    id="ALT-01",
                    target_ids=["AS-01"],
                    trigger="Brand pack file is missing or below 2000 px.",
                    preserved="Label exactness and pack silhouette.",
                    revised_dependencies=["AS-06"],
                    cost_delta_usd=2,
                    cost_estimate_id="ES-08",
                    approval_scope=["SH-02", "SH-03", "SH-04"],
                ),
                AlternateRoute(
                    id="ALT-02",
                    target_ids=["AS-01"],
                    trigger="No pack art or physical sample is available.",
                    preserved="Four-shot structure and brand close.",
                    revised_dependencies=[],
                    cost_delta_usd=0,
                    approval_scope=["SH-02", "SH-03", "SH-04"],
                ),
            ]
        )
    return alternates


def _held_items() -> list[HeldItem]:
    return [
        HeldItem(
            id="HI-01",
            title="Price and promotion confirmation",
            reason=(
                "The storefront price varies by pack size and the offer has no visible "
                "expiry or terms."
            ),
            affects=["ED-02", "ED-03", "ED-04"],
            required_evidence=(
                "Brand-approved hero size, advertising price, offer terms and expiry, "
                "with a named approver."
            ),
            owner=Owner.HUMAN,
        ),
        HeldItem(
            id="HI-02",
            title="Brand pack art, logo and font clearance",
            reason="No brand kit or advertising-use licence was supplied.",
            affects=["AS-01", "AS-02"],
            required_evidence=(
                "Pack art and vector logo with written advertising-use confirmation, "
                "plus the brand font or approval to use the placeholder."
            ),
            owner=Owner.HUMAN,
        ),
        HeldItem(
            id="HI-03",
            title="Music licence",
            reason="No track is selected or licensed.",
            affects=["AS-07"],
            required_evidence="A production-library licence covering organic and paid social.",
            owner=Owner.HUMAN,
        ),
    ]


def build_plan(
    project_id: str = PROJECT_ID,
    *,
    revision: int = 1,
    applied: frozenset[str] | None = None,
) -> ProductionPlan:
    applied = applied or frozenset()
    safe_fixed = "safe_area" in applied
    commercial_fixed = "commercial" in applied
    budget_fixed = "budget" in applied
    fallback_fixed = "fallback" in applied
    rights_fixed = "rights" in applied

    layers = _layers(
        safe_fixed=safe_fixed,
        commercial_fixed=commercial_fixed,
        budget_fixed=budget_fixed,
    )
    include_offer = not commercial_fixed
    assets = _assets(
        budget_fixed=budget_fixed,
        fallback_fixed=fallback_fixed,
        rights_fixed=rights_fixed,
    )

    return ProductionPlan(
        project_id=project_id,
        revision=revision,
        brief_revision=1,
        deliverable=_deliverable(),
        beats=_beats(include_offer=include_offer),
        shots=_shots(budget_fixed=budget_fixed, layers=layers),
        layers=layers,
        copy_blocks=_copy_blocks(include_offer=include_offer),
        exact_data=build_exact_data(),
        claims=build_claims(),
        assets=assets,
        audio_cues=[
            AudioCue(
                id="AU-01",
                start_frame=0,
                end_frame=230,
                kind=AudioKind.VO,
                description="Ethiopia. Speciality instant coffee. In an instant.",
                asset_id="AS-08",
                level_db=-3,
            ),
            AudioCue(
                id="AU-02",
                start_frame=0,
                end_frame=250,
                kind=AudioKind.MUSIC,
                description="Warm restrained electronic bed with a lift at the reveal.",
                asset_id="AS-07",
                level_db=-18,
            ),
            AudioCue(
                id="AU-03",
                start_frame=42,
                end_frame=52,
                kind=AudioKind.SFX,
                description="Short whoosh into the pack reveal.",
                asset_id="AS-09",
                level_db=-12,
            ),
            AudioCue(
                id="AU-04",
                start_frame=118,
                end_frame=150,
                kind=AudioKind.SFX,
                description="Liquid splash on the payoff beat.",
                asset_id="AS-10",
                level_db=-8,
            ),
            AudioCue(
                id="AU-05",
                start_frame=195,
                end_frame=225,
                kind=AudioKind.SFX,
                description="Low brand sting under the end card.",
                asset_id="AS-11",
                level_db=-10,
            ),
        ],
        transitions=[
            Transition(
                id="TR-01",
                from_shot_id="SH-01",
                to_shot_id="SH-02",
                at_frame=50,
                kind="light wipe",
                duration_frames=6,
            ),
            Transition(
                id="TR-02",
                from_shot_id="SH-02",
                to_shot_id="SH-03",
                at_frame=125,
                kind="match cut on pack",
                duration_frames=4,
            ),
            Transition(
                id="TR-03",
                from_shot_id="SH-03",
                to_shot_id="SH-04",
                at_frame=200,
                kind="splash wipe",
                duration_frames=8,
            ),
        ],
        alternates=_alternates(fallback_fixed=fallback_fixed),
        estimates=_estimates(budget_fixed=budget_fixed),
        budget=_budget(budget_fixed=budget_fixed),
        checks=_checks(),
        held_items=_held_items(),
        decisions=toffee_decisions(),
        assumptions=[
            "Audience is inferred from the INR storefront and specialty range.",
            "Safe area is a provisional operator assumption, not a platform guarantee.",
            "Inter (SIL OFL 1.1) is a documented placeholder for the brand font.",
            "Music and VO are planned as one licence and one human session.",
            "Pack size is not chosen; no price appears in the ready cut.",
        ],
        open_questions=[
            "Which pack size is the hero?",
            "Is the BOGO/B2G2 promotion approved for advertising, and with what expiry?",
            "Can the storefront pack art and logo be used in ads?",
            "Which landing page should the CTA open?",
            "Human or synthetic narration?",
        ],
    )
