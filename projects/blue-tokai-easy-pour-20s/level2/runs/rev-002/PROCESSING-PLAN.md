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
- Cost: $0.10

### AS-02 — Easy Pour Mixed Bag pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/MixedBag__Front_c9b610f1-ce4
- Processing: alpha_cutout → grade → scale → encode
- Cost: $0.10

### AS-03 — Easy Pour Vienna pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/ViennaRoast__Front_1_a175fab
- Processing: alpha_cutout → grade → scale → encode
- Cost: $0.10

### AS-04 — Easy Pour Attikan Estate pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/AttikanEstate__Front.jpg?v=1
- Processing: alpha_cutout → grade → scale → encode
- Cost: $0.10

### AS-05 — Easy Pour brewing demonstration, hands

- Source: pixabay: coffee, barista, pouring, milk, heart, cappuccino, espresso, cafe, drink, beverage, close up, morning, breakfast, delicious, foam, cup, mug, hands, skill, preparation, warm, creamy, coffee shop, latte art
- Processing: trim → stabilise → conform → grade → scale → encode
- Cost: $0.16

### AS-06 — Hot water pour and bloom footage

- Source: pixabay: coffee, hot drink, coffee pot, enjoyment, drink, coffee enjoyment, caffeine, motivation, coffee break, espresso, machine, coffee machine
- Processing: trim → stabilise → conform → grade → scale → encode
- Cost: $0.16

### AS-07 — Warm kitchen background

- Source: pexels: Pexels photo 33256980
- Processing: grade → scale → encode
- Cost: $0.06

### AS-08 — Finished cup of coffee

- Source: openverse: Cup of Coffee on Table Rock in Linville Gorge
- Processing: grade → scale → encode
- Cost: $0.06

### AS-09 — Voice over, warm Indian English

- Source: supplied:Voice artist session
- Processing: tts → trim → loudness_norm → resample → encode
- Cost: $0.16

### AS-10 — Music bed, 20 seconds

- Source: ccmixter: Lost Roamin'
- Processing: trim → fade → loudness_norm → resample → encode
- Cost: $0.10

### AS-11 — Water pour sound effect

- Source: wikimedia: File:Pouring water bottles.ogg
- Processing: trim → denoise → loudness_norm → resample → encode
- Cost: $0.12

### AS-12 — Brand sting

- Source: owned:In-house sound design
- Processing: synth → loudness_norm → resample → encode
- Cost: $0.12

### AS-13 — Captured Mixed Bag fallback

- Source: capture:In-house studio capture
- Processing: alpha_cutout → grade → scale → encode
- Cost: $0.10

### AS-14 — Music fallback track

- Source: openverse: Road In The Forest
- Processing: trim → fade → loudness_norm → resample → encode
- Cost: $0.10

### AS-15 — Synthetic narration fallback

- Source: generate:Approved speech provider
- Processing: tts → trim → loudness_norm → resample → encode
- Cost: $0.16

### AS-17 — Easy Pour Seethargundu Estate pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/Seethargundu-Estate__Front_1
- Processing: alpha_cutout → grade → scale → encode
- Cost: $0.10

## Budget rule

- Stock licensing is free or in-kind for CC0/CC-BY/Pexels/Pixabay/Unsplash.
- AI generation is capped at 40% of assets and is disclosed.
- Processing is priced per operation and kept within the $2 trial cap.
