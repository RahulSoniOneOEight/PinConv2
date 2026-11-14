# PinConv2 — Level 2 Implementation Plan

**Asset Production Planner → Ready-to-Assemble Build Sheet → Rough Cut**

| Field | Value |
|---|---|
| Date | 2026-11-15 |
| Status | Approved for implementation — no code written yet |
| Repository | `D:\pinconv2` |
| Base commit | `0feab16 feat: make 9:16 variant executable and include it in handoff` |
| Level 1 state | Approved, Gate 1 passed, 66 tests passing, Ruff and mypy clean |
| Acceptance fixture | Blue Tokai Easy Pour 20s, revision 002, variant `VO-01` |
| Spend authority | None. Gate 2A must be approved by a named human before any paid call |

This document is the build contract for Level 2. It is written to be implemented
directly: every phase has a deliverable and an exit test, every rule references
real IDs from the approved plan, and every number is reproducible from
`plans/rev-002.json`.

### Implementation notes (as built)

| Point | Resolution |
|---|---|
| Exact capture | `AS-13` is an `exact` pack acquired by capture. The matrix therefore allows `exact → M6` **only** for a capture of the original object (`original_capture`); stock and generation stay blocked. |
| Synthetic voice | `AS-15` is `representative` and `M7`; the matrix allows it only with `disclosure_required=true`. |
| Gate order | Gate 2A is assembled as `ready_for_approval`; only a named human can approve it. Gate 2B and `level2 build` refuse until that approval exists. |
| Budget | Handoff per-asset lines sum to $89.00; dedupe removes $42.00 of repeated `ES-06`/`ES-07`, leaving the approved $76.00 subtotal and $87.40 total. |
| Operator cap | `level2 plan --cap` sets a user cap; the effective cap is the lower of the approved cap and the operator cap. Exceeding it blocks Gate 2A instead of aborting the plan. |
| Lean mode | `--lean` moves paid lines to zero-cash in-kind work and records each substitution for Gate 2A approval; cash total becomes $0.00 with the in-kind value shown separately. |
| Critical path | The computed path is capture-led (`CAP-01 → AS-05/06/08 → shot → VO-01`), not the illustrative order in §15.1. |
| Sourcing | No sourcing round runs in the spend-free slice; candidate licences are reported as unverified, not as cleared. |
| Verification | 116 tests pass; Ruff and mypy are clean; the Blue Tokai run produces the full artifact set under `projects/blue-tokai-easy-pour-20s/level2/runs/rev-002/`. |


---

## 0. How to read this

| Reader | Sections |
|---|---|
| Product / brand owner | 1, 11.5, 21, 22, 27 |
| Implementer | 2–20, 23–25 |
| Reviewer / QC | 6–12, 21–22, 25–26 |
| Compositor receiving the build sheet | 15–18, Appendix A–C |

Terms are defined in Appendix E. Numbers marked **computed** were produced from
the approved JSON during planning and must be re-derived by code, not hardcoded.

---

## 1. Goal and boundaries

### 1.1 The job

Level 2 consumes the approved, hash-bound Level 1 output and answers, for every
asset and every layer:

1. **What is it?** — truth class, impact, rights state.
2. **Where does it come from?** — supplied, owned, stock, capture, generate.
3. **How is it made?** — processing recipe, generation spec, or capture plan.
4. **What does it cost?** — acquisition, processing, reserve, fallback.
5. **Is it good enough?** — rights, technical, acceptance, continuity gates.
6. **When does it run?** — dependency graph, batch, critical path.
7. **Is it ready to assemble?** — build sheet, bindings, variant, blockers.

Level 2 does **not** reopen a creative decision. Shot count, copy, price, pack
choice, effect design and the approved 9:16 variant are fixed inputs.

### 1.2 In scope

- Stock sourcing (image, video, audio, SFX, fonts, icons, 3D/textures).
- Generation through OpenMontage / fal / Runware where L1 permits it.
- Ingestion of supplied brand files and captured demonstration footage.
- Processing to technical and creative spec.
- Evaluation of every Shot × Layer × Asset binding.
- 16:9 master package and 9:16 `VO-01` package.
- Budget with quotes, dedupe, reserve and cap control.
- Ready-to-assemble build sheet.
- Human review pack, typed corrections, re-plan loop.
- Assembly of 16:9 and 9:16 rough cuts.

### 1.3 Out of scope

- Re-deciding concept, copy, shots, layers, effects or variant geometry.
- Inventing price, pack size, claims, CTA destination or placement name.
- Using unlicensed brand media.
- Final mastering sign-off, publishing, scheduling (Level 3).
- Performance measurement (Level 4).

### 1.4 Hard prohibitions

1. No paid acquisition, generation or render before **Gate 2A** approval.
2. No exact or proof layer may use stock-as-is or generated product media.
3. No source that is NC, ND, SA or on the block list may enter a package.
4. Manual-only sources are never fetched by script.
5. Aggregator licences (Openverse, Internet Archive, Wikimedia) are never
   trusted as-is; the origin licence must be resolved and recorded.
6. No `needs_approval`, `unknown` or `reference_only` asset is marked ready.
7. No correction edits an approved record in place; corrections create a new run.

---

## 2. Ground truth: inputs

| Input | Path | Role |
|---|---|---|
| Plan revision | `projects/blue-tokai-easy-pour-20s/plans/rev-002.json` | Immutable approved plan |
| Production plan | `projects/blue-tokai-easy-pour-20s/exports/rev-002/production-plan.json` | Full detail: 6 shots, 38 layers, 16 assets, 6 effects |
| Level 2 handoff | `projects/blue-tokai-easy-pour-20s/exports/rev-002/level2-handoff.json` | Approved scope, 13 in-scope assets, `VO-01` overrides |
| Research pack | `projects/blue-tokai-easy-pour-20s/exports/rev-002/research-pack.json` | Effect assessments and evidence |
| Approval record | `projects/blue-tokai-easy-pour-20s/approvals/rev-002.json` | Approver, scope, exact data, variant |
| Brief | `projects/blue-tokai-easy-pour-20s/brief.json` | `MH-01`–`MH-09`, cap `$100`, 500 frames @ 25 fps |

### 2.1 Hash chain

| Artefact | SHA-256 |
|---|---|
| Plan | `1370f029b0b35730625c459cf85579bfd767d2e4a7b62016055e100d15f2aba5` |
| Bundle | `5a67ac5e48201fc48984a7f913d0f040e57327e807d072e488aad00810574cc2` |
| Packet | `756d91de1005ff0c5002a12670168498f164c80bed1a4d89feacab33e949e427` |

Level 2 recomputes all three at ingestion. Any mismatch → `E_HANDOFF_HASH` and
no planning proceeds. Every Level 2 artefact records `source_plan_hash`, so the
package is provably derived from the approved revision.

### 2.2 Approval facts to carry forward

- Approver: `RahulSoniOneOEight`
- Scope: `SH-01`–`SH-06`
- Approved exact data: `ED-01`, `ED-04`, `ED-05`
- Approved variants: `VO-01`
- Conditions: 18, including holds `HI-01`–`HI-05`
- Allowed substitutions: none

### 2.3 Data-shape facts that must not be assumed away

- Assets are `AS-01`–`AS-15` plus `AS-17`. **There is no `AS-16`.** Code must
  never iterate a contiguous `AS-01..AS-16` range.
- Copy blocks are `CP-01`–`CP-05` and `CP-07`–`CP-13`. **There is no `CP-06`.**
- The handoff lists **13** assets. The plan lists **16**. `AS-13`, `AS-14` and
  `AS-15` are fallbacks and are planned as *conditional* tasks, not acquired by
  default.
- 38 layers: 19 asset-bound, 12 copy-bound, 7 unbound (6 caption plates + 1
  steam effect layer rendered procedurally).
- 4 layers carry effects: `LY-012`, `LY-031`, `LY-051`, `LY-063` (see
  Appendix C).
- `AC-16` (9:16 safe area) is `pending`; `VO-01` safe area is an operator
  assumption.

---

## 3. Outputs

