# PACK 2 — 05_decision_matrix.md
> Enforce: `tools/auditor.py` `decide()` · chứng thực: test R209.

**Purpose:** Chuẩn hoá verdict SHIP/BLOCK_SHIP — mọi quyết định ship do MÁY, không do Builder.
**Scope:** Mọi milestone/commit chạy qua `auditor.py`; KHÔNG phán nội dung sáng tạo.
**Responsibilities:** Enforcer `auditor.py decide()` · Certify `test R209` · Approver tranh chấp = LEAD (R1) · Builder nộp evidence, cấm tự PASS.
**Mandatory Rules · PASS Criteria · FAIL Criteria · Examples:** xem bảng dưới (SHIP=all auditor PASS; BLOCK=≥1 FAIL / fail-safe).
**Promotion Rules:** reconcile theo `governance/constitution/00_constitution.md` (`draft→candidate→locked→deprecated`) — KHÔNG nhân đôi.

## PASS / FAIL Matrix (mọi verdict do MÁY, không do Builder)
| Điều kiện | Verdict | Exit |
|---|---|---|
| Tất cả Auditor PASS | **SHIP** | 0 |
| ≥1 Auditor FAIL | **BLOCK_SHIP** | 1 |
| KHÔNG có Auditor nào chạy | **BLOCK_SHIP** (fail-safe) | 1 |

## Escalation
`BLOCK_SHIP` → trả Builder fix → chạy lại `auditor.py`. Nếu tranh chấp rule/kiến trúc → **LEAD (Mr.Long) R1** quyết (Builder không được override).

## Reconcile
Không thay R196 (Engineering PASS ≠ Production): SHIP ở đây = qua gate máy; production còn cần R197 FULL_TEXT_GATE.
