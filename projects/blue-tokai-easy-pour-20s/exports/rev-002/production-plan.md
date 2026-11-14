# Production Plan - Blue Tokai Easy Pour - specialty coffee, just a mug and hot water

**Project:** blue-tokai-easy-pour-20s  
**Plan revision:** 2  
**Plan hash:** `1370f029b0b35730625c459cf85579bfd767d2e4a7b62016055e100d15f2aba5`  
**Brief revision:** 1  
**Validation:** PASS  
**Gate 1:** approved by RahulSoniOneOEight (repo owner)

## 1. Deliverable

| Field | Value |
|---|---|
| Format | 1920x1080, 16:9 |
| Frame rate | 25 fps |
| Frames | 500 |
| Duration | 20.00s |
| Placement | YouTube / 16:9 in-stream and Demand Gen master |
| Captions | yes |
| Safe area | top 70, bottom 90, left 80, right 80 |
| Caption rules | 2 lines, 42 chars/line, 16.0 cps, 36 frame minimum |
| Placement safe areas | youtube_in_stream: top 70, bottom 90, left 80, right 80; youtube_demand_gen: top 70, bottom 90, left 80, right 80 |
| Delivery codec | H.264 High Profile, AAC 320 kbps, MP4 |
| Colour | Rec.709 / sRGB web delivery |
| Caption mode | Burned-in campaign copy plus a separate SRT for accessibility captions; do not rely on platform auto-captions for the message. |
| Audio target | -16 LUFS integrated, -1 dBTP true peak |

## 2. Must-have coverage

| ID | Must-have | Status | Evidence |
|---|---|---|---|
| MH-01 | 20.0-second 16:9 YouTube ad at 1920x1080 and 25 fps | satisfied | DP-01, AC-01 |
| MH-02 | Open on specialty coffee and the product within the first three seconds | satisfied | SH-01, CP-01, AC-02 |
| MH-03 | Show the built-in filter clipped to a mug and water hitting the grounds | satisfied | SH-02, SH-03, AS-05, AS-06 |
| MH-04 | Show the finished cup | satisfied | SH-05, AS-08 |
| MH-05 | Feature the Mixed Bag and the light-to-dark roast range | satisfied | SH-04, AS-02, AS-03, AS-04, AS-17 |
| MH-06 | End on the Blue Tokai logo, Mixed Bag pack and Shop Easy Pour CTA | satisfied | SH-06, CP-05, AS-01, AS-02 |
| MH-07 | Captions carry the message with sound off | satisfied | CP-01, CP-03, CP-04, CP-05 |
| MH-08 | Ready cut excludes unapproved price, promotion and product claims; pending identifiers are Gate 1 conditions | satisfied | ED-01, ED-02, ED-03, AC-04 |
| MH-09 | Do not call Easy Pour instant coffee or imply it needs equipment | satisfied | CL-02, CL-05, SH-03 |

## 3. Beat sheet

| Beat | Frames | Purpose | Spoken | On screen | Emotion |
|---|---|---|---|---|---|
| BT-01 | [0,75) | Name the category and show the product before the scroll decision. | Specialty coffee. | SPECIALTY COFFEE. | curiosity |
| BT-02 | [75,160) | Prove the sachet contains a real filter. | Tear, anchor, pour. | TEAR. ANCHOR. POUR. | recognition |
| BT-03 | [160,275) | Show water hitting the grounds and coffee blooming. | Just a mug and hot water. | JUST A MUG AND HOT WATER. | proof |
| BT-04 | [275,380) | Make the light-to-dark range concrete. | Light to dark. | LIGHT TO DARK. | choice |
| BT-05 | [380,445) | Land the finished cup and the honest time compression. | One mug. One cup. | ONE MUG. ONE SACHET. ONE CUP. | satisfaction |
| BT-06 | [445,500) | Close on brand, Mixed Bag and a direct CTA. | Shop Easy Pour. | SHOP EASY POUR | confidence |

## 4. Shot plan

| Shot | Frames | Time | Picture | Method | Fallback | Status |
|---|---|---|---|---|---|---|
| SH-01 | [0,75) | 0.00-3.00s | Medium-wide kitchen counter; pack at camera right, type left. The pack lands; the category line holds. | Live-action counter plate with product cut-out and kinetic type. | Static pack-on-counter still with a slow push-in and type fade. | ready |
| SH-02 | [75,160) | 3.00-6.40s | Overhead close-up of hands, sachet and mug. Tear, open, anchor; the filter seats on the mug rim. | Real-time overhead food demonstration, one continuous take. | Stop-motion of the same steps at two frames per action. | ready |
| SH-03 | [160,275) | 6.40-11.00s | Macro side profile of the filter over the mug. First pour blooms the grounds; a short time-lapse carries the repeated pours and steep before the first drip resolves. | Macro live-action pour at 50 fps, finished at 25 fps. | Still macro pour plate with animated steam and a slow scale. | ready |
| SH-04 | [275,380) | 11.00-15.20s | Four-pack fan across the counter; type above. The four-pack fan lands and holds for label recognition. | Product stills with a four-pack fan and a single camera move. | Captured four-pack still on the same counter with a slow scale; keep the light and dark endpoints. | ready |
| SH-05 | [380,445) | 15.20-17.80s | Finished cup at camera left; pack at right; type above. The cup settles; the disclaimer holds under the frame. | Finished-cup live action with a time-lapse transition. | Still cup with animated steam and a type-only time card. | ready |
| SH-06 | [445,500) | 17.80-20.00s | Cream end card; logo left, pack right, CTA and brand below. The end card holds for the final read. | End-card composite with supplied logo and pack. | Typographic end card with logo, scaled Mixed Bag pack and CTA; the pack remains mandatory even if the hero image is unavailable. | ready |

## 5. Shot x Layer x Asset

### Effect plan

| ID | Family | Effect | Behaviour | Target | Timing | Intensity / direction | Sync | Fallback / acceptance |
|---|---|---|---|---|---|---|---|---|
| FX-01 | practical | steam_drift | simulate | SH-01 / LY-012 | 0-75 | 0.18 / up_right | AU-02 | Static pack plate with a slow grade shift. / Steam moves inside its mask and never crosses the pack label. |
| FX-02 | liquid_food | macro_pour | prove | SH-03 / LY-031 | 0-115 | 0.8 / top_down | AU-03 | Still pour plate with animated steam and drip. / Water visibly contacts the coffee bed; bloom and first drip read; the filter stays anchored. |
| FX-03 | editorial | time_lapse | compress | SH-03 / LY-031 | 55-115 | 0.7 / forward | AU-01 | Short step montage with the same disclosure. / Repeated pours and steep are compressed; disclosure is visible. |
| FX-04 | product | range_fan | reveal | SH-04 | 0-105 | 0.6 / left_to_right | AU-02 | Captured four-pack still with a slow scale. / Four pack names and descriptors read; light-to-dark order is unambiguous. |
| FX-05 | practical | finished_steam | simulate | SH-05 / LY-051 | 0-65 | 0.12 / up_right | AU-02 | Still cup with a simple animated steam plate. / Steam reads as hot coffee and stays clear of the pack label. |
| FX-06 | motion_type | cta_fade | emphasise | SH-06 / LY-063 | 0-6 | 1 / none | AU-04 | Static end card with the CTA already visible. / CTA is legible by frame 6 and remains inside the end-card plate. |

