# Level 2 test run report — Blue Tokai Easy Pour

**Run:** `rev-002` · plan revision 2
**Project:** `blue-tokai-easy-pour-20s`
**Plan hash:** `1370f029b0b35730625c459cf85579bfd767d2e4a7b62016055e100d15f2aba5`
**Generated:** 2026-11-14T20:56:10+00:00
**Verdict:** PASS — the spend-free Level 2 slice produced the full package; Gate 2A is ready for a human decision.

## Environment

| Tool | Version |
|---|---|
| Python | 3.10.11 |
| pytest | 8.4.2 |
| Ruff | 0.17.4 |
| mypy | 1.20.2 (strict) |
| ffmpeg | 9.0.2 |

## Test suite

```
$ python -m pytest -q
121 passed in 11.02s
```

```
$ python -m ruff check src tests
All checks passed!
```

```
$ python -m mypy
Success: no issues found in 75 source files
```

## Acceptance run — Blue Tokai rev-002

| Item | Result |
|---|---|
| Assets | 16 |
| Layers | 38 |
| Shots | 6 (SH-01 … SH-06) |
| Effects | 6 (FX-01 … FX-06) |
| Variant | `VO-01`, 1080×1920, 500 frames, 38 overrides |
| Stock-sourced assets | 9 library-music candidates, 9 previews, 2 chosen, 0 final acquisitions |
| Truth classes | 10 exact, 12 exact_text, 3 proof, 7 atmospheric, 6 representative |
| Impact | 18 high, 10 medium, 10 low |
| Cash plan | $0.00 (lean) |
| In-kind value | $81.00 |
| Project cap | $2.00 |
| Headroom | $2.00 |
| Retry reserve | $0.00 |

## Gate 2A

**Status:** `ready_for_approval` · 8 pass, 6 warn, 0 fail · blockers: 0

| Check | State | Detail |
|---|---|---|
| G2A-01 Hash chain | pass | plan, bundle, packet and budget reconcile with the approval record |
| G2A-02 Method selection | pass | 38 decisions checked against the class matrix |
| G2A-03 Exact and proof policy | pass | no exact layer uses stock or generation and every proof layer is captured |
| G2A-04 Budget within cap | pass | total $0.00, worst $0.00, cap $2.00, headroom $2.00 |
| G2A-05 Rights posture | warn | 13 assets need written approval; every one names a hold owner |
| G2A-06 Catalogue compliance | pass | 9 candidates checked; 9 passed the licence gate; 9 with previews (9 from sourcing) |
| G2A-07 Probe plan | pass | every M2-M7 choice has a probe before full commit |
| G2A-08 Capture plan | warn | CAP-01 covers 4 assets at $0.00 cash ($18.00 in-kind); release HI-04 is still pending |
| G2A-09 Technical QC | pass | 3 findings, verdict pass |
| G2A-10 Semantic QC | warn | 1 findings, verdict warn |
| G2A-11 Rights QC | warn | 1 findings, verdict warn |
| G2A-12 Budget QC | warn | 4 findings, verdict warn |
| G2A-13 Lean substitutions | warn | 10 paid lines moved to in-kind ($81.00); cash is $0.00 and Gate 2A approves these substitutions |
| G2A-14 Provider budget | pass | fal+Runware cap $2.00, spent $0.00, committed $0.00, remaining $2.00, per-job max $0.50 |

## fal.ai + Runware governance

| Item | Value |
|---|---|
| Shared cap | $2.00 |
| Per-job maximum | $0.50 |
| Spent | $0.00 |
| Committed | $0.00 |
| Remaining | $2.00 |
| Calls | 0 |

No provider call was made. A call needs an approved Gate 2A, a live provider key
and a positive quote within the per-job maximum.

## What is not done

- No sourcing, generation, capture or render has run; the plan is spend-free.
- Gate 2A is `ready_for_approval`; only a named human can approve it.
- `AC-16` (9:16 safe area) is pending.
- External holds `HI-01`–`HI-05` remain open.

## Raw command outputs

- `pytest-output.txt`
- `ruff-output.txt`
- `mypy-output.txt`
- `cli-plan-output.json`
- `cli-spend-output.json`
- `cli-qc-output.json`
- `cli-gate2a-output.json`
