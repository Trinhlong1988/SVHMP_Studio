# SVHMP — EP SCAFFOLD TEMPLATE (BẮT BUỘC sử dụng trước khi viết EP)

**Lock date:** 2026-06-27 (round 5 — Mr.Long lệnh "định hướng dựng chuẩn trước tránh làm đi làm lại")
**Status:** HARD MANDATORY — mọi EP mới PHẢI bắt đầu từ scaffold này
**Cross-ref:** bible/00 v1.2 enforcement_level: HARD_UNIVERSAL

---

## PRE-WRITE CHECKLIST (PHẢI VERIFY TRƯỚC KHI VIẾT 1 CHỮ)

```yaml
# Run: python tools/pre_render_checklist.py --ep N
# Output: ep_N_scaffold.yaml (filled từ bible lookups)

ep_number: N
phase: introductory | warming | heightening | peak | climax  # bible/09
pillar: family | love | promise | kindness | self  # bible/21 R33 interleave
intensity_level: 0.45 | 0.55 | 0.70 | 0.85 | 0.95  # bible/09 + milestone bump
quang_memory_fragment: M_X  # bible/21 R35 (1-18)
quang_memory_text: "Khải Phong nhớ ..."  # bible/21 progression_table[M_X]
callback_target: ep_N | none  # bible/21 R36 callback_schedule_s1
object_sub_arc:
  type: symbol_clustering | temporal_arc | geographic_arc | none
  target_symbol: "..."  # bible/21 object_sub_arc_s1
milestone: true | false  # bible/21 R37 if N in [10,20,30,40,50,60,70,80,90]
milestone_special: "..."  # if milestone, copy from bible/21
passenger_main: "..."  # pick từ runtime/passenger_roster_100.yaml
signature_object: OBJ_XXX  # bible/12_object_library
signature_setting: setting_XXX  # bible/13_setting_library
stop_location: ngã ba XXX  # specific city
word_count_target: 2300  # R39 target_range [2200, 2500]
bell_count: 1  # R SERIES_RULES.bell HARD MAX
ghost_manifest: 1  # R SERIES_RULES.ghost_visual HARD MAX
driver_lines: 2  # "Con đã nhớ ra chưa?" + "Chưa tới lúc." UNLESS milestone or [73,90]
```

---

## SECTION BUDGET (R39 — HARD)

```
INTRO Hắc Dạ Ký        →  ~50 words   (fixed template, R40)
HOOK (section 1)        → ~280 words  (bus arrives, passenger boards)
SETUP (section 2)       → ~240 words  (Khải Phong observes passenger)
INCIDENT (section 3)    → ~240 words  (ghost glimpse + clock 10 ticks)
REVEAL (section 4)      → ~1050 words (passenger story — year breakdown)
PAYOFF (section 5)      → ~270 words  (passenger disembarks, ritual, ghost manifest)
CLIFFHANGER (section 6) → ~320 words  (Khải Phong internal + bác tài line + memory unlock)
────────────────────────────────────
TOTAL TARGET           → ~2300 words / 15-17 minutes
HARD FLOOR             → 2000 words / 13 minutes (R39 hard_floor)
HARD CEILING           → 2700 words / 18.5 minutes (R39 hard_ceiling)
```

---

## EP SCAFFOLD (sao chép → fill từng [BRACKET])

