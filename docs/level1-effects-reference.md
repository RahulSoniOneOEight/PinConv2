# Level 1 effects reference

**Status:** Global reference for every Level 1 run.
**Scope:** Effect planning for ads, product films, explainers, tutorials, brand films,
social content, training and other screen formats.
**Boundary:** Level 1 describes and validates effects. It does not render, simulate,
source or publish them. Level 2 executes them.

Related documents:

- `docs/level1-detail-standard.md` — required Concept Note and Shot × Layer × Asset detail.
- `docs/level1.md` — contracts, state machine and Gate 1 rules.
- `docs/architecture.md` — the four-level operating model.

---

## 1. Why effects matter

An effect is not decoration. It is a **controlled visual change** that helps the viewer
understand, feel or believe something they would otherwise miss.

Effects matter because they:

- **Reveal** what the eye cannot see at normal speed or scale — a label, a bloom, a
  texture, a mechanism.
- **Connect** two ideas — pack to cup, ingredient to product, problem to result.
- **Compress** time honestly — a steep, a commute, a build, a transformation.
- **Direct attention** — a light sweep, focus pull, callout or motion path tells the
  viewer where to look.
- **Create meaning** — warmth, energy, precision, luxury, play or urgency.
- **Make the product legible** in the actual placement — phone scale, sound off,
  captions and platform UI.

### The planning rule

> **Every effect must earn its place by changing what the viewer understands, feels or
> believes. If it only decorates, remove it.**

An effect also carries cost and risk: render time, rights, safety, continuity, label
accuracy and disclosure. Level 1 must record those before Level 2 spends money.

### Three different things

| Term | Meaning | Example |
|---|---|---|
| **Effect** | A visual change applied to a layer, subject or frame | Steam drift, light sweep, liquid splash, particle reveal |
| **Transition** | A change from one shot to another | Match cut, light wipe, whip pan, time-lapse resolve |
| **Behaviour** | The job the effect or transition performs | Reveal, emphasise, connect, transform, compress |

A single technique can serve different behaviours. A whip pan can be **pace** in an ad,
**connection** in a tutorial, or **orientation** in a product film. The planner records
the behaviour, not just the technique name.

### Honesty rules

- A compressed brew, build or journey must be **disclosed** when the audience could
  otherwise assume real time.
- A simulation must not be presented as documentary evidence.
- AI-generated or AI-edited media needs an explicit disclosure decision.
- Product geometry, labels, counts, prices and claims remain exact records. An effect may
  not “improve” them into something untrue.
- Practical fire, water, glass, talent or vehicles need a safety and rights position.

---

## 2. Effect families

Use one **use cases** column. The same effect can serve an ad, a product film, an
explainer, a tutorial, a brand film or social content; the difference is purpose,
duration and proof.

