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
  - **Phát hiện phụ (CHƯA sửa, ngoài phạm vi DEBT-001 gốc):** `output/ep_N/episode_tts_ready.md` (N=02–50, bao gồm cả `ep_30`/`ep_50`) **cũng chứa y hệt 2 pattern cũ** (`Series:` / thiếu "kịp") — nhưng `tools/post_render_gate.py` CHỈ đọc `episode.md`, không đọc `episode_tts_ready.md`, nên gate không bắt được. File TTS-ready dùng để render audio thật — nếu không đồng bộ, audio production sẽ vẫn phát bản intro cũ dù text-gate đã PASS bản mới. **Cần Mr.Long quyết định phạm vi trước khi ai đó retrofit file này** (không tự ý mở rộng phạm vi DEBT-001 đã đóng). Đề xuất mở ticket riêng (số thứ tự tiếp theo còn trống tại thời điểm mở — xem `DEBT-002`/`DEBT-003` bên dưới đã chiếm 2 số này trước) nếu cần xử lý.

---

## DEBT-002: Fixture audio thật `cliffhanger.wav`/`hook.wav` bị xóa khỏi `output/ep_01/sections/` — 8 test case Voice QA skip âm thầm, không rõ lý do trong output pytest mặc định

- **Phát hiện:** 2026-07-05, khi rà soát finding MEDIUM của `tests/test_voice_qa_tools.py` (fixture `real_cliffhanger`/`real_hook`).
- **Nguyên nhân gốc:** `output/ep_01/sections/cliffhanger.wav` và `output/ep_01/sections/hook.wav` không còn tồn tại trên đĩa (nghi vấn: bị xóa trong sự cố 2/7 cùng đợt với các vụ mất dữ liệu khác đã ghi nhận trong dự án — chưa xác nhận được commit/thời điểm chính xác vì file chưa từng được track bởi Git trong lịch sử worktree hiện tại). Các file `.whisper_compare.json` sinh ra từ 2 file `.wav` này (`cliffhanger.whisper_compare.json`, `hook.whisper_compare.json`) vẫn còn nguyên trong thư mục — chỉ riêng audio thật bị mất.
- **Bằng chứng (đã tự kiểm chứng, không suy đoán):**
  - `Get-ChildItem output/ep_01/sections/` (2026-07-05) liệt kê 14 file: toàn bộ là `.json` (`spec_*.json`, `*.whisper_compare.json`) + 1 thư mục `BACKUP_v53_BAD_29_06_1350`. **Không có bất kỳ file `.wav` nào.**
  - `tests/test_voice_qa_tools.py` fixture `real_cliffhanger`/`real_hook` (trước fix) gọi `pytest.skip(f"missing real audio {p}")` — message generic, không nói rõ đây là nợ kỹ thuật đã biết, không trỏ tới TECH_DEBT.md, không nói cần làm gì để hết skip.
  - `python -m pytest tests/test_voice_qa_tools.py -q` (trước fix): output mặc định chỉ hiện `"X passed, 8 skipped"` — không có ticket, không có lý do cụ thể hiển thị trừ khi chạy `-rs`/`-v` và tự suy luận từ đường dẫn file.
  - 8 test case bị skip do phụ thuộc 2 fixture này: `TestR188Boundary.test_03`, `TestR189Breath.test_03`, `TestR190Prosody.test_03`, `TestR190bOnset.test_03`, `TestR191DialogueIdentity.test_03` (đều dùng `real_cliffhanger`), và `TestR181cEmbedding.test_03`, `test_04`, `test_05` (dùng `real_cliffhanger` + `real_hook`) — tức toàn bộ nhánh "chạy trên audio thật" của 6 Voice QA tool (R188/R189/R190/R190b/R191/R181c) hiện **không được kiểm chứng bằng audio thật**, chỉ còn nhánh synthetic (`synth_clean`, `synth_pitch_drop`, v.v.) chạy.
- **Phạm vi:** `tests/test_voice_qa_tools.py` — 8/N test case của bộ Voice QA tool. Không ảnh hưởng test case dùng audio synthetic (tự sinh trong RAM, không phụ thuộc file that).
- **Không tự tạo lại fixture:** KHÔNG tự tạo file `.wav` giả lập để thay thế — 2 file này là audio giọng đọc thật (TTS output của ep_01), test case R188-191/embedding cần kiểm chứng trên đặc tính audio thật (artifact biên, breath, prosody, giọng nói) mà audio giả lập (sine wave) không tái hiện được đúng bản chất bug cần bắt.
- **Đề xuất fix:** Boss cung cấp lại 2 file audio thật `cliffhanger.wav`/`hook.wav` (từ bản render ep_01 gốc, hoặc render lại từ `spec_cliffhanger.json`/`spec_hook.json` nếu pipeline TTS còn tái tạo được đúng giọng) → đặt vào `output/ep_01/sections/` → chạy `pytest tests/test_voice_qa_tools.py -v` xác nhận 8 test case trước đây skip nay PASS (hoặc FAIL đúng nghĩa, không còn SKIP).
- **Đã làm (2026-07-05, khắc phục triệu chứng "im lặng", KHÔNG khắc phục gốc — vẫn thiếu audio thật):** Sửa message `pytest.skip(...)` trong `tests/test_voice_qa_tools.py` (fixture `real_cliffhanger`, `real_hook`) từ generic `f"missing real audio {p}"` thành reason cụ thể, nêu rõ: file gì thiếu, nghi vấn nguyên nhân, trỏ tới đúng entry này (`DEBT-002`), nói rõ cần gì (audio thật từ Boss) để hết skip, và 5+3 test case nào đang phụ thuộc. Mục tiêu: biến "nguy cơ âm thầm" (skip không lý do rõ trong output mặc định) thành nợ kỹ thuật CÓ GHI NHẬN — không phải xóa cảnh báo, không phải tự chế fixture giả để "cho xanh".
- **Trạng thái:** **OPEN** — chờ Boss cung cấp audio thật. 8 test case vẫn SKIP (đúng, có chủ đích) cho tới khi có fixture.

