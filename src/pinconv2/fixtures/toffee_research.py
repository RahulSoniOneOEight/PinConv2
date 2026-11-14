"""Brief and research fixture for the Toffee Coffee Roasters test run.

All web observations were recorded on 2026-11-14 from the public storefront.
The fixture deliberately keeps observed values separate from approved values.
"""

from __future__ import annotations

from ..models import (
    AssetReadiness,
    BriefRevision,
    Claim,
    ClaimStatus,
    ContentFamily,
    DataStatus,
    EvidenceReliability,
    EvidenceSource,
    ExactData,
    ExactField,
    Finding,
    FindingStatus,
    MustHave,
    Outcome,
    ProductRole,
    QualityTier,
    ResearchPack,
    ResearchQuestion,
    RightsStatus,
    Tag,
)

PROJECT_ID = "toffee-coffee-10s"
ACCESSED_AT = "2026-11-14"

BRIEF_TEXT = """Make a 10-second vertical ad for Toffee Coffee Roasters' Ethiopia Speciality
Instant Coffee. It should feel premium, warm and unmistakably Indian specialty coffee.
Open with a strong hook, reveal the pack, show the coffee's energy, then land the brand
and a clear call to action. Use a 9:16 frame for Instagram Reels and YouTube Shorts, with
captions for sound-off viewing. Use only approved product facts, price and promotion
details, and do not reuse any reference video footage. The production planning cap is
USD 60."""


def build_brief() -> BriefRevision:
    return BriefRevision(
        project_id=PROJECT_ID,
        revision=1,
        source_text=BRIEF_TEXT,
        title="Toffee Coffee Roasters - Ethiopia, in an instant",
        objective=(
            "Introduce the Ethiopia Speciality Instant Coffee in ten seconds and drive "
            "a qualified click to the product page."
        ),
        audience=(
            "Indian urban coffee drinkers aged 25-40 who already buy specialty coffee "
            "online, plus existing Toffee customers and small gift buyers. Inferred from "
            "the INR storefront and range; confirm with the brand."
        ),
        language="en",
        content_family=ContentFamily.AD,
        subject="speciality instant coffee",
        tones=[Tag.PREMIUM, Tag.WARM],
        outcome=Outcome.SELL,
        product_role=ProductRole.HERO,
        quality_tier=QualityTier.PREMIUM,
        asset_readiness=AssetReadiness.PARTIAL,
        series_pattern="one-off hero ad; optional three-variant test later",
        duration_seconds=10.0,
        fps=25,
        aspect_ratio="9:16",
        platform="Instagram Reels and YouTube Shorts",
        placements=["instagram_reels", "youtube_shorts"],
        captions=True,
        cta="Shop the Ethiopia range",
        budget_cap_usd=60.0,
        currency="USD",
        constraints=[
            "10.0 seconds, 1080x1920, 25 fps, 250 frames",
            "Captions must carry the story with sound off",
            "No price, offer or claim unless an approved exact-data record exists",
            "No reference video footage may be reused",
            "Paid asset generation belongs to Level 2, not Level 1",
            "One hero cut; no variant is required for this test",
        ],
        avoid=[
            "generic bean-sack imagery",
            "unapproved 'best coffee' or health claims",
            "hard-sell discount language before the brand reveal",
        ],
        assumptions=[
            "The audience is inferred from the INR storefront and specialty range.",
            "Reels and Shorts safe areas are operator assumptions until placement specs "
            "are confirmed.",
            "No brand font or brand guideline was supplied; Inter (SIL OFL 1.1) is a "
            "documented placeholder.",
        ],
        rights_notes=(
            "Storefront pack imagery and the logo are brand property. Their presence on "
            "the public site does not grant advertising use. Reference Shorts are "
            "inspiration only."
        ),
        must_have=[
            MustHave(
                id="MH-01",
                text="10.0-second vertical 9:16 ad at 1080x1920 and 25 fps",
                satisfied_by=["DP-01", "AC-01"],
                status="satisfied",
            ),
            MustHave(
                id="MH-02",
                text="Strong opening hook in the first two seconds",
                satisfied_by=["SH-01", "CP-01", "AC-02"],
                status="satisfied",
            ),
            MustHave(
                id="MH-03",
                text="Reveal the Ethiopia Speciality Instant Coffee pack",
                satisfied_by=["SH-02", "AS-01", "AC-03"],
                status="satisfied",
            ),
            MustHave(
                id="MH-04",
                text="Show coffee energy: liquid, macro texture and steam",
                satisfied_by=["SH-03", "AS-03"],
                status="satisfied",
            ),
            MustHave(
                id="MH-05",
                text="Land the Toffee brand and a clear call to action",
                satisfied_by=["SH-04", "CP-05", "AC-05"],
                status="satisfied",
            ),
            MustHave(
                id="MH-06",
                text="Captions that work with sound off",
                satisfied_by=["CP-11", "CP-12", "CP-13", "CP-14", "AC-09"],
                status="satisfied",
            ),
            MustHave(
                id="MH-07",
                text="Only approved product facts, price and promotion",
                satisfied_by=["ED-01", "ED-02", "ED-03", "AC-04"],
                status="satisfied",
            ),
            MustHave(
                id="MH-08",
                text="No reuse of reference video footage",
                satisfied_by=["AC-10"],
                status="satisfied",
            ),
            MustHave(
                id="MH-09",
                text="Premium, warm tone",
                satisfied_by=["SH-01", "SH-03", "DC-02"],
                status="satisfied",
            ),
        ],
        classification_confidence=0.9,
    )


