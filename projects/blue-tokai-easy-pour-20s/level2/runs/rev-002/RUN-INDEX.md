# Blue Tokai Level 2 — run index

**Run:** `rev-002` · **Plan revision:** 2
**Status:** Gate 2A `ready_for_approval` · cash $0.00 · in-kind $81.00
**Plan hash:** `1370f029b0b35730625c459cf85579bfd767d2e4a7b62016055e100d15f2aba5`

## Start here

| Document | What it is |
|---|---|
| [REVIEW-GUIDE.md](REVIEW-GUIDE.md) | How a human reviews the pack, records corrections and approves Gate 2A |
| [SOURCE-SHEET.md](SOURCE-SHEET.md) | Every shot/layer with its actual asset source and preview |
| [stock-check/stock-check.md](stock-check/stock-check.md) | Live fetch result per stock source, with licences |
| [openmontage-status.json](openmontage-status.json) | OpenMontage account, version and connected providers |
| [openmontage-check.json](openmontage-check.json) | Real NASA stock acquisition and 2-second HyperFrames render |
| [openmontage/render.mp4](openmontage/render.mp4) | Rendered test clip (1920?1080, 2 s, 60 frames) |
| [shortgpt-status.json](shortgpt-status.json) | Edge TTS working; transcription explicitly unavailable |
| [voice-sample.json](voice-sample.json) | ShortGPT Edge TTS fallback sample metadata |
| [TEST-REPORT.md](TEST-REPORT.md) | Test results, gate checks, environment, raw output links |
| [review-pack.html](review-pack.html) | Review pack that opens in any browser |
| [review-pack.md](review-pack.md) | Human review pack: every asset, layer, shot, variant, cost |
| [review-pack.docx](review-pack.docx) | Standard Word version of the review pack |
| [budget-estimate.html](budget-estimate.html) | Budget that opens in any browser |
| [budget-estimate.md](budget-estimate.md) | Budget, lean substitutions, provider cap |
| [budget-estimate.docx](budget-estimate.docx) | Standard Word budget |
| [build-sheet/production-build-sheet.html](build-sheet/production-build-sheet.html) | Build sheet that opens in any browser |
| [build-sheet/production-build-sheet.md](build-sheet/production-build-sheet.md) | Ready-to-assemble build sheet |
| [sourcing-report.md](sourcing-report.md) | 9 library-music candidates, licences and chosen previews |
| [asset-sourcing.json](asset-sourcing.json) | Machine-readable sourcing record |
| [build-sheet/manifest.json](build-sheet/manifest.json) | Hashes of every build-sheet part |
| [gate2/packet-2a.json](gate2/packet-2a.json) | Gate 2A packet and checks |
| [provider-spend.json](provider-spend.json) | fal.ai + Runware cap and remaining |
| [feedback-form.md](feedback-form.md) | Fill-in review form |
| [blockers.json](blockers.json) | Open external holds |

## Key decisions

- 16 assets, 38 layers, 6 shots, 6 effects, 1 variant (`VO-01`).
- 9 library-music candidates found; `AS-10` and `AS-14` have chosen CC BY previews, not yet acquired.
- Every exact/proof layer is supplied or captured; no stock or generation for product, pack or logo.
- Cash $0.00; $81.00 in-kind across 10 substitutions; provider cap $2.00 with $2.00 remaining.
- Gate 2A has 8 passes, 6 warnings, 0 failures and 0 blockers.

## Files

