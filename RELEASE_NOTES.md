# RELEASE NOTES — v1.0.0-rc1 (Tier 1 Frozen)

**Release date**: 2026-06-30 02:48  
**Status**: Release Candidate 1  
**Verified by**: Regression 8/8 PASS

## What's in this release

Tier 1 = QA Engine layer hoàn chỉnh cho EP01 production.

### 8 Quality Assurance tools (validated)

| Rule | Detects | KPI Result |
|---|---|---|
| R86 | EOL diacritic (ngã/nặng/hỏi cuối câu — TTS phù phù) | FP 0% / FN 14.3% |
| R92b | Honorific (xưng hô + name count + reference distance) | 100% |
| R110 | Narrative continuity (object tracking + scene physics + character count) | 100% |
| R111 | TTS phonetic safe-word DB | FP 0% / FN 14.3% |
| R113 | Action verb repeat >2 cùng wording | 100% |
| R117 | Fact Database check | 100% |
| R128 | Anti-generic AI phrase | 100% |
| R141 | SSOT diff vs fact_db (incl brand drift) | 100% |

### Publish Score Gate (R140)
- Logic ≥ 90 / Language ≥ 85 / TTS ≥ 90 → SHIP ALLOWED
- Fail any → KILL SWITCH (R142)

### Infrastructure
- Episode state machine (R149)
- Per-chunk render skeleton (R146 — chunk_timestamps emit TBD)
- Error handbook 50 structured entries (R147)
- Repair contract schema (R161)
- Rule catalog (R162)
- Multi-pass agent prompts 3 roles (R143)

### Hiến pháp top priority
- R170 Zero Hallucination
- R171 Technical Audit Protocol v1.0
- R172 Role Separation Writer/Tester/Auditor
- R173 Autonomous Execution v2.0

## Validation evidence
- `tests/regression/validation_report.md`
- `tests/regression/regression_report.json`
- `tests/regression/rule_score.csv`
- `tests/regression/diagnosis_report.md`

## Known limitations (Tier 2 TBD)
- Whisper Closed-Loop QA (post-render TTS verify) — NOT BUILT
- Character Memory per-character — NOT BUILT
- Dashboard observability — NOT BUILT
- Information Graph + Causality Graph + World Simulation — NOT BUILT
- chunk_timestamps emit from render — NOT IMPLEMENTED
- 50pos+50neg dataset coverage limited (some rules have 3-7 negatives only)

## Recommended Git tag
```bash
git tag -a v1.0.0-rc1 -m "Tier 1 Frozen — 8 QA tools regression 8/8 PASS"
git push origin v1.0.0-rc1
```

## Next steps (Tier 2 — not blocking RC1)
1. Build Whisper compare
2. Build Character Memory YAML
3. Build Dashboard
4. Implement chunk_timestamps emit
5. Build Information Graph (after Character Memory)
6. Build World State minimal

## Production-ready disclaimer
v1.0.0-**rc1** = Release Candidate. Verified by regression on EP01 golden sample only.
NOT yet validated across multiple episodes (EP02-EP90 regression TBD).
