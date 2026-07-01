# PACK 1 — 00_constitution.md
# SVHMP Enterprise Governance v1.0 (refined, tool-enforced)
> Status: candidate · Scope: Builder + 3 Independent Auditors · **Mỗi rule PHẢI có tool enforce + test chứng thực (Boss 2/7)**

## Mission
Định nghĩa luật quản trị cho mọi thay đổi repo — **enforced bằng tool máy chạy**, không phải prose.

## Core Principles (mỗi cái → tool + test)
| # | Principle | Enforce tool | Chứng thực |
|---|---|---|---|
| 1 | Repository integrity > delivery speed | `architecture_registry_check.py` | registry 0 MISSING/DUP/UNMAPPED |
| 2 | Architecture Registry = source of truth | `governance/architecture_registry.yaml` | R211 |
| 3 | Major change cần evidence khách quan | `auditor.py` (commit+matrix+exit) | R200/log_ping |
| 4 | **Verification ĐỘC LẬP với implementation** | `auditor.py` (máy phát verdict) | test R209 |
| 5 | Milestone xong CHỈ khi tất cả gate PASS | `ci_gate.py` + `auditor.py` | exit code |

## Authority (Authority Matrix — ai quyết cái gì)
| Cấp | Quyền | Reconcile |
|---|---|---|
| **LEAD (Mr.Long)** | Quyết kiến trúc/rule/promotion/freeze; duyệt exception | R1 (only authority) |
| **Independent Auditor** | Phát verdict SHIP/BLOCK_SHIP (máy); không sửa repo | R209 |
| **Builder (Claude)** | Thực thi trong phạm vi được duyệt | R_SUPREME |

## Roles & Forbidden Actions (tách vai — chống tự đánh giá)
- **Builder**: implement/refactor/add-test/update-doc. **FORBIDDEN: tự tuyên PASS · override auditor · giấu fail · nhân đôi module.**
- **Architecture Auditor** (đọc, không sửa): `architecture_registry_check.py`.
- **QA Auditor** (đọc, không sửa): `ci_gate.py` (R199/203/205/206/207/208/209…).
- **Publish Auditor** (quyết release): `auditor.py` publish gate.

## Responsibilities
Builder sinh code+test+evidence · Auditor xác minh độc lập + phát verdict · LEAD phê duyệt/đóng băng. Không ai kiêm cả build lẫn verdict.

## Workflow (Promotion Workflow — exit-code gated)
`Builder → Architecture Auditor → Contract Auditor → QA Auditor → Publish Auditor → Release`. Fail bất kỳ chặng → trả Builder. Chạy 1 lệnh: `python tools/auditor.py`.

## Evidence Requirements (Evidence Standard — BẮT BUỘC mọi report)
`Commit hash · Branch · Commands executed · PASS/FAIL matrix · Final verdict · Exit code`. Thiếu bất kỳ = report VÔ HIỆU (enforce `tools/evidence_check.py`).

## Severity
| Mức | Nghĩa | Ví dụ | Hành động |
|---|---|---|---|
| **Critical** | Chặn promotion | registry MISSING/DUP · test FAIL · phantom artifact · clip peak | BLOCK |
| **Major** | Fix sớm | onset-pop · cụt chữ · DoD thiếu manager/validator | fix trước ship |
| **Minor** | Nợ kỹ thuật | md_doc/sample_yaml thiếu | backlog |
| **Info** | Ghi nhận | waiver R77/R80 | log |

## PASS Criteria
Tất cả Auditor PASS → **SHIP** (exit 0). Enforce `auditor.decide()`.

## FAIL Criteria
≥1 Auditor FAIL, hoặc không có auditor nào chạy → **BLOCK_SHIP** (exit 1). Critical > 0 → FAIL.

## Exit Codes (chuẩn hoá toàn dự án)
`0 SUCCESS/SHIP · 1 FAIL/BLOCK_SHIP · 2 BLOCKED (thiếu input)`.

## Promotion Rules
`draft → candidate → locked → deprecated`. Chỉ `locked` được Generator dùng. Freeze v1.0 = tất cả 14 phase FREEZE GATE PASS + LEAD duyệt. Reconcile: bible lock_date + git backup (R8).

## Reconcile (KHÔNG nhân đôi hiến pháp cũ)
Builder-role=R_SUPREME R1 · Change-Gate=R7 · Audit-log=R200+log_ping · Promotion=bible lock · Registry=R211.
