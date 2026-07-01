# PING CMD LEAD — R198 cap_peak.py wired into render pipeline
**From:** CMD THỰC THI
**Date:** 2026-06-30T23:55
**Trigger:** Mr.Long catch setup.wav CLIP recur 4 lần — root cause `cap_peak.py` not wired into svhmp_v13_render.

## Status

| Item | Status |
|---|---|
| R198 codified bible/00 | ✅ DONE |
| svhmp_v13_render.py wire cap_peak.py post-loudnorm | ✅ DONE (line 360-374) |
| Syntax verified | ✅ PASS |
| cap_peak.py existing setup.wav check | ✅ PASS peak -1.50 dB |
| Render v200 still alive (will pick up R198 for remaining sections) | ✅ chunk 69/95 reveal section |
| Memory feedback saved | ✅ feedback_tool_built_not_wired_gap_global_30_6.md |
| MEMORY.md indexed | ⏸️ next |
| Orphan rule flush 30/6 | ✅ DONE 8 stubs codified (R77/R78/R79/R80/R87b/R108/R109/R175b) |
| Real orphans remaining | 0 (R2-R17/R200 are preflight tool-internal numbers, not bible rules) |

## Pipeline before/after

**BEFORE (broken — setup.wav CLIP 4 lần):**
```
TTS render → loudnorm → volume → alimiter (limit=0.85) → OUTPUT (peak push qua 0 = CLIP)
```

**AFTER (R198 wired):**
```
TTS render → loudnorm → volume → alimiter → cap_peak.py (hardlock ≤ -1.0 dB) → OUTPUT
```

## Process gap class identified (new)

**"Tool built ≠ Tool wired"** — distinct from "Test PASS ≠ Rule codified".
- cap_peak.py existed (~30 LOC) since earlier round but never invoked
- Em manual volume fix 4 lần = symptom patch, KHÔNG fix root cause
- Process gap: tool registry vs pipeline invocation gap

## Recommended Phase 2.6 build (post Tier 2.1 Golden)

Build `tools/pipeline_wiring_audit.py` — scan every `tools/*.py` with "wire/pipeline/gate" docstring, verify caller exists in pipeline scripts.

## Em STANDBY

Render still running (chunk 69/95 reveal). After all 6 sections done:
1. Re-render setup.wav individually with new R198-wired pipeline (verify peak ≤ -1.0 dB)
2. Mix v200
3. Voice QA detect catalog
4. audio_pre_ship_gate
5. Generate remaining 3 mandatory artifacts
6. Ping CMD LEAD final + STOP for Mr.Long review
