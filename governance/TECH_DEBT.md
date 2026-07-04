# TECH DEBT LEDGER

Nợ kỹ thuật liên project-wide, không gắn với 1 pack/1 task cụ thể. Mỗi mục ghi: phát hiện khi nào, bằng chứng, phạm vi, đề xuất fix, trạng thái.

---

## DEBT-001: Intro template cũ chưa cập nhật brand mới (R40/R41 "5 elements")

- **Phát hiện:** 2026-07-04, trong lúc audit R41 gate chặn commit ep_40 của G2_EXECUTOR.
- **Nguyên nhân gốc:** `tools/post_render_gate.py` (`INTRO_ELEMENTS`, comment "2026-06-30 R108 brand... Mr.Long revert comma") siết brand template mới, nhưng **không có bước retrofit toàn bộ back-catalog** khi rule đổi. Rule mới chỉ áp cho ep_01 (pilot) tại thời điểm viết.
- **Bằng chứng (đã tự kiểm chứng, không suy đoán):**
  - Quét trực tiếp `output/ep_11/episode.md` → `ep_50/episode.md` (40 tập): **40/40 (100%) fail** đúng 2 pattern:
    1. Thiếu literal `"Loạt truyện"` — bản cũ dùng `"Series:"` (VD ep_40 dòng 15: `Series: Chuyến xe cuối cùng về đâu.`)
    2. Thiếu literal `"chuyến xe chưa kịp nói lời tạm biệt"` — bản cũ thiếu chữ "kịp" (VD ep_40 dòng 19: `Ai cũng có một chuyến xe chưa nói lời tạm biệt.`)
  - `output/ep_01/episode.md` (pilot) có đủ cả 2 pattern → xác nhận đây là baseline ĐÚNG, các tập sau lệch dần theo thời gian, không phải lỗi thiết kế hệ thống.
  - Đã bác bỏ giả thuyết "intro là shared asset ghép lúc render" (do G2_EXECUTOR nêu khi báo cáo bị chặn) — intro là **text tĩnh nằm ngay trong `episode.md`** của từng tập, không phải asset ghép runtime. `post_render_gate.py` đọc trực tiếp nội dung file `.md`, không đọc audio/asset render.
- **Phạm vi:** ep_11 → ep_50 (40 tập). Chưa quét ep_02–ep_10 (nằm ngoài batch B3 hiện tại) — cần bổ sung khi có thời gian.
- **Không dùng để fix:** `SVHMP_RESTORE_AUTH=1` — cơ chế này (trong `tools/git_hook_pre_commit.py` SECTION B) được khai báo hẹp cho **khôi phục nội dung đã duyệt trước sự cố 2/7**, không phải bypass nợ kỹ thuật chung. Dùng sai mục đích sẽ biến 1 exemption có phạm vi hẹp thành cửa sau chung cho mọi gate.
- **Đề xuất fix:** batch job thay `"Series:"` → `"Loạt truyện:"` và chèn `"kịp"` vào cụm `"chưa nói lời tạm biệt"` cho 40 file, mỗi thay đổi chỉ 2 cụm từ/tập (không đụng nội dung khác, không đụng canon nhân vật) → chạy `post_render_gate.py --ep N` xác nhận PASS từng tập trước khi commit hàng loạt.
- **Trạng thái:** OPEN — chưa gán session nào. Không phải việc của G2_EXECUTOR (task hiện tại của G2 là character-fill, không phải brand-template retrofit). Đề xuất giao CMD_BUILD hoặc CMD_BUILD_3 sau khi rảnh khỏi task hiện tại, hoặc 1 task riêng `TASK_INTRO_TEMPLATE_RETROFIT.md`.
