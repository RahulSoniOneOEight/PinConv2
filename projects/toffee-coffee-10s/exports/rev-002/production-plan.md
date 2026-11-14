# Production Plan - Toffee Coffee Roasters - Ethiopia, in an instant

**Project:** toffee-coffee-10s  
**Plan revision:** 2  
**Plan hash:** `c2f43e7aa4dd6ded9419e74d0fd4bc4bc00a49df755453b0df0f1cb411ca069b`  
**Brief revision:** 1  
**Validation:** PASS  
**Gate 1:** approved by RahulSoniOneOEight (repo owner)

## 1. Deliverable

| Field | Value |
|---|---|
| Format | 1080x1920, 9:16 |
| Frame rate | 25 fps |
| Frames | 250 |
| Duration | 10.00s |
| Placement | Instagram Reels / YouTube Shorts / organic short video, 9:16 |
| Captions | yes |
| Safe area | top 220, bottom 320, left 60, right 140 |
| Caption rules | 2 lines, 32 chars/line, 17.0 cps, 24 frame minimum |

## 2. Must-have coverage

| ID | Must-have | Status | Evidence |
|---|---|---|---|
| MH-01 | 10.0-second vertical 9:16 ad at 1080x1920 and 25 fps | satisfied | DP-01, AC-01 |
| MH-02 | Strong opening hook in the first two seconds | satisfied | SH-01, CP-01, AC-02 |
| MH-03 | Reveal the Ethiopia Speciality Instant Coffee pack | satisfied | SH-02, AS-01, AC-03 |
| MH-04 | Show coffee energy: liquid, macro texture and steam | satisfied | SH-03, AS-03 |
| MH-05 | Land the Toffee brand and a clear call to action | satisfied | SH-04, CP-05, AC-05 |
| MH-06 | Captions that work with sound off | satisfied | CP-11, CP-12, CP-13, CP-14, AC-09 |
| MH-07 | Only approved product facts, price and promotion | satisfied | ED-01, ED-02, ED-03, AC-04 |
| MH-08 | No reuse of reference video footage | satisfied | AC-10 |
| MH-09 | Premium, warm tone | satisfied | SH-01, SH-03, DC-02 |

## 3. Beat sheet

| Beat | Frames | Purpose | Spoken | On screen | Emotion |
|---|---|---|---|---|---|
| BT-01 | [0,50) | Stop the scroll with origin and texture. | Ethiopia. | ETHIOPIA | intrigue |
| BT-02 | [50,125) | Reveal the pack and name the format. | Speciality instant coffee. | SPECIALITY INSTANT COFFEE | recognition |
| BT-03 | [125,200) | Deliver the sensory payoff. | In an instant. | IN AN INSTANT. | appetite |
| BT-04 | [200,250) | Close on brand and CTA. | Toffee Coffee Roasters. | TOFFEE COFFEE ROASTERS | confidence |

## 4. Shot plan

| Shot | Frames | Time | Picture | Method | Fallback | Status |
|---|---|---|---|---|---|---|
| SH-01 | [0,50) | 0.00-2.00s | Full-frame macro; type centered in the upper third. The origin word lands on beat one and holds. | Authored motion-graphics composite: macro plate, steam element, kinetic type. | Static macro still with a slow scale and a type fade. | ready |
| SH-02 | [50,125) | 2.00-5.00s | Pack hero at center, label square to camera. Pack settles; descriptor appears below. | Pack hero composite with supplied art, light sweep and type. | Pack still on seamless background with a simple gradient. | ready |
| SH-03 | [125,200) | 5.00-8.00s | Pack fills the frame; liquid wraps the lower half. Splash peaks, then settles around the pack. | Liquid and macro composite around the pack with type. | Pack hero still with an animated light sweep; no liquid simulation. | ready |
| SH-04 | [200,250) | 8.00-10.00s | Logo top-center, pack center, CTA and caption below. End card holds for the final read. | End-card composite: logo, pack, CTA and caption. | Typographic end card with logo and CTA if pack art is unavailable. | ready |

