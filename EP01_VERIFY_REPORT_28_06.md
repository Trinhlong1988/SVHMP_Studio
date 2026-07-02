# EP01 VERIFY REPORT — 2026-06-28 22:50
**Audit cho CMD khác handle TTS re-render lần tới.**

Source: `D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\output\ep_01\episode.md`
Current bản TTS render: `narration.wav` 18:38 (Mr.Long reject — nhiều bug)
Pipeline: `tools/svhmp_v13_render.py` LOCKED v1.3 + WPM 142 (atempo 0.916) + emo_alpha 0.65

---

## 🚨 SECTION 1: BUG PHONETIC TTS (Mr.Long listen catch)

### 1.1 "Khải Phong" → TTS đọc thành "Hải Phòng" (city)
- **Fix applied:** hyphen "Khải-Phong" (63 → 6 mentions remaining sau R75 cap)
- **R74** codified (rename from em em codify R68): `bible/00 R74_hyphen_proper_noun_phonetic_clash_hardlock`
- **Verify next render:** TTS đọc "Khải-Phong" có phát âm 2 syllables distinct hay vẫn elide thành "Hải Phòng"?

### 1.2 "Hạ Vy" → TTS đọc thành "Hà Vy"
- **Fix applied:** hyphen "Hạ-Vy" (22 → 11 mentions, OVER cap 6 — còn 10 dialogue lines)
- **R74** cùng rule
- **Verify next render:** TTS đọc "Hạ-Vy" đúng chưa?

### 1.3 "ở cầu Long Biên" → TTS đọc "ỡ cầu" (dấu hỏi → dấu ngã)
- **Status:** CHƯA fix
- **Occurrences:** 8 lần "ở" trong content body (L242 "ở đâu", L340 "ở cổng B", L354 "ở quán cà phê", L414 "ở phòng bên", L490 "ở cuối", L668 "ở bảy giờ mười")
- **Đề xuất rule R76:** Single-syllable "ở" + danh từ open vowel → TTS BigVGAN tone drift (hỏi → ngã)
- **Fix options:**
  - (a) Thay "ở" với "tại" / "nơi" (vd "ở cầu" → "tại cầu Long Biên")
  - (b) Pad "ở" + bridge ("ngay ở cầu Long Biên")
  - (c) Codify R76 + auto-fix script

### 1.4 "Tập 1" → TTS đọc "Tập one" (English digit)
- **Fix applied:** L23 → "Tập một" ✅
- **R69 round 19** number reading Việt chữ — already codified
- **Còn 40 digits trong content** — kiểm tra bracket marker [pause:Xms] (acceptable) + body content digits

### 1.5 "người ơi" → TTS đọc "nhười ơi" (phonetic mishear)
- **Location:** L246 (REVEAL flashback radio old song "...người ơi...")
- **Why:** BigVGAN nasal cluster "ng" + open vowel "ơ" → soft "nh-" articulation
- **Fix proposal:** Spell out "ng-ười" hoặc replace với "...em ơi..." nếu acceptable narrative
- **Status:** CHƯA fix

### 1.6 Bracket SFX marker → TTS đọc bracket noise
- **Example caught:** `[chuông ngân một nhịp, 1.0s vang nhẹ]` → "one pine os vang nhẹ"
- **Fix applied:** `tools/build_spec_ep01.py` strip ALL `[...]` markers (except [pause:Xms] [DIALOGUE_SEG_*])
- **22 brackets total** in episode.md — 16 [pause:Xms] OK, 6 stage/SFX strip needed

---

## 🚨 SECTION 2: ANAPHORA / REPETITION

### 2.1 Khải-Phong cap 6 ✅ (R75)
- Apply: `C:/tmp/cap_proper_noun_6.py` reduce 54 → 6
- Spacing: chưa verify even distribution (R75 spacing_rule mới codify)

### 2.2 Hạ-Vy CÒN OVER cap 6 — hiện 11
- 1 narrator + 10 dialogue (Khải-Phong recall mối tình)
- **Đề xuất:** Giữ 4 emotional anchor + replace 6 dialogue → "cô ấy"
- Keep candidates: "Tên cô ấy là Hạ-Vy" (intro), "Đó là lần cuối tôi gặp Hạ-Vy" (closure), 2 mạnh khác

### 2.3 Verb lặp khô khan
- L164/166: "Không bao giờ cầm. Chỉ tối nay anh mới cầm." → "cầm" lặp
- **Fix proposal:** "Không bao giờ chạm vào. Chỉ tối nay anh mới mang theo." (vary verb)

