# PACK 2 — 09_review_workflow.md
> Enforce: pipeline trong `tools/auditor.py`.

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
