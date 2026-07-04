# CMD AUDIT — PHỤ LỤC RIÊNG G6 (Story Planner + Decision Engine)

> KHÔNG thay thế `CMD_AUDIT_PROTOCOL.md` (7 bước chung — vẫn bắt buộc chạy đủ). Cùng mẫu với
> `CMD_AUDIT_G4_G5.md` — viết TRƯỚC khi có kết quả build, tránh thiên vị xác nhận. Nguồn rủi ro:
> đọc trực tiếp `TASK_G6_STORY_PLANNER.md` + `bp6/decision_contract.yaml` + `blueprint_domains.yaml`
> dòng 486-592.

## THỨ TỰ CHẠY
1. `CMD_AUDIT_PROTOCOL.md` đủ 7 bước trên worktree sạch từ origin/main.
2. Bảng checkpoint domain dưới đây.
3. **Kiểm TÁCH BIỆT G6a (decision_engine) và G6b (story_planner)** — 2 domain khác nhau, khác
   blocking_dependency, audit riêng verdict, KHÔNG gộp chung 1 verdict duy nhất.

## QUY TẮC PHÂN ĐỊNH 100-ĐÚNG / 100-SAI
Giống hệt `CMD_AUDIT_G4_G5.md`: 100% ĐÚNG = lệnh máy + exit code + đối chiếu dòng cụ thể +
mutation ngược không lọt. 100% SAI = ≥1 bằng chứng cụ thể mâu thuẫn. Nhóm G6-1 (build-ahead)
và G6-4 (số bịa R195) KHÔNG có mức giữa.

## BẢNG RỦI RO ĐÃ BIẾT ← BÀI HỌC LỊCH SỬ

| # | Rủi ro cụ thể | Bài học lịch sử áp dụng | Cách kiểm — tiêu chí 100đ/100s |
|---|---|---|---|
| G6-1 | **G6b (story_planner.py) build TRƯỚC khi G4 D1(timeline_check)/D2(event_ledger_miner) thật sự có trên disk** — build-ahead vi phạm luật 9 REALITY ANCHOR | REALITY ANCHOR (luật 9 MASTER) + phát hiện chính của phiên audit trước-build (BP0 dòng 499 khai rõ blocking_dependency) | `Test-Path runtime/event_ledger_draft.yaml` + `Test-Path tools/timeline_check.py` PHẢI True trước khi chấp nhận bất kỳ file nào thuộc D5 (`tools/story_planner.py`) tồn tại trong commit. CÓ D5 nhưng KHÔNG có 2 file G4 kia = **100% SAI, build-ahead** |
| G6-2 | 12 knob trong `bible/42_decision_policy.yaml` dùng số tự nghĩ thay vì đúng `method` đã ghi sẵn trong `bp6/decision_contract.yaml#knobs[].calibration_source.method` | R195 (đã bắt nhiều lần trong dự án — BP6 chính nó từng lọt 1 lần "top-level leak" lúc audit 4/7) | Với MỖI knob: đọc `calibration_source.method` gốc (VD "đếm `[pause:*ms]` golden theo scene") → tự tay đo lại trên `EP01_FULL` text → SO KHỚP số G6 ghi trong bible/42. Lệch số đo thật = 100% SAI knob đó (không quy tất cả 12 knob thành 1 verdict — liệt kê từng knob) |
| G6-3 | `calibrated_from.evidence` trỏ path/key KHÔNG tồn tại trong `bible/31_golden_samples.yaml` (bịa evidence cho có) | lesson-enterprise-audit (auditor đọc không grep-đoán) | Với mỗi `calibrated_from`, mở đúng path+key ra đọc — path/key không resolve được = 100% SAI (không chỉ check "field có tồn tại" mà phải RESOLVE ra giá trị thật) |
| G6-4 | `decision_engine.py` (D3) tự bịa giá trị cho field packet cần input từ story plan (khi G6b chưa xong) thay vì để `status: planned` trung thực | PLANNED HONESTY (5-metadata) + lesson-dont-downplay-rigor | Đọc code D3 — field nào phụ thuộc story_planner output mà G6b CHƯA build: PHẢI thấy code raise/return `planned`/`None` tường minh, KHÔNG thấy giá trị mặc định giả (vd `0.5`, `[]` rỗng ngụy trang "đã có") |
| G6-5 | `story_plan_schema.yaml` (D5) field-hóa mà KHÔNG có bằng chứng Mr.Long đã duyệt format (BP0 khai rõ "Mr.Long duyệt format kế hoạch" là blocking_dependency riêng, KHÁC với "G4 xong") | bible/lock discipline — mọi field-hóa `planned→exists` cần authorization tường minh | Tìm PING/commit message có trích dẫn rõ Mr.Long duyệt ĐÚNG format này (không phải duyệt chung chung "làm G6 đi") — thiếu = 100% SAI dù nội dung kỹ thuật đúng |
| G6-6 | `tools/g6_story_planner_check.py` gộp cả G6a+G6b vào 1 gate nhưng short-circuit ở G6a khiến G6b không bao giờ được chạy check (hoặc ngược lại) | TASK_G6 tự khai "KHÔNG short-circuit" (mirror luật blueprint_suite) | Mutation: cho G6a FAIL cố ý → xác nhận gate VẪN chạy tiếp check G6b (không dừng sớm) — 2 chiều |
| Cross-G4/G6 | G6 tự ý sửa `runtime/event_ledger_draft.yaml` (file sở hữu G4) thay vì chỉ ĐỌC | PACK CLAIM luật 11 + 1-writer discipline | `git diff` — `runtime/event_ledger_draft.yaml` KHÔNG được xuất hiện trong commit G6 (chỉ G4 được ghi file này) |
| Cross-BP6 | G6 sửa `bp6/decision_contract.yaml` (LOCKED) để "cho vừa" số đo được thay vì sửa số cho khớp contract | BP6 LOCKED — RFC nếu cần đổi contract, không tự sửa lén | `git diff governance/blueprint/bp6/` — commit G6 KHÔNG được đụng file này. Đụng = 100% SAI ngay, không cần xét tiếp |

## KHÔNG CHỜ G6a/G6b XONG CÙNG LÚC MỚI AUDIT
G6a (decision_engine) sẵn sàng ngay từ đầu — audit G6a ngay khi báo `READY_FOR_AUDIT`, không đợi
G6b (blocked on G4). G6b chỉ audit sau khi xác nhận G4 D1/D2 tồn tại thật (checkpoint G6-1).

## SAU KHI CÓ VERDICT
Theo format `CMD_AUDIT_PROTOCOL.md`. G6-1 hoặc Cross-BP6 FAIL → route lại kèm nguyên văn dòng
BP0 (486-514, 555-592) đã trích trong `TASK_G6_STORY_PLANNER.md` — không để lặp lại vòng tự tra
cứu lại domain declaration.

## THAM CHIẾU
`CMD_AUDIT_PROTOCOL.md` · `CMD_AUDIT_G4_G5.md` (mẫu gốc) · `prompts/TASK_G6_STORY_PLANNER.md` ·
`governance/blueprint/bp6/decision_contract.yaml` · `governance/blueprint/blueprint_domains.yaml`
(dòng 486-592) · lesson-enterprise-audit · lesson-dont-downplay-rigor.
