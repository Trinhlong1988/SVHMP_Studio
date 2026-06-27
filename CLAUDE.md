# SVHMP_Studio Project CLAUDE.md

**Project:** SVHMP (Sài Gòn Hắc Mạ Phố / Hắc Dạ Ký narrative horror)
**Path:** `D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\`
**Last update:** 2026-06-27 (round 14 Phase H8)

## Session Start Protocol (BẮT BUỘC)

1. Đọc `CLAUDE.md` workspace (`C:\Users\Administrator\CLAUDE.md`)
2. Đọc `VERSION.md` project → so với last_known_version, mismatch → re-read changed artifacts
3. Đọc `BUGS_FIXED.md` project (B1-B36+)
4. Đọc memory `feedback_svhmp_*` + `project_svhmp_*` relevant
5. EP02+ render: Đọc `feedback_svhmp_script_8_hard_rules.md` (32 rules) + `project_svhmp_master_production_v1.md`

## Bibles (immutable)

- `bible/00` Constitution (ALWAYS_5 + NEVER_7 + GHOST_RULES_3 + SERIES_RULES_8 + ENDING_RULES_2)
- `bible/03` Recurring chars (CHAR_DRIVER + CHAR_NAM only — CẤM tạo mới)
- `bible/11` Regret catalog (27 sub-archetypes, distribution 32/24/20/14/10)
- `bible/12` Object library (71+ OBJ_)
- `bible/13` Setting library (21+ setting_)
- `bible/18` Driver reveal budget (EP73 + EP90 reserved)
- `bible/22` Anti-slop VN (32 rules)
- `bible/23` Passenger naming (5 rules, Mr.Long lock 27/6)

## 100 Passenger Framework

- `runtime/passenger_roster_100.yaml` — 100 passenger LOCK
- 50 NU + 50 NAM unique names (15 forbidden Mr.Long: Nam, Tài, Quang, Hưng, Long, Trang, Linh, Nhung, Lương, Khánh, An, Tùng, Tiến, Tú, Mai)
- `data/vietnamese_names_extended.yaml` — REUSABLE database 200+ syllables

## Pipeline

```
Generator → episode.md
    ↓ (auto_watch daemon poll 5s)
qa_skeptic_orchestrator.py
    ↓ AUTO_FIX (R001 bùn cầu, R002 Bất chợt + future rules)
    ↓ VNQA H1-H9 (underthesea + Hoàng Phê lexicon)
    ↓ Claude QA
    ↓ Skeptic Gemma adversarial (Ollama)
    ↓
final_verdict_ep_{N}.json
```

## Audits

- `C:/tmp/svhmp_constitution_50round_audit.py` — 50 vòng hiến pháp
- `C:/tmp/svhmp_deep_100round_audit.py` — 110 vòng comprehensive
- `C:/tmp/svhmp_vnqa_100round_audit.py` — VNQA framework
- `C:/tmp/hdk_audit_20rounds.py` — HDK channel + intro

## Tools key

- `tools/auto_watch.py` — daemon (Windows scheduled task `SVHMP_AutoWatch`)
- `tools/vnqa/pipeline.py` — H1-H9 checks
- `tools/vnqa/auto_fix.py` — Phase H4 semi-auto literal map
- `tools/gen_100_passenger.py` — procedural roster gen
- `tools/build_name_pool.py` — load Vietnamese names database → pair pool
- `tools/llm_router.py` — Ollama + free_ollama_vram() (B34 fix)
- `tools/svhmp_v13_render.py` — TTS pipeline LOCKED v1.3

## Memory references

- `feedback_svhmp_long_sentence_intent.md` — câu dài chủ ý
- `feedback_svhmp_tts_voice_fixes.md` — TTS pronunciation fixes
- `feedback_ollama_keepalive_vram_truth.md` — Ollama VRAM
- `project_svhmp_vnqa_framework.md` — VNQA wire
- `project_svhmp_vnqa_autofix.md` — Phase H4 autofix
- `project_svhmp_auto_watch.md` — Phase H5 daemon
- `feedback_cam_suy_luan.md` — NO speculation rule
- `feedback_fix_registry_rule.md` — BUGS_FIXED + VERSION.md global rule
