# Independent QC record — Blue Tokai Easy Pour

**Reviewer:** GPT-5.6 Sol (separate review context, read-only)
**Repository:** `https://github.com/RahulSoniOneOEight/PinConv2`
**Project:** `blue-tokai-easy-pour-20s`
**Scope:** Level 1 research, Concept Note, Production Plan, Shot × Layer × Asset
detail, Gate 1 packet and the human-readable Word outcome.

## Process

Sol reviewed the source JSON, validators, gate packet and Word document against
`docs/level1-detail-standard.md`, the user brief and current YouTube creative
guidance. It did not modify tracked files and did not infer approval.

## Round 1 — FAIL

The first review raised:

- **B1** — shot, layer and asset records still required invention: missing lens
  intent, handles, effect specifications, dependencies and acceptance criteria.
- **B2** — proposed copy was labelled `approved_copy`; the document called
  “Shop Easy Pour” approved although `ED-04` was pending.
- **H1** — the demo compressed the steep but not the repeated pours.
- **H2** — the “light to dark” fan had no light-roast pack.
- **H3** — rights states contradicted the Gate holds.
- **H4** — no single canonical audio script.
- **H5** — several alternates were not executable.
- **H6** — no per-placement delivery contract.
- **H7** — Word/JSON fidelity and readiness overclaim.
- **M1–M4** — concept completeness, research narrowness, provisional budget and
  caption terminology.
- **Low** — no contents page and stale metadata.

## Corrections after Round 1

- Added lens intent, editorial handles, shot acceptance, shot audio links,
  rights-readiness and production-readiness fields.
- Added layer effect specifications, anchors, rotation and acceptance fields.
- Added asset dependencies and acceptance-on-receipt fields.
- Changed all copy-layer exactness to `proposed_copy`.
- Added `ED-01`, `ED-04` and `ED-05` as explicit pending identifiers in Word.
- Added Seethargundu as the light endpoint: four-pack fan, new `AS-17`.
- Changed the demo to compress the repeated pours and steep, with
  “Brew sequence compressed.”
- Corrected future-capture rights to `needs_approval`.
- Added a canonical script and line windows to the VO cue.
- Added switch authorities to alternates and preserved the four-pack proof.
- Added placement, delivery, colour, caption and loudness fields.
- Added concept success, viewing context, references, reverse evidence,
  prohibited content and canonical script.
- Added contents, current metadata, pending exact identifiers and the planning
  estimate to Word.

## Round 2 — FAIL

The second review confirmed B2 and M4 were resolved, but found propagation and
consistency gaps:

- four-pack language still conflicted with three-pack research, concept and
  fallback text;
- `fallback_required` was still true on assets without fallbacks;
- SH-04 fallback dropped the light endpoint;
- BT-02/BT-03 did not match the canonical script;
- `AS-06` recorded 25 fps while instructing 50 fps capture;
- `AS-15` said 15 seconds but recorded 470 frames;
- `AC-08` omitted `CL-07` and `HI-05` did not cover every copy block;
- all shots were `ready` without a separate rights state;
- Word reproduced the three/four-pack contradiction.

## Corrections after Round 2

- Propagated Seethargundu through research, concept, beat, shot, method,
  fallback and Word.
- Changed research and decision language to “repeated pours and steep” and
  “Brew sequence compressed.”
- Set every asset without a fallback to `fallback_required: false`.
- Restored the four-pack proof in the SH-04 fallback.
- Aligned BT-02 with “Tear, anchor, pour” and BT-03 with “Just a mug and hot
  water.”
- Set `AS-06` source capture to 50 fps with a 25 fps conform note.
- Set synthetic VO to 20 seconds / 500 frames and removed “approved script”
  language.
- Added `CL-07` to `AC-08`; `HI-05` now covers all twelve copy blocks.
- Added `rights_readiness: pending` and `production_ready: false` to every shot.
- Added quality gates for audio links, fallback coverage and rights readiness.
- Updated Word phrase “executable as a brief” to “reviewable as a brief;
  production remains gated.”
- Removed “three-pack” and “Brew time compressed” strings from the final
  records.

## Final local verification

| Check | Evidence |
|---|---|
| Tests | `62 passed` |
| Lint / typing | Ruff clean; mypy clean on 27 source files |
| Pipeline | `run-all` reaches `gate1_ready` |
| Plan | revision 2, 6 shots, 38 layers, 16 assets |
| Validation | 0 failures, 14 warnings |
| Critique | 0 findings |
| Gate blockers | none |
| Exact data | `ED-01`, `ED-04`, `ED-05` pending; no approval record |
| Rights state | all shots plan-ready, rights pending, production not cleared |
| Fallbacks | no `fallback_required` asset without a fallback |
| Audio | every shot has audio IDs; canonical script aligned |
| Four-pack proof | `AS-17` / `LY-047` present; Document says Seethargundu |
| Word | hashes, counts and pending identifiers match the JSON |

## Third independent pass — DeepSeek Pro, FAIL

The user authorised DeepSeek V4 Pro after the GPT-5.6 Sol quota remained
unavailable. The Round 3 read-only review found two HIGH contradictions:

- the canonical VO script still placed “Just a mug and hot water” before
  “Tear, anchor, pour” while beats BT-02/BT-03 used the reverse;
- the SH-04 pack fan placed Vienna and Attikan left of Seethargundu, reversing
  the “LIGHT TO DARK” reading.

It also found eight low-severity traceability and wording issues.

### Corrections after Round 3

- Canonical script, AS-09, AU-01 and Word now read: “Specialty coffee. Tear,
  anchor, pour. Just a mug and hot water. Light to dark. One mug. One cup. Shop
  Easy Pour.”
- SH-04 now reads left to right: Mixed Bag, Seethargundu, Attikan, Vienna.
- CP-10 names all four packs.
- MH-08 no longer implies the pending identifiers are approved.
- DC-04 no longer references the v1-only CP-06.
- Gate input statuses cover every critique finding.
- Research synthesis, source reliability and CL-07 locator corrected.
- Beats now carry asset IDs; AU-01 carries per-line windows and performance
  direction.
- Word heading changed to “GATE 1 REVIEW CANDIDATE”.

## Fourth independent pass — DeepSeek Pro, PASS WITH CONDITIONS

Round 4 re-review of plan revision 2 (hash `deb1119b…`) confirmed every Round 3
finding resolved and introduced no new contradiction. The review verified the
canonical script/beat parity, four-pack geometry, pending exact data, rights
states, fallback coverage, frame rates, Word/JSON fidelity and the Gate
boundary.

**Remaining conditions are the recorded Level 1 holds, not open plan defects:**
`ED-01`, `ED-04` and `ED-05` require named-human approval; `HI-01`–`HI-05`
require brand, rights, talent, music and typeface evidence. No approval is
recorded and no render, sourcing purchase or publication is authorised.

## Final verdict

**PASS WITH CONDITIONS** — the package is reviewable as a brief and executable
without inventing a decision. It is not production clearance.

**Current status:** Gate 1 review candidate — named human approval pending.

## Boundary

**Gate 1 approval is not recorded.** The packet has `approval: null`, the three
exact identifiers are pending, and five rights/approval holds remain. No render,
sourcing purchase or publication is authorised.
