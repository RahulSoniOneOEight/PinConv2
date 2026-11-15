# Production plan — blue-tokai-easy-pour-20s rev-002

**Run:** `rev-002` · **Plan hash:** `1370f029b0b35730625c459cf85579bfd767d2e4a7b62016055e100d15f2aba5`
**Status:** Gate 2A `ready_for_approval`; no paid acquisition or generation yet.

## Sequence

| Shot | Frames | Layers | Assets | Ready | Blockers |
|---|---|---|---|---|---|
| SH-01 | 0–75 | 6 | AS-02, AS-07 | no | HI-02 |
| SH-02 | 75–160 | 6 | AS-02, AS-05, AS-07 | no | HI-02, HI-04 |
| SH-03 | 160–275 | 6 | AS-02, AS-06, AS-07 | no | HI-02, HI-04 |
| SH-04 | 275–380 | 8 | AS-02, AS-03, AS-04, AS-07, AS-17 | no | HI-02 |
| SH-05 | 380–445 | 6 | AS-02, AS-07, AS-08 | no | HI-02, HI-04 |
| SH-06 | 445–500 | 6 | AS-01, AS-02, AS-07 | no | HI-02 |

## Asset queue

| Order | Asset | Current route | Action | No-shoot route | Shots | Rights / hold | Gate |
|---|---|---|---|---|---|---|---|
| 1 | `AS-01` Blue Tokai Coffee Roasters logo | supplied | Obtain rights and import the supplied file | keep | SH-06 | needs_approval / `HI-02` | Level 1 / rights |
| 2 | `AS-02` Easy Pour Mixed Bag pack | supplied | Obtain rights and import the supplied file | keep | SH-01, SH-02, SH-03, SH-04, SH-05, SH-06 | needs_approval / `HI-02` | Level 1 / rights |
| 3 | `AS-03` Easy Pour Vienna pack | supplied | Obtain rights and import the supplied file | keep | SH-04 | needs_approval / `HI-02` | Level 1 / rights |
| 4 | `AS-04` Easy Pour Attikan Estate pack | supplied | Obtain rights and import the supplied file | keep | SH-04 | needs_approval / `HI-02` | Level 1 / rights |
| 5 | `AS-09` Voice over, warm Indian English | supplied | AI TTS voice (AS-15 route) or licensed voice; no camera shoot needed | generate | - | needs_approval / `HI-03` | Level 1 / rights |
| 6 | `AS-17` Easy Pour Seethargundu Estate pack | supplied | Obtain rights and import the supplied file | keep | SH-04 | needs_approval / `HI-02` | Level 1 / rights |
| 7 | `AS-05` Easy Pour brewing demonstration, hands | capture | stock pour-over hands footage or AI-generated hands; reclassify proof to representative with disclosure | stock | SH-02 | needs_approval / `HI-04` | Level 1 / rights |
| 8 | `AS-06` Hot water pour and bloom footage | capture | stock hot-water pour/bloom footage or AI-generated clip; reclassify proof to representative with disclosure | stock | SH-03 | needs_approval / `HI-04` | Level 1 / rights |
| 9 | `AS-08` Finished cup of coffee | capture | stock finished-cup footage or AI-generated cup; reclassify proof to representative with disclosure | stock | SH-05 | needs_approval / `HI-04` | Level 1 / rights |
| 10 | `AS-13` Captured Mixed Bag fallback | capture | use the supplied AS-02 pack image; remove the capture fallback | supplied | - | needs_approval / `HI-02` | Level 1 / rights |
| 11 | `AS-10` Music bed, 20 seconds | stock | Acquire the chosen licence after Gate 2A | keep | - | needs_approval / `HI-03` | Gate 2A |
| 12 | `AS-14` Music fallback track | stock | Acquire the chosen licence after Gate 2A | keep | - | needs_approval / `HI-03` | Gate 2A |
| 13 | `AS-15` Synthetic narration fallback | generate | Use only as a disclosed fallback | keep | - | needs_approval / `HI-03` | Gate 2A |
| 14 | `AS-07` Warm kitchen background | owned | stock kitchen background or AI-generated background; atmospheric allows it | stock | SH-01, SH-02, SH-03, SH-04, SH-05, SH-06 | cleared | Level 1 / rights |
| 15 | `AS-11` Water pour sound effect | owned | stock pour SFX or AI audio generation | stock | - | cleared | Level 1 / rights |
| 16 | `AS-12` Brand sting | owned | AI-generated or licensed brand sting | generate | - | cleared | Level 1 / rights |

