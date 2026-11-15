# Level 2 re-baseline proposal — no in-house production

**Why:** Gate 2A was approved against the old capture/in-kind plan
(`plan_hash 1370f029…`). The production actually runs the no-in-house routes,
so the approval does not cover it. This is the proposed re-baseline.

## Proposed routes

| Asset | Old route / class | New route / class | Method |
|---|---|---|---|
| AS-05 hands | capture / proof | stock (Pixabay/Pexels) / representative | M2 |
| AS-06 pour/bloom | capture / proof | stock (Pixabay/Pexels) / representative | M2 |
| AS-08 cup | capture / proof | stock (Openverse/Pexels) / representative | M2 |
| AS-13 pack fallback | capture / exact | supplied AS-02 / exact | M0 |
| AS-07 background | owned set build / atmospheric | stock / atmospheric | M1 |
| AS-09 voice | supplied session / representative | AI TTS / representative (generated) | M7 |
| AS-11 SFX | owned foley / atmospheric | stock / atmospheric | M1 |
| AS-12 sting | owned / atmospheric | AI generation / atmospheric | M7 |
| AS-01/02/03/04/17 | supplied / exact | unchanged | M0 |
| AS-10/14 music | stock | unchanged | M1 |
| AS-15 narration | generate | unchanged | M7 |

## Governance changes

- Drop CAP-01 (capture plan) and HI-04 (talent release) — no shoot.
- Replace the 10 in-kind lines with stock / AI-generation / AI-enhancement /
  tool processing (`NO-IN-HOUSE-POLICY.md`).
- AI generation stays at 3 assets (18.8% ≤ 40%).
- Budget: stock mostly free; AI generation/enhancement inside the $2.00 cap.
- Produce a **new run id** (e.g. `rev-003`) with its own plan hash and Gate 2A
  packet. The old `rev-002` approval remains historical and is not reused.

## What is implemented already

- `no_shoot.py`, `no_in_house.py`, `gaps.py`.
- `stock_plan.py` multi-source scoring + annex.
- `processing_plan.py` per-asset AI processing and $2 budget.
- `RENDERER-DECISION.md` accepted (HyperFrames).
- Rough cut (free/local) in `deliverables/ROUGH-CUT-16x9.mp4` /
  `ROUGH-CUT-9x16.mp4`, 48 kHz stereo, labelled NOT FINAL.

## What still needs a named human

- Approve the new `rev-003` Gate 2A packet.
- HI-02 brand files + advertising rights (logo + 4 packs).
- HI-05 typeface; AC-16 9:16 safe area.
- Confirmation that proof → representative (AS-05/06/08) with disclosure is
  acceptable.

## Blocking note

Do not spend against the old `rev-002` Gate 2A. The new run must be planned,
hashed and approved before paid fal/Runware or the HyperFrames final render.
