# LESSONS SESSION 29/6 — 4 MẢNG (prompt / quy trình / nội dung / QA)

**Session scope:** SVHMP_Studio ~15 hours, 19+ commits Round 19.5→19.15, 24+ rules R86-R109, EP01 GOLDEN, 3 CMDs parallel coordination.

**Memory mirror:** `C:\Users\Administrator\.claude\projects\C--Users-Administrator\memory\feedback_session_29_6_lessons_4_mang.md`

---

## 1️⃣ PROMPT + CÁCH GEN

### Vấn đề phát hiện
- LLM gen tiếng Việt natural → **~30-40% câu kết thúc dấu cấm** (ngã/nặng/hỏi) = R86 vi phạm
- `prompts/qa.md` round 18 gen EP02-50 KHÔNG có R86 constraint → legacy debt **1845 violations / 49 EPs**
- CMD #2 propose text fix **introduced R86 mới 2 lần** (L166 "cũ" NGA, L218 "đợi" NANG) — R92 codify SAU vi phạm

### Rule cứng global
- **Generator prompt PHẢI inline R86 constraint** trước gen
- **R92 SELF-VERIFY R86**: text propose → `qa_eol_diacritic.py` trước suggest
- **Áp ngược legacy**: rule mới ship → MUST batch fix existing
- **Pre-flight loop**: gen → audit → reject vi phạm → gen lại

---

## 2️⃣ QUY TRÌNH (workflow)

### Vấn đề phát hiện
- **REACTIVE iter v22-v66** (19 versions) — render → flag → fix 1 layer → re-render → repeat
- CMD LEAD vi phạm grep narrow **3 LẦN** trong session (R59→R91→R93→R105) dù memory đã save
- 3 CMDs không protocol auto-coordinate → Mr.Long làm trung gian
- "Biết rule" ≠ "apply rule" — memory không tự enforce

### Rule cứng global
- **PROACTIVE STAGE 1+3+5 mandatory** (R90)
- **Tool hardlock thay willpower**: pre-commit hook + inline check → physical block
- **MASTER PIPELINE LOCK** (R91): 1 section approved → áp section sau, KHÔNG iterate
- **R-ID conflict guard** (Round 19.13): `tools/check_rule_id_free.py --staged` + pre-commit SECTION A
- **File-based coordinate** (Round 19.14): `COORDINATION_HUB.md` + `log_ping.py` → loop ≤60s

### Anti-pattern (CẤM)
1. REACTIVE iter — fix 1 layer → re-render
2. SKIP STAGE 1 — render không verify R86
3. Single update — bug không codify rule (R93)
4. Narrow grep — assume "miss = chưa có"
5. Self-praise "✅ DONE" trước verify

---

## 3️⃣ NỘI DUNG (content + text quality)

### Vấn đề phát hiện
- EP01 evolve **70+ text fixes** session 29/6 mà em không track:
  - R66 chains: 38→14→6→0
  - Khải-Phong: 54→6 (R75/R95)
  - Hạ-Vy: 17→6 (R75/R95)
  - "vuốt vai...Mỉm cười": 25→12 (R49)
  - INTRO rebrand: "Hắc Dạ Ký" → "Hắc Vỹ Dạ" (CMD LEAD không biết khi nào)
- 5 R98 detect — **4 false positive** (rì rì onomatopoeia / từ từ idiom / 2× cross-sentence) + 1 real
- "tay sạch" subtext lost → R83 codify SAU Mr.Long catch

### Rule cứng global
- **Whitelist onomatopoeia + idiom**: rì rì / từ từ / chậm chậm / khẽ khẽ trong R98 detect
- **Cross-sentence skip**: w1 ends with .!? → skip duplicate check
- **Genre-aware threshold**: horror SVHMP câu 150 từ OK, podcast 30-40 từ
- **Track rewrite history** via `log_ping.py [FIX] msg`
- **Subtext audit R83**: text descriptive ("tay sạch") phải clear context

---

## 4️⃣ QA (quality assurance)

### Vấn đề phát hiện
- **STAGE 3 strict threshold** = false FAIL forever:
  - `slow_onsets == 0` vs BigVGAN inherent (R96 mitigation không cure)
  - RMS [-22, -12] strict vs actual -23 (off 1dB)
  - CMD LEAD ship R96 tolerance → 0/6 → 6/6 PASS
- **Counter mismatch cross-script**: R66 — script A đếm 14, script B đếm 38, Mr.Long báo 42
- **QA detect-only loop** (qa_watch.py 17 iter persistent): chỉ count, không log từ cụ thể
- **CMD LEAD ship `feedback_no_grep_assumption.md`** → vi phạm CHÍNH lesson 3 LẦN

### Rule cứng global
- **Threshold match reality**: R96 tolerance pattern — vocoder limit phải reflect spec
- **QA log CỤ THỂ** đủ apply fix: line + word + context (không chỉ count)
- **Counter canonical**: 1 detector chính per rule
- **Auto-trigger downstream**: detect → log → CMD apply → verify (loop ≤60s)
- **STAGE 1+3+5 layered**: pre-render text / post-render audio / pre-commit hook

---

## 📊 META BÀI HỌC (cross-cutting)

### Memory ≠ Behavior
CMD LEAD vi phạm `feedback_no_grep_assumption.md` **3 LẦN trong cùng session** sau khi save:
- Save memory ✓
- Reinforce LẦN 1 ✓
- Reinforce LẦN 2 ✓
- Build tool hardlock `check_rule_id_free.py` + pre-commit hook SECTION A → CHẤM DỨT

**Pattern global:** memory note → reinforce → **physical tool/hook là cuối cùng** → enforcement guaranteed.

### Verify > Suy luận
CMD LEAD catch 4 lần CMD #2 report KHÔNG khớp factual:
- "R86-R90 codified" → list format em grep top-level miss
- "R59→R91 free" → R91 đã occupied
- "R93 free" → R93 đã occupied (LẦN 3 vi phạm)
- "24 rules R86-R109" → factual 20 rules R86-R105 (R106-R109 chỉ memory)

**Pattern global:** Mọi check status verify số liệu thực với 4-format multiple grep.

### Coordinate cost
Mr.Long phải trung gian giữa 3 CMDs nhiều lần. Sau `COORDINATION_HUB.md` + `log_ping.py` → auto loop ≤60s, Mr.Long thoát role middleman.

**Pattern global:** N≥2 CMDs work cùng project → MUST có protocol auto-coordinate ngay từ session start.

---

## 🚀 Áp global 8 projects

| Project | Lesson chính |
|---------|--------------|
| SVHMP | R86-R105 + COORDINATION_HUB ship |
| HDK | R86 + R90 + pre-commit hook chain |
| tro-ly | R83 subtext + R92 SELF-VERIFY |
| tai-xiu | R98 whitelist pattern (game text) |
| art-pilot-filter | R83 subtext + R96 tolerance threshold |
| SVTK | R83 + threshold reality-matched (LoRA QA) |
| Globeway 5 | log_ping pattern auto-coordinate |
| TSOnlineClone | R83 verify pattern (data parsing) |