### SH-01 - Name the category and put the product in frame immediately.

**Framing:** Medium-wide kitchen counter; pack at camera right, type left.  
**Movement:** A 12-frame pack settle; steam drifts across the negative space.  
**Lighting:** Soft window key from camera left; gentle fill on the label.  
**Palette:** Blue Tokai blue, cream, warm oak, black coffee.  
**Continuity:** Same counter, mug and daylight for the whole film.  
**Transition in:** Cold open.  
**Lens / handles:** 35mm full-frame normal perspective; no wide distortion. · 6 frame handles  
**Shot acceptance:** Pack and SPECIALTY COFFEE are readable by frame 12; the label is clear of type and no text crosses the safe area.  
**Effects:** FX-01  

| Layer | Role | Frames | Z | Rect | Binding | Effects | Text / opacity | Motion | Effect | Effect spec | Anchor / rotation | Req | Exact | Protected | Allowed edits | Acceptance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LY-010 | background | 0-75 | 0 | 0,0,1920,1080 | asset:AS-07 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | illustrative | - | colour grade, timing within 4 frames, crop within 5 percent | AS-07 reads clearly in the background layer; the protected region remains unobstructed at final phone scale. |
| LY-011 | product | 0-75 | 10 | 1080,180,700,700 | asset:AS-02 | - | opacity 1, fill - | f0: y 220, scale 0.94 (linear); f12: y 180, scale 1 (ease_out) | - | - | top-left / 0° | yes | exact | 1150,340 560x360 | colour grade, timing within 4 frames, crop within 5 percent | AS-02 reads clearly in the product layer; the protected region remains unobstructed at final phone scale. |
| LY-012 | effect | 0-75 | 8 | 900,170,760,720 | none:- | FX-01 | opacity 0.18, fill #DCE8F0 | - | steam_drift | Authored steam plate for FX-01. Timing, mask and acceptance are recorded on FX-01; this layer supplies the visual plate only. | top-left / 0° | yes | illustrative | - | opacity, timing | Steam moves slowly inside its mask and never crosses the pack label. |
| LY-013 | typography | 0-75 | 20 | 120,150,1000,180 | copy:CP-01 | - | Inter 86px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | - | - | - | top-left / 0° | yes | proposed_copy | whole layer | none without renewed approval | CP-01 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |
| LY-014 | caption_plate | 0-75 | 25 | 110,880,1320,110 | none:- | - | opacity 0.88, fill #F7F3EC | - | - | - | top-left / 0° | yes | illustrative | - | height, opacity | Plate provides contrast behind the copy and does not cover any protected product region. |
| LY-015 | caption | 0-75 | 30 | 120,900,1300,70 | copy:CP-07 | - | Inter 38px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | - | - | - | top-left / 0° | yes | proposed_copy | - | position within safe area, size within 10 percent, colour grade | CP-07 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |

### SH-02 - Prove the sachet has a built-in filter.

**Framing:** Overhead close-up of hands, sachet and mug.  
**Movement:** Locked-off overhead; hands enter left and work in real time.  
**Lighting:** Soft overhead key; no hand shadow across the filter.  
**Palette:** Kraft paper, cream filter, blue mug, warm counter.  
**Continuity:** Same mug and counter; hands enter from the left.  
**Transition in:** Match cut from the pack in SH-01.  
**Lens / handles:** 50mm overhead, locked-off; hands fill the centre third. · 4 frame handles  
**Shot acceptance:** Tear, open and anchor are each visible and physically correct; the filter is seated on the mug rim by the last frame.  
**Effects:** none  

| Layer | Role | Frames | Z | Rect | Binding | Effects | Text / opacity | Motion | Effect | Effect spec | Anchor / rotation | Req | Exact | Protected | Allowed edits | Acceptance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LY-020 | background | 0-85 | 0 | 0,0,1920,1080 | asset:AS-07 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | illustrative | - | colour grade, timing within 4 frames, crop within 5 percent | AS-07 reads clearly in the background layer; the protected region remains unobstructed at final phone scale. |
| LY-021 | subject | 0-85 | 10 | 160,70,1040,900 | asset:AS-05 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | illustrative | - | colour grade, timing within 4 frames, crop within 5 percent | AS-05 reads clearly in the subject layer; the protected region remains unobstructed at final phone scale. |
| LY-022 | product | 0-85 | 12 | 1360,120,440,440 | asset:AS-02 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | exact | 1390,240 380x220 | colour grade, timing within 4 frames, crop within 5 percent | AS-02 reads clearly in the product layer; the protected region remains unobstructed at final phone scale. |
| LY-023 | typography | 0-85 | 20 | 120,120,900,160 | copy:CP-03 | - | Inter 82px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | - | - | - | top-left / 0° | yes | proposed_copy | whole layer | none without renewed approval | CP-03 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |
| LY-024 | caption_plate | 0-85 | 25 | 110,880,1320,110 | none:- | - | opacity 0.88, fill #F7F3EC | - | - | - | top-left / 0° | yes | illustrative | - | height, opacity | Plate provides contrast behind the copy and does not cover any protected product region. |
| LY-025 | caption | 0-85 | 30 | 120,900,1300,70 | copy:CP-08 | - | Inter 38px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | - | - | - | top-left / 0° | yes | proposed_copy | - | position within safe area, size within 10 percent, colour grade | CP-08 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |

### SH-03 - Show water hitting the grounds; the edit compresses the repeated pours and steep.

**Framing:** Macro side profile of the filter over the mug.  
**Movement:** Slow push-in as the bloom rises; a 50 fps pour insert.  
**Lighting:** Backlit steam with a warm edge on the water.  
**Palette:** Deep brown, copper, cream, blue rim.  
**Continuity:** Mug rim and filter position match SH-02.  
**Transition in:** Cut on the kettle tilt from SH-02.  
**Lens / handles:** 100mm macro; shallow depth, focus on the coffee bed and first drip. · 5 frame handles  
**Shot acceptance:** Water visibly contacts the grounds; bloom and first drip read; the filter stays anchored and the mug rim does not jump.  
**Effects:** FX-02, FX-03  

