# PACK 2 — 06_severity_matrix.md
> Chuẩn hoá 4 mức (dùng chung QA + Architecture). Enforce: gate exit code.

| Mức | Định nghĩa | Ví dụ SVHMP | Gate |
|---|---|---|---|
| **Critical** | Sai/vỡ, chặn promotion | registry MISSING/DUP/UNMAPPED>0 · test FAIL · phantom artifact · clip peak thật | **BLOCK** (exit 1) |
| **Major** | Lỗi phải fix sớm | onset-pop ≥0.13 · cụt chữ · hụt hơi · DoD thiếu manager/validator | fix trước SHIP |
| **Minor** | Nợ kỹ thuật | md_doc/sample_yaml thiếu · file cần archive | backlog, không chặn |
| **Info** | Ghi nhận | waiver R77 nghỉ intro · R80.peak advisory (-1.4dB) | log |

## Quy tắc
Chỉ **Critical** làm auditor `BLOCK_SHIP`. Major/Minor/Info = report, không tự chặn (tránh spam chặn). Map QA code → severity trong từng validator.
