> ✅ **APPROVED Mr.Long 2026-06-26** — TẤT CẢ T1-T8 (60+ items) đã được Mr.Long approve. File này giữ làm AUDIT TRAIL historical, KHÔNG xóa. Các file khác đã chuyển sang APPROVED banner.

# HDK Channel — AUDIT TENTATIVE_SUY_LUẬN LOG

**Lập:** 2026-06-26
**Rule:** Mr.Long "cấm suy luận" (memory `feedback_cam_suy_luan.md`)
**Status:** Master log mọi chỗ Claude suy luận trong session HDK 26/6. BLOCK render cho tới Mr.Long approve từng mục.

---

## Cách dùng

- Mr.Long đọc từng mục, gõ:
  - `APPROVE <id>` → em update file gỡ tag TENTATIVE_SUY_LUẬN, value trở thành lock fact
  - `REJECT <id> -> <value mới>` → em thay value, mark APPROVED Mr.Long
  - `SKIP <id>` → giữ TENTATIVE, không adopt
- Render asset hay ship pipeline chỉ được start khi **toàn bộ mục liên quan asset đó = APPROVED**

---

## T1 — `bible/19_motion_bible.yaml` motion values

**File:** `bible/19_motion_bible.yaml`
**Source suy luận:** AI khác (GPT/Gemini, docx Mr.Long forward 26/6) đề xuất + em adopt làm "initial tentative"

| ID | Key | Em đoán | Source thật | Action cần Mr.Long |
|---|---|---|---|---|
| T1.1 | fog_rules.speed.horizontal_drift_px_per_frame | 0.12 | AI kia | Approve hoặc set khác |
| T1.2 | fog_rules.speed.vertical_rise_px_per_frame | 0.08 | Em đoán parallel với T1.1 | Approve / set khác |
| T1.3 | fog_rules.speed.max_speed_px_per_frame | 0.20 | Em đoán cap = 1.67x base | Approve / set khác |
| T1.4 | fog_rules.density.intro_segment_2 | 60% | Em đoán | Approve |
| T1.5 | fog_rules.density.ep_body_baseline | 40% | Em đoán | Approve |
| T1.6 | lantern_rules.flame_flicker.cycle_hz | 2.0 | AI kia | Approve |
| T1.7 | lantern_rules.flame_flicker.intensity_variation_pct | 12% | AI kia | Approve |
| T1.8 | lantern_rules.color_temperature_kelvin | 2500 | Em đoán "warm đèn dầu cổ" | Approve / sửa |
| T1.9 | lantern_rules.scale_in_intro | 100→108% | Em đoán camera push amount | Approve |
| T1.10 | logo_rules.fade_in_frames | 18 | AI kia | Approve |
| T1.11 | logo_rules.fade_out_intro_frames | 24 | Em đoán (segment 4 duration) | Approve |
| T1.12 | logo_rules.scale.intro_appear | 95→100% | Em đoán "subtle bloom" | Approve / set khác |
| T1.13 | logo_rules.max_scale_ever | 105 | AI kia | Approve |
| T1.14 | logo_rules.inner_glow_intensity_pct | 15% | Em đoán từ docx "không phát sáng mạnh" | Approve |
| T1.15 | camera_rules.intro_4_5s.segment_2 | push 100→108% over 1.4s | Em đoán "rất chậm" → 1.4s | Approve / set khác |
| T1.16 | camera_rules.intro_push_speed_pct_per_s | 5.7%/s | Math từ T1.15, derived | Confirm sau khi T1.15 approve |
| T1.17 | moon_rules.opacity_ep_body_default | 35% | AI kia | Approve |
| T1.18 | dust_rules.ep_body_opacity_pct | 20% | Em đoán | Approve |
| T1.19 | signature_consistency_rules.fog_speed_drift_max_pct_across_eps | 5% | Em đoán cap drift | Approve |
| T1.20 | signature_consistency_rules.lantern_flicker_drift_max_pct_across_eps | 10% | Em đoán | Approve |
| T1.21 | signature_consistency_rules.logo_scale_drift_max_pct_across_eps | 2% | Em đoán | Approve |
| T1.22 | quality_check_per_render.intro_motion_check thresholds | various | Em đoán ±tolerance | Approve |

---

## T2 — `prompts/video_intro.md` V9 audio LUFS (FACT SAI)

**File:** `prompts/video_intro.md`
**Specific issue:** Em viết `audio_loudness_target: -18 LUFS integrated` — **SAI**, bible/10 brand_audio có varied per element (-20 rain, -16 bell distant, -30 engine_hum, -22 piano, -18 bell outro).