def build_research_pack() -> ResearchPack:
    questions = [
        ResearchQuestion(
            id="RQ-01",
            question="Which Ethiopia SKU and pack size is the hero?",
            why_it_matters="Price, pack art and label copy change by variant.",
            priority=5,
            status="blocked",
            finding_ids=["F-01", "F-04"],
        ),
        ResearchQuestion(
            id="RQ-02",
            question="Is the BOGO/B2G2 promotion approved for advertising, and what are "
            "its terms and expiry?",
            why_it_matters="An unapproved offer is a commercial and legal risk.",
            priority=5,
            status="blocked",
            finding_ids=["F-02"],
        ),
        ResearchQuestion(
            id="RQ-03",
            question="Which product claims may be used in advertising?",
            why_it_matters="Origin and cup-count claims need substantiation and wording.",
            priority=4,
            status="blocked",
            finding_ids=["F-03"],
        ),
        ResearchQuestion(
            id="RQ-04",
            question="Do we have cleared pack art, logo, typography and brand guidelines?",
            why_it_matters="Pack and logo are exact commercial elements.",
            priority=5,
            status="blocked",
            finding_ids=["F-04", "F-08"],
        ),
        ResearchQuestion(
            id="RQ-05",
            question="What can the two benchmark Shorts actually establish?",
            why_it_matters="Only preview frames and titles were accessible.",
            priority=3,
            status="answered",
            finding_ids=["F-05", "F-06"],
        ),
        ResearchQuestion(
            id="RQ-06",
            question="What placement and safe-area rules apply?",
            why_it_matters="Text and product must survive platform UI and crops.",
            priority=4,
            status="answered",
            finding_ids=["F-07"],
        ),
        ResearchQuestion(
            id="RQ-07",
            question="Who is the primary viewer and what do they need in ten seconds?",
            why_it_matters="The hook, pace and CTA depend on the audience.",
            priority=4,
            status="answered",
            finding_ids=["F-09"],
        ),
    ]

    sources = [
        EvidenceSource(
            id="SRC-01",
            title="Toffee Coffee Roasters storefront",
            locator="https://toffeecoffeeroasters.com/",
            accessed_at=ACCESSED_AT,
            channels=["page_text", "price_listing", "promotion_banner", "brand_header"],
            reliability=EvidenceReliability.PRIMARY,
            notes="Public storefront captured as text; no legal or media licence granted.",
        ),
        EvidenceSource(
            id="SRC-02",
            title="Ethiopia Speciality Instant Coffee product page",
            locator=(
                "https://toffeecoffeeroasters.com/products/"
                "ethiopia-speciality-instant-coffee"
            ),
            accessed_at=ACCESSED_AT,
            channels=[
                "page_text",
                "price_listing",
                "variant_list",
                "product_gallery",
                "embedded_video_present",
            ],
            reliability=EvidenceReliability.PRIMARY,
            notes=(
                "Lists 50 gm at Rs 499 and 100 gm at Rs 699. Describes Ethiopia as "
                "'known as a Birthplace of Coffee' and 100 gm as making 50 cups."
            ),
        ),
        EvidenceSource(
            id="SRC-03",
            title="Coffee motion graphics advertisement (AK Edits)",
            locator="https://www.youtube.com/shorts/mH5IY6CpU8c",
            accessed_at=ACCESSED_AT,
            channels=["title", "preview_frame"],
            reliability=EvidenceReliability.REFERENCE,
            notes=(
                "Only the oEmbed title and hq2 preview frame were inspected. Editing, "
                "motion and audio were not reviewed."
            ),
        ),
        EvidenceSource(
            id="SRC-04",
            title="Peak Indian mom behaviour (Hows Hardy)",
            locator="https://www.youtube.com/shorts/qDvCZU-4d4Y",
            accessed_at=ACCESSED_AT,
            channels=["title", "preview_frame"],
            reliability=EvidenceReliability.REFERENCE,
            notes=(
                "Only the oEmbed title and hq2 preview frame were inspected. Timing, "
                "voice and animation were not reviewed."
            ),
        ),
        EvidenceSource(
            id="SRC-05",
            title="Operator assumption: Reels and Shorts safe areas",
            locator="internal://assumption/reels-shorts-safe-area",
            accessed_at=ACCESSED_AT,
            channels=["operator_assumption"],
            reliability=EvidenceReliability.ASSUMPTION,
            notes=(
                "Safe insets of top 220, bottom 320, left 60 and right 140 pixels are "
                "provisional and must be confirmed against current placement specs."
            ),
        ),
        EvidenceSource(
            id="SRC-06",
            title="SIL Open Font License 1.1",
            locator="https://openfontlicense.org/",
            accessed_at=ACCESSED_AT,
            channels=["licence_text"],
            reliability=EvidenceReliability.PRIMARY,
            notes="Inter is used as a placeholder brand font under the SIL OFL.",
        ),
    ]

    findings = [
        Finding(
            id="F-01",
            stage="research",
            observation=(
                "The Ethiopia product page lists 50 gm at Rs 499 and 100 gm at Rs 699, "
                "with a regular price of Rs 500 on the 50 gm variant."
            ),
            interpretation=(
                "The storefront headline 'from Rs 499' is not the price of every "
                "variant, so a single price card would be ambiguous."
            ),
            proposed_action=(
                "Do not put a price in the ready plan. Hold price until the hero size "
                "and the approved advertising price are confirmed."
            ),
            source_id="SRC-02",
            evidence_locator="Size selector and price block",
            observed_at=ACCESSED_AT,
            confidence=5,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=5,
            effort=1,
            linked_ids=["ED-02"],
        ),
        Finding(
            id="F-02",
            stage="research",
            observation=(
                "The storefront announcement banner offers Buy 1 Get 1 Free or Buy 2 "
                "Get 2 Free with code BOGO or B2G2 and a free mug. No expiry or terms "
                "are visible in the captured text."
            ),
            interpretation=(
                "A live banner is evidence that an offer exists, not approval to "
                "advertise its terms or to imply an expiry."
            ),
            proposed_action=(
                "Keep promotion out of the ready plan. Hold the offer, code and expiry "
                "until the brand confirms advertising use."
            ),
            source_id="SRC-01",
            evidence_locator="Announcement bar above the header",
            observed_at=ACCESSED_AT,
            confidence=4,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=5,
            effort=1,
            linked_ids=["ED-03", "ED-04"],
        ),
        Finding(
            id="F-03",
            stage="research",
            observation=(
                "The product page says Ethiopia is 'known as a Birthplace of Coffee', "
                "that 100 gm makes 50 cups, and describes a rich aroma with bold and "
                "fruity flavours."
            ),
            interpretation=(
                "These are brand-authored descriptions. They still need approved "
                "advertising wording and, for origin claims, legal review."
            ),
            proposed_action=(
                "Use only 'speciality instant coffee' with approved wording. Keep the "
                "birthplace and cup-count claims out of the ready copy."
            ),
            source_id="SRC-02",
            evidence_locator="Ethiopia Coffee bullet list",
            observed_at=ACCESSED_AT,
            confidence=4,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=4,
            effort=2,
            linked_ids=["CL-01", "CL-02", "CL-03", "CP-02"],
        ),
        Finding(
            id="F-04",
            stage="research",
            observation=(
                "The storefront exposes a product gallery and logo files on its CDN, "
                "but no brand kit, font, usage licence or advertising approval was "
                "supplied."
            ),
            interpretation=(
                "Public availability is not a licence. Pack art and logo are exact "
                "brand elements that must come from the brand."
            ),
            proposed_action=(
                "Request pack art, vector logo, font and usage terms. Hold brand assets "
                "as needs-approval until supplied."
            ),
            source_id="SRC-01",
            evidence_locator="Product gallery and header logo",
            observed_at=ACCESSED_AT,
            confidence=4,
            status=FindingStatus.HELD,
            rights_status=RightsStatus.NEEDS_APPROVAL,
            impact=5,
            effort=2,
            linked_ids=["AS-01", "AS-02"],
        ),
        Finding(
            id="F-05",
            stage="research",
            observation=(
                "The coffee reference preview frame shows a dark, high-contrast product "
                "composition with liquid, bold vertical type and a logo."
            ),
            interpretation=(
                "This supports a premium product-hero visual language, but only the "
                "preview frame was accessible."
            ),
            proposed_action=(
                "Adapt the visual principles, not the media. Plan a product-led hero "
                "with dark warm grade and bold type."
            ),
            source_id="SRC-03",
            evidence_locator="hq2 preview frame",
            observed_at=ACCESSED_AT,
            confidence=3,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.REFERENCE_ONLY,
            impact=4,
            effort=2,
            linked_ids=["DC-02", "CO-01"],
        ),
        Finding(
            id="F-06",
            stage="research",
            observation=(
                "The character reference preview frame shows a bright 2D character, "
                "bold top caption and an Indian street setting."
            ),
            interpretation=(
                "This is a viable character-led route, but not the strongest route for "
                "a ten-second product ad with one hero SKU."
            ),
            proposed_action=(
                "Keep a character-led concept as the third option; do not use the "
                "reference footage."
            ),
            source_id="SRC-04",
            evidence_locator="hq2 preview frame",
            observed_at=ACCESSED_AT,
            confidence=3,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.REFERENCE_ONLY,
            impact=3,
            effort=3,
            linked_ids=["DC-02", "CO-03"],
        ),
        Finding(
            id="F-07",
            stage="research",
            observation=(
                "Reels and Shorts are 9:16, sound-off by default, and overlay UI on the "
                "top, bottom and right edge."
            ),
            interpretation=(
                "Captions and product must stay inside a conservative safe area; the "
                "exact insets are provisional."
            ),
            proposed_action=(
                "Plan a four-shot story with burned-in captions and a safe area of top "
                "220, bottom 320, left 60, right 140."
            ),
            source_id="SRC-05",
            evidence_locator="Operator assumption",
            observed_at=ACCESSED_AT,
            confidence=3,
            status=FindingStatus.ASSUMPTION,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=4,
            effort=1,
            linked_ids=["DP-01", "DC-03"],
        ),
        Finding(
            id="F-08",
            stage="research",
            observation=(
                "No brand font or typographic guideline was supplied in the brief or on "
                "the public storefront."
            ),
            interpretation=(
                "A placeholder font is acceptable for the plan, but not for final brand "
                "delivery."
            ),
            proposed_action=(
                "Use Inter under the SIL OFL for the plan and flag replacement when the "
                "brand kit arrives."
            ),
            source_id="SRC-06",
            evidence_locator="SIL Open Font License 1.1",
            observed_at=ACCESSED_AT,
            confidence=4,
            status=FindingStatus.ASSUMPTION,
            rights_status=RightsStatus.CLEARED,
            impact=3,
            effort=1,
            linked_ids=["DC-04"],
        ),
        Finding(
            id="F-09",
            stage="research",
            observation=(
                "The storefront prices in INR, sells single-origin, filter, instant and "
                "gift coffee, and positions itself as specialty coffee."
            ),
            interpretation=(
                "The likely buyer values origin and craft more than discount, so the "
                "hook should lead with origin and product, not price."
            ),
            proposed_action=(
                "Lead with Ethiopia and the instant format; keep the CTA direct."
            ),
            source_id="SRC-01",
            evidence_locator="Navigation, product range and pricing",
            observed_at=ACCESSED_AT,
            confidence=3,
            status=FindingStatus.ASSUMPTION,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=4,
            effort=1,
            linked_ids=["CO-01", "HK-01"],
        ),
        Finding(
            id="F-10",
            stage="research",
            observation=(
                "A ten-second product ad has roughly four usable beats: hook, reveal, "
                "payoff and brand close."
            ),
            interpretation=(
                "Four shots at 2s, 3s, 3s and 2s give each beat enough hold without "
                "rushing the product."
            ),
            proposed_action="Plan four shots over 250 frames at 25 fps.",
            source_id="SRC-05",
            evidence_locator="Operator planning assumption",
            observed_at=ACCESSED_AT,
            confidence=3,
            status=FindingStatus.ASSUMPTION,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=4,
            effort=1,
            linked_ids=["BT-01", "BT-02", "BT-03", "BT-04"],
        ),
        Finding(
            id="F-11",
            stage="research",
            observation="No music track has been selected or licensed.",
            interpretation=(
                "The cut needs a cleared bed; an unlicensed track cannot enter a render."
            ),
            proposed_action=(
                "Budget one library licence and keep a second track as a fallback."
            ),
            source_id="SRC-05",
            evidence_locator="Operator assumption",
            observed_at=ACCESSED_AT,
            confidence=3,
            status=FindingStatus.UNVERIFIED,
            rights_status=RightsStatus.UNKNOWN,
            impact=4,
            effort=2,
            linked_ids=["AS-07"],
        ),
        Finding(
            id="F-12",
            stage="research",
            observation="The brief does not say whether narration is human or synthetic.",
            interpretation=(
                "A human VO needs a release; synthetic narration needs an AI disclosure "
                "decision."
            ),
            proposed_action=(
                "Plan a recorded VO with a release and keep disclosed synthetic "
                "narration as the fallback."
            ),
            source_id="SRC-05",
            evidence_locator="Operator assumption",
            observed_at=ACCESSED_AT,
            confidence=3,
            status=FindingStatus.ASSUMPTION,
            rights_status=RightsStatus.NEEDS_APPROVAL,
            impact=3,
            effort=2,
            linked_ids=["AS-08", "AS-14"],
        ),
    ]

    return ResearchPack(
        project_id=PROJECT_ID,
        revision=1,
        questions=questions,
        sources=sources,
        findings=findings,
        synthesis=(
            "The product is real and the storefront gives usable raw material, but the "
            "commercial layer is not approved: the hero size, advertising price, offer "
            "terms, claims, pack art and logo all remain holds. The creative route can "
            "still be planned because the visual and audio work does not depend on those "
            "values. The two benchmark Shorts establish visual principles only; their "
            "video and audio were not inspected and their media cannot be reused. The "
            "plan therefore leads with origin and product craft, uses captions for "
            "sound-off viewing, and keeps price and promotion out of the ready cut until "
            "a named human approves them."
        ),
    )


