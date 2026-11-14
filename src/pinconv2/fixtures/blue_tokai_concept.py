"""Concept Note fixture for the Blue Tokai Easy Pour 20-second ad."""

from __future__ import annotations

from ..models import (
    ConceptNote,
    ConceptOption,
    ConceptScores,
    Decision,
    HookOption,
)
from .blue_tokai_research import PROJECT_ID


def blue_tokai_decisions() -> list[Decision]:
    return [
        Decision(
            id="DC-01",
            finding_ids=["F-03", "F-12"],
            selected="Lead with 'Specialty coffee', not 'instant coffee'.",
            alternatives=[
                "Call it instant coffee in a convenience comparison",
                "Lead with the roast origin story",
                "Lead with the price",
            ],
            rationale=(
                "Blue Tokai explicitly separates Easy Pour from instant coffee. The "
                "category word and a visible pack avoid a false comparison."
            ),
            impacted_ids=["CP-01", "CP-02", "SH-01"],
        ),
        Decision(
            id="DC-02",
            finding_ids=["F-02", "F-08"],
            selected=(
                "Demonstrate tear, anchor and first pour; compress the repeated pours and "
                "steep with a disclosure."
            ),
            alternatives=[
                "Show the whole brew as a 20-second real-time take",
                "Skip the demo and use pack beauty shots",
                "Use a stylised split-screen diagram",
            ],
            rationale=(
                "The built-in filter is the product benefit. A real action proves it, "
                "and a labelled time-lapse keeps the 20-second format honest."
            ),
            impacted_ids=["SH-02", "SH-03", "SH-05", "CP-12"],
        ),
        Decision(
            id="DC-03",
            finding_ids=["F-01", "F-11"],
            selected=(
                "Hero the Mixed Bag and show Seethargundu, Attikan and Vienna as range support."
            ),
            alternatives=[
                "Hero only the Mixed Bag",
                "Hero Vienna as the darkest roast",
                "Show all five single-estate packs",
            ],
            rationale=(
                "The Mixed Bag is the first-time buyer's variety route. Four packs "
                "communicate light to dark with a real light endpoint and a dark endpoint, "
                "without turning the frame into a catalogue."
            ),
            impacted_ids=["SH-04", "AS-02", "AS-03", "AS-04"],
        ),
        Decision(
            id="DC-04",
            finding_ids=["F-04"],
            selected="Keep price and pack size out of the ready cut.",
            alternatives=[
                "End on 'Pack of 5 at Rs 300'",
                "Use the price as the hook",
                "Hold the price for a later approved version",
            ],
            rationale=(
                "The values are observed but not approved, and the hero pack size is "
                "still unresolved. Price would turn observation into an ad claim."
            ),
            impacted_ids=["ED-02", "ED-03", "CP-06"],
        ),
        Decision(
            id="DC-05",
            finding_ids=["F-06", "F-07"],
            selected="Build a 16:9 500-frame YouTube master with early branding.",
            alternatives=[
                "9:16 Shorts-first master",
                "1:1 feed master",
                "15-second cut",
            ],
            rationale=(
                "The brief asks for a 20-second YouTube ad. A 16:9 master fits "
                "in-stream, while the pack and brand appear from the first shot."
            ),
            impacted_ids=["DP-01", "SH-01", "SH-06"],
        ),
        Decision(
            id="DC-06",
            finding_ids=["F-05", "F-10"],
            selected="Use the public image URLs as observed sources and hold rights.",
            alternatives=[
                "Treat public images as cleared",
                "Recreate the packs in 3D",
                "Use unlabelled stand-in packs",
            ],
            rationale=(
                "The supplied links identify the exact product, but public access does "
                "not grant paid-media use. Stand-ins would break exactness."
            ),
            impacted_ids=["AS-01", "AS-02", "AS-03", "AS-04"],
        ),
    ]


