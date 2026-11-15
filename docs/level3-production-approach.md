# Level 3 — Production approach

**Status:** agreed approach for execution. Updated 2026-11-15.
**Rule:** Level 2 plans; Level 3 executes the plan and tracks spend.

## Boundary

| Layer | Owns |
|---|---|
| Level 1 | Concept, creative plan, Gate 1 |
| Level 2 | Sourcing, per-asset processing plan, budget, provider governor, Gate 2A. No execution. |
| Level 3 | Execution: asset finalization, composition, render, QC, spend tracking, delivery |

**Level 3 outcomes:** final video(s) + per-step spend schedule.

## Tool roles

| Tool | Role |
|---|---|
| OpenMontage | Primary: import/attach assets, HyperFrames composition, render 16:9 + 9:16, `media.inspect` QC |
| ShortGPT | Edge TTS voice, transcription/caption timing |
| fal.ai / Runware | High-impact hero generation only (quote ≤ $0.50/job) |
| ffmpeg / local | Deterministic processing and audio checks |
| Mixkit | Free stock video/music/sfx gaps |

## Three-phase execution

### Phase 1 — Finalize assets ($0 expected)

1. Import selected stock + supplied brand masters into OpenMontage.
2. Run the Level 2 processing plan: cutout, grade, scale, trim, conform, denoise, loudness.
3. Generate voice with ShortGPT; build caption timings.
4. Probe every output; record each step as a $0 ledger line.

Exit: every asset processed/probed; spend $0.

### Phase 2 — Compose and render locally ($0 expected)

1. Author the HyperFrames composition from the build sheet: shots, layers, captions, effects, vertical.
2. Render with OpenMontage HyperFrames.
3. `media.inspect` + visual QC (sync, loudness, black frames, safe area).
4. Record render + QC as $0 lines.

Exit: both videos rendered and QC-passed; spend $0.

### Phase 3 — Hero generation and delivery (paid, capped)

1. Identify only hero gaps surviving Phase 2.
2. `reserve` a quote ≤ $0.50, call fal/Runware, `receipt` actual (or `release` on failure).
3. Re-render affected shots, final QC, export + manifest + spend schedule.

Exit: final videos + spend schedule; total ≤ $2.00.

## Spend schedule

Every step writes a line:

```
step | provider | description | quote | actual | status | cumulative | remaining
```

- Local steps: $0 receipt lines.
- Paid steps: reserved -> receipt (or released).
- Refuse a quote above remaining; cap $2.00, per-job $0.50.

Outputs: `deliverables/LEVEL3-SPEND.md`, `deliverables/level3-spend.json`,
`deliverables/level3-spend.jsonl`.

## Checkpoints

| Checkpoint | Evidence |
|---|---|
| L3-P1 | processed assets + $0 spend proof |
| L3-P2 | 16:9/9:16 render + QC + $0 proof |
| L3-P3 | hero quote(s) before spend, then final + spend schedule |

## Governance rules

- No paid call before Phase 3 and a positive quote.
- No in-house production: stock, AI generation, or AI enhancement of stock only.
- AI generation ≤ 40% (currently 3 of 16: AS-09, AS-12, AS-15).
- Do not approve Gate 2A on a human's behalf.
- The no-in-house routes need a fresh `rev-003` plan and Gate 2A before paid work;
  do not spend against the stale capture/in-kind packet.

## Current readiness

- Level 2 plan/assets/processing: ready.
- OpenMontage + HyperFrames: verified.
- ShortGPT voice: working.
- Level 3 spend ledger: implemented; $0.00 spent of $2.00.
- Rough cut (free/local): `deliverables/ROUGH-CUT-16x9.mp4` / `ROUGH-CUT-9x16.mp4`,
  labelled NOT FINAL.