| Effect family | Typical effects | Visual behaviour | Use cases | Where executed | Key parameters | Risks / fallback |
|---|---|---|---|---|---|---|
| **Camera / in-camera** | Push-in, pull-out, orbit, truck, tilt, crash zoom, whip pan, handheld, speed ramp, macro probe | Reveal, intensify, follow, disorient | Product ads, product showcase, brand films, real-estate tours, event films, sports edits, music videos | Capture / camera department | Path, speed, easing, lens, start and end pose, stabilisation | Motion sickness, unstable horizon, unreadable labels; fallback to locked-off or slow push |
| **Focus** | Rack focus, split diopter, shallow/deep focus, focus pull between pack and label | Direct attention, connect subjects | Pack-to-cup ads, before/after films, tutorials, explainers, interviews, documentary detail | Capture / focus puller | Near and far subject, pull timing, aperture, focal length | Focus hunting, soft label; fallback to deeper focus or cut |
| **Lighting** | Light sweep, hard/soft key, rim light, practicals, flicker, shadow play, day/night shift | Sculpt, reveal, signal time or mood | Premium product ads, beauty films, festive campaigns, brand films, music videos, narrative scenes | Set / lighting / grade | Direction, speed, falloff, colour temperature, intensity, mask | Label glare, inconsistent grade, unlicensed fixtures; fallback to static key |
| **Liquid / food** | Pour, splash, drip, bloom, steam, condensation, bubbles, viscosity, crumb, cheese pull | Appetite, freshness, tactility | Coffee and beverage ads, food films, recipe tutorials, cooking shows, menu promos, beauty serum demos | Practical shoot / CGI / compositing | Fluid volume, pour height, splash shape, temperature cue, frame rate, mask | Fake pours, food-safety staging, continuity, time compression; fallback to still with animated steam |
| **Product behaviour** | Pack rise, float, rotate, hero turn, label reveal, cap pop, explode view, parts assembly, powder dust, mist | Explain, reveal, premiumise | Product ads, e-commerce loops, range reveals, tech explainers, assembly guides, hardware demos | Capture / 3D / compositing | Start/end pose, axis, rotation, scale, label protection, shadow | Product geometry errors, label distortion, file rights; fallback to supplied still |
| **Practical atmosphere** | Smoke, haze, wind, rain, snow, dust, sparks, fire, confetti, fabric flow | Energy, atmosphere, scale | Festive retail ads, sports films, fashion, narrative films, music videos, event promos | Set / practical effects / VFX | Density, direction, speed, colour, safety zone, cleanup | Fire/safety permits, continuity, cleanup, talent safety; fallback to clean plate plus graded atmosphere |
| **Editorial** | Hard cut, match cut, jump cut, whip-pan transition, light wipe, splash wipe, shape wipe, freeze frame, speed ramp, time-lapse, stop motion, split screen, flash frame | Compress time, connect ideas, create rhythm | 10–30s ads, demo montages, range reveals, explainer chapters, tutorial steps, social recaps, documentary montages | Edit | In/out frames, overlap, speed curve, matching point, hold | Over-cutting, transitions hiding product errors, misleading time distortion; fallback to straight cut |
| **Motion graphics / type** | Kinetic type, mask reveal, type-on, tracking, underline, highlight, sticker, lower third, end card, logo lockup, label callout, diagram, data viz | Explain, emphasise, brand | Hooks, claims, CTAs, price/offer cards, explainers, tutorials, SaaS demos, training modules, corporate reports | Motion design / edit | Font, size, weight, colour, line count, reading frames, safe area, in/out | Reading speed, safe area, caption duplication, font rights; fallback to static type card |
| **Compositing / VFX** | Chroma key, clean-up, screen replacement, sky replacement, set extension, product replacement, 3D pack, CGI liquid, particles, smoke simulation, light wrap, lens flare, depth of field, motion blur, parallax, 2.5D, camera tracking, stabilisation, paint-out, clone, morph, dissolve | Construct impossible or expensive images | Product hero ads, liquid beauty, fantasy films, narrative scenes, architecture visualisation, training simulations, music videos | VFX / compositing | Plate, track, mask, matte, light direction, blend, grain, render cost | Cost, render time, uncanny results, product accuracy, disclosure; fallback to practical still or simpler comp |
| **Colour / finish** | Grade, bleach bypass, film emulation, halation, grain, bloom, vignette, split tone, LUT, flicker | Unify, stylise, age, premiumise | Whole-film looks for ads, brand films, documentaries, narrative films, archive-style pieces, music videos | Grade / finishing | LUT or reference, contrast, saturation, skin tone, pack colour, grain | Brand colour accuracy, skin tones, pack shift; fallback to neutral grade |
| **Sound-synced visual** | Beat hit, whoosh, splash sync, bass pulse, waveform, speaker vibration, caption pop | Sync image to audio | Music-led ads, transition hits, CTA stings, music videos, lyric videos, podcast visualisation, event openers | Edit / sound / motion | Hit frame, offset, amplitude, decay, audio cue, sound-off fallback | Rights, sync drift, sound-off comprehension; fallback to caption or visual beat |
| **Platform / delivery** | Safe-area overlay, caption pop, progress cue, CTA card, loop, thumbnail frame, 9:16 reframe, 16:9 master, 1:1 crop | Make the film legible in placement | YouTube ads, Reels/Shorts, feed ads, e-learning, website heroes, trade-show loops, internal comms, e-commerce PDPs | Edit / delivery | Placement, safe area, crop, caption mode, loop point, CTA position | Platform UI changes, caption burn-in vs SRT, crop losing label or CTA; fallback to a placement-specific master |

### Choosing an effect

Ask four questions in order:

1. **What must the viewer understand or feel?**
2. **Is the effect proving something or decorating?**
3. **Can it be done honestly at this duration and budget?**
4. **Will it survive phone scale, sound-off, captions and the final crop?**

If the answer to question 1 is unclear, do not plan the effect.

---

## 3. Visual behaviours

A behaviour is the job an effect performs. Two effects in different families can have the
same behaviour. Record the behaviour even when the technique changes.