| File | Bytes |
|---|---|
| [asset-intents.json](asset-intents.json) | 10,867 |
| [asset-production-tasks.json](asset-production-tasks.json) | 19,299 |
| [asset-sourcing.json](asset-sourcing.json) | 7,670 |
| [blockers.json](blockers.json) | 500 |
| [budget-estimate.docx](budget-estimate.docx) | 37,450 |
| [budget-estimate.html](budget-estimate.html) | 4,771 |
| [budget-estimate.json](budget-estimate.json) | 9,354 |
| [budget-estimate.md](budget-estimate.md) | 3,108 |
| [budget-policy.json](budget-policy.json) | 261 |
| [build-sheet/assets/AS-01.json](build-sheet/assets/AS-01.json) | 720 |
| [build-sheet/assets/AS-02.json](build-sheet/assets/AS-02.json) | 772 |
| [build-sheet/assets/AS-03.json](build-sheet/assets/AS-03.json) | 667 |
| [build-sheet/assets/AS-04.json](build-sheet/assets/AS-04.json) | 640 |
| [build-sheet/assets/AS-05.json](build-sheet/assets/AS-05.json) | 646 |
| [build-sheet/assets/AS-06.json](build-sheet/assets/AS-06.json) | 670 |
| [build-sheet/assets/AS-07.json](build-sheet/assets/AS-07.json) | 607 |
| [build-sheet/assets/AS-08.json](build-sheet/assets/AS-08.json) | 636 |
| [build-sheet/assets/AS-09.json](build-sheet/assets/AS-09.json) | 639 |
| [build-sheet/assets/AS-10.json](build-sheet/assets/AS-10.json) | 626 |
| [build-sheet/assets/AS-11.json](build-sheet/assets/AS-11.json) | 551 |
| [build-sheet/assets/AS-12.json](build-sheet/assets/AS-12.json) | 531 |
| [build-sheet/assets/AS-13.json](build-sheet/assets/AS-13.json) | 629 |
| [build-sheet/assets/AS-14.json](build-sheet/assets/AS-14.json) | 634 |
| [build-sheet/assets/AS-15.json](build-sheet/assets/AS-15.json) | 672 |
| [build-sheet/assets/AS-17.json](build-sheet/assets/AS-17.json) | 658 |
| [build-sheet/build-sheet.json](build-sheet/build-sheet.json) | 71,270 |
| [build-sheet/captions/captions-16x9.srt](build-sheet/captions/captions-16x9.srt) | 374 |
| [build-sheet/captions/captions-9x16.srt](build-sheet/captions/captions-9x16.srt) | 374 |
| [build-sheet/manifest.json](build-sheet/manifest.json) | 4,890 |
| [build-sheet/previews/16x9/SH-01.svg](build-sheet/previews/16x9/SH-01.svg) | 1,376 |
| [build-sheet/previews/16x9/SH-02.svg](build-sheet/previews/16x9/SH-02.svg) | 1,359 |
| [build-sheet/previews/16x9/SH-03.svg](build-sheet/previews/16x9/SH-03.svg) | 1,365 |
| [build-sheet/previews/16x9/SH-04.svg](build-sheet/previews/16x9/SH-04.svg) | 1,568 |
| [build-sheet/previews/16x9/SH-05.svg](build-sheet/previews/16x9/SH-05.svg) | 1,377 |
| [build-sheet/previews/16x9/SH-06.svg](build-sheet/previews/16x9/SH-06.svg) | 1,478 |
| [build-sheet/previews/9x16/SH-01.svg](build-sheet/previews/9x16/SH-01.svg) | 1,369 |
| [build-sheet/previews/9x16/SH-02.svg](build-sheet/previews/9x16/SH-02.svg) | 1,354 |
| [build-sheet/previews/9x16/SH-03.svg](build-sheet/previews/9x16/SH-03.svg) | 1,361 |
| [build-sheet/previews/9x16/SH-04.svg](build-sheet/previews/9x16/SH-04.svg) | 1,563 |
| [build-sheet/previews/9x16/SH-05.svg](build-sheet/previews/9x16/SH-05.svg) | 1,374 |
| [build-sheet/previews/9x16/SH-06.svg](build-sheet/previews/9x16/SH-06.svg) | 1,479 |
| [build-sheet/production-build-sheet.docx](build-sheet/production-build-sheet.docx) | 37,295 |
| [build-sheet/production-build-sheet.html](build-sheet/production-build-sheet.html) | 15,055 |
| [build-sheet/production-build-sheet.md](build-sheet/production-build-sheet.md) | 10,495 |
| [build-sheet/shots/SH-01.json](build-sheet/shots/SH-01.json) | 2,157 |
| [build-sheet/shots/SH-02.json](build-sheet/shots/SH-02.json) | 2,188 |
| [build-sheet/shots/SH-03.json](build-sheet/shots/SH-03.json) | 2,230 |
| [build-sheet/shots/SH-04.json](build-sheet/shots/SH-04.json) | 2,801 |
| [build-sheet/shots/SH-05.json](build-sheet/shots/SH-05.json) | 2,238 |
| [build-sheet/shots/SH-06.json](build-sheet/shots/SH-06.json) | 2,218 |
| [build-sheet/timeline/timeline.json](build-sheet/timeline/timeline.json) | 9,332 |
| [build-sheet/variants/VO-01.json](build-sheet/variants/VO-01.json) | 23,160 |
| [capture-plan.json](capture-plan.json) | 1,480 |
| [catalogue-resolutions.json](catalogue-resolutions.json) | 4,587 |
| [cli-gate2a-output.json](cli-gate2a-output.json) | 1,873 |
| [cli-plan-output.json](cli-plan-output.json) | 1,033 |
| [cli-qc-output.json](cli-qc-output.json) | 631 |
| [cli-spend-output.json](cli-spend-output.json) | 720 |
| [cli-stockcheck-output.json](cli-stockcheck-output.json) | 245 |
| [cli-voice-output.json](cli-voice-output.json) | 345 |
| [events.jsonl](events.jsonl) | 9,558 |
| [feedback-form.md](feedback-form.md) | 4,580 |
| [flow.json](flow.json) | 5,774 |
| [gate2/packet-2a.json](gate2/packet-2a.json) | 3,229 |
| [generated/AS-15-edge-sample.mp3](generated/AS-15-edge-sample.mp3) | 89,712 |
| [layer-method-decisions.json](layer-method-decisions.json) | 25,090 |
| [licence-gate-report.json](licence-gate-report.json) | 4,768 |
| [mypy-output.txt](mypy-output.txt) | 46 |
| [OPEN-TOOLS-STATUS.md](OPEN-TOOLS-STATUS.md) | 8,161 |
| [openmontage/nasa-stock.jpg](openmontage/nasa-stock.jpg) | 103,961 |
| [openmontage/render.mp4](openmontage/render.mp4) | 26,984 |
| [openmontage-check.json](openmontage-check.json) | 1,020 |
| [openmontage-status.json](openmontage-status.json) | 904 |
| [provider-budget.json](provider-budget.json) | 283 |
| [provider-spend.json](provider-spend.json) | 468 |
| [provider-spend.jsonl](provider-spend.jsonl) | 0 |
| [pytest-output.txt](pytest-output.txt) | 187 |
| [qc/budget.json](qc/budget.json) | 1,110 |
| [qc/rights.json](qc/rights.json) | 464 |
| [qc/semantic.json](qc/semantic.json) | 407 |
| [qc/technical.json](qc/technical.json) | 780 |
| [qc/visual.json](qc/visual.json) | 423 |
| [REVIEW-GUIDE.md](REVIEW-GUIDE.md) | 8,328 |
| [review-pack.docx](review-pack.docx) | 39,142 |
| [review-pack.html](review-pack.html) | 23,358 |
| [review-pack.md](review-pack.md) | 16,094 |
| [rights-manifest.json](rights-manifest.json) | 4,932 |
| [ruff-output.txt](ruff-output.txt) | 21 |
| [run.json](run.json) | 117,646 |
| [shortgpt-status.json](shortgpt-status.json) | 253 |
| [sound-plan.json](sound-plan.json) | 2,757 |
| [SOURCE-SHEET.html](SOURCE-SHEET.html) | 13,284 |
| [SOURCE-SHEET.json](SOURCE-SHEET.json) | 18,224 |
| [SOURCE-SHEET.md](SOURCE-SHEET.md) | 8,565 |
| [sourcing/CND-AS10-02-lost-roamin.mp3](sourcing/CND-AS10-02-lost-roamin.mp3) | 241,063 |
| [sourcing/CND-AS10-03-this-is-our-music-instrumental.mp3](sourcing/CND-AS10-03-this-is-our-music-instrumental.mp3) | 241,134 |
| [sourcing/CND-AS10-04-roman-song.mp3](sourcing/CND-AS10-04-roman-song.mp3) | 241,089 |
| [sourcing/CND-AS10-05-passing-through.mp3](sourcing/CND-AS10-05-passing-through.mp3) | 241,079 |
| [sourcing/CND-AS14-01-lost-roamin.mp3](sourcing/CND-AS14-01-lost-roamin.mp3) | 241,063 |
| [sourcing/CND-AS14-02-this-is-our-music-instrumental.mp3](sourcing/CND-AS14-02-this-is-our-music-instrumental.mp3) | 241,134 |
| [sourcing/CND-AS14-03-roman-song.mp3](sourcing/CND-AS14-03-roman-song.mp3) | 241,089 |
| [sourcing/CND-AS14-04-passing-through.mp3](sourcing/CND-AS14-04-passing-through.mp3) | 241,079 |
| [sourcing/CND-AS14-05-safer-inside-with-my-beloved-machine.mp3](sourcing/CND-AS14-05-safer-inside-with-my-beloved-machine.mp3) | 241,091 |
| [sourcing-report.md](sourcing-report.md) | 2,081 |
| [spend-ledger.json](spend-ledger.json) | 252 |
| [spend-ledger.jsonl](spend-ledger.jsonl) | 0 |
| [stock-check/stock-check.json](stock-check/stock-check.json) | 10,412 |
| [stock-check/stock-check.md](stock-check/stock-check.md) | 7,967 |
| [TEST-REPORT.md](TEST-REPORT.md) | 3,793 |
| [variants.json](variants.json) | 25,176 |
| [voice-sample.json](voice-sample.json) | 339 |

_Generated from the run artifacts; do not edit by hand._