| Layer | Role | Frames | Z | Rect | Binding | Effects | Text / opacity | Motion | Effect | Effect spec | Anchor / rotation | Req | Exact | Protected | Allowed edits | Acceptance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LY-030 | background | 0-115 | 0 | 0,0,1920,1080 | asset:AS-07 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | illustrative | - | colour grade, timing within 4 frames, crop within 5 percent | AS-07 reads clearly in the background layer; the protected region remains unobstructed at final phone scale. |
| LY-031 | subject | 0-115 | 10 | 0,70,1200,900 | asset:AS-06 | FX-02, FX-03 | opacity 1, fill - | - | - | - | top-left / 0° | yes | illustrative | - | colour grade, timing within 4 frames, crop within 5 percent | AS-06 reads clearly in the subject layer; the protected region remains unobstructed at final phone scale. |
| LY-032 | product | 0-115 | 12 | 1350,180,480,480 | asset:AS-02 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | exact | 1390,300 400x260 | colour grade, timing within 4 frames, crop within 5 percent | AS-02 reads clearly in the product layer; the protected region remains unobstructed at final phone scale. |
| LY-033 | typography | 0-115 | 20 | 120,120,1050,160 | copy:CP-02 | - | Inter 78px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | - | - | - | top-left / 0° | yes | proposed_copy | whole layer | none without renewed approval | CP-02 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |
| LY-034 | caption_plate | 0-115 | 25 | 110,880,1320,110 | none:- | - | opacity 0.88, fill #F7F3EC | - | - | - | top-left / 0° | yes | illustrative | - | height, opacity | Plate provides contrast behind the copy and does not cover any protected product region. |
| LY-035 | caption | 0-115 | 30 | 120,900,1300,70 | copy:CP-09 | - | Inter 38px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | - | - | - | top-left / 0° | yes | proposed_copy | - | position within safe area, size within 10 percent, colour grade | CP-09 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |

### SH-04 - Make the light-to-dark range concrete with the named packs.

**Framing:** Four-pack fan across the counter; type above.  
**Movement:** Packs settle in a shallow arc; no rotation.  
**Lighting:** Even warm key; each front label catches the same light.  
**Palette:** Blue, cream, roast-brown and copper.  
**Continuity:** Same counter and daylight; packs face camera.  
**Transition in:** Whip pan from the brewing mug.  
**Lens / handles:** 50mm at counter height; four packs share the same focal plane. · 5 frame handles  
**Shot acceptance:** All four pack names and roast descriptors are readable; the fan reads as light, medium-dark and dark with no label occluded.  
**Effects:** FX-04  

| Layer | Role | Frames | Z | Rect | Binding | Effects | Text / opacity | Motion | Effect | Effect spec | Anchor / rotation | Req | Exact | Protected | Allowed edits | Acceptance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LY-040 | background | 0-105 | 0 | 0,0,1920,1080 | asset:AS-07 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | illustrative | - | colour grade, timing within 4 frames, crop within 5 percent | AS-07 reads clearly in the background layer; the protected region remains unobstructed at final phone scale. |
| LY-041 | product | 0-105 | 10 | 90,230,400,430 | asset:AS-02 | - | opacity 1, fill - | f0: y 250, opacity 0 (linear); f10: y 230, opacity 1 (ease_out) | - | - | top-left / 0° | yes | exact | 115,340 350x220 | colour grade, timing within 4 frames, crop within 5 percent | AS-02 reads clearly in the product layer; the protected region remains unobstructed at final phone scale. |
| LY-042 | product | 0-105 | 13 | 1440,230,400,430 | asset:AS-03 | - | opacity 1, fill - | f18: y 250, opacity 0 (linear); f28: y 230, opacity 1 (ease_out) | - | - | top-left / 0° | yes | exact | 1465,340 350x220 | colour grade, timing within 4 frames, crop within 5 percent | AS-03 reads clearly in the product layer; the protected region remains unobstructed at final phone scale. |
| LY-043 | product | 0-105 | 12 | 990,230,400,430 | asset:AS-04 | - | opacity 1, fill - | f12: y 250, opacity 0 (linear); f22: y 230, opacity 1 (ease_out) | - | - | top-left / 0° | yes | exact | 1015,340 350x220 | colour grade, timing within 4 frames, crop within 5 percent | AS-04 reads clearly in the product layer; the protected region remains unobstructed at final phone scale. |
| LY-047 | product | 0-105 | 11 | 540,230,400,430 | asset:AS-17 | - | opacity 1, fill - | f6: y 250, opacity 0 (linear); f16: y 230, opacity 1 (ease_out) | - | - | top-left / 0° | yes | exact | 565,340 350x220 | colour grade, timing within 4 frames, crop within 5 percent | AS-17 reads clearly in the product layer; the protected region remains unobstructed at final phone scale. |
| LY-044 | typography | 0-105 | 20 | 120,120,1200,150 | copy:CP-04 | - | Inter 86px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | - | - | - | top-left / 0° | yes | proposed_copy | whole layer | none without renewed approval | CP-04 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |
| LY-045 | caption_plate | 0-105 | 25 | 110,880,1320,110 | none:- | - | opacity 0.88, fill #F7F3EC | - | - | - | top-left / 0° | yes | illustrative | - | height, opacity | Plate provides contrast behind the copy and does not cover any protected product region. |
| LY-046 | caption | 0-105 | 30 | 120,900,1300,70 | copy:CP-10 | - | Inter 38px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | - | - | - | top-left / 0° | yes | proposed_copy | - | position within safe area, size within 10 percent, colour grade | CP-10 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |

### SH-05 - Land the finished cup and disclose the time compression.

**Framing:** Finished cup at camera left; pack at right; type above.  
**Movement:** Slow push-in on the cup; steam rises.  
**Lighting:** Warm key on the crema; soft falloff behind.  
**Palette:** Coffee brown, cream, blue.  
**Continuity:** Same mug, counter and pack orientation.  
**Transition in:** Time-lapse resolve from the drip.  
**Lens / handles:** 50mm at counter height; cup rim and crema in focus, pack soft behind. · 5 frame handles  
**Shot acceptance:** Finished cup reads as coffee, not a prop; the brew-sequence disclaimer is legible; pack label remains clear.  
**Effects:** FX-05  

| Layer | Role | Frames | Z | Rect | Binding | Effects | Text / opacity | Motion | Effect | Effect spec | Anchor / rotation | Req | Exact | Protected | Allowed edits | Acceptance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LY-050 | background | 0-65 | 0 | 0,0,1920,1080 | asset:AS-07 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | illustrative | - | colour grade, timing within 4 frames, crop within 5 percent | AS-07 reads clearly in the background layer; the protected region remains unobstructed at final phone scale. |
| LY-051 | subject | 0-65 | 10 | 180,140,900,850 | asset:AS-08 | FX-05 | opacity 1, fill - | - | - | - | top-left / 0° | yes | illustrative | - | colour grade, timing within 4 frames, crop within 5 percent | AS-08 reads clearly in the subject layer; the protected region remains unobstructed at final phone scale. |
| LY-052 | product | 0-65 | 12 | 1280,180,500,500 | asset:AS-02 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | exact | 1320,300 420x260 | colour grade, timing within 4 frames, crop within 5 percent | AS-02 reads clearly in the product layer; the protected region remains unobstructed at final phone scale. |
| LY-053 | typography | 0-65 | 20 | 120,700,1000,100 | copy:CP-13 | - | Inter 54px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | - | - | - | top-left / 0° | yes | proposed_copy | whole layer | none without renewed approval | CP-13 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |
| LY-054 | caption_plate | 0-65 | 25 | 110,880,1320,110 | none:- | - | opacity 0.88, fill #F7F3EC | - | - | - | top-left / 0° | yes | illustrative | - | height, opacity | Plate provides contrast behind the copy and does not cover any protected product region. |
| LY-055 | caption | 0-65 | 30 | 120,900,1000,65 | copy:CP-12 | - | Inter 30px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | - | - | - | top-left / 0° | yes | proposed_copy | - | position within safe area, size within 10 percent, colour grade | CP-12 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |

### SH-06 - Close on brand, hero pack and a direct purchase prompt.

**Framing:** Cream end card; logo left, pack right, CTA and brand below.  
**Movement:** CTA and caption fade up over six frames; pack holds.  
**Lighting:** Even cream card with a soft pack shadow.  
**Palette:** Cream, Blue Tokai blue, pack colours.  
**Continuity:** Pack orientation matches SH-04 and SH-05.  
**Transition in:** Cut from the finished cup.  
**Lens / handles:** 35mm graphic end card; no camera movement after the settle. · 4 frame handles  
**Shot acceptance:** Logo, Mixed Bag pack, CTA and brand name are all readable in the final hold; no element is clipped by the end-card plate.  
**Effects:** FX-06  

| Layer | Role | Frames | Z | Rect | Binding | Effects | Text / opacity | Motion | Effect | Effect spec | Anchor / rotation | Req | Exact | Protected | Allowed edits | Acceptance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LY-060 | background | 0-55 | 0 | 0,0,1920,1080 | asset:AS-07 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | illustrative | - | colour grade, timing within 4 frames, crop within 5 percent | AS-07 reads clearly in the background layer; the protected region remains unobstructed at final phone scale. |
| LY-061 | product | 0-55 | 10 | 1180,100,600,520 | asset:AS-02 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | exact | 1220,230 520x300 | colour grade, timing within 4 frames, crop within 5 percent | AS-02 reads clearly in the product layer; the protected region remains unobstructed at final phone scale. |
| LY-062 | logo | 0-55 | 20 | 150,140,520,220 | asset:AS-01 | - | opacity 1, fill - | - | - | - | top-left / 0° | yes | exact | whole layer | colour grade, timing within 4 frames, crop within 5 percent | AS-01 reads clearly in the logo layer; the protected region remains unobstructed at final phone scale. |
| LY-063 | cta | 0-55 | 30 | 150,680,900,90 | copy:CP-05 | FX-06 | Inter 58px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | f0: opacity 0 (linear); f6: opacity 1 (ease_out) | - | - | top-left / 0° | yes | proposed_copy | whole layer | none without renewed approval | CP-05 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |
| LY-064 | caption_plate | 0-55 | 25 | 140,650,1320,300 | none:- | - | opacity 0.88, fill #F7F3EC | - | - | - | top-left / 0° | yes | illustrative | - | height, opacity | Plate provides contrast behind the copy and does not cover any protected product region. |
| LY-065 | caption | 0-55 | 40 | 150,890,1200,60 | copy:CP-11 | - | Inter 34px/700, #132A3A, left, line 1.08, tracking -1.0, max 2 lines | f8: opacity 0 (linear); f14: opacity 1 (ease_out) | - | - | top-left / 0° | yes | proposed_copy | - | position within safe area, size within 10 percent, colour grade | CP-11 renders exactly, inside the safe area, with no clipping or unintended line break at final phone scale. |

## 6. Asset requirements

| Asset | Name | Route | Rights | Exact | Specification | Estimate | Fallback | Used by |
|---|---|---|---|---|---|---|---|---|
| AS-01 | Blue Tokai Coffee Roasters logo | supplied | needs_approval | exact | PNG; no fixed raster | - | - | LY-062 |
| AS-02 | Easy Pour Mixed Bag pack | supplied | needs_approval | exact | JPEG; 1800x1800 | 4.00 | AS-13 | LY-011, LY-022, LY-032, LY-041, LY-052, LY-061 |
| AS-03 | Easy Pour Vienna pack | supplied | needs_approval | exact | JPEG; 1800x1800 | 3.00 | - | LY-042 |
| AS-04 | Easy Pour Attikan Estate pack | supplied | needs_approval | exact | JPEG; 1800x1800 | 3.00 | - | LY-043 |
| AS-17 | Easy Pour Seethargundu Estate pack | supplied | needs_approval | exact | JPEG; 1800x1800 | 3.00 | - | LY-047 |
| AS-05 | Easy Pour brewing demonstration, hands | to_capture | needs_approval | illustrative | ProRes 422 HQ; 3840x2160 | 18.00 | - | LY-021 |
| AS-06 | Hot water pour and bloom footage | to_capture | needs_approval | illustrative | ProRes 422 HQ; 3840x2160 | 18.00 | - | LY-031 |
| AS-07 | Warm kitchen background | owned | cleared | illustrative | PNG; 1920x1080 | - | - | LY-010, LY-020, LY-030, LY-040, LY-050, LY-060 |
| AS-08 | Finished cup of coffee | to_capture | needs_approval | illustrative | ProRes 422 HQ; 3840x2160 | 18.00 | - | LY-051 |
| AS-09 | Voice over, warm Indian English | to_create | needs_approval | illustrative | WAV; no fixed raster | 12.00 | AS-15 | AU-01 |
| AS-10 | Music bed, 20 seconds | to_source | needs_approval | illustrative | WAV; no fixed raster | 10.00 | AS-14 | AU-02 |
| AS-11 | Water pour sound effect | owned | cleared | illustrative | WAV; no fixed raster | - | - | AU-03 |
| AS-12 | Brand sting | owned | cleared | illustrative | WAV; no fixed raster | - | - | AU-04 |
| AS-13 | Captured Mixed Bag fallback | to_capture | needs_approval | exact | PNG; 2400x2400 | 5.00 | - | - |
| AS-14 | Music fallback track | to_source | needs_approval | illustrative | WAV; no fixed raster | - | - | - |
| AS-15 | Synthetic narration fallback | to_generate | needs_approval | illustrative | WAV; no fixed raster | - | - | - |

### Asset briefs

**AS-01 - Blue Tokai Coffee Roasters logo**

- Route: `supplied`; status: `pending`
- Source: User-supplied logo attachment, 2026-11-14; public footer fallback: https://bluetokaicoffee.com/cdn/shop/files/logo-footer.png?v=1688108473
- Description: User-supplied Blue Tokai circular logo attachment (2026-11-14): peacock mark with BLUE TOKAI COFFEE ROASTERS. Use the supplied proportions and colour; do not redraw. The public footer URL is a fallback reference only.
- Rights: `needs_approval`; licence: Brand logo advertising licence (pending); consent: -; AI generated: no; disclosure: no
- Technical: PNG; -x-; fps -; frames -; Use the largest available master; do not upscale a thumbnail.
- Allowed edits: scale proportionally
- Dependencies: -; fallback: -
- Generation spec: -
- Acceptance: Logo edges clean at end-card size; proportions and colour match the supplied master.
- Notes: -