---

## DEBT-003: `tools/sfx_acquire.py` — 2 nhánh AI-gen / build_from chưa implement thật (ACE-Step API)

- **Phát hiện:** 2026-07-05, review finding LOW (fix/debt3-sfx-todo) — 2 dòng `print(f"  TODO: ...")` nằm chìm trong luồng log runtime bình thường (stdout lẫn với các dòng info/progress khác), không ai theo dõi được còn bao nhiêu chỗ TODO này, ở đâu.
- **Vị trí:**
  1. `generate_via_ace_step()` (~dòng 413 cũ) — chưa gọi `gradio_client` thật tới ACE-Step local port 7865; hàm luôn `return None`, buộc `acquire_asset()` rơi vào nhánh "chờ Mr.Long gen thủ công qua webui".
  2. `acquire_asset()`, nhánh `spec.get("build_from")` (~dòng 449 cũ) — chưa implement compositing từ raw asset có sẵn; luôn `return False`.
- **Phạm vi ảnh hưởng:** mọi `asset_id` có `ai_generate: true` hoặc `build_from: ...` trong registry `ASSETS` sẽ không bao giờ tự động hoàn tất — pipeline luôn dừng ở bước này và cần Mr.Long can thiệp thủ công. Asset đi qua nhánh search-candidate (mặc định) không bị ảnh hưởng.
- **Vì sao chưa fix:** cần API key/service ACE-Step thật (`gradio_client` call tới port 7865) + raw assets thật cho compositing — ngoài phạm vi 1 fix code đơn thuần, không tự ý fake return data để "giả vờ" đã implement.
- **Đề xuất fix:** khi có ACE-Step service sẵn sàng + raw assets, implement `gradio_client.Client(...)` call thật trong `generate_via_ace_step()` và logic compositing (ffmpeg concat/mix) trong nhánh `build_from`; verify bằng cách chạy `--asset <id có ai_generate/build_from>` và xác nhận file wav thật được tạo + checksum lock (không còn early-return).
- **Trạng thái:** **OPEN**. 2026-07-05 (fix/debt3-sfx-todo): đã đổi 2 dòng `print(TODO)` thành `logging.warning("[NOT-IMPLEMENTED] ...")` kèm tham chiếu `DEBT-003` ngay trong message + comment code, để không còn "TODO chìm" trong stdout — chưa implement logic thật (đúng phạm vi finding LOW, không tự ý mở rộng).

---

## DEBT-004: Cross-G3/G6 — `dialogue_generator.py.scene_context` không khớp packet 12-knob thật của `decision_engine` (chưa build)

- **Phát hiện:** 2026-07-05, audit độc lập checkpoint `Cross-G3/G6` (`prompts/CMD_AUDIT_G3.md`) trên pack `g3_dialogue`.
- **Nguyên nhân gốc:** `tools/dialogue_generator.py::generate_line()` nhận `scene_context` dạng dict tự do (`emotion_beat`, `listener_call`, `ep_n`, `driver_trigger_window`, `driver_target`) — thiết kế TẠM để G3 không tự tính tỉ lệ thoại/trần thuật (đúng `non_responsibility` của domain `dialogue`: "KHÔNG quyết ratio thoại/narration — việc của G6 decision_engine"). Nhưng cấu trúc dict tạm này **không khớp** packet 12-knob thật đã khai trong `governance/blueprint/bp6/decision_contract.yaml` (trong đó `dialogue_ratio`/`narration_ratio` là 2/12 knob) — vì `tools/decision_engine.py` **chưa tồn tại** (G6 chưa build) nên chưa có packet thật để đối chiếu/khớp interface.
- **Bằng chứng:** `governance/blueprint/bp6/decision_contract.yaml` có 12 knob khai báo (bao gồm `dialogue_ratio`, `narration_ratio`); `tools/dialogue_generator.py` scene_context hiện chỉ có 5 field tự do, không field nào đặt tên khớp 2 knob trên; `tools/decision_engine.py` không tồn tại trên disk (grep xác nhận).
- **Phạm vi:** `tools/dialogue_generator.py::generate_line()` — tham số `scene_context`. Không ảnh hưởng phần còn lại của G3 (validator/manager/gate) vì chúng không phụ thuộc cấu trúc packet.
- **Vì sao chưa fix ngay:** G6 (Story Planner/decision_engine) **chưa build** — không có packet thật nào để khớp interface vào lúc này; tự đoán/bịa cấu trúc packet trước khi G6 khai chính thức sẽ là R211 (nhân đôi/đoán trước quyết định domain khác).
- **Đề xuất fix (khi G6 build xong):** sau khi `tools/decision_engine.py` tồn tại + packet 12-knob có `status: exists` thật, sửa lại `scene_context` (hoặc thêm 1 adapter mỏng) trong `dialogue_generator.py` để nhận đúng field `dialogue_ratio`/`narration_ratio` (và các field liên quan khác nếu G6 xác nhận cần) từ packet thật — KHÔNG tự tính toán ratio bên trong `dialogue_generator.py` (giữ đúng ranh giới domain).
- **Trạng thái:** **OPEN** (ghi nhận trước, chưa có việc cần làm ngay — chờ G6 build).
