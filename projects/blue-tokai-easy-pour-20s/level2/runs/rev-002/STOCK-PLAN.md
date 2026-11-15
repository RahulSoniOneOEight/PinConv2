# Stock sourcing plan with AI-share guard

Level 2 acquires assets from the shared stock sources; original AI
generation is capped at 40% of assets.

| Assets | Supplied | Stock | AI-generated | AI share | Within 40% cap |
|---|---|---|---|---|---|
| 16 | 6 | 7 | 3 | 18.8% | yes |

## Asset routes

| Asset | What | Kind | Provider | Query | Route | Note |
|---|---|---|---|---|---|---|
| `AS-01` | Blue Tokai Coffee Roasters logo | image | supplied | PNG, alpha, Use the largest available master; do not upscale a thumbnail. | supplied | exact brand file stays supplied |
| `AS-02` | Easy Pour Mixed Bag pack | image | supplied | JPEG, 1800x1800, Crop only to the pack edge; do not crop the front label. | supplied | exact brand file stays supplied |
| `AS-03` | Easy Pour Vienna pack | image | supplied | JPEG, 1800x1800, Front pack only; keep the roast descriptor visible. | supplied | exact brand file stays supplied |
| `AS-04` | Easy Pour Attikan Estate pack | image | supplied | JPEG, 1800x1800, Front pack only; keep the roast descriptor visible. | supplied | exact brand file stays supplied |
| `AS-05` | Easy Pour brewing demonstration, hands | video | pexels | pouring coffee hands | stock | licensed stock, AI-processed as needed |
| `AS-06` | Hot water pour and bloom footage | video | pexels | pouring hot water coffee bloom | stock | licensed stock, AI-processed as needed |
| `AS-07` | Warm kitchen background | image | pexels | warm kitchen coffee background | stock | licensed stock, AI-processed as needed |
| `AS-08` | Finished cup of coffee | image | pexels | cup of coffee on table | stock | licensed stock, AI-processed as needed |
| `AS-09` | Voice over, warm Indian English | voice | generate | warm Indian English narration | generate | AI-generated with disclosure; counted against the 40% cap |
| `AS-10` | Music bed, 20 seconds | music | ccmixter | coffee acoustic instrumental | stock | licensed stock, AI-processed as needed |
| `AS-11` | Water pour sound effect | sound | freesound | water pouring | stock | licensed stock, AI-processed as needed |
| `AS-12` | Brand sting | sound | generate | brand sting | generate | AI-generated with disclosure; counted against the 40% cap |
| `AS-13` | Captured Mixed Bag fallback | image | supplied | use AS-02 pack image | supplied | exact brand file stays supplied |
| `AS-14` | Music fallback track | music | ccmixter | warm ambient instrumental | stock | licensed stock, AI-processed as needed |
| `AS-15` | Synthetic narration fallback | voice | generate | synthetic narration fallback | generate | AI-generated with disclosure; counted against the 40% cap |
| `AS-17` | Easy Pour Seethargundu Estate pack | image | supplied | JPEG, 1800x1800, Front pack only; keep the light-roast descriptor visible. | supplied | exact brand file stays supplied |

## Final selected candidates

| Asset | Provider | Title | Creator | Licence | Fit | Source | File |
|---|---|---|---|---|---|---|---|
| AS-05 | pexels | Pexels video 2853791 | K | Pexels License | 38 | https://www.pexels.com/video/a-man-pouring-ground-coffee-on-a-tin-cup-filter-to-make-hot-brewed-coffee-2853791/ | AS-05.mp4 |
| AS-06 | pexels | Pexels video 14969539 | Colorblind Paisa | Pexels License | 38 | https://www.pexels.com/video/pouring-hot-water-into-a-drip-coffee-maker-14969539/ | AS-06.mp4 |
| AS-07 | pexels | Pexels photo 33256980 | Golboo Maghooli | Pexels License | 33 | https://www.pexels.com/photo/cozy-kitchen-setting-with-coffee-and-moka-pot-33256980/ | AS-07.jpg |
| AS-08 | openverse | Cup of Coffee on Table Rock in Linville Gorge | ballancio | CC-BY | 35 | https://www.flickr.com/photos/24991097@N08/2432383541 | openverse-cup-of-coffee-on-table-rock-in-linville-gorge.jpg |
| AS-11 | wikimedia | File:Pouring water bottles.ogg | stephan | PD | 55 | https://commons.wikimedia.org/wiki/File%3APouring%20water%20bottles.ogg | wikimedia-file-pouring-water-bottles-ogg.ogg |

Backup candidates (7): reported in `ANNEX-SOURCED-NOT-USED.md`.


## Rules

- exact product/pack/logo stays supplied; never stock or generated.
- Pexels and Unsplash are both fetched and scored for every image asset;
  the higher fit is selected and the other is reported as a backup.
- AI generation is only for voice, sting and disclosed fallbacks, and
  stays within 40% of assets.
- Stock assets may be AI-processed (grade, upscale, relight, retime);
  processing is not generation and does not count against the 40%.
