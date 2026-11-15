# No-shoot production policy

**Constraint:** there is no camera shoot. Assets are supplied brand files,
licensed stock, licensed stock with AI processing, or AI-generated media
with disclosure.

**Status:** `blocked`

| Asset | Current route | Class | Issue | Recommended route | Note |
|---|---|---|---|---|---|
| `AS-05` | `to_capture` | proof | capture, set build, owned production or recorded voice is not allowed in a no-shoot production | `stock` | stock pour-over hands footage or AI-generated hands; reclassify proof to representative with disclosure |
| `AS-06` | `to_capture` | proof | capture, set build, owned production or recorded voice is not allowed in a no-shoot production | `stock` | stock hot-water pour/bloom footage or AI-generated clip; reclassify proof to representative with disclosure |
| `AS-07` | `owned` | atmospheric | capture, set build, owned production or recorded voice is not allowed in a no-shoot production | `stock` | stock kitchen background or AI-generated background; atmospheric allows it |
| `AS-08` | `to_capture` | proof | capture, set build, owned production or recorded voice is not allowed in a no-shoot production | `stock` | stock finished-cup footage or AI-generated cup; reclassify proof to representative with disclosure |
| `AS-09` | `to_create` | representative | capture, set build, owned production or recorded voice is not allowed in a no-shoot production | `generate` | AI TTS voice (AS-15 route) or licensed voice; no camera shoot needed |
| `AS-11` | `owned` | atmospheric | capture, set build, owned production or recorded voice is not allowed in a no-shoot production | `stock` | stock pour SFX or AI audio generation |
| `AS-12` | `owned` | atmospheric | capture, set build, owned production or recorded voice is not allowed in a no-shoot production | `generate` | AI-generated or licensed brand sting |
| `AS-13` | `to_capture` | exact | capture, set build, owned production or recorded voice is not allowed in a no-shoot production | `supplied` | use the supplied AS-02 pack image; remove the capture fallback |

## Rules

- `exact` product/pack/logo stays supplied; never stock or generated.
- `proof` cannot survive without a capture; reclassify to representative
  with disclosure, replace with stock/AI, or drop the proof claim.
- `atmospheric` and `representative` may use stock, stock + AI, or AI
  generation with disclosure.
- A human must approve any proof-to-representative change and any
  synthetic replacement before Gate 2A.
