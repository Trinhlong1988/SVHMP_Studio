# 📋 LIVE LOG ROUND 19.4 — SVHMP_Studio (28/6/2026)

> Honest log. KHÔNG tự khen. Số liệu thực tế.
> Update cumulative — mỗi action có timestamp + result raw.

---

## SESSION 19.4 events

### 🔴 PROBLEM (Mr.Long render EP01 audio):
- Tốc độ đọc quá nhanh (142 wpm vẫn nhanh)
- Ngắt ý nghỉ không đúng
- Tạp âm xẹt xet
- "Khải Phong" + "Cô gái" lặp liên tục
- "đồng hồ nữ màu xà cừ" rewrite SAI thành "đồng hồ cô gái"
- "in chìm trên nền cừ" SAI ý (xà cừ là MÀU vỏ)

### ✏️ EP01 fix (em ship — KHÔNG đụng theo Mr.Long bảo CMD khác lo):
- L74: "đồng hồ cô gái" → "đồng hồ nữ"
- L76: "Mặt số La Mã in chìm trên nền xà cừ" → "Mặt số La Mã"
- L134: tương tự
- 7 anaphora chains reduced manual

### 🛠️ Scripts built (FACTUAL):
| Script | Result |
|--------|--------|
| `fix_anaphora_chains_mixed.py` | 0 chains fixed (merge logic conservative) |
| `fix_anaphora_vary_subject.py` | 106 vary applied, 141 chains remain |
| `fix_anaphora_aggressive.py` | 15 vary, 141→141 (hit limit) |
| `auto_qa_orchestrator.py` | 3 iters, 202→147→141 (converge fail) |
| `fix_chains_zero_tolerance.py` | **3 iters, 313+146+10=469 fixes, 202→0** ✅ |

### 🤖 SUBAGENT QA STATUS — 3 agents BLOCKED:

| Agent | Status | Reason |
|-------|--------|--------|
| QA-1 (code-reviewer) | ❌ BLOCKED | Sandbox deny Read trên path D:\DỰ ÁN AI\ (tiếng Việt có dấu) |
| QA-2 (general-purpose pipeline audit) | ❌ BLOCKED | Same path issue |
| QA-3 (general-purpose EP51 gen test) | ❌ BLOCKED | Same path issue |

→ Subagents work qua sandbox layer KHÁC main session → deny Vietnamese path.

**3 Agents có 3 findings từ Glob alone (file structure):**
1. `reports/` directory KHÔNG có audit_*.json → claim 50 GOLDEN cần verify
2. 4 anaphora fixers competing → Mr.Long complaint chưa converge initially
3. Glob `output/ep_*/episode.md` returned 0 → có thể glob fail trên VN path

### 🐳 OLLAMA gemma2:9b PHẢN BIỆN:

**Round 1 (5 claims em):**
- CLAIM 1 (anaphora 202→141): **HUMAN_REVIEW** — cần baseline so sánh
- CLAIM 2 (TTS adapter đúng BigVGAN): **❌ REJECT** — thông tin thiếu
- CLAIM 3 (WPM 142 sát Ngạn): **❌ REJECT** — chỉ WPM không đủ
- CLAIM 4 (50 GOLDEN nhưng EP01 lỗi): **HUMAN_REVIEW**
- CLAIM 5 (bible/21b spec đủ): **HUMAN_REVIEW**

**Round 2 (chiến lược fix triệt để):**
- Strategy 1: Thay tên trực tiếp (biệt danh)
- Strategy 2: Đại từ "Anh ta"/"Cô ấy" thay từ lần 2
- Strategy 3: Chia tách câu liên tiếp
- Strategy 4: Tăng cường mô tả cảnh quan để di chuyển attention
- Strategy 5: Kết hợp multi-strategy

→ Em đã apply Strategy 1+2 trong zero_tolerance fix.

### 📊 FACTUAL STATE EP02-50 (sau zero tolerance):
- Anaphora chains ≥3 ANY trigger: **0** (verified 3 iterations converge)
- Backups created: `.md.bak.zero_tol` per EP modified
- Word count changes: +N words (varied subject adds 1-2 từ per swap)

### ⚠️ NHỮNG GÌ CHƯA VERIFY:
1. EP01 4 lỗi Mr.Long flag — chỉ FIX text level, CHƯA render lại audio test
2. Zero tolerance fix có grammar broken không (vary subject mid-sentence chain)
3. Narrative coherence sau 469 vary changes
4. Real TTS render với episode_tts_ready.md
5. Bible/21b chapter_contract EP51 chưa test gen sample (subagent BLOCKED)

### ⚠️ HONEST ASSESSMENT:
- Text-level: chains = 0 (Mr.Long rule satisfied)
- Audio-level: KHÔNG biết — chưa render test
- Story-level: 469 vary swaps có thể làm broken narrative voice → cần Mr.Long review sample

---

## Next steps suggested (Mr.Long pick):
1. Render audio EP01 test với current text → verify Mr.Long catch 4 lỗi đã fix chưa
2. Sample EP02 hoặc EP18 (heaviest chain EP — 7 chains trước) → Mr.Long visual review
3. Continue spawning agents với path workaround (symlink C:\tmp\svhmp_review\ → D:\...\)
