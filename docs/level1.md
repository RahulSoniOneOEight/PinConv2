# Level 1 - research and production planning

## 1. Purpose

Level 1 turns a short creative brief into a plan that another team can execute
without inventing a decision. It is deliberately upstream of money: no paid
generation, no stock download, no render, no publish.

The output is two documents approved together at Gate 1:

1. **Concept Note** - audience, evidence, recommended treatment, alternatives,
   hooks, look, sound and open questions.
2. **Production Plan** - a timed Shot x Layer x Asset specification with exact
   data, audio, budget, alternates and acceptance checks.

A third machine-readable **Level 2 handoff** carries the approved scope.

## 2. Sequence

```
INIT
  -> INTAKE        normalise the brief, classify it, list must-haves and holds
  -> RESEARCH      questions, sources, findings, claims and exact-data register
  -> TREATMENT     concept note with one recommendation and two alternatives
  -> SHOT_PLAN     beats, shots, layers, assets, audio, budget, checks
  -> VALIDATED     deterministic checks against the exact plan revision
  -> CRITIQUED     fresh-context critic, findings by ID, top three inputs
  -> INPUTS_UPDATED revised plan revision with the top three handled
  -> VALIDATED     re-check the revised plan
  -> CRITIQUED     re-critique the revised plan
  -> GATE1_READY   packet with ready shots, held items, conditions and blockers
  -> APPROVED      named human approval bound to revision and hash
```

A command fails rather than skipping a predecessor. A failing validation does
not stop the critique; it stops Gate 1.

## 3. Contracts

| Record | What it carries |
|---|---|
| `BriefRevision` | source text, classification, audience, language, duration, fps, aspect, placements, budget cap, constraints, assumptions, must-haves |
| `DeliverableProfile` | platform, canvas, fps, frame count, safe area, caption rules, CTA copy, variant |
| `ResearchQuestion` | question, why it matters, priority, status |
| `EvidenceSource` | locator, access date, channels actually inspected, reliability |
| `Finding` | observation, interpretation, proposed action, source, evidence locator, confidence, status, rights status, impact/effort, linked IDs |
| `ExactData` | field, value, status, source, evidence locator, approver, expiry |
| `Claim` | wording, verification, approved advertising wording, limitations |
| `ConceptOption` | treatment, look, sound, scores, rationale, risks, evidence links |
| `HookOption` | three candidate hooks with rationale and risk |
| `Beat` | half-open frames, purpose, spoken line, on-screen copy, action, emotion, cues |
| `Shot` | half-open frames, framing, movement, subject, action, lighting, palette, continuity, method, fallback, status, layer/asset/check IDs |
| `Layer` | shot-relative frames, role, z-order, rect, text style, motion, effect, protected regions, asset or copy binding, exactness, required |
| `Asset` | route, source, rights, technical spec, exactness, permissions, dependencies, estimate, fallback, usage |
| `AudioCue` | frames, kind, description, asset, level, essential |
| `AlternateRoute` | trigger, preserved requirement, revised dependencies, cost delta, approval scope |
| `Estimate` / `BudgetPlan` | shared/shot/variant/fallback cost, basis, confidence, retry reserve |
| `AcceptanceCheck` | target, observable condition, method, level, rule references, status |
| `HeldItem` | what is blocked, why, what evidence clears it, owner |
| `ValidationReport` | rule, target, severity, pass/fail/warn, remediation, check status |
| `CritiqueFinding` | category, observation, evidence, action, impact, confidence, effort, blocking weight, owner, disposition |
| `ResolutionReport` | top-three rank, mode, decision, changes, impacted IDs, status |
| `BundleManifest` | hashes of brief, research, concept, plan, validation, critique and resolution; one bundle hash |
| `Gate1Packet` | plan and bundle hashes, validation, ready shots, held layers, held items, exact data pending, conditions, blockers, input statuses |
| `Gate1Approval` | approver, role, actor kind, evidence, timestamp, scope, approved exact data, plan and bundle hashes |
| `Level2Handoff` | approved shots, asset briefs, rights actions, pending checks, held items, approved and pending exact data |

All records are frozen Pydantic models. A plan revision is immutable. Writing a
different plan to the same revision is refused.

## 4. Shot x Layer x Asset

A shot is not "a clip". It is a complete instruction:

- half-open frame range `[start, end)`;
- what the viewer must understand;
- framing, movement, subject, action, expression, lighting, palette, cut;
- spoken line, on-screen copy, audio cues and continuity;
- primary method and a genuinely different fallback;
- layer, asset, estimate and acceptance-check references.

A layer is independently editable:

- shot-relative in/out frames and absolute canvas rect;
- role, z-order, opacity, fill, text style, motion keyframes and effects;
- binding to an asset or a copy block;
- exactness and required/optional status;
- protected regions for pack labels and logos;
- allowed edits for the next level.

An asset is a requirement, not an assumption:

- owned, supplied, to-source, to-capture, to-create or to-generate;
- source, generation spec, rights position and technical spec;
- exactness, allowed edits, dependencies, estimate, fallback and usage.

The Toffee plan has four shots, 24 layers and 12 asset requirements in revision
2. Every layer binds to a resolvable asset or copy block.

## 5. Exactness policy

Public observation is not approval.

