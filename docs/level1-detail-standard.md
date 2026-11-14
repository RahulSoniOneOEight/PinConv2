# Level 1 detail standard

**Status:** Required for Level 1 review output.
**Scope:** Concept Note, Production Plan, and the Shot × Layer × Asset register.

Level 1 must produce more than a valid record graph. A reviewer, editor,
animator or renderer must be able to understand the creative idea and execute
each shot without inventing a creative, commercial or technical decision.

The test for every field is: **what would the executor still have to invent?**
If the answer can change the outcome, the field is incomplete.

This standard does not add sourcing, purchasing, rendering or publishing to
Level 1. Asset rights status, pending decisions and fallbacks are still recorded
as holds.

## 1. Concept Note

A Concept Note must contain:

| Section | Required detail |
|---|---|
| Brief and success condition | Original brief, communication job, primary viewer, viewing context, desired response, definition of success |
| Audience evidence | Who the viewer is, what they already believe, evidence source and confidence; separate observed evidence from assumption |
| Category and references | Category conventions, references actually inspected, inaccessible channels, borrowed principle versus copied media, distinctiveness |
| The idea | One-line concept, central visual device, emotional turn, why it is native to the format |
| Treatment | Opening image, hook, product entrance, proof or payoff, brand close, what the viewer remembers |
| Hook system | On-screen line, spoken line, visual hook, why they work together, two alternate hooks and their risks |
| Alternatives | At least two credible routes, comparative scoring, reason for the recommendation, evidence that would reverse it |
| Look and sound | Palette, contrast, texture, type behaviour, product prominence, music energy, voice role, sound-off strategy, prohibited content |
| Evidence register | Finding → interpretation → decision, with source, confidence and labelled assumptions |
| Open decisions | Unresolved brand, rights, destination or production inputs; owner and what they block |

## 2. Production Plan

A Production Plan must contain:

| Section | Required detail |
|---|---|
| Deliverable contract | Canvas, aspect ratio, frame rate, frame count, duration, placements, per-placement safe area, caption rules, sound-off requirement, delivery format, variants |
| Timed beats | Frame range, purpose, spoken line, on-screen copy, action, emotion, audio cues, copy and asset references |
| Shot list | Purpose, timing, framing, movement, performance, lighting, colour, continuity, transitions, primary method, fallback, cross-references |
| Asset plan | Identity, use, route, visual brief, technical specification, rights, dependencies, allowed edits, fallback, acceptance condition |
| Audio plan | Voice script with performance notes, music energy and hit points, cue sync frames, mix intent, rights and consent |
| Risk and alternates | Failure triggers, shots that proceed, switch to fallback or wait, what each route preserves, who approves the switch |
| Acceptance and release | Observable checks, method and stage, structural versus rendered versus human checks, what remains pending after Gate 1 |

## 3. Shot record

| Field | Required detail |
|---|---|
| Identity | Shot ID, beat ID, purpose, viewer takeaway |
| Timing | Start, end, duration and handles |
| Composition | Framing, angle, lens intent, subject position, negative space |
| Movement | Camera and object paths, speed, easing, start and end pose |
| Performance | Action, expression, eyeline, start state and end state |
| Light and colour | Key direction, contrast, palette and grade intent |
| Continuity | What must match the adjacent shots |
| Transitions | In and out method, duration and overlap |
| Method | Primary method and a genuinely different fallback |
| Execution detail | Lens intent, editorial handles, audio-cue links and a shot-level acceptance condition |
| Readiness | Plan-ready status separated from rights clearance and production readiness |
| Links | Layer, asset, audio, estimate and acceptance-check IDs |

## 4. Layer record

| Field | Required detail |
|---|---|
| Identity | Layer ID, shot ID and role |
| Timing | Shot-relative in and out, and absolute timing |
| Stack | Z-order, opacity and blend mode |
| Geometry | Canvas rectangle, anchor, scale and rotation |
| Typography | Font, size, weight, colour, alignment, line height, tracking and line limit |
| Motion | Keyframes with frame, position, scale, opacity and easing |
| Effect | Type, trigger frame, duration, intensity, mask and a written effect specification |
| Binding | Asset or copy ID, or an explicitly authored element |
| Protection | Protected region and what must remain visible |
| Exactness | Exact, approved copy or proposed copy |
| Edit limits | What may change without renewed approval |
| Acceptance | What must be true in the rendered frame |

## 4a. Effect record

| Field | Required detail |
|---|---|
| Identity | Effect ID, family, controlled effect name and visual behaviour |
| Research | Selected `EffectAssessment` reference and evidence for the choice |
| Target | Shot and layer, or shot-level effect |
| Timing | Shot-relative trigger and duration |
| Look | Intensity, direction, easing, mask, blend mode |
| Sync | Audio cue or visual hit |
| Fallback | Genuinely different behaviour-preserving route |
| Acceptance | Observable condition in the rendered frame |
| Rights / safety | Licence, consent, safety or disclosure position |
| Owner | Who executes it in Level 2 |
| Status | proposed, approved, held or rejected |

The full catalogue and selection method are in `docs/level1-effects-reference.md`.

## 5. Asset record

| Field | Required detail |
|---|---|
| Identity | Asset ID, version, name and description |
| Usage | Every layer and audio cue that uses it |
| Route | Owned, supplied, captured, created or generated |
| Visual brief | Subject, angle, crop and scale reference |
| Technical specification | Format, resolution, transparency, frame rate, duration and colour |
| Rights | Status, licence basis, commercial use, modification, consent and disclosure |
| Dependencies | What must exist before the asset can be made |
| Allowed edits | Permitted retouch, crop, grade or timing changes |
| Fallback | Alternate asset and the trigger for switching |
| Acceptance | Objective condition for accepting delivery |
| Dependencies | What must exist before the asset can be made |

## 6. Platform review

Placement rules change. Before a plan is called placement-ready:

- check the current platform specification for each intended placement;
- compare the plan's safe area with the published recommendation;
- record a new finding when the approved layout does not match;
- change geometry only through a new plan revision and approval.

A structural validator passing the plan's own geometry is not evidence that the
layout meets a platform's current paid-placement guidance.

## 7. Review gates

| Stage | Reviewer question |
|---|---|
| Concept | Can I approve the idea without asking what it looks, sounds or feels like? |
| Plan | Can a producer schedule this and an editor execute it without inventing a decision? |
| Shot record | Can a renderer build this shot from the record alone? |
| Layer record | Is position, stack, motion, binding and edit authority unambiguous? |
| Asset record | Is the requirement, rights status, fallback and acceptance condition explicit? |

Level 1 output is complete only when these questions can be answered **yes** or
the remaining gap is recorded as an explicit hold.
