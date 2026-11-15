# Asset visual QC

Agent visual inspection of the available asset files. This checks the
asset itself, not the shot storyboard preview.

| Asset | Verdict | Reviewer | Note |
|---|---|---|---|
| `AS-01` | **warn** | agent:multimodal | Clean transparent logo, correct Blue Tokai lockup; 188x128 px may soften if scaled beyond 1x at 1080p. Request vector or larger master. |
| `AS-02` | **pass** | agent:multimodal | Mixed Bag pack front is sharp, correct product identity, label legible, no watermark. |
| `AS-03` | **pass** | agent:multimodal | Vienna Roast pack front is sharp, correct product identity, label legible, no watermark. |
| `AS-04` | **pass** | agent:multimodal | Attikan Estate pack front is sharp, correct product identity, label legible, no watermark. |
| `AS-05` | **pending** | agent:multimodal | No capture file yet; visual QC waits for the demonstration shoot. |
| `AS-06` | **pending** | agent:multimodal | No capture file yet; visual QC waits for the demonstration shoot. |
| `AS-07` | **pending** | agent:multimodal | Owned background plate has no delivered file yet. |
| `AS-08` | **pending** | agent:multimodal | No capture file yet; visual QC waits for the demonstration shoot. |
| `AS-09` | n/a | agent:multimodal | Audio asset; visual QC does not apply. |
| `AS-10` | n/a | agent:multimodal | Audio preview; visual QC does not apply. |
| `AS-11` | n/a | agent:multimodal | Audio asset; visual QC does not apply. |
| `AS-12` | n/a | agent:multimodal | Audio asset; visual QC does not apply. |
| `AS-13` | **pending** | agent:multimodal | Conditional capture fallback; no file unless triggered. |
| `AS-14` | n/a | agent:multimodal | Audio preview; visual QC does not apply. |
| `AS-15` | n/a | agent:multimodal | Audio sample; visual QC does not apply. |
| `AS-17` | **pass** | agent:multimodal | Seethargundu Estate pack front is sharp, correct product identity, label legible, no watermark. |

## Limits

- Pending captures cannot be visually reviewed before the shoot.
- Audio assets are marked `n/a`; they need audio QC, not visual QC.
- A `warn` is a review decision, not an automatic rejection.