```markdown
# TẬP [N] — [TITLE Vietnamese vivid]

[INTRO 4.5s — HẮC DẠ KÝ master]

[pause:800ms]

Hắc Dạ Ký — chuyện kể từ cõi vô hình.

[pause:600ms]

Tác giả: Hắc Dạ Ký.

[pause:600ms]

Series: Chuyến xe cuối cùng về đâu.

[pause:600ms]

Ai cũng có một chuyến xe chưa nói lời tạm biệt.

[pause:1000ms]

Tập [N] — câu chuyện đêm nay.

[pause:1500ms]

---

\`\`\`
prompt_version: SVHMP-10.0-RC3.6
ep_number: [N]
phase: [phase from checklist]
pillar: [pillar]
intensity_level: [level]
quang_memory_fragment: [M_X — text]
object_sub_arc: [type — vật N trong cluster]
callback_target: [ep_N | none]
passenger_main: [name age stop pillar one-liner]
signature_object: [OBJ_XXX]
signature_setting: setting_dem_thang_tu_HN
stop_location: ngã ba [city]
bell_count: 1
ghost_manifest: 1
word_count: ~2300
hand_crafted: true
arc_design_compliant: bible/21 R33-R40
\`\`\`

---

# HOOK [section 1]

[pause:800ms]

[280 words — establish: đêm tháng tư, mưa, xe đi qua [setting], Khải Phong ghế 3 đêm thứ N, X vật trong túi, bác tài lái. Xe chậm lại trước [setting object], passenger đứng đợi, mô tả áo / tay / vật. Bước lên xe, ngồi ghế thứ X, mở vật, [object description]. Xe lăn bánh.]

---

# SETUP [section 2]

[pause:600ms]

[240 words — Passenger ngồi yên, vuốt vật, Khải Phong quan sát từ ghế 3 (mô tả ngoại hình + ấn tượng). Ông cụ vặn radio "quê nhà" tắt. Bác tài liếc gương. Passenger gesture nhỏ.]

[pause:500ms]

---

# INCIDENT [section 3]

[pause:500ms]

[240 words — Xe đi qua xóm cũ, ghost glimpse phía bên đường (mô tả 3-4 dòng), passenger nhìn về phía đó, thốt 1 từ tên người đã mất ("[Name]..."). Đồng hồ kim phút nhích 10 lần. Xe đi qua, ghost khuất.]

[pause:1000ms]

---

# REVEAL [section 4]

[pause:1000ms]

["Em là [Name]. [Age] tuổi. Em ở [city]..."]

[1050 words — Passenger story:
- Background (job, family situation, era)
- The relationship to deceased (origin, depth, years)
- The trigger event (year-by-year breakdown)
- The mistake / regret (specific, not abstract)
- Death (1-2 paragraphs, factual, no gore)
- Years of aftermath (5-15 years carrying object)
- Why tonight (decision to return object)

Bác tài cất lời:
"Con đã nhớ ra chưa?"

Passenger gật:
"[Name nhớ. ...]"

[pause:1200ms]

"Đêm nay — [Name] đem [object] về [stop] — [ritual plan]."
]

---

# PAYOFF [section 5]

[pause:800ms]

[270 words — Xe chậm lại. Ngã ba [city] — cây [tree] — bến không tên. Chuông xe ngân. Một tiếng. Tan.

Passenger gather object. Đứng dậy.
"Chào anh."

Đồng hồ cabin bảy giờ mười phút. Kim không di chuyển.
Bác tài: "Chưa tới lúc."

Passenger bước xuống.

Bên ngoài — Passenger đi vào [destination] — đèn nến. Ritual cụ thể (quỳ / đặt vật / cúi đầu).

Khải Phong chớp mắt — ghost manifest (deceased xuất hiện — mô tả ngắn — vuốt vai/tóc passenger — mỉm cười).

Khải Phong chớp lần nữa. Ghost tan.

Passenger ngẩng đầu. [No tears / có lệ]. Đi ra.]

[pause:1500ms]

---

# CLIFFHANGER [section 6]

[320 words — Xe lăn bánh. Ghế X trống. Trên sàn — vật nhỏ rơi (mảnh từ object).
Khải Phong nhặt. Vật thứ [N].

Bác tài lái. Kim phút cabin nhích 10 lần.

[pause:1500ms]

Khải Phong ngồi. [Internal monologue connecting to Hạ Vy memory:
- Vật mới connection với cụm vật trước
- Memory fragment M_X unlock thêm 1 detail
- Hình ảnh Hạ Vy rõ hơn (vai / áo / cúc cài tai / sân trường kiến trúc / phòng trọ Khâm Thiên / công ty Mộc Hà / tin nhắn / cuộc gọi không bắt / Bạch Mai)]

[pause:1500ms]

Bác tài liếc gương. "Đêm [N]. [Foreshadow đêm sau]."

Khải Phong gật.

Đêm thứ [N]. Xe đi tiếp. Phía sau — [city] khuất. [Passenger còn lại ở đâu làm gì].
```

---

## POST-RENDER GATE (BẮT BUỘC PASS trước commit)

```bash
# Run: python tools/post_render_gate.py --ep N
# Must PASS all:
# 1. VNQA verdict != CRITICAL
# 2. word_count in [2000, 2700]
# 3. duration >= 13 minutes
# 4. bell_count == 1
# 5. ghost_manifest == 1
# 6. driver lines: 2 (unless milestone or [73, 90])
# 7. has intro Hắc Dạ Ký 5 elements (R40)
# 8. Hà → Hạ Vy verified (no naked "Hà" except whitelisted)
# 9. Quang → Khải Phong verified
# 10. memory fragment text matches bible/21 progression_table[M_X]
# 11. pillar matches bible/21 pillar_interleave_ep01_50[ep_N]
# 12. callback target (if any) matches bible/21 callback_schedule_s1[ep_N]

# FAIL → BLOCK commit. Fix + re-verify.
```

---

## NOTES

- Đây là HARD scaffold — KHÔNG được skip section.
- Mỗi section có word budget — KHÔNG được dồn 1 section quá lớn.
- Nếu draft đầu < 2000 từ → EXPAND ngay, KHÔNG ship trước rồi fix sau.
- "Tránh làm đi làm lại" = đọc checklist + fill scaffold → viết 1 lần đạt target.

**Mr.Long 27/6 lệnh: "đọc kỹ trước khi render — phải có định hướng dựng chuẩn trước."**
