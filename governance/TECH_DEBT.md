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
- **Trạng thái:** **CLOSED** (2026-07-05, CMD_BUILD_3, pack `intro_template_retrofit`).
  - **Đã sửa:** 37/40 tập (`ep_11`–`ep_49`, trừ `ep_30`/`ep_50` — giữ waiver naming riêng của G2, không đụng file 2 tập đó theo chỉ đạo). Mỗi tập chỉ đổi đúng 2 cụm (`git diff --stat`: `4 ++--`/tập = 2 dòng, không đụng nội dung khác). Xác nhận `git diff output/ep_30 output/ep_50` = rỗng.
  - **`ep_40`: đã đúng sẵn từ trước** (0 vi phạm khi quét lại — trùng thời điểm commit `fix(G2+text): ep_40 bay-nam->tam-nam + go 2 co canh bao` của G2_EXECUTOR, có vẻ đã tiện thể sửa luôn 2 cụm này). Không cần sửa gì thêm cho `ep_40`.
  - **Bằng chứng:** `python tools/post_render_gate.py --ep N` chạy cho toàn bộ 38 tập (11–49 trừ 30/50) → **38/38 PASS (0 FAIL)**.
  - **Phát hiện phụ (CHƯA sửa, ngoài phạm vi DEBT-001 gốc):** `output/ep_N/episode_tts_ready.md` (N=02–50, bao gồm cả `ep_30`/`ep_50`) **cũng chứa y hệt 2 pattern cũ** (`Series:` / thiếu "kịp") — nhưng `tools/post_render_gate.py` CHỈ đọc `episode.md`, không đọc `episode_tts_ready.md`, nên gate không bắt được. File TTS-ready dùng để render audio thật — nếu không đồng bộ, audio production sẽ vẫn phát bản intro cũ dù text-gate đã PASS bản mới. **Cần Mr.Long quyết định phạm vi trước khi ai đó retrofit file này** (không tự ý mở rộng phạm vi DEBT-001 đã đóng). Đề xuất mở `DEBT-002` riêng nếu cần xử lý.

---

## DEBT-002: `tools/sfx_acquire.py` — 2 nhánh AI-gen / build_from chưa implement thật (ACE-Step API)

- **Phát hiện:** 2026-07-05, review finding LOW (fix/debt3-sfx-todo) — 2 dòng `print(f"  TODO: ...")` nằm chìm trong luồng log runtime bình thường (stdout lẫn với các dòng info/progress khác), không ai theo dõi được còn bao nhiêu chỗ TODO này, ở đâu.
- **Vị trí:**
  1. `generate_via_ace_step()` (~dòng 413 cũ) — chưa gọi `gradio_client` thật tới ACE-Step local port 7865; hàm luôn `return None`, buộc `acquire_asset()` rơi vào nhánh "chờ Mr.Long gen thủ công qua webui".
  2. `acquire_asset()`, nhánh `spec.get("build_from")` (~dòng 449 cũ) — chưa implement compositing từ raw asset có sẵn; luôn `return False`.
- **Phạm vi ảnh hưởng:** mọi `asset_id` có `ai_generate: true` hoặc `build_from: ...` trong registry `ASSETS` sẽ không bao giờ tự động hoàn tất — pipeline luôn dừng ở bước này và cần Mr.Long can thiệp thủ công. Asset đi qua nhánh search-candidate (mặc định) không bị ảnh hưởng.
- **Vì sao chưa fix:** cần API key/service ACE-Step thật (`gradio_client` call tới port 7865) + raw assets thật cho compositing — ngoài phạm vi 1 fix code đơn thuần, không tự ý fake return data để "giả vờ" đã implement.
- **Đề xuất fix:** khi có ACE-Step service sẵn sàng + raw assets, implement `gradio_client.Client(...)` call thật trong `generate_via_ace_step()` và logic compositing (ffmpeg concat/mix) trong nhánh `build_from`; verify bằng cách chạy `--asset <id có ai_generate/build_from>` và xác nhận file wav thật được tạo + checksum lock (không còn early-return).
- **Trạng thái:** **OPEN**. 2026-07-05 (fix/debt3-sfx-todo): đã đổi 2 dòng `print(TODO)` thành `logging.warning("[NOT-IMPLEMENTED] ...")` kèm tham chiếu `DEBT-002` ngay trong message + comment code, để không còn "TODO chìm" trong stdout — chưa implement logic thật (đúng phạm vi finding LOW, không tự ý mở rộng).
