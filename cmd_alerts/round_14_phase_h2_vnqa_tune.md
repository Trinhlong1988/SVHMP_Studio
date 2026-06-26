---
alert_id: round_14_phase_h2_vnqa_tune
ts: 2026-06-26
severity: INFO
target: ALL_ACTIVE_CMDS (SVHMP, render, audit)
ack_required: false
---

# Alert — Round 14 Phase H2 VNQA tune SHIPPED

**Mr.Long approve 26/6:** câu dài 60-145 từ trong SVHMP horror là chủ ý văn học, KHÔNG flag.

## Thay đổi đã ship (commit `3a6a756` + Phase H2 wire pending commit)

1. **`tools/vnqa/genres/horror_narrative.yaml:13`** — `sentence_len_max_words` 40 → **150**
2. **`tools/vnqa/pipeline.py:89`** — constant tune cùng giá trị
3. **`tools/vnqa/pipeline.py`** — wire load `resources/*.yaml` + `data/vnsl_lexicon.json` (path B30 fix)
4. **`TOKEN_REPEAT_WHITELIST`** — 34 entries (proper noun + central object), B29 fix
5. **`prompts/qa.md` v1.5** — PHASE 12.20 VNQA Library Check H1-H7
6. **`tools/qa_skeptic_orchestrator.py` v1.1** — chain QA → VNQA → Skeptic
7. **`tools/dashboard/` v3.1** — `/api/vnqa` route + panel verdict

## CMD đang chạy cần làm gì

- Nếu CMD đã cache `tools/vnqa/pipeline.py` trong memory: **reload module** hoặc restart
- Nếu CMD đang gen TTS EP02+: không bị ảnh hưởng (TTS không dùng VNQA realtime)
- Nếu CMD đang chạy audit batch: chỉ áp dụng cho run NEXT (file đã update on-disk)

## Cấm
- **KHÔNG tự chẻ câu dài** trong SVHMP scripts (memory `feedback_svhmp_long_sentence_intent.md`)
- **KHÔNG flag** "anh"/"đồng hồ"/"ghế"/"tay" repeat (memory B29)

## Verify thực tế (đã chạy)
- EP01 VNQA verdict: WARN(10) → PASS(0 critical/0 warning/1 minor)
- Lexicon load: 8 top keys / 9 voice_speech entries
- Regression 6 audit: 170/170 PASS giữ nguyên

## Cross-ref
- `BUGS_FIXED.md` B29 (token_repeat false positive), B30 (path resolve)
- `VERSION.md` round 14 Phase H + Phase H2
- `MEMORY.md` → `feedback_svhmp_long_sentence_intent.md`, `project_svhmp_vnqa_framework.md`

---

**CMD đang đọc alert này:** acknowledge bằng append timestamp vào `cmd_alerts/ack/<your_cmd_id>.txt`. Mr.Long check folder ack để biết CMD nào đã đọc.
