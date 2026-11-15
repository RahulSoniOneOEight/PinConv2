# Pending asset routes — stock vs generation

**Project:** `blue-tokai-easy-pour-20s` · **Run:** `rev-002`
**Purpose:** decide, for every pending image/asset, whether it should be
**stock-sourced**, **generated**, or neither.
**Status:** recommendation only; Gate 2A is still `ready_for_approval`.

## Decision rule

Apply the truth class first. Source convenience never overrides it.

| Truth class | Stock? | Generated? | Required route |
|---|---|---|---|
| `exact` | **No** | **No** | Supplied brand file or real capture |
| `exact_text` | **No** | **No** | Approved copy rendered procedurally |
| `proof` | **No** | **No** | Real capture of the demonstration |
| `atmospheric` | Yes, licence-cleared | Yes, disclosed | Owned plate, stock, or procedural |
| `representative` | Yes, licence-cleared | Yes, disclosed | Procedural, stock, or disclosed generation |
| `editorial` | Yes, licence-cleared | Yes, disclosed | Stock or authored |

So: **all exact product/pack/logo and all proof footage are supply/capture
only.** Stock or generation there is a method-matrix failure, not a shortcut.

## Asset-by-asset

| Asset | What it is | Current route | Stock? | Generated? | Recommended route |
|---|---|---|---|---|---|
| `AS-01` | Blue Tokai logo | supplied | No | No | Use the approved logo file; clear `HI-02` |
| `AS-02` | Easy Pour Mixed Bag pack | supplied | No | No | Use the approved pack image; clear `HI-02` |
| `AS-03` | Easy Pour Vienna pack | supplied | No | No | Use the approved pack image; clear `HI-02` |
| `AS-04` | Easy Pour Attikan Estate pack | supplied | No | No | Use the approved pack image; clear `HI-02` |
| `AS-17` | Easy Pour Seethargundu Estate pack | supplied | No | No | Use the approved pack image; clear `HI-02` |
| `AS-05` | Brewing demonstration, hands | capture | No | No | Shoot on the demonstration session; clear `HI-04` |
| `AS-06` | Hot water pour and bloom | capture | No | No | Shoot on the demonstration session; clear `HI-04` |
| `AS-07` | Warm kitchen background | owned | Fallback only | Fallback only | Keep the owned plate; if unavailable use `M4` procedural, not stock |
| `AS-08` | Finished cup | capture | No | No | Shoot on the demonstration session; clear `HI-04` |
| `AS-09` | Voice over, warm Indian English | supplied | No | No | Record the approved voice artist; clear `HI-03` |
| `AS-10` | Music bed, 20 s | stock | **Yes** | No | Licence **“Lost Roamin'” by speck** (CC BY 3.0), preview already fetched |
| `AS-11` | Water pour SFX | owned | No | No | Use in-house foley |
| `AS-12` | Brand sting | owned | No | No | Use in-house sting |
| `AS-13` | Captured Mixed Bag fallback | capture | No | No | Capture only if the primary pack path triggers the fallback |
| `AS-14` | Music fallback track | stock | **Yes** | Possible but unnecessary | Licence **“This Is Our Music - Instrumental” by gabriel_shelligton** (CC BY 3.0) |
| `AS-15` | Synthetic narration fallback | generate | No | **Yes** | Use the disclosed Edge TTS sample now; approve an OpenMontage speech route only if fallback is triggered |

## What this means

### Stock

Only two assets are genuinely stock candidates:

1. `AS-10` — primary music bed.
2. `AS-14` — conditional music fallback.

Both already have CC BY 3.0 candidates and 20-second previews in `sourcing/`.
Neither has been acquired into `sourced/`; final acquisition still needs Gate 2A.

There is **no pending image that should be stock-sourced**. The image layers are
either exact brand assets, proof capture, an owned background, or procedural
plates/effects.

### Generation

Only one asset is a generation candidate:

- `AS-15` — synthetic narration fallback.

It is conditional. The Edge TTS sample is free and disclosed; a paid
OpenMontage speech route is not authorised. **No image should be generated**:
every image layer is exact, proof, owned, or procedural.

### Neither

These need human/supply work, not a media search:

- `AS-01`, `AS-02`, `AS-03`, `AS-04`, `AS-17` — supplied brand files + rights.
- `AS-05`, `AS-06`, `AS-08`, `AS-13` — capture + talent/location release.
- `AS-07` — owned set plate; procedural fallback is already approved.
- `AS-09` — voice artist session and licence.
- `AS-11`, `AS-12` — owned sound design.

## Immediate order of work

1. Clear `HI-02` for the logo and four pack images.
2. Clear `HI-04` and shoot `AS-05`, `AS-06`, `AS-08`; keep `AS-13` conditional.
3. Clear `HI-03` and record `AS-09`.
4. Approve Gate 2A; acquire `AS-10` and, only if triggered, `AS-14`.
5. Use the existing `AS-15` Edge TTS sample only as a disclosed fallback; do not
   buy a speech generation route unless the fallback is triggered.

**Bottom line:** the stock/generation question applies to **audio only**
(`AS-10`, `AS-14`, `AS-15`). The pending images are supply/capture work, not
stock or generation candidates.
