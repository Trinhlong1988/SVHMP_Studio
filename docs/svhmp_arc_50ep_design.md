# SVHMP — ARC 50 EP DESIGN PROPOSAL (round 4)

**Date:** 2026-06-27
**Trigger:** Mr.Long 26/6 reject "EP11-41 lộn xộn không thành bản nhạc"
**Status:** PROPOSAL — chờ Mr.Long approve trước khi rework
**Scope:** Re-design EP11-50 (40 EPs) + lay foundation cho EP51-90

---

## 1. PROBLEM DIAGNOSIS — vì sao "lộn xộn"

| # | Lỗi | Hệ quả |
|---|---|---|
| L1 | Linear pillar distribution (FAM_005 6 EPs liên tiếp, LOV_001 4 EPs liên tiếp...) | Block flat — như 6 bài cùng nốt |
| L2 | Mỗi EP đứng riêng — không có cross-EP arc | Khán giả không có "case thắt" theo dõi |
| L3 | Intensity flat (level 0.55 từ EP11→EP41) | Không có cao trào tăng dần |
| L4 | Quang memory unlock random + đơn lẻ | Không thấy Quang đi đâu về đâu |
| L5 | Item collection chỉ là counter (1 vật / EP) — không kết tiếp arc | 38 items thành 38 mảnh rời |
| L6 | Milestone EP (EP10, EP20, EP30, EP40) không khác EP thường | Không có "ô nhịp" để thở |

---

## 2. FIX — 6 ARC RULES (AR1-AR6)

### AR1 — PILLAR INTERLEAVE

**Rule:** Không dồn >2 EPs cùng pillar liên tiếp.

| Pillar | EP count S1 (EP1-30) | EP count S2 (EP31-60) | EP count S3 (EP61-90) |
|---|---|---|---|
| family_regret | 7 | 7 | 6 |
| love_regret | 5 | 5 | 5 |
| promise_regret | 6 | 6 | 6 |
| kindness_regret | 5 | 6 | 6 |
| self_regret | 7 | 6 | 7 |

**Distribution example EP11-20 (interleave):**
EP11 family / EP12 love / EP13 promise / EP14 kindness / EP15 self / EP16 family / EP17 promise / EP18 love / EP19 kindness / EP20 self

### AR2 — ESCALATION CURVE

**Rule:** Intensity tuân `bible/09 emotion_intensity` per-phase.

| Phase | EPs | Level | Style |
|---|---|---|---|
| Introductory | EP1-10 | 0.45 | Đơn giản, sensory ≤4 dòng |
| Warming | EP11-30 | 0.55 | Flashback ngắn, sensory 4-5 dòng |
| Heightening | EP31-60 | 0.70 | Multi-layer regret, sensory 5-6 dòng, double bell allowed |
| Peak | EP61-80 | 0.85 | Cross-EP echo, ghost manifest có thể 2 lần |
| Climax | EP81-90 | 0.95 | Series reveal — Quang là ai, driver là ai |

### AR3 — QUANG MEMORY UNLOCK PROGRESSIVE

**Rule:** Mỗi 5 EPs Quang unlock 1 mảnh memory. 18 mảnh cho 90 EPs.

