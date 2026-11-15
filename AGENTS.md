# PinConv2 project rules

- Level 1 plans. It never generates, downloads, renders or publishes paid media.
- The machine-readable record is the source of truth; Markdown is rendered from it.
- Every plan output is bound to a revision and a content hash.
- Exact commercial fields (price, offer, code, pack art, logo, CTA, claims) bind to an
  exact-data record. Public observation is not approval.
- A named human approves Gate 1. Agents must never record approval on a human's behalf.
- Research separates observation, interpretation and proposed decision. Inaccessible
  channels are recorded as unknown.
- Run `python -m pytest` and `python -m ruff check .` before reporting a change complete.
- Do not add a UI, database, queue or provider integration until a measured need exists.

## Level 2 vs Level 3

- **Level 2 plans only.** It owns sourcing, per-asset processing plans, budget, the
  provider governor and Gate 2A. It does **not** execute production.
- **Level 3 executes the approved plan.** Primary tool: OpenMontage (import/attach,
  HyperFrames composition + render, `media.inspect` QC). ShortGPT: Edge TTS voice
  and caption timing. fal.ai / Runware: high-impact hero generation only. ffmpeg:
  deterministic processing. Mixkit: free stock gaps.
- **Level 3 outcomes:** the final video(s) and a per-step spend schedule.
- **Level 3 runs in three phases:**
  1. Finalize assets ($0 expected) — processing, ShortGPT voice, probes.
  2. Compose + render + QC ($0 expected) — OpenMontage HyperFrames, 16:9 and 9:16.
  3. Hero generation + delivery (paid, capped) — fal/Runware only for surviving
     hero gaps; quote before spend, receipt actual.
- **Every Level 3 step writes a spend line** (quote, actual, cumulative, remaining)
  to the Level 3 ledger. No paid call before Phase 3 and a positive quote; never
  exceed the $2.00 cap or the $0.50 per-job maximum.
- **No in-house production:** assets are licensed stock, AI generation, or AI
  enhancement of stock. No shoot, set build, in-house voice or manual pack prep.
- Agents must not approve Gate 2A on a human's behalf. The no-in-house routes need
  a fresh `rev-003` plan and Gate 2A before paid work; do not spend against the
  stale capture/in-kind packet.

