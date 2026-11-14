# Production build sheet — blue-tokai-easy-pour-20s

Run `rev-002` · plan revision 2 · schema 2.0

Source plan hash: `1370f029b0b35730625c459cf85579bfd767d2e4a7b62016055e100d15f2aba5`

## Summary

| Item | Value |
|---|---|
| Assets | 16 |
| Layers | 38 |
| Shots | 6 |
| Effects | 6 |
| Variants | 1 |
| Estimate | $0.00 |
| Worst case | $0.00 |
| Cap | $2.00 |
| Headroom | $2.00 |

## Assets

| Asset | Class | Impact | Method | Status | Rights | Hold |
|---|---|---|---|---|---|---|
| `AS-01` Blue Tokai Coffee Roasters logo | exact | high | M0 | blocked | needs_approval | HI-02 |
| `AS-02` Easy Pour Mixed Bag pack | exact | high | M0 | blocked | needs_approval | HI-02 |
| `AS-03` Easy Pour Vienna pack | exact | high | M0 | blocked | needs_approval | HI-02 |
| `AS-04` Easy Pour Attikan Estate pack | exact | high | M0 | blocked | needs_approval | HI-02 |
| `AS-17` Easy Pour Seethargundu Estate pack | exact | high | M0 | blocked | needs_approval | HI-02 |
| `AS-05` Easy Pour brewing demonstration, hands | proof | high | M6 | blocked | needs_approval | HI-04 |
| `AS-06` Hot water pour and bloom footage | proof | high | M6 | blocked | needs_approval | HI-04 |
| `AS-07` Warm kitchen background | atmospheric | medium | M0 | planned | cleared | — |
| `AS-08` Finished cup of coffee | proof | high | M6 | blocked | needs_approval | HI-04 |
| `AS-09` Voice over, warm Indian English | representative | low | M0 | blocked | needs_approval | HI-03 |
| `AS-10` Music bed, 20 seconds | atmospheric | low | M1 | blocked | needs_approval | HI-03 |
| `AS-11` Water pour sound effect | atmospheric | low | M0 | planned | cleared | — |
| `AS-12` Brand sting | atmospheric | low | M0 | planned | cleared | — |
| `AS-13` Captured Mixed Bag fallback | exact | low | M6 | conditional | needs_approval | HI-02 |
| `AS-14` Music fallback track | atmospheric | low | M1 | conditional | needs_approval | HI-03 |
| `AS-15` Synthetic narration fallback | representative | low | M7 | conditional | needs_approval | HI-03 |

### Asset detail

#### AS-01 · Blue Tokai Coffee Roasters logo

- Source: supplied:User-supplied logo attachment, 2026-11-14; public footer fallback: https://bluetokaicoffee.com/cdn/shop/files/logo-footer.png?v=1688108473
- Processing: alpha_cutout, grade, encode
- Bindings: LY-062
- Acceptance: Logo edges clean at end-card size; proportions and colour match the supplied master.
- Status: `blocked`
- Blockers: HI-02

#### AS-02 · Easy Pour Mixed Bag pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/MixedBag__Front_c9b610f1-ce4a-4b53-8b30-f6ca758eb6bb.jpg?v=1717566490
- Processing: alpha_cutout, grade, encode
- Bindings: LY-011, LY-022, LY-032, LY-041, LY-052, LY-061
- Acceptance: Front title, ‘Light to Dark Roasts’ and Blue Tokai mark readable at phone scale; no label crop.
- Status: `blocked`
- Blockers: HI-02

#### AS-03 · Easy Pour Vienna pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/ViennaRoast__Front_1_a175faba-8e5f-40b8-aaa1-0efc3a525321.jpg?v=1717565466
- Processing: alpha_cutout, grade, encode
- Bindings: LY-042
- Acceptance: Vienna name and dark-roast descriptor readable; no label crop.
- Status: `blocked`
- Blockers: HI-02

#### AS-04 · Easy Pour Attikan Estate pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/AttikanEstate__Front.jpg?v=1764321548
- Processing: alpha_cutout, grade, encode
- Bindings: LY-043
- Acceptance: Attikan name and medium-dark descriptor readable; no label crop.
- Status: `blocked`
- Blockers: HI-02