def build_exact_data() -> list[ExactData]:
    return [
        ExactData(
            id="ED-01",
            field=ExactField.PRODUCT_NAME,
            value="Ethiopia Speciality Instant Coffee",
            status=DataStatus.OBSERVED,
            source_id="SRC-02",
            evidence_locator="Product title",
            notes="Brand product name; Gate 1 must approve the identifier.",
        ),
        ExactData(
            id="ED-02",
            field=ExactField.PRICE,
            value="50 gm: Rs 499; 100 gm: Rs 699",
            status=DataStatus.OBSERVED,
            source_id="SRC-02",
            evidence_locator="Size selector and price block",
            notes="Variant-dependent. Not approved for advertising.",
        ),
        ExactData(
            id="ED-03",
            field=ExactField.OFFER,
            value="Buy 1 Get 1 Free or Buy 2 Get 2 Free (+ free mug)",
            status=DataStatus.OBSERVED,
            source_id="SRC-01",
            evidence_locator="Announcement bar",
            notes="Expiry and terms are not visible. Not approved for advertising.",
        ),
        ExactData(
            id="ED-04",
            field=ExactField.PROMO_CODE,
            value="BOGO / B2G2",
            status=DataStatus.OBSERVED,
            source_id="SRC-01",
            evidence_locator="Announcement bar",
            notes="Code exists on the storefront; advertising use is unconfirmed.",
        ),
        ExactData(
            id="ED-05",
            field=ExactField.CTA,
            value="Shop the Ethiopia range",
            status=DataStatus.PROPOSED,
            notes="Proposed creative CTA. Gate 1 must approve the exact wording.",
        ),
        ExactData(
            id="ED-06",
            field=ExactField.BRAND_NAME,
            value="Toffee Coffee Roasters",
            status=DataStatus.OBSERVED,
            source_id="SRC-01",
            evidence_locator="Header logo and footer",
            notes="Brand identifier observed on the storefront.",
        ),
        ExactData(
            id="ED-07",
            field=ExactField.ORIGIN,
            value="Ethiopia",
            status=DataStatus.OBSERVED,
            source_id="SRC-02",
            evidence_locator="Ethiopia Coffee section",
            notes="Origin name from the product page.",
        ),
        ExactData(
            id="ED-08",
            field=ExactField.PACK_SIZE,
            value="50 gm / 100 gm",
            status=DataStatus.OBSERVED,
            source_id="SRC-02",
            evidence_locator="Size selector",
            notes="Hero size has not been chosen.",
        ),
    ]


