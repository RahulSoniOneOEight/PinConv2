# Architecture

## 1. Position

PinConv2 is a production system, not a prompt wrapper. It treats creative work
as a durable, auditable workflow with typed contracts, content hashes, explicit
budgets and human gates.

The system is split into four operating levels:

```
L1  Plan              research -> concept -> shot/layer/asset plan -> Gate 1
L2  Source and budget quotes -> route selection -> assets -> rough cut
L3  Review and deliver review -> finish -> QC -> delivery
L4  Learn             publish -> measure -> iterate
```

**This repository implements L1.** Later levels consume the Level 2 handoff and
must not re-open an approved decision without a new revision.

## 2. Principles

1. **Artifact-first.** Every output is a file with a hash and lineage.
2. **Contract-first.** Agents exchange Pydantic records, not prose.
3. **Human authority at meaning boundaries.** Brief, plan, budget, identity,
   rights and final creative approval are human gates.
4. **No invisible spend.** L1 has no production spend; later levels need a quote,
   a reservation and a receipt.
5. **Rights by default.** No asset enters a timeline without a rights position.
6. **Durable workflow.** Every transition is persisted; a restart resumes at the
   last complete checkpoint.
7. **Evidence over assertion.** A check passes against the exact revision hash.

## 3. Components

```
CLI              init · research · concept · plan · validate · critique
                 resolve-inputs · gate1 · approve · export · status
Application      service.py - state guards, records, packets, exports
Domain           models.py - frozen typed contracts and content hashing
Persistence      store.py - folders, JSON records, immutable plan revisions
Quality          validators/ - timing, exactness, layers, budget, rights, trace
Critique         critique.py - independent findings and top-three ranking
Rendering        render.py - Markdown notes, Gate 1 packet, Level 2 handoff
Fixtures         fixtures/ - the Toffee brief, research, concept and plan
```

The CLI is deliberately thin. Every command goes through the same service
functions used by the tests.

## 4. State machine

```
INIT -> INTAKE -> RESEARCH -> TREATMENT -> SHOT_PLAN -> VALIDATED
     -> CRITIQUED -> INPUTS_UPDATED -> VALIDATED -> CRITIQUED
     -> GATE1_READY -> APPROVED
```

`FAILED` is reachable from any active state. A transition that is not in the
table is rejected. `validate` and `critique` are idempotent for the same
revision; `resolve-inputs` creates exactly one new revision in v0.1.

## 5. Storage and identity

```
projects/<project_id>/
  project.json
  brief.json
  research.json
  concept.json
  plans/rev-001.json
  validation/rev-001.json
  critique/rev-001.json
  resolutions/001-to-002.json
  gate/packet-rev-002.json
  approvals/rev-002.json
  exports/rev-002/...
  events.jsonl
```

A plan hash is the SHA-256 of canonical JSON with `created_at` removed. This
makes a rebuild deterministic and binds validation, critique, packet and
approval to the same content. Plan revisions are immutable: a different plan at
the same revision is refused.

## 6. Gates

```
Brief intake   every must-have has an evidence target
Research       consequential statements link to a source or an assumption
Concept        one recommendation, two credible alternatives, three hooks
Plan           every shot has method, fallback, layers, assets and checks
Validation     deterministic rules pass or produce a reviewable failure
Critique       blockers and high findings must be resolved or escalated
Gate 1         named human approves the exact revision and hash
```

L1 can prepare static previews and timing mockups. It cannot render the final
cut or spend money.

## 7. Extension points

The fixture planner implements the same interfaces a live agent will use:

- `build_research_pack()` can be replaced by research adapters that write the
  same `ResearchPack`;
- `build_concept_note()` can be replaced by an LLM director that returns a
  `ConceptNote`;
- `build_plan()` can be replaced by a planner that returns a `ProductionPlan`;
- `critique_plan()` stays independent and read-only;
- the validators do not care who wrote the plan.

A live adapter must preserve the invariants: evidence locators, exact-data
status, rights positions and a plan hash.

## 8. Non-goals

- a chat UI or a general-purpose agent;
- a renderer or NLE;
- provider billing;
- multi-tenant storage;
- replacing OpenMontage's media tools.

## 9. Roadmap

1. **v0.1 (this slice)** - Level 1 contracts, Toffee fixture, validators,
   critique, Gate 1, export.
2. **v0.2** - live research adapters, LLM concept and planner behind the same
   contracts, static preview renderer.
3. **v0.3** - Level 2 quoting, budget reservation, asset production and rough
   cut.
4. **v0.4** - Level 3 review, finish and delivery.
5. **v0.5** - Level 4 measurement and iteration.
