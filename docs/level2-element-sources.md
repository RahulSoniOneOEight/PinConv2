# Element and effect sources — live probe

**Date:** 2026-11-15
**Method:** direct HTTPS request from this machine, no key, 25-second timeout,
browser user agent.
**Meaning:** `200` means the asset endpoint answered; the licence still has to be
read per file/set.

## Icons — accessible now

| Source | Endpoint tested | Status | Licence |
|---|---|---|---|
| Iconify API | `api.iconify.design/lucide.json?icons=coffee` | **200** | Per-set; resolve the set licence |
| Iconify SVG | `api.iconify.design/lucide/coffee.svg` | **200** | Per-set |
| Lucide CDN | `cdn.jsdelivr.net/npm/lucide-static` | **200** | ISC |
| Tabler CDN | `cdn.jsdelivr.net/npm/@tabler/icons` | **200** | MIT |
| Heroicons raw | `raw.githubusercontent.com/tailwindlabs/heroicons` | **200** | MIT |
| Phosphor CDN | `cdn.jsdelivr.net/npm/@phosphor-icons/core` | **200** | MIT |
| Bootstrap Icons | `cdn.jsdelivr.net/npm/bootstrap-icons` | **200** | MIT |
| Font Awesome Free | `cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free` | **200** | CC BY 4.0 icons, OFL fonts, MIT code |
| Material Symbols | `fonts.googleapis.com/css2?family=Material+Symbols+Outlined` | **200** | Apache-2.0 |
| Simple Icons | `cdn.jsdelivr.net/npm/simple-icons` | **200** | CC0 |

Safest defaults for title-card glyphs: **Lucide, Tabler, Heroicons, Phosphor,
Bootstrap Icons**. Font Awesome needs attribution.

## Emoji — accessible now

| Source | Endpoint tested | Status | Licence |
|---|---|---|---|
| Twemoji CDN | `cdn.jsdelivr.net/gh/jdecked/twemoji` | **200** | CC BY 4.0 |
| Noto Emoji | `fonts.gstatic.com/s/e/notoemoji` | **200** | Apache / OFL |
| OpenMoji | `cdn.jsdelivr.net/npm/openmoji` | **200** | **CC BY-SA 4.0 — block for paid output** |

Prefer Twemoji or Noto Emoji; OpenMoji’s share-alike can propagate onto the cut.

## Fonts — accessible now

| Source | Endpoint tested | Status | Licence |
|---|---|---|---|
| Google Fonts | `fonts.googleapis.com/css2?family=Inter` | **200** | OFL / Apache / UFL per family |
| Fontsource | `api.fontsource.org/v1/fonts` | **200** | Per family; self-host friendly |
| Fontshare | `api.fontshare.com/v2/css` | **200** | ITF free commercial, **not open source** |

## Illustration, vector and patterns — accessible now

| Source | Endpoint | Status | Licence |
|---|---|---|---|
| unDraw | `undraw.co` | **200** | Free commercial, no attribution; no pack resale |
| Open Peeps | `openpeeps.com` | **200** | CC0 |
| SVG Repo | `svgrepo.com` | **200** | Mixed per file |
| Openclipart | `openclipart.org` | **200** | Mostly CC0; legacy metadata |
| Hero Patterns | `heropatterns.com` | **200** | Free; attribution varies by pack |
| Pattern Monster | `pattern.monster` | **200** | Free; per-pattern terms |
| Humaaans | `humaaans.com` | browser | CC BY 4.0 |
| Storyset | `storyset.com` | browser | Freepik; on-screen credit on free tier |

## 3D, HDRI and texture — accessible now

| Source | Endpoint | Status | Licence |
|---|---|---|---|
| Poly Haven API | `api.polyhaven.com/assets` | **200** | CC0 |
| ambientCG API | `ambientcg.com/api/v2/full_json` | **200** | CC0 |
| Sketchfab search | `api.sketchfab.com/v3/search` | **200** | Per model; downloads need auth and CC0 filter |
| Kenney | `kenney.nl/assets` | **200** | CC0 |
| Quaternius | `quaternius.com` | **200** | CC0 |
| NASA 3D | `nasa3d.arc.nasa.gov` | **200** | US public domain |
| Poly Pizza | `api.poly.pizza` | **401** | Needs `x-auth-token` |

## Effects and overlays

| Source | Status | Use |
|---|---|---|
| Mixkit free effects | **200** | Free, manual import |
| Videezy | **403** | Cloudflare/bot block; manual only, automation prohibited |
| ActionVFX | **429** | Paid; rate-limited |
| RocketStock | **403** | Paid/Shutterstock |
| LottieFiles | **200** | Free/paid animations; per-file licence |
| Freesound | key present | SFX; CC0/BY/NC filtering |
| Poly Haven / ambientCG | **200** | Smoke, dust, light and texture plates (CC0) |
| Blender / ffmpeg / Remotion / HyperFrames | local | Procedural steam, grain, light leaks, ramps, type |

LUT packs (IWLTBAP, Lutify, RocketStock) are per-seat and not redistributable.
Generate a deterministic `.cube` in-repo instead.

## What Blue Tokai actually uses

- **No external icons or stock overlays.** Typography, caption plates, steam,
  speed ramp and end card are `M4` procedural.
- `FX-01` steam, `FX-03` time-lapse, `FX-04` range fan, `FX-05` finished steam,
  `FX-06` CTA fade are authored locally; `FX-02` macro pour comes from capture.
- Only the music bed and fallback use a sourced element (ccMixter).
- Icons/illustrations are not needed for this film.

## Agent wiring

| Source | Wired? |
|---|---|
| ccMixter | Yes — sourcing runner |
| Iconify / Lucide / Tabler / Bootstrap / Font Awesome / Material | Catalogue only; no element fetcher yet |
| Twemoji / Noto / OpenMoji | Catalogue only |
| Poly Haven / ambientCG | Catalogue only |
| Blender / ffmpeg / Remotion | Local procedural path |