## 5. Shot x Layer x Asset

### SH-01 - Earn the next two seconds with origin and texture.

**Framing:** Full-frame macro; type centered in the upper third.  
**Movement:** Slow push-in on the coffee surface; steam drifts right.  
**Lighting:** Low-key warm key from the right; copper rim.  
**Palette:** Near-black brown, cream type, copper highlight.  
**Continuity:** Coffee texture carries into the pack reveal.  
**Transition in:** Cold open.

| Layer | Role | Frames | Rect | Binding | Exact | Req | Protected |
|---|---|---|---|---|---|---|---|
| LY-010 | background | 0-50 | 0,0,1080,1920 | asset:AS-05 | illustrative | yes | - |
| LY-011 | subject | 0-50 | 0,240,1080,1300 | asset:AS-03 | illustrative | yes | - |
| LY-012 | effect | 0-50 | 200,300,680,900 | none:- | illustrative | yes | - |
| LY-013 | typography | 0-50 | 80,700,860,200 | copy:CP-01 | approved_copy | yes | yes |
| LY-014 | caption_plate | 0-50 | 60,1430,880,150 | none:- | illustrative | yes | - |
| LY-015 | caption | 0-50 | 80,1450,800,100 | copy:CP-11 | approved_copy | yes | - |

### SH-02 - Reveal the pack and name the format.

**Framing:** Pack hero at center, label square to camera.  
**Movement:** Pack rises 40 px; a single light sweep crosses left to right.  
**Lighting:** Warm key on the pack; dark surround.  
**Palette:** Copper, cream, deep brown.  
**Continuity:** Same warm grade and pack orientation as SH-03 and SH-04.  
**Transition in:** Light wipe from SH-01.

| Layer | Role | Frames | Rect | Binding | Exact | Req | Protected |
|---|---|---|---|---|---|---|---|
| LY-020 | background | 0-75 | 0,0,1080,1920 | asset:AS-05 | illustrative | yes | - |
| LY-021 | product | 0-75 | 190,480,700,900 | asset:AS-01 | exact | yes | - |
| LY-022 | effect | 0-75 | 160,460,760,940 | none:- | illustrative | yes | - |
| LY-023 | typography | 0-75 | 80,1330,860,130 | copy:CP-02 | approved_copy | yes | yes |
| LY-024 | caption_plate | 0-75 | 60,1475,880,120 | none:- | illustrative | yes | - |
| LY-025 | caption | 0-75 | 80,1500,800,80 | copy:CP-12 | approved_copy | yes | - |

### SH-03 - Deliver the sensory payoff and hold the label.

**Framing:** Pack fills the frame; liquid wraps the lower half.  
**Movement:** Slow push-in; liquid peaks at frame 150 and falls.  
**Lighting:** Backlit liquid with a warm edge.  
**Palette:** Caramel, copper, near-black.  
**Continuity:** Pack label remains unobstructed; same pack scale direction.  
**Transition in:** Match cut on the pack.

| Layer | Role | Frames | Rect | Binding | Exact | Req | Protected |
|---|---|---|---|---|---|---|---|
| LY-030 | background | 0-75 | 0,0,1080,1920 | asset:AS-05 | illustrative | yes | - |
| LY-031 | subject | 0-75 | 0,700,1080,1100 | asset:AS-03 | illustrative | yes | - |
| LY-033 | product | 0-75 | 100,300,880,1000 | asset:AS-01 | exact | yes | - |
| LY-034 | typography | 0-75 | 80,1240,860,160 | copy:CP-03 | approved_copy | yes | yes |
| LY-036 | caption_plate | 0-75 | 60,1475,880,120 | none:- | illustrative | yes | - |
| LY-037 | caption | 0-75 | 80,1500,800,90 | copy:CP-13 | approved_copy | yes | - |

### SH-04 - Close on brand and a clear CTA.

