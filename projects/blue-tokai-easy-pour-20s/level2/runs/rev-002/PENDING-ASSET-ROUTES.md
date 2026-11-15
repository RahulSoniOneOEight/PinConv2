# Pending asset routes — no-shoot production

**Project:** `blue-tokai-easy-pour-20s` · **Run:** `rev-002`
**Constraint:** there is no camera shoot. Every asset must be one of:

- a supplied brand file;
- licensed stock;
- licensed stock with AI processing;
- AI-generated media, disclosed.

**Status:** the current plan still contains capture and owned-production routes,
so the no-shoot policy is `blocked`. See `NO-SHOOT-POLICY.md`.

## Asset-by-asset

| Asset | What | Current route | No-shoot route | Action |
|---|---|---|---|---|
| `AS-01` | Blue Tokai logo | supplied | **keep supplied** | Use the approved brand file |
| `AS-02` | Easy Pour Mixed Bag pack | supplied | **keep supplied** | Use the approved pack image |
| `AS-03` | Easy Pour Vienna pack | supplied | **keep supplied** | Use the approved pack image |
| `AS-04` | Easy Pour Attikan Estate pack | supplied | **keep supplied** | Use the approved pack image |
| `AS-17` | Easy Pour Seethargundu Estate pack | supplied | **keep supplied** | Use the approved pack image |
| `AS-05` | Brewing demonstration, hands | capture | **stock / AI** | Stock pour-over hands or AI-generated hands; reclassify proof to representative |
| `AS-06` | Hot water pour and bloom | capture | **stock / AI** | Stock pour/bloom footage or AI-generated clip; reclassify proof |
| `AS-07` | Warm kitchen background | owned set build | **stock / AI** | Stock kitchen plate or AI-generated background; atmospheric allows it |
| `AS-08` | Finished cup | capture | **stock / AI** | Stock finished-cup footage or AI-generated cup; reclassify proof |
| `AS-09` | Voice over | supplied voice session | **AI TTS / licensed voice** | Use the `AS-15` TTS route or a licensed voice |
| `AS-10` | Music bed | stock | **stock** | Licence the chosen ccMixter track |
| `AS-11` | Water pour SFX | owned foley | **stock / AI** | Stock pour SFX or AI audio generation |
| `AS-12` | Brand sting | owned sting | **AI / stock** | AI-generated or licensed brand sting |
| `AS-13` | Captured Mixed Bag fallback | capture | **supplied** | Use the supplied `AS-02` pack image; remove the capture fallback |
| `AS-14` | Music fallback | stock | **stock** | Licence the chosen ccMixter fallback |
| `AS-15` | Synthetic narration fallback | generate | **generate** | Disclosed AI TTS fallback |

## What cannot change

- `AS-01`, `AS-02`, `AS-03`, `AS-04`, `AS-17` are exact brand assets. They remain
  **supplied files**. Stock or AI generation would break the exact rule.
- `AS-05`, `AS-06`, `AS-08` are currently `proof`. Without a shoot they cannot
  remain proof. They must become `representative` with disclosure, or the proof
  claim must be removed.
- Stock and AI-generated replacements need a licence/disclosure decision before
  they can enter Gate 2A.

## Immediate order of work

1. Clear `HI-02` for the logo and four pack images.
2. Choose stock or AI for `AS-05`, `AS-06`, `AS-08`, `AS-07`, `AS-11`, `AS-12`.
3. Replace `AS-13` with the supplied `AS-02` pack image.
4. Use AI TTS for `AS-09`, or license a voice.
5. Re-run the plan so the no-shoot routes become the approved methods, then
   re-open Gate 2A.
