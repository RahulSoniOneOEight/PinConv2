# Blue Tokai Level 2 — run index

**Run:** `rev-002` · **Plan revision:** 2
**Status:** Gate 2A `ready_for_approval` · cash $0.00 · in-kind $81.00
**Plan hash:** `1370f029b0b35730625c459cf85579bfd767d2e4a7b62016055e100d15f2aba5`

## Start here

| Document | What it is |
|---|---|
| [REVIEW-GUIDE.md](REVIEW-GUIDE.md) | How a human reviews the pack, records corrections and approves Gate 2A |
| [ASSET-SUMMARY.md](ASSET-SUMMARY.md) | Main asset table: shot/layer/asset, route, access and visual QC |
| [NO-SHOOT-POLICY.md](NO-SHOOT-POLICY.md) | No-shoot constraint and stock/AI route findings |
| [NO-IN-HOUSE-POLICY.md](NO-IN-HOUSE-POLICY.md) | Stock / AI-generation / AI-enhancement only, with line replacements |
| [USER-INPUT-GAPS.md](USER-INPUT-GAPS.md) | Awaiting-user vs agent-resolvable vs obsolete work |
| [REBASELINE-PLAN.md](REBASELINE-PLAN.md) | Proposed no-in-house re-baseline and new Gate 2A requirement |
| [LEVEL3-SPEND.md](deliverables/LEVEL3-SPEND.md) | Per-step Level 3 production spend |
| [RIGHTS-CLEARANCE.md](RIGHTS-CLEARANCE.md) | HI-02 brand files imported and rights accepted |
| [STOCK-PLAN.md](STOCK-PLAN.md) | Per-asset stock route, fetched candidates and AI-share guard |
| [ANNEX-SOURCED-NOT-USED.md](ANNEX-SOURCED-NOT-USED.md) | Sourced-but-not-used backup candidates with reasons |
| [PENDING-ASSET-ROUTES.md](PENDING-ASSET-ROUTES.md) | Current route vs no-shoot route for every asset |
| [PRODUCTION-PLAN.md](PRODUCTION-PLAN.md) | Shot order, asset queue and layer plan |
| [PROCESSING-PLAN.md](PROCESSING-PLAN.md) | Per-asset processing and the $2 trial budget |
| [VOICE-DIRECTION.md](VOICE-DIRECTION.md) | VO casting, continuous delivery and two audition takes |
| [voice-selection.json](voice-selection.json) | Selected take — male VO-M1 |
| [VOICE-TOOLS-STATUS.md](VOICE-TOOLS-STATUS.md) | Which TTS tools are installed/working |
| [qc/visual-assets.md](qc/visual-assets.md) | Agent visual QC verdict per asset |
| [SOURCE-SHEET.md](SOURCE-SHEET.md) | Every shot/layer with its actual asset source and preview |
| [stock-check/stock-check.md](stock-check/stock-check.md) | Live fetch result per stock source, with licences |
| [openmontage-status.json](openmontage-status.json) | OpenMontage account, version and connected providers |
| [openmontage-check.json](openmontage-check.json) | Real NASA stock acquisition and 2-second HyperFrames render |
| [openmontage-sourcing.json](openmontage-sourcing.json) | 5 NASA stock candidates for AS-07, search only |
| [RENDERER-DECISION.md](RENDERER-DECISION.md) | HyperFrames vs Remotion; awaiting named-human acceptance |
| [openmontage/candidates/](openmontage/candidates/) | Downloaded candidate previews |
| [openmontage/render.mp4](openmontage/render.mp4) | Rendered test clip (1920?1080, 2 s, 60 frames) |
| [shortgpt-status.json](shortgpt-status.json) | Edge TTS and local faster-whisper transcription |
| [transcription.json](transcription.json) | Timed transcript of the voice sample |
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
| [ANNEX-SOURCED-NOT-USED.md](ANNEX-SOURCED-NOT-USED.md) | 1,942 |
| [asset-intents.json](asset-intents.json) | 10,867 |
| [asset-production-tasks.json](asset-production-tasks.json) | 19,299 |
| [asset-sourcing.json](asset-sourcing.json) | 7,670 |
| [ASSET-SUMMARY.html](ASSET-SUMMARY.html) | 18,715 |
| [ASSET-SUMMARY.json](ASSET-SUMMARY.json) | 15,091 |
| [ASSET-SUMMARY.md](ASSET-SUMMARY.md) | 12,879 |
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
| [cli-gate2a-output.json](cli-gate2a-output.json) | 3,413 |
| [cli-plan-output.json](cli-plan-output.json) | 1,673 |
| [cli-qc-output.json](cli-qc-output.json) | 1,211 |
| [cli-spend-output.json](cli-spend-output.json) | 1,320 |
| [cli-stockcheck-output.json](cli-stockcheck-output.json) | 385 |
| [cli-voice-output.json](cli-voice-output.json) | 335 |
| [deliverables/clips/concat.txt](deliverables/clips/concat.txt) | 678 |
| [deliverables/clips/SH-01-1080x1920.mp4](deliverables/clips/SH-01-1080x1920.mp4) | 211,714 |
| [deliverables/clips/SH-01-1920x1080.mp4](deliverables/clips/SH-01-1920x1080.mp4) | 264,039 |
| [deliverables/clips/SH-02-1080x1920.mp4](deliverables/clips/SH-02-1080x1920.mp4) | 1,191,960 |
| [deliverables/clips/SH-02-1920x1080.mp4](deliverables/clips/SH-02-1920x1080.mp4) | 856,598 |
| [deliverables/clips/SH-03-1080x1920.mp4](deliverables/clips/SH-03-1080x1920.mp4) | 1,179,070 |
| [deliverables/clips/SH-03-1920x1080.mp4](deliverables/clips/SH-03-1920x1080.mp4) | 1,041,720 |
| [deliverables/clips/SH-04-1080x1920.mp4](deliverables/clips/SH-04-1080x1920.mp4) | 213,680 |
| [deliverables/clips/SH-04-1920x1080.mp4](deliverables/clips/SH-04-1920x1080.mp4) | 268,085 |
| [deliverables/clips/SH-05-1080x1920.mp4](deliverables/clips/SH-05-1080x1920.mp4) | 164,007 |
| [deliverables/clips/SH-05-1920x1080.mp4](deliverables/clips/SH-05-1920x1080.mp4) | 221,376 |
| [deliverables/clips/SH-06-1080x1920.mp4](deliverables/clips/SH-06-1080x1920.mp4) | 205,292 |
| [deliverables/clips/SH-06-1920x1080.mp4](deliverables/clips/SH-06-1920x1080.mp4) | 260,058 |
| [deliverables/level3-spend.json](deliverables/level3-spend.json) | 1,861 |
| [deliverables/level3-spend.jsonl](deliverables/level3-spend.jsonl) | 1,218 |
| [deliverables/LEVEL3-SPEND.md](deliverables/LEVEL3-SPEND.md) | 1,059 |
| [deliverables/rough-16x9-silent.mp4](deliverables/rough-16x9-silent.mp4) | 2,903,746 |
| [deliverables/rough-9x16-silent.mp4](deliverables/rough-9x16-silent.mp4) | 3,157,597 |
| [deliverables/ROUGH-CUT-16x9.mp4](deliverables/ROUGH-CUT-16x9.mp4) | 3,547,255 |
| [deliverables/ROUGH-CUT-9x16.mp4](deliverables/ROUGH-CUT-9x16.mp4) | 3,928,134 |
| [deliverables/ROUGH-CUT-REPORT.md](deliverables/ROUGH-CUT-REPORT.md) | 417 |
| [events.jsonl](events.jsonl) | 16,765 |
| [feedback-form.md](feedback-form.md) | 4,580 |
| [flow.json](flow.json) | 5,774 |
| [gaps.json](gaps.json) | 4,087 |
| [gate2/packet-2a.json](gate2/packet-2a.json) | 3,229 |
| [generated/AS-09-female-take.mp3](generated/AS-09-female-take.mp3) | 115,056 |
| [generated/AS-09-male-take.mp3](generated/AS-09-male-take.mp3) | 114,624 |
| [generated/AS-15-edge-sample.mp3](generated/AS-15-edge-sample.mp3) | 89,712 |
| [layer-method-decisions.json](layer-method-decisions.json) | 25,090 |
| [licence-gate-report.json](licence-gate-report.json) | 4,768 |
| [mypy-output.txt](mypy-output.txt) | 46 |
| [no-in-house-plan.json](no-in-house-plan.json) | 1,848 |
| [NO-IN-HOUSE-POLICY.md](NO-IN-HOUSE-POLICY.md) | 1,680 |
| [no-shoot-plan.json](no-shoot-plan.json) | 2,880 |
| [NO-SHOOT-POLICY.md](NO-SHOOT-POLICY.md) | 2,506 |
| [OPEN-TOOLS-STATUS.md](OPEN-TOOLS-STATUS.md) | 9,511 |
| [openmontage/candidates/AS-07-01.jpg](openmontage/candidates/AS-07-01.jpg) | 35,656 |
| [openmontage/candidates/AS-07-02.jpg](openmontage/candidates/AS-07-02.jpg) | 47,936 |
| [openmontage/candidates/AS-07-03.jpg](openmontage/candidates/AS-07-03.jpg) | 44,247 |
| [openmontage/candidates/AS-07-04.jpg](openmontage/candidates/AS-07-04.jpg) | 58,912 |
| [openmontage/candidates/AS-07-05.jpg](openmontage/candidates/AS-07-05.jpg) | 41,981 |
| [openmontage/nasa-stock.jpg](openmontage/nasa-stock.jpg) | 103,961 |
| [openmontage/render.mp4](openmontage/render.mp4) | 26,984 |
| [openmontage-check.json](openmontage-check.json) | 1,020 |
| [openmontage-sourcing.json](openmontage-sourcing.json) | 4,276 |
| [openmontage-status.json](openmontage-status.json) | 904 |
| [PENDING-ASSET-ROUTES.md](PENDING-ASSET-ROUTES.md) | 3,146 |
| [PROCESSING-PLAN.html](PROCESSING-PLAN.html) | 12,852 |
| [processing-plan.json](processing-plan.json) | 9,008 |
| [PROCESSING-PLAN.md](PROCESSING-PLAN.md) | 9,231 |
| [PRODUCTION-PLAN.html](PRODUCTION-PLAN.html) | 11,812 |
| [PRODUCTION-PLAN.md](PRODUCTION-PLAN.md) | 6,753 |
| [provider-budget.json](provider-budget.json) | 283 |
| [provider-spend.json](provider-spend.json) | 468 |
| [provider-spend.jsonl](provider-spend.jsonl) | 0 |
| [pytest-output.txt](pytest-output.txt) | 187 |
| [qc/assets/AS-01.png](qc/assets/AS-01.png) | 9,073 |
| [qc/assets/AS-02.jpg](qc/assets/AS-02.jpg) | 167,931 |
| [qc/assets/AS-03.jpg](qc/assets/AS-03.jpg) | 172,354 |
| [qc/assets/AS-04.jpg](qc/assets/AS-04.jpg) | 159,381 |
| [qc/assets/AS-17.jpg](qc/assets/AS-17.jpg) | 114,232 |
| [qc/assets.json](qc/assets.json) | 3,139 |
| [qc/budget.json](qc/budget.json) | 1,110 |
| [qc/rights.json](qc/rights.json) | 464 |
| [qc/semantic.json](qc/semantic.json) | 407 |
| [qc/technical.json](qc/technical.json) | 780 |
| [qc/visual-assets.md](qc/visual-assets.md) | 2,129 |
| [qc/visual.json](qc/visual.json) | 423 |
| [REBASELINE-PLAN.md](REBASELINE-PLAN.md) | 2,463 |
| [RENDERER-DECISION.md](RENDERER-DECISION.md) | 2,096 |
| [REVIEW-GUIDE.md](REVIEW-GUIDE.md) | 11,237 |
| [review-pack.docx](review-pack.docx) | 39,142 |
| [review-pack.html](review-pack.html) | 28,293 |
| [review-pack.md](review-pack.md) | 19,465 |
| [RIGHTS-CLEARANCE.md](RIGHTS-CLEARANCE.md) | 1,326 |
| [rights-manifest.json](rights-manifest.json) | 4,932 |
| [ruff-output.txt](ruff-output.txt) | 21 |
| [run.json](run.json) | 117,646 |
| [shortgpt-status.json](shortgpt-status.json) | 223 |
| [sound-plan.json](sound-plan.json) | 2,757 |
| [SOURCE-SHEET.html](SOURCE-SHEET.html) | 14,651 |
| [SOURCE-SHEET.json](SOURCE-SHEET.json) | 22,598 |
| [SOURCE-SHEET.md](SOURCE-SHEET.md) | 9,644 |
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
| [stock-candidates/archive-donniesands-airplanesacousticcover.ogg](stock-candidates/archive-donniesands-airplanesacousticcover.ogg) | 3,213,523 |
| [stock-candidates/archive-iuma-too-much-coffee.ogg](stock-candidates/archive-iuma-too-much-coffee.ogg) | 676,838 |
| [stock-candidates/archive-jamendo-560425.mp3](stock-candidates/archive-jamendo-560425.mp3) | 5,608,887 |
| [stock-candidates/archive-jamendo-618068.mp3](stock-candidates/archive-jamendo-618068.mp3) | 7,942,586 |
| [stock-candidates/archive-spring-2023-202304.mp3](stock-candidates/archive-spring-2023-202304.mp3) | 10,532,545 |
| [stock-candidates/archive-technico1949.mp4](stock-candidates/archive-technico1949.mp4) | 4,493,755 |
| [stock-candidates/archive-tsunami-penang-beach.mp4](stock-candidates/archive-tsunami-penang-beach.mp4) | 4,205,710 |
| [stock-candidates/AS-05.mp4](stock-candidates/AS-05.mp4) | 10,870,570 |
| [stock-candidates/AS-06.mp4](stock-candidates/AS-06.mp4) | 49,192,757 |
| [stock-candidates/AS-07.jpg](stock-candidates/AS-07.jpg) | 192,334 |
| [stock-candidates/AS-08.jpg](stock-candidates/AS-08.jpg) | 197,345 |
| [stock-candidates/AS-10.mp3](stock-candidates/AS-10.mp3) | 1,505,114 |
| [stock-candidates/AS-11.mp3](stock-candidates/AS-11.mp3) | 421,701 |
| [stock-candidates/AS-14.mp3](stock-candidates/AS-14.mp3) | 1,867,536 |
| [stock-candidates/openverse-cup-of-coffee-on-table-rock-in-linville-gorge.jpg](stock-candidates/openverse-cup-of-coffee-on-table-rock-in-linville-gorge.jpg) | 100,772 |
| [stock-candidates/openverse-road-in-the-forest.mp3](stock-candidates/openverse-road-in-the-forest.mp3) | 10,143,023 |
| [stock-candidates/openverse-water-pouring-9-wav.mp3](stock-candidates/openverse-water-pouring-9-wav.mp3) | 61,873 |
| [stock-candidates/wikimedia-file-juan-gris-moulin-caf-tasse-et-verre-sur-une-t.jpg](stock-candidates/wikimedia-file-juan-gris-moulin-caf-tasse-et-verre-sur-une-t.jpg) | 274,860 |
| [stock-candidates/wikimedia-file-kitchen-arrangement-and-equipment-ia-kitchena.jpg](stock-candidates/wikimedia-file-kitchen-arrangement-and-equipment-ia-kitchena.jpg) | 3,285,471 |
| [stock-candidates/wikimedia-file-pouring-water-bottles-ogg.ogg](stock-candidates/wikimedia-file-pouring-water-bottles-ogg.ogg) | 744,457 |
| [stock-candidates.json](stock-candidates.json) | 12,780 |
| [stock-check/stock-check.json](stock-check/stock-check.json) | 10,412 |
| [stock-check/stock-check.md](stock-check/stock-check.md) | 7,967 |
| [stock-plan.json](stock-plan.json) | 17,936 |
| [STOCK-PLAN.md](STOCK-PLAN.md) | 4,935 |
| [TEST-REPORT.md](TEST-REPORT.md) | 5,006 |
| [transcription.json](transcription.json) | 756 |
| [USER-INPUT-GAPS.md](USER-INPUT-GAPS.md) | 2,933 |
| [variants.json](variants.json) | 25,176 |
| [voice-direction.json](voice-direction.json) | 1,983 |
| [VOICE-DIRECTION.md](VOICE-DIRECTION.md) | 2,897 |
| [voice-sample.json](voice-sample.json) | 340 |
| [voice-selection.json](voice-selection.json) | 297 |
| [voice-take-female.json](voice-take-female.json) | 1,256 |
| [voice-take-male.json](voice-take-male.json) | 1,293 |
| [VOICE-TOOLS-STATUS.md](VOICE-TOOLS-STATUS.md) | 1,378 |

_Generated from the run artifacts; do not edit by hand._