def build_claims() -> list[Claim]:
    return [
        Claim(
            id="CL-01",
            text="Ethiopia is the birthplace of coffee",
            status=ClaimStatus.UNVERIFIED,
            source_ids=["SRC-02"],
            evidence_locator="Ethiopia Coffee bullet list",
            limitations=(
                "The brand page says 'known as a Birthplace of Coffee'; this is not "
                "independent substantiation."
            ),
        ),
        Claim(
            id="CL-02",
            text="Makes 50 cups per 100 g",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-02"],
            evidence_locator="Ethiopia Coffee bullet list",
            limitations="Brand-authored serving estimate; advertising wording not approved.",
        ),
        Claim(
            id="CL-03",
            text="Speciality instant coffee",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-02"],
            evidence_locator="Product title and category",
            approved_wording="speciality instant coffee",
            limitations="Use as a category descriptor, not a superiority claim.",
            used_in=["CP-02", "CP-12"],
        ),
        Claim(
            id="CL-04",
            text="Rich aroma with bold and fruity flavours",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-02"],
            evidence_locator="Ethiopia Coffee bullet list",
            limitations="Sensory description; advertising wording not approved.",
        ),
        Claim(
            id="CL-05",
            text="Have it black or with milk or cream",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-02"],
            evidence_locator="Ethiopia Coffee bullet list",
            limitations="Serving suggestion; not used in this cut.",
        ),
    ]