| EP range | Memory fragment unlocked |
|---|---|
| EP1-5 | M1: Quang biết mình ngồi xe — không biết tại sao |
| EP6-10 | M2: Quang nhớ năm sinh (1996) |
| EP11-15 | M3: Quang nhớ có yêu một người tên Hà |
| EP16-20 | M4: Quang nhớ Hà mất |
| EP21-25 | M5: Quang nhớ mình từng học Hà Nội |
| EP26-30 | M6: Quang nhớ tên ngành học (kiến trúc) |
| EP31-35 | M7: Quang nhớ ngày Hà mất (12 tháng 4) |
| EP36-40 | M8: Quang nhớ có ai bên Hà lúc Hà chết |
| EP41-45 | M9: Quang nhớ Hà nhắn gì cho Quang đêm cuối |
| EP46-50 | M10: Quang nhớ mình hứa với Hà điều gì |
| EP51-55 | M11: Quang nhớ mình đã không giữ lời |
| EP56-60 | M12: Quang nhớ Hà đợi Quang ở đâu |
| EP61-65 | M13: Quang nhớ Quang chính là người chở Hà ngày Hà mất |
| EP66-70 | M14: Quang nhớ tai nạn xe đêm đó |
| EP71-75 | M15: Quang nhớ Quang chết theo Hà |
| EP76-80 | M16: Quang nhận ra mình là hành khách (không phải nhân chứng) |
| EP81-85 | M17: Quang nhận ra bác tài là ai (deferred per bible/18) |
| EP86-90 | M18: Quang nhớ ra "Chưa tới lúc" nghĩa là gì |

### AR4 — CROSS-EP CALLBACK REQUIRED

**Rule:** Mỗi 10 EPs PHẢI có ≥1 callback đến passenger / object EP trước.

**Examples for EP11-50:**
- EP15: bác tài nhắc "đêm trước có cô kế toán cũng cầm hộp đỏ" (callback EP11)
- EP20 (milestone): radio cũ phát bài cô y tá EP08 từng nghe
- EP25: passenger ghế thứ chín nhận ra mình ngồi đúng ghế của ai đó "đêm 14"
- EP30 (milestone): xe đi qua bến cô EP07 đã xuống
- EP35: Quang nhặt món vật giống y hệt một vật EP25 (echo, không trùng)
- EP40 (milestone): passenger nói với Quang "tôi biết anh — anh đêm 30 từng nhìn tôi"
- EP45: xe dừng ở 2 stop (EP20 + EP45)
- EP50 (milestone): season 1 finale — Quang nhìn xuyên qua 50 ghế trống thấy 50 vật mình đã nhặt

### AR5 — MILESTONE EP RULE

**Rule:** EP10/20/30/40/50/60/70/80/90 là turn points — phải KHÁC EP thường.

| Milestone | Khác biệt |
|---|---|
| EP10 | First major Quang memory crisis — Quang lần đầu khóc trên xe |
| EP20 | Bác tài nói câu phụ "Đêm hai mươi — con đã đi nửa đoạn đầu rồi" |
| EP30 | Quang gặp passenger biết tên mình (vô tình gọi đúng "Quang" — anchor) |
| EP40 | Half-series mark — Quang counts 40 items + 40 nights, dawn không tới |
| EP50 | S1 FINALE — Quang nhận ra mình đã đi qua 50 đêm không sáng |
| EP60 | S2 FINALE — Quang lần đầu thấy bóng mình trong gương — không phải mình |
| EP70 | Bác tài hé lộ "Con tên Quang" (lần đầu xác nhận tên) |
| EP80 | Quang nhìn thấy Hà trên xe — passenger ghế ba (Quang ngồi ghế 3!) |
| EP90 | Series finale — Quang xuống xe ở stop của Hà |

### AR6 — OBJECT COLLECTION DRIVES ARC

**Rule:** Mỗi EP Quang nhặt 1 vật + 1 vật từ EP trước có ý nghĩa mới.

- EP11: nhặt khăn tay (vật 11)
- EP20 milestone: tổng kiểm 20 vật, nhận ra 3 vật có cùng symbol (hoa cúc khô)
- EP30: nhặt vật giống vật EP14 — flashback EP14
- EP40 milestone: 40 vật, Quang xếp theo năm — thấy bắt đầu năm 2017
- EP50 milestone: 50 vật xếp lại thành "bản đồ" địa lý 50 stops

---

## 3. EP11-50 RESHUFFLE — passenger order

**Hiện tại EP11-41 ship linear theo pillar.** Em đề xuất shuffle lại theo AR1 interleave + AR4 cross-EP echo:

### Đề xuất EP11-50 (40 EPs):

