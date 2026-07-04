# RULE ID DUP AUDIT — bible/00_constitution.yaml (4/7/2026, kiểm duyệt độc lập)
> Phát hiện khi audit sync/BP7 (không liên quan xây dựng BP7). Root cause: `check_rule_id_free.py`
> --all/--staged CHỈ đếm format `top_level`/`list_id` là "definition" — bỏ sót quy ước
> `rule_R{N}_xxx:` (76/123 rule dùng dạng này). Đã fix tool (+5 test hành vi, không hard-code
> số lượng dup hiện tại vì sẽ đổi khi Mr.Long sửa nội dung). **Bible KHÔNG bị em sửa** (writer=mr_long).

## PHÂN LOẠI 3 LỚP (mức nghiêm trọng khác nhau — đừng gộp)

### 🔴 LỚP 1 — DUP-KEY THẬT (yaml.safe_load ÂM THẦM MẤT DỮ LIỆU) — 2 case
Cùng 1 literal key lặp lại 2 lần → mọi tool đọc bằng `yaml.safe_load` thường chỉ thấy bản SAU,
bản ĐẦU biến mất vô hình, không log lỗi.

| Rule | Dòng | Bản 1 (MẤT) | Bản 2 (còn sống) |
|---|---|---|---|
| **R142_kill_switch** (đã biết, CMD_BUILD báo khi audit BP7) | 2007 / 2034 | "Lỗi nặng (timeline/reveal sớm/fact mâu thuẫn) → QUAY LẠI outline" (status TBD) | "Publish Score FAIL → ABORT pipeline" (status PARTIAL) |
| **R143_multi_pass_agent** (⚠️ MỚI PHÁT HIỆN — chưa ai từng báo) | 2012 / 2040 | "Tách Writer+Logic QA+Language QA+Emotion QA+Publisher" (status TBD) | "Separation of Concerns CMD_QA_LOGIC/LANGUAGE/AUDIO" (status PARTIAL) |

**Cần Mr.Long quyết định nội dung** (bible immutable, chỉ writer=mr_long sửa được):
tách 2 concern thành 2 rule ID riêng, hay giữ 1 rule gộp cả 2 ý (viết lại description hợp nhất)?

### 🟡 LỚP 2 — TRÙNG SỐ HIỆU, KHÁC KEY (không mất dữ liệu, nhưng 2 định nghĩa cạnh tranh 1 số)
| Rule | Dòng | Key 1 | Key 2 |
|---|---|---|---|
| **R141** | 2003 / 2028 | `rule_R141_diff_check` "Bản rewrite vs cũ" (status TBD — có vẻ STUB CŨ) | `rule_R141_ssot_diff_check` "Post-edit diff vs fact_db" (status BUILT, tool `qa_ssot_diff.py`) |

Nhận định (không khẳng định thay Mr.Long): giống stub cũ (2003) chưa xóa sau khi rule được xây
thật dưới tên khác (2028, đã BUILT). Đề xuất: xóa/deprecate bản TBD nếu đúng là tiền thân của bản BUILT.

### 🟢 LỚP 3 — COMPANION "codified_from_test" (nhiều khả năng CỐ Ý, thấp nhất mức khẩn)
5 rule có thêm 1 entry phụ dạng `R{N}_codified_from_test:` (30/6, "CMD LEAD bible_audit fill_stub"),
khác key, không mất dữ liệu — trông như sổ ghi xuất xứ (provenance) song song bản chính:

`R110_narrative_continuity · R111_tts_phonetic_safe · R113_action_verb_repeat ·
R117_fact_database · R128_anti_generic_ai` — mỗi cái có `rule_R{N}_xxx:` (định nghĩa chính)
+ `R{N}_codified_from_test:` (metadata: ngày codify, nguồn, why, test_evidence).

**Không tự phán là lỗi** — có thể là mẫu archival hợp lệ. Cần Mr.Long xác nhận: giữ nguyên (và dạy
tool nhận diện `_codified_from_test` là companion hợp lệ, không tính dup) hay dọn/sáp nhập vào rule chính.

## BẰNG CHỨNG MÁY (lệnh đã chạy, ref sạch `943b9b2`)
```
python tools/check_rule_id_free.py 142   -> [COLLISION] 2 hit  (đã biết)
python tools/check_rule_id_free.py 143   -> [COLLISION] 2 hit  (MỚI)
python tools/check_rule_id_free.py --all -> [FAIL] 8 duplicate(s): R110,R111,R113,R117,R128,R141,R142,R143
python -m pytest tests/test_check_rule_id_free_prefix.py -> 5 passed
```

## KHÔNG PHẢI LỖI CỦA BP7
Checker BP7 (loader single-impl chuẩn dự án) phát hiện R142 khi resolve `ENDING_RULES` — đúng
thiết kế, không phải bug BP7. Vấn đề nằm ở bible/00 + ở chính `check_rule_id_free.py` (đã fix).

## VIỆC CẦN MR.LONG (bible immutable — không phải việc máy tự quyết)
1. R142, R143: chọn 1 trong 2 nội dung mỗi rule, hoặc tách ID mới cho ý còn lại.
2. R141: xác nhận `rule_R141_diff_check` (2003) là stub cũ nên xóa/deprecate.
3. Nhóm companion (R110/111/113/117/128): giữ nguyên mẫu hay dọn — quyết định 1 lần áp cho cả nhóm.
4. Sau khi bible sửa xong: chạy lại `check_rule_id_free.py --all` phải về `[OK]` mới coi là đóng.
