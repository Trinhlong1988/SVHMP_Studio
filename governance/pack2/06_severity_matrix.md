# PACK 2 — 06_severity_matrix.md
> Chuẩn hoá 4 mức (dùng chung QA + Architecture). Enforce: gate exit code.

**Purpose:** Chuẩn hoá 4 mức severity để phân loại finding → có/không chặn promotion.
**Scope:** Mọi QA + Architecture finding; map QA code → severity trong từng validator.
**Responsibilities:** Enforcer `tools/severity_gate.py` · Certify `test R214` · Approver hạ mức = LEAD (R1).
**Mandatory Rules · PASS Criteria · FAIL Criteria · Examples:** xem bảng dưới (cột "Ví dụ SVHMP"; PASS=Major/Minor/Info không chặn, FAIL=Critical BLOCK).
**Promotion Rules:** reconcile theo `governance/constitution/00_constitution.md` (`draft→candidate→locked→deprecated`) — KHÔNG nhân đôi.

| Mức | Định nghĩa | Ví dụ SVHMP | Gate |
|---|---|---|---|
| **Critical** | Sai/vỡ, chặn promotion | registry MISSING/DUP/UNMAPPED>0 · test FAIL · phantom artifact · clip peak thật | **BLOCK** (exit 1) |
| **Major** | Lỗi phải fix sớm | onset-pop ≥0.13 · cụt chữ · hụt hơi · DoD thiếu manager/validator | fix trước SHIP |
| **Minor** | Nợ kỹ thuật | md_doc/sample_yaml thiếu · file cần archive | backlog, không chặn |
| **Info** | Ghi nhận | waiver R77 nghỉ intro · R80.peak advisory (-1.4dB) | log |

## Quy tắc
Chỉ **Critical** làm auditor `BLOCK_SHIP`. Major/Minor/Info = report, không tự chặn (tránh spam chặn). Map QA code → severity trong từng validator.
