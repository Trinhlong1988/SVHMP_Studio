# PACK 2 — 10_exception_policy.md
> Enforce: `runtime/qa_waivers.json` (opt-in) + R204 + Change-Gate R7.

**Mission:** Bảo đảm mọi ngoại lệ có phê duyệt tường minh — không giấu lỗi dưới danh nghĩa waiver.
**Purpose:** Quy định khi nào được override/waiver + cơ chế duyệt.
**Scope:** Waiver QA finding + sửa file `locked`/rule/kiến trúc.
**Authority:** Approver tối cao = LEAD/Mr.Long (R1); phái sinh từ PACK1 Constitution (`constitution/00`) + Change-Gate R7.
**Responsibilities:** Approver = LEAD/Mr.Long (R1) · Enforcer `qa_waivers.json` (R204) + Change-Gate R7 · Builder cấm skip/xoá test đỏ.
**Workflow:** Cần override → Change-Gate R7 (Read→Diff→Proposal→Approval→Backup→Patch→Regression) trước khi patch.
**Mandatory Rules · PASS Criteria · FAIL Criteria · Examples:** xem dưới (PASS=waiver explicit+approved+log; FAIL=waiver ngầm / skip test đỏ CẤM; ví dụ R77/R80 waiver opt-in).
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Khi nào được override (exception)
Chỉ khi lỗi đã **được phân tích + chấp nhận có chủ đích** (không phải giấu lỗi):
| Exception | Cơ chế | Ai duyệt |
|---|---|---|
| QA finding đã chấp nhận (vd R77 nghỉ intro, R80 advisory) | `qa_waivers.json` opt-in (R204) — chống re-spam | LEAD |
| Sửa file `locked` / rule / kiến trúc | Change-Gate R7 (Read→Diff→Proposal→**Approval**→Backup→Patch→Regression) | **Mr.Long/LEAD (R1)** |
| Skip test tạm | CẤM — không được xoá/skip test đỏ để cho xanh (01_builder) | không ai |

## Nguyên tắc
- Waiver phải **explicit + có lý do + log**; không waiver ngầm.
- Exception KHÔNG hạ Critical → vẫn phải fix hoặc có phê duyệt LEAD ghi rõ.
- Mọi override → `log_ping` + commit (R200 audit trail).
