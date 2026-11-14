"""Brief and research fixture for the Blue Tokai Easy Pour 20-second ad.

Observations were recorded from the public Blue Tokai storefront on 2026-11-14.
Public product imagery is recorded as an observed reference URL, not as a
cleared advertising licence. Audience and message are supplied by the brief;
only category and product facts are researched.
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

PROJECT_ID = "blue-tokai-easy-pour-20s"
ACCESSED_AT = "2026-11-14"

BRIEF_TEXT = """Blue Tokai Easy Pour - 20-second YouTube ad.

Objective: drive first-time online purchases of Blue Tokai Easy Pour. Feature the
Mixed Bag so people new to specialty coffee can try roasts ranging from light to
dark. bluetokaicoffee.com

Target audience: coffee drinkers in India who want specialty coffee at home or at
work without buying brewing equipment. Busy professionals who already buy cafe
coffee or drink instant coffee at home and are curious about easy pour-over.

Core message: Specialty coffee. Just a mug and hot water. Show the Easy Pour
filter clipped to a mug, the water hitting the grounds, and the finished cup. The
filter is built into the sachet, so the demo makes the benefit visible.

Call to action: Shop Easy Pour. Pair the CTA with the Mixed Bag pack and the Blue
Tokai logo on the end card."""

LOGO_URL = "https://bluetokaicoffee.com/cdn/shop/files/logo-footer.png?v=1688108473"
MIXED_BAG_URL = (
    "https://bluetokaicoffee.com/cdn/shop/files/"
    "MixedBag__Front_c9b610f1-ce4a-4b53-8b30-f6ca758eb6bb.jpg?v=1717566490"
)
VIENNA_URL = (
    "https://bluetokaicoffee.com/cdn/shop/files/"
    "ViennaRoast__Front_1_a175faba-8e5f-40b8-aaa1-0efc3a525321.jpg?v=1717565466"
)
ATTIKAN_URL = "https://bluetokaicoffee.com/cdn/shop/files/AttikanEstate__Front.jpg?v=1764321548"
SEETHARGUNDU_URL = (
    "https://bluetokaicoffee.com/cdn/shop/files/Seethargundu-Estate__Front_1.jpg?v=1764321548"
)


def build_blue_tokai_brief() -> BriefRevision:
    return BriefRevision(
        project_id=PROJECT_ID,
        revision=1,
        source_text=BRIEF_TEXT,
        title="Blue Tokai Easy Pour - specialty coffee, just a mug and hot water",
        objective=(
            "Drive first-time online purchases of Blue Tokai Easy Pour by making the "
            "built-in-filter brewing benefit visible in 20 seconds."
        ),
        audience=(
            "Indian coffee drinkers who want specialty coffee at home or work without "
            "buying brewing equipment; busy professionals who already buy cafe coffee "
            "or instant coffee and are curious about easy pour-over. Supplied by the "
            "brief; not independently audience-tested."
        ),
        language="en",
        content_family=ContentFamily.AD,
        subject="Easy Pour single-serve specialty coffee",
        tones=[Tag.PREMIUM, Tag.INFORMATIVE, Tag.WARM],
        outcome=Outcome.SELL,
        product_role=ProductRole.HERO,
        quality_tier=QualityTier.PREMIUM,
        asset_readiness=AssetReadiness.PARTIAL,
        series_pattern="one 20-second YouTube hero; optional 9:16 Shorts cut later",
        duration_seconds=20.0,
        fps=25,
        aspect_ratio="16:9",
        platform="YouTube",
        placements=["youtube_in_stream", "youtube_demand_gen"],
        captions=True,
        cta="Shop Easy Pour",
        budget_cap_usd=100.0,
        currency="USD",
        constraints=[
            "20.0 seconds, 1920x1080, 25 fps, 500 frames",
            "Show the filter clipped to a mug, water hitting the grounds and a finished cup",
            "Feature the Mixed Bag and the light-to-dark roast range",
            "End card pairs the CTA with the Mixed Bag pack and Blue Tokai logo",
            "Captions must work with sound off",
            "No price or promotion unless approved exact data exists",
            "Paid asset generation belongs to Level 2, not Level 1",
        ],
        avoid=[
            "calling Easy Pour instant coffee",
            "showing equipment the product does not need",
            "using public product images as if they were licensed advertising assets",
            "implying a real-time brew when the film compresses time",
        ],
        assumptions=[
            "16:9 YouTube in-stream is the primary placement; a 9:16 Shorts cut is optional.",
            "The supplied audience and core message are treated as brief inputs, "
            "not research findings.",
            "The budget cap is an operator planning assumption because the brief gives none.",
            "The 20-second film compresses a brew that the brand says needs a short steep.",
            "Public logo and product images are observed references; advertising "
            "rights are pending.",
            "Inter is used as a documented placeholder until Blue Tokai supplies its "
            "brand typeface.",
        ],
        rights_notes=(
            "Blue Tokai owns the logo, packs and product photography. Public availability "
            "is not an advertising licence. Demonstration footage needs a performer/hand "
            "release. Music and voice need licences."
        ),
        must_have=[
            MustHave(
                id="MH-01",
                text="20.0-second 16:9 YouTube ad at 1920x1080 and 25 fps",
                satisfied_by=["DP-01", "AC-01"],
                status="satisfied",
            ),
            MustHave(
                id="MH-02",
                text="Open on specialty coffee and the product within the first three seconds",
                satisfied_by=["SH-01", "CP-01", "AC-02"],
                status="satisfied",
            ),
            MustHave(
                id="MH-03",
                text="Show the built-in filter clipped to a mug and water hitting the grounds",
                satisfied_by=["SH-02", "SH-03", "AS-05", "AS-06"],
                status="satisfied",
            ),
            MustHave(
                id="MH-04",
                text="Show the finished cup",
                satisfied_by=["SH-05", "AS-08"],
                status="satisfied",
            ),
            MustHave(
                id="MH-05",
                text="Feature the Mixed Bag and the light-to-dark roast range",
                satisfied_by=["SH-04", "AS-02", "AS-03", "AS-04", "AS-17"],
                status="satisfied",
            ),
            MustHave(
                id="MH-06",
                text="End on the Blue Tokai logo, Mixed Bag pack and Shop Easy Pour CTA",
                satisfied_by=["SH-06", "CP-05", "AS-01", "AS-02"],
                status="satisfied",
            ),
            MustHave(
                id="MH-07",
                text="Captions carry the message with sound off",
                satisfied_by=["CP-01", "CP-03", "CP-04", "CP-05"],
                status="satisfied",
            ),
            MustHave(
                id="MH-08",
                text=(
                    "Ready cut excludes unapproved price, promotion and product claims; "
                    "pending identifiers are Gate 1 conditions"
                ),
                satisfied_by=["ED-01", "ED-02", "ED-03", "AC-04"],
                status="satisfied",
            ),
            MustHave(
                id="MH-09",
                text="Do not call Easy Pour instant coffee or imply it needs equipment",
                satisfied_by=["CL-02", "CL-05", "SH-03"],
                status="satisfied",
            ),
        ],
        classification_confidence=0.9,
    )


def build_blue_tokai_research() -> ResearchPack:
    questions = [
        ResearchQuestion(
            id="RQ-01",
            question=(
                "What exactly is in the Easy Pour Mixed Bag and what roast range does it cover?"
            ),
            why_it_matters="The range claim and hero pack depend on the actual assortment.",
            priority=5,
            status="answered",
            finding_ids=["F-01"],
        ),
        ResearchQuestion(
            id="RQ-02",
            question="How does the built-in filter brew, step by step?",
            why_it_matters="The core demo must show the real product action, not an invented one.",
            priority=5,
            status="answered",
            finding_ids=["F-02"],
        ),
        ResearchQuestion(
            id="RQ-03",
            question="Can the ad call Easy Pour instant coffee?",
            why_it_matters="A category error would mislead the viewer and damage trust.",
            priority=5,
            status="answered",
            finding_ids=["F-03"],
        ),
        ResearchQuestion(
            id="RQ-04",
            question="Which price and pack-size values are approved for advertising?",
            why_it_matters="Observed storefront values are not approved commercial claims.",
            priority=5,
            status="blocked",
            finding_ids=["F-04"],
        ),
        ResearchQuestion(
            id="RQ-05",
            question="May the public logo and product images be used in paid advertising?",
            why_it_matters="Public availability is not an advertising licence.",
            priority=5,
            status="blocked",
            finding_ids=["F-05"],
        ),
        ResearchQuestion(
            id="RQ-06",
            question="What YouTube format, length and safe-area rules apply?",
            why_it_matters="The edit, type placement and end card depend on the placement.",
            priority=4,
            status="answered",
            finding_ids=["F-06"],
        ),
        ResearchQuestion(
            id="RQ-07",
            question="What hook, brand and CTA structure fits a 20-second YouTube ad?",
            why_it_matters=(
                "A 20-second ad needs early attention, early brand and a clear direction."
            ),
            priority=4,
            status="answered",
            finding_ids=["F-07"],
        ),
        ResearchQuestion(
            id="RQ-08",
            question="Can a real brew be shown honestly in 20 seconds?",
            why_it_matters=("The brand instructions include a steep time longer than the ad."),
            priority=4,
            status="answered",
            finding_ids=["F-02", "F-08"],
        ),
        ResearchQuestion(
            id="RQ-09",
            question="Who is the viewer and what do they already believe?",
            why_it_matters="The hook and proof depend on the viewer's starting point.",
            priority=4,
            status="blocked",
            finding_ids=["F-09"],
        ),
    ]

    sources = [
        EvidenceSource(
            id="SRC-01",
            title="Blue Tokai Coffee Roasters storefront",
            locator="https://bluetokaicoffee.com/",
            accessed_at=ACCESSED_AT,
            channels=["page_text", "product_cards", "brand_header", "product_images"],
            reliability=EvidenceReliability.PRIMARY,
            notes="Public storefront; no advertising licence is granted by access.",
        ),
        EvidenceSource(
            id="SRC-02",
            title="Mixed | Light to Dark Roasts - Easy Pour product page",
            locator="https://bluetokaicoffee.com/products/mixed-light-to-dark-roasts",
            accessed_at=ACCESSED_AT,
            channels=["page_text", "variant_list", "product_gallery", "price_listing"],
            reliability=EvidenceReliability.PRIMARY,
            notes=(
                "Lists pack of 5 at Rs 300 and pack of 10 at Rs 500. Names "
                "Seethargundu light, Vienna dark, Thogarihunkal medium and Attikan "
                "medium-dark."
            ),
        ),
        EvidenceSource(
            id="SRC-03",
            title="Vienna | Dark Roast - Easy Pour product page",
            locator=(
                "https://bluetokaicoffee.com/products/vienna-dark-roast-easy-pour-coffee-sachets"
            ),
            accessed_at=ACCESSED_AT,
            channels=["page_text", "product_gallery", "price_listing"],
            reliability=EvidenceReliability.PRIMARY,
            notes="Describes Vienna as a dark roast with cocoa and bitterness.",
        ),
        EvidenceSource(
            id="SRC-04",
            title="Attikan Estate | Medium-Dark Roast - Easy Pour product page",
            locator=(
                "https://bluetokaicoffee.com/collections/all-products-except-drop/"
                "products/attikan-estate-easy-pour-coffee-sachets"
            ),
            accessed_at=ACCESSED_AT,
            channels=["page_text", "product_gallery", "price_listing"],
            reliability=EvidenceReliability.PRIMARY,
            notes="Describes Attikan as medium-dark with nutty and chocolatey notes.",
        ),
        EvidenceSource(
            id="SRC-05",
            title="Easy Pour brewing instructions",
            locator="https://bluetokaicoffee.com/pages/easypour",
            accessed_at=ACCESSED_AT,
            channels=["page_text", "instruction_images", "faq"],
            reliability=EvidenceReliability.PRIMARY,
            notes=(
                "Tear the outer sachet, tear the filter top, anchor over a 180-200 ml "
                "cup, pour hot water and wait 20 seconds; repeat 2-3 times; steep 2 "
                "minutes; discard the filter."
            ),
        ),
        EvidenceSource(
            id="SRC-06",
            title="Google Ads: About the ABCDs of effective video ads",
            locator="https://support.google.com/google-ads/answer/14783551?hl=en",
            accessed_at=ACCESSED_AT,
            channels=["guidance_text"],
            reliability=EvidenceReliability.SECONDARY,
            notes=(
                "Attention, Branding, Connection, Direction. Brand early and often; "
                "clear CTA; focused message."
            ),
        ),
        EvidenceSource(
            id="SRC-07",
            title="Google Ads: About video ad specs",
            locator="https://support.google.com/google-ads/answer/13547298?hl=en",
            accessed_at=ACCESSED_AT,
            channels=["spec_table", "safe_zone_template"],
            reliability=EvidenceReliability.SECONDARY,
            notes=(
                "1920x1080 horizontal and 1080x1920 vertical are recommended; safe "
                "zones vary by placement and should be checked against the template."
            ),
        ),
        EvidenceSource(
            id="SRC-08",
            title="Operator assumption: 16:9 YouTube in-stream profile",
            locator="internal://assumption/youtube-16x9-safe-area",
            accessed_at=ACCESSED_AT,
            channels=["operator_assumption"],
            reliability=EvidenceReliability.ASSUMPTION,
            notes=(
                "Safe insets top 70, bottom 90, left 80 and right 80 are a conservative "
                "planning assumption, not a platform guarantee."
            ),
        ),
        EvidenceSource(
            id="SRC-09",
            title="Brief-supplied audience and core message",
            locator="internal://brief/blue-tokai-easy-pour-20s",
            accessed_at=ACCESSED_AT,
            channels=["brief_text"],
            reliability=EvidenceReliability.PRIMARY,
            notes=(
                "The brief is authoritative for user-supplied requirements and asset "
                "links, not for independent audience evidence."
            ),
        ),
    ]

    findings = [
        Finding(
            id="F-01",
            stage="research",
            observation=(
                "The Mixed Bag page describes a range of single-estate coffees from "
                "light to dark: Seethargundu light, Thogarihunkal medium, Attikan "
                "medium-dark and Vienna dark. It is sold as a pack of 5 or 10."
            ),
            interpretation=(
                "The Mixed Bag is a variety product, so the film can show a range of "
                "roast levels without inventing a new assortment."
            ),
            proposed_action=(
                "Use the Mixed Bag as the hero and show four packs: Mixed Bag, "
                "Seethargundu light, Attikan medium-dark and Vienna dark. Say only "
                "'light to dark'."
            ),
            source_id="SRC-02",
            evidence_locator="Product description and variant list",
            observed_at=ACCESSED_AT,
            confidence=5,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=5,
            effort=1,
            linked_ids=["ED-01", "CL-03", "CP-04"],
        ),
        Finding(
            id="F-02",
            stage="research",
            observation=(
                "The brewing instructions say to tear the outer sachet, tear the filter "
                "top, anchor the filter over a 180-200 ml cup, pour hot water, wait 20 "
                "seconds, repeat 2-3 times, then steep for 2 minutes."
            ),
            interpretation=(
                "The real action is a multi-step brew with a steep that cannot fit in "
                "20 seconds at real speed. A truthful demo needs time compression and a "
                "visible disclosure."
            ),
            proposed_action=(
                "Show tear, anchor and pour, then compress the repeated pours and steep "
                "with a time-lapse cue and the caption 'Brew sequence compressed'."
            ),
            source_id="SRC-05",
            evidence_locator="Step 1-4 instructions",
            observed_at=ACCESSED_AT,
            confidence=5,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=5,
            effort=2,
            linked_ids=["SH-02", "SH-03", "SH-05", "CP-12"],
        ),
        Finding(
            id="F-03",
            stage="research",
            observation=(
                "The Easy Pour FAQ says it is not powdered instant coffee or a premix, "
                "but is as quick and hassle-free to brew."
            ),
            interpretation=(
                "Calling it instant coffee would be a category error. The ad should "
                "contrast specialty coffee with the convenience, not the product."
            ),
            proposed_action=("Use 'specialty coffee' and 'no equipment', never 'instant coffee'."),
            source_id="SRC-05",
            evidence_locator="FAQ: Is this the same as instant coffee?",
            observed_at=ACCESSED_AT,
            confidence=5,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=5,
            effort=1,
            linked_ids=["CL-01", "CL-02", "CP-01"],
        ),
        Finding(
            id="F-04",
            stage="research",
            observation=(
                "The Mixed Bag page lists pack of 5 at Rs 300 and pack of 10 at Rs 500. "
                "The brief does not approve a price or hero pack size."
            ),
            interpretation=(
                "Price and pack size are observed commercial values. They cannot enter "
                "the ready cut without brand approval."
            ),
            proposed_action=(
                "Keep price out of the ready cut and hold the hero pack size for brand "
                "confirmation."
            ),
            source_id="SRC-02",
            evidence_locator="Variant selector and price block",
            observed_at=ACCESSED_AT,
            confidence=5,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=5,
            effort=1,
            linked_ids=["ED-02", "ED-03"],
        ),
        Finding(
            id="F-05",
            stage="research",
            observation=(
                "The storefront exposes the Blue Tokai logo and product images on its "
                "CDN, but the brief supplies links only and no advertising licence or "
                "brand kit."
            ),
            interpretation=(
                "The images are technically usable references, not cleared paid-media "
                "assets. Pack labels are exact commercial elements."
            ),
            proposed_action=(
                "Use the observed URLs as the asset source of record, request written "
                "advertising approval, and hold the pack and logo until cleared."
            ),
            source_id="SRC-01",
            evidence_locator="Header logo and product galleries",
            observed_at=ACCESSED_AT,
            confidence=5,
            status=FindingStatus.HELD,
            rights_status=RightsStatus.NEEDS_APPROVAL,
            impact=5,
            effort=2,
            linked_ids=["AS-01", "AS-02", "AS-03", "AS-04", "AS-13"],
        ),
        Finding(
            id="F-06",
            stage="research",
            observation=(
                "Google recommends 1920x1080 horizontal and 1080x1920 vertical video, "
                "and publishes placement-specific safe-zone templates."
            ),
            interpretation=(
                "16:9 is a valid YouTube master. Exact safe insets must be checked "
                "against the chosen placement rather than assumed universal."
            ),
            proposed_action=(
                "Plan a 1920x1080 master with conservative insets and a placement "
                "preview before paid media."
            ),
            source_id="SRC-07",
            evidence_locator="Video ad specs table and safe-zone templates",
            observed_at=ACCESSED_AT,
            confidence=4,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=4,
            effort=1,
            linked_ids=["DP-01", "AC-02"],
        ),
        Finding(
            id="F-07",
            stage="research",
            observation=(
                "Google's ABCD guidance asks for early attention, early and repeated "
                "branding, focused connection and a clear direction or CTA."
            ),
            interpretation=(
                "A 20-second ad can use a 3-second hook, a 7-second demo, a 5-second "
                "range proof and a 5-second close."
            ),
            proposed_action=(
                "Put the pack and brand in the hook, keep the demo single-minded, and "
                "land the CTA on the end card."
            ),
            source_id="SRC-06",
            evidence_locator="Core ABCDs and Shorts guidance",
            observed_at=ACCESSED_AT,
            confidence=4,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=4,
            effort=2,
            linked_ids=["SH-01", "SH-06", "CP-05"],
        ),
        Finding(
            id="F-08",
            stage="research",
            observation=(
                "The brand's brew instructions include a 2-minute steep after pouring. "
                "A 20-second film cannot show that at real speed."
            ),
            interpretation=(
                "Time compression is a production treatment, not a product claim. It "
                "needs an on-screen disclosure so the demo remains honest."
            ),
            proposed_action=(
                "Use a time-lapse transition and a small 'Brew sequence compressed' "
                "disclaimer in the payoff shot."
            ),
            source_id="SRC-05",
            evidence_locator="Step 3-4 and FAQ",
            observed_at=ACCESSED_AT,
            confidence=5,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=4,
            effort=1,
            linked_ids=["CP-12", "SH-05"],
        ),
        Finding(
            id="F-09",
            stage="research",
            observation=(
                "The brief defines the viewer as busy Indian professionals who already "
                "buy cafe or instant coffee and want specialty coffee without equipment."
            ),
            interpretation=(
                "The viewer needs the benefit demonstrated, not a origin lecture. The "
                "hook should name the category and show the pack immediately."
            ),
            proposed_action=("Open on 'Specialty coffee' with the pack; use the demo as proof."),
            source_id="SRC-09",
            evidence_locator="Brief target audience and core message",
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
                "No finished voice-over, music bed or demonstration footage was supplied."
            ),
            interpretation=(
                "The demo and audio are production requirements with rights and consent "
                "gates, not assets already available."
            ),
            proposed_action=(
                "Record the demo, voice and music in Level 2; hold the performer and "
                "licence approvals."
            ),
            source_id="SRC-09",
            evidence_locator="Brief inputs",
            observed_at=ACCESSED_AT,
            confidence=5,
            status=FindingStatus.HELD,
            rights_status=RightsStatus.NEEDS_APPROVAL,
            impact=4,
            effort=3,
            linked_ids=["AS-05", "AS-06", "AS-09", "AS-10"],
        ),
        Finding(
            id="F-11",
            stage="research",
            observation=(
                "The brief names the Mixed Bag, Vienna and Attikan Estate packs and "
                "supplies the logo and product-image links. Seethargundu is added from "
                "the Mixed Bag page to provide the light endpoint."
            ),
            interpretation=(
                "The exact product set is fixed by the brief, while the creative use of "
                "each pack still needs a composition decision."
            ),
            proposed_action=(
                "Use Mixed Bag as hero, Seethargundu, Attikan and Vienna as range "
                "support, and keep each label unobstructed."
            ),
            source_id="SRC-09",
            evidence_locator="Brief asset list",
            observed_at=ACCESSED_AT,
            confidence=5,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NEEDS_APPROVAL,
            impact=4,
            effort=2,
            linked_ids=["AS-02", "AS-03", "AS-04"],
        ),
        Finding(
            id="F-12",
            stage="research",
            observation=(
                "The brand describes Easy Pour as specialty coffee brewed with hot "
                "water in a 180-200 ml cup, with no equipment."
            ),
            interpretation=(
                "The core message is supported by the brand's own instructions, but it "
                "is still brand-authored rather than independent product testing."
            ),
            proposed_action=(
                "Use 'no equipment' and 'just a mug and hot water' as brand-supported "
                "wording, not a superiority claim."
            ),
            source_id="SRC-05",
            evidence_locator="Brewing instructions and FAQ",
            observed_at=ACCESSED_AT,
            confidence=4,
            status=FindingStatus.VERIFIED,
            rights_status=RightsStatus.NOT_APPLICABLE,
            impact=4,
            effort=1,
            linked_ids=["CL-02", "CP-02"],
        ),
    ]

    return ResearchPack(
        project_id=PROJECT_ID,
        revision=1,
        questions=questions,
        sources=sources,
        findings=findings,
        synthesis=(
            "The product and its core benefit are supported by Blue Tokai's own product "
            "and brewing pages: a single-serve sachet with a built-in paper filter, "
            "brewed over a 180-200 ml cup with hot water, and a Mixed Bag spanning "
            "light to dark roasts. The honest creative route is a visible demo, not an "
            "instant-coffee comparison. Price, pack sizes and public product images are "
            "observed commercial material and remain rights or approval holds. A real "
            "brew includes repeated pours and a two-minute steep, so the film must "
            "disclose time compression rather than imply real-time brewing. The range shot "
            "needs a real light endpoint, so Seethargundu is added to the supplied "
            "Vienna and Attikan packs."
        ),
    )


def build_blue_tokai_exact_data() -> list[ExactData]:
    return [
        ExactData(
            id="ED-01",
            field=ExactField.PRODUCT_NAME,
            value="Easy Pour | Light to Dark Roasts — Mixed Bag",
            status=DataStatus.OBSERVED,
            source_id="SRC-02",
            evidence_locator="Product title",
            notes="Brand product name; Gate 1 must approve the identifier.",
        ),
        ExactData(
            id="ED-02",
            field=ExactField.PRICE,
            value="Pack of 5: Rs 300; Pack of 10: Rs 500",
            status=DataStatus.OBSERVED,
            source_id="SRC-02",
            evidence_locator="Variant selector and price block",
            notes="Variant-dependent. Not approved for advertising.",
        ),
        ExactData(
            id="ED-03",
            field=ExactField.PACK_SIZE,
            value="Pack of 5 sachets / Pack of 10 sachets",
            status=DataStatus.OBSERVED,
            source_id="SRC-02",
            evidence_locator="Size selector",
            notes="Hero pack size has not been chosen.",
        ),
        ExactData(
            id="ED-04",
            field=ExactField.CTA,
            value="Shop Easy Pour",
            status=DataStatus.PROPOSED,
            notes="Brief-supplied CTA. Gate 1 must approve the exact wording.",
        ),
        ExactData(
            id="ED-05",
            field=ExactField.BRAND_NAME,
            value="Blue Tokai Coffee Roasters",
            status=DataStatus.OBSERVED,
            source_id="SRC-01",
            evidence_locator="Header logo and footer",
            notes="Brand identifier observed on the storefront.",
        ),
    ]


def build_blue_tokai_claims() -> list[Claim]:
    return [
        Claim(
            id="CL-01",
            text="Specialty coffee",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-02"],
            evidence_locator="Product and collection copy",
            approved_wording="specialty coffee",
            limitations="Category descriptor; not a superiority claim.",
            used_in=["CP-01"],
        ),
        Claim(
            id="CL-02",
            text="No equipment; just a mug and hot water",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-05"],
            evidence_locator="Brewing instructions and FAQ",
            approved_wording="just a mug and hot water",
            limitations="Refers to the Easy Pour sachet brewing method, not all coffee.",
            used_in=["CP-02"],
        ),
        Claim(
            id="CL-03",
            text="The Mixed Bag spans light to dark roasts",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-02"],
            evidence_locator="Product description",
            approved_wording="light to dark",
            limitations="Describes the assortment, not every pack having equal quantities.",
            used_in=["CP-04"],
        ),
        Claim(
            id="CL-04",
            text="Vienna is a dark roast",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-03"],
            evidence_locator="Product title and roast panel",
            approved_wording="Vienna",
            limitations="Product name only; bitterness language is not used.",
            used_in=["CP-10"],
        ),
        Claim(
            id="CL-05",
            text="The filter is built into the sachet",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-05"],
            evidence_locator="Brewing instructions",
            approved_wording="filter is built into the sachet",
            limitations="Describes the sachet construction; not a durability claim.",
            used_in=["CP-07"],
        ),
        Claim(
            id="CL-06",
            text="Attikan Estate is a medium-dark roast",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-04"],
            evidence_locator="Product title and roast panel",
            approved_wording="Attikan",
            limitations="Product name only; tasting notes are not used.",
            used_in=["CP-10"],
        ),
        Claim(
            id="CL-07",
            text="Seethargundu Estate is a light roast",
            status=ClaimStatus.VERIFIED,
            source_ids=["SRC-02"],
            evidence_locator="Mixed Bag product description: Seethargundu light roast",
            approved_wording="Seethargundu",
            limitations="Product name only; the full roast guide is not quoted.",
            used_in=["CP-10"],
        ),
    ]
