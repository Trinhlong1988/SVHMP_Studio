> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: SVHMP_Studio/assets/hdk_channel/_AUDIT_TENTATIVE_LOG.md.
# HDK INTRO MASTER — 4.5s LOCKED storyboard

**Output target:** `assets/hdk_channel/brand\intro_master\HDK_INTRO_4500ms_LOCKED.mov`
**Spec:** 3840×2160, 24fps, 108 frames total, ProRes 422 HQ (master) + H.264 NVENC (delivery)
**Audio:** stereo 48kHz
**Lock requirement:** SHA256 byte-identical across 1000+ ep
**Source hiến pháp:** Mr.Long docx 2026-06-25 23:56 (memory entry `project_svhmp_youtube_channel.md`)

> **HIẾN PHÁP LOCK:**
> ```
> 0.0–0.8s   Màn hình đen. Gió nhẹ + chuông tàu rất xa.
> 0.8–2.2s   Đèn dầu sáng lên. Sương mù trôi. Camera tiến rất chậm.
> 2.2–3.5s   Logo "HẮC DẠ KÝ" hiện từ trong sương (không phát sáng mạnh).
> 3.5–4.5s   Tagline "Chuyện kể từ cõi vô hình" + 1 còi tàu nhỏ. Logo mờ dần.
> 4.5s       Cắt thẳng vào câu chuyện.
> ```
> **KHÔNG fade đen, KHÔNG nhạc dạo dài. KHÔNG tiếng hét/quỷ. Để người xem nhớ KHÔNG KHÍ.**

---

## Timeline 4 segment (LOCK theo docx)

| # | Segment | Time | Frames | Frame range | Asset chính |
|---|---|---|---|---|---|
| 1 | ĐEN | 0.000 – 0.800s | 19 | 0-18 | (gió + chuông tàu xa SFX, visual đen) |
| 2 | ĐÈN DẦU + SƯƠNG | 0.800 – 2.200s | 34 | 19-52 | lantern_still.png + lantern_flame_loop.mp4 + fog_loop_4s.mp4 + camera push-in slow |
| 3 | LOGO | 2.200 – 3.500s | 31 | 53-83 | hdk_logo.svg hiện từ trong sương (subtle glow, không bright) + smoke_base.png + fog_loop_4s.mp4 |
| 4 | TAGLINE + CÒI TÀU | 3.500 – 4.500s | 24 | 84-107 | hdk_tagline_channel.svg + còi tàu SFX 1 lần + logo fade ra |
| – | CẮT | 4.500s instant | 1 | 108 | hard cut, frame 108 = first frame of ep narration (KHÔNG render trong intro file) |

**Total: 108 frames @ 24fps = 4.500s exact.** Frame 108 KHÔNG thuộc intro — ep narration video bắt đầu ngay tại 4.500s.

---

## Segment 1 — ĐEN (0.000-0.800s, 19 frames, 0-18)

**Mục đích:** reset mắt khán giả, build không khí qua AUDIO (không qua visual).

| Frame | Time | Action |
|---|---|---|
| 0 | 0.000s | Pure black #000000 |
| 0-18 | 0.000-0.750s | Pure black giữ nguyên |

**Audio (CỰC QUAN TRỌNG — visual đen nên audio mang toàn bộ không khí):**
- **0.000s**: gió đêm SFX vào ngay (-12dB peak, soft attack)
- **0.000-0.800s**: gió duy trì
- **0.300s**: chuông tàu RẤT XA (-22dB, single distant bell strike, reverb tail dài 1.5s)
- **0.800s**: chuông tail vẫn còn fade (carry vào segment 2)

**Layers (bottom→top):**
1. Solid black plate

**Note:** docx LOCK ghi "Màn hình đen" → KHÔNG có dust particle như em viết bản trước (em đã rút). Visual hoàn toàn đen 0.8s.

---

## Segment 2 — ĐÈN DẦU + SƯƠNG (0.800-2.200s, 34 frames, 19-52)