**AS-02 - Easy Pour Mixed Bag pack**

- Route: `supplied`; status: `pending`
- Source: https://bluetokaicoffee.com/cdn/shop/files/MixedBag__Front_c9b610f1-ce4a-4b53-8b30-f6ca758eb6bb.jpg?v=1717566490
- Description: Front pack of Mixed | Light to Dark Roasts - Easy Pour. The title, roast descriptor and Blue Tokai mark must remain legible.
- Rights: `needs_approval`; licence: Brand pack advertising licence (pending); consent: -; AI generated: no; disclosure: no
- Technical: JPEG; 1800x1800; fps -; frames -; Crop only to the pack edge; do not crop the front label.
- Allowed edits: background removal, drop shadow, colour match to grade
- Dependencies: -; fallback: AS-13
- Generation spec: -
- Acceptance: Front title, ‘Light to Dark Roasts’ and Blue Tokai mark readable at phone scale; no label crop.
- Notes: -

**AS-03 - Easy Pour Vienna pack**

- Route: `supplied`; status: `pending`
- Source: https://bluetokaicoffee.com/cdn/shop/files/ViennaRoast__Front_1_a175faba-8e5f-40b8-aaa1-0efc3a525321.jpg?v=1717565466
- Description: Front pack of Vienna | Dark Roast - Easy Pour.
- Rights: `needs_approval`; licence: Brand pack advertising licence (pending); consent: -; AI generated: no; disclosure: no
- Technical: JPEG; 1800x1800; fps -; frames -; Front pack only; keep the roast descriptor visible.
- Allowed edits: background removal, colour match to grade
- Dependencies: -; fallback: -
- Generation spec: -
- Acceptance: Vienna name and dark-roast descriptor readable; no label crop.
- Notes: -

**AS-04 - Easy Pour Attikan Estate pack**

- Route: `supplied`; status: `pending`
- Source: https://bluetokaicoffee.com/cdn/shop/files/AttikanEstate__Front.jpg?v=1764321548
- Description: Front pack of Attikan Estate | Medium-Dark Roast - Easy Pour.
- Rights: `needs_approval`; licence: Brand pack advertising licence (pending); consent: -; AI generated: no; disclosure: no
- Technical: JPEG; 1800x1800; fps -; frames -; Front pack only; keep the roast descriptor visible.
- Allowed edits: background removal, colour match to grade
- Dependencies: -; fallback: -
- Generation spec: -
- Acceptance: Attikan name and medium-dark descriptor readable; no label crop.
- Notes: -

**AS-17 - Easy Pour Seethargundu Estate pack**

- Route: `supplied`; status: `pending`
- Source: https://bluetokaicoffee.com/cdn/shop/files/Seethargundu-Estate__Front_1.jpg?v=1764321548
- Description: Front pack of Seethargundu Estate | Light Roast - Easy Pour.
- Rights: `needs_approval`; licence: Brand pack advertising licence (pending); consent: -; AI generated: no; disclosure: no
- Technical: JPEG; 1800x1800; fps -; frames -; Front pack only; keep the light-roast descriptor visible.
- Allowed edits: background removal, colour match to grade
- Dependencies: -; fallback: -
- Generation spec: -
- Acceptance: Seethargundu name and light-roast descriptor readable; no label crop.
- Notes: -

**AS-05 - Easy Pour brewing demonstration, hands**

- Route: `to_capture`; status: `pending`
- Source: In-house food shoot
- Description: Controlled kitchen demonstration: lift the sachet, tear the outer pack, open the built-in filter, anchor it on a 180-200 ml mug. Hands only; no face required.
- Rights: `needs_approval`; licence: Talent and hand release (pending); consent: Hand model release pending; AI generated: no; disclosure: no
- Technical: ProRes 422 HQ; 3840x2160; fps 25; frames 170; Shoot 4K for a 1080p master crop; 180-degree shutter.
- Allowed edits: trim, speed within 10 percent, colour grade
- Dependencies: AS-02; fallback: -
- Generation spec: -
- Acceptance: Tear, open and anchor actions are physically correct and match the brand instructions.
- Notes: -

**AS-06 - Hot water pour and bloom footage**

- Route: `to_capture`; status: `pending`
- Source: In-house food shoot
- Description: Macro hot water hitting the coffee bed inside the anchored filter; visible bloom and drip into the mug.
- Rights: `needs_approval`; licence: In-house capture approval (pending); consent: -; AI generated: no; disclosure: no
- Technical: ProRes 422 HQ; 3840x2160; fps 50; frames 140; Source timebase 50 fps; conform to the 25 fps master at 50 percent speed.
- Allowed edits: trim, retime, colour grade
- Dependencies: AS-05; fallback: -
- Generation spec: -
- Acceptance: Water visibly contacts the coffee bed; bloom and drip read in macro; no spill or continuity break.
- Notes: -

**AS-07 - Warm kitchen background**

- Route: `owned`; status: `pending`
- Source: In-house set build
- Description: Warm daylight kitchen counter with soft linen and a blue-grey wall. The background must not compete with the pack.
- Rights: `cleared`; licence: In-house production asset; consent: -; AI generated: no; disclosure: no
- Technical: PNG; 1920x1080; fps -; frames -; 
- Allowed edits: -
- Dependencies: -; fallback: -
- Generation spec: -
- Acceptance: Full-canvas background holds a consistent grade across all six shots.
- Notes: -

**AS-08 - Finished cup of coffee**

- Route: `to_capture`; status: `pending`
- Source: In-house food shoot
- Description: Finished cup of brewed Easy Pour coffee on the same counter, with a thin steam plume and a clean rim.
- Rights: `needs_approval`; licence: In-house capture approval (pending); consent: -; AI generated: no; disclosure: no
- Technical: ProRes 422 HQ; 3840x2160; fps 25; frames 90; Shoot 4K; keep the cup rim and coffee surface in focus.
- Allowed edits: trim, colour grade
- Dependencies: AS-06; fallback: -
- Generation spec: -
- Acceptance: Finished cup matches the brewed colour; rim clean; steam visible without obscuring the pack.
- Notes: -

**AS-09 - Voice over, warm Indian English**

- Route: `to_create`; status: `pending`
- Source: Voice artist session
- Description: Canonical narration: Specialty coffee. Tear, anchor, pour. Just a mug and hot water. Light to dark. One mug. One cup. Shop Easy Pour. Recorded by a human voice artist.
- Rights: `needs_approval`; licence: Performer release (pending); consent: Voice performer release pending; AI generated: no; disclosure: no
- Technical: WAV; -x-; fps 25; frames 500; 48 kHz, 24-bit, dry studio recording; full 20-second read.
- Allowed edits: trim, de-noise, level
- Dependencies: -; fallback: AS-15
- Generation spec: -
- Acceptance: Performer release present; intelligible read; no claim beyond the canonical script.
- Notes: -

