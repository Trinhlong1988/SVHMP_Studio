# TASK — DEBT-030: ghi nhận chính thức mạch "hồi ức Khải Phong" vào bible, cập nhật bible/03

> Viết bởi CMD_AUDIT 12/7. Mr.Long ĐÃ XÁC NHẬN trực tiếp: mạch bác tài nói tăng dần (EP07→90) +
> hành khách "quang_memory_fragment"/`callback_target` (EP07→ít nhất EP50, đã tự grep xác nhận
> **40/50 tập** có tag này) LÀ mạch truyện có chủ đích — KHÔNG phải lỗi. `bible/03` hiện chỉ khai
> "2 câu chuẩn + 2 ngoại lệ cố định (ep_73/90)" đã LỖI THỜI so với thiết kế thật — cần cập nhật.

## Việc cần làm

### Bước 1 — Đọc đủ bằng chứng trước khi viết bible (KHÔNG suy đoán/bịa cấu trúc arc)

Grep toàn bộ 40 tập có `quang_memory_fragment` (`grep -rln "quang_memory_fragment" output/ep_*/episode.md`),
đọc frontmatter (`quang_memory_fragment`, `callback_target`) + đoạn CLIFFHANGER liên quan của MỖI tập
— lập bảng đầy đủ: tập nào, giai đoạn arc nào (M1/M2/M3/M4.../PEAK — đọc đúng ký hiệu đang dùng thật
trong frontmatter, KHÔNG tự đặt tên mới), câu thoại bác tài (nếu có) ở tập đó, `callback_target` trỏ
tới tập nào. Đối chiếu với 2 mốc đã biết (ep_73 "Tới rồi đấy, Nam.", ep_90 "Đến lúc tôi cũng nhớ ra
rồi.") xem 2 mốc này có khớp là đỉnh/kết của cùng 1 arc không, hay là 2 arc khác nhau.

### Bước 2 — Soạn proposal (KHÔNG sửa thẳng bible/03 — bible đã SIGNED)

Theo đúng quy ước dự án (`governance/proposals/*.yaml` — xem mẫu `story_plan_schema_proposal.yaml`),
soạn 1 proposal mới mô tả:
- Tên chính thức của mạch (đề xuất, Mr.Long chốt): "Mạch hồi ức Khải Phong" hoặc tên khác phù hợp.
- Cấu trúc arc thật (từ Bước 1) — các mốc M1→M2→...→PEAK, tập nào rơi vào mốc nào.
- Quy tắc thoại bác tài LEO THANG: thay thế "chỉ 2 câu + 2 ngoại lệ cố định" bằng mô tả đúng cơ chế
  thật (bao nhiêu câu tối đa/tập theo giai đoạn arc, điều kiện nào cho phép thêm câu — dựa dữ liệu
  thật đã đọc, KHÔNG suy đoán công thức chưa có bằng chứng).
- Làm rõ quan hệ với 2 mốc `ep_73`/`ep_90` đã biết — có còn là "ngoại lệ" hay là 1 phần tự nhiên của
  arc lớn hơn.
- Đề xuất vị trí lưu: cập nhật `bible/03_character_bible.yaml` (phần CHAR_DRIVER `speech_lines`/
  `max_dialog_per_ep`) trỏ sang bible mới, hoặc mở 1 file bible riêng (nếu quy mô 40+ tập đủ lớn để
  tách domain riêng — đề xuất, Mr.Long quyết).

### Bước 3 — Chờ Mr.Long xác nhận proposal, KHÔNG tự merge vào bible/03

Sau khi có proposal, dừng lại — báo qua `log_ping.py`, chờ Mr.Long duyệt (giống quy trình
`story_plan_schema_proposal.yaml` đã dùng trước: proposal → APPROVED_X → mới field-hoá chính thức).

### Bước 4 — SAU KHI proposal được duyệt: cập nhật bible + xây enforcer DEBT-032 (phần driver dialogue)

- Cập nhật `bible/03_character_bible.yaml` theo đúng nội dung đã duyệt.
- Xây check "driver dialogue" còn thiếu của DEBT-032 (đã hoãn ở task DEBT-031 content-fix) — đối chiếu
  ĐÚNG luật mới (không phải luật cũ "chỉ 2 câu"), dùng cấu trúc M1/M2/.../PEAK + tập tương ứng đã
  field-hoá ở Bước 1/2.

## Ràng buộc

- Bước 1-2 KHÔNG sửa bất kỳ file bible/episode nào — chỉ đọc + viết proposal mới.
- KHÔNG tự merge proposal vào bible/03 khi chưa có xác nhận Mr.Long (Bước 3 là gate bắt buộc).
- Domain `character` (bible/03) — kiểm ownership_matrix trước khi ai được sửa (Bước 4).

## DoD
Bảng đầy đủ cấu trúc arc (Bước 1) + 1 proposal file hoàn chỉnh (Bước 2), đã log_ping báo Mr.Long xem
xét — DỪNG ở đó cho tới khi có xác nhận, KHÔNG tự chạy tiếp Bước 4.

## THAM CHIẾU
`governance/TECH_DEBT.md` DEBT-030 (2 vòng quyết định) + DEBT-032, `bible/03_character_bible.yaml`,
`governance/proposals/story_plan_schema_proposal.yaml` (mẫu quy trình proposal→approved→field-hoá).