## Layer plan

| Shot | Layer | Asset | Method | Class | Impact | Pick |
|---|---|---|---|---|---|---|
| SH-01 | `LY-010` | AS-07 | M0 | atmospheric | medium (4) | human |
| SH-01 | `LY-011` | AS-02 | M0 | exact | high (8) | human |
| SH-01 | `LY-012` | procedural | M4 | atmospheric | medium (4) | human |
| SH-01 | `LY-013` | copy:CP-01 | M4 | exact_text | high (8) | human |
| SH-01 | `LY-014` | procedural | M4 | representative | medium (3) | human |
| SH-01 | `LY-015` | copy:CP-07 | M4 | exact_text | high (5) | human |
| SH-02 | `LY-020` | AS-07 | M0 | atmospheric | low (2) | automatic |
| SH-02 | `LY-021` | AS-05 | M6 | proof | high (5) | human |
| SH-02 | `LY-022` | AS-02 | M0 | exact | high (6) | human |
| SH-02 | `LY-023` | copy:CP-03 | M4 | exact_text | high (6) | human |
| SH-02 | `LY-024` | procedural | M4 | representative | low (1) | automatic |
| SH-02 | `LY-025` | copy:CP-08 | M4 | exact_text | medium (3) | human |
| SH-03 | `LY-030` | AS-07 | M0 | atmospheric | low (2) | automatic |
| SH-03 | `LY-031` | AS-06 | M6 | proof | high (5) | human |
| SH-03 | `LY-032` | AS-02 | M0 | exact | high (6) | human |
| SH-03 | `LY-033` | copy:CP-02 | M4 | exact_text | medium (3) | human |
| SH-03 | `LY-034` | procedural | M4 | representative | low (1) | automatic |
| SH-03 | `LY-035` | copy:CP-09 | M4 | exact_text | medium (3) | human |
| SH-04 | `LY-040` | AS-07 | M0 | atmospheric | low (2) | automatic |
| SH-04 | `LY-041` | AS-02 | M0 | exact | high (6) | human |
| SH-04 | `LY-042` | AS-03 | M0 | exact | high (6) | human |
| SH-04 | `LY-043` | AS-04 | M0 | exact | high (6) | human |
| SH-04 | `LY-047` | AS-17 | M0 | exact | high (6) | human |
| SH-04 | `LY-044` | copy:CP-04 | M4 | exact_text | high (6) | human |
| SH-04 | `LY-045` | procedural | M4 | representative | low (1) | automatic |
| SH-04 | `LY-046` | copy:CP-10 | M4 | exact_text | medium (3) | human |
| SH-05 | `LY-050` | AS-07 | M0 | atmospheric | low (2) | automatic |
| SH-05 | `LY-051` | AS-08 | M6 | proof | high (5) | human |
| SH-05 | `LY-052` | AS-02 | M0 | exact | high (6) | human |
| SH-05 | `LY-053` | copy:CP-13 | M4 | exact_text | medium (3) | human |
| SH-05 | `LY-054` | procedural | M4 | representative | low (1) | automatic |
| SH-05 | `LY-055` | copy:CP-12 | M4 | exact_text | medium (3) | human |
| SH-06 | `LY-060` | AS-07 | M0 | atmospheric | low (2) | automatic |
| SH-06 | `LY-061` | AS-02 | M0 | exact | high (6) | human |
| SH-06 | `LY-062` | AS-01 | M0 | exact | high (6) | human |
| SH-06 | `LY-063` | copy:CP-05 | M4 | exact_text | high (6) | human |
| SH-06 | `LY-064` | procedural | M4 | representative | low (1) | automatic |
| SH-06 | `LY-065` | copy:CP-11 | M4 | exact_text | medium (3) | human |

## Production notes

- Supplied brand files and proof captures are non-negotiable; stock and
  generation are not substitutes.
- Stock audio (`AS-10`, `AS-14`) is still a preview until Gate 2A and the
  final licence.
- `AS-15` is a disclosed fallback only; the Edge TTS sample is not an
  approved final voice.
- Every paid provider call is reserved and receipted through the
  provider governor.