```
projects/blue-tokai-easy-pour-20s/level2/runs/rev-002/
  run.json                      run id, source hashes, state, timestamps
  asset-intents.json            16 intents (13 in scope, 3 conditional)
  layer-method-decisions.json   38 decisions
  asset-production-tasks.json   16 tasks
  capture-plan.json             1 session covering AS-05 / AS-06 / AS-08
  sound-plan.json               AS-09 / AS-10 / AS-11 / AS-12
  budget-estimate.json          machine source
  budget-estimate.md            user-facing, readable
  budget-estimate.docx          shareable
  spend-ledger.json             reservations and receipts (empty until Gate 2A)
  catalogue-resolutions.json    candidate → licence → origin verification
  licence-gate-report.json      blocks, warnings, attributions
  rights-manifest.json          per-asset rights posture
  sourced/                      untouched originals
  processed/                    final media per asset
  generated/                    provider output + job records
  previews/                     2-second probes, thumbnails
  qc/
    technical.json
    visual.json
    semantic.json
  build-sheet/
    manifest.json
    production-build-sheet.md
    production-build-sheet.docx
    assets/<asset_id>.json     (16 files: AS-01–AS-15, AS-17)
    shots/SH-01.json … SH-06.json
    variants/VO-01.json
    timeline/timeline.json
    captions/captions-16x9.srt
    captions/captions-9x16.srt
  review-pack.md
  review-pack.docx
  feedback-form.md
  corrections.jsonl
  blockers.json
  gate2/
    packet-2a.json
    packet-2b.json
    packet-2c.json
  deliverables/
    blue-tokai-20s-16x9-v1.mp4
    blue-tokai-20s-9x16-v1.mp4
    audio-stems/
```

---

## 4. State machine

```
HANDOFF_VALIDATED
  → METHOD_PLANNED
  → CAPTURE_PLANNED
  → QUOTED
  → BUDGET_APPROVED        (Gate 2A — human)
  → SOURCING
  → PROBES_PASSED
  → ASSETS_PROCESSED
  → SHOT_PACKAGES_READY
  → GATE2_READY            (Gate 2B — human + independent reviewer)
  → ROUGH_CUT_REVIEWED     (Gate 2C — human)
  → APPROVED
```

`BLOCKED` is reachable from any state. Each transition writes a `run.json`
event with actor, timestamp, input hashes and check results. Transitions are
refused if any guard fails; guards are listed in Section 22.

---

## 5. Data contracts

All records are pydantic v2 models with `extra="forbid"`, UUID-free stable
string IDs, ISO-8601 UTC timestamps and explicit `schema_version`.

### 5.1 `AssetIntent`

One per L1 asset (16).

| Field | Type | Notes |
|---|---|---|
| `asset_id` | str | `AS-01` … `AS-17` |
| `name` | str | from L1 |
| `route` | enum | `supplied`, `owned`, `to_source`, `to_capture`, `to_create`, `to_generate` |
| `exactness` | enum | `exact`, `illustrative` |
| `truth_class` | enum | derived — Section 6 |
| `impact` | enum | derived — Section 7 |
| `scope` | enum | `approved`, `conditional_fallback` |
| `tech` | TechSpec | format, dimensions, fps, duration, alpha, loudness |
| `rights` | RightsSpec | copied unchanged from L1 |
| `acceptance` | str | verbatim from L1 |
| `allowed_edits` | list[str] | verbatim |
| `dependencies` | list[str] | asset IDs |
| `fallback_asset_id` | str \| null | |
| `used_by` | list[str] | layer IDs |
| `estimate_id` | str \| null | `ES-xx` |
| `blockers` | list[str] | hold IDs affecting this asset |

### 5.2 `LayerMethodDecision`

One per layer (38). This is the core reviewable record.

| Field | Type | Notes |
|---|---|---|
| `layer_id` | str | `LY-010` … `LY-065` |
| `shot_id` | str | |
| `role` | enum | background, product, subject, logo, typography, caption, caption_plate, cta, effect |
| `truth_class` | enum | Section 6 |
| `truth_class_rule` | str | rule ID, e.g. `R3` |
| `impact_score` | int | 0–9 |
| `impact` | enum | `high`, `medium`, `low` |
| `impact_signals` | list[str] | `MH`, `t3`, `data`, `area`, `dur` |
| `method` | enum | `M0` … `M8` |
| `method_reason` | str | reason code + human sentence |
| `candidates` | list[Candidate] | 0–5 |
| `chosen_candidate` | str \| null | candidate ID |
| `fallback_method` | enum | must satisfy the class matrix |
| `probe_required` | bool | true for M2–M7 |
| `probe_id` | str \| null | `PR-xxx` |
| `rights_gate` | enum | `pass`, `hold`, `block` |
| `cost_usd` | float | attributable or 0 |
| `notes` | str \| null | |

### 5.3 `AssetProductionTask`

One per asset (16).

| Field | Type | Notes |
|---|---|---|
| `task_id` | str | `APT-AS-02` |
| `asset_id` | str | |
| `source_strategy` | enum | `supplied`, `owned`, `stock`, `capture`, `generate`, `procedural` |
| `methods` | list[str] | methods used together, e.g. `["M6","M2"]` |
| `processing_recipe` | list[Op] | Section 13 |
| `generation_spec` | GenerationSpec \| null | Section 14 |
| `capture_ref` | str \| null | `CAP-01` |
| `budget_line_ids` | list[str] | `BL-xxx` |
| `flow` | FlowSpec | deps, stage, batch, critical path flag |
| `acceptance` | str | from L1 |
| `probe_required` | bool | |
| `conditional` | bool | true for `AS-13`, `AS-14`, `AS-15` |
| `status` | enum | `planned`, `sourced`, `probed`, `processed`, `accepted`, `blocked`, `conditional` |

### 5.4 `Candidate`, `SourceReceipt`, `ProbeRecord`

```json
{
  "candidate_id": "CND-AS10-01",
  "asset_id": "AS-10",
  "provider": "ccmixter",
  "url": "https://ccmixter.org/files/...",
  "licence_class": "CC-BY",
  "licence_url": "https://...",
  "origin_verified": true,
  "attribution_text": "\"...\" by ... licensed CC BY 4.0",
  "scriptable": true,
  "fit_score": 78,
  "technical_match": true,
  "cost_usd": 0.0,
  "preview_path": "previews/AS-10-cand-01.mp3",
  "gate_result": "pass"
}
```

```json
{
  "receipt_id": "RCP-0007",
  "candidate_id": "CND-AS10-01",
  "provider": "ccmixter",
  "provider_job_id": null,
  "sha256": "…",
  "bytes": 4823110,
  "licence_snapshot": "…",
  "amount_usd": 0.0,
  "acquired_at": "2026-11-15T10:22:31Z"
}
```

```json
{
  "probe_id": "PR-AS06-01",
  "layer_ids": ["LY-021", "LY-031"],
  "method": "M6",
  "sample_path": "previews/AS-06-probe-2s.mp4",
  "acceptance_ref": "LY-021.acceptance",
  "verdict": "pass",
  "reviewer": "vision:chatgpt",
  "reviewed_at": "2026-11-15T11:04:00Z",
  "expires_at": "2026-12-15T11:04:00Z"
}
```

### 5.5 `ProcessedAsset`

`asset_id`, `path`, `sha256`, `bytes`, `ffprobe` (codec, pix_fmt, width, height,
fps, duration, channels, sample_rate, loudness LUFS/TP), `transforms_applied`,
`acceptance_result`, `probe_id`, `derived_from` (candidate/receipt/generation).

### 5.6 `BudgetLine`

| Field | Type | Notes |
|---|---|---|
| `line_id` | str | `BL-xxx` |
| `estimate_id` | str \| null | trace to L1 `ES-xx` |
| `asset_id` | str \| null | null for project-level lines |
| `kind` | enum | `acquisition`, `capture`, `processing`, `variant`, `fallback`, `project` |
| `amount_usd` | float | |
| `basis` | enum | `verified_quote`, `operator_estimate` |
| `quote_ref` | str \| null | required for `verified_quote` |
| `quote_expires_at` | str \| null | |
| `dedupe_key` | str \| null | e.g. `ES-06:capture-session` |
| `in_worst_case` | bool | |
| `notes` | str \| null | |

### 5.7 `Correction`

Section 21.4.

### 5.8 `BuildSheet` and `manifest.json`

The build sheet is pure data plus a rendered Markdown/DOCX view. `manifest.json`
records each part with its SHA-256, byte count and schema version, plus
`source_plan_hash`, `bundle_hash`, `packet_hash`, `run_id` and `generated_at`.

---

## 6. Truth classification

Level 2 does not invent a new taxonomy. It derives a **truth class** from L1
fields with an explicit, testable rule and stores the rule ID beside the result.

