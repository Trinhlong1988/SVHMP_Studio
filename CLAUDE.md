# SVHMP_Studio Project CLAUDE.md

> **TỐI THƯỢNG (Mr.Long 30/6 21:45):** Mỗi lần Mr.Long đào sâu mà phát hiện bug mới, hãy coi đó là **thất bại của quy trình kiểm thử**, không chỉ là thất bại của module. Sau khi sửa bug, **bắt buộc đề xuất thay đổi quy trình hoặc bổ sung test** để loại bug đó không thể lọt qua lần nữa. (R_SUPREME.test_process_failure_principle — bible/00)

> **TỐI THƯỢNG R196 (Mr.Long 30/6 22:50):** **Engineering PASS ≠ Production PASS.** A module is NEVER complete until it passes at least one real production run. Production evidence ALWAYS overrides engineering evidence. Only Golden Production Output authorizes Freeze and Release. CẤM dùng từ "complete / done / 100% hoàn thành" cho module chưa Production validated. Dùng "Engineering Validation PASS / Ready for Production Validation" thay thế.

> **TỐI THƯỢNG R197 (Mr.Long 30/6 23:30):** **Every text modification MUST execute FULL_TEXT_GATE before any render — without exception.** KHÔNG phải "Remember" — MÀ **MUST**. FULL_TEXT_GATE = qa_eol_diacritic (R86 broad NGA+NANG+HOI) + ALL existing text QA tools. KHÔNG được "Text Gate" với 1 tool — phải FULL stack. Enforce: `tools/svhmp_preflight_qa.py`. Regression: `tests/test_full_text_gate_r86_broad.py` 5/5 PASS.

> **TỐI THƯỢNG R_SUPREME R1-R10 GOVERNANCE LOCK (Mr.Long 30/6 02:50 docx):** Mr.Long = ONLY AUTHORITY for any architecture/production/render/freeze/release/rule change. Claude = Engineering Executor, NOT autonomous decision maker. **R1** No autonomous action. **R2** Permission first (4 questions). **R3** Production Validation mode: ONLY render/QA/reports/evidence/wait — FORBIDDEN redesign/extend/optimize/speculative. **R4** Bug class — extend existing rule ONLY after approval. **R5** Process failure — NO instance fix first, analyze process. **R6** PASS declaration MUST qualify (e.g., "PASS within current QA coverage"). **R7** Write workflow: Read→Diff→Proposal→Approval→Backup→Patch→Regression→Production. **R8** Baseline protection (verify/lock/backup/checksum/diff before patch). **R9** Evidence first (no assumption). **R10** Final safety: uncertainty → STOP not ACT. No exception.

> **TỐI THƯỢNG R200 REALTIME SYNC (Mr.Long 1/7):** **Bất kể CMD nào, làm trên máy nào — đều PHẢI giữ repo ↔ local đồng bộ toàn diện, realtime.**
> - **TRƯỚC khi làm:** `git pull --rebase origin main` + kiểm tra `git status` sạch + `git log --oneline -1` local == remote HEAD. Máy khác (CMD executor) push realtime → không rebase là bị reject "fetch first".
> - **SAU mỗi fix (ngay lập tức, KHÔNG gom cuối buổi):** (1) **cập nhật lại config liên quan** — CLAUDE.md / VERSION.md / BUGS_FIXED.md / bible — sửa ở đâu cập nhật conf ở đó, KHÔNG để lệch giữa các máy; (2) `python tools/log_ping.py FIX "..."` cho CMD khác biết; (3) `git add` + commit + `git push origin main`; (4) xác nhận local HEAD == remote HEAD.
> - **Copy chuẩn:** máy Admin = clone `C:\Users\Admin\SVHMP_git` (có `.git`). Thư mục ZIP `...-6d16ecda` là STALE — **CẤM sửa vào đó** (sẽ lệch repo).

> **TỐI THƯỢNG R210 CHARACTER IDENTITY SYSTEM v2 (Mr.Long 1/7):** Mỗi nhân vật = **1 hồ sơ sống** định danh bởi `character_id` DUY NHẤT. Schema 3 tầng `bible/37_character_schema.yaml` (Tier1 BẮT BUỘC ~40 field / Tier2 bối cảnh / Tier3 mở rộng — audio-first, CẮT field thị giác thuần, **KHÔNG bịa field vô căn cứ**). **Voice Profile + Relationship Graph BẮT BUỘC.** (1) **CẤM sinh dialog** khi focal char thiếu Tier1 (quê/giọng/xưng hô/nỗi đau/haunting_symbol) — *completeness gate*. (2) **CẤM đổi field khóa cross-episode** (id/tên/tuổi/giới/quê/nghề) — `story_consistency_validator`. (3) **Cân bằng xuyên 100 tập** theo target (trẻ em 10-15%, người già 15-20%, ≥3 vùng giọng, 9 kiểu chết, 5-8 nhân vật/tập) — `character_balance_report`. Reconcile: **KHÔNG sinh lại tên** (bible/23 giữ nguyên), **KHÔNG phá** bible/11 regret lock. Tools: `character_manager` · `dialog_voice_validator` · `character_balance_report` · `story_consistency_validator`. QA evidence: R205 16/16, R206 1000/1000, R207 1000/1000. Status: **LOCKED** (Boss 2/7) — schema `bible/37` active + roster **ĐÃ migrate v2** (`migrate_roster_v2.py`): age/region/death cân bằng **0 flag**, **100/100 profile hợp lệ** (quê↔giọng nhất quán). Identity (id/tên/regret/object/gender/ep) giữ nguyên; chỉ enrich age/voice/death/life_status.

> **TỐI THƯỢNG R211 TIER-0 GOVERNANCE (Mr.Long 2/7, từ phản biện.txt):** `governance/architecture_registry.yaml` = **source of truth** cho file↔domain↔quyền sửa↔promotion. **TRƯỚC khi tạo module/tool mới**: (1) chạy `tools/architecture_registry_check.py` (0 MISSING); (2) trả đủ **Change Request Gate 6 câu** (domain? trùng cũ? source-of-truth? schema/runtime? QA ảnh hưởng? test nào chứng minh?) — không đủ → **STOP**. Promotion Gate: chỉ `promotion_status=locked` được Generator dùng. **Reconcile (KHÔNG nhân đôi):** Change Gate=R7, Audit Log=R200+log_ping+commit, Promotion=bible lock. Bằng chứng hiện tại: **186 file UNMAPPED** cần triage dần (KHÔNG sửa logic ồ ạt trước khi map — chống loạn).

**Project:** SVHMP (Sài Gòn Hắc Mạ Phố / Hắc Dạ Ký narrative horror)
**Path:** `D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\`
**Last update:** 2026-06-30 (R_SUPREME workflow lock + test_process_failure_principle)

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