| Behaviour | Meaning | Example | Agent test | Failure mode |
|---|---|---|---|---|
| **Reveal** | Hide, then disclose something the viewer needs | A light sweep exposes a pack label; a mask opens to a product | Is the newly visible element clear by the intended frame? | Reveal is too fast, too dark, or exposes the wrong thing |
| **Emphasise** | Make one element momentarily dominant | Push-in on the CTA; a highlight ring around a claim | Does the eye land on the intended element first? | Everything is emphasised, so nothing is |
| **Connect** | Link two shots, objects or ideas | Match cut from pack label to cup; ingredient falls into the product | Does the connection read without a caption? | The match is arbitrary or hides a continuity break |
| **Transform** | Show a change of state | Beans become grounds; water blooms the coffee; a blank page becomes a plan | Is the before and after unmistakable? | The middle state is skipped or physically wrong |
| **Simulate** | Add believable physical behaviour | Steam, splash, condensation, fabric movement, particles | Does it obey the scene’s physics and product geometry? | The simulation looks generic or contradicts the product |
| **Compress** | Collapse time | Time-lapse of a steep, commute, build or sunset | Is the time change disclosed or conventionally clear? | Viewer assumes real time and feels misled |
| **Orient** | Tell the viewer where to look or what is connected | Label callout, arrow, diagram, split screen, highlight | Can a first-time viewer follow without pausing? | Too many labels; the eye jumps |
| **Pace** | Control energy and rhythm | Whip pan, speed ramp, flash cut, beat hit | Does the pace serve the message rather than fight it? | Fatigue, lost product detail, unreadable copy |
| **Brand** | Reassert identity or personality | Logo lockup, brand sting, colour signature, end-card motion | Is the brand recognisable with sound off? | Brand appears only at the end; effect overwhelms identity |
| **Prove** | Provide evidence for a claim or benefit | Real filter clipped to a mug; water hitting grounds; finished cup | Does the effect show the actual mechanism or result? | Effect implies a proof the product does not deliver |

### Behaviour-to-effect examples

| Behaviour | Common effect choices | Better for | Weaker for |
|---|---|---|---|
| Reveal | Light sweep, mask reveal, pack rise, rack focus | Product, pack, label, feature | Long explanatory sequences |
| Emphasise | Push-in, highlight, callout, freeze frame | CTA, claim, price, single feature | Range or multi-product stories |
| Connect | Match cut, whip pan, morph, sound bridge | Demo, process, before/after | Dense product catalogues |
| Transform | Time-lapse, dissolve, assembly, liquid simulation | Brewing, cooking, manufacturing, makeover | Exact product geometry without references |
| Simulate | Steam, splash, particles, cloth, smoke | Atmosphere, food, beauty, weather | Documentary evidence |
| Compress | Time-lapse, speed ramp, montage | Brew, build, commute, day cycle | Legal or safety-critical process |
| Orient | Diagram, arrows, labels, split screen | Explainer, tutorial, training | Premium mood film |
| Pace | Whip pan, flash cut, beat edit, speed ramp | Social, sports, music, fashion | Complex product detail |
| Brand | Logo lockup, end card, sting, colour | Every ad, brand film, sponsorship | Long-form documentary where brand must stay implicit |
| Prove | Real demo, macro, before/after, measured comparison | Product claims, tutorials, efficacy | Unsubstantiated or simulated proof |

---

## 4. What the agent must record for each effect

Every effect needs a record that another person or tool can execute without inventing a
decision. The record belongs to the plan, not to a chat message.

```yaml
effect:
  id: FX-01
  family: camera | focus | lighting | liquid_food | product | practical |
          editorial | motion_type | vfx | colour | sound_sync | platform
  name: light_sweep
  behaviour: reveal | emphasise | connect | transform | simulate |
             compress | orient | pace | brand | prove
  target_shot: SH-02
  target_layer: LY-022
  trigger_frame: 0
  duration_frames: 20
  intensity: 0.55
  direction: left_to_right
  easing: ease_out
  mask_region: {x: 160, y: 460, w: 760, h: 940}
  blend_mode: screen
  sync_cue: AU-03
  fallback: static_key_with_type_fade
  acceptance: "Pack label remains readable; sweep clears the frame by f20."
  rights_or_safety: "No third-party footage; practical light only."
  owner: motion_design
  status: proposed
```

### Required fields

