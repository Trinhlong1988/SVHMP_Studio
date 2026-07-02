# PACK 2 — 09_review_workflow.md
> Enforce: pipeline trong `tools/auditor.py`.

**Mission:** Bảo đảm review đi đúng tuần tự, không chặng nào bị bỏ qua (chống shortcut).
**Purpose:** Định nghĩa chuỗi review Builder→Auditor→Promotion 1 lệnh.
**Scope:** Mọi ship chạy qua `auditor.py`; mỗi chặng 1 tool.
**Authority:** Phái sinh từ PACK1 Constitution (`constitution/00`) + LEAD (Mr.Long R1); doc không tự tạo quyền.
**Responsibilities:** Enforcer `auditor.py` pipeline · fail bất kỳ chặng → trả Builder · Builder cấm tự PASS.
**Workflow:** Builder → Architecture → Contract → QA → Publish → SHIP (bảng dưới); fail 1 chặng = dừng.
**Mandatory Rules · PASS Criteria · FAIL Criteria · Examples:** xem dưới (PASS=mọi chặng PASS → SHIP; FAIL=1 chặng FAIL → dừng, trả Builder; ví dụ Architecture FAIL → không đi tiếp).
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Chuỗi review (1 lệnh `python tools/auditor.py`)
```
Builder → Architecture Auditor → Contract Auditor → QA Auditor → Publish Auditor → SHIP
```
| Chặng | Tool | FAIL → |
|---|---|---|
| Architecture | architecture_registry_check | trả Builder |
| Contract | artifact_contract_check | trả Builder |
| QA | ci_gate (R199–R209) | trả Builder |
| Publish | auditor artifact/version gate | trả Builder |

## Nguyên tắc
- Fail bất kỳ chặng → **dừng, trả Builder** (không đi tiếp).
- Builder **cấm tự PASS** — verdict do gate máy.
- Reconcile R7 Change-Gate: trước khi Builder code phải trả 6 câu (registry `change_request_gate`).