### 6.1 Rules (first match wins)

| Rule | Condition | Truth class |
|---|---|---|
| `R1` | `layer.exactness == "exact"` | `exact` |
| `R2` | `layer.exactness == "proposed_copy"` or `layer.binding_kind == "copy"` | `exact_text` |
| `R3` | `layer.role == "subject"` and bound asset `route == "to_capture"` | `proof` |
| `R4` | `layer.role ∈ {background, effect}` | `atmospheric` |
| `R5` | otherwise | `representative` |

`exact_text` and `proof` are subtypes of Exact and Proof used to drive different
method constraints: text is rendered from data (M4), proof is captured (M6).

### 6.2 Computed distribution (Blue Tokai)

| Class | Layers | IDs |
|---|---|---|
| `exact` | 10 | `LY-011`, `LY-022`, `LY-032`, `LY-041`, `LY-042`, `LY-043`, `LY-047`, `LY-052`, `LY-061`, `LY-062` |
| `exact_text` | 12 | `LY-013`, `LY-015`, `LY-023`, `LY-025`, `LY-033`, `LY-035`, `LY-044`, `LY-046`, `LY-053`, `LY-055`, `LY-063`, `LY-065` |
| `proof` | 3 | `LY-021`, `LY-031`, `LY-051` |
| `atmospheric` | 7 | 6 backgrounds (`LY-010`, `020`, `030`, `040`, `050`, `060`) + `LY-012` |
| `representative` | 6 | six caption plates |

Constraint: `R1`–`R5` must be pure functions of L1 data. Any layer that cannot be
classified raises `E_TRUTH_CLASS`; no default bucket is allowed.

---

## 7. Impact scoring

### 7.1 Signals

| Code | Signal | Points | Source |
|---|---|---|---|
| `MH` | Layer, its bound asset, or its copy block appears directly in `MH-xx.satisfied_by` | +3 | brief. **Shot-level references do not count.** |
| `t3` | Global start frame `shot.start_frame + layer.start_frame < 75` | +2 | plan |
| `data` | `exactness ∈ {exact, proposed_copy}` | +2 | layer |
| `area` | `rect.w × rect.h ≥ 0.25 × 1920 × 1080` | +1 | layer |
| `dur` | `end_frame − start_frame > 50` (>2 s) | +1 | layer |

**Design correction found during planning:** an earlier version awarded `MH`
when the *shot* was referenced and computed `t3` from shot-local frames. Both
made all 38 layers score high. Impact must use direct references and global
frames, otherwise the score cannot prioritise anything.

### 7.2 Thresholds

| Score | Impact | Consequence |
|---|---|---|
| ≥5 | high | deep sourcing, up to 5 candidates, human pick, probe mandatory |
| 3–4 | medium | normal sourcing, up to 3 candidates, human pick, probe mandatory |
| ≤2 | low | one search round, automatic pick, probe only where M2–M7 |

### 7.3 Computed distribution

| Impact | Count | Layers |
|---|---|---|
| high | 18 | `LY-011`, `LY-013`, `LY-015`, `LY-021`, `LY-022`, `LY-023`, `LY-031`, `LY-032`, `LY-041`–`LY-044`, `LY-047`, `LY-051`, `LY-052`, `LY-061`, `LY-062`, `LY-063` |
| medium | 10 | `LY-010`, `LY-012`, `LY-014`, `LY-025`, `LY-033`, `LY-035`, `LY-046`, `LY-053`, `LY-055`, `LY-065` |
| low | 10 | `LY-020`, `LY-024`, `LY-030`, `LY-034`, `LY-040`, `LY-045`, `LY-050`, `LY-054`, `LY-060`, `LY-064` |

The spread is sane: product, proof, logo and CTA are high; late caption plates
and later backgrounds are low. This distribution becomes a fixture assertion.

---

## 8. Method spectrum and selection

### 8.1 Spectrum

| Method | Meaning | Blue Tokai use | Spend |
|---|---|---|---|
| `M0` | Owned or supplied, as-is, trimmed and graded | Logo `AS-01`, packs `AS-02/03/04/17`, plate `AS-07`, SFX `AS-11/12`, voice `AS-09` | ~0 |
| `M1` | Stock as-is | Music bed `AS-10` if a track fits unedited | licence |
| `M2` | Stock or owned asset adapted | Cup clip regraded to match the counter plate | processing |
| `M3` | Kitbash | Owned pack on stock counter plus procedural steam | licence + processing |
| `M4` | Procedural / authored (Remotion / HyperFrames / ffmpeg) | Steam, type, caption plates, end card, speed ramp, sting | processing |
| `M5` | Reference-guided generation | Gap-fill / animate a still pour (fallback only) | generation |
| `M6` | Pickup capture | Tear, anchor, pour, finished cup (`AS-05/06/08`, `AS-13`) | capture |
| `M7` | Fully generated | Synthetic narration fallback `AS-15` (disclosed) | generation |
| `M8` | Full custom | Not needed for this plan | — |

### 8.2 Class × method matrix (enforced)

| Truth class | M0 | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 |
|---|---|---|---|---|---|---|---|---|---|
| `exact` | ✅ | ⛔ | ⛔ | ⛔ | ✅ geometry/type only | ⛔ | ✅ original capture only | ⛔ | ⛔ |
| `exact_text` | ✅ supplied artwork | ⛔ | ⛔ | ⛔ | ✅ text from copy block | ⛔ | ⛔ | ⛔ | ⛔ |
| `proof` | ⛔ | ⛔ | ✅ enhancement of capture only | ⛔ | ⛔ | ⛔ | ✅ primary | ⛔ | ⛔ |
| `representative` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ disclosed only | ⛔ |
| `atmospheric` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⛔ |
| `editorial` | ⛔ | ⛔ | ⛔ | ⛔ | ✅ over captured footage | ⛔ | ✅ source | ⛔ | ⛔ |

Any matrix violation raises `E_METHOD_CLASS` and fails the plan build. This is
the mechanism that stops "we couldn't find a pack photo, so we generated one".

### 8.3 Search yield → method

| Best candidate fit | Method | Notes |
|---|---|---|
| ≥85 | `M1` | acceptable unedited |
| 70–84 | `M2` | acceptable after grade/crop/retime |
| 55–69 | `M3`, `M4` or `M5` | cheapest that passes a probe |
| <55 | `M6` for proof, `M7` for atmospheric gap-fill, `M8` hero only | |

### 8.4 Selection algorithm

```
for layer in layers:
    cls   = classify(layer)                      # Section 6
    imp   = score(layer)                         # Section 7
    allow = matrix[cls]                          # Section 8.2
    cands = catalogue.search(layer, allow)       # scriptable + licence-gated
    cands = [c for c in cands if origin_verified(c)]
    cands = rank(cands, by=(fit, rights_margin, cost, reuse))
    best  = cands[0] if cands else None
    method = map_yield(best.fit) if best else escalate(cls)
    if method not in allow: method = cheapest_allowed(allow, that_passes(probe))
    if method in M2..M7 and not probe_planned(method): method = escalate(...)
    decision = LayerMethodDecision(...)
```

`escalate()` order:

1. Capture (`M6`) if the class permits and the asset is in the capture plan.
2. Procedural (`M4`) if the layer is type, plate, effect or end card.
3. Conditional fallback asset (`AS-13`, `AS-14`, `AS-15`).
4. `BLOCKED` with a named reason — never a silent downgrade.

### 8.5 Method reason codes

`class_requires_supplied`, `yield_high_m1`, `yield_mid_m2`, `yield_low_m3`,
`procedural_only`, `capture_required`, `capture_cheaper_than_stock`,
`reuse_existing_asset`, `rights_hold`, `no_passing_candidate`, `fallback_asset`.

Every decision stores one code plus a human-readable sentence.

---

## 9. Probe before commit

Any `M2`–`M7` choice requires a 2-second sample that passes the layer's L1
`acceptance` line **before** the full asset is paid for or processed.

| Rule | Detail |
|---|---|
| Sample length | 2 s (50 frames @ 25 fps) |
| Source | lowest-cost preview the provider offers; local render for M4 |
| Reviewer | vision model first, human for `high` impact |
| Pass condition | every acceptance clause for every layer the asset binds |
| Storage | `previews/PR-<asset>-<n>.<ext>` + `ProbeRecord` |
| Expiry | 30 days; pricing or source change invalidates |
| Cap | at most 2 probes per asset, at most 3 per high-impact asset |
| Failure | next candidate; after all fail → escalate per 8.4 |