#### AS-17 · Easy Pour Seethargundu Estate pack

- Source: supplied:https://bluetokaicoffee.com/cdn/shop/files/Seethargundu-Estate__Front_1.jpg?v=1764321548
- Processing: alpha_cutout, grade, encode
- Bindings: LY-047
- Acceptance: Seethargundu name and light-roast descriptor readable; no label crop.
- Status: `blocked`
- Blockers: HI-02

#### AS-05 · Easy Pour brewing demonstration, hands

- Source: capture:In-house food shoot
- Processing: trim, stabilise, conform, grade, scale, encode
- Bindings: LY-021
- Acceptance: Tear, open and anchor actions are physically correct and match the brand instructions.
- Status: `blocked`
- Blockers: HI-04

#### AS-06 · Hot water pour and bloom footage

- Source: capture:In-house food shoot
- Processing: trim, stabilise, conform, speed_ramp, grade, scale, encode
- Bindings: LY-031
- Acceptance: Water visibly contacts the coffee bed; bloom and drip read in macro; no spill or continuity break.
- Status: `blocked`
- Blockers: HI-04

#### AS-07 · Warm kitchen background

- Source: owned:In-house set build
- Processing: grade, encode
- Bindings: LY-010, LY-020, LY-030, LY-040, LY-050, LY-060
- Acceptance: Full-canvas background holds a consistent grade across all six shots.
- Status: `planned`
- Blockers: none

#### AS-08 · Finished cup of coffee

- Source: capture:In-house food shoot
- Processing: trim, stabilise, conform, grade, scale, encode
- Bindings: LY-051
- Acceptance: Finished cup matches the brewed colour; rim clean; steam visible without obscuring the pack.
- Status: `blocked`
- Blockers: HI-04

#### AS-09 · Voice over, warm Indian English

- Source: supplied:Voice artist session
- Processing: trim, denoise, loudness_norm, resample, encode
- Bindings: AU-01
- Acceptance: Performer release present; intelligible read; no claim beyond the canonical script.
- Status: `blocked`
- Blockers: HI-03

#### AS-10 · Music bed, 20 seconds

- Source: stock:ccmixter:Lost Roamin'
- Processing: trim, fade, loudness_norm, resample, encode
- Bindings: AU-02
- Acceptance: Licence covers paid YouTube; 20-second edit supports the 275 range lift and 445 resolve.
- Status: `blocked`
- Blockers: HI-03

#### AS-11 · Water pour sound effect

- Source: owned:In-house sound design
- Processing: trim, loudness_norm, encode
- Bindings: AU-03
- Acceptance: Pour sound syncs to the water action without a phasing artefact.
- Status: `planned`
- Blockers: none

#### AS-12 · Brand sting

- Source: owned:In-house sound design
- Processing: trim, loudness_norm, encode
- Bindings: AU-04
- Acceptance: Sting lands under the end card and does not mask the VO.
- Status: `planned`
- Blockers: none

#### AS-13 · Captured Mixed Bag fallback

- Source: capture:In-house studio capture
- Processing: alpha_cutout, grade, scale, encode
- Bindings: none
- Acceptance: Physical pack label is square to camera and at least as legible as the supplied image.
- Status: `conditional`
- Blockers: HI-02, conditional fallback

#### AS-14 · Music fallback track

- Source: stock:ccmixter:This Is Our Music - Instrumental
- Processing: trim, fade, loudness_norm, resample, encode
- Bindings: none
- Acceptance: Fallback bed matches the primary tempo and emotional resolve.
- Status: `conditional`
- Blockers: HI-03, conditional fallback

#### AS-15 · Synthetic narration fallback

- Source: generate:Approved speech provider
- Processing: channel_map, trim, denoise, loudness_norm, resample, encode
- Bindings: none
- Acceptance: Synthetic read matches the canonical script and carries the disclosure decision.
- Status: `conditional`
- Blockers: HI-03, conditional fallback

## Shots

### SH-01 · frames 0–75

- Method: Live-action counter plate with product cut-out and kinetic type.
- Layers: LY-010, LY-011, LY-012, LY-013, LY-014, LY-015
- Effects: FX-01
- Audio: AU-01, AU-02
- Ready: no
- Blockers: HI-02

