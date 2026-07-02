# PACK 3 — 14_release_gate.md — Release / Promotion Gate
> Enforce: `tools/auditor.py` + `constitution/05_builder_hard_gate.md` · chứng thực: `tests/test_builder_hard_gate.py`.

**Mission:** Bảo đảm FREEZE/release chỉ do **independent auditor** — Builder KHÔNG tự ký.
**Purpose:** Định nghĩa gate chuyển `promotion_status: candidate→locked` + tạo release tag.
**Scope:** Promotion mọi pack/domain + release tag. KHÔNG gồm commit thường (đó là 11/12).
**Authority:** Independent auditor / LEAD (R1); Builder chỉ ĐỀ XUẤT (`05_builder_hard_gate`).
**Responsibilities:** Enforcer `auditor.py` (SHIP/BLOCK) + hard-gate 05 · Certify `test_builder_hard_gate.py` · Builder CẤM tự `locked`/tag.
**Workflow:** Builder `READY_FOR_AUDIT=YES` → independent auditor chạy freeze-gate 16-phase → SHIP → LEAD (R1) ký → `promotion_status→locked` + tag.
**Mandatory Rules:** release gate 3 bước (bảng dưới) — freeze do independent auditor + LEAD.
**PASS Criteria:** independent auditor SHIP + LEAD duyệt.
**FAIL Criteria:** Builder tự freeze/tag → vi phạm 05.
**Examples:** PACK2 v1.0 = ngoại lệ LEAD-ratified một lần.
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Release gate (3 bước)
| Bước | Ai | Điều kiện |
|---|---|---|
| Đề xuất | Builder | `READY_FOR_AUDIT=YES` + Evidence Contract đủ (07) |
| Audit | **Independent** auditor | freeze-gate 16-phase PASS + `auditor.py` SHIP |
| Freeze | LEAD (R1) | ký → `promotion_status locked` + release tag |

## Reconcile
Ghép `05_builder_hard_gate` (Builder cấm tự freeze/tag) + `09_review_workflow` (chuỗi auditor) + `00` Promotion Rules — KHÔNG nhân đôi, doc này chỉ định nghĩa release gate từ 3 nguồn đó.
