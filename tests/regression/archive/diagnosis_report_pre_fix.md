# DIAGNOSIS REPORT — PRE-FIX SNAPSHOT (2026-06-30 02:25)
Reconstructed from session log + memory after current report overwrote.

## Context
- 100 regression samples × 8 QA tools = 800 runs
- Total elapsed: 70s
- 5/8 rules FAILED KPI before fixes

## Pre-fix Results
| Rule | TP | TN | FP | FN | FP% | FN% | Verdict |
|---|---|---|---|---|---|---|---|
| R86 | 6 | 25 | 25 | 1 | 50.0% | 14.3% | FAIL |
| R92b | 0 | 50 | 0 | 0 | 0% | 0% | PASS |
| R110 | 0 | 50 | 0 | 4 | 0% | 100% | FAIL |
| R111 | 6 | 50 | 0 | 1 | 0% | 14.3% | PASS (borderline) |
| R113 | 0 | 50 | 0 | 7 | 0% | 100% | FAIL |
| R117 | 3 | 50 | 0 | 0 | 0% | 0% | PASS |
| R128 | 0 | 50 | 0 | 7 | 0% | 100% | FAIL |
| R141 | 2 | 50 | 0 | 1 | 0% | 33.3% | FAIL |

## Pre-fix Issues identified

### R110 — 4 MISSED samples
| Sample | Injected keywords (in raw) | Survived cut_metadata | Tool result |
|---|---|---|---|
| neg_007_R110_001.md | tay vẫn ôm, siết chặt | YES | MISSED |
| neg_008_R110_002.md | tay vẫn ôm, siết chặt, không hề cúi xuống nhặt | YES | MISSED |
| neg_009_R110_003.md | tay vẫn ôm, siết chặt | YES | MISSED |
| neg_010_R110_004.md | siết chặt | YES | MISSED |

State trace example (neg_007_R110_001):
- L387 DROPPED: Một giọt nước rơi xuống mặt đồng hồ
- L405 DROPPED: chiếc đồng hồ ... trượt khỏi lòng tay
- L407 PICKED_UP: Anh không buồn nhặt nó lên (FALSE positive — negation not detected)
- L449 HOLDING: Anh gật, tay vẫn ôm chiếc đồng hồ (the INJECT)
- L473 PICKED_UP: Cô gái nhặt
- L477 HOLDING: Cô siết chặt

Tool checks `state == HOLDING and last_state == DROPPED`. At L449, last_state was PICKED_UP (from L407 FALSE) — so no flag.

### R86 — 25 FALSE POSITIVES on positive samples
Investigation: 4-5 positive samples (pos_005-009) flagged R86 violation.
- pos_005: "khoan thai" → "thong thả" — "thả" hỏi EOL = REAL R86 violation
- pos_006-009: "nhẹ nhàng" → "khe khẽ" — "khẽ" ngã EOL = REAL R86 violation

Root cause: positive variant generator introduces R86 violations unknowingly.

### R141 — 1 missed sample (R141_001)
- Injected: `replace("Hắc Dạ Ký", "Hắc Vỹ Dạ")` + `replace("Hắc, Dạ, Ký", "Hắc, Vỹ, Dạ")`
- After replace: "Hắc Vỹ Dạ" in text, "Hắc Dạ Ký" not in text
- qa_ssot_diff did NOT check brand drift forbidden list — missed.

### R113 + R128 (previously appeared as 100% FN)
These were caused by INJECT AT END of golden text — cut_metadata stripped them. Sample bug, not tool bug.
Fixed by adding `inject_before_metadata()` helper that inserts before next ## section after HOOK.
