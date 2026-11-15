"""Voice-over casting and delivery direction for Level 2.

The VO is a continuous read, not line-by-line announcements. The plan records
the voice profile, language/accent, pitch, resonance, pace, energy, emphasis,
pauses and pronunciation so the voice agent has a real brief.
"""

from __future__ import annotations

from pydantic import Field

from ..models import ProductionPlan, StrictModel, utc_now
from .models import Level2Plan

PROFILES = [
    (
        "deep-bass",
        "Low pitch, full-bodied resonance, slow steady delivery",
        "premium coffee, luxury, cinematic reveal",
    ),
    (
        "warm-conversational",
        "Middle register, soft edges, relaxed pace, slight smile",
        "D2C, caf?s, founder-led ads",
    ),
    (
        "clear-authoritative",
        "Low-to-middle register, crisp consonants, measured emphasis",
        "B2B, tech, evidence-led",
    ),
    (
        "bright-upbeat",
        "Brighter resonance, quicker pace, lively pitch changes",
        "food launches, lifestyle, social",
    ),
    (
        "bold-punchy",
        "Firm attacks, short phrases, decisive endings",
        "offers, launches, performance",
    ),
    (
        "soft-intimate",
        "Warm close delivery, gentle volume, clear consonants",
        "fragrance, wellness, personal",
    ),
    (
        "textured-earthy",
        "Slight grain, relaxed rhythm, grounded emphasis",
        "craft, coffee roasting, origin",
    ),
    (
        "playful-expressive",
        "Elastic pacing, quick pitch shifts, comedic pause",
        "comedy, character-led",
    ),
]


class VoiceTake(StrictModel):
    take_id: str = Field(min_length=1, max_length=40)
    label: str
    voice_profile: str
    language_accent: str
    pitch: str
    resonance: str
    pace: str
    energy: str
    emphasis: str
    pauses: str
    pronunciation: str
    delivery_arc: str
    edge_voice: str
    rate: str
    model: str = "shortgpt:edge-tts"


class VoiceDirection(StrictModel):
    asset_id: str = "AS-09"
    script: str
    mode: str = "continuous narration"
    takes: list[VoiceTake] = Field(min_length=1)
    disclosure: str = "Synthetic voice generated with Edge TTS"
    created_at: str = Field(default_factory=utc_now)


def build_voice_direction(plan: ProductionPlan, level2: Level2Plan) -> VoiceDirection:
    script = (
        "Specialty coffee. Tear, anchor, pour. Just a mug and hot water. "
        "Light to dark. One mug. One cup. Shop Easy Pour."
    )
    cue = next((cue for cue in level2.sound.cues if cue.asset_id == "AS-09"), None)
    if cue is not None and "Canonical read:" in cue.description:
        script = cue.description.split("Canonical read:", 1)[1].strip()
    return VoiceDirection(
        script=script,
        takes=[
            VoiceTake(
                take_id="VO-M1",
                label="Male — warm, lightly textured",
                voice_profile="warm-conversational / textured-earthy",
                language_accent="Indian English, neutral urban",
                pitch="low-to-middle",
                resonance="full, lightly textured",
                pace="measured, continuous, no line gaps",
                energy="low-medium, lifting slightly at the CTA",
                emphasis="‘Specialty’, ‘Light to dark’, ‘Shop Easy Pour’",
                pauses="short breath before the brand name; no pause between other lines",
                pronunciation="clear ‘Tear, anchor, pour’; brand name unhurried",
                delivery_arc="open conversational → benefit measured → CTA slower and more direct",
                edge_voice="en-IN-PrabhatNeural",
                rate="-25%",
            ),
            VoiceTake(
                take_id="VO-F1",
                label="Female — lower-middle alto, warm",
                voice_profile="warm-conversational / soft-intimate",
                language_accent="Indian English, neutral urban",
                pitch="lower-middle",
                resonance="warm and full-bodied",
                pace="relaxed, continuous, no line gaps",
                energy="low-medium, inviting at the CTA",
                emphasis="‘Specialty’, ‘one mug’, ‘Shop Easy Pour’",
                pauses="short pause before the product reveal; no line-by-line gaps",
                pronunciation="clear consonants; keep English brand words natural in Hinglish",
                delivery_arc="warm open → intimate reveal → clear inviting CTA",
                edge_voice="en-IN-NeerjaNeural",
                rate="-22%",
            ),
        ],
    )


def render_voice_direction(direction: VoiceDirection) -> str:
    lines = [
        "# Voice-over direction — AS-09",
        "",
        f"**Mode:** {direction.mode}",
        f"**Script:** {direction.script}",
        f"**Disclosure:** {direction.disclosure}",
        "",
        "## Casting profiles",
        "",
        "| Profile | Direction | Good fit |",
        "|---|---|---|",
    ]
    for name, direction_text, fit in PROFILES:
        lines.append(f"| {name} | {direction_text} | {fit} |")
    lines.extend(["", "## Takes", ""])
    for take in direction.takes:
        lines.extend(
            [
                f"### {take.take_id} — {take.label}",
                "",
                f"- Profile: {take.voice_profile}",
                f"- Language / accent: {take.language_accent}",
                f"- Pitch: {take.pitch}; resonance: {take.resonance}",
                f"- Pace: {take.pace}",
                f"- Energy: {take.energy}",
                f"- Emphasis: {take.emphasis}",
                f"- Pauses: {take.pauses}",
                f"- Pronunciation: {take.pronunciation}",
                f"- Delivery arc: {take.delivery_arc}",
                f"- Edge voice: `{take.edge_voice}` at rate `{take.rate}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Notes",
            "",
            "- Continuous narration: no gaps between lines; only a short breath "
            "before the brand name.",
            "- Deep (pitch) and bass-rich (low-frequency weight) are separate; "
            "bass is a mix EQ decision.",
            "- Audition both takes with the same script, music and edit; check the "
            "brand name and CTA on a phone speaker.",
            "- Indic Parler-TTS / Kokoro-82M / Qwen3-TTS / Chatterbox are not "
            "installed here; Edge TTS is the working fallback.",
            "",
        ]
    )
    return "\n".join(lines)