**Framing:** Logo top-center, pack center, CTA and caption below.  
**Movement:** Pack settles; CTA fades up on the final beat.  
**Lighting:** Even warm key; logo separated from background.  
**Palette:** Cream logo, copper pack, near-black ground.  
**Continuity:** Final pack orientation matches SH-02 and SH-03.  
**Transition in:** Splash wipe from SH-03.

| Layer | Role | Frames | Rect | Binding | Exact | Req | Protected |
|---|---|---|---|---|---|---|---|
| LY-040 | background | 0-50 | 0,0,1080,1920 | asset:AS-05 | illustrative | yes | - |
| LY-041 | product | 0-50 | 240,560,600,760 | asset:AS-01 | exact | yes | - |
| LY-042 | logo | 0-50 | 340,300,400,180 | asset:AS-02 | exact | yes | yes |
| LY-043 | cta | 0-50 | 140,1360,800,100 | copy:CP-05 | approved_copy | yes | yes |
| LY-044 | caption_plate | 0-50 | 60,1340,880,260 | none:- | illustrative | yes | - |
| LY-045 | caption | 0-50 | 80,1505,800,80 | copy:CP-14 | approved_copy | yes | - |

## 6. Asset requirements

| Asset | Name | Route | Rights | Exact | Specification | Estimate | Fallback | Used by |
|---|---|---|---|---|---|---|---|---|
| AS-01 | Ethiopia pack artwork | supplied | needs_approval | exact | PNG; 2000x2000 | 5.00 | AS-06 | LY-021, LY-033, LY-041 |
| AS-02 | Toffee Coffee Roasters logo | supplied | needs_approval | exact | SVG; no fixed raster | 5.00 | - | LY-042 |
| AS-03 | Liquid and macro coffee pack | to_create | cleared | illustrative | PNG sequence; 1080x1920 | 6.00 | - | LY-011, LY-031 |
| AS-05 | Warm dark background | owned | cleared | illustrative | PNG; 1080x1920 | - | - | LY-010, LY-020, LY-030, LY-040 |
| AS-07 | Music bed, 10 seconds | to_source | needs_approval | illustrative | WAV; no fixed raster | 10.00 | AS-13 | AU-02 |
| AS-08 | Voice over, warm Indian English | to_create | needs_approval | illustrative | WAV; no fixed raster | 14.00 | AS-14 | AU-01 |
| AS-09 | Reveal whoosh | to_create | cleared | illustrative | WAV; no fixed raster | - | - | AU-03 |
| AS-10 | Liquid splash | to_create | cleared | illustrative | WAV; no fixed raster | - | - | AU-04 |
| AS-11 | Brand sting | to_create | cleared | illustrative | WAV; no fixed raster | - | - | AU-05 |
| AS-06 | Captured pack fallback | to_capture | needs_approval | exact | PNG; 2400x2400 | 2.00 | - | - |
| AS-13 | Music fallback track | to_source | needs_approval | illustrative | WAV; no fixed raster | - | - | - |
| AS-14 | Synthetic narration fallback | to_generate | needs_approval | illustrative | WAV; no fixed raster | - | - | - |

## 7. Copy blocks

| Copy | Role | Status | Text | Exact data | Claims |
|---|---|---|---|---|---|
| CP-01 | hook | proposed | ETHIOPIA | ED-07 | - |
| CP-02 | headline | proposed | SPECIALITY INSTANT COFFEE | - | CL-03 |
| CP-03 | headline | proposed | IN AN INSTANT. | - | - |
| CP-05 | cta | proposed | Shop the Ethiopia range | ED-05 | - |
| CP-11 | caption | proposed | Ethiopia. | ED-07 | - |
| CP-12 | caption | proposed | Speciality instant coffee. | - | CL-03 |
| CP-13 | caption | proposed | In an instant. | - | - |
| CP-14 | caption | proposed | Toffee Coffee Roasters | ED-06 | - |

## 8. Exact data register

