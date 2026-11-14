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

## Verified numbers (re-derived, not trusted)

| Claim | Result |
|---|---|
| Assets / layers / shots / effects | 16 / 38 / 6 / 6 |
| `VO-01` | 1080×1920, 25 fps, 500 frames, 38 overrides, 4 effect masks |
| Truth classes | 10 exact, 12 exact_text, 3 proof, 7 atmospheric, 6 representative |
| Impact | 18 high, 10 medium, 10 low |
| Budget | 76.00 subtotal, 11.40 reserve, 87.40 total, 5.00 fallback, 92.40 worst, 100.00 cap, 7.60 headroom |
| Dedupe | raw 89.00 → 42.00 saved → 47.00 direct + 29.00 project/variant |
| Capture | one session, `ES-06` charged once, covers `AS-05/06/08/13` |
| Gates | 2A `ready_for_approval`, no blockers; 2B and build refuse before approval |
| Spend | no reservation, no receipt, `spent_usd = 0.00` |

## Final verdict

**PASS.** No blockers or open findings remain. The spend-free Level 2 slice is
implemented, the Blue Tokai case produces the full artifact set, and every spend
path is still behind a named human Gate 2A approval.

## Evidence

```
python -m pytest -q          → 112 passed at review time
python -m ruff check src tests → All checks passed!
python -m mypy               → Success: no issues found in 72 source files
pinconv2 level2 plan ...     → state quoted, gate 2a ready_for_approval
pinconv2 level2 gate --gate 2b → error: Gate 2A is not approved (exit 2)
pinconv2 level2 build        → error: Gate 2A is not approved (exit 2)
```

Post-review, one additional test was added for the local rough-cut assembler;
the final suite is 113 passing tests with the same Ruff and mypy results.

## Limits

- No sourcing round, generation, capture or render has run; the plan is
  spend-free by design.
- `AC-16` (9:16 safe area) remains pending, so `VO-01` is ready for review, not
  for publication.
- Gate 2A is `ready_for_approval`; only a named human can approve it.
