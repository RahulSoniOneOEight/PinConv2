# Source access — live probe

**Date:** 2026-11-15
**Method:** direct HTTPS requests from this machine with **no API keys or tokens**,
25-second timeout, browser user agent, 1-result query per endpoint.
**Meaning:** “accessible now” means the endpoint answered successfully without
credentials. It does not mean the licence is cleared; every candidate still goes
through the licence gate and origin verification where required.

## Image — accessible now

| Source | Endpoint | Result | Licence caveat |
|---|---|---|---|
| Openverse images | `api.openverse.org/v1/images/` | **200** | Aggregator; licence is unverified until the origin page is read |
| Wikimedia Commons | `commons.wikimedia.org/w/api.php` | **200** | Aggregator; `Restrictions` field needs human review |
| NASA Image Library | `images-api.nasa.gov/search` | **200** | Mostly US public domain; partner/ESA exceptions |

## Video — accessible now

| Source | Endpoint | Result | Licence caveat |
|---|---|---|---|
| Internet Archive | `archive.org/advancedsearch.php` | **200** | Item-specific rights; discovery only |
| NASA video | `images-api.nasa.gov/search` | **200** | Mostly US public domain; partner exceptions |
| Wikimedia Commons video | `commons.wikimedia.org/w/api.php` | **200** | Per-file CC/PD; verify the file page |

## Sound — accessible now

| Source | Endpoint | Result | Licence caveat |
|---|---|---|---|
| ccMixter | `ccmixter.org/api/query` | **200** | Direct source; CC BY/NC per track; `lic=by` filter works |
| Openverse audio | `api.openverse.org/v1/audio/` | **200** | Aggregator; resolve at the origin |
| Internet Archive audio | `archive.org/advancedsearch.php` | **200** | Item-specific rights |
| Wikimedia Commons audio | `commons.wikimedia.org/w/api.php` | **200** | Per-file CC/PD |
| LibriVox | `librivox.org/api/feed/audiobooks` | **200** | Public-domain recordings; only when the script matches the PD text |

## Local credential vault — verified working

The vault at `D:\pinaka-credentials\secrets` contains the actual keys. They were
tested directly and returned `200`:

| Provider | Key file | API result |
|---|---|---|
| Pexels | `pexels-api-key` | `200`, 8,000 results for “coffee” |
| Unsplash | `unsplash-access-key` | `200`, results returned |
| Freesound | `freesound-api-key` | `200`, 15 preview results |

The same values were set as **user-scope** environment variables:

```
PEXELS_API_KEY
UNSPLASH_ACCESS_KEY
FREESOUND_API_KEY
```

A new terminal/OpenCode session inherits them. The current session reads them
through `level2.credentials`, which resolves env → vault → Windows user registry:

```
python -m pinconv2 --data-dir projects level2 credentials ...
→ {"PEXELS_API_KEY":"vault","UNSPLASH_ACCESS_KEY":"vault","FREESOUND_API_KEY":"vault","FAL_KEY":"vault"}
```

No key value is written to git, logs or the run artifacts.

## Key-gated sources — no-key probe results

Pexels, Unsplash and Freesound are now keyed via the vault and verified above.
The remaining rows still have no credential in this environment.

| Source | Type | Result | What is missing |
|---|---|---|---|
| Pexels | image/video | 401 | API key |
| Unsplash | image | 401 | Client-ID |
| Pixabay | image/video | 400 | API key |
| Smithsonian | image | 403 | `api.data.gov` key |
| Europeana | image | 401 | `wskey` |
| NYPL | image | 401 | API token |
| Coverr | video | 401 | API key |
| Freesound | sound | 401 | OAuth token |
| Jamendo | sound | HTTP 200 but `status: failed` | `client_id`; commercial clearance is paid |
| Rijksmuseum | image | 410 | API endpoint no longer available |
| The Met search | image | 410 | Search retired 2026-10-01; object records only |
| Library of Congress | image | 403 | Bot challenge blocked the scripted request |

## Not scriptable — manual only

Free Music Archive (API retired), Mixkit, Videezy, Videvo, Mazwai, Zapsplat,
Sonniss, Bensound, Uppbeat, Storyset, unDraw, Fontshare, Sketchfab (beyond CC0
filter), Openclipboard-style legacy sources.

## Blocked for commercial output

BBC Sound Effects (RemArc: personal/education/research), GADM (non-commercial),
any NC/ND/share-alike licence, OSM ODbL for derived data, OpenMoji share-alike.

## What the agent currently uses

| Source | Wired? | Evidence |
|---|---|---|
| **ccMixter** | **Yes** — search, filter, preview, probe, gate | `src/pinconv2/level2/sourcing.py`; 9 CC BY candidates in `asset-sourcing.json` |
| Openverse | Catalogue and licence gate only; no search adapter | `catalogue.py`, `licence_gate.py` |
| Wikimedia / Internet Archive / NASA / LibriVox | Catalogue only | `catalogue.py` |
| Pexels / Unsplash / Pixabay / Freesound / Jamendo / Coverr | Catalogue only; no key | `catalogue.py` |
| fal.ai / Runware | Generation adapters, not stock; keys absent | `engines/fal_runware.py` |

## Blue Tokai relevance

- **Sound:** ccMixter was used for `AS-10` and `AS-14`; nine CC BY 3.0 previews,
  two chosen.
- **Image:** none sourced. Packs, logo and plate are supplied/owned.
- **Video:** none sourced. Demonstration and cup are capture (`M6`).
- Exact and proof material is never sourced from stock.
