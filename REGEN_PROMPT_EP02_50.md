# 🎬 REGEN PROMPT EP02-50 — SVHMP Vietnamese horror narration

> Copy nguyên block vào CMD Claude khác để regen từng EP.
> Mỗi CMD lo 5-10 EPs để parallel speed up.

---

## PROMPT (copy nguyên):

```
Bạn là Generator SVHMP. NHIỆM VỤ: regen EP_N (N = 2 đến 50) từ đầu.

WORKING DIR: D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\

LOAD ORDER (BẮT BUỘC trước khi viết):
1. bible/00_constitution.yaml — 35 rules R40-R73
2. bible/01_narrative_structure.yaml — Ngạn opening + sensory hierarchy + cliffhanger pool
3. bible/21_series_arc_design.yaml + bible/21b_ep51_90_spec.yaml — Arc map
4. bible/22_anti_slop_vi.yaml + bible/22b_anti_ai_tone_kentjuno.yaml — Anti-AI tone
5. bible/24_meta_arc_easter_eggs.yaml — Easter eggs cho EP73/90 future
6. data/place_names.yaml — Whitelist địa danh R71
7. output/ep_01/episode.md — REFERENCE EP (đã golden + Mr.Long approve)

CONSTRAINTS HARD (rule cứng Mr.Long 28/6):

A) ANAPHORA — "Bất kể từ gì không được lặp liền nhau quá 2 lần":
   - Trigger words {Khải-Phong, Khải, Cô, Anh, Bà, Ông, Em, Tôi, Bác}
   - CẤM 3 câu liên tiếp đều bắt đầu với trigger word (kể cả MIXED)
   - Vary subject bằng synonym: "Người đàn ông", "Người con gái", "Bóng anh"...
   - Hoặc merge 2-3 câu ngắn vào 1 câu compound

B) TTS PRONUNCIATION:
   - R58 CẤM dấu ngã cuối câu (Mỹ./cũ./xã.)
   - R60 CẤM câu ≤3 từ ending mono-syl (im./đi./tan.)
   - R61 CẤM mở đầu câu ngắn "Đêm./Hôm./Năm." (≤5 words trigger)
   - R66 1 câu ngắn 4-6 từ phải đi kèm 1 câu dài ≥10 từ
   - R67 "nhớ/quên" = distant past / "nhận ra" = vừa xảy ra / "hiểu" = lý do
   - R69 số <100 + giờ giấc VIẾT CHỮ (bảy giờ, không "7 giờ")

C) NGẠN STYLE (bible/01):
   - Opening = bối cảnh thời gian/địa danh + nhân chứng frame
     ✓ "Tháng tư Hà Nội. Mưa từ bảy giờ tối, không dứt."
     ✗ "Tôi giật mình tỉnh giấc."
   - Bimodal sentence: câu dài 60-100 từ xen câu cụt 3-7 từ
   - Ghost manifest NGHE TRƯỚC NHÌN (tiếng dép lê / mùi nhang trước)
   - Negative-space ghost (tóc che mặt, quay lưng, không tả face features)
   - Kết = lửng triết lý (KHÔNG cliffhanger Mỹ)
   - Marker [REVEAL_PAUSE_1000ms] TRƯỚC reveal sentence
   - WPM target 142 (~16-17 phút/EP, ~2400 từ)

D) PROHIBITED CONTENT:
   - "đồng hồ cô gái" → phải là "đồng hồ nữ"
   - "in chìm trên nền cừ" → SAI ý (xà cừ là màu vỏ, không nền in chìm)
   - "mắt trắng dã/miệng há hốc/khuôn mặt biến dạng" → CẤM ghost face
   - In medias res mở đầu kiểu Mỹ → CẤM
   - Cliffhanger giật gân Mỹ → CẤM (dùng kết lửng triết lý)

E) STRUCTURE 6 sections:
   1. HOOK (≤120 từ, 0:00-0:20) [TÒ MÒ]
   2. SETUP (~480 từ, 0:20-3:30) [BẤT AN]
   3. INCIDENT (~480 từ, 3:30-6:30) [ĐỒNG CẢM]
   4. REVEAL (~600 từ, 6:30-9:30) [NGHẸN — R54 ≥600]
   5. PAYOFF (~440 từ, 10:15-13:00) [DƯ ÂM transition]
   6. CLIFFHANGER (~210 từ, 13:00-14:30) [DƯ ÂM Ngạn]

F) ARC TARGETS per EP (load bible/21):
   - Pillar (interleave family/promise/love/work/regret)
   - Memory fragment M_N (M2 EP06-10, M3 EP11-15...)
   - Object sub-arc cluster
   - Cross-EP callback (nếu schedule)
   - Milestone special (EP10/20/30/40/50)

G) CHAPTER_CONTRACT verify before commit (bible/21b schema):
   - required_beats present
   - forbidden_moves absent
   - continuity_checks pass
   - emotion_target arc hit
   - hook_goal next EP teaser

POST-WRITE GATE (BẮT BUỘC chạy trước commit):
python tools/post_render_gate.py --ep N    # 11 checks
python tools/audit_tilde_eol.py --ep N      # R58 = 0
python tools/audit_short_eol.py --ep N       # R60 ≤ 5
python tools/audit_short_start.py --ep N     # R61 ≤ 5
python tools/audit_anaphora_consecutive.py --ep N  # R62 = 0
python tools/fix_chains_zero_tolerance.py --apply  # zero mixed chains

Vi phạm ANY rule → REGEN không ship.

DELIVERABLE per EP:
- output/ep_N/episode.md (replace existing)
- Backup old → output/ep_N/episode.md.bak.regen_round_19_4
- Commit message: "Regen EP_N round 19.4 — Ngạn style + zero anaphora"

SESSION protocol:
1. Read CLAUDE.md workspace
2. Read VERSION.md (round 19)
3. Read NOTICE_ACTIVE_SESSION.md
4. Read memory project_svhmp_round_18_19_complete.md
5. Read bible/00 + bible/01 + bible/21 + bible/22 + bible/24
6. Load EP_N spec từ bible/21
7. Write new EP draft
8. Run all audits PASS
9. Commit
```

---

## 📅 Phân chia workload parallel (Mr.Long pick CMDs):

| CMD | EP range | ETA per EP |
|-----|----------|-----------|
| CMD#1 | EP02-10 (9 EPs) | ~15-20 phút/EP |
| CMD#2 | EP11-20 (10 EPs) | ~15-20 phút/EP |
| CMD#3 | EP21-30 (10 EPs) | ~15-20 phút/EP |
| CMD#4 | EP31-40 (10 EPs) | ~15-20 phút/EP |
| CMD#5 | EP41-50 (10 EPs) | ~15-20 phút/EP |

→ 5 CMDs parallel = ~3 giờ regen toàn bộ EP02-50.

---

## ⚠️ Coordination notes:

- Mỗi CMD lock 1 EP range — không overlap
- Commit format: "Regen EP_N round 19.4 — Ngạn style + zero anaphora"
- Push lên branch riêng `regen-19-4-cmd-N` nếu cần avoid main conflict
- Báo cáo: viết log vào `runtime/regen_log_cmd_N.md`