| EP | Pillar | Passenger spec (re-shuffle) | Quang memory | Cross-EP callback |
|---|---|---|---|---|
| 11 | family | PAS_0023 Lan Hương 22 mẹ kho cua | M3 nhớ Hà | — |
| 12 | love | PAS_0048 Hân Hậu 45 đồng hồ xà cừ | M3 deepens | callback EP01 đồng hồ |
| 13 | promise | (chưa specced — pillar promise EP đầu) | M3 setup | — |
| 14 | kindness | (chưa specced — pillar kindness EP đầu) | M3 setup | — |
| 15 | self | (chưa specced — pillar self EP đầu) | M3 setup | callback EP11 mẹ |
| 16 | family | PAS_0024 Thành Đạt 31 ông Hán Nôm | M4 Hà mất | — |
| 17 | promise | (specced) | M4 deepens | — |
| 18 | love | PAS_0049 Tấn Phát 59 áo gió xanh | M4 deepens | — |
| 19 | kindness | (specced) | M4 deepens | callback EP14 |
| 20 | self | (specced) | **MILESTONE — Quang khóc** | callback EP08 cô y tá |
| ... | ... | ... | ... | ... |

(full table tới EP50 ship đầy đủ trong bible/21_series_arc_design.yaml)

---

## 4. HIẾN PHÁP AMEND — 6 RULES R33-R38

Em đề xuất thêm vào `bible/00_constitution.yaml`:

```yaml
SERIES_ARC_RULES:  # round 4 add — 2026-06-27 (chống "lộn xộn no arc")
  R33_pillar_interleave:
    max_consecutive_same_pillar: 2
    enforcement: Generator pre-write reject + QA PHASE 12.16 check

  R34_escalation_curve_enforcement:
    rule: "level tuân bible/09 per-phase"
    enforcement: QA PHASE 12.8 check intensity vs phase target

  R35_quang_memory_unlock_progressive:
    rule: "Mỗi 5 EPs unlock 1 fragment per bible/21"
    enforcement: Generator load bible/21 + QA cross-check

  R36_cross_ep_callback_required:
    rule: "Mỗi 10 EPs ≥1 callback đến EP trước"
    enforcement: QA PHASE 12.17 callback check

  R37_milestone_ep_rule:
    list: [10, 20, 30, 40, 50, 60, 70, 80, 90]
    rule: "Milestone EP phải KHÁC EP thường — escalation peak + reveal"
    enforcement: Generator load milestone profile + QA distinguish check

  R38_object_collection_arc:
    rule: "Item collection drives arc — mỗi 10 EPs phải có sub-arc objects (symbol clustering / geographic / temporal)"
    enforcement: Generator + QA cross-EP echo check
```

---

## 5. EP11-41 REWORK PLAN

**Em đề xuất:**

| # | Action | Time |
|---|---|---|
| A | Pause EP11-41 hiện tại → archive "draft v1" | 5 min |
| B | Generate EP11-50 spec table theo AR1-AR6 | 10 min |
| C | Rewrite EP11-50 theo spec — 1 EP / turn — 40 turns | ~40 turns |
| D | Verify VNQA + cross-EP arc consistency | 5 min |
| E | Ship + commit "round_15_arc_redesign" | 5 min |

**Realistic:** ~10 session turns nếu ship 4 EPs/turn.

---

## 6. CÂU HỎI MR.LONG TRƯỚC EM BẮT ĐẦU

1. **Approve 6 ARC rules R33-R38** ở section 4?
2. **Approve memory unlock progression M1-M18** ở section AR3?
3. **Approve milestone EP plan** ở section AR5?
4. **Quang real identity (M13-M16)** — Mr.Long muốn em là biên kịch hay Mr.Long đã chốt?
5. **EP11-41 hiện tại** — archive draft v1 hay delete?

Mr.Long trả lời từng câu 1-5 hoặc "OK tất cả" để em start.
