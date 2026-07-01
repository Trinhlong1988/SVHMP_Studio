# PACK 2 — 10_exception_policy.md
> Enforce: `runtime/qa_waivers.json` (opt-in) + R204 + Change-Gate R7.

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