### 2.4 "đều/đều" lặp 2 câu liên tiếp
- **Fix applied:** L170-172 gộp 1 câu "Tiếng mưa rơi nhịp nhàng bên ngoài, hòa cùng tiếng máy xe rì rì trầm thấp." ✅

### 2.5 "Người ông cụ" sai ngữ pháp
- **Fix applied:** L182 → "Ông cụ không bật radio, chỉ ngồi ôm nó vào lòng." ✅

### 2.6 "Cô gái" lặp consecutive
- **Fix applied prior:** L185/L187 → "Cô không hỏi..." / "Cô chỉ lặng nhìn..."
- L575/L577 → "Cô nhặt vật ấy lên." ✅

### 2.7 "anh không định kể. Nhưng anh kể." — "anh" lặp + "kể" lặp
- **Location:** L218-220 INCIDENT section
- **Current:** "Khải-Phong thở ra một hơi dài. / Anh không định kể. / [pause:500ms] Nhưng anh kể."
- **Fix proposal:** "Khải-Phong thở ra một hơi dài. Định im lặng, nhưng cuối cùng anh vẫn lên tiếng." (gộp + vary verb)

### 2.10 "vật" lặp liên tiếp (L575-578)
- **Fix applied:** L575-578 "Có một vật nhỏ." / "nhặt vật ấy lên" → "Có một chiếc đồng hồ nhỏ." / "nhặt nó lên" ✅

### 2.12 "đã ngồi đã lâu rồi" — repeat "đã" + awkward grammar
- **Fix applied:** L90 "Họ ngồi yên. Như đã ngồi đã lâu rồi." → "Họ ngồi yên, như đã ở đó từ rất lâu." ✅
- Bonus: gộp 2 câu ngắn (R66) + remove "đã" double + smoother prosody

### 2.11 "Tay sạch" awkward standalone + repeated
- **Fix applied:**
  - L190 "Tay cô đặt trên đùi. Tay sạch." → "Tay cô đặt trên đùi, trắng tinh, không một vết máu." ✅
  - L562 "đặt tay sạch lên đùi" → "đặt đôi bàn tay trắng lên đùi" ✅
- **Reason:** Clarify intent (cô y tá KHÔNG vết máu = subtle horror cue) + remove awkward standalone

### 2.9 "Cô y tá" lặp 3 lần liên tiếp (R69/R75 + R66 short chain)
- **Fix applied:** L308-312 gộp 3 câu → "Trên ghế chín, cô y tá ngước lên, nhìn về phía anh rồi khẽ lắc đầu một cái." ✅
- Còn 3 chỗ "Cô y tá" khác (L502, L530, L566) — non-consecutive, accept

### 2.8 "đặc" lặp gần (Khải-Phong nhìn ra ngoài + sương đặc)
- **Location:** L204-208 INCIDENT (đoạn dialogue về "bạn của chú")
- **Current:** "Khải-Phong nhìn ra ngoài. Mặt kính đọng giọt mưa nhỏ. / Sương đặc thêm sau lớp kính mờ."
- **Issue:** "đặc" có thể không lặp word — nhưng Mr.Long flag "2 từ đặc gần nhau" — em verify lại context
- **Fix proposal:** "Sương dày thêm sau lớp kính mờ." (đặc → dày)

---

## 🚨 SECTION 3: R66 SHORT SENTENCE CHAIN — 38 HIGH violations

Audit: `tools/audit_short_chain.py` (new round 19+)
Spec: max 2 consecutive câu 4-6 từ

**Examples (top 3):**
- L51-L53: "Đèn trần xe vàng." (4w) / "Sáng vừa đủ thấy mặt người." (6w) / "Mười một vị khách khác." (5w)
- L73-L77: "Khải-Phong nhìn ra cửa kính." / "Sương ngoài cửa kính dày dần." / "Hà Nội đêm tháng tư."
- L75-L79: tiếp tục chain "Hà Nội đêm Khải-Phong vẫn nhớ."

**Fix strategy (R66 spec example):**
- Bad: "Anh đến đó. Anh ngồi xuống. Anh đứng dậy."
- Good: "Khải Phong đến đó. Người đàn ông ngồi xuống một lúc, rồi từ từ đứng dậy bước ra ngoài."
- → Merge 2-3 câu ngắn thành 1 câu dài bằng connector ("và", "rồi", "khi", "trong khi")