Probes are spend-bearing on paid providers, so the probe cost is part of the
task budget, not a hidden extra.

---

## 10. Capture economics

One session covers the three proof assets plus foley and any marginal angle.

| Asset | Covered by | Note |
|---|---|---|
| `AS-05` demonstration, hands | `CAP-01` | Tear, anchor, pour |
| `AS-06` hot water pour, bloom | `CAP-01` | 50 fps for the ramp |
| `AS-08` finished cup | `CAP-01` | Includes steam plate reference |
| `AS-11` pour SFX | `CAP-01` | Foley on the same session |
| `AS-13` captured pack fallback | `CAP-01` | Conditional; shoot if schedule allows |
| Extra angles / steam plate | `CAP-01` | Marginal, same setup |

Cost: `ES-06` **$18.00** once for the session, not per asset. Fallback `ES-09`
**$5.00** only if `AS-13` is triggered.

Capture plan must record: date, studio, hand model, release status (`HI-04`),
shot list per storyboard, frame rates, colour target, audio rig, foley list,
backup media, and the acceptance lines the operator is shooting against.

---

## 11. Budget

### 11.1 Formula

```
subtotal  = Σ unique per-task cost + Σ project-level lines + Σ variant lines
reserve   = round(subtotal × retry_reserve_pct / 100, 2)      # 15%
total     = subtotal + reserve
worst     = total + Σ fallback lines
constraint: total ≤ cap  AND  worst ≤ cap
```

Reserve is applied **once at project level**. An earlier draft put 15% on every
task, which double-counted it.

### 11.1a Operator cap and lean mode

The approved Level 1 cap is not the only guard. A user can impose a lower
project cap:

```
effective_cap = min(approved_cap_usd, operator_cap_usd)
constraint: total <= effective_cap and worst <= effective_cap
```

`level2 plan --cap 2` records the cap in `budget-policy.json`. If the estimate
exceeds it, planning still completes, the variance is shown, the run state is
`blocked`, and Gate 2A fails `G2A-04`. This is deliberate: a blocked plan must
still be reviewable so the user can see the overage and choose.

`level2 plan --cap 2 --lean` produces a zero-cash in-kind budget. Each paid line
becomes $0.00 cash with an in-kind value and a named route and risk, and every
substitution is listed for Gate 2A approval. Lean mode never changes the
creative plan, the shot list or the layer methods; it changes who performs the
work and whether cash is spent. Gate 2A adds a `Lean substitutions` warning so
the approver sees exactly what they are accepting.

Per-task cost = acquisition + attributable processing. Project-level lines
(`ES-03` edit/motion, `ES-04` grade, `ES-08` end-card build) are **not**
allocated across assets by guesswork; they stay as named project lines.

### 11.2 Dedupe

| Rule | Example |
|---|---|
| One acquisition per asset | `AS-02` used by 6 layers → 1 acquisition |
| One capture session | `ES-06` covers `AS-05`, `AS-06`, `AS-08` → $18 once |
| One pack-preparation line | `ES-07` covers `AS-03`, `AS-04`, `AS-17` → $3 once |
| Variant lines separate | `ES-11` $6 for `VO-01` |
| Fallbacks never in subtotal | `ES-09` only in worst case |

Raw per-asset `estimate_usd` in the handoff sums to **$89.00**. Dedupe removes
**$42.00** of double-counted `ES-06` (3 × $18 → $18) and `ES-07` (3 × $3 → $3),
leaving **$47.00** direct, plus **$29.00** of unattached project and variant
lines = **$76.00** subtotal.

### 11.3 Blue Tokai estimate (computed)

| Line | Source | Kind | USD |
|---|---|---|---|
| Music library licence (`AS-10`) | `ES-01` | acquisition | 10.00 |
| Voice artist session and edit (`AS-09`) | `ES-02` | acquisition | 12.00 |
| Demo and finished-cup capture (`AS-05/06/08`) | `ES-06` | capture | 18.00 |
| Mixed Bag pack preparation (`AS-02`) | `ES-05` | processing | 4.00 |
| Range pack preparation (`AS-03/04/17`) | `ES-07` | processing | 3.00 |
| Edit, motion and compositing | `ES-03` | project | 15.00 |
| Colour grade and finishing | `ES-04` | project | 5.00 |
| End-card build (`SH-06`) | `ES-08` | project | 3.00 |
| 9:16 re-edit and end-card rebuild (`VO-01`) | `ES-11` | variant | 6.00 |
| **Subtotal** | | | **76.00** |
| Retry reserve 15% | | | 11.40 |
| **Estimated total** | | | **87.40** |
| Captured pack fallback (`AS-13`) | `ES-09` | fallback | 5.00 |
| **Worst case** | | | **92.40** |
| Cap | brief | | 100.00 |
| **Headroom** | | | **7.60** |

All lines are `operator_estimate`. Nothing is a `verified_quote` yet.

### 11.4 Quote lifecycle

```
operator_estimate → quote_requested → verified_quote → reserved → receipted → reconciled
```

- `verified_quote` requires `quote_ref` and `quote_expires_at`.
- A quote older than 30 days reverts to `operator_estimate`.
- Every paid call writes a ledger reservation **before** the call and a receipt
  after; failed calls write a release, not a deletion.
- Variance above 10% between quote and receipt raises `E_BUDGET_DRIFT` and
  pauses further spend pending human acknowledgement.

### 11.5 User-visible budget

The user always sees the estimate before spend, in three artefacts:
`budget-estimate.md` (readable), `budget-estimate.docx` (shareable) and the
Budget section of `review-pack.md`. Both documents show, per line: method, kind,
basis, amount, what must become a real quote, and the cap maths. After Gate 2A
the same view shows planned vs reserved vs actual.

### 11.6 Known budget gaps

| Gap | Impact | Action |
|---|---|---|
| `B-1` `AS-15` synthetic-narration fallback has no estimate line | Worst case understated | Require a TTS quote at Gate 2A or record it as `0.00` with an explicit "unpriced fallback" flag |
| `B-2` `AS-14` music fallback has no estimate line | Likely $0 if a second track under the same licence | Record as $0 with the licence reference |
| `B-3` `ES-03`/`ES-04`/`ES-08` are not attributable per asset | Per-asset totals do not sum to project total | Keep as project lines; state this in the build sheet |

---

## 12. Source catalogue and licence gate

### 12.1 Licence classes

| Class | Commercial output | Rule |
|---|---|---|
| `PD` / `CC0` | ✅ | Attribution optional; still record provenance |
| `CC-BY` | ✅ | Attribution mandatory |
| `CC-BY-SA` | ⚠️ | Block where share-alike can propagate onto the cut |
| `CC-BY-NC` | ⛔ | Block |
| `CC-BY-ND` | ⛔ | Block |
| `PROPRIETARY-FREE` | ✅ | Platform licence only; honour its restrictions |
| `EDITORIAL` | ⛔ | Block for advertising |
| `BLOCKED` | ⛔ | Never import |

### 12.2 Scriptability

Every catalogue entry carries `scriptable: true|false`. Manual-only sources are
listed for the human operator and are **never** fetched by code.

### 12.3 Catalogue

#### Music bed

| Source | Licence | API | Scriptable | Commercial | Notes |
|---|---|---|---|---|---|
| Free Music Archive | per-track CC | retired | ⛔ manual | varies | Never script |
| ccMixter | CC mixes/stems | `ccmixter.org/api/query?f=json` | ✅ no key | BY attribution | Remix friendly |
| Jamendo | per-track CC | `api.jamendo.com/v3.0/tracks` | ✅ client_id | paid clearance for commercial | Free tier restricted |
| Musopen | PD/CC | none | ⛔ manual | check recording, not score | Some NC |
| Incompetech | CC-BY | none | ⛔ manual | attribution | |
| Uppbeat / Bensound | freemium | none | ⛔ manual | credit + link on free tier | |
| Pixabay Music | Pixabay licence | none | ⛔ manual | ✅ no attribution | No standalone resale |
| Openverse audio | CC/PD aggregate | `api.openverse.org/v1/audio/` | ✅ no key | verify origin | Licence unverified |
| Internet Archive / Wikimedia | item-specific | IA + MediaWiki | ✅ | varies | Discovery only |

#### SFX

