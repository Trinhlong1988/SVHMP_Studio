# Generator VNSL Addon v1.0

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
  - PAST_FLASHBACK_MARKER → `Trong ký ức,` / `Hồi đó,` / `Lúc ấy,` / `Quang nhớ lại,`
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