| ID | Field | Value | Status | Source | Notes |
|---|---|---|---|---|---|
| ED-01 | product_name | Ethiopia Speciality Instant Coffee | observed | SRC-02 | Brand product name; Gate 1 must approve the identifier. |
| ED-02 | price | 50 gm: Rs 499; 100 gm: Rs 699 | observed | SRC-02 | Variant-dependent. Not approved for advertising. |
| ED-03 | offer | Buy 1 Get 1 Free or Buy 2 Get 2 Free (+ free mug) | observed | SRC-01 | Expiry and terms are not visible. Not approved for advertising. |
| ED-04 | promo_code | BOGO / B2G2 | observed | SRC-01 | Code exists on the storefront; advertising use is unconfirmed. |
| ED-05 | cta | Shop the Ethiopia range | proposed | - | Proposed creative CTA. Gate 1 must approve the exact wording. |
| ED-06 | brand_name | Toffee Coffee Roasters | observed | SRC-01 | Brand identifier observed on the storefront. |
| ED-07 | origin | Ethiopia | observed | SRC-02 | Origin name from the product page. |
| ED-08 | pack_size | 50 gm / 100 gm | observed | SRC-02 | Hero size has not been chosen. |

## 9. Claims register

| ID | Claim | Status | Approved wording | Limitation |
|---|---|---|---|---|
| CL-01 | Ethiopia is the birthplace of coffee | unverified | - | The brand page says 'known as a Birthplace of Coffee'; this is not independent substantiation. |
| CL-02 | Makes 50 cups per 100 g | verified | - | Brand-authored serving estimate; advertising wording not approved. |
| CL-03 | Speciality instant coffee | verified | speciality instant coffee | Use as a category descriptor, not a superiority claim. |
| CL-04 | Rich aroma with bold and fruity flavours | verified | - | Sensory description; advertising wording not approved. |
| CL-05 | Have it black or with milk or cream | verified | - | Serving suggestion; not used in this cut. |

## 10. Audio

| Cue | Frames | Kind | Description | Asset | Level | Essential |
|---|---|---|---|---|---|---|
| AU-01 | [0,230) | vo | Ethiopia. Speciality instant coffee. In an instant. | AS-08 | -3.0 dB | yes |
| AU-02 | [0,250) | music | Warm restrained electronic bed with a lift at the reveal. | AS-07 | -18.0 dB | yes |
| AU-03 | [42,52) | sfx | Short whoosh into the pack reveal. | AS-09 | -12.0 dB | yes |
| AU-04 | [118,150) | sfx | Liquid splash on the payoff beat. | AS-10 | -8.0 dB | yes |
| AU-05 | [195,225) | sfx | Low brand sting under the end card. | AS-11 | -10.0 dB | yes |

## 11. Transitions

| ID | From | To | Frame | Kind | Frames |
|---|---|---|---|---|---|
| TR-01 | SH-01 | SH-02 | 50 | light wipe | 6 |
| TR-02 | SH-02 | SH-03 | 125 | match cut on pack | 4 |
| TR-03 | SH-03 | SH-04 | 200 | splash wipe | 8 |

## 12. Alternate routes

| ID | Targets | Trigger | Preserved | Cost delta | Scope |
|---|---|---|---|---|---|
| ALT-03 | SH-03 | Liquid simulation overruns or reads poorly at phone size. | Sensory payoff and pack clarity. | 0.00 | SH-03 |
| ALT-04 | CP-05 | Brand rejects the proposed CTA wording. | Brand close with a direct CTA. | 0.00 | SH-04 |
| ALT-01 | AS-01 | Brand pack file is missing or below 2000 px. | Label exactness and pack silhouette. | 2.00 | SH-02, SH-03, SH-04 |
| ALT-02 | AS-01 | No pack art or physical sample is available. | Four-shot structure and brand close. | 0.00 | SH-02, SH-03, SH-04 |

## 13. Budget

