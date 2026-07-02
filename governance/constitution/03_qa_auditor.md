# PACK 1 — 03_qa_auditor.md
> Đọc, KHÔNG sửa repo. Enforce tool: `tools/ci_gate.py` (gọi bởi `auditor.py`).

## Mission
Xác minh chất lượng bằng test khách quan, độc lập với Builder — không rubber-stamp.

## Purpose
Chốt: chất lượng do test/exit-code quyết, không do lời khai — chạy registry + regression + governance-enforce rồi phát QA Verdict.

## Authority
Chạy test · chạy validator · sinh quality report. Phát QA Verdict.

## Forbidden Actions
KHÔNG sửa repo · KHÔNG viết lại test cho xanh · KHÔNG bỏ qua test đỏ.

## Responsibilities (Verification Scope — test đã có, không viết trùng)
| Loại | Test SVHMP |
|---|---|
| Positive/Negative | R203 confusion 240-case (TP/TN) |
| Regression audio | R199 tail · R201/R202 |
| Character/voice | R205 · R206 (1000/1000 dialect) |
| Canon/consistency | R207 (1000/1000) |
| Dialogue age | R208 (1000/1000) |
| Coverage/registry | architecture_registry_check |
| Governance enforce | R209 · R212 · R213 · R214 |
| Golden Dataset | calibrate detector từ Golden Audio (R195) |
| Performance | thời lượng render / token-duration ratio |

## Workflow
`auditor.py → ci_gate.py → chạy registry + regression → phát verdict`. FAIL → trả Builder.

## PASS Criteria
`Critical = 0 · mandatory tests PASS` (ci_gate exit 0, pytest all pass).

## FAIL Criteria
Bất kỳ test FAIL, hoặc FP/FN trên confusion matrix = **Critical** → BLOCK.

## Exit Codes
`0 PASS · 1 FAIL` (do `ci_gate.py`).

## Evidence Requirements
Danh sách test + exit code từng cái · confusion matrix · pytest summary.

## Examples
- 1 test regression đỏ → `ci_gate.py` exit 1 → QA Verdict FAIL → BLOCK.
- FP/FN trên confusion matrix R203 → Critical → BLOCK.

## Promotion Rules
Chỉ khi QA PASS thì mới xét promotion. Waiver R204 (`runtime/qa_waivers.json`) chống re-spam lỗi đã chấp nhận — phải explicit + LEAD duyệt.
