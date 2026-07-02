# Generator VNSL Addon v1.2 LOCKED (R66-R85)

**Status:** ❄️ FROZEN 2026-06-27 round 18. EP02-EP90 generate spec PHẢI tuân thủ.

## R81-R85 thêm round 18 (session 26-27/6 rút kinh nghiệm)

- **R81** SINGLE-CHUNK render lẻ tạo lạc giọng → ưu tiên full section render
- **R82** EMO_VECTOR consistency guard (deviation ≤0.15/axis trong consecutive chunks)
- **R83** PHÙ-CUT mandatory tail residue cuts post-render
- **R84** VERIFY pre-render mandatory (đọc hiến pháp + audit spec trước launch)
- **R85** RENDER WORKFLOW LOCKED — 10 steps strict, KHÔNG skip

## RENDER WORKFLOW LOCKED

```
1. Read CLAUDE.md + VERSION.md + BUGS_FIXED.md + memory feedback_svhmp_* (R1-R85)
2. Read full spec section trước fix
3. Pre-render audit → PASS 0 HIGH issue (text validator + ngram + open-vowel + em-dash + pause + emo)
4. Launch render (full section preferred)
5. Wait completion
6. Apply chunk-level STF + phù_cut (R83)
7. Audio QA strict (R80.1-20) → PASS HIGH=0
8. Splice / replace section
9. Reconcat full EP01 với LOCKED boundary (R66 1600-1900ms adaptive)
10. Ship + QA listener verdict
```

KHÔNG SKIP. KHÔNG SUY LUẬN. KHÔNG SHIP partial.

---

# Generator VNSL Addon v1.1 LOCKED (R66-R80)

**Status:** ❄️ FROZEN 2026-06-26 round 17. EP02-EP90 generate spec PHẢI tuân thủ.

## Rules enforce: R66 R67 R72 R73 R74 R75 R76 R77 R78 R79 R80

(R74-R80 thêm round 17 — xem chi tiết memory `feedback_svhmp_script_8_hard_rules.md` + `feedback_svhmp_audit_lessons_20260626.md`)

- **R74** anaphora cross-chunk guard (Tôi sợ x3, Anh không x2)
- **R75** em-dash `—` không pause TTS (continuation marker)
- **R76** open-vowel tail BigVGAN phù (`nữa/mãi/qua/rồi/lâu/đâu/sau...`)
- **R77** short-fragment chain dính (`Vỏ xà cừ, mặt số La Mã. Kim đồng hồ...`)
- **R78** voice carryover cross-chunk (the thé `/vowel/+/stop/`)
- **R79** post-audit mandatory (vnsl_validator PASS 0)
- **R80** transient peak tail guard (BigVGAN "bụp" near clipping)

**ANTI-PATTERN:** câu dài >20 từ có ≥3 comma split mid-clause → IndexTTS2 + BigVGAN insert internal silence + stop-consonant resume = **"BỤP" transient**. Fix: split thành 2-3 câu rời `.`.



**Embed vào SVHMP Generator template phần OUTPUT_SPEC_TXT cho EP02-EP90.**

## 1. VNSL LEXICON REFERENCE (R65 mandatory)

Mọi từ ngữ trạng thái/cảm xúc/cử chỉ/giác quan ưu tiên PICK từ `data/vnsl_lexicon.json`:
- `sensory.vision/audio/smell/touch/taste` — 5 giác quan ngoại cảnh
- `body_gesture.head/eyes/hands/body` — cử chỉ thân thể
- `voice_speech.{strong_alert|burst_short_INSTINCT|soft_intimate|painful_grief|hesitant|silent_blocked|narrative_calm|formal_initiate|ghost_distant}` — 9 mode nói
- `emotion.joy/sad_grief/fear/regret_unresolved/anger/surprise_burst`
- `temporal.{PRESENT_specific|PAST_specific|PAST_vague|PAST_flashback_marker|RECURRING|FUTURE_open|DURATION}`
- `spatial.near/far/back/location_ep01/direction`
- `supernatural.spirits/objects_ep01_signature/atmospheric/anomalies`

**Từ ngoài kho** → mark `TENTATIVE_NEW_LEX` trong field `lex_review` của chunk, đề xuất bổ sung kho v.next.

## 2. VERB USAGE GUIDE (R73 hardlock)

