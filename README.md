# PinConv2

**Brief in, an executable production plan out, with evidence.**

PinConv2 is the AI-native creative production system for research-led video work.
This repository contains **Level 1**: the research and production-planning stage
that runs before any paid asset is generated.

Level 1 takes a 50-100 word creative idea and returns two linked documents:

1. a **Concept Note** with the audience, evidence, recommended treatment, two
   alternatives and three hooks;
2. an **executable Production Plan** with timed beats, shots, independently
   editable layers, asset requirements, exact-data bindings, audio cues,
   alternates, budget estimates and observable acceptance checks.

Both are approved together at **Gate 1** by a named human. Level 2 uses the
approved scope to produce assets and assemble a rough cut.

## The four levels

| Level | Job | Spend |
|---|---|---|
| **L1 - Plan** | Research, concept, shot x layer x asset plan, validation, critique, Gate 1 | No production spend |
| **L2 - Source and budget** | Quote, select routes, lock budget, produce assets and rough cut | Approved budget |
| **L3 - Review and deliver** | Review cuts, finish, QC, deliver | Approved budget |
| **L4 - Learn** | Publish, measure, iterate | Approved budget |

This repository implements **L1 only**. No command generates, downloads, renders
or publishes media.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -e ".[dev]"
pytest
```

The only runtime dependency is Pydantic.

## The Toffee test run

The acceptance case is a 10-second vertical ad for
[Toffee Coffee Roasters](https://toffeecoffeeroasters.com/) Ethiopia Speciality
Instant Coffee. The brief, research pack and plan are deterministic fixtures so
the workflow can be tested without an LLM, a provider key or a media spend.

```bash
pinconv2 --data-dir projects run-all --fixture toffee-coffee-10s
```

That runs:

```
init -> research -> concept -> plan -> validate (fails v1)
     -> critique -> resolve top 3 -> validate v2 (passes)
     -> critique v2 (clean) -> Gate 1 packet
```

The packet stops before approval. A named human then runs:

```bash
pinconv2 --data-dir projects approve \
  --reviewer "Your Name" \
  --role "Brand producer" \
  --evidence "email 2026-11-14 14:32, subject: Gate 1" \
  --channel email \
  --confirm APPROVE \
  --approve-exact-data all \
  --condition "Price and promotion remain out of the cut."

pinconv2 --data-dir projects export
```

`approve` is the only command that records a human decision. It requires a
named reviewer, a role, an evidence reference and the typed confirmation
`APPROVE`; agents and automation are rejected. `--approve-exact-data all`
approves the pending identifiers (origin, brand name and CTA) that the packet
lists. Omit it and those values stay pending in the handoff.

To drive the stages one at a time:

```bash
pinconv2 --data-dir projects init --fixture toffee-coffee-10s
pinconv2 --data-dir projects research
pinconv2 --data-dir projects concept
pinconv2 --data-dir projects plan
pinconv2 --data-dir projects validate
pinconv2 --data-dir projects critique
pinconv2 --data-dir projects resolve-inputs
pinconv2 --data-dir projects validate
pinconv2 --data-dir projects critique
pinconv2 --data-dir projects gate1
pinconv2 --data-dir projects status
```

## What the test run produces

Under `projects/toffee-coffee-10s/`:

```
project.json
brief.json
research.json
concept.json
plans/rev-001.json            # rejected after critique
plans/rev-002.json            # Gate 1 candidate
validation/rev-001.json
validation/rev-002.json
critique/rev-001.json
critique/rev-002.json
resolutions/001-to-002.json
gate/packet-rev-002.json
approvals/rev-002.json        # only after a named human approves
exports/rev-002/
  concept-note.md
  production-plan.md
  gate1-packet.md
  level2-handoff.json
  production-plan.json
  concept-note.json
  research-pack.json
  brief.md
  previews/SH-01.svg ... SH-04.svg
  previews/contact-sheet.svg
events.jsonl
```

The Markdown and SVG mockups are rendered from the JSON. The JSON is the source
of truth.

## Gate 1 rules

- A bundle hash binds the brief, research, concept note, plan, validation,
  critique and resolution together.
- The plan hash and bundle hash bind the packet and approval.
- A changed plan or concept creates a new revision and invalidates the old
  approval; export rechecks the bundle.
- Validation must pass: timing, safe area, layer bindings, protected regions,
  commercial exactness, budget, rights and traceability.
- Every Level 1 acceptance check is evaluated against its own rule references.
- No blocker or high-severity critique finding may remain open.
- Every top-three input must name a target record that actually changed or was
  removed in the new revision.
- The approver must be a named human with a role, an approval channel and an
  evidence reference; the service has no default actor kind.
- The approved packet is immutable; export verifies the packet hash stored in
  the approval.
- The packet lists every held item (price/promotion, brand assets, music) and
  every exact value still pending approval.
- A held commercial value remains blocked until its evidence exists.

## What Level 1 will not do

- call a paid image, video, music or speech provider;
- download stock media;
- render a final MP4;
- publish to a platform;
- invent an approval, a price, an offer or a claim.

## Repository layout

```
src/pinconv2/
  models.py              typed contracts and content hashing
  store.py               folder persistence and immutable revisions
  workflow.py            Level 1 state machine
  service.py             application service used by the CLI
  cli.py                 command line
  critique.py            fresh-context critic and top-three selector
  render.py              Markdown renderers and Level 2 handoff
  validators/            timing, exact data, layers, budget, rights, traceability
  fixtures/              Toffee brief, research, concept and plan
tests/                   59 deterministic tests
examples/                the test brief
docs/                    Level 1 design and architecture
```

## Evidence

At the last run:

- 59 tests pass;
- `ruff check .` passes;
- `mypy src/pinconv2` passes;
- the Toffee run reaches `gate1_ready` with no blockers;
- revision 1 fails with 8 reviewable failures and revision 2 passes;
- the critic selects safe area, commercial data and budget as the top three
  inputs, and the revision records which target records changed;
- the Gate 1 packet lists the three held items and the pending exact values;
- the exported Level 2 handoff is bound to the approved plan and bundle hashes.

See `docs/level1.md` for the contracts and rules, and
`docs/architecture.md` for the four-level model.
