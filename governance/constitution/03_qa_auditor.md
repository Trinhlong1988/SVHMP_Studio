# PACK 1 — 03_qa_auditor.md
> Đọc, KHÔNG sửa repo. Enforce tool: `tools/ci_gate.py` (gọi bởi `auditor.py`).

## Verification Scope (test đã có — không viết trùng)
| Loại | Test SVHMP |
|---|---|
| Regression audio | R199 tail · R203 confusion 240-case |
| Character/voice | R205 · R206 (1000/1000 dialect) |
| Canon/consistency | R207 (1000/1000) |
| Dialogue age | R208 (1000/1000) |
| Registry | architecture_registry_check |
| Governance enforce | **R209** (auditor BLOCK khi fail) |

## PASS Criteria (exit 0)
`Critical = 0 · mandatory tests PASS`. Test FAIL = **Critical** → BLOCK.

## Golden calibration
Detector hiệu chỉnh từ Golden Audio (R195) — FP/FN = 0 trên confusion matrix (chống spam báo lỗi giả). Waiver R204 chặn re-spam lỗi đã chấp nhận.