**Mục đích:** "đèn dầu sáng lên, sương mù trôi, camera tiến rất chậm" — không gian cõi vô hình hiện hình.

| Frame | Time | Action |
|---|---|---|
| 19 | 0.792s | lantern_flame_loop.mp4 fade in opacity 0→100% trong 0.4s (frame 19-28), screen blend |
| 19-52 | 0.792-2.167s | lantern_still.png fade in opacity 0→90% trong 0.6s (frame 19-33), position center |
| 19-52 | 0.792-2.167s | fog_loop_4s.mp4 fade in opacity 0→60% screen blend, drift slow horizontal |
| 19-52 | 0.792-2.167s | **Camera push-in slow**: scale toàn comp 100% → 108% qua 1.4s (Resolve Fusion: animate transform center) |
| 33 | 1.375s | lantern + flame ổn định 90% opacity |
| 52 | 2.167s | fog dày 60%, chuẩn bị reveal logo |

**Audio:**
- 0.800-2.200s: gió tiếp tục (-12dB)
- 0.800-2.200s: **đèn dầu cháy** SFX vào (-18dB, subtle crackle loop, 1.4s)
- 1.200s: chuông tàu reverb tail kết thúc (từ segment 1)
- KHÔNG thêm chuông mới (chỉ "rất xa" 1 lần ban đầu)

**Layers (bottom→top):**
1. Solid black
2. fog_loop_4s.mp4 (screen blend, opacity 0→60%, drift)
3. lantern_still.png (alpha, opacity 0→90%, center, scale 100→108% camera push)
4. lantern_flame_loop.mp4 (screen blend, opacity 0→100%, khớp glass chimney, scale push)

**Camera push** áp dụng cho toàn comp (mọi layer scale đồng đều) hoặc chỉ lantern + fog (tùy Resolve Fusion setup). Effect: cảm giác MÌNH đang tiến đến đèn dầu trong sương.

---

## Segment 3 — LOGO (2.200-3.500s, 31 frames, 53-83)

**Mục đích:** logo "HẮC DẠ KÝ" hiện **từ trong sương** — KHÔNG phát sáng mạnh, ngấm dần.

| Frame | Time | Action |
|---|---|---|
| 53 | 2.208s | smoke_base.png fade in opacity 0→50% screen blend (smoke wraps logo area) |
| 53-83 | 2.208-3.458s | fog_loop_4s.mp4 tiếp tục drift, opacity 60% |
| 58 | 2.417s | hdk_logo.svg fade in opacity 0→100% trong 0.8s (frame 58-77), KHÔNG glow mạnh — chỉ subtle inner glow 15% intensity, scale 95→100% (subtle bloom) |
| 58-83 | 2.417-3.458s | lantern + flame stay background, opacity drop 90→40% (logo lên foreground) |
| 77 | 3.208s | logo lock 100% opacity, scale 100% |
| 77-83 | 3.208-3.458s | logo hold, fog vẫn drift |

**Audio:**
- 2.200-3.500s: gió tiếp tục (-12dB)
- 2.200-3.500s: piano RẤT NHẸ vào (-20dB, single low note hoặc 2-note arpeggio nhẹ, mood)
- 2.500-3.500s: đèn dầu crackle giảm dần (-22dB)
- KHÔNG còi tàu (để dành segment 4)

**Layers (bottom→top):**
1. Solid black
2. fog_loop_4s.mp4 (opacity 60%, drift)
3. smoke_base.png (screen blend, opacity 0→50%)
4. lantern_still.png (opacity 90→40%, scale 108%)
5. lantern_flame_loop.mp4 (opacity 100→40%, scale 108%)
6. hdk_logo.svg (alpha, opacity 0→100%, scale 95→100%, center, subtle inner glow 15%)

**KHÔNG dùng glow_plate_radial.png mạnh ở segment này** — docx LOCK "không phát sáng mạnh". Glow chỉ subtle qua layer style logo SVG.

---

## Segment 4 — TAGLINE + CÒI TÀU (3.500-4.500s, 24 frames, 84-107)

**Mục đích:** tagline channel + 1 còi tàu nhỏ + logo mờ dần.