| Source | Licence | API | Scriptable | Commercial | Notes |
|---|---|---|---|---|---|
| Freesound | CC, varied | `freesound.org/apiv2` token | ✅ | NC/ND traps | Previews audition-only |
| BBC Sound Effects | RemArc | none | ⛔ | ⛔ **blocked** | Personal/education only |
| Zapsplat | free + attribution | none | ⛔ manual | account | No redistribution |
| Sonniss GDC | royalty-free per bundle | none | ⛔ manual | per bundle | Huge, check licence file |
| Mixkit / Pixabay SFX | free vs restricted | none | ⛔ manual | verify per file | |
| SoundBible / OpenGameArt | mixed CC0 / CC-BY | partial | ⚠️ | verify per file | |

#### Narration

| Source | Licence | Use |
|---|---|---|
| LibriVox | PD recordings | Only when the script matches the PD text |
| Common Voice | CC0 | ASR fixtures only, never delivery |

Blue Tokai uses a **performer** (`AS-09`, M0) with a disclosed synthetic
fallback (`AS-15`, M7) — not LibriVox.

#### Fonts

| Source | Licence | Rule |
|---|---|---|
| google/fonts | OFL / Apache / UFL per family | Licence file beside binary |
| Fontsource | per family | Self-host friendly |
| Fontshare | ITF | Exclude from OFL inventory |
| Open Font Library / League / Velvetyne | OFL / custom-open | Display faces |

Blue Tokai: **Inter (OFL)** until `HI-05` supplies the brand face.

#### Icons and emoji

| Source | Licence | Rule |
|---|---|---|
| Lucide / Phosphor / Tabler / Heroicons / Bootstrap | ISC / MIT | Safe defaults |
| Iconify | varies per set | Resolve the set licence |
| Material Symbols | Apache-2.0 | Licence travels with subset |
| Font Awesome Free | CC-BY icons / OFL fonts / MIT code | Attribution on icons |
| Twemoji / Noto Emoji | CC-BY 4.0 | Prefer over OpenMoji (SA) |
| OpenMoji | CC-BY-SA 4.0 | Avoid: share-alike |

#### Illustration and vector

| Source | Licence | Rule |
|---|---|---|
| unDraw | free commercial | No pack resale |
| Open Peeps | CC0 | Cleanest |
| Humaaans | CC-BY 4.0 | Attribution |
| Storyset | Freepik / CC-BY | On-screen credit on free tier |
| SVG Repo / Openclipart | mixed | Verify per file |

#### 3D, HDRI, texture

| Source | Licence | Notes |
|---|---|---|
| Poly Haven | CC0 | Best fit for Blender headless |
| ambientCG | CC0 | ZIP download API |
| Kenney / Quaternius | CC0 | Low-poly props |
| Poly Pizza | mixed CC0 / CC-BY | Filter |
| Sketchfab | per-model | CC0 filter mandatory |
| NASA 3D | US PD | Spacecraft/terrain only |

#### Photographic stills

| Source | Licence | API | Commercial |
|---|---|---|---|
| Pexels | Pexels licence | key, 200/h | metadata only, link required |
| Unsplash | Unsplash licence | Client-ID, 50/h demo | download event required; Unsplash+ excluded |
| Pixabay | Pixabay licence | `pixabay.com/api/` | no standalone resale |
| Openverse | CC aggregate | no key | licence unverified |
| Wikimedia Commons | PD/CC | MediaWiki | `Restrictions` → human review |
| Smithsonian | CC0 media | api.data.gov key | per-record usage field |
| The Met | CC0 Open Access | no key | fastest zero-key CC0 |
| Rijksmuseum | PD | key | strict rate limits |
| NYPL | item-level PD | token | metadata is not a grant |
| Library of Congress | per item | `fo=json` | archival strength |
| Europeana | mixed | wskey | verify at institution |
| NASA Image & Video | mostly US PD | no key | exceptions for partners/logos |

#### Video footage

| Source | Licence | API | Scriptable | Commercial |
|---|---|---|---|---|
| Coverr | free commercial | key + MCP; stats PATCH required | ✅ | **no AI training** |
| Wikimedia / IA video | PD (Prelinger) | MediaWiki / IA | ✅ | discovery only |
| Mixkit / Videezy / Videvo / Mazwai | per clip | none | ⛔ manual | Videezy prohibits automation |

#### Geo and data

| Source | Licence | Rule |
|---|---|---|
| Natural Earth | PD | Only unrestricted basemap |
| NASA GIBS | PD | Satellite backgrounds |
| OpenStreetMap | ODbL | Share-alike + attribution |
| GADM | non-commercial | ⛔ block |
| World Bank / OWID | CC-BY 4.0 | Attribution |

### 12.4 Gate order

1. **Licence gate** — reject NC/ND/SA/blocked before any other work.
2. **Scriptability gate** — no scripted fetch of a manual-only source.
3. **Origin verification** — aggregators resolve to the origin page; record the
   licence as seen at the origin, with a timestamp.
4. **Technical gate** — `ffprobe`: resolution, fps, duration, alpha, colour
   space, channels, loudness.
5. **Acceptance gate** — vision model against the L1 acceptance line.
6. **Continuity gate** — grade, light and motion match to the shot.
7. **Cost fit** — cheapest method that passes all of the above.

### 12.5 Attribution pack

`rights-manifest.json` and the review pack carry a ready-to-paste attribution
block: title, creator, source URL, licence name, licence URL, modifications
made, and where it appears in the cut. If any `CC-BY` item is used, the block is
a render-gate requirement, not a nicety.

---

## 13. Processing recipes

Declarative, ordered, idempotent, each op with explicit parameters. No implicit
defaults; an omitted parameter is a validation error.

```json
{
  "task_id": "APT-AS-06",
  "asset_id": "AS-06",
  "ops": [
    {"op": "trim", "in_frame": 0, "out_frame": 120},
    {"op": "stabilise", "strength": 0.3, "crop_pct": 2.0},
    {"op": "conform", "fps": 25, "interp": "nearest"},
    {"op": "speed_ramp", "from": 1.0, "to": 0.35, "curve": "ease_in_out"},
    {"op": "grade", "lut": "bt_warm_counter_v1", "exposure": 0.05},
    {"op": "scale", "width": 1920, "height": 1080, "mode": "cover"},
    {"op": "encode", "codec": "prores_422hq", "pix_fmt": "yuv422p10le"}
  ]
}
```

Allowed ops: `trim`, `crop`, `scale`, `pad`, `conform`, `speed_ramp`,
`stabilise`, `denoise`, `sharpen`, `grade`, `alpha_cutout`, `despill`,
`mask_generate`, `composite`, `text_render`, `loudness_norm`, `resample`,
`channel_map`, `fade`, `encode`.

Validation:

- Every op declares its parameters; unknown ops fail `E_RECIPE_OP`.
- `text_render` must reference a `CP-xx` copy block; text is never inline.
- `grade` must reference a LUT file recorded in the repo, not a vendor preset.
- `alpha_cutout` on an `exact` pack must preserve the label; the mask bounding
  box may not intersect a protected region.
- Audio ops must end at `lufs=-16, true_peak=-1.0` for the master unless the
  brief says otherwise.

---

## 14. Generation specs

Generation is allowed only where Section 8.2 permits, and never for a product,
pack, label, logo or price.

```json
{
  "provider": "fal",
  "model": "…",
  "prompt": "…",
  "negative_prompt": "…",
  "seed": 12345,
  "width": 1080,
  "height": 1920,
  "duration_seconds": 4,
  "reference_images": ["processed/AS-06-still.png"],
  "disclosure_required": true,
  "disclosure_text": "AI-assisted steam simulation",
  "cost_usd": 0.0,
  "budget_line_id": "BL-xxx"
}
```

Rules:

1. `prompt` is versioned; a change creates a new candidate, not an edit.
2. Seed and settings are stored so any output is reproducible.
3. `disclosure_required` is copied from L1 `rights.disclosure_required` and may
   only be escalated, never cleared.
4. Any generated frame that shows the product is rejected automatically.
5. Generation is the **last** resort: capture, procedural and stock are always
   evaluated first.

---

## 15. Flow scheduler

### 15.1 Graph

Nodes: 16 asset tasks + 38 layer decisions + 1 capture session + 6 shot
composites + 2 variant renders. Edges come from `asset.dependencies`, layer
bindings, capture membership and shot membership.