def build_blue_tokai_concept() -> ConceptNote:
    options = [
        ConceptOption(
            id="CO-01",
            name="No machine. Just a mug.",
            one_liner=(
                "A real Easy Pour sachet becomes a cup of specialty coffee in one "
                "continuous, tactile demonstration."
            ),
            hook="Specialty coffee. Just a mug and hot water.",
            treatment=(
                "Open tight on a Blue Tokai Mixed Bag pack on a kitchen counter, with "
                "a mug already in frame. The hook lands as the sachet is lifted. Cut to "
                "hands tearing the outer sachet and the built-in filter, anchoring it "
                "over the mug. Water hits the grounds in macro; the bed blooms. A "
                "labelled time-lapse carries the repeated pours and steep. The film opens "
                "out to the Mixed "
                "Bag, Seethargundu, Attikan and Vienna packs, then lands on the finished "
                "cup and the end card: logo, Mixed Bag and Shop Easy Pour."
            ),
            visual_style=(
                "Warm daylight kitchen, honest hands, macro water and coffee texture, "
                "clean cream end card. Blue Tokai blue and pack colours carry the frame. "
                "No lab equipment, no espresso machine, no fake UI."
            ),
            sound=(
                "Dry kitchen ambience, a soft pack crinkle, a clear water pour, a low "
                "music bed that lifts at the range reveal, and a quiet brand sting. "
                "Sparse VO: Specialty coffee. Just a mug and hot water. Shop Easy Pour."
            ),
            scores=ConceptScores(
                audience_fit=5,
                clarity=5,
                distinctiveness=4,
                achievable_quality=5,
                cost_efficiency=4,
                revision_simplicity=4,
            ),
            rationale=(
                "The product benefit is physical, so the strongest ad is the action "
                "itself. One continuous demo proves the built-in filter without a "
                "category lecture, and the range reveal gives the first-time buyer a "
                "reason to choose the Mixed Bag."
            ),
            risks=[
                "Hands and brew footage need a performer release and a controlled food set.",
                "Public pack images are not yet cleared for paid media.",
                "The repeated pours and two-minute steep must be compressed and disclosed.",
            ],
            linked_finding_ids=["F-02", "F-03", "F-09", "F-12"],
        ),
        ConceptOption(
            id="CO-02",
            name="Light to dark",
            one_liner=(
                "Three roast chapters move from bright morning light to deep evening "
                "colour, ending on the Mixed Bag."
            ),
            hook="One bag. Light to dark.",
            treatment=(
                "A colour-graded triptych: Seethargundu in cool morning light, Attikan "
                "in warm afternoon, Vienna in low evening light. Each chapter shows a "
                "finished cup and a pack, then resolves into the Mixed Bag. The CTA "
                "closes on the range."
            ),
            visual_style=(
                "Editorial coffee-table photography, strong colour chapters, slow "
                "lateral moves, minimal type."
            ),
            sound=("Three musical textures that resolve into one bed; no VO until the close."),
            scores=ConceptScores(
                audience_fit=4,
                clarity=3,
                distinctiveness=4,
                achievable_quality=4,
                cost_efficiency=3,
                revision_simplicity=3,
            ),
            rationale=(
                "It makes the range tangible and premium, but it spends the 20 seconds "
                "on roast character rather than the built-in-filter benefit the brief "
                "asks to demonstrate."
            ),
            risks=[
                "Needs more product and cup setups.",
                "The demo benefit becomes secondary.",
                "Harder to prove 'no equipment' visually.",
            ],
            linked_finding_ids=["F-01", "F-11"],
        ),
        ConceptOption(
            id="CO-03",
            name="The 3pm desk brew",
            one_liner=(
                "A busy professional swaps a sad instant coffee for an Easy Pour at their desk."
            ),
            hook="3pm. Still no machine.",
            treatment=(
                "A character at a desk hits the afternoon slump, opens the Mixed Bag, "
                "anchors the filter to a mug and pours. The finished cup lands next to "
                "the laptop; the end card closes on the pack and CTA."
            ),
            visual_style=(
                "Bright observational comedy, office detail, handheld energy, bold captions."
            ),
            sound=("Playful percussion, comic reaction, a clean brand sting."),
            scores=ConceptScores(
                audience_fit=4,
                clarity=4,
                distinctiveness=4,
                achievable_quality=3,
                cost_efficiency=3,
                revision_simplicity=2,
            ),
            rationale=(
                "It makes the audience concrete, but adds casting, performance and a "
                "set. It also risks making the coffee look like an office shortcut "
                "rather than a specialty product."
            ),
            risks=[
                "Casting and performance add cost and revision risk.",
                "The product benefit competes with the joke.",
                "The premium specialty cue can get lost.",
            ],
            linked_finding_ids=["F-09"],
        ),
    ]

    hooks = [
        HookOption(
            id="HK-01",
            text="Specialty coffee. Just a mug and hot water.",
            rationale=(
                "States the category and the benefit in one line, matches the brief's "
                "core message, and sets up the demo."
            ),
            risk="'Just' can sound too casual for a premium product.",
        ),
        HookOption(
            id="HK-02",
            text="No machine. No barista. Just coffee.",
            rationale=(
                "Names the barriers the audience cares about and creates a clean before/after."
            ),
            risk="'No barista' may imply cafe coffee is the enemy.",
        ),
        HookOption(
            id="HK-03",
            text="One sachet. One cup. Light to dark.",
            rationale=(
                "Combines convenience and range, and gives the edit a natural three-part structure."
            ),
            risk="Leads with format rather than the specialty-coffee promise.",
        ),
    ]

    return ConceptNote(
        project_id=PROJECT_ID,
        revision=1,
        brief_revision=1,
        audience_summary=(
            "Busy Indian coffee drinkers who want specialty coffee at home or work "
            "without buying equipment. They already buy cafe coffee or instant coffee "
            "and are curious about easy pour-over. This is the brief's audience, not a "
            "measured study."
        ),
        objective=(
            "Make the built-in-filter benefit visible and drive a first Easy Pour "
            "purchase, with the Mixed Bag as the entry product."
        ),
        evidence_summary=(
            "Blue Tokai's product pages establish the Mixed Bag assortment and the "
            "named Vienna and Attikan packs, with Seethargundu added from the Mixed Bag "
            "page to complete the light end of the range. The brewing page establishes "
            "the real "
            "tear-anchor-pour method and the two-minute steep. Google's creative "
            "guidance supports early attention, early branding and a clear CTA. Price, "
            "pack size and public image rights remain unapproved."
        ),
        options=options,
        recommended_option_id="CO-01",
        hooks=hooks,
        why_hook=(
            "HK-01 says the category and the benefit in one line. It works as spoken and "
            "on-screen copy and does not depend on price, promotion or an unverified "
            "claim."
        ),
        why_script=(
            "The script follows the physical demo: name the category, state the benefit, "
            "show the three actions, reveal the range, ask for the purchase. It avoids "
            "calling the product instant coffee."
        ),
        why_look=(
            "A warm kitchen and macro water make the product action legible. The pack "
            "labels stay unobstructed, and the range shot uses the actual Mixed Bag, "
            "Seethargundu, Attikan and Vienna packs rather than invented variants."
        ),
        why_sound=(
            "The pour and pack crinkle carry the demo; the music lifts only at the range "
            "reveal and the brand sting closes the film. Captions carry the message with "
            "sound off."
        ),
        decisions=blue_tokai_decisions(),
        open_questions=[
            "Hero pack size: brand decision; blocks pack layout, price and end-card copy.",
            "CTA destination: brand decision; blocks tracking and publishing, not the wording.",
            "Cleared pack/logo masters: brand rights owner; blocks all pack and logo renders.",
            "9:16 Shorts variant: media owner; blocks a separate vertical deliverable.",
            "Human or synthetic narration: brand producer; blocks voice casting and disclosure.",
            "Brand typeface: brand design owner; blocks final typography and HI-05 clearance.",
        ],
        planned_look=(
            "Warm daylight kitchen, deep blue and cream brand accents, macro water and "
            "coffee texture, clean pack photography, a cream end card with the Blue "
            "Tokai logo, Mixed Bag pack and CTA."
        ),
        success_definition=(
            "A viewer can repeat the product benefit after one sound-off view: specialty "
            "coffee, a built-in filter, just a mug and hot water. The end card names Easy "
            "Pour and the Mixed Bag. Performance targets are not invented at Level 1."
        ),
        viewing_context=(
            "YouTube 16:9, likely watched on a phone in a feed or in-stream; assume sound "
            "off for the first view and a skippable opening. A 9:16 cut is a separate "
            "placement decision."
        ),
        reference_notes=(
            "No competitor video was used as a creative template. The treatment borrows "
            "the public principle of a tactile product demonstration and YouTube's ABCD "
            "guidance; it does not reuse any third-party footage or audio."
        ),
        reverse_evidence=(
            "Reverse the demo-led route if a controlled test shows the brew action reads "
            "as too slow, if the built-in filter cannot be shown clearly at phone scale, "
            "or if brand approval requires a pack-only end card."
        ),
        prohibited_content=(
            "No 'instant coffee' label, no invented equipment, no price or promotion, no "
            "unapproved health or superiority claim, no third-party footage, no fake UI."
        ),
        canonical_script=(
            "Specialty coffee. Just a mug and hot water. Tear, anchor, pour. Light to "
            "dark. One mug. One cup. Shop Easy Pour."
        ),
    )