| ID | Item | Kind | Amount USD | Basis | Confidence |
|---|---|---|---|---|---|
| ES-01 | Music library licence | shared | 10.00 | operator_estimate | medium |
| ES-02 | Voice artist session and edit | shared | 14.00 | operator_estimate | medium |
| ES-03 | Motion design and compositing | shared | 8.00 | operator_estimate | medium |
| ES-04 | Colour grade and finishing | shared | 3.00 | operator_estimate | high |
| ES-05 | Pack and logo preparation | shot | 5.00 | operator_estimate | medium |
| ES-06 | Liquid and macro pack | shot | 6.00 | operator_estimate | medium |
| ES-10 | End-card build | shot | 2.00 | operator_estimate | high |
| ES-08 | Pack capture fallback | fallback | 2.00 | operator_estimate | medium |

| Budget line | USD |
|---|---|
| Shared | 35.00 |
| Shot | 13.00 |
| Variant | 0.00 |
| Subtotal | 48.00 |
| Retry reserve (15%) | 7.20 |
| Total | 55.20 |
| Fallback | 2.00 |
| Worst case | 57.20 |
| Cap | 60.00 |

## 14. Acceptance checks

| ID | Check | Method | Level | Status | Targets |
|---|---|---|---|---|---|
| AC-01 | Timeline covers exactly 250 frames across four contiguous shots. | structural | level_1 | pass | DP-01, SH-01, SH-02, SH-03, SH-04 |
| AC-02 | All text sits inside the 1080x1920 safe area. | structural | level_1 | pass | SH-01, SH-02, SH-03, SH-04 |
| AC-03 | Pack label and logo regions are not occluded by planned layers. | structural | level_1 | pass | LY-021, LY-033, LY-041, LY-042 |
| AC-04 | No required layer depends on unapproved price or offer data. | structural | level_1 | pass | ED-02, ED-03, ED-04 |
| AC-05 | Brand and CTA are legible at 50 percent scale on a 1080x1920 phone. | render_pixel | level_2 | pending | LY-042, LY-043 |
| AC-06 | VO is intelligible and the music sits at least 6 dB under it. | audio | level_2 | pending | AU-01, AU-02 |
| AC-07 | Exact data in final pixels matches the approved values. | render_pixel | level_2 | pending | ED-01, ED-05 |
| AC-08 | Every used claim is verified and every exact reference resolves. | structural | level_1 | pass | CL-03, ED-05 |
| AC-09 | A sound-off viewer understands the product and the brand. | human | level_2 | pending | SH-02, SH-04 |
| AC-10 | All picture assets are owned, supplied or commissioned; no reference footage is bound. | structural | level_1 | pass | AS-01, AS-02, AS-03, AS-05 |
| AC-11 | Final file is 1080x1920, 25 fps, 10.0 s, H.264/AAC. | render_pixel | level_2 | pending | DP-01 |
| AC-12 | Contact sheet shows the pack clear of captions and platform UI. | static_preview | level_2 | pending | SH-02, SH-03, SH-04 |
| AC-13 | Budget total plus fallback stays inside the approved cap. | structural | level_1 | pass | DP-01 |
| AC-14 | Every shot has a primary and a genuinely different fallback method. | structural | level_1 | pass | SH-01, SH-02, SH-03, SH-04 |

## 15. Holds

| ID | Hold | Reason | Affects | Evidence needed | Owner |
|---|---|---|---|---|---|
| HI-01 | Price and promotion confirmation | The storefront price varies by pack size and the offer has no visible expiry or terms. | ED-02, ED-03, ED-04 | Brand-approved hero size, advertising price, offer terms and expiry, with a named approver. | human |
| HI-02 | Brand pack art, logo and font clearance | No brand kit or advertising-use licence was supplied. | AS-01, AS-02 | Pack art and vector logo with written advertising-use confirmation, plus the brand font or approval to use the placeholder. | human |
| HI-03 | Music licence | No track is selected or licensed. | AS-07 | A production-library licence covering organic and paid social. | human |

## 16. Decisions

