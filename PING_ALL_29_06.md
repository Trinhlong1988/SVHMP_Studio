# 📢 PING ALL CMDs — 29/6 18:15 — Coordination protocol

**From:** CMD LEAD (Claude Opus 4.7 1M)
**To:** CMD #2 (RENDER session) + CMD #3 (QA WATCH loop) + future CMDs
**Mr.Long lệnh:** "phải cho phối hợp tự động" — set up auto-coordinate KHÔNG qua Mr.Long trung gian.

## 📋 READ FIRST

**`COORDINATION_HUB.md`** — Full protocol architecture, anti-patterns, channels mapped.

## 🆕 Channel auto-trigger ACTIVE

| Channel | Direction | Tool |
|---------|-----------|------|
| `PING_CMD_LEAD_29_06.md` AUTO LOG | All | `python tools/log_ping.py CATEGORY "msg"` |
| `COORDINATION_HUB.md` | LEAD → All | Static protocol |
| `git log --oneline` | All | Source of truth |

**Categories:** VIOLATION / FIX / RENDER / AUDIT / APPROVE / RULE / INFO

## 🔁 Auto-workflow ACTIVE từ giờ

### CMD #3 → CMD LEAD (R98/R86 violation):
- CMD #3 `qa_watch.py` detect violation
- AUTO LOG `[VIOLATION] QA WATCH iter N: X repeat words [L<line>:<word> ...]` (em vừa cập nhật chi tiết)
- CMD LEAD đọc PING → fetch context → propose fix R92 SELF-VERIFY → apply → log [FIX]
- Loop close ≤ 60s

### CMD #2 → CMD #3 (section render done):
- CMD #2 `render_section.py` done → log `[RENDER] section.wav shipped`
- CMD #3 next iter detect file mới → STAGE 3 audit → log [AUDIT]
- Nếu FAIL → CMD LEAD action; nếu PASS → CMD #2 next section

### Commit pipeline:
- Pre-commit hook .githooks/pre-commit:
  - SECTION A: R-ID conflict check (tools/check_rule_id_free.py --staged)
  - SECTION B: R41 post_render_gate (EP modified)
- BLOCK nếu fail. KHÔNG `--no-verify` (Mr.Long lệnh nghiêm cấm).

## ⚡ ACTION đã ship session 18:15

| Action | Status |
|--------|--------|
| R98 fix EP01 L220 "lâu lâu" → "lâu" | ✅ applied |
| qa_watch.py whitelist (rì rì / từ từ / cross-sentence) | ✅ updated |
| qa_watch.py log với từ + line cụ thể | ✅ updated |
| Verify R86 STAGE 1: 0 violations | ✅ |
| Verify R98: 5 detect → 0 real | ✅ |
| COORDINATION_HUB.md ship | ✅ |
| PING_ALL_29_06.md ship | ✅ (this) |

## 📡 CMD #3 RESTART REQUEST
qa_watch.py updated — CMD #3 kill current loop + restart để pull whitelist mới:
```
Ctrl+C current loop
python tools/qa_watch.py
```
Expect: STAGE 1 PASS + R98 0 violations từ iter tiếp.

## 📡 CMD #2 NEXT
- Mix REVEAL/PAYOFF/CLIFFHANGER + music (cùng pattern HOOK+SETUP+INCIDENT)
- Concat full 6 sections → EP01 master
- Log từng step qua `log_ping.py [RENDER] msg`

## 📡 CMD LEAD STANDBY
Em monitor PING + auto-apply fix khi VIOLATION log từ CMD #3.
Em không touch EP02-50 (1845 R86) cho tới khi EP01 master xong + Mr.Long approve scale.

**End ping all.**
