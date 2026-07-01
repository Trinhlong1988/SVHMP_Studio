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

## Roles (tách vai — chống tự đánh giá)
- **Builder** (Claude): implement/refactor/add-test/update-doc. **FORBIDDEN: tự tuyên PASS · override auditor · giấu fail.** → cưỡng chế: verdict chỉ do `auditor.py` phát.
- **Architecture Auditor** (đọc, không sửa): `architecture_registry_check.py`.
- **QA Auditor** (đọc, không sửa): `ci_gate.py` (registry + regression R199/203/205/206/207/208).
- **Publish Auditor** (quyết release): `auditor.py` publish gate (artifact/version).

## Evidence Standard (BẮT BUỘC mọi report — = output `auditor.py`)
`Commit hash · Branch · Commands executed · PASS/FAIL matrix · Final verdict · Exit code`. Thiếu bất kỳ = report VÔ HIỆU.

## Severity (map QA hiện có)
| Mức | Nghĩa | Ví dụ SVHMP | Hành động |
|---|---|---|---|
| **Critical** | Chặn promotion | registry MISSING/DUP, test FAIL, R80.peak clip thật | BLOCK |
| **Major** | Phải fix sớm | onset-pop, cụt chữ, DoD thiếu manager/validator | fix trước ship |
| **Minor** | Nợ kỹ thuật | UNMAPPED file, md_doc thiếu | backlog |
| **Info** | Ghi nhận | waiver R77 nghỉ intro, R80 advisory | log |

## Promotion Workflow (exit-code gated)
`Builder → Architecture Auditor → QA Auditor → Publish Auditor → Release`. Fail ở bất kỳ chặng → trả Builder. Chuỗi này chạy 1 lệnh: `python tools/auditor.py` (SHIP=0 / BLOCK_SHIP=1).

## Exit Codes (chuẩn hoá toàn dự án)
`0 SUCCESS/SHIP · 1 FAIL/BLOCK_SHIP · 2 BLOCKED (thiếu input)`.

## Reconcile (KHÔNG nhân đôi hiến pháp cũ)
Builder-role=R_SUPREME R1 · Change-Gate=R7 · Audit-log=R200+log_ping · Promotion=bible lock · Registry=R211. PACK1 chỉ **bổ sung tách Auditor + Evidence template + Severity 4 mức + Publish gate** (những gap R-rule chưa có).
