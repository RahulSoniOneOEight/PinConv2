# How to review the Level 2 output

**Project:** `blue-tokai-easy-pour-20s` · **Run:** `rev-002`
**What you are approving:** Gate 2A — budget, methods, sources, lean
substitutions and the fal.ai/Runware cap.

You are **not** re-approving the creative. The concept, 6 shots, 38 layers,
copy and `VO-01` were fixed at Level 1. Level 2 answers a different question:
*can this be produced exactly as approved, from which sources, at what cost, and
is it ready to assemble?*

---

## 1. Open the review pack

| Format | File |
|---|---|
| Read and comment | `review-pack.md` |
| Opens in any browser | `review-pack.html` |
| Share with a colleague | `review-pack.docx` (standard Word document) |
| Budget only | `budget-estimate.md` / `.html` / `.docx` |
| Technical handoff | `build-sheet/production-build-sheet.md` / `.html` |
| Per-shot/layer sources | `SOURCE-SHEET.md` / `.html` |
| Pending asset routes | `PENDING-ASSET-ROUTES.md` |
| Stock fetch check | `stock-check/stock-check.md` |
| OpenMontage discovery | `openmontage-sourcing.json` |
| Renderer decision | `RENDERER-DECISION.md` |
| Generation stage | `generation-report.json` (only after Gate 2A) |
| Voice fallback sample | `generated/AS-15-edge-sample.mp3` |
| Gate checks | `gate2/packet-2a.json` |
| Fill-in form | `feedback-form.md` |

The pack is generated from the same records as the build sheet, so a decision
you see in the pack is the decision the compositor receives.

---

## 2. Review in this order (about 20 minutes)

### Step 1 — Summary (2 min)

Check the counts and money:

- 16 assets, 38 layers, 6 shots, 1 variant (`VO-01`);
- cash total and in-kind value;
- project cap and headroom;
- fal.ai + Runware cap, spent and remaining;
- number of blocked assets and open holds.

If the cash or provider figures are wrong, stop. Nothing else matters until
they reconcile.

### Step 2 — Budget (3 min)

Read `budget-estimate.md`:

- every line is labelled `operator_estimate` or `verified_quote`;
- shared lines are charged once (`ES-06` capture, `ES-07` pack preparation);
- lean mode lists each substitution with its route and risk;
- the provider section shows the $2 cap and the $0.50 per-job maximum.

Ask: *is each line something I am willing to pay for or do in-house?*

### Step 3 — Assets (5 min)

Each asset block shows: truth class, impact, method, source, rights, hold,
cost, acceptance line and a preview link.

Judge against the **acceptance line**, not the description:

| Class | What must be true |
|---|---|
| `exact` | Real pack, logo or price; supplied or captured from the original; never stock or generated |
| `proof` | Captured demonstration; never a stock substitute |
| `atmospheric` / `representative` | Stock or procedural is allowed, licence must pass |

Red flags: an exact asset marked `stock`, a proof asset without capture, a
cleared asset without a licence name, a `needs_approval` asset with no hold.

### Step 4 — Layers (5 min)

The layer table gives one row per layer:

`class · impact · method · fallback · probe · pick mode`

- `M0` supplied/owned, `M4` procedural, `M6` capture, `M1` library;
- every `M2`–`M7` must require a probe;
- high and medium impact must be a human pick;
- exact text is rendered from the approved copy block, never typed by hand.

Spot-check the layers you care about against their shot preview.

### Step 5 — Shots and previews (3 min)

Open the 16:9 and 9:16 SVGs for each shot. Green dashed line = safe area, red
dashed box = protected region. Check that:

- the pack label and logo are never covered;
- captions sit inside the safe area in both ratios;
- the vertical cut is a recomposition, not a crop of the 16:9 frame.

### Step 6 — Variant (1 min)

`VO-01` must resolve all 38 layers, carry 4 effect masks, keep 500 frames at
1080×1920, and state that `AC-16` is still pending. A missing override is a
blocker, not a note.

### Step 7 — Compliance and provider spend (1 min)

- no NC, ND, share-alike, BBC SFX or GADM source;
- manual-only sources are not scripted;
- aggregator licences resolve at the origin;
- fal/Runware cap, spend and remaining are visible;
- every warning is either acceptable or a correction.

### Stock check

No stock media is committed to the package. A sourcing discovery round ran for
the two library-music intents:

- `AS-10` music bed: 4 CC BY candidates, chosen **“Lost Roamin'” by speck**.
- `AS-14` conditional fallback: 5 CC BY candidates, chosen **“This Is Our
  Music - Instrumental” by gabriel_shelligton**.
