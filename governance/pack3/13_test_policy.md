# PACK 3 — 13_test_policy.md — Test Policy
> Enforce: `tests/conftest.py` + `ci_gate.py` pytest_suite · chứng thực: pytest collect count.

**Mission:** Bảo đảm test THẬT được chạy — không bị glob nuốt thầm (G1: 43 test từng bị ẩn khỏi gate).
**Purpose:** Định nghĩa taxonomy test + luật collect + loại test bắt buộc.
**Scope:** Mọi test trong `tests/`. 2 loại: pytest-func (assert) vs script-style (subprocess exit).
**Authority:** Phái sinh từ PACK1 Constitution (`constitution/00`); doc không tự tạo quyền.
**Responsibilities:** Enforcer `conftest.collect_ignore` (EXACT-filename, KHÔNG glob) · Certify pytest collect count · Builder CẤM skip/xoá test đỏ.
**Workflow:** pytest-func → `pytest tests/` tự collect; script-style → CHECKS trong `ci_gate` (subprocess) + `collect_ignore` exact.
**Mandatory Rules · PASS Criteria · FAIL Criteria · Examples:** xem dưới (PASS=mỗi loại chạy đúng kênh, 0 test ẩn; FAIL=pytest-func bị glob ignore / test đỏ bị skip; ví dụ `test_voice_qa_tools` ignore vì FN F8 chưa calibrate — có lý do log).
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Loại test bắt buộc
- **Positive** (happy path) · **Negative** (empty/invalid → BLOCK) · **Regression** (chống tái diễn bug) · **Blocking** (gate FAIL đúng exit).
- **Wiring test** khi có nguy cơ "built≠wired" (ví dụ `test_gate_wired_g2` xfail→live).

## Reconcile
`collect_ignore` EXACT-filename (KHÔNG glob — glob từng nuốt 43 test, G1). Test đỏ CẤM skip/xoá để cho xanh (01_builder + 10_exception_policy). Re-entrancy guard cho pytest lồng trong `ci_gate` (11).
