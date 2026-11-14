# Independent QC record — Level 2 implementation

**Reviewer:** DeepSeek V4 Pro (separate review context, read-only)
**Date:** 2026-11-15
**Repository:** `D:\pinconv2`
**Project:** `blue-tokai-easy-pour-20s`, approved revision 2, variant `VO-01`
**Scope:** Level 2 implementation against `docs/level2-implementation-plan.md`,
the Blue Tokai acceptance run under `projects/blue-tokai-easy-pour-20s/level2/runs/rev-002/`,
the test suite and the toolchain.

## Process

The reviewer read the plan, the Level 2 source and the generated artifacts,
re-derived the acceptance numbers from `plans/rev-002.json`, ran the test suite,
Ruff and mypy, and checked the gates and spend guards. It did not modify files,
approve a gate or call a paid provider. Three rounds were run: an adversarial
review, a closure review after fixes, and a final confirmation of the residuals.

## Round 1 — FAIL

Two blockers and ten further findings:

| ID | Severity | Finding |
|---|---|---|
| F1 | blocker | `VO-01` build-sheet variant dropped the actual layer and effect override geometry, so the vertical cut could not be reconstructed. |
| F2 | blocker | Gate 2A reported `pass` on vacuous checks: hash chain hardcoded, method check only tested enum membership, catalogue check had nothing to inspect. |
| F3 | high | The licence gate existed but no runtime path called it; engines returned ungated candidates. |
| F4 | medium | The exact/proof policy check ignored proof layers entirely. |
| F5 | medium | Two ledger formats (`spend-ledger.json` and `.jsonl`), so Gate 2B always read the empty placeholder. |
| F6 | medium | `feedback-form.md` and `catalogue-resolutions.json` were missing; the correction loop only wrote a file into a new directory. |
| F7 | medium | The review pack asserted licence compliance that had not been checked. |
| F8 | low | Asset and capture nodes had zero duration, so the reported critical path was misleading. |
| F9 | low | `run_build` created an authorised ledger that no engine used. |
| F10 | low | Budget asset membership was hardcoded instead of derived from the plan. |
| F11 | low | The plan's matrix said "exact → M0/M4" while the approved plan captures `AS-13` with M6; undocumented inconsistency. |
| F12 | low | The seven `agents/` classes were exported but never used. |

## Fixes applied

- **F1** `VariantPackage` now carries `layer_overrides` and `effect_masks`, copied
  unchanged from the handoff; the build-sheet variant round-trips
  `rect`, `motion`, `text_style`, `protected`, `protected_regions`,
  `mask_region` and `intensity`.
- **F2/F4** Gate 2A now compares the recomputed plan hash with the build sheet,
  compares the bundle and packet hashes with the approval record, checks every
  method **and fallback** against the class matrix, enforces the proof policy
  (`M6`/`M2` only), requires budget equality, fails when a needs-approval asset
  has no hold, and reports `WARN` when no sourcing round has run.
- **F3** `OpenMontageEngine.search` gates every candidate; `acquire` refuses any
  candidate that is not `PASS` (including `HOLD`); generated media must declare
  disclosure.
- **F5** `spend-ledger.jsonl` is the canonical ledger; `spend-ledger.json` is a
  computed view; Gate 2B reads the ledger class; `run_build` refreshes the view.
- **F6** `feedback-form.md`, `catalogue-resolutions.json` and
  `level2 correct --apply` now exist. Corrections are validated, the base run is
  checked, a new run is built, and the accepted corrections are carried into the
  build sheet and hash-bound in `build-sheet/corrections.json`.
- **F7** The review pack now states that sourcing has not run and that candidate
  licences are unverified.
- **F8** Flow nodes carry nominal durations; the computed path is
  `CAP-01 → AS-05 → AS-06 → AS-08 → SH-05 → VO-01`.