| Status | Meaning | Effect |
|---|---|---|
| `approved` | a named human approved the exact value | usable |
| `proposed` | creative wording awaiting Gate 1 | warning; approval scope must name it |
| `observed` | seen on a public source | warning for identifiers; failure for price, offer, code, pack size or claim |
| `held` | missing or unconfirmed | required layer fails |
| `stale` / `rejected` | expired or refused | required layer fails |

A copy block can reference exact data and claims. A required layer that uses
unapproved price, offer, promo code, pack size or claim fails validation. A
required layer that uses a held copy block fails validation.

## 6. Budget policy

```
subtotal = unique shared + shot + variant
reserve  = subtotal x retry reserve percent
total    = subtotal + reserve
worst    = total + costed fallbacks
```

- `total <= cap`;
- `worst <= cap`;
- every estimate declares `operator_estimate` or `verified_quote` and a
  confidence;
- every estimate is referenced by an asset or shot;
- the Toffee v1 plan is 67.85 against a 60.00 cap and fails; v2 is 55.20 with a
  2.00 fallback and passes.

## 7. Rights policy

- every required asset has a rights record;
- `cleared` needs a licence or ownership basis and commercial use;
- `needs_approval` and `unknown` are Gate 1 conditions;
- `blocked` and `reference_only` fail;
- AI-generated assets need a disclosure decision;
- people and voices need a consent reference;
- reference Shorts may inform treatment but cannot be bound as assets.

## 8. Validation rules

| Group | Checks |
|---|---|
| Timing | frame count, contiguous shots, contiguous beats, layers inside shots, audio inside timeline, caption CPS and hold, transitions on boundaries |
| Exact data | references resolve, critical commercial fields approved, held copy blocked, claims verified and worded, no orphan approved data |
| Layers | bindings resolve, unique z-order, canvas bounds, safe area, full background, protected regions not occluded, text does not overlap, caption plates, minimum text duration, exactness match, reference-only rejection |
| Budget | cap match, total and worst case under cap, estimate references, reserve, quote basis |
| Rights | required asset position, reference-only rejection, AI disclosure, consent, attribution |
| Traceability | unique IDs, shot/beat/asset/check references, two-way asset usage, must-have coverage, alternate scope, held-item scope, shot status, CTA binding, critical asset fallback |

Each group writes a PASS finding when clean. Failures include the exact target
and a remediation. A structural acceptance check is evaluated only against its
own `rule_refs`: a check fails if one of its rules fails, stays pending if one
of its rules warns, and passes only when its own evidence is clean. An
unrelated budget failure does not mark the timing check failed.

## 9. Critique and the top three

The critic reviews the plan artifact, not the planner's reasoning. It looks for:

- text outside the safe area;
- required unapproved commercial data;
- budget over cap;
- text density;
- a critical exact asset without a fallback or hold;
- unknown rights on a required asset;
- unreadable reading speed;
- a late or missing hook;
- late product visibility;
- other validator failures.

Ranking:

```
priority = impact x confidence x blocking_weight / effort
```

The top three are handled as **auto-resolved** or **escalated**. The revised
plan records every change, and each top-three input must name at least one
target record that changed or was removed in the new revision; otherwise the
revision is refused. All other auto-resolvable findings are applied too and
listed in `applied_fixes`. In the Toffee run:

| Rank | Finding | Mode | Outcome |
|---|---|---|---|
| 1 | safe area | auto | captions and headline moved inside the safe area |
| 2 | commercial data | human | price and offer removed from the ready cut; held for the brand |
| 3 | budget | auto | redundant stock routes removed; fallback kept inside cap |

## 10. Gate 1

Gate 1 requires:

- validation pass on the exact revision;
- every Level 1 check PASS against its own rule references;
- no open blocker or high finding;
- a resolution record for every top-three input, with a verified target diff;
- a named human approver, role and evidence reference;
- an actor kind of `human`; agents and automation are rejected;
- an approval scope drawn only from the ready shots;
- a packet plan hash equal to the plan hash;
- a bundle hash matching the current brief, research, concept, plan,
  validation, critique and resolution.

The packet lists ready shots, held layers, held items, exact data still pending,
conditions and blockers. Approval does not clear a held commercial value; it
approves the plan around it. The approver explicitly names any pending exact
values they approve; unapproved values stay pending in the Level 2 handoff.

## 11. Level 2 handoff

The handoff contains:

- the approval and its plan and bundle hashes;
- approved shots with method, fallback, layer, asset and check IDs;
- asset briefs with rights actions and estimates, filtered to the approved
  scope and the audio cues that overlap it;
- pending Level 2 checks;
- held items and conditions;
- exact data explicitly approved by Gate 1, with everything else in a separate
  pending list.

Level 2 receives an executable brief, not permission to invent missing values.

## 12. Limits of v0.1

- the intake, research and planner are deterministic fixtures, not live LLM
  agents; the interfaces are the extension point;
- no live research adapter is wired;
- no static preview image is rendered; safe-area and occlusion checks are
  geometric;
- one critique cycle and one plan revision are allowed;
- the Toffee test is a planning exercise, not a brand engagement; every
  commercial value remains unapproved;
- the duck fixture from the governing note is deferred because the requested
  scope is one Toffee test run; a `VariantOverride` contract exists but is not
  exercised;
- identity is recorded, not authenticated: the CLI requires a named human, an
  evidence reference and the typed confirmation `APPROVE`, but a local operator
  could still enter false details. Real identity needs an authenticated
  approval channel.