| Frame | Time | Action |
|---|---|---|
| 84 | 3.500s | hdk_tagline_channel.svg fade in opacity 0→100% trong 0.5s (frame 84-95), position lower-third center |
| 84-107 | 3.500-4.458s | hdk_logo.svg fade out opacity 100→60% (mờ dần per docx "Logo mờ dần") |
| 95 | 3.958s | tagline lock 100% |
| 95-107 | 3.958-4.458s | hold tagline, fog vẫn drift, logo tiếp tục mờ tới 60% |
| 107 | 4.458s | last frame intro, frame 108 = hard cut to ep narration |

**Audio (signature moment):**
- 3.500s: **CÒI TÀU 1 LẦN NHỎ** SFX (-10dB peak, single short whistle 0.6s duration, NOT long sustained)
- 3.500-4.100s: còi tàu phát + fade
- 3.500-4.500s: gió tiếp tục background (-15dB, hơi giảm)
- 3.500-4.500s: piano tail fade out
- 4.500s: ALL audio cut hard (hand off cho ep narration audio)

**Layers (bottom→top):**
1. Solid black
2. fog_loop_4s.mp4 (opacity 60%, drift)
3. smoke_base.png (opacity 50%)
4. lantern_still.png (opacity 40%, scale 108%)
5. lantern_flame_loop.mp4 (opacity 40%, scale 108%)
6. hdk_logo.svg (opacity 100→60%, scale 100%, mờ dần)
7. hdk_tagline_channel.svg (alpha, opacity 0→100%, lower-third center)

---

## Hard cut tại 4.500s (KHÔNG segment 5 fade)

Mr.Long docx LOCK: "Cắt thẳng vào câu chuyện".
→ KHÔNG transition mask, KHÔNG fade to black, KHÔNG iris.
→ Frame 107 (4.458s) = last visible intro frame có đầy đủ tagline + fog + logo mờ.
→ Frame 108 (4.500s) = FIRST frame ep narration video.
→ Trong concat FFmpeg: ghép intro.mov + ep_narration.mp4 trực tiếp, không transition.

**Implication asset:** `transition_mask_blackout.png` (asset 13) **KHÔNG dùng cho intro**. Reserve cho end card / inter-scene khác.

---

## Render order

```
1. Render 4 segment riêng → 4 file .mov ProRes 422 HQ
   seg1_black.mov (0-18, 19f, 0.792s)
   seg2_lantern_fog.mov (19-52, 34f, 1.417s)
   seg3_logo.mov (53-83, 31f, 1.292s)
   seg4_tagline_whistle.mov (84-107, 24f, 1.000s)

2. Concat trong Resolve OR FFmpeg:
   ffmpeg -f concat -safe 0 -i seg_list.txt -c copy HDK_INTRO_4500ms_LOCKED.mov

3. Audio mux (intro_audio_4500ms.wav build riêng từ 5 track: gió/chuông xa/đèn dầu/piano/còi tàu):
   ffmpeg -i HDK_INTRO_4500ms_LOCKED.mov -i intro_audio_4500ms.wav \
          -c:v copy -c:a aac -b:a 192k -shortest HDK_INTRO_4500ms_LOCKED_AV.mov

4. SHA256 lock:
   certutil -hashfile HDK_INTRO_4500ms_LOCKED_AV.mov SHA256 > HDK_INTRO_LOCK.sha256

5. Verify byte-identical: re-render từ project file, sha256 phải match.
```

---

## Audio asset checklist (5 SFX riêng cần source)

| # | SFX | Time intro | Source recommend |
|---|---|---|---|
| 1 | Gió đêm loop | 0.0-4.5s background | YouTube Audio Library "night wind" CC0 hoặc Freesound "wind night ambient" |
| 2 | Chuông tàu xa 1 strike | 0.3s | Freesound "distant train bell" CC0 |
| 3 | Đèn dầu cháy crackle | 0.8-3.5s | Freesound "oil lamp burn" CC0 |
| 4 | Piano nốt thấp 1-2 note | 2.2-3.5s | Tự đánh trong Resolve Fairlight HOẶC Musopen single note |
| 5 | Còi tàu nhỏ 1 lần | 3.5-4.1s | Freesound "short train whistle" CC0, 0.6s duration |