```
AS-02 pack cutout ─┬─▶ SH-01, SH-04, SH-06 comps
AS-01 logo ────────┤
AS-07 plate ───────┤
AS-05 ─▶ AS-06 ─▶ AS-08 ─▶ SH-02/03/05 comps
AS-09 voice ───────┐
AS-10 music ───────┼─▶ audio mix ─▶ captions ─▶ 16:9 master ─▶ VO-01 9:16
AS-11 SFX ─────────┘
```

### 15.2 Batches

| Batch | Contents | Gate |
|---|---|---|
| `B0` | Rights follow-up, capture booking, quotes | Gate 2A |
| `B1` | Pack and logo cutout, range packs | — |
| `B2` | Capture session `CAP-01` + foley | `HI-04` |
| `B3` | Procedural builds: steam, type, plates, end card, ramp | — |
| `B4` | Music, voice, SFX, mix | `HI-03` |
| `B5` | Shot composites, 16:9 master, `VO-01` 9:16 | Gate 2B/2C |

### 15.3 Validation

- Graph must be acyclic (`E_FLOW_CYCLE`).
- Every layer's asset must appear upstream of its shot (`E_FLOW_ORDER`).
- Every task must belong to exactly one batch (`E_FLOW_BATCH`).
- The scheduler reports the critical path; for Blue Tokai it runs through
  `AS-05 → AS-06 → SH-03` and through `HI-04` (capture release), which is why
  `HI-04` is the earliest external blocker to clear.

---

## 16. Build sheet

`build-sheet/manifest.json`:

```json
{
  "schema_version": "2.0",
  "run_id": "rev-002",
  "project_id": "blue-tokai-easy-pour-20s",
  "source_plan_hash": "1370f029…",
  "bundle_hash": "5a67ac5e…",
  "packet_hash": "756d91de…",
  "generated_at": "2026-11-15T…Z",
  "parts": {
    "assets/AS-02.json": {"sha256": "…", "bytes": 1832},
    "shots/SH-01.json": {"sha256": "…", "bytes": 2401},
    "variants/VO-01.json": {"sha256": "…", "bytes": 9821},
    "timeline/timeline.json": {"sha256": "…", "bytes": 14220}
  },
  "counts": {"assets": 16, "layers": 38, "shots": 6, "effects": 6, "variants": 1},
  "budget": {"subtotal_usd": 76.0, "reserve_usd": 11.4, "total_usd": 87.4, "worst_usd": 92.4, "cap_usd": 100.0}
}
```

`assets/AS-02.json`:

```json
{
  "asset_id": "AS-02",
  "truth_class": "exact",
  "impact": "high",
  "method": ["M0"],
  "source": "supplied:brand-pack",
  "processing": [{"op": "alpha_cutout", "preserve_label": true}],
  "output": {"path": "processed/AS-02.png", "sha256": "…", "width": 1800, "height": 1800, "alpha": true},
  "bindings": ["LY-011", "LY-022", "LY-032", "LY-041", "LY-052", "LY-061"],
  "acceptance": "Front title, 'Light to Dark Roasts' and Blue Tokai mark readable at phone scale; no label crop.",
  "probe": null,
  "rights": {"status": "hold", "hold_id": "HI-02"},
  "status": "blocked_rights"
}
```

`shots/SH-01.json` carries layer stack, z-order, transforms, effects, audio,
checks and preview path. `variants/VO-01.json` carries the 38 layer overrides and
4 effect overrides unchanged from the handoff plus resolution status per layer.

---

## 17. Variants

| Property | 16:9 master | `VO-01` 9:16 |
|---|---|---|
| Resolution | 1920×1080 | 1080×1920 |
| Frames | 500 | 500 |
| FPS | 25 | 25 |
| Layers | 38 | 38 overrides |
| Effect overrides | — | 4 |
| Safe area | broadcast | 220 / 320 / 60 / 140 |
| Cost | in project lines | `ES-11`, $6.00 |
| Check | `AC-01`… | `AC-16` (pending) |

Rules:

- Shared source files; per-variant transforms and masks only.
- `VO-01` protected regions must not be violated by any effect mask.
- Safe area is an **operator assumption** until the placement template is
  confirmed; `AC-16` stays `pending` until then and blocks "ready for
  publication", not "ready for assembly".
- Each variant gets its own QC run and its own build-sheet manifest entry.

---

## 18. Sound

| Asset | Method | Plan |
|---|---|---|
| `AS-09` voice | `M0` performer | Warm Indian English, recorded, edited within `ES-02`; release via `HI-03` |
| `AS-10` music | `M1`/`M2` library | 20 s bed edited for the 275 lift and 445 resolve; Content ID check before commit |
| `AS-11` pour SFX | `M0` + foley | Foley from `CAP-01`, layered with a stock pour if needed |
| `AS-12` brand sting | `M0` owned | Trim and loudness-match |
| `AS-15` fallback voice | `M7` TTS | Disclosed; only if `HI-03` fails; unpriced (gap `B-1`) |

Mix target: master `-16 LUFS`, true peak `-1.0 dBTP`, dialogue always intelligible
with music ducked under captions, and a sound-off check because `MH-07` requires
captions to carry the message.

---

## 19. Engines and adapters

```python
class EngineAdapter(Protocol):
    name: str
    def search(self, request: SourceRequest) -> list[Candidate]: ...
    def acquire(self, candidate: Candidate) -> SourceReceipt: ...
    def generate(self, spec: GenerationSpec) -> GenerationResult: ...
    def process(self, recipe: list[Op], source: Path) -> ProcessedAsset: ...
    def probe(self, candidate: Candidate, spec: ProbeSpec) -> ProbeRecord: ...
    def evaluate(self, asset: ProcessedAsset, acceptance: str) -> Evaluation: ...
    def reserve(self, line: BudgetLine) -> Reservation: ...
    def receipt(self, reservation: Reservation) -> Receipt: ...
```

| Adapter | Responsibilities |
|---|---|
| `OpenMontageEngine` | Orchestration, stock routes, ledger, local processing, Remotion/HyperFrames |
| `FalRunwareEngine` | Image/video generation, upscale, depth/segment, Demucs, TTS |
| `LocalEngine` | ffmpeg/ffprobe, Pillow/OpenCV/ImageMagick, whisper, rembg/BRIA, OpenTimelineIO |

The planner only ever calls an adapter. Providers are never imported into
planning modules, which keeps the spend-free slice fully testable with fakes.

Adapter obligations: every call returns a receipt with a hash and a job ID;
every paid call reserves first; every failure releases the reservation.

---

## 20. LLM routing

| Job | Model | Why |
|---|---|---|
| Truth-class and impact derivation | **code only** | Must be deterministic and testable |
| Method selection | DeepSeek | Reasoning over candidates and constraints |
| Processing-recipe planning | DeepSeek | Structured plan, validated by code |
| Budget estimation | DeepSeek + code | Code owns arithmetic |
| Candidate scoring | ChatGPT (vision) | Frames, labels, legibility |
| Probe review | ChatGPT (vision) | Acceptance judgement |
| Prompt refinement | ChatGPT | Language quality |
| Semantic consistency | ChatGPT | Script ↔ beat ↔ caption ↔ pack |
| Independent Gate 2 review | DeepSeek V4 Pro (current), GPT-5.6 Sol when quota allows | Read-only reviewer |

LLM output is always a proposal. Code validates it against the matrix, the
budget, the hash chain and the schema. An LLM can never write a hash or a price.

---

## 21. Review pack and corrections

### 21.1 Review pack

`review-pack.md` and `review-pack.docx`, generated from the build sheet, with:

1. Summary — readiness, budget, blockers, rights, what changed since Level 1.
2. Budget — the table from 11.3, plus quote status.
3. Assets — 16 assets (`AS-01`–`AS-15`, `AS-17`), one block each: status badge, method, source,
   licence, cost, acceptance, preview link, conditional flag.
4. Layers — `LY-010` … `LY-065`: truth class, impact, method, candidates, chosen,
   fallback, probe.
5. Shots — `SH-01` … `SH-06`: layer stack, preview, audio, checks.
6. Variant — `VO-01`: overrides, safe area, `AC-16` status.
7. Compliance — rights manifest, licence gate, attribution block.
8. Corrections — open items and history.
9. Feedback form — one block per item, plus a free-text section.

Every item carries a badge: `ready`, `sourced`, `processed`, `blocked_rights`,
`needs_approval`, `conditional`.

### 21.2 Review item shape