- 9 candidates passed the licence gate; nine 20-second previews are in
  `sourcing/`; nothing has been acquired into `sourced/`.
- All 38 layer methods remain `M0` supplied/owned, `M4` procedural or `M6`
  capture — zero stock layers. Exact and proof material is never stock.

Acquisition and the final music licence are part of Gate 2A.

### Generation stage

The generation stage is `level2.generation_stage.run_generation`. It is called
by `run_build` when a generation engine is supplied. It:

- refuses unless Gate 2A is APPROVED and has a named approver;
- loads the project provider budget ($2 cap, $0.50 per job);
- reserves each quoted job through `ProviderGovernor` before calling the engine;
- receipts the actual cost and releases the reservation on failure;
- writes `generation-report.json` and refreshes `provider-spend.json`.

`AS-15` is a conditional fallback, so it is skipped unless the run explicitly
includes conditional assets. No paid generation has run.

### Renderer

`RENDERER-DECISION.md` records that HyperFrames `0.8.123` is installed and
Remotion is not. A named human must accept HyperFrames or approve installing
Remotion before the production render path is final.

---

## 3. Record a decision

Use one decision per item:

| Decision | Meaning |
|---|---|
| **APPROVE** | Keep it; it can move to Gate 2B |
| **CHANGE** | One concrete instruction; produces a correction and a new run |
| **REJECT** | Block or replace the item |

Fill `feedback-form.md`, or write `corrections.jsonl` directly:

```json
{"id":"COR-001","item_kind":"asset","item_id":"AS-02","decision":"change","instruction":"Use the 2400px pack master, not the 1800px web image","reason":"Label edge is soft at 1080p","requested_by":"Your Name","status":"open"}
```

Allowed `item_kind`: `asset`, `layer`, `shot`, `variant`, `budget`.
Creative changes to a shot or the variant are refused here and routed back to
Level 1, because Level 2 may not reopen an approved creative decision.

---

## 4. Apply corrections

Preview only (no new run):

```bash
python -m pinconv2 --data-dir projects level2 correct \
  --project blue-tokai-easy-pour-20s --revision 2 --run rev-002 \
  --input corrections.jsonl
```

Build the new run:

```bash
python -m pinconv2 --data-dir projects level2 correct \
  --project blue-tokai-easy-pour-20s --revision 2 --run rev-002 \
  --input corrections.jsonl --apply
```

This creates `rev-003`, re-derives the plan, carries the accepted corrections in
the build sheet, and produces a fresh Gate 2A packet. `rev-002` is never edited.

---

## 5. Approve Gate 2A

Only a named human can do this. The command records who approved, their role and
the evidence reference:

```bash
python -m pinconv2 --data-dir projects level2 gate \
  --project blue-tokai-easy-pour-20s --revision 2 --run rev-002 \
  --gate 2a --approve \
  --reviewer "Your Name" --role "Brand owner" \
  --evidence "ticket or email reference" --confirm APPROVE
```

Approving Gate 2A does **not** spend money. It authorises sourcing and processing,
and it accepts the lean substitutions and the provider cap. Every fal/Runware
call still needs a positive quote within $0.50 per job and the remaining $2.00.

---

## 6. What happens after approval

| Gate | What it needs | What it unlocks |
|---|---|---|
| **2A** | This review | Sourcing, capture, processing, provider calls |
| **2B** | Every in-scope asset processed and bound; rights cleared; visual QC | Ready-to-assemble package |
| **2C** | 16:9 and 9:16 rough cuts; audio and captions checked | Delivery review |

`level2 build` only processes files you have imported under
`projects/blue-tokai-easy-pour-20s/inputs/`; it never downloads or generates
implicitly. Until sources exist, Gate 2B stays blocked — by design.

---

## 7. Quick commands

```bash
# paths to the pack
python -m pinconv2 --data-dir projects level2 review --project blue-tokai-easy-pour-20s --run rev-002

# QC verdicts
python -m pinconv2 --data-dir projects level2 qc --project blue-tokai-easy-pour-20s --run rev-002

# provider cap and remaining
python -m pinconv2 --data-dir projects level2 spend --project blue-tokai-easy-pour-20s --run rev-002

# gate status
python -m pinconv2 --data-dir projects level2 gate --project blue-tokai-easy-pour-20s --gate 2a
```

## 8. Golden rules

1. Judge against the acceptance line and the preview, not the prose.
2. Exact and proof material never gets a stock or generated substitute.
3. No paid call before Gate 2A; no provider call without a quote inside the cap.
4. Corrections create a new run; they never edit the approved one.
5. A warning is a decision to make, not noise to ignore.