| Field | What it must answer |
|---|---|
| `id` | Stable effect ID, unique in the plan |
| `family` | Which production family owns it |
| `name` | Controlled effect name from the catalogue |
| `behaviour` | What job it performs for the viewer |
| `target_shot` | Which shot it belongs to |
| `target_layer` | Which layer it changes, or `null` for a whole-frame effect; the target shot is named separately |
| `trigger_frame` | Exact start frame |
| `duration_frames` | Exact duration; must fit the shot |
| `intensity` | How strong it is, with a defined scale |
| `direction` | Direction, axis or path |
| `easing` | Linear, ease-in, ease-out, custom curve |
| `mask_region` | Where the effect is allowed |
| `blend_mode` | Screen, multiply, overlay, normal, etc. |
| `sync_cue` | Audio cue or visual hit it follows |
| `fallback` | What replaces the effect if it fails |
| `acceptance` | Observable condition in the rendered frame |
| `rights_or_safety` | Licence, consent, safety or disclosure position |
| `owner` | Who executes it in Level 2 |
| `status` | proposed, approved, held or rejected |

### Validation rules

The agent should reject an effect when:

- it has no target layer or shot;
- its trigger or duration falls outside the shot;
- it covers an exact label, logo or protected region;
- it is the only proof of a claim and has no fallback;
- it compresses time without a disclosure decision;
- it uses third-party media without a rights record;
- it requires a practical hazard without a safety position;
- its acceptance condition cannot be observed;
- it exists only to decorate and has no stated behaviour.

---

## 5. How effects operate through the levels

### Level 1 — Plan

1. Name the behaviour before the technique.
2. Choose the simplest effect family that achieves it.
3. Record the full effect specification.
4. Check timing, safe area, occlusion, exactness, rights and budget.
5. Record a fallback that preserves the same behaviour.
6. Add an acceptance condition.
7. Send the effect to Gate 1 as part of the shot plan.

### Level 2 — Produce

1. Assign the effect to the correct owner: camera, set, edit, motion, VFX, grade or sound.
2. Build a test or animatic for timing and legibility.
3. Check the effect against the protected regions and exact content.
4. Compare the fallback before committing expensive simulation or cleanup.
5. Record the version actually used.

### Level 3 — Review and deliver

1. Check the effect at final phone scale, sound off.
2. Check the effect against platform UI and captions.
3. Check exact pixels, label readability and disclosure.
4. Confirm the effect did not introduce a rights or safety issue.
5. Deliver the approved effect version with the master.

### Level 4 — Learn

1. Record whether the effect improved attention, comprehension or conversion.
2. Compare effect variants where the test design allows.
3. Retire effects that add cost without evidence.
4. Feed the result back into the effect catalogue.

---

## 6. Effect budget and restraint

Effects are not free. Each one adds:

- planning time;
- capture or render time;
- review cycles;
- rights or safety work;
- continuity risk;
- another thing that can fail.

A practical default for short-form work:

| Duration | Suggested maximum simultaneous effects | Reason |
|---|---|---|
| 6–10s | 2–3 | One hook, one proof, one brand behaviour |
| 10–20s | 3–5 | Room for demo, range and close |
| 20–60s | 5–8 | Chapter changes and proof beats |
| 60s+ | Budget by scene | Each scene needs its own effect logic |

These are starting points, not rules. The real limit is whether the viewer can still
understand the product and the next action.

---

## 7. Example — Blue Tokai Easy Pour

The Blue Tokai plan uses effects only where they prove or clarify the benefit:

| Shot | Effect or behaviour | Why it exists | Fallback |
|---|---|---|---|
| SH-01 | `steam_drift`, pack settle | Signal fresh coffee and reveal the pack | Static pack with type fade |
| SH-02 | Match cut, real-time tear/anchor | Prove the built-in filter | Stop-motion of the same steps |
| SH-03 | Macro pour, bloom, time-lapse | Show water hitting grounds and compress the real brew | Still pour plate with animated steam |
| SH-04 | Four-pack fan, staggered fades | Make light-to-dark concrete | Captured four-pack still |
| SH-05 | Finished-cup steam, time-lapse resolve | Show the result and disclose compression | Still cup with animated steam |
| SH-06 | CTA and caption fades | Land the action and brand | Static end card with pack |

The plan does **not** add particles, lens flares, fake UI or spectacle. The product
demonstration is the effect.

---

## 8. Quick checklist

Before approving any effect:

- [ ] Behaviour is named.
- [ ] Technique is the simplest one that works.
- [ ] Target shot and layer exist.
- [ ] Trigger and duration fit the shot.
- [ ] Exact labels and protected regions stay clear.
- [ ] Copy remains readable at phone scale.
- [ ] Time compression is disclosed.
- [ ] Rights, consent, safety and AI disclosure are recorded.
- [ ] A genuinely different fallback exists.
- [ ] Acceptance is observable.
- [ ] The effect survives sound-off and the final crop.
- [ ] The effect earns its cost.