```markdown
### AS-02 · Easy Pour Mixed Bag pack · exact · high
- Method: M0 supplied brand file
- Output: processed/AS-02.png · 1800×1800 · alpha
- Licence: brand advertising licence — **hold `HI-02`**
- Cost: $4.00 (ES-05, operator estimate)
- Acceptance: front title, roast line and mark readable at phone scale; no label crop
- Preview: [view](previews/AS-02.png)
- Decision: ☐ APPROVE  ☐ CHANGE  ☐ REJECT
```

### 21.3 Feedback form

Per item: ID, decision, instruction, reason, approver, date. JSONL companion uses
the same fields so a human can fill the Markdown by hand and the operator can
transcribe without interpretation.

### 21.4 Correction record

```json
{
  "id": "COR-007",
  "item_kind": "asset",
  "item_id": "AS-10",
  "decision": "change",
  "instruction": "Recut the lift 6 frames earlier",
  "reason": "Lift lands after the pack reveal",
  "requested_by": "RahulSoniOneOEight",
  "created_at": "2026-11-15T12:00:00Z",
  "status": "open",
  "affects": ["PR-AS10-01", "BL-ES01"]
}
```

Statuses: `open`, `accepted`, `rejected`, `applied`, `superseded`.

### 21.5 Re-plan loop

```
review → corrections.jsonl → validate decisions → re-plan affected items only
       → re-probe → rebuild build sheet → new run rev-003 → Gate 2 again
```

Rules:

- Corrections never mutate `rev-002`.
- Unaffected items are carried forward with their hashes, so the diff is small
  and reviewable.
- A correction that changes creative intent (copy, shot, variant) is refused and
  routed back to Level 1, because Level 2 may not reopen creative decisions.

---

## 22. Gates

### 22.1 Gate 2A — budget and authorisation

| Check | Pass condition |
|---|---|
| Hash chain | Plan, bundle, packet all match |
| Method matrix | No violation across 38 decisions |
| Class policy | No exact/proof layer on stock or generation |
| Rights posture | Every asset has a hold owner and a path to clearance |
| Catalogue | No NC/ND/SA/blocked item; no manual-only scripting |
| Budget | `total ≤ cap` and `worst ≤ cap`, all lines labelled estimate or quote |
| Probes | Every M2–M7 decision has a probe plan and probe budget |
| Capture | Session, release and shot list ready |

Output: `gate2/packet-2a.json` + human approval record. Only this unlocks spend.

### 22.2 Gate 2B — asset readiness

| Check | Pass condition |
|---|---|
| Coverage | All 13 in-scope assets processed and bound; 3 fallbacks either ready or explicitly conditional |
| Layers | All 38 decisions resolved to a passing asset or procedural render |
| Variants | 16:9 and `VO-01` each resolve all 38 layers |
| Rights | No `needs_approval` item marked ready; `CC-BY` attributions collected |
| QC | Technical, visual and semantic QC recorded |
| Blockers | Zero unresolved blockers for ready shots; `AC-16` status stated |
| Ledger | Every paid call receipted; no orphan reservation |

### 22.3 Gate 2C — rough cut

| Check | Pass condition |
|---|---|
| Duration | 500 frames, 20.0 s, 25 fps, both variants |
| Safe areas | 16:9 and 9:16 both clean |
| Audio | `-16 LUFS`, `-1.0 dBTP`, no clipping, intelligible |
| Captions | Both variants, timed, legible, sound-off message intact |
| Claims | No unapproved price, promotion or claim present |
| Product | Pack, logo and label correct in every appearance |
| Review | Named human sign-off; independent reviewer verdict recorded |

---

## 23. Module layout and CLI

```
src/pinconv2/level2/
  __init__.py
  models.py            contracts, enums, schema versions
  handoff.py           ingestion, hash validation, intent building
  truth.py             truth classification rules R1–R5
  impact.py            impact scoring
  method_selector.py   matrix, yield mapping, escalation
  capture_planner.py   session plan and marginal additions
  catalogue.py         source registry as data
  licence_gate.py      licence, scriptability, origin verification
  recipes.py           processing op models + validation
  generation.py        generation spec models + allowlist
  budget.py            lines, dedupe, reserve, quads, quote lifecycle
  flow_scheduler.py    graph, batches, critical path
  build_sheet.py       builder + manifest + renderers
  review_pack.py       markdown/docx review pack
  corrections.py       typed feedback, diff, re-plan routing
  sound.py             sound plan
  variants.py          VO-01 resolution
  gate2.py             2A/2B/2C packets and guards
  engines/
    base.py
    openmontage.py
    fal_runware.py
    local.py
  llm/
    deepseek.py
    chatgpt.py
    router.py
  agents/
    handoff_validator.py
    classifier.py
    processor.py
    generator.py
    evaluator.py
    scheduler.py
    builder.py
```

CLI:

```
pinconv2 level2 ingest   --project blue-tokai-easy-pour-20s --revision 2
pinconv2 level2 plan     --project … --revision 2 --run rev-002
pinconv2 level2 budget   --run rev-002 --format md|docx|json
pinconv2 level2 review   --run rev-002 --format md|docx
pinconv2 level2 correct  --run rev-002 --input corrections.jsonl
pinconv2 level2 gate     --run rev-002 --gate 2a|2b|2c
pinconv2 level2 build    --run rev-002            # refuses without Gate 2A
```

Every command is dry-run by default and prints the hash of what it would write.

---

## 24. Implementation phases

| Phase | Build | Exit test |
|---|---|---|
| **0** | Freeze interfaces: enums, IDs, schemas, error codes | Models import; `extra="forbid"` rejects unknown fields |
| **1** | `models.py`, `truth.py`, `impact.py` | 38 decisions derive; class counts 10/12/3/7/6; impact counts 18/10/10 |
| **2** | `handoff.py` ingestion + hash validation | Tampered hash → `E_HANDOFF_HASH`; clean load reproduces all hashes |
| **3** | `catalogue.py`, `licence_gate.py` | NC/ND/SA/BBC/GADM blocked; manual-only never scripted; origin verification required |
| **4** | `method_selector.py` | Matrix enforced; every decision has a reason code; escalation never silent |
| **5** | `recipes.py`, `generation.py` | Recipes validate; generation refused for exact/proof |
| **6** | `capture_planner.py`, `sound.py` | One session covers `AS-05/06/08` + foley; `ES-06` charged once |
| **7** | `budget.py` | Dedupe yields 47 + 29 = 76; reserve 11.40; total 87.40; worst 92.40; cap maths pass |
| **8** | `flow_scheduler.py` | Acyclic; every layer upstream of its shot; batches complete; critical path reported |
| **9** | `build_sheet.py` + `review_pack.py` | 16 asset files, 6 shots, `VO-01`, timeline, captions, manifests, review pack, budget docs; **zero spend** |
| **10** | `gate2.py` 2A | Packet 2A produced; build refused before approval |
| **11** | `engines/local.py` | One real ffmpeg process + probe on owned `AS-07`; receipt and hash recorded |
| **12** | `engines/openmontage.py`, `engines/fal_runware.py` | One paid job behind 2A, reservation → receipt → reconcile |
| **13** | `engines/*.probe`, QC, Gate 2B/2C | Probes pass, QC recorded, 2B zero blockers, rough cuts produced |

**First slice = phases 0–10**, spend-free, producing the complete Blue Tokai
build sheet, budget documents and review pack as the acceptance fixture.

---

## 25. Test matrix

| Type | Tests |
|---|---|
| Unit | `R1`–`R5` classification; each impact signal; matrix allow/deny; yield mapping; escalation order; dedupe keys; reserve rounding |
| Property | Hash stability across runs; graph acyclicity for random dependency sets; budget monotonicity under added lines; every layer maps to exactly one decision |
| Fixture | Blue Tokai: 16 intents, 38 decisions, 16 tasks, 6 shots, `VO-01` 38 overrides, budget 76/11.40/87.40/92.40 |
| Negative | `AS-16` absent → no lookup error; NC source blocked; BBC/GADM blocked; manual-only script refused; exact layer with M1 refused; proof layer with M1/M5/M7 refused; generation for `AS-02` refused; paid call before 2A refused; correction mutating `rev-002` refused |
| Golden files | `layer-method-decisions.json`, `budget-estimate.json`, `build-sheet/manifest.json` diffed byte-for-byte |
| Render | Review pack and budget docs render in Markdown and DOCX with matching hashes |
| Integration | Local engine processes `AS-07`, probe passes, receipt written, ledger reconciles |