- **F9** `run_build` no longer creates an authorised ledger.
- **F10** Budget membership is derived from `plan.assets` by `estimate_id`.
- **F11** The plan documents exact-original capture, disclosed representative
  `M7`, the gate order, the budget dedupe and the computed critical path.
- **F12** The planner uses `HandoffValidator`, `AssetClassifier`,
  `ProcessingPlanner`, `GenerationPlanner`, `FlowScheduler` and
  `BuildSheetBuilder`.

## Round 2 — PASS

All twelve findings closed. Two residuals remained:

1. `G2A-01` checked bundle/packet length only, while its wording implied a
   content comparison.
2. The `spend-ledger.json` view was a plan-time snapshot and could drift after
   spend.

## Round 3 — PASS

The five residual fixes were confirmed:

| Fix | Status | Evidence |
|---|---|---|
| Gate 2A compares bundle/packet to the approval record; `WARN` when absent | closed | `gate2.py:66-98`, `planner.py:393-401`; `packet-2a.json` G2A-01 `pass` |
| `run_build` refreshes the ledger view | closed | `build.py:143-153` |
| `apply_corrections` requires an existing base run with a matching plan hash | closed | `planner.py:445-449` |
| Dead `neutralise` removed | closed | no matches in `src/` |
| Corrections hash-bound in `build-sheet/corrections.json` | closed | `store.py:131-137` |

## Round 4 — budget guardrail ($2) — PASS with one finding

After the user set a **$2.00** project cap, the guardrail was re-reviewed:

- effective cap = `min(approved_cap, operator_cap)`, so a request above the
  approved $100 cannot raise the ceiling;
- `--cap 2` without lean mode blocks: total $87.40, worst $92.40, cap $2.00,
  Gate 2A fails `G2A-04`;
- `--cap 2 --lean` gives $0.00 cash, $81.00 in-kind, cap $2.00, headroom
  $2.00, 10 substitutions, capture $0 cash / $18 in-kind, unchanged layer
  methods, run `quoted`, Gate 2A `ready_for_approval` with `G2A-13` warn.

One medium finding: the review pack's per-asset and variant cost lines still
showed the original cash estimates in lean mode, contradicting the $0.00 cash
summary.

## Round 5 — PASS

The review pack now renders lean cost as `$0.00 cash · $X in-kind` for every
asset and for `VO-01`, in both Markdown and DOCX; non-lean runs still show plain
cash. A final label nit (supplied assets showing "fallback, unpriced") was also
removed. No medium or high findings remain.

## Round 6 — provider spend governance — PASS

The user clarified that the $2 covers **fal.ai + Runware production calls**.
`ProviderGovernor` was reviewed:

- authorisation comes from an approved Gate 2A packet object, not a boolean;
- only fal and runware are allowed; the cap is shared;
- every call is quoted, checked against the per-job maximum ($0.50) and the
  remaining shared cap ($2.00), reserved, receipted or released;
- the remaining arithmetic is `cap - spent - open reservations`, enforced by
  the summary validator;
- Gate 2A `G2A-14` shows cap/spent/committed/remaining/per-job and fails if the
  ledger is over cap;
- the provider cap cannot exceed the project cap, and the project cap cannot
  exceed the approved $100.

Two low findings: no idempotency guard on receipt/release, and a hand-built
Gate 2A object could be passed to the constructor (the canonical
`open_governor` reads the packet from disk).

## Round 7 — PASS

The idempotency guard now rejects a second receipt or release for the same
reservation, and the gate-object trust is documented as a defence-in-depth
boundary: production paths use `open_governor`, which reads
`gate2/packet-2a.json`, and a live provider key is still required. The $2 cap
cannot be exceeded through the governor API.

## Round 8 — sourcing discovery — PASS

The user correctly challenged that no assets had been sourced. The cause was
twofold: the spend-free slice stopped at Gate 2A, and no sourcing runner had
been implemented. A runner now exists and a real discovery round ran.

