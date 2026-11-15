# No in-house production policy

Assets are produced only by: **licensed stock**, **AI generation**, or
**AI enhancement of stock**. There is no camera shoot, set build, in-house
voice session or manual pack preparation.

**Status:** `ready` · AI share 18.8% (cap 40%) · generated: AS-09, AS-12, AS-15

## In-kind line replacements

| Line | Original line | Method | Replacement |
|---|---|---|---|
| `ES-01` | Music library licence | `stock` | licensed CC0/CC BY music track |
| `ES-02` | Voice artist session and edit | `generate` | AI TTS voice (ShortGPT or fal/Runware) |
| `ES-03` | Edit, motion and compositing | `tool` | OpenMontage edit + compositing |
| `ES-04` | Colour grade and finishing | `tool` | AI-enhanced grade or deterministic LUT |
| `ES-05` | Mixed Bag pack preparation | `enhance` | AI label-preserving cutout of the supplied pack |
| `ES-06` | Demo and finished-cup capture | `stock` | stock pour/cup footage, AI-enhanced if needed |
| `ES-07` | Range pack preparation | `enhance` | AI label-preserving cutout of the supplied packs |
| `ES-08` | End-card build | `generate` | HyperFrames end card + AI brand sting |
| `ES-09` | Captured pack fallback | `stock` | stock pack-fallback footage, AI-enhanced |
| `ES-11` | 9:16 vertical re-edit and end-card rebuild | `tool` | OpenMontage 9:16 re-edit |

## Budget rule

- `stock` — licensed, mostly free (CC0/CC BY/Pexels/Pixabay/Unsplash).
- `enhance` — AI processing of stock; does not count against the 40% cap.
- `generate` — original AI media; counted against the 40% cap and the
  $2.00 provider budget (fal/Runware, $0.50 per job).
- `tool` — OpenMontage / HyperFrames / ffmpeg processing, $0.