**AS-10 - Music bed, 20 seconds**

- Route: `to_source`; status: `pending`
- Source: Production music library
- Description: Restrained, warm electronic bed with a soft lift at the range reveal and a clean resolve under the end card.
- Rights: `needs_approval`; licence: Library licence to be purchased; consent: -; AI generated: no; disclosure: no
- Technical: WAV; -x-; fps 25; frames 500; 48 kHz, 24-bit, instrumental, loopable tail.
- Allowed edits: trim, fade, level
- Dependencies: -; fallback: AS-14
- Generation spec: -
- Acceptance: Licence covers paid YouTube; 20-second edit supports the 275 range lift and 445 resolve.
- Notes: -

**AS-11 - Water pour sound effect**

- Route: `owned`; status: `pending`
- Source: In-house sound design
- Description: Close, natural water pour with a soft filter-drip tail.
- Rights: `cleared`; licence: In-house production asset; consent: -; AI generated: no; disclosure: no
- Technical: WAV; -x-; fps 25; frames 85; 
- Allowed edits: trim, level, pitch
- Dependencies: -; fallback: -
- Generation spec: -
- Acceptance: Pour sound syncs to the water action without a phasing artefact.
- Notes: -

**AS-12 - Brand sting**

- Route: `owned`; status: `pending`
- Source: In-house sound design
- Description: Low, warm brand sting under the end card.
- Rights: `cleared`; licence: In-house production asset; consent: -; AI generated: no; disclosure: no
- Technical: WAV; -x-; fps 25; frames 45; 
- Allowed edits: trim, level
- Dependencies: -; fallback: -
- Generation spec: -
- Acceptance: Sting lands under the end card and does not mask the VO.
- Notes: -

**AS-13 - Captured Mixed Bag fallback**

- Route: `to_capture`; status: `pending`
- Source: In-house studio capture
- Description: In-house still of the physical Mixed Bag on the same counter, used if the brand image cannot be cleared or is below 1800 px.
- Rights: `needs_approval`; licence: Brand pack capture approval (pending); consent: -; AI generated: no; disclosure: no
- Technical: PNG; 2400x2400; fps -; frames -; Front label square to camera; four angles.
- Allowed edits: retouch, shadow, colour match
- Dependencies: AS-02; fallback: -
- Generation spec: -
- Acceptance: Physical pack label is square to camera and at least as legible as the supplied image.
- Notes: -

**AS-14 - Music fallback track**

- Route: `to_source`; status: `pending`
- Source: Production music library
- Description: Second library bed with the same tempo, warmth and length.
- Rights: `needs_approval`; licence: Library licence to be purchased; consent: -; AI generated: no; disclosure: no
- Technical: WAV; -x-; fps 25; frames 500; 
- Allowed edits: trim, fade, level
- Dependencies: -; fallback: -
- Generation spec: -
- Acceptance: Fallback bed matches the primary tempo and emotional resolve.
- Notes: -

**AS-15 - Synthetic narration fallback**

- Route: `to_generate`; status: `pending`
- Source: Approved speech provider
- Description: Disclosed synthetic narration used only if the human session fails.
- Rights: `needs_approval`; licence: Provider terms and AI disclosure (pending); consent: -; AI generated: yes; disclosure: yes
- Technical: WAV; -x-; fps 25; frames 500; 
- Allowed edits: trim, level
- Dependencies: AS-09; fallback: -
- Generation spec: Warm Indian English, measured pace, 20 seconds, no claim beyond the canonical script. Disclose synthetic voice in the delivery notes.
- Acceptance: Synthetic read matches the canonical script and carries the disclosure decision.
- Notes: -

## 7. Copy blocks

| Copy | Role | Status | Text | Exact data | Claims |
|---|---|---|---|---|---|
| CP-01 | hook | proposed | SPECIALTY COFFEE. | - | CL-01 |
| CP-02 | headline | proposed | JUST A MUG AND HOT WATER. | - | CL-02 |
| CP-03 | headline | proposed | TEAR. ANCHOR. POUR. | - | - |
| CP-04 | headline | proposed | LIGHT TO DARK. | - | CL-03 |
| CP-05 | cta | proposed | Shop Easy Pour | ED-04 | - |
| CP-07 | caption | proposed | The filter is built into the sachet. | - | CL-05 |
| CP-08 | caption | proposed | Tear, anchor, pour. | - | - |
| CP-09 | caption | proposed | Easy Pour Mixed Bag | ED-01 | - |
| CP-10 | caption | proposed | Mixed Bag · Seethargundu · Attikan · Vienna | ED-01 | CL-04, CL-06, CL-07 |
| CP-11 | caption | proposed | Blue Tokai Coffee Roasters | ED-05 | - |
| CP-12 | disclaimer | proposed | Brew sequence compressed. | - | - |
| CP-13 | headline | proposed | One mug. One sachet. One cup. | - | - |

## 8. Exact data register

| ID | Field | Value | Status | Source | Notes |
|---|---|---|---|---|---|
| ED-01 | product_name | Easy Pour / Light to Dark Roasts — Mixed Bag | observed | SRC-02 | Brand product name; Gate 1 must approve the identifier. |
| ED-02 | price | Pack of 5: Rs 300; Pack of 10: Rs 500 | observed | SRC-02 | Variant-dependent. Not approved for advertising. |
| ED-03 | pack_size | Pack of 5 sachets / Pack of 10 sachets | observed | SRC-02 | Hero pack size has not been chosen. |
| ED-04 | cta | Shop Easy Pour | proposed | - | Brief-supplied CTA. Gate 1 must approve the exact wording. |
| ED-05 | brand_name | Blue Tokai Coffee Roasters | observed | SRC-01 | Brand identifier observed on the storefront. |

## 9. Claims register

| ID | Claim | Status | Approved wording | Limitation |
|---|---|---|---|---|
| CL-01 | Specialty coffee | verified | specialty coffee | Category descriptor; not a superiority claim. |
| CL-02 | No equipment; just a mug and hot water | verified | just a mug and hot water | Refers to the Easy Pour sachet brewing method, not all coffee. |
| CL-03 | The Mixed Bag spans light to dark roasts | verified | light to dark | Describes the assortment, not every pack having equal quantities. |
| CL-04 | Vienna is a dark roast | verified | Vienna | Product name only; bitterness language is not used. |
| CL-05 | The filter is built into the sachet | verified | filter is built into the sachet | Describes the sachet construction; not a durability claim. |
| CL-06 | Attikan Estate is a medium-dark roast | verified | Attikan | Product name only; tasting notes are not used. |
| CL-07 | Seethargundu Estate is a light roast | verified | Seethargundu | Product name only; the full roast guide is not quoted. |

## 10. Audio