→ Mix trong Resolve Fairlight hoặc Audacity → export `intro_audio_4500ms.wav` 48kHz stereo.

---

## Decision gates Mr.Long verify

- [ ] Segment 1 (ĐEN 0.8s): chuông xa volume -22dB đủ "xa" hay quá nhỏ?
- [ ] Segment 2 (ĐÈN DẦU + SƯƠNG): camera push-in scale 108% đủ "rất chậm" hay quá fast?
- [ ] Segment 3 (LOGO): inner glow 15% đúng "không phát sáng mạnh"?
- [ ] Segment 4 (CÒI TÀU): còi 0.6s đủ "nhỏ" hay cần ngắn hơn?
- [ ] Logo fade mờ tới 60% (không 0%) — Mr.Long approve không cho logo biến mất hẳn cuối intro?
- [ ] Tagline position lower-third vs center — docx không specify, em đề xuất lower-third
- [ ] Hard cut 4.500s: confirm KHÔNG transition mask?

---

## Asset usage cross-segment (sau khi sửa theo docx LOCK)

| Asset | Seg1 | Seg2 | Seg3 | Seg4 |
|---|---|---|---|---|
| dust_particle.mp4 | – | – | – | – | **KHÔNG dùng cho intro** (docx LOCK không có "dust") |
| glow_plate_radial.png | – | – | – | – | **KHÔNG dùng cho intro** (docx LOCK "không phát sáng mạnh") |
| lantern_still.png | – | ✓ (90%) | ✓ (90→40%) | ✓ (40%) | |
| lantern_flame_loop.mp4 | – | ✓ | ✓ (fade) | ✓ (40%) | |
| smoke_base.png | – | – | ✓ (50%) | ✓ (50%) | |
| fog_loop_4s.mp4 | – | ✓ (60%) | ✓ (60%) | ✓ (60%) | |
| hdk_logo.svg | – | – | ✓ (100%) | ✓ (60%) mờ dần | |
| hdk_tagline_channel.svg | – | – | – | ✓ (100%) | |
| moon_phase.png | – | – | – | – | **KHÔNG dùng cho intro** (docx LOCK không mention) |
| transition_mask_blackout.png | – | – | – | – | **KHÔNG dùng** (hard cut) |

**4/13 master asset dùng trong intro** (lantern_still, lantern_flame_loop, smoke_base, fog_loop) + 2 brand (logo, tagline_channel) = 6 asset thực sự cần cho intro.

**9/13 master asset reserve cho ep body / end card / future use:**
- moon_phase, railway_dusk, storyteller_silhouette → ep body scene
- smoke_fx, dust_particle → ep body atmospheric
- glow_plate_radial → end card highlight
- hdk_tagline_chuyenxe → end card series-specific
- transition_mask_blackout → inter-scene fade trong ep body

---

## Note quan trọng — em đã chỉnh sửa so với draft đầu

Draft đầu em viết 5 segment có "CẮT 0.5s fade". Đã rút theo docx LOCK Mr.Long 25/6:
- 5 segment → 4 segment
- ĐÈN DẦU 0.8-1.6s → 0.8-2.2s (đúng docx, lâu hơn 0.6s, có thêm "sương mù trôi + camera tiến chậm")
- LOGO 1.6-2.8s → 2.2-3.5s (đúng docx)
- TAGLINE 2.8-4.0s → 3.5-4.5s (đúng docx)
- "CẮT" segment 0.5s fade → bỏ, thay bằng hard cut instant tại 4.500s
- Bỏ dust_particle + glow_plate_radial khỏi intro (docx không mention, "không phát sáng mạnh")
- Thêm camera push-in slow segment 2 (docx specify)
- Audio: 5 SFX bible đúng docx (gió/chuông xa/đèn dầu/piano/còi tàu)