| ID | Key | Em đoán | Source thật bible/10 | Action |
|---|---|---|---|---|
| T2.1 | V9 audio_loudness_target | -18 LUFS integrated | KHÔNG có single target, per-element | Mr.Long quyết target master LUFS hoặc giữ per-element |
| T2.2 | V9 step_4 sources LUFS per element | KHÔNG có | bible/10 có per element nhưng cho ep narration, KHÔNG cho intro 4.5s | Cần Mr.Long quyết LUFS từng SFX intro |
| T2.3 | V9 true_peak ≤ -1 dBTP | -1 dBTP | Em đoán YouTube standard | Approve / sửa |

---

## T3 — `prompts/video_intro.md` V8 layer stack order

**File:** `prompts/video_intro.md`

| ID | Key | Em đoán | Action |
|---|---|---|---|
| T3.1 | layer_stack 8 layers z_order | bottom: solid_black → fog → smoke → lantern → flame → logo → tagline → reserve | Mr.Long verify order đúng visual không |
| T3.2 | opacity per segment cho mỗi layer | various %s | Mr.Long quyết hoặc keep TENTATIVE |
| T3.3 | layer_07_reserve future use | "vignette, color overlay" | Mr.Long quyết có dùng không |

---

## T4 — 13 SDXL/Inkscape/Wan prompts content

**Files:** `assets/hdk_channel/_prompts/01..13_*.md`
**Source suy luận:** **TOÀN BỘ** prompt content (positive prompt, negative prompt, seed strategy, resolution, style cue) là Claude suy luận từ docx structure + SDXL knowledge. Docx Mr.Long KHÔNG có 1 prompt nào cụ thể.

| ID | File | Content suy luận | Action |
|---|---|---|---|
| T4.1 | 01_brand_logo.md | Inkscape brief logo: form H+D+K negative space, vệt khói, color #E8DCC4, font Cormorant Garamond | Mr.Long verify design direction |
| T4.2 | 02_brand_typography.md | Tagline font Cormorant Garamond Italic, size 180pt, color #C9B789, letter spacing +40, drop shadow 4px | Mr.Long verify |
| T4.3 | 03_still_moon_phase.md | SDXL prompt crescent moon, navy palette, dust particles | Mr.Long verify creative |
| T4.4 | 04_still_railway_dusk.md | SDXL prompt vanishing point, dusk twilight indigo+orange, no train | Mr.Long verify |
| T4.5 | 05_still_storyteller_silhouette.md | SDXL prompt elderly profile, lantern light only, ao the dark | Mr.Long verify (đặc biệt: "elderly vietnamese storyteller" — Mr.Long có muốn storyteller character không?) |
| T4.6 | 06_still_lantern.md | SDXL prompt antique vietnamese oil lantern, brass, glass chimney | Mr.Long verify |
| T4.7 | 07_still_smoke_base.md | SDXL prompt smoke volumetric, neutral grey, black background | Mr.Long verify |
| T4.8 | 08_motion_fog_loop.md | Wan 2.1 prompt fog horizontal drift, 4s loop seamless | Mr.Long verify |
| T4.9 | 09_motion_lantern_flame.md | Wan 2.1 prompt flame inside chimney, 3s loop, breathing rhythm | Mr.Long verify |
| T4.10 | 10_motion_smoke_fx.md | Wan 2.1 prompt smoke rising vertical, 5s loop | Mr.Long verify (ep body use, intro KHÔNG dùng) |
| T4.11 | 11_motion_dust_particle.md | Wan 2.1 prompt dust particles, warm side light, 4s | Mr.Long verify |
| T4.12 | 12_utility_glow_plate.md | Inkscape radial gradient #FFE8B8 → transparent | Mr.Long verify (utility chưa được docx mention) |
| T4.13 | 13_utility_transition_mask.md | Inkscape linear + iris gradient mask | Mr.Long verify (utility chưa được docx mention) |

---

## T5 — Storyboard frame-by-frame breakdown

**File:** `assets/hdk_channel/_storyboard/intro_master_4500ms.md`
**Source:** docx Mr.Long LOCK 4 segment timing (FACT). Em **suy luận distribution** frame-level chi tiết:

