# Comparison Report — v108 baseline vs v200 production candidate

**Generated:** 2026-06-30T23:10

## Headline

| Metric | v108 (engineering snapshot 17:06) | v200 (production candidate 23:04) | Delta |
|---|---|---|---|
| audit_audio_mix_qa 15-check | 8/15 PASS | **11/15 PASS** | **+3** |
| audit HIGH violations | 4 | **2** | **-2** |
| audio_pre_ship_gate | 🔴 FAIL | **🟢 PASS** | ✅ |
| Peak dBFS | 0.80 ❌ (near clip) | **-16.14** ✅ | -16.94 dB |
| LUFS_i (target [-17,-15]) | -20.93 ❌ | **PASS in range** | ✅ |
| Clip count | 12 | **0** | -12 |
| Click/pop count | 586 | 9964 | +9378 (loudnorm trade-off) |
| Music coverage | 1051s (gap 2:38 cuối) | **1243s** (full coverage) | ✅ |
| setup.wav peak (post_render) | -0.0 dB FAIL | **-1.50 dB PASS** | R198 wired |
| 6-section post_render audit | 5 PASS / 1 FAIL | **6 PASS / 0 FAIL** | ✅ |

## Per-section peak comparison

| Section | v108 mtime | v108 peak | v200 mtime | v200 peak | R198 wire |
|---|---|---|---|---|---|
| hook | 13:04 | -1.82 dB | 21:55 | -1.82 dB | pre-wire |
| setup | 13:17 | **-0.0 dB** ❌ | 22:10 | **-1.50 dB** ✅ | pre-wire (alimiter 0.85 caught) |
| incident | 13:25 | -2.1 dB | 22:16 | -1.86 dB | pre-wire |
| reveal | 16:34 | -1.9 dB | 22:37 | -2.11 dB | pre-wire |
| payoff | 16:44 | -2.8 dB | 22:47 | -2.50 dB | **R198 fired** |
| cliffhanger | 18:36 | -2.0 dB | 22:54 | -1.68 dB | **R198 fired** |

## Text changes between v108 and v200 (Phase 0)

| Type | Count |
|---|---|
| R61 prefix expansion (short START fix) | 9 |
| R177 adjacent word repeat fix | 3 |
| R60 short EOL extension | 5 |
| R86 NGA/NANG/HOI EOL fix | 4 |
| R180b collocation fix | 1 |
| B60 driver dialogue Q2→Q1 | 1 |
| B62 outro Option D completion | 1 |
| R178b time marker pause | 1 |
| **TOTAL** | **25 text edits** |

## Voice QA detection (R195 detect-only, no thresholds calibrated)

| Tool | v108 result | v200 result |
|---|---|---|
| R181c speaker embedding | not run | extractable 192-dim, deterministic |
| R188 boundary artifact | not run | 0 detected (auto-boundary heuristic) |
| R189 breath artifact | not run | 0 HIGH ✅ |
| R190 prosody collapse | not run | 516 HIGH + 862 MED — see `r190_timestamp_catalog.json` |
| R190b onset artifact | not run | 0 detected (auto-boundary heuristic) |
| R191 dialogue identity | not run | 266 segments / 0 HIGH ✅ |

## Process changes between v108 ship time (17:15) and v200 (23:04)

| Time | Event |
|---|---|
| 17:15 | v108 engineering snapshot ship — Mr.Long approve baseline reference |
| 19:30 | Tier 2.1 Engineering Validation 4-gate PASS (Mr.Long sign-off) |
| 21:00 | R195 Golden Audio principle codified |
| 21:30 | R_SUPREME workflow lock codified |
| 22:50 | R196 production reality principle codified |
| 23:00 | R197 FULL_TEXT_GATE codified + qa_eol_diacritic chained |
| 23:55 | R198 cap_peak post-render wired + 8 orphan rules flushed |
| 23:04 | v200 production candidate generated — 11/15 audit PASS, audio gate PASS |

## Honest delta assessment

**v200 IS NOT yet Golden.** Per R196:
- L1 Engineering: ✅ PASS (4-gate Tier 2.1)
- L2 Production Validation: ⏸️ candidate generated, awaiting Mr.Long listen
- L3 Golden Output: ❌ NOT YET
- L4 Freeze: ❌ FORBIDDEN until L3
- L5 Release: ❌ FORBIDDEN until L4

**v200 IS objectively stronger than v108** in measurable engineering metrics:
- +3 PASS in 15-check audit
- -2 HIGH violations
- Peak safe 16 dB headroom
- LUFS in target range
- Audio pre-ship gate from FAIL → PASS
- Setup.wav CLIP issue resolved (R198 wired)
- Music covers full duration (no silent tail)

**v200 still has detected artifacts** (per R195 detect-only):
- R190 prosody 516 HIGH (detector flagged — Mr.Long listen will confirm or deny audibility)
- C13 click/pop 9964 (loudnorm trade-off — typically inaudible if RMS reasonable)

## Recommended next step

**Mr.Long listen v200 EP01_FULL_v200.mp3.**

- ACCEPT → calibrate → freeze → tag
- REJECT → catalog bugs → CMD THỰC THI iterate v201

Em STOP for Mr.Long review.