| Cue | Frames | Kind | Description | Asset | Level | Essential |
|---|---|---|---|---|---|---|
| AU-01 | [0,500) | vo | Canonical read: Specialty coffee. Tear, anchor, pour. Just a mug and hot water. Light to dark. One mug. One cup. Shop Easy Pour. | AS-09 | -4.0 dB | yes |
| AU-02 | [0,500) | music | Warm restrained bed; lift at 275, resolve under the end card. | AS-10 | -20.0 dB | yes |
| AU-03 | [160,245) | sfx | Close water pour and filter drip. | AS-11 | -10.0 dB | yes |
| AU-04 | [440,485) | sfx | Low brand sting under the end card. | AS-12 | -12.0 dB | yes |

## 11. Transitions

| ID | From | To | Frame | Kind | Frames |
|---|---|---|---|---|---|
| TR-01 | SH-01 | SH-02 | 75 | match cut on pack | 5 |
| TR-02 | SH-02 | SH-03 | 160 | kettle tilt cut | 4 |
| TR-03 | SH-03 | SH-04 | 275 | whip pan | 6 |
| TR-04 | SH-04 | SH-05 | 380 | time-lapse resolve | 8 |
| TR-05 | SH-05 | SH-06 | 445 | cut to cream | 4 |

## 12. Alternate routes

| ID | Targets | Trigger | Preserved | Cost delta | Scope | Switch authority |
|---|---|---|---|---|---|---|
| ALT-01 | AS-02 | Brand pack image is not cleared or is below 1800 px. | Exact Mixed Bag label, pack silhouette and end-card hero. | 5.00 | SH-02, SH-03, SH-04, SH-05, SH-06 | Named brand producer plus planner |
| ALT-02 | AS-06 | Macro pour footage fails; use a locked-off still of the anchored filter with animated water, steam and drip. | Water-through-coffee proof and the finished cup. | 0.00 | SH-03, SH-05 | Named brand producer plus planner |
| ALT-03 | CP-05 | Brand rejects ‘Shop Easy Pour’; use ‘Explore Easy Pour’ subject to a new exact-data approval. | A direct purchase prompt on the end card. | 0.00 | SH-06 | Named brand producer |
| ALT-04 | AS-10 | Music licence is not secured or the track does not fit. | Pace, warmth and a clean end-card resolve. | 0.00 | SH-01, SH-02, SH-03, SH-04, SH-05, SH-06 | Named brand producer plus editor |

## 13. Budget

| ID | Item | Kind | Amount USD | Basis | Confidence |
|---|---|---|---|---|---|
| ES-01 | Music library licence | shared | 10.00 | operator_estimate | medium |
| ES-02 | Voice artist session and edit | shared | 12.00 | operator_estimate | medium |
| ES-03 | Edit, motion and compositing | shared | 15.00 | operator_estimate | medium |
| ES-04 | Colour grade and finishing | shared | 5.00 | operator_estimate | high |
| ES-05 | Mixed Bag pack preparation | shot | 4.00 | operator_estimate | medium |
| ES-06 | Demo and finished-cup capture | shot | 18.00 | operator_estimate | medium |
| ES-07 | Range pack preparation | shot | 3.00 | operator_estimate | high |
| ES-08 | End-card build | shot | 3.00 | operator_estimate | high |
| ES-09 | Captured pack fallback | fallback | 5.00 | operator_estimate | medium |
| ES-11 | 9:16 vertical re-edit and end-card rebuild | variant | 6.00 | operator_estimate | medium |

| Budget line | USD |
|---|---|
| Shared | 42.00 |
| Shot | 28.00 |
| Variant | 6.00 |
| Subtotal | 76.00 |
| Retry reserve (15%) | 11.40 |
| Total | 87.40 |
| Fallback | 5.00 |
| Worst case | 92.40 |
| Cap | 100.00 |

## 14. Acceptance checks

| ID | Check | Method | Level | Status | Targets |
|---|---|---|---|---|---|
| AC-01 | Timeline covers exactly 500 frames across six contiguous shots. | structural | level_1 | pass | DP-01, SH-01, SH-02, SH-03, SH-04, SH-05, SH-06 |
| AC-02 | All text sits inside the 1920x1080 safe area. | structural | level_1 | pass | SH-01, SH-02, SH-03, SH-04, SH-05, SH-06 |
| AC-03 | Pack labels and the logo are not occluded by planned layers. | structural | level_1 | pass | LY-011, LY-022, LY-032, LY-041, LY-042, LY-043, LY-047, LY-052, LY-061, LY-062 |
| AC-04 | No required layer depends on unapproved price or pack-size data. | structural | level_1 | pass | ED-02, ED-03 |
| AC-05 | Logo and CTA remain legible at 50 percent scale on a phone. | render_pixel | level_2 | pending | LY-062, LY-063 |
| AC-06 | VO is intelligible and music sits at least 6 dB under it. | audio | level_2 | pending | AU-01, AU-02 |
| AC-07 | Exact data in final pixels matches the approved values. | render_pixel | level_2 | pending | ED-01, ED-04, ED-05 |
| AC-08 | Every used claim is verified and every exact reference resolves. | structural | level_1 | pass | CL-01, CL-02, CL-03, CL-04, CL-05, CL-06, CL-07, ED-04 |
| AC-09 | A sound-off viewer understands the product, benefit and brand. | human | level_2 | pending | SH-02, SH-05, SH-06 |
| AC-10 | All picture assets are owned, supplied or commissioned; no reference footage is bound. | structural | level_1 | pass | AS-01, AS-02, AS-03, AS-04, AS-05, AS-06, AS-07, AS-08, AS-17 |
| AC-11 | Final file is 1920x1080, 25 fps, 20.0 s, H.264/AAC. | render_pixel | level_2 | pending | DP-01 |
| AC-12 | Contact sheet shows packs, labels and captions clear of platform UI. | static_preview | level_2 | pending | SH-01, SH-03, SH-04, SH-06 |
| AC-13 | Budget total plus fallback stays inside the approved cap. | structural | level_1 | pass | DP-01 |
| AC-14 | Every shot has a primary and a genuinely different fallback method. | structural | level_1 | pass | SH-01, SH-02, SH-03, SH-04, SH-05, SH-06 |
| AC-15 | The compressed brew sequence is disclosed on screen. | structural | level_1 | pass | CP-12, SH-05 |
| AC-16 | 9:16 variant keeps every pack label, caption, CTA and logo inside the vertical safe area at 1080x1920. | static_preview | level_2 | pending | DP-01, SH-01, SH-02, SH-03, SH-04, SH-05, SH-06 |

## 15. Holds

