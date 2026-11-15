# Processing plan — shot x layer x asset

Each asset's required processing, its cost, and the trial budget. The
trial run is capped at $2.00.

| Total processing | Budget | Within budget |
|---|---|---|
| $1.80 | $2.00 | yes |

| Asset | What | Route | Kind | Shots | Layers | Processing | Cost |
|---|---|---|---|---|---|---|---|
| `AS-01` | Blue Tokai Coffee Roasters logo | supplied | image | SH-06 | 1 | alpha_cutout → grade → scale → encode | $0.10 |
| `AS-02` | Easy Pour Mixed Bag pack | supplied | image | SH-01, SH-02, SH-03, SH-04, SH-05, SH-06 | 6 | alpha_cutout → grade → scale → encode | $0.10 |
| `AS-03` | Easy Pour Vienna pack | supplied | image | SH-04 | 1 | alpha_cutout → grade → scale → encode | $0.10 |
| `AS-04` | Easy Pour Attikan Estate pack | supplied | image | SH-04 | 1 | alpha_cutout → grade → scale → encode | $0.10 |
| `AS-05` | Easy Pour brewing demonstration, hands | stock | video | SH-02 | 1 | trim → stabilise → conform → grade → scale → encode | $0.16 |
| `AS-06` | Hot water pour and bloom footage | stock | video | SH-03 | 1 | trim → stabilise → conform → grade → scale → encode | $0.16 |
| `AS-07` | Warm kitchen background | stock | image | SH-01, SH-02, SH-03, SH-04, SH-05, SH-06 | 6 | grade → scale → encode | $0.06 |
| `AS-08` | Finished cup of coffee | stock | image | SH-05 | 1 | grade → scale → encode | $0.06 |
| `AS-09` | Voice over, warm Indian English | generate | voice | — | 0 | tts → trim → loudness_norm → resample → encode | $0.16 |
| `AS-10` | Music bed, 20 seconds | stock | music | — | 0 | trim → fade → loudness_norm → resample → encode | $0.10 |
| `AS-11` | Water pour sound effect | stock | sound | — | 0 | trim → denoise → loudness_norm → resample → encode | $0.12 |
| `AS-12` | Brand sting | generate | sound | — | 0 | synth → loudness_norm → resample → encode | $0.12 |
| `AS-13` | Captured Mixed Bag fallback | supplied | image | — | 0 | alpha_cutout → grade → scale → encode | $0.10 |
| `AS-14` | Music fallback track | stock | music | — | 0 | trim → fade → loudness_norm → resample → encode | $0.10 |
| `AS-15` | Synthetic narration fallback | generate | voice | — | 0 | tts → trim → loudness_norm → resample → encode | $0.16 |
| `AS-17` | Easy Pour Seethargundu Estate pack | supplied | image | SH-04 | 1 | alpha_cutout → grade → scale → encode | $0.10 |

## Processing detail

### AS-01 — Blue Tokai Coffee Roasters logo

- Source: supplied:User-supplied logo attachment, 2026-11-14; public footer fallback: http
- Processing: alpha_cutout → grade → scale → encode
- AI: AI background removal to alpha + edge cleanup; upscale only from a real master, never a thumbnail
- AI generation: no (edit only)
- Cost: $0.10

### AS-02 — Easy Pour Mixed Bag pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/MixedBag__Front_c9b610f1-ce4
- Processing: alpha_cutout → grade → scale → encode
- AI: AI label-preserving background cutout; color/light normalize to the counter plates
- AI generation: no (edit only)
- Cost: $0.10

### AS-03 — Easy Pour Vienna pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/ViennaRoast__Front_1_a175fab
- Processing: alpha_cutout → grade → scale → encode
- AI: AI label-preserving background cutout; color/light normalize
- AI generation: no (edit only)
- Cost: $0.10

### AS-04 — Easy Pour Attikan Estate pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/AttikanEstate__Front.jpg?v=1
- Processing: alpha_cutout → grade → scale → encode
- AI: AI label-preserving background cutout; color/light normalize
- AI generation: no (edit only)
- Cost: $0.10

### AS-05 — Easy Pour brewing demonstration, hands

- Source: pixabay: coffee, barista, pouring, milk, heart, cappuccino, espresso, cafe, drink, beverage, close up, morning, breakfast, delicious, foam, cup, mug, hands, skill, preparation, warm, creamy, coffee shop, latte art
- Processing: trim → stabilise → conform → grade → scale → encode
- AI: AI stabilise + denoise; AI frame interpolation for the 50->25 conform; AI relight; inpaint stray objects
- AI generation: no (edit only)
- Cost: $0.16

### AS-06 — Hot water pour and bloom footage

- Source: pixabay: coffee, hot drink, coffee pot, enjoyment, drink, coffee enjoyment, caffeine, motivation, coffee break, espresso, machine, coffee machine
- Processing: trim → stabilise → conform → grade → scale → encode
- AI: AI stabilise + denoise; AI speed-ramp retime; AI relight; inpaint stray objects
- AI generation: no (edit only)
- Cost: $0.16

