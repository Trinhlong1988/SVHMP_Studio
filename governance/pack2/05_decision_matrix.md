# PACK 2 — 05_decision_matrix.md
> Enforce: `tools/auditor.py` `decide()` · chứng thực: test R209.

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