- ccMixter searched with `lic=by`; NC/ND/SA and vocal tracks filtered.
- 9 candidates for the two stock-routed music assets: 4 for `AS-10`, 5 for
  `AS-14`; all `CC-BY 3.0`, all licence gate `pass`.
- Nine 20-second previews downloaded (about 2.1 MB total) and probed.
- Distinct choices: `AS-10` "Lost Roamin'" by speck; `AS-14` "This Is Our
  Music - Instrumental" by gabriel_shelligton.
- Build-sheet sources and the rights manifest carry the chosen titles, CC BY
  3.0 attributions and source URLs.
- Gate 2A `G2A-06` passes with "9 candidates checked; 9 passed the licence
  gate; 9 with previews".

One medium finding: only the top three candidates per asset were previewed
while the gate text implied all nine. Fixed by previewing all nine before the
final pass. Nothing was acquired into `sourced/`, and no money was spent.

## Verified numbers (re-derived, not trusted)

| Claim | Result |
|---|---|
| Assets / layers / shots / effects | 16 / 38 / 6 / 6 |
| `VO-01` | 1080×1920, 25 fps, 500 frames, 38 overrides, 4 effect masks |
| Truth classes | 10 exact, 12 exact_text, 3 proof, 7 atmospheric, 6 representative |
| Impact | 18 high, 10 medium, 10 low |
| Budget at approved cap | 76.00 subtotal, 11.40 reserve, 87.40 total, 5.00 fallback, 92.40 worst, 100.00 cap, 7.60 headroom |
| Budget at $2 operator cap | 0.00 cash, 0.00 worst, 2.00 cap, 2.00 headroom, 81.00 in-kind, 10 substitutions |
| Dedupe | raw 89.00 → 42.00 saved → 47.00 direct + 29.00 project/variant |
| Capture | one session, `ES-06` charged once; lean run $0 cash / $18 in-kind |
| Gates | 2A `ready_for_approval`, no blockers; 2B and build refuse before approval |
| Provider budget | fal+Runware cap 2.00, per-job 0.50, spent 0.00, remaining 2.00 |
| Stock sourcing | 9 CC BY candidates, 9 previews, 2 chosen, 0 final acquisitions |
| Spend | no reservation, no receipt, `spent_usd = 0.00` |

## Final verdict

**PASS.** No blockers or open findings remain. The spend-free Level 2 slice is
implemented, the Blue Tokai case produces the full artifact set, and every spend
path is still behind a named human Gate 2A approval.

## Evidence

```
python -m pytest -q          → 121 passed
python -m ruff check src tests → All checks passed!
python -m mypy               → Success: no issues found in 72 source files
pinconv2 level2 plan ... --cap 2 --lean --provider-cap 2 --per-job-cap 0.5
                             → lean $0.00 cash, provider remaining $2.00, gate 2a ready
pinconv2 level2 spend ...    → cap $2.00, spent $0.00, remaining $2.00
pinconv2 level2 gate --gate 2b → error: Gate 2A is not approved (exit 2)
pinconv2 level2 build        → error: Gate 2A is not approved (exit 2)
```

## Limits

- The canonical run is the **$2 lean run**: $0.00 cash, $81.00 in-kind. The
  approved-cap estimate ($87.40) remains reproducible with
  `level2 plan --cap 100`.
- Lean substitutions (self-operated capture, in-house edit, library music) need
  Gate 2A approval; they are listed individually in the review pack.
- Nine library-music candidates were discovered and previewed; nothing has
  been acquired into `sourced/`, so the chosen tracks still need Gate 2A and the
  final licence confirmation.
- No fal.ai or Runware call has been made. The full $2.00 provider cap remains
  available; a call needs an approved Gate 2A, a live provider key and a
  positive quote within the $0.50 per-job maximum.
- No sourcing round, generation, capture or render has run; the plan is
  spend-free by design.
- `AC-16` (9:16 safe area) remains pending, so `VO-01` is ready for review, not
  for publication.
- Gate 2A is `ready_for_approval`; only a named human can approve it.