### AS-07 — Warm kitchen background

- Source: pexels: Pexels photo 33256980
- Processing: grade → scale → encode
- AI: AI relight to the warm counter; AI inpaint distractions; crop to 1080p
- AI generation: no (edit only)
- Cost: $0.06

### AS-08 — Finished cup of coffee

- Source: openverse: Cup of Coffee on Table Rock in Linville Gorge
- Processing: grade → scale → encode
- AI: AI relight to the counter; AI background clean + cup-edge inpaint
- AI generation: no (edit only)
- Cost: $0.06

### AS-09 — Voice over, warm Indian English

- Source: supplied:Voice artist session
- Processing: tts → trim → loudness_norm → resample → encode
- AI: AI generation: TTS voice (counts against the 40% allowance); AI denoise + loudness norm
- AI generation: yes
- Cost: $0.16

### AS-10 — Music bed, 20 seconds

- Source: ccmixter: Lost Roamin'
- Processing: trim → fade → loudness_norm → resample → encode
- AI: AI loudness norm to -16 LUFS; AI loop tail; trim + fade
- AI generation: no (edit only)
- Cost: $0.10

### AS-11 — Water pour sound effect

- Source: wikimedia: File:Pouring water bottles.ogg
- Processing: trim → denoise → loudness_norm → resample → encode
- AI: AI denoise; trim to the pour; level-match to the mix
- AI generation: no (edit only)
- Cost: $0.12

### AS-12 — Brand sting

- Source: owned:In-house sound design
- Processing: synth → loudness_norm → resample → encode
- AI: AI generation: synthetic brand sting; loudness norm
- AI generation: yes
- Cost: $0.12

### AS-13 — Captured Mixed Bag fallback

- Source: capture:In-house studio capture
- Processing: alpha_cutout → grade → scale → encode
- AI: AI label-preserving cutout across the four angles
- AI generation: no (edit only)
- Cost: $0.10

### AS-14 — Music fallback track

- Source: openverse: Road In The Forest
- Processing: trim → fade → loudness_norm → resample → encode
- AI: AI loudness norm to -16 LUFS; loop tail
- AI generation: no (edit only)
- Cost: $0.10

### AS-15 — Synthetic narration fallback

- Source: generate:Approved speech provider
- Processing: tts → trim → loudness_norm → resample → encode
- AI: AI generation: TTS fallback; loudness norm
- AI generation: yes
- Cost: $0.16

### AS-17 — Easy Pour Seethargundu Estate pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/Seethargundu-Estate__Front_1
- Processing: alpha_cutout → grade → scale → encode
- AI: AI label-preserving background cutout; color/light normalize
- AI generation: no (edit only)
- Cost: $0.10

## AI processing vs AI generation

AI **processing** is a minor edit/enhancement applied to an existing
asset (relight, inpaint, denoise, retime, label cutout, loudness norm).
It does not count against the 40% cap. AI **generation** creates new
media and is limited to voice, sting and the narration fallback.

| Asset | AI processing / generation | Generation? |
|---|---|---|
| `AS-01` | AI background removal to alpha + edge cleanup; upscale only from a real master, never a thumbnail | no |
| `AS-02` | AI label-preserving background cutout; color/light normalize to the counter plates | no |
| `AS-03` | AI label-preserving background cutout; color/light normalize | no |
| `AS-04` | AI label-preserving background cutout; color/light normalize | no |
| `AS-05` | AI stabilise + denoise; AI frame interpolation for the 50->25 conform; AI relight; inpaint stray objects | no |
| `AS-06` | AI stabilise + denoise; AI speed-ramp retime; AI relight; inpaint stray objects | no |
| `AS-07` | AI relight to the warm counter; AI inpaint distractions; crop to 1080p | no |
| `AS-08` | AI relight to the counter; AI background clean + cup-edge inpaint | no |
| `AS-09` | AI generation: TTS voice (counts against the 40% allowance); AI denoise + loudness norm | yes |
| `AS-10` | AI loudness norm to -16 LUFS; AI loop tail; trim + fade | no |
| `AS-11` | AI denoise; trim to the pour; level-match to the mix | no |
| `AS-12` | AI generation: synthetic brand sting; loudness norm | yes |
| `AS-13` | AI label-preserving cutout across the four angles | no |
| `AS-14` | AI loudness norm to -16 LUFS; loop tail | no |
| `AS-15` | AI generation: TTS fallback; loudness norm | yes |
| `AS-17` | AI label-preserving background cutout; color/light normalize | no |

## Budget rule

- Stock licensing is free or in-kind for CC0/CC-BY/Pexels/Pixabay/Unsplash.
- AI generation is capped at 40% of assets and is disclosed.
- Processing is priced per operation and kept within the $2 trial cap.
