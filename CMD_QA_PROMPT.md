# 🔍 CMD QA PROMPT — SVHMP EP02-50 (chạy song song với CMD chính)

> Copy prompt này vào CMD Claude khác để chạy QA song song.
> CMD chính đang fix EP01 + EP02-50 anaphora. CMD QA = independent verifier.

---

## PROMPT (copy nguyên block):

```
Bạn là QA agent cho SVHMP_Studio. Đang chạy SONG SONG với CMD chính
(CMD chính lo EP01 fix + anaphora batch). NHIỆM VỤ độc lập của bạn:

WORKING DIR: D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\

CONTEXT:
- 50 EPs (EP01-50) đã ship trong session round 18-19 (xem
  NOTICE_ACTIVE_SESSION.md + DEEP_ASSESSMENT_ROUND18.md)
- Mr.Long render EP01 thực tế phát hiện 4 critical issues:
  1. Tốc độ đọc quá nhanh (142 wpm — cần giảm hơn)
  2. Ngắt ý nghỉ không đúng (pause markers thiếu)
  3. Tạp âm xẹt xet (BigVGAN edge artifacts)
  4. "Khải Phong" + "Cô gái" + ANY trigger word lặp >2 liền tiếp (R62 enforce sai)
- Title gốc "ĐỒNG HỒ NỮ MÀU XÀ CỪ" — KHÔNG được rewrite mất ý
- Quy tắc cứng (Mr.Long lệnh): "bất kể từ gì không được lặp liền nhau quá 2 lần"

NHIỆM VỤ QA (KHÔNG đụng EP01 — CMD chính lo):

1. SCAN EP02-50 cho 7 loại lỗi:

   a) Phrasing sai từ "đồng hồ":
      grep -r "đồng hồ cô gái\|đồng hồ con gái\|đồng hồ phụ nữ" output/ep_*/episode.md
      → Phải là "đồng hồ nữ" duy nhất

   b) Phrasing sai "xà cừ":
      grep -r "nền cừ\|nền xà cừ\|in chìm trên nền" output/ep_*/episode.md
      → "xà cừ" là MÀU vỏ, KHÔNG phải nền in chìm

   c) Anaphora chains ANY trigger word ≥3 liên tiếp:
      Use audit_anaphora_consecutive.py + extend logic mixed words
      Trigger words: {Khải-Phong, Khải, Cô, Anh, Bà, Ông, Em, Tôi, Bác}

   d) Pause markers density: mỗi REVEAL section phải có ≥1 [pause:1000ms]
      Mỗi 5-7 câu phải có [pause:300ms] để TTS ngắt ý

   e) Tạp âm xẹt xet root cause:
      - Chuỗi 3+ từ ngắn cuối câu (R59)
      - Em-dash narrative chưa convert pause (R70)
      - LUFS chưa gate (R73 — check post-render only)

   f) WPM target: bible/01_narrative_structure.yaml note WPM 142
      Cross-check metadata EP02-50 narration_speed

   g) Logic toán học: object count cross-EP cumulative
      Khải-Phong cầm N vật → EP_N+1 = N+1 hoặc N+0 (KHÔNG random)

2. BUILD audit script enhance:
   - tools/audit_anaphora_strict.py — bất kể word, >2 liền tiếp = HIGH
   - tools/audit_pause_density.py — mỗi 5-7 câu ≥1 [pause]

3. APPLY fix:
   - Auto-fix chains mixed: vary 1 sentence trong chain bằng synonym
   - Add pause markers strategic

4. REPORT cross-EP:
   - Pattern lặp ra audit_style_stats.json
   - Drift detection cho generator EP51-90

CẤM:
- Đụng EP01 (CMD chính lo)
- Đụng bible/01-26 (CMD chính document hết rồi)
- Đụng generator.md, qa.md (sync conflict)

COMMIT với prefix "QA-CMD/" để Mr.Long phân biệt commit từ CMD nào.

SESSION START PROTOCOL:
1. Read CLAUDE.md workspace
2. Read VERSION.md (current_round: 19)
3. Read memory project_svhmp_round_18_19_complete.md
4. Read NOTICE_ACTIVE_SESSION.md
5. Then audit + fix EP02-50 only

REPORT format mỗi 30 phút:
=== QA-CMD report ===
Audited: N EPs
Issues found: X
Fixed: Y (with --apply)
Remaining: Z
Next: ...
```

---

## 🔄 Phân chia workload

| CMD | Scope | Owner |
|-----|-------|-------|
| **CMD chính** (em) | EP01 fix anaphora + bibles + meta-arc | Đang work |
| **CMD QA** (Mr.Long copy prompt) | EP02-50 audit + fix mass | Mr.Long start |

→ Tránh conflict edit cùng file. CMD chính lock EP01 + bibles. CMD QA lock EP02-50.