| ID | Decision | Evidence | Rationale |
|---|---|---|---|
| DC-01 | No price or promotion in the ready cut. | F-01, F-02 | The price varies by pack size and the offer terms are not visible. Putting either in the ready cut would turn an observation into an advertising claim. |
| DC-02 | Premium product-led hero, with a character route as an alternative. | F-05, F-06 | A product hero communicates the SKU and brand fastest in ten seconds. The character route is credible but spends too much time before the product appears. |
| DC-03 | Four shots over 250 frames: 2s hook, 3s reveal, 3s payoff, 2s close. | F-07, F-10 | Four beats give the pack enough hold for label recognition while keeping the cut under ten seconds. |
| DC-04 | Inter under the SIL OFL as a documented placeholder. | F-08 | The plan needs a concrete typographic specification. Inter is legally clear and easy to replace when the brand kit arrives. |
| DC-05 | Use only the approved descriptor 'speciality instant coffee'. | F-03 | The other claims need substantiation and approved advertising wording. The category descriptor is verified and sufficient for this cut. |

## 17. Validation summary

**Passed:** yes  
**Failures:** 0  
**Warnings:** 8

| ID | Rule | Target | Status | Detail |
|---|---|---|---|---|
| V-009 | exact.identifiers | LY-013 | warn | origin ED-07 is observed; Gate 1 must approve this identifier or wording |
| V-010 | exact.identifiers | LY-015 | warn | origin ED-07 is observed; Gate 1 must approve this identifier or wording |
| V-011 | exact.identifiers | LY-043 | warn | cta ED-05 is proposed; Gate 1 must approve this identifier or wording |
| V-012 | exact.identifiers | LY-045 | warn | brand_name ED-06 is observed; Gate 1 must approve this identifier or wording |
| V-038 | rights.assets | AS-01 | warn | rights need approval for Ethiopia pack artwork |
| V-039 | rights.assets | AS-02 | warn | rights need approval for Toffee Coffee Roasters logo |
| V-040 | rights.assets | AS-07 | warn | rights need approval for Music bed, 10 seconds |
| V-041 | rights.assets | AS-08 | warn | rights need approval for Voice over, warm Indian English |

## 18. Critique and top three

No material findings. The ready plan has no unapproved commercial layer, no safe-area violation, no over-cap estimate and no unknown rights on a required asset. Remaining warnings are Gate 1 conditions.

| ID | Category | Severity | Priority | Owner | Disposition | Action |
|---|---|---|---|---|---|---|
| - | - | - | - | - | - | No findings. |

## 19. Gate 1 conditions

- HI-01 Price and promotion confirmation: Brand-approved hero size, advertising price, offer terms and expiry, with a named approver.
- HI-02 Brand pack art, logo and font clearance: Pack art and vector logo with written advertising-use confirmation, plus the brand font or approval to use the placeholder.
- HI-03 Music licence: A production-library licence covering organic and paid social.
- exact.identifiers: brand_name ED-06 is observed; Gate 1 must approve this identifier or wording
- exact.identifiers: cta ED-05 is proposed; Gate 1 must approve this identifier or wording
- exact.identifiers: origin ED-07 is observed; Gate 1 must approve this identifier or wording
- rights.assets: rights need approval for Ethiopia pack artwork
- rights.assets: rights need approval for Music bed, 10 seconds
- rights.assets: rights need approval for Toffee Coffee Roasters logo
- rights.assets: rights need approval for Voice over, warm Indian English

## 20. Research basis

| ID | Source | Accessed | Reliability |
|---|---|---|---|
| SRC-01 | Toffee Coffee Roasters storefront | 2026-11-14 | primary |
| SRC-02 | Ethiopia Speciality Instant Coffee product page | 2026-11-14 | primary |
| SRC-03 | Coffee motion graphics advertisement (AK Edits) | 2026-11-14 | reference |
| SRC-04 | Peak Indian mom behaviour (Hows Hardy) | 2026-11-14 | reference |
| SRC-05 | Operator assumption: Reels and Shorts safe areas | 2026-11-14 | assumption |
| SRC-06 | SIL Open Font License 1.1 | 2026-11-14 | primary |