### SH-02 · frames 75–160

- Method: Real-time overhead food demonstration, one continuous take.
- Layers: LY-020, LY-021, LY-022, LY-023, LY-024, LY-025
- Effects: none
- Audio: AU-01, AU-02
- Ready: no
- Blockers: HI-02, HI-04

### SH-03 · frames 160–275

- Method: Macro live-action pour at 50 fps, finished at 25 fps.
- Layers: LY-030, LY-031, LY-032, LY-033, LY-034, LY-035
- Effects: FX-02, FX-03
- Audio: AU-01, AU-02, AU-03
- Ready: no
- Blockers: HI-02, HI-04

### SH-04 · frames 275–380

- Method: Product stills with a four-pack fan and a single camera move.
- Layers: LY-040, LY-041, LY-042, LY-043, LY-047, LY-044, LY-045, LY-046
- Effects: none
- Audio: AU-01, AU-02, AU-03
- Ready: no
- Blockers: HI-02

### SH-05 · frames 380–445

- Method: Finished-cup live action with a time-lapse transition.
- Layers: LY-050, LY-051, LY-052, LY-053, LY-054, LY-055
- Effects: FX-05
- Audio: AU-01, AU-02, AU-03, AU-04
- Ready: no
- Blockers: HI-02, HI-04

### SH-06 · frames 445–500

- Method: End-card composite with supplied logo and pack.
- Layers: LY-060, LY-061, LY-062, LY-063, LY-064, LY-065
- Effects: FX-06
- Audio: AU-01, AU-02, AU-03, AU-04
- Ready: no
- Blockers: HI-02

## Variants

### VO-01 · 1080x1920 @ 25 fps

- Frames: 500
- Layer overrides: 38 of 38
- Effect overrides: FX-01, FX-02, FX-03, FX-05
- Safe area: 220/320/60/140
- Check status: `pending`
- Ready: no
- Blockers: AC-16 pending: 9:16 safe-area template not confirmed

## Timeline

- `TL-001` layer LY-010 0–75
- `TL-002` layer LY-011 0–75
- `TL-003` layer LY-012 0–75
- `TL-004` layer LY-013 0–75
- `TL-005` layer LY-014 0–75
- `TL-006` layer LY-015 0–75
- `TL-007` layer LY-020 75–160
- `TL-008` layer LY-021 75–160
- `TL-009` layer LY-022 75–160
- `TL-010` layer LY-023 75–160
- `TL-011` layer LY-024 75–160
- `TL-012` layer LY-025 75–160
- `TL-013` layer LY-030 160–275
- `TL-014` layer LY-031 160–275
- `TL-015` layer LY-032 160–275
- `TL-016` layer LY-033 160–275
- `TL-017` layer LY-034 160–275
- `TL-018` layer LY-035 160–275
- `TL-019` layer LY-040 275–380
- `TL-020` layer LY-041 275–380
- `TL-021` layer LY-042 275–380
- `TL-022` layer LY-043 275–380
- `TL-023` layer LY-047 275–380
- `TL-024` layer LY-044 275–380
- `TL-025` layer LY-045 275–380
- `TL-026` layer LY-046 275–380
- `TL-027` layer LY-050 380–445
- `TL-028` layer LY-051 380–445
- `TL-029` layer LY-052 380–445
- `TL-030` layer LY-053 380–445
- `TL-031` layer LY-054 380–445
- `TL-032` layer LY-055 380–445
- `TL-033` layer LY-060 445–500
- `TL-034` layer LY-061 445–500
- `TL-035` layer LY-062 445–500
- `TL-036` layer LY-063 445–500
- `TL-037` layer LY-064 445–500
- `TL-038` layer LY-065 445–500
- `TL-039` audio AU-01 0–500
- `TL-040` audio AU-02 0–500
- `TL-041` audio AU-03 160–245
- `TL-042` audio AU-04 440–485
- `TL-043` caption LY-015 0–75
- `TL-044` caption LY-025 75–160
- `TL-045` caption LY-035 160–275
- `TL-046` caption LY-046 275–380
- `TL-047` caption LY-055 380–445
- `TL-048` caption LY-065 445–500