Target: keep the existing 66 Level 1 tests green and add Level 2 tests per phase;
no phase merges with a failing suite, Ruff issue or mypy error.

---

## 26. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Level 1 revision changes, invalidating the package | Medium | High | Hash gate; any change starts a new `rev-00x` run |
| `HI-04` capture release delays the critical path | High | High | Book capture in `B0`; `AS-13`/`ALT` fallbacks costed |
| Rights not cleared for packs/logo (`HI-02`) | Medium | High | Block readiness, not planning; dossier per asset |
| Aggregator licence drift (Openverse/IA/Wikimedia) | Medium | Medium | Origin verification with timestamp; re-verify at Gate 2B |
| Library music triggers Content ID | Medium | Medium | Pre-clearance check; alternate `AS-14` ready |
| `AC-16` safe-area assumption wrong | Medium | Medium | Confirm placement template before paid media; rebuild `VO-01` only |
| Probe cost exceeds savings on low-impact layers | Low | Low | Probe cap by impact tier |
| Provider pricing or model availability changes | Medium | Medium | Quotes expire in 30 days; adapters isolate providers |
| 9:16 rebuild drifts from 16:9 | Medium | Medium | Shared source assets, per-variant QC, layer-level resolution check |
| Fallbacks unpriced (`B-1`) | High | Low | Require quote or explicit zero at Gate 2A |
| Independent reviewer unavailable (Sol quota) | High | Low | DeepSeek V4 Pro reviews read-only; verdict recorded with model name |

---

## 27. Open decisions and blockers

| ID | Item | Owner | Blocks |
|---|---|---|---|
| `HI-01` | Price and hero pack size | Human | `ED-02`, `ED-03` |
| `HI-02` | Brand pack and logo advertising rights, hi-res masters | Human | `AS-01`, `AS-02`, `AS-03`, `AS-04`, `AS-13`, `AS-17` |
| `HI-03` | Voice and music licences | Human | `AS-09`, `AS-10`, `AS-14`, `AS-15` |
| `HI-04` | Demonstration and talent release | Human | `AS-05`, `AS-06`, `AS-08` |
| `HI-05` | Brand typeface | Human | `CP-01`–`CP-05`, `CP-07`–`CP-13` |
| `PROD-01` | CTA destination and tracking | Human | End card |
| `PL-01` | Vertical placement name and safe-zone template | Human | `AC-16` |
| `B-1` | `AS-15` TTS fallback pricing | Human | Worst-case budget accuracy |
| `B-2` | `AS-14` fallback licence | Human | Worst-case budget accuracy |

None of these blocks the spend-free slice. They block Gate 2B and any paid call.

---

## Appendix A — Asset plan (computed)

| Asset | Name | Route | Class | Method | Cost | Scope | Hold | Fallback |
|---|---|---|---|---|---|---|---|---|
| `AS-01` | Blue Tokai logo | supplied | exact | M0 | 0.00 | approved | `HI-02` | — |
| `AS-02` | Mixed Bag pack | supplied | exact | M0 | 4.00 (`ES-05`) | approved | `HI-02` | `AS-13` |
| `AS-03` | Vienna pack | supplied | exact | M0 | 3.00 (`ES-07`, shared) | approved | `HI-02` | — |
| `AS-04` | Attikan Estate pack | supplied | exact | M0 | — (shared) | approved | `HI-02` | — |
| `AS-17` | Seethargundu Estate pack | supplied | exact | M0 | — (shared) | approved | `HI-02` | — |
| `AS-05` | Demonstration, hands | to_capture | proof | M6 | 18.00 (`ES-06`) | approved | `HI-04` | — |
| `AS-06` | Pour and bloom | to_capture | proof | M6 | — (shared session) | approved | `HI-04` | — |
| `AS-07` | Warm kitchen plate | owned | atmospheric | M0 | 0.00 | approved | cleared | — |
| `AS-08` | Finished cup | to_capture | proof | M6 | — (shared session) | approved | `HI-04` | — |
| `AS-09` | Voice over | to_create | representative | M0 performer | 12.00 (`ES-02`) | approved | `HI-03` | `AS-15` |
| `AS-10` | Music bed | to_source | atmospheric | M1/M2 | 10.00 (`ES-01`) | approved | `HI-03` | `AS-14` |
| `AS-11` | Pour SFX | owned | representative | M0 + foley | 0.00 | approved | cleared | — |
| `AS-12` | Brand sting | owned | atmospheric | M0 | 0.00 | approved | cleared | — |
| `AS-13` | Captured Mixed Bag fallback | to_capture | exact | M6 | 0.00 (5.00 fallback) | conditional | `HI-02`/`HI-04` | — |
| `AS-14` | Music fallback | to_source | atmospheric | M1/M2 | 0.00 | conditional | `HI-03` | — |
| `AS-15` | Synthetic narration fallback | to_generate | representative | M7 | unpriced (`B-1`) | conditional | `HI-03` | — |

Bound layers: `AS-02` → 6 layers, `AS-07` → 6, `AS-05/06/08/03/04/17/01` → 1
each. Unbound: 12 copy layers and 7 procedural layers.

## Appendix B — Layer summary

| Shot | Frames | Layers | Dominant content |
|---|---|---|---|
| `SH-01` | 0–75 | 6 | Plate, pack, steam, headline, plate, caption |
| `SH-02` | 75–160 | 6 | Plate, hands demo, pack, type, plate, caption |
| `SH-03` | 160–275 | 6 | Plate, pour/bloom, pack, type, plate, caption |
| `SH-04` | 275–380 | 8 | Plate, 4 packs, range type, plate, caption |
| `SH-05` | 380–445 | 6 | Plate, finished cup, pack, type, plate, caption |
| `SH-06` | 445–500 | 6 | Plate, pack, logo, CTA, plate, caption |

Layer totals: 38 — 19 asset-bound, 12 copy-bound, 7 procedural. 4 layers carry
effects; 7 layers are protected (all typography plus logo and CTA).

## Appendix C — Effects

| Effect | Name | Behaviour | Shot | Layer | Method |
|---|---|---|---|---|---|
| `FX-01` | `steam_drift` | simulate | `SH-01` | `LY-012` | M4 |
| `FX-02` | `macro_pour` | prove | `SH-03` | `LY-031` | M6 + M2 |
| `FX-03` | `time_lapse` | compress | `SH-03` | `LY-031` | M4 over capture |
| `FX-04` | `range_fan` | reveal | `SH-04` | — (shot-wide) | M4 |
| `FX-05` | `finished_steam` | simulate | `SH-05` | `LY-051` | M4 |
| `FX-06` | `cta_fade` | emphasise | `SH-06` | `LY-063` | M4 |

All six are authored in-house; none require third-party effect media. Effect
masks must not intersect protected product, pack or logo regions; `VO-01`
re-masks four of them for 1080×1920.

## Appendix D — Budget arithmetic

```
direct per-task   = 4.00 + 3.00 + 18.00 + 12.00 + 10.00 = 47.00
project lines     = 15.00 + 5.00 + 3.00                = 23.00
variant lines     = 6.00                                =  6.00
subtotal          = 47.00 + 23.00 + 6.00                = 76.00
reserve 15%       = 76.00 × 0.15                        = 11.40
total             = 76.00 + 11.40                       = 87.40
fallback          = 5.00                                =  5.00
worst             = 87.40 + 5.00                        = 92.40
cap               = 100.00
headroom          = 100.00 − 92.40                       =  7.60
```

## Appendix E — Glossary

| Term | Meaning |
|---|---|
| **Truth class** | How exact a layer must be: `exact`, `exact_text`, `proof`, `representative`, `atmospheric`, `editorial` |
| **Impact** | How much the layer matters: high / medium / low |
| **Method** | How the asset is produced: `M0`–`M8` |
| **Probe** | 2-second sample judged against acceptance before full commit |
| **Dedupe** | Charging a shared acquisition once |
| **Worst case** | Total plus every fallback |
| **Gate 2A** | Budget and authorisation approval |
| **Gate 2B** | Asset readiness approval |
| **Gate 2C** | Rough-cut approval |
| **Conditional task** | Planned but only executed if its trigger fires (`AS-13/14/15`) |
| **Origin verification** | Resolving an aggregator licence at the source institution |

---

*End of plan. Next action: implement phases 0–10 (spend-free) and emit the Blue
Tokai build sheet as the acceptance fixture.*
