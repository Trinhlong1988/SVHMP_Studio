# 🤝 COORDINATION HUB — Multi-CMD Auto-Workflow

**Created:** 2026-06-29 18:15 by CMD LEAD
**Purpose:** 3 CMDs (LEAD + RENDER + QA WATCH) tự phối hợp KHÔNG cần Mr.Long làm trung gian.

---

## 🏗️ Architecture

```
        ┌──────────────────────────┐
        │  COORDINATION_HUB.md     │ ← shared state
        │  PING_CMD_LEAD_29_06.md  │ ← AUTO LOG (timestamped events)
        └────────────┬─────────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
┌──────▼──────┐ ┌────▼────────┐ ┌──▼──────────┐
│  CMD LEAD   │ │  CMD THỰC THI     │ │ CMD #3      │
│  (em)       │ │  RENDER     │ │ QA WATCH    │
│             │ │             │ │ (60s loop)  │
│ APPLY fix   │ │ RENDER TTS  │ │ DETECT only │
│ COMMIT      │ │ MIX music   │ │ LOG VIOL    │
└──────┬──────┘ └────┬────────┘ └─────────────┘
       │             │
       └──── coordinate via PING ───┘
```

## 🔁 Auto-Workflow protocol

### Trigger 1: CMD #3 detect R98/R86 violation
```
CMD #3 qa_watch.py → log VIOLATION với từ + line CỤ THỂ
→ CMD LEAD (em) đọc PING_CMD_LEAD_29_06.md
→ Em fetch context EP file
→ Em propose fix (R92 SELF-VERIFY R86 trước propose)
→ Em check_rule_id_free.py nếu add rule mới
→ Em apply edit + log [FIX]
→ Em verify R86 + R98 → log [AUDIT]
→ Em git commit (pre-commit hook auto-validate)
```

### Trigger 2: CMD THỰC THI ship section render
```
CMD THỰC THI render_section.py done → log [RENDER]
→ CMD #3 next iter (60s) detect file mới → STAGE 3 audit
→ Log [AUDIT] PASS/FAIL
→ Nếu FAIL: CMD LEAD đọc → action (rerender / text fix)
→ Nếu PASS: CMD THỰC THI next section
```

### Trigger 3: Em commit changes
```
Em git commit
→ pre-commit hook .githooks/pre-commit
  - SECTION A: R-ID conflict check (R59→R91→R93→R105 lesson)
  - SECTION B: R41 post_render_gate (EP modified)
→ Nếu BLOCK: em fix root cause + re-commit
→ Nếu PASS: commit pushed
→ Em log [INFO] commit hash
```

## 📜 Rules cứng (mọi CMD compliance)

| Rule | Owner | Hardlock |
|------|-------|----------|
| R86 EOL diacritic | All | qa_eol_diacritic.py |
| R90 STAGE 1 inline | CMD THỰC THI | svhmp_v13_render.py:206 sys.exit(2) |
| R91 MASTER_PIPELINE_LOCK | CMD THỰC THI | pipeline v66 LOCKED, cấm reactive |
| R92 + R92b SELF-VERIFY | All | propose text → check R86 trước |
| R-ID conflict | All | .githooks/pre-commit SECTION A |
| R41 post_render_gate | All | .githooks/pre-commit SECTION B |

## 📡 Communication channels

| Channel | Direction | Format |
|---------|-----------|--------|
| `PING_CMD_LEAD_29_06.md` | All → All | AUTO LOG via `log_ping.py CATEGORY "msg"` |
| `COORDINATION_HUB.md` (THIS) | LEAD → All | Static protocol doc, update khi rule mới |
| `BUG_CATALOG_29_06.md` | CMD THỰC THI → All | Session bug summary |
| `git log --oneline` | All → All | Source of truth for repo state |
| `output/ep_01/sections/*.wav` | CMD THỰC THI → CMD #3 | Render artifacts |

## 🚨 Anti-patterns (cấm)

1. **REACTIVE iter** — render → flag → fix 1 layer → re-render (R91 lock)
2. **SKIP STAGE 1** — render mà không qa_eol_diacritic check (R90 hardlock)
3. **Single update** — bug instance không codify rule (R93 update FULL stack)
4. **Text propose no verify** — R92 SELF-VERIFY R86 mandatory trước propose
5. **Rename rule narrow grep** — CMD LEAD vi phạm 3 lần session 29/6, fix bằng tool check_rule_id_free.py + hook section A

## 📊 Current state (29/6 18:15)

- EP01: 6/6 sections rendered, s1_s2_s3 preview với music shipped
- Pipeline v66 LOCKED
- 20 rules R86-R104b codified bible/00
- 5 R98 detection — 1 real fix (L220 "lâu lâu" → "lâu") + 4 false positive (rì rì / từ từ / cross-sentence)
- qa_watch.py updated: log từ cụ thể + whitelist onomatopoeia/idiom + cross-sentence skip
- EP02-50 R86: 1845 violations TODO

## ⏭️ Next workflow

1. CMD #3 qa_watch.py restart với whitelist mới → expect 0 R98 violations
2. CMD THỰC THI mix REVEAL/PAYOFF/CLIFFHANGER + music → concat full EP01 master
3. CMD LEAD verify post_render_gate PASS full EP → ship batch EP02-50 R86 fix