| ID | Hold | Reason | Affects | Evidence needed | Owner |
|---|---|---|---|---|---|
| HI-01 | Price and hero pack size | The storefront price varies by pack size and the brief gives no approved commercial value. | ED-02, ED-03 | Brand-approved hero pack size and advertising price with a named approver. | human |
| HI-02 | Brand pack and logo advertising rights | Public product images and logo are not an advertising licence. | AS-01, AS-02, AS-03, AS-04, AS-13, AS-17 | Written paid-media approval and high-resolution pack and logo masters. | human |
| HI-03 | Voice and music licences | No voice performer release or music licence has been supplied. | AS-09, AS-10, AS-14, AS-15 | Signed performer release and a production-library licence covering paid YouTube. | human |
| HI-04 | Demonstration and talent release | Hands and a demonstration set appear on camera; no release is supplied. | AS-05, AS-06, AS-08 | Signed hand-model/performer release and approval to film the product demonstration. | human |
| HI-05 | Brand typeface | No Blue Tokai brand font was supplied; Inter is a placeholder. | CP-01, CP-02, CP-03, CP-04, CP-05, CP-07, CP-08, CP-09, CP-10, CP-11, CP-12, CP-13 | Brand font files and typography guidance, or written approval to use Inter for this production. | human |

## 16. Decisions

| ID | Decision | Evidence | Rationale |
|---|---|---|---|
| DC-01 | Lead with 'Specialty coffee', not 'instant coffee'. | F-03, F-12 | Blue Tokai explicitly separates Easy Pour from instant coffee. The category word and a visible pack avoid a false comparison. |
| DC-02 | Demonstrate tear, anchor and first pour; compress the repeated pours and steep with a disclosure. | F-02, F-08 | The built-in filter is the product benefit. A real action proves it, and a labelled time-lapse keeps the 20-second format honest. |
| DC-03 | Hero the Mixed Bag and show Seethargundu, Attikan and Vienna as range support. | F-01, F-11, F-13 | The Mixed Bag is the first-time buyer's variety route. Four packs communicate light to dark with a real light endpoint and a dark endpoint, without turning the frame into a catalogue. |
| DC-04 | Keep price and pack size out of the ready cut. | F-04 | The values are observed but not approved, and the hero pack size is still unresolved. Price would turn observation into an ad claim. |
| DC-05 | Build a 16:9 500-frame YouTube master with early branding. | F-06, F-07 | The brief asks for a 20-second YouTube ad. A 16:9 master fits in-stream, while the pack and brand appear from the first shot. |
| DC-06 | Use the public image URLs as observed sources and hold rights. | F-05, F-10 | The supplied links identify the exact product, but public access does not grant paid-media use. Stand-ins would break exactness. |

## 17. Validation summary

**Passed:** yes  
**Failures:** 0  
**Warnings:** 14

| ID | Rule | Target | Status | Detail |
|---|---|---|---|---|
| V-009 | exact.identifiers | LY-035 | warn | product_name ED-01 is observed; Gate 1 must approve this identifier or wording |
| V-010 | exact.identifiers | LY-046 | warn | product_name ED-01 is observed; Gate 1 must approve this identifier or wording |
| V-011 | exact.identifiers | LY-063 | warn | cta ED-04 is proposed; Gate 1 must approve this identifier or wording |
| V-012 | exact.identifiers | LY-065 | warn | brand_name ED-05 is observed; Gate 1 must approve this identifier or wording |
| V-038 | rights.assets | AS-01 | warn | rights need approval for Blue Tokai Coffee Roasters logo |
| V-039 | rights.assets | AS-02 | warn | rights need approval for Easy Pour Mixed Bag pack |
| V-040 | rights.assets | AS-03 | warn | rights need approval for Easy Pour Vienna pack |
| V-041 | rights.assets | AS-04 | warn | rights need approval for Easy Pour Attikan Estate pack |
| V-042 | rights.assets | AS-05 | warn | rights need approval for Easy Pour brewing demonstration, hands |
| V-043 | rights.assets | AS-06 | warn | rights need approval for Hot water pour and bloom footage |
| V-044 | rights.assets | AS-08 | warn | rights need approval for Finished cup of coffee |
| V-045 | rights.assets | AS-09 | warn | rights need approval for Voice over, warm Indian English |
| V-046 | rights.assets | AS-10 | warn | rights need approval for Music bed, 20 seconds |
| V-047 | rights.assets | AS-17 | warn | rights need approval for Easy Pour Seethargundu Estate pack |

## 18. Critique and top three

No material findings. The ready plan has no unapproved commercial layer, no safe-area violation, no over-cap estimate and no unknown rights on a required asset. Remaining warnings are Gate 1 conditions.

| ID | Category | Severity | Priority | Owner | Disposition | Action |
|---|---|---|---|---|---|---|
| - | - | - | - | - | - | No findings. |

## 19. Gate 1 conditions

- HI-01 Price and hero pack size: Brand-approved hero pack size and advertising price with a named approver.
- HI-02 Brand pack and logo advertising rights: Written paid-media approval and high-resolution pack and logo masters.
- HI-03 Voice and music licences: Signed performer release and a production-library licence covering paid YouTube.
- HI-04 Demonstration and talent release: Signed hand-model/performer release and approval to film the product demonstration.
- HI-05 Brand typeface: Brand font files and typography guidance, or written approval to use Inter for this production.
- exact.identifiers: brand_name ED-05 is observed; Gate 1 must approve this identifier or wording
- exact.identifiers: cta ED-04 is proposed; Gate 1 must approve this identifier or wording
- exact.identifiers: product_name ED-01 is observed; Gate 1 must approve this identifier or wording
- rights.assets: rights need approval for Blue Tokai Coffee Roasters logo
- rights.assets: rights need approval for Easy Pour Attikan Estate pack
- rights.assets: rights need approval for Easy Pour Mixed Bag pack
- rights.assets: rights need approval for Easy Pour Seethargundu Estate pack
- rights.assets: rights need approval for Easy Pour Vienna pack
- rights.assets: rights need approval for Easy Pour brewing demonstration, hands
- rights.assets: rights need approval for Finished cup of coffee
- rights.assets: rights need approval for Hot water pour and bloom footage
- rights.assets: rights need approval for Music bed, 20 seconds
- rights.assets: rights need approval for Voice over, warm Indian English

## 20. Research basis

| ID | Source | Accessed | Reliability |
|---|---|---|---|
| SRC-01 | Blue Tokai Coffee Roasters storefront | 2026-11-14 | primary |
| SRC-02 | Mixed / Light to Dark Roasts - Easy Pour product page | 2026-11-14 | primary |
| SRC-03 | Vienna / Dark Roast - Easy Pour product page | 2026-11-14 | primary |
| SRC-04 | Attikan Estate / Medium-Dark Roast - Easy Pour product page | 2026-11-14 | primary |
| SRC-05 | Easy Pour brewing instructions | 2026-11-14 | primary |
| SRC-06 | Google Ads: About the ABCDs of effective video ads | 2026-11-14 | secondary |
| SRC-07 | Google Ads: About video ad specs | 2026-11-14 | secondary |
| SRC-08 | Operator assumption: 16:9 YouTube in-stream profile | 2026-11-14 | assumption |
| SRC-09 | Brief-supplied audience and core message | 2026-11-14 | primary |
| SRC-10 | The Rich & Bold Trio Pack | 2026-11-14 | primary |