**Risk:** Rewrite 38 chỗ có thể lạc văn phong Ngọc Ngạn (intentional short fragments). Cần manual editorial pass.

---

## 🚨 SECTION 4: SEMANTIC VAGUE / GRAMMAR

### 4.1 "Có lẽ vì cái khác" — semantically vague
- **Fix applied:** L136-138 → "Có lẽ pin đã hết, hoặc vì một lý do nào khác." ✅

### 4.2 "đồng phục y tá xưa" — Mr.Long thắc mắc "xưa"
- Status: CHƯA fix
- L188: "Trên ghế chín, một cô gái mặc đồng phục y tá xưa."
- **Đề xuất:** "đồng phục y tá thời cũ" hoặc "đồng phục y tá lỗi thời" hoặc "đồng phục y tá kiểu cũ"

### 4.3 R67 verb semantic precision (nhớ vs nhận ra vs hiểu)
- **Fix applied prior:** L94/L170/L570/L632 (4 chỗ)

### 4.5 "Hạ-Vy" hyphen TTS render → pause QUÁ XA giữa "Hạ" và "Vy"
- **Mr.Long flag:** "anh tự nhủ Hạ.... Vy đang bay" / "sao xa nhau thế"
- **Audio symptom:** BigVGAN treat hyphen as long pause boundary (~400ms+) giữa syllables
- **Trade-off:** Hyphen fix phonetic clash (Hạ Vy → Hà Vy) BUT introduce unnatural break artifact
- **Fix proposal options:**
  - (a) Try CamelCase "HạVy" (no separator) — may keep elision
  - (b) Try comma "Hạ, Vy" — comma pause shorter ~150ms but mid-sentence
  - (c) Try ZWNJ U+200C (zero-width non-joiner) — no audible pause but TTS may not handle
  - (d) Phonetic respelling "Hạ Vi" (Vi instead of Vy) — different name but may render cleaner
  - (e) Revert hyphen + accept phonetic clash (some Hạ Vy → Hà Vy occasionally)
- **Same issue likely for "Khải-Phong"** — verify TTS render quality
- **Status:** CHƯA fix — Mr.Long quyết option

### 4.6 "tại nơi" → "tại chỗ" (chuẩn collocation)
- **Fix applied:** L380 "— cô ấy mất tại nơi." → "— cô ấy mất tại chỗ." ✅
- "Tại nơi" KHÔNG phải tiếng Việt chuẩn — "tại chỗ" mới đúng collocation (on the spot)
- L62 metadata codeblock — không render TTS, skip

### 4.4 "Cô ấy đã đi từ lâu rồi" — Mr.Long thắc mắc nghĩa
- **Location:** L210 INCIDENT (Khải-Phong answer cô gái ghế tám)
- **Possible interpretation issue:** "đi rồi" = chết / sang nước ngoài / không còn liên hệ → ambiguous
- **Fix proposal:** Clarify hơn — "Cô ấy mất rồi" (death explicit) hay "Cô ấy không còn nữa" (subtle)
- **Note:** "đi" trong văn nói VN có thể = "mất" (passed away) — Ngọc Ngạn style hợp acceptable, nhưng Mr.Long flag → có thể audio TTS đọc "đi rồi" sounds weird

---

## 🚨 SECTION 5: PRONOUN CONVENTION (R75 v1.1)

**Codified rule** (bible/00 R75 pronoun_convention):

| Character | Pronoun | Context |
|---|---|---|
| Khải-Phong (full, max 6) | section start / emotional peak / scene intro |
| anh | default narrator action/feeling (close POV per R47) |
| anh ấy | RARE — outsider POV |
| Hạ-Vy (full, max 6) | intro / emotional peak / vision present |
| cô ấy | default recall (distant past) |
| cô | only Hạ-Vy physically present in flashback |

**EP01 verify needed:** scan từng "anh"/"cô"/"cô ấy"/"cô gái" placement có match context không.

---

## 🚨 SECTION 6: AUDIT RESULTS SUMMARY

