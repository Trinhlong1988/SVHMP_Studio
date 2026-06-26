---
alert_id: round_14_phase_h4_autofix_chained
ts: 2026-06-26
severity: INFO
target: ALL_ACTIVE_CMDS
ack_required: false
---

# Alert — Phase H4 Auto-Fix CHAINED vào orchestrator pipeline

**Generator EP02-EP90 từ giờ KHÔNG cần chạy thủ công auto_fix.**

## Pipeline mới

```
Generator → episode.md
            ↓
        orchestrator.py (qa_skeptic_orchestrator.py v1.2)
            ↓
        AUTO_FIX (apply mode default) ← R001 bùn cầu, R002 Bất chợt
            ↓
        VNQA library check (H1-H9)
            ↓
        Claude QA
            ↓
        Skeptic Gemma adversarial
            ↓
        Final verdict + runtime/{autofix,vnqa,final_verdict}_ep_{N}.json
```

## Run lệnh
```bash
# Full chain (default — autofix apply + vnqa + skeptic)
python tools/qa_skeptic_orchestrator.py --ep 2 --episode output/ep_02/episode.md

# Skip autofix (Mr.Long muốn review diff trước)
python tools/qa_skeptic_orchestrator.py --ep 2 --episode output/ep_02/episode.md --autofix-mode propose

# Skip everything autofix
python tools/qa_skeptic_orchestrator.py --ep 2 --episode output/ep_02/episode.md --no-autofix
```

## Thay đổi

1. `tools/qa_skeptic_orchestrator.py` v1.1 → v1.2
   - Wire `auto_fix.py` BEFORE VNQA
   - Fix encoding=utf-8 subprocess (cp1252 crash Vietnamese characters)
   - Flag `--no-autofix` + `--autofix-mode {apply,propose}`
   - Output: `runtime/autofix_ep_{N}.json` log

2. Default behavior: AUTO_APPLY rules trong registry → có backup `.bak_autofix_{ts}`
3. Mr.Long approve rules trong session sau = append vào `data/vnqa_approved_replacements.yaml`

## Verify thực tế (đã chạy)

- Fake EP02 inject 3 bugs (2× bùn cầu + 1× Bất chợt) → orchestrator chain → bugs CLEAR
- `runtime/autofix_ep_2.json` log đầy đủ
- Regression 170/170 PASS (6 audits)

## Cross-ref

- `BUGS_FIXED.md` B32 (encoding fix orchestrator subprocess)
- `VERSION.md` round 14 Phase H4 entry
- `MEMORY.md` → `project_svhmp_vnqa_autofix.md`
