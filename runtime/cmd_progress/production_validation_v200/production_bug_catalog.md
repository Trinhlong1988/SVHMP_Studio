# Production Bug Catalog — EP01 v200

**Status:** PARTIAL — render in progress
**Last update:** 2026-06-30T21:50

## Bugs found DURING this Production Validation cycle

### Pre-render gate failures (caught by R90 STAGE 1)

| # | Bug | Severity | Origin | Status |
|---|---|---|---|---|
| PV-01 | R86 EOL NGA "rãi" L7 (em-introduced Phase 0 R61 prefix expansion) | HIGH | em Round 22 | ✅ FIXED → "trên thành phố" SAC |
| PV-02 | R86 EOL NANG "nhẹ" L318 (em-introduced Phase 0 R61) | HIGH | em Round 22 | ✅ FIXED → "êm đềm" HUYEN |
| PV-03 | R86 EOL HOI "cả" L330 (em-introduced Phase 0 R61) | HIGH | em Round 22 | ✅ FIXED → "điều gì" HUYEN |
| PV-04 | R86 EOL NGA "cũ" L7 (em-introduced PV-01 fix) | HIGH | em PV-01 retry | ✅ FIXED → "thành phố" SAC |

**Total pre-render gate catches:** 4 EOL violations, all FIXED before render.

### Render-time bugs

(To be filled when render completes)

### Mix-time bugs

(To be filled when mix v200 builds)

### Voice QA catalog (detect-only per R195)

(To be filled when 5 voice QA tools run on v200)

### Audio metrics violations

(To be filled when audio_pre_ship_gate runs)

---

## Process gap identified

**Em's text gate did NOT include qa_eol_diacritic.py** — relied only on audit_tilde_eol.py (NGA-only).

**Fix:** Add qa_eol_diacritic to Phase 0 text gate routine. Run automatically after every text edit.

**Status:** Pending integration into tools/svhmp_preflight_qa.py.

---

## NOT VERIFIED items

- Render success per section (6)
- Mix v200 success
- 5 voice QA detect catalogs
- audio_pre_ship_gate verdict
- Cross-section voice consistency
- Music coverage v200 duration
- LUFS/Peak/clip count