```
post_render_gate.py:            11/11 PASS ✅
audit_tilde_eol.py R58:         0 HIGH ✅
audit_short_eol.py R60:         0 HIGH ✅
audit_short_start.py R61:       0 HIGH ✅
audit_anaphora_consecutive R62: 0 HIGH ✅
audit_pronoun_pov.py R47:       0 violations ✅
audit_dialogue_hierarchy R48:   0 HIGH ✅
audit_60_dimensions:            HIGH=0, MED=10, OK=50/60 🟡
audit_short_chain.py R66:       38 HIGH ❌ ← critical
audit_r68_to_r73.py:            R68=63 (Khải triphthong false positive after hyphen)
                                R72=21 (dialogue separate render — applied spec.json 5 chunks)
audit_audio_mix_qa.py R59:      FAIL 10/15 (TTS-only, music layer chưa mix — false positive C9)
```

---

## 🚨 SECTION 7: PIPELINE NEXT STEPS cho CMD khác

### Pre-render fixes (text):
1. ❌ Hạ-Vy: reduce 11 → 6 (chọn 6 emotional anchor, rest → "cô ấy")
2. ❌ "ở cầu" → codify R76 + auto-fix text (8 occurrences)
3. ❌ "đồng phục y tá xưa" → reword (xưa → cũ / kiểu cũ)
4. ❌ "Không bao giờ cầm / cầm" → vary verb (cầm → chạm vào / mang theo)
5. ❌ R66 38 chuỗi câu ngắn → manual rewrite merge
6. ❌ "Anh không định kể. Nhưng anh kể." → gộp + vary verb
7. ❌ "Sương đặc" → "Sương dày" (avoid "đặc" repeat near other context)
8. ❌ "...người ơi..." → "...em ơi..." hoặc spell "ng-ười" (TTS phonetic mishear)
9. ❌ "Cô ấy đã đi từ lâu rồi" → "Cô ấy mất rồi" hoặc keep + verify TTS render

### Render setup:
- Pipeline: `tools/svhmp_v13_render.py` LOCKED v1.3 (UV venv `C:\Users\Administrator\index-tts\`)
- Source: `output/ep_01/episode_tts_ready.md` (regen sau text fix)
- Build spec: `C:/tmp/build_spec_ep01.py` (đã fix strip [...] brackets)
- ENV: `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`
- WPM 142: `atempo=0.916` trong ffmpeg master (đã hard-code trong svhmp_v13_render.py round 19)
- emo_alpha=0.65 (LOCKED v1.3)
- Output: `output/ep_01/narration.wav` (overwrite — backup current `narration.wav.bak_R39_18m38_28_06`)

### Known render risks:
- Per-sentence 350+ chunks = 60-90 min render
- GPU memory accumulates → kill + restart if >5min stuck
- Chunk 105-style cuDNN recompile spike on specific shapes (em-dash + question short)

### Post-render QA:
- Verify duration ~17-18 min
- Run all audits trong SECTION 6
- Mr.Long listen + accept hoặc iterate fix

---

## 🚨 SECTION 8: HIẾN PHÁP UPDATES round 19+ (em codified)

| Rule | File | Purpose |
|---|---|---|
| R74 | bible/00 | hyphen proper noun phonetic clash (Khải-Phong, Hạ-Vy) |
| R75 v1.1 | bible/00 | max 6 per EP + spacing + pronoun convention |
| R76 (PROPOSED) | bible/00 | "ở" short hỏi + open vowel TTS bug — chưa codify |
| R_AUDIO_01-10 | bible/05 v1.1 | audio mix rules (em codified round 17) |
| R59 audio_mix_qa | bible/00 | mandatory QA gate (round 17 em codified) |
| R67 | bible/00 | verb semantic precision (round 18) |

---

## 🚨 SECTION 9: BACKUP FILES (rollback nếu cần)

```
output/ep_01/episode.md.bak_R58            (round 18 R58 fix)
output/ep_01/episode.md.bak_R60            (round 18 R60 fix)
output/ep_01/episode.md.bak_R61_manual     (round 18 R61 fix)
output/ep_01/episode.md.bak_R61_final      (round 18 R61 final)
output/ep_01/episode.md.bak_pre_anaphora_28_06_2230  (em em apply per-paragraph fix)
output/ep_01/episode.md.bak_aggressive_28_06_2235    (em aggressive cap fix)
output/ep_01/episode.md.bak_cap6_28_06               (em cap 6 fix)
output/ep_01/narration.wav.bak_v3_WRONG_28_06_12h   (bản v3 13:31 wrong intro)
output/ep_01/narration.wav (current R39 18:38, Mr.Long reject)
output/ep_01/EP01_R38_FULL.wav  (bản LOCKED 27.6 18:12, no text fix)
```

---

**End of report. CMD khác please handle SECTION 7 next steps.**