Tra cứu `_verb_usage_guide` trước khi pick verb:
- **"thốt"** CHỈ dùng khi cảm xúc bùng nổ NGẮN 1-5 từ (surprise/fear_sudden/pain_acute/joy_burst). KHÔNG dùng cho narration trầm tĩnh, monologue, whisper.
  - **Cấm**: `khẽ thốt`, `thốt được`, `thốt từ từ`, `thốt ra câu dài 7+ từ`.
  - **Thay** narration trầm → `nói/kể/bảo`, whisper → `thì thầm/lẩm bẩm`, regret quiet → `khẽ bảo/ngân nga`, monologue → `tự nhủ/nghĩ thầm`.
- **"hét"** HIẾM trong horror radio quiet (overuse hỏng atmosphere). Chỉ panic peak.
- **"thì thầm"** + **"lẩm bẩm"** + **"nức nở"** + **"nghẹn lại"** + **"vọng"** = TOP picks cho SVHMP.

## 3. TEMPORAL DISAMBIGUATION (R72 hardlock)

Trong 1 chunk HOẶC 2 chunks liền nhau:
- KHÔNG dùng cùng 1 base word (`đêm` / `tối` / `lúc` / `khi` / `hôm`) cho cả PRESENT lẫn PAST.
- Trong 1 đoạn KHÔNG dùng base "đêm" > 2 lần (trừ poetic anaphora intentional).
- Map phân biệt:
  - PRESENT → `đêm nay / tối nay / lúc này / bây giờ`
  - PAST_VAGUE → `một quãng xa xôi / thuở ấy / khi xưa / có một dạo / một lần nào đó`
  - PAST_FLASHBACK_MARKER → `Trong ký ức,` / `Hồi đó,` / `Lúc ấy,` / `Khải Phong nhớ lại,`
  - RECURRING → `mỗi đêm / mỗi khuya / đêm đêm / hằng đêm` (rotate, không lặp 1 form 2+ lần)

## 4. STOP-CONSONANT TAIL GUARD (R67 hardlock)

Câu KẾT section/chunk KHÔNG kết bằng `/t/ /k/ /p/` stop ngắn:
- **Cấm tail**: `suốt khuất biết đứt tắt thắt ngắt cắt kịch khắc tách đập thắp tắp kẹt rút sót`
- **Ưu tiên kết bằng**: vần mở `/aːj/ /əː/ /ɤ/` HOẶC vần đóng êm `/n/ /m/ /ŋ/ /ɲ/`
- Fix bằng cách đảo từ phụ lên trước (vd "trong suốt" → "lặng lẽ").

## 5. CROSS-SECTION BOUNDARY (R66 LOCKED)

Spec gen PHẢI ghi `boundary_pause_target_ms` cho mỗi cặp section liền kề theo emotion arc:
- pair_12 HOOK→SETUP: **1600ms**
- pair_23 SETUP→INCIDENT: **1700ms**
- pair_34 INCIDENT→REVEAL: **1800ms**
- pair_45 REVEAL→PAYOFF: **1800ms**
- pair_56 PAYOFF→CLIFFHANGER: **1900ms**

Câu kết section PHẢI TRÒN NGHĨA (kết `.` `…`, KHÔNG `,` `—` `;`).

## 6. EPISODE-END TEMPO RELAX (R71)

Chunk cuối EP (CLIFFHANGER cuối) field `tempo_factor`:
- Buồn lắng/lingering → 0.85 (chậm 15%)
- Cliffhanger nhẹ → 0.88 (chậm 12%)
- Câu hỏi mở chuyến xe sau → 0.90 (chậm 10%)
- Chunks GIỮA EP: TUYỆT ĐỐI `tempo_factor: 1.0` (chống lạm dụng)

## 7. FORBIDDEN PATTERNS REGISTRY (auto-check)

Generator output spec PHẢI tự loại các pattern trong `_forbidden_patterns`:
- `phonetic_risk` (mispronounce)
- `logic_violations` (chết rồi gọi điện...)
- `temporal_overload`
- `verb_misuse`
- `stop_consonant_tail`

Sau khi generate spec, chạy `tools/vnsl_validator.py spec.json` → expect 0 issues. Nếu FAIL → tự reword + retry.

## 8. PHRASE TEMPLATES (R65 seed)

Tham khảo `phrase_templates` cho mỗi section type:
- `HOOK_opener`, `SETUP_scene`, `INCIDENT_pivot`, `REVEAL_twist`, `PAYOFF_resolve`, `CLIFFHANGER_closer`

## VALIDATOR ENFORCEMENT

```
python tools/vnsl_validator.py spec_ep0X_section_*.json
# expect: TOTAL: 0 issues
# nếu có issue → reword theo `fix` suggestion → re-validate
```

Validator báo cáo theo: `rule (R72/R67/R73/R3) / severity (HIGH/MED) / sec / ch / msg / fix`.