| ID | Item | Em suy luận | Source thật | Action |
|---|---|---|---|---|
| T5.1 | seg_2 frame distribution: glow_plate frame 19-26, lantern fade frame 24, flame at frame 24 | timing chi tiết | Docx chỉ nói "đèn dầu sáng lên, sương mù trôi, camera tiến rất chậm" | Mr.Long approve cho phép em design timing chi tiết hoặc anh quyết |
| T5.2 | seg_3 frame distribution: smoke fade 53-66, logo fade 58-77, lantern shrink 38-47 | timing chi tiết | Docx chỉ nói "logo hiện từ trong sương, không phát sáng mạnh" | Như T5.1 |
| T5.3 | seg_4 frame distribution: tagline fade 75-87, logo mờ 84-107 (100→60%) | timing chi tiết | Docx chỉ "tagline + 1 còi tàu nhỏ + logo mờ dần" | Như T5.1, đặc biệt logo "mờ dần tới 60%" hay biến mất hẳn? |
| T5.4 | tagline position lower-third center | em quyết | Docx KHÔNG specify | Approve / center / top |
| T5.5 | Camera push amount 100→108% trong 1.4s | T1.15 reference | Như T1.15 | Approve sau T1.15 |
| T5.6 | Spark SFX 0.8s "quẹt diêm" optional segment 2 | em đề xuất | Docx KHÔNG mention | Approve / bỏ |
| T5.7 | "Inner glow 15%" logo | T1.14 reference | Như T1.14 | Approve sau T1.14 |
| T5.8 | Audio breakdown -22dB chuông xa, -18dB đèn dầu, -10dB còi tàu | em đoán mix levels | Docx chỉ "rất xa" / "nhỏ" qualitative | Mr.Long quyết dB hoặc giữ qualitative |

---

## T6 — Bible/04 channel_brand_assets extension

**File:** `bible/04_asset_bible.yaml` v1.1
**Em suy luận:**

| ID | Key | Em đoán | Action |
|---|---|---|---|
| T6.1 | Asset id naming convention: `logo_hdk_v01`, `still_lantern_v01`, `motion_fog_loop_v01`, `util_glow_plate_radial_v01` | em quyết style match bible/04 v1.0 existing | Approve / sửa style |
| T6.2 | Style_prompt strings cho mỗi asset (lấy từ 13 prompts T4) | em suy luận | Phụ thuộc T4 approve |
| T6.3 | Resolutions: still 3840x2160, lantern 2048x2048, motion 1920x1080, motion lantern 1024x1024 | em quyết | Approve / sửa |
| T6.4 | Motion duration: fog 4s, flame 3s, smoke 5s, dust 4s | em quyết | Approve |
| T6.5 | composite_pair relationships (lantern still + flame motion) | em đoán composite logic | Approve |
| T6.6 | use_in_intro flags per asset (true/false) | em đoán từ docx LOCK | Approve |
| T6.7 | channel_drift_policy rules (HARD-FAIL conditions) | em đoán theo style bible/04 v1.0 | Approve |

---

## T7 — Naming convention prefix

**Bao trùm:** mọi asset ID + file path

| ID | Key | Em quyết | AI khác đề xuất | Action |
|---|---|---|---|---|
| T7.1 | Prefix style | `lowercase_underscore_v01` (vd `logo_hdk_v01`) | `UPPERCASE_` (vd `LOGO_HDK_v01`) | Mr.Long quyết style |
| T7.2 | Version suffix `_v01` | em adopt theo bible/04 v1.0 existing | OK | Approve / sửa |

---

## T8 — Cost projection (worst-case scenario)

**File:** `assets/hdk_channel/PHUONG_AN_CHOT.md` (sắp đổi thành README.md)
**Em suy luận:**

| ID | Item | Em đoán | Action |
|---|---|---|---|
| T8.1 | Worst case $402 | Affinity $70 + Kling $37 + Resolve Studio $295 | Mr.Long approve làm projection or remove |
| T8.2 | Mega 50GB free đủ | Em đoán 13 master <5GB | Verify thực tế sau khi render |
| T8.3 | Electric local render $120/24mo | Em đoán | Skip projection nếu không có data |

---

## Summary

**8 cluster TENTATIVE_SUY_LUẬN** = ~60+ items cụ thể cần Mr.Long approve.

**Critical (render block):**
- T1.* (motion values bible/19)
- T2.* (audio LUFS V9)
- T4.* (13 SDXL prompts)
- T5.* (storyboard frame breakdown)

**Non-critical (cosmetic/projection):**
- T7.* (naming style)
- T8.* (cost projection)

---

## Mr.Long action

Đề xuất: anh đọc file này 1 lần, decide cluster nào:
- **APPROVE ALL T1** → em adopt toàn bộ motion values
- **SKIP T1** → em revert bible/19 → skeleton trống (TBD_AWAITING_MRLONG mọi value)
- **PARTIAL T1.1-T1.10 approve, T1.11-T1.22 skip** → granular

Hoặc anh đề xuất cách khác để verify.

Em đợi.
