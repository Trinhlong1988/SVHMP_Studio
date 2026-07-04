# CMD AUDIT — PHỤ LỤC RIÊNG G4 (World/Timeline/Event) + G5 (Supernatural)

> KHÔNG thay thế `CMD_AUDIT_PROTOCOL.md` (7 bước chung — vẫn bắt buộc chạy đủ, không rút gọn).
> File này là checkpoint BỔ SUNG, ánh xạ trực tiếp rủi ro đã lường trước khi build (viết TRƯỚC
> khi CMD_BUILD/CMD_BUILD_3 nộp báo cáo — kiểm duyệt không tự chế tiêu chí SAU khi thấy kết quả,
> tránh thiên vị xác nhận). Nguồn rủi ro: đọc trực tiếp `TASK_G4_WORLD.md` / `TASK_G5_SUPERNATURAL.md`
> + lịch sử lỗi dự án (memory lessons + docs/ENVIRONMENT_GOTCHAS.md G1-G12).

## THỨ TỰ CHẠY (bắt buộc, không đảo)
1. `CMD_AUDIT_PROTOCOL.md` đủ 7 bước (B0-B7) trên worktree sạch từ origin/main.
2. Bảng checkpoint domain-specific dưới đây — MỌI dòng phải có verdict, không bỏ sót.
3. Tổng hợp theo QUY TẮC PHÂN ĐỊNH — 1 FAIL ở nhóm "an toàn/R211" = bác toàn bộ pack, không có
   "PASS có điều kiện" cho nhóm này (khác PASS-với-điều-kiện thông thường ở B-verdict chung).

## QUY TẮC PHÂN ĐỊNH 100-ĐÚNG / 100-SAI (không có mức giữa "có vẻ", "chắc là")
- **100% ĐÚNG**: có lệnh máy chạy thật + exit code + đối chiếu dòng code/dữ liệu cụ thể xác nhận
  đúng claim, VÀ đã thử bắn mutation ngược mà không lọt.
- **100% SAI**: có ≥1 bằng chứng cụ thể (dòng code/exit-code/diff) mâu thuẫn trực tiếp với claim.
  Dù chỉ 1 điểm sai, toàn bộ checkpoint đó bị bác — không cộng điểm trung bình.
- **CHƯA ĐỦ BẰNG CHỨNG**: khi thiếu công cụ đo/quyền truy cập để kết luận — PHẢI ghi rõ thiếu gì,
  KHÔNG được mặc định quy về PASS.
- Nhóm **an toàn pháp lý + R211** (G5-1, G5-2) và nhóm **named-vs-enforced** (G4-1) KHÔNG có mức
  "tạm chấp nhận" — đây là 2 lớp lỗi đã tái diễn nhiều lần nhất trong lịch sử dự án này.

## BẢNG RỦI RO ĐÃ BIẾT ← BÀI HỌC LỊCH SỬ (viết trước khi có kết quả build)

