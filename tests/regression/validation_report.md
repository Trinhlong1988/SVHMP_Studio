# VALIDATION REPORT — Regression Test 30/6 02:45
Source: tests/regression/{positive,negative}/*
Samples: 50 positive + 50 negative
QA tools: 8
Total runs: 100 samples × 8 tools = 800
Elapsed: 70s

## Per-Rule Results

| Rule | TP | TN | FP | FN | FP% | FN% | Detect% | Verdict |
|---|---|---|---|---|---|---|---|---|
| R86 | 6 | 50 | 0 | 1 | 0.0% | 14.3% | 85.7% | ✅ PASS |
| R92b | 0 | 50 | 0 | 0 | 0.0% | 0.0% | 100.0% | ✅ PASS |
| R110 | 4 | 50 | 0 | 0 | 0.0% | 0.0% | 100.0% | ✅ PASS |
| R111 | 6 | 50 | 0 | 1 | 0.0% | 14.3% | 85.7% | ✅ PASS |
| R113 | 7 | 50 | 0 | 0 | 0.0% | 0.0% | 100.0% | ✅ PASS |
| R117 | 3 | 50 | 0 | 0 | 0.0% | 0.0% | 100.0% | ✅ PASS |
| R128 | 7 | 50 | 0 | 0 | 0.0% | 0.0% | 100.0% | ✅ PASS |
| R141 | 3 | 50 | 0 | 0 | 0.0% | 0.0% | 100.0% | ✅ PASS |

## Overall: 🟢 ALL PASS

## KPI thresholds (Mr.Long lock)
- False Positive ≤ 10%
- False Negative ≤ 15%
- Detection Rate Logic ≥ 90%
