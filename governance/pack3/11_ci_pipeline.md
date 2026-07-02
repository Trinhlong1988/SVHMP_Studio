# PACK 3 — 11_ci_pipeline.md — CI Pipeline
> Enforce: `tools/ci_gate.py` (client-side) + `.github/workflows/ci.yml` (server-side) · chứng thực: `tests/test_ci_suite.py` + pytest.

**Mission:** Bảo đảm KHÔNG commit/push nào lọt mà chưa qua chuỗi gate máy — chống regression + báo cáo láo.
**Purpose:** Định nghĩa các stage CI tuần tự + verdict PASS/FAIL.
**Scope:** Mọi commit/push local chạy qua `ci_gate.py`. KHÔNG gồm content-QA render-time (`svhmp_preflight_qa`).
**Authority:** Phái sinh từ PACK1 Constitution (`constitution/00`) + registry R211; doc không tự tạo quyền.
**Responsibilities:** Enforcer `tools/ci_gate.py` · Certify `tests/test_ci_suite.py` · re-entrancy guard env `SVHMP_CI_GATE_PYTEST_RUNNING` (chống fork-bomb).
**Workflow:** registry → R199/203/205/206/207/208 → pytest_suite → verdict (fail 1 stage = BLOCK, exit 1).
**Mandatory Rules:** chuỗi stage gate máy (bảng dưới) — mọi commit/push qua `ci_gate.py`, fail 1 stage = BLOCK.
**PASS Criteria:** mọi stage exit 0 → CI GATE PASS.
**FAIL Criteria:** 1 stage exit ≠ 0 → CI GATE FAIL, exit 1.
**Examples:** registry UNMAPPED > 0 → BLOCK; 1 test đỏ → BLOCK.
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Stage gate (máy sinh)
| # | Stage | Tool | FAIL → |
|---|---|---|---|
| 1 | registry | `architecture_registry_check.py` | BLOCK nếu MISSING/DUP/UNMAPPED > 0 |
| 2 | R199/203/205/206/207/208 | test script (subprocess exit) | BLOCK |
| 3 | pytest_suite | `pytest tests/` | BLOCK nếu 1 test đỏ |

## Server-side CI (chống hook-inert)
Git hook client-side có thể INERT (hooksPath rỗng / MinGit / máy chưa bootstrap) → từng để commit hỏng lọt lên origin. **`.github/workflows/ci.yml`** chạy `ci_gate.py` trên GitHub mỗi `push`/`pull_request` vào `main` — **cưỡng chế BẤT KỂ trạng thái hook của từng máy**. Đây là chốt gate không phụ thuộc client. (CD/deploy tự động: chưa có — thuộc pack sau.)

## Reconcile
Không thay `09_review_workflow` — `ci_gate` = chặng QA Auditor trong chuỗi đó. Re-entrancy guard chống đệ quy R213→auditor→ci_gate→pytest (fork-bomb). KHÔNG nhân đôi luật gate của hook (12) — hook chỉ chạy cùng gate sớm hơn.