| # | Rủi ro cụ thể | Bài học lịch sử áp dụng | Cách kiểm — tiêu chí 100đ/100s |
|---|---|---|---|
| G4-1 | `R84_temporal_anchor_for_events` "đóng nợ" giả — tool tồn tại nhưng không thật sự chặn được vi phạm | lesson-enforcer-claim-vs-behavior (named≠enforced, ca pack4) | Tự viết 2 tập test có mốc thời gian mâu thuẫn cố ý (2 chunk nói khác nhau về "bao nhiêu năm trước") → chạy `tools/timeline_check.py` → PHẢI thấy FAIL. Không FAIL dù tool "tồn tại và exit 0" = 100% SAI |
| G4-2 | Số hiệu "R84" đụng thêm 1 nghĩa thứ 3 (đã phát hiện: `pre_render_audit.py` có "R84" khác nghĩa, không liên quan) | Phát hiện mới trong phiên audit trước-build (2026-07-04/05) — bug-class tương tự R141/142/143 dup-key ở bible/00 nhưng khác namespace | `grep -rn "R84" tools/` sau khi G4 build xong — mọi hit MỚI phải trỏ đúng `temporal_anchor_for_events`; nếu code mới tự thêm 1 "R84" khác nữa (nghĩa thứ 3) = 100% SAI (làm rối thêm thay vì dọn) |
| G4-3 | `event_ledger_miner.py` tạo khung rỗng — chạy được nhưng 0 dữ liệu thật, vẫn báo "DONE" | lesson-dont-downplay-rigor (cấm "xong" chỉ vì máy PASS rỗng) | Đếm dòng thật trong `runtime/event_ledger_draft.yaml` sau khi miner chạy trên 50 tập thật — phải >0 VÀ mọi dòng có `evidence: ep:line` cụ thể. 1 dòng thiếu evidence = 100% SAI dòng đó (không phải cả file, ghi rõ tỉ lệ) |
| G4-4 | `bible/fact_ledger_schema.yaml` sửa/tạo trực tiếp trong `bible/` thay vì qua `governance/blueprint/schemas/proposals/` | lesson-lock-ceremony-and-regen (bible writer=mr_long, immutable, cần "per Mr.Long authorization" tường minh trong commit) | `git log --follow <path>` — file mới PHẢI nằm ở `proposals/`; nếu commit trực tiếp vào `bible/*.yaml` mà message KHÔNG có cụm "per Mr.Long authorization" = 100% SAI, bất kể nội dung đúng |
| G4-5 | D4 (continuity mở rộng 2 field-lock mới) viết engine riêng thay vì mở rộng `story_consistency_validator.py`/R207 có sẵn | R211 cấm nhân đôi | Đọc diff `tools/story_consistency_validator.py` — 2 field-lock mới (sự kiện/đồ vật) PHẢI nằm trong file này (mở rộng `LOCKED_FIELDS` hoặc tương đương), KHÔNG có file `*_continuity_v2.py` song song mới |
| G5-1 | **D4 gốc (compliance_gate) bị build lại trùng BP9 — RỦI RO CAO NHẤT đã cảnh báo sẵn trong `TASK_G5_SUPERNATURAL.md` mục "⚠️ PHẢN BIỆN QUAN TRỌNG"** | R211; phát hiện chính của phiên audit trước-khi-build (đọc nguyên văn `bp9/content_policy.yaml` + `bp9/policy_gates.yaml` xác nhận HB01/HB02 + sensitivity_tiers đã có) | `git diff` toàn bộ commit G5 — tìm file MỚI tên `content_policy.yaml` (ngoài bp9 đã có) hoặc `compliance_check.py`/`publish_gate.py` (đây là việc của G8, không phải G5). CÓ file này = **100% SAI, BÁC THẲNG không cần xét tiếp các checkpoint khác của G5**. KHÔNG CÓ + có `reports/G5_HANDOFF_G8.md` ghi rõ danh sách sensitivity=high cần G8 quét = 100% ĐÚNG |
| G5-2 | `sensitivity` field trong typology tự chế thang đo mới thay vì dùng enum BP9 đã khóa | R211 + BP9 sensitivity_tiers locked | Đọc `bible/supernatural_typology.yaml` (hoặc file tương đương G5 tạo) — mọi giá trị field `sensitivity` PHẢI ∈ {low, medium, high} — grep giá trị nào khác 3 chữ này = 100% SAI |
| G5-3 | `entity_class` thêm vào `bible/37_character_schema.yaml` không qua RFC/authorization | bible immutable discipline (đã áp dụng nhiều lần: R142/R143, bible/31) | Commit sửa bible/37 PHẢI có "per Mr.Long authorization" trong message. Thiếu = 100% SAI dù nội dung field đúng kỹ thuật |
| G5-4 | Possession state machine viết engine riêng thay vì mở rộng `bp4/state_machines.yaml` (draft tự cam kết "KHÔNG viết engine riêng") | R211 + tự-cam-kết trong chính task file (claim=work — phải khớp) | Diff `governance/blueprint/bp4/state_machines.yaml` — entity `ghost` phải được MỞ RỘNG state (thêm state possession), KHÔNG có 1 file state-machine song song đứng riêng làm luật cho cùng entity |
| Cross-G4/G5 | Cả 2 pack cùng sửa 1 file trong cùng cửa sổ thời gian (vd `bp4/event_bus.yaml` — cả G4 D2 lẫn G5 D3 đều tham chiếu) mà không claim/thông báo nhau | PACK CLAIM luật 11 + gotcha G6 (claim chỉ chặn trùng-pack, KHÔNG chặn 2 pack khác nhau cùng sửa 1 file chung) | Trước khi merge: `git log --all --oneline -- governance/blueprint/bp4/event_bus.yaml` kể từ lúc 2 claim mở — nếu có 2 commit từ 2 session khác nhau sửa CÙNG vùng dòng gần nhau → cần Boss trọng tài như vụ BP6 bản A/B, KHÔNG tự ý merge cả 2 |
| Cross-G4/G5 | Cultural KB (deep-research 4/7) bị 1 trong 2 pack "hấp thụ" sai — vd G4 chép nguyên `sensitivity` cũ của Cultural KB draft thay vì enum BP9 đã chuẩn hóa | Đã phát hiện: Cultural KB gốc dùng thang đo riêng trước khi có Evidence Schema chuẩn hóa (CMD_BUILD_3 SVAF 4/5) | Grep field `sensitivity`/`confidence` trong output G4 lẫn G5 — PHẢI khớp enum đã chuẩn hóa (`evidence_schema_cultural_kb.yaml`), không dùng số/nhãn tự do từ Cultural KB draft gốc |

## KHÔNG CHỜ ĐỦ 2 PACK MỚI AUDIT
G4 và G5 độc lập (không phụ thuộc nhau theo BP3), audit riêng từng pack ngay khi mỗi pack báo
`READY_FOR_AUDIT`, không cần đợi cả 2 xong cùng lúc — tránh nghẽn cổ chai giả tạo.

## SAU KHI CÓ VERDICT
Theo đúng format `CMD_AUDIT_PROTOCOL.md` (bảng Claim|Kiểm bằng gì|Kết quả + PASS/FAIL/PASS-với-
điều-kiện). Riêng G5-1/G5-2 nếu FAIL: route lại CMD_BUILD_3 kèm nguyên văn 3 dòng trích từ
`bp9/policy_gates.yaml` (đã trích sẵn trong bảng trên) — không để lặp lại vòng "tự nghiên cứu lại
căn cứ pháp lý" tốn thời gian (đã có sẵn, chỉ cần đọc).

## THAM CHIẾU
`CMD_AUDIT_PROTOCOL.md` (7 bước gốc) · `prompts/TASK_G4_WORLD.md` · `prompts/TASK_G5_SUPERNATURAL.md`
· `governance/blueprint/bp9/content_policy.yaml` + `policy_gates.yaml` (căn cứ pháp lý gốc, KHÔNG
nghiên cứu lại) · lesson-enforcer-claim-vs-behavior · lesson-dont-downplay-rigor ·
lesson-lock-ceremony-and-regen · lesson-claim-equals-work.
