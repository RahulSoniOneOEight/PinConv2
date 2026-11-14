# Open-source elements and local tools — status

**Date:** 2026-11-15
**Scope:** which icon/element/effect sources are open-licence and reachable, plus
whether OpenMontage and ShortGPT are usable by Level 2 agents.

## 1. Open-licence sources that are accessible now

All statuses are live HTTPS probes with no key.

### Icons

| Source | Status | Licence | Notes |
|---|---|---|---|
| Lucide | **200** | ISC | CDN and GitHub raw |
| Tabler | **200** | MIT | CDN |
| Heroicons | **200** | MIT | GitHub raw |
| Phosphor | **200** | MIT | CDN |
| Bootstrap Icons | **200** | MIT | CDN |
| Simple Icons | **200** | CC0 | Brand glyphs only |
| Material Symbols | **200** | Apache-2.0 | Icon font; licence travels with subset |
| Font Awesome Free | **200** | CC BY 4.0 icons / OFL fonts / MIT code | Attribution required on icons |

Iconify is accessible (`200`) but is an aggregator; the licence belongs to the
underlying set, so it must be resolved per set.

### Emoji

| Source | Status | Licence | Use |
|---|---|---|---|
| Twemoji | **200** | CC BY 4.0 | Preferred |
| Noto Emoji | **200** | Apache / OFL | Preferred |
| OpenMoji | **200** | CC BY-SA 4.0 | **Block for paid output** (share-alike) |

### Fonts

| Source | Status | Licence |
|---|---|---|
| Google Fonts | **200** | OFL / Apache / UFL per family |
| Fontsource | **200** | Same family licence; self-host friendly |
| Fontshare | **200** | ITF free commercial — **not open source** |

### Illustration / vector / pattern

| Source | Status | Licence | Open? |
|---|---|---|---|
| Open Peeps | **200** | CC0 | Yes |
| Openclipart | **200** | Mostly CC0 | Yes, verify per file |
| unDraw | **200** | Custom free commercial | Free, not open |
| SVG Repo | **200** | Mixed per file | Verify |
| Hero Patterns | **200** | Custom free | Free, not open |
| Pattern Monster | **200** | Custom free | Free, not open |
| Humaaans | browser | CC BY 4.0 | Yes, attribution |
| Storyset | browser | Freepik / CC BY | Free tier needs credit |

### 3D / HDRI / texture

| Source | Status | Licence | Open? |
|---|---|---|---|
| Poly Haven | **200** | CC0 | Yes |
| ambientCG | **200** | CC0 | Yes |
| Kenney | **200** | CC0 | Yes |
| Quaternius | **200** | CC0 | Yes |
| NASA 3D | **200** | US public domain | Yes |
| Sketchfab | **200** | Per model; CC0 filter mandatory | Mixed |
| Poly Pizza | **401** | Needs `x-auth-token` | Not accessible now |

### Effects / overlays

| Source | Status | Licence | Verdict |
|---|---|---|---|
| Poly Haven textures | **200** | CC0 | Smoke, dust, light plates |
| ambientCG | **200** | CC0 | Texture/grain plates |
| Freesound | key present | CC0 / BY / NC | SFX, filter NC/ND |
| Mixkit | **200** | Custom free | Manual import |
| LottieFiles | **200** | Free/paid per animation | Verify per file |
| Videezy | **403** | Custom | Manual only; automation prohibited |
| ActionVFX | **429** | Paid | Not usable |
| RocketStock | **403** | Paid | Not usable |
| IWLTBAP / Lutify / RocketStock LUTs | paid | Per-seat | Generate `.cube` locally |

Open-source **tools** for effects: Blender, ffmpeg, Remotion, HyperFrames,
OpenCV, Pillow. These are installed or locally available; Blue Tokai’s steam,
ramp, grain, light and end card are authored this way.

## 2. OpenMontage

**Available: yes.** OpenMontage Studio is running locally, version `0.1.8`,
account signed in.

### Connected providers

| Provider | Verified operations |
|---|---|
| Google | music, speech, transcribe, image, video, video understanding |
| OpenRouter | music, speech, transcribe, image, video |
| Runware | speech, image, video, upscale, cleanup, mesh, avatar |
| fal | audio separation, depth, upscale, image, mesh, avatar, segment, video |
| Recraft | vector image |

### Stock routes with no key

| Route | Readiness |
|---|---|
| Free To Use | ready |
| NASA | ready |
| Openverse | ready |
| Wikimedia Commons | ready |

Pixabay, OpenAI, ElevenLabs, HeyGen, MiniMax, Runway, Meshy, Tripo, xAI,
Higgsfield, QuiverAI, Azure Speech, Cartesia and World Labs are **not connected**.

### Local gaps

- ComfyUI: not configured.
- Blender bridge: not configured.
- Kokoro TTS: unsupported (eSpeak-NG path missing).
- Local whisper.cpp: not enabled; model download needs owner approval.
- ACE-Step: not configured.

### How Level 2 may use it

- Stock search/acquire through the four no-key routes.
- fal/Runware/Google generation when Gate 2A permits.
- Remotion render and media processing.
- Studio’s ledger remains authoritative for Studio calls; Level 2 must not bypass
  it or the $2 provider cap. Paid work still requires an approved Gate 2A.

## 3. ShortGPT

**Available: yes.** Installed at `D:\shortgpt`, Python 3.10.11, status healthy.

| Dependency | Present |
|---|---|
| moviepy | yes |
| edge_tts | yes |
| openai | yes (package) |
| torch | yes |
| whisper_timestamped | yes |

| Key | Present |
|---|---|
| `OPENAI_API_KEY` | **no** |
| `PEXELS_API_KEY` | **yes** |
| `ELEVEN_LABS_API_KEY` | **no** |

Jobs in queue: 0. Output directory exists.

### What it can do for Level 2

- **Edge TTS narration** without a key — useful for `AS-15` synthetic fallback,
  with disclosure.
- **Transcription / caption timing** through `whisper_timestamped`.
- **Pexels background search** using the existing Pexels key.
- **Short-form render** with moviepy, but its facts-short template is not a brand
  ad compositor.

### Limits

- No OpenAI key, so its script-generation prompt path is unavailable.
- Not a substitute for the Level 2 build sheet, compositor or source ledger.
- Any voice output is synthetic and must be disclosed and approved.

## 5. Integration state (updated)

- `SourcingAgent` now owns `source_assets` and the stock check.
- `ShortGptEngine` and `VoiceAgent` implement Edge TTS and a guarded transcription
  path. A real sample was generated: `generated/AS-15-edge-sample.mp3`, 14.95 s,
  89,712 bytes, voice `en-IN-NeerjaNeural`, disclosed as synthetic.
- `OpenMontageEngine` gained `render()` and `from_mcp()`; the MCP bridge is still
  injected by the runtime, so a standalone CLI fails closed.
- `level2 stockcheck` fetched and probed 11 of 12 sources; see
  `stock-check/stock-check.md`.
- `SOURCE-SHEET.md` now lists every shot/layer with its actual source and
  preview, plus the chosen music candidates.
- Level 2 still owns the decision records, build sheet, provider governor and
  Gate 2A. No paid call was made for any of these checks.


## 6. Recommendation

- Use **OpenMontage** as the Level 2 stock/generation/render adapter where its
  ledger and the $2 cap agree.
- Use **ShortGPT** for **Edge TTS fallback and transcription only**; do not use
  its renderer for the Blue Tokai master.
- Keep Level 2’s own decision records, build sheet, provider governor and Gate 2A
  as the source of truth.
- No paid call is authorised by this status check.
