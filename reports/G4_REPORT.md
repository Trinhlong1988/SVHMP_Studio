# G4 REPORT — World / Timeline / Event (TASK_G4_WORLD, kiểm chứng 4/7)

## Số đo (REALITY ANCHOR — luật 9: validator PASS trên dữ liệu THẬT)

| Số đo | Giá trị | Nguồn máy |
|---|---|---|
| Tập quét thật | 50/50 (ep_01..ep_50 — DoD "50 tập" khớp disk, không phải "90" như draft gốc) | `event_ledger_miner.py` |
| F1 nickname cross-episode | 57 ứng viên (đã lọc nhiễu 341→108→57 qua 2 vòng tinh chỉnh) | máy đếm |
| F2 mâu thuẫn số học tuổi/mốc (±3 dòng) | 4 tập ứng viên (đã lọc nhiễu 35→4 sau khi phát hiện lỗi gộp-nhiều-nhân-vật) | máy đếm |
| F3 object không có trong bible/12 | **36/50 tập — REALITY ANCHOR đạt** (phát hiện thật, không phải giả) | máy đếm |
| Gate 1 cửa (D5) | 4/4 PASS | `g4_world_check.py` |
| Mutation test | 20/20 pass | `tests/test_g4_world.py` |

## Quá trình build — 3 lần tự bắt lỗi trước khi ship (ghi lại để auditor không phải bắt lại)

1. **F1 (nickname cross-episode) ban đầu 341 finding — gần như toàn nhiễu.** Root cause: dùng heuristic "2-3 từ viết hoa liên tiếp" bắt cả "Con đã" (start-of-sentence + xưng hô), "Anh ơi" — không phải tên riêng. Sửa: chuyển sang dò theo âm tiết THẬT trong `passenger_roster_100.yaml` char_name + free-form name_guess (tái dùng `parse_passenger_main` từ G2, không viết lại) + loại từ trùng tên tắt nhân vật recurring (Khải Phong/Hạ Vy) + ngưỡng tần suất thấp. 341→57.
2. **F2 (mâu thuẫn tuổi nội bộ) ban đầu 35/50 tập — spot-check phát hiện: gộp tuổi NHIỀU nhân vật khác nhau trong cùng 1 tập** (vd tuổi mẹ 40 + tuổi con 21/60s bị coi là 1 người). Sửa: thu hẹp so sánh vào cửa sổ ±3 dòng quanh mốc "X năm trước" thay vì toàn tập. 35→4, đã spot-check case còn lại (ep_38: "mười bảy năm trước... mười bảy tuổi... trước sinh nhật mười tám tuổi" — văn phong "gần tròn tuổi" KHÔNG phải mâu thuẫn, ghi rõ giới hạn này trong report thay vì giấu).
3. **M1 (timeline_check) thiết kế sai ban đầu: dùng F1 (chưa xác nhận) làm nguồn HARD-FAIL** → chạy thử ra 16 "violation" giả (vì F1 tự nó chỉ là ứng viên trùng âm tiết, không phải xác nhận cùng 1 người). Đã dừng lại, tách hàm số học thuần `check_arithmetic_consistency_across_episodes()` (test được bằng mutation với dữ liệu XÁC NHẬN) khỏi việc tự động áp lên F1 chưa xác nhận. Trên dữ liệu thật: 0 violation là **ĐÚNG** (chưa có liên kết xác nhận từ D3, không phải tool yếu) — đúng đúng escape hatch REALITY ANCHOR của TASK ("nếu 0 = nghi tool yếu, phải bắn mutation trước khi tin").
4. **F3 (object không có trong bible/12) — phát hiện MỚI ngoài dự kiến**, khớp đúng RFC đã ghi nhận trước đó (memory: bible/12 thiếu nhóm gương/kính, hoa cúc, văn bản nghề nghiệp) nhưng lần này có **con số hệ thống: 36/50 tập** thay vì vài ví dụ lẻ tẻ.

## Deliverables

1. `tools/vn_number_words.py` — parser số đếm tiếng Việt viết chữ (episode.md KHÔNG dùng digit) — 9/9 self-test pass, xử lý đúng ambiguity "năm"=5 vs "năm"=year qua regex+backtrack, elision "hai mốt"=21.
2. `tools/event_ledger_miner.py` (D2) — mine 50 tập thật → `runtime/event_ledger_draft.yaml` (draft) + `reports/G4_EVENT_FINDINGS.md` (F1+F2+F3, đều đóng khung "ứng viên cần người xem lại" — không overclaim).
3. `tools/timeline_check.py` (D1) — bọc D2 + hàm số học thuần M1 (test được, KHÔNG áp lên dữ liệu chưa xác nhận) + M4 lịch âm cơ bản (rằm tháng 7/Tết — từ khóa phổ thông, KHÔNG cần Cultural KB verified vì không phải tuyên bố tôn giáo/pháp lý nhạy cảm) + reconcile note: `qa_fact_check.py` xác minh KHÔNG tái dùng được (hardcode EP01, không đọc tham số).
4. `governance/proposals/fact_ledger_schema.yaml` (D3) — đề xuất schema (fact_id/nguồn/cấp_độ_tin/trạng_thái_theo_thời_gian), kèm patch đề xuất tối thiểu cho `qa_fact_check.py` khi Mr.Long ký.
5. `tools/story_consistency_validator.py` (D4) — mở rộng: `validate_event_consistency` (event lock) + `validate_object_state_transition` (object jump detection, KHÔNG phải "không đổi" mà là "không nhảy vô lý không giải thích").
6. `tools/g4_world_check.py` (D5) — gate 1 cửa mirror `blueprint_suite_check.py`, wire `ci_gate` stage `G4_world`.
7. `tests/test_g4_world.py` — 20 test: unwire-guard (M5) + đủ đòn TASK M1/M2/M3/M4/M6 + reality-anchor F3.

## Ghi chú cho auditor

- Registry: `g4_world: candidate` (1 dòng, không dup-key).
- F1/F2 là **ứng viên**, không phải xác nhận — route executor/Mr.Long xem lại trước khi merge vào sổ chính thức.
- F3 là **phát hiện hệ thống mới**, khuyến nghị route RFC bible/12 mở rộng riêng (ngoài phạm vi G4 sửa trực tiếp bible LOCKED).
- Builder không kết luận PASS/FREEZE — chỉ READY FOR AUDIT.
