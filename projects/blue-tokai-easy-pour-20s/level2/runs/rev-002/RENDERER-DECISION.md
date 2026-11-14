# Renderer decision — HyperFrames vs Remotion

**Project:** `blue-tokai-easy-pour-20s` · **Run:** `rev-002`
**Status:** awaiting named-human acceptance
**Recorded:** 2026-11-15

## What is installed

| Renderer | State |
|---|---|
| OpenMontage HyperFrames | installed, `0.8.123`, real render verified |
| Remotion CLI | **not installed** on this machine |
| ffmpeg | installed, `9.0.2` |

The verified OpenMontage capability render used HyperFrames:

- `1920x1080`, 30 fps, 60 frames, 2.0 s
- SHA-256 `a271844321fe1127d01ebe1d2faca911db2e0a24073609bcdc11ec22e21a1ceb`
- verification `passed`
- budget `$2.00`, spent `$0.00`

## Why this is a decision, not a defect

The original tool note said “Remotion render”. OpenMontage Studio’s installed
composition renderer is HyperFrames, and Remotion is not present. HyperFrames is
the renderer Studio actually ships here; its output is verified and editable.

## Options

| Option | What it means | Cost / risk |
|---|---|---|
| **A. Accept HyperFrames** | Use the installed renderer for this production and future OpenMontage compositions | No install; keep the verified render path |
| **B. Install Remotion** | Add the Remotion CLI and re-run the capability render before production | New dependency; render path and review evidence must be re-verified |
| **C. Defer** | Do not approve either; render remains blocked | Production cannot finish |

## Human acceptance

If option A is chosen, sign here:

- Name:
- Role:
- Date:
- Evidence / ticket:

> “I accept HyperFrames `0.8.123` as the renderer for the Blue Tokai Level 2
> production. Remotion is not required for this run.”

If option B is chosen, record the install evidence and re-run
`level2 omcheck` before production.

## Agent rule until signed

- Do not claim Remotion was used.
- Do not install or switch renderers without a named-human instruction.
- Keep the HyperFrames render hash and verification in every status report.
