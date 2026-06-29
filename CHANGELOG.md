# CHANGELOG

## v1.0.0-rc1 — Tier 1 Frozen (2026-06-30)

### Added
- **bible/00_constitution.yaml**: 43 codified rules (R170-R173 priority)
  - R170 ZERO-HALLUCINATION (TOP)
  - R171 Technical Audit Protocol v1.0 (table format)
  - R172 Role Separation 3-way (Writer/Tester/Auditor)
  - R173 Autonomous Execution v2.0
- **bible/27_fact_db.yaml**: Fact Database EP01 immutable
- **bible/30_error_handbook.yaml**: 50 structured errors (E-001 → E-050 + 5 patterns)
- **bible/31_golden_samples.yaml**: Golden text EP01 locked + regression validation note
- **bible/32_repair_contract.yaml**: Repair schema (locked/allowed/forbidden + rollback_if_fail)
- **bible/33_rule_catalog.yaml**: Rule catalog with severity/phase/auto_fix/rollback

### Tools (8 QA + infrastructure)
- tools/qa_eol_diacritic.py (R86)
- tools/qa_honorific.py (R92b/R95/R107)
- tools/qa_continuity.py (R110 — negation-aware after fix)
- tools/qa_phonetic_safe.py (R111)
- tools/qa_repeat_action.py (R113)
- tools/qa_fact_check.py (R117)
- tools/qa_anti_generic.py (R128)
- tools/qa_ssot_diff.py (R141 — brand drift check added)
- tools/publish_score.py (R140 gate)
- tools/episode_state.py (R149 state machine)
- tools/render_chunk.py + patch_audio_chunk.py (R146 skeleton)

### Tests
- tests/test_harness.py — 10-vòng runner all stable
- tests/cases/ — 10 dedicated test files (R86/R92b/R110/R111/R113/R117/R128/R141/R140/R149/R146)
- tests/regression/generate_dataset.py — 50 positive + 50 negative generator
- tests/regression_runner.py — full regression with KPI verification
- tests/regression/{positive,negative}/ — 100 sample dataset

### Validation artifacts
- tests/regression/validation_report.md
- tests/regression/regression_report.json
- tests/regression/rule_score.csv
- tests/regression/diagnosis_report.md

### CMD QA prompts (R143 Multi-Pass Agent)
- cmd/CMD_QA_LOGIC.md
- cmd/CMD_QA_LANGUAGE.md
- cmd/CMD_QA_AUDIO.md

### Fixed
- R86 FP 50% → 0% (positive variants self-verify added)
- R110 FN 100% → 0% (negation-aware + elif→if multiple states per line)
- R141 FN 33% → 0% (brand drift check added)
- gen_dataset IndexError (extended violations list to 50)

### Removed
- (none)

### Regression Validation (KPI Mr.Long lock: FP≤10%, FN≤15%)
- 100 samples × 8 tools = 800 runs
- 8/8 PASS
