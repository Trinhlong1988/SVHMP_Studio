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
  **Cập nhật 5/7 (xem `governance/master_roadmap.md` §6 mục 6):** Mr.Long chốt 50 tập hiện có là "thử nghiệm turn 1", sẽ REGEN lại toàn bộ qua pipeline chuẩn G6-G8 khi sẵn sàng — retrofit `episode_tts_ready.md` giờ là việc TẠM THỜI (không cấp thiết bằng trước), có thể hoãn tới đợt regen thay vì patch tay riêng lẻ.

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
- **Đề xuất fix (SỬA 5/7 — hướng cũ "chờ Boss cung cấp file cũ" SAI, đã kiểm chứng lại):** KHÔNG cần tìm lại file cũ. Pipeline render + làm sạch audio (`tools/svhmp_v13_render.py`: `qa_clean_tail()` voicing-based tail cleaner, `TAIL_TRIM_DB=-62`, `FADE_TAIL_MS=80`, `fade_head` 80ms cosine — toàn bộ đã tune và Boss duyệt 1/7, bằng chứng sản phẩm thật `D:\SVHMP_render\ep_01\intro_FULL_v2q.wav`) hoàn toàn còn dùng được và đã proven trên chính máy này. Text gốc 2 đoạn vẫn còn nguyên (`spec_hook.json`/`spec_cliffhanger.json`). Việc cần làm: chạy `scratchpad/render_one.py` (cwd `render_cwd`, theo đúng quy trình chunk-by-chunk đã dùng cho intro) cho 2 spec này → output đặt vào `output/ep_01/sections/hook.wav`/`cliffhanger.wav` → chạy `pytest tests/test_voice_qa_tools.py -v` xác nhận 8 test case hết SKIP.
- **Đã làm (2026-07-05, khắc phục triệu chứng "im lặng", KHÔNG khắc phục gốc — vẫn thiếu audio thật):** Sửa message `pytest.skip(...)` trong `tests/test_voice_qa_tools.py` (fixture `real_cliffhanger`, `real_hook`) từ generic `f"missing real audio {p}"` thành reason cụ thể, nêu rõ: file gì thiếu, nghi vấn nguyên nhân, trỏ tới đúng entry này (`DEBT-002`), nói rõ cần gì để hết skip, và 5+3 test case nào đang phụ thuộc. Mục tiêu: biến "nguy cơ âm thầm" (skip không lý do rõ trong output mặc định) thành nợ kỹ thuật CÓ GHI NHẬN — không phải xóa cảnh báo, không phải tự chế fixture giả để "cho xanh".
- **Trạng thái:** **CLOSED** (2026-07-10, CMD_BUILD, pack `debt002_003_004_fix`, per Mr.Long authorization 10/7).
  - **Bằng chứng (đã tự kiểm chứng, không suy đoán):** `output/ep_01/sections/hook.wav` (6.75MB) và `cliffhanger.wav` (5.05MB) **đã tồn tại thật trên đĩa** tại thời điểm nhận việc (mtime 2026-06-30, TRƯỚC CẢ thời điểm DEBT-002 được ghi OPEN 5/7 — nghĩa là file chưa từng thực sự mất trên máy này ở thời điểm 10/7, hoặc đã được khôi phục/render lại giữa 5/7-10/7 mà chưa ai cập nhật ticket). `scratchpad/render_one.py` (đề xuất fix cũ) hiện KHÔNG tồn tại — không cần dùng tới vì file đã có sẵn.
  - `python -m pytest tests/test_voice_qa_tools.py -v` → **23/23 PASS, 0 SKIP** (trước đó 8 test skip) — bao gồm đủ cả `TestR188Boundary.test_03`, `TestR189Breath.test_03`, `TestR190Prosody.test_03`, `TestR190bOnset.test_03`, `TestR191DialogueIdentity.test_03` (dùng `real_cliffhanger`) và `TestR181cEmbedding.test_03/04/05` (dùng `real_cliffhanger`+`real_hook`, bao gồm `test_05_cross_section_similarity_within_speaker` — phép so sánh giọng nói thật giữa 2 section, không thể giả mạo bằng file stub).
  - **Không cần hành động thêm:** không tự tạo lại fixture (đúng nguyên tắc gốc), không cần chạy render pipeline (file thật đã có sẵn) — chỉ xác nhận + đóng ticket với bằng chứng.

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
  - **Xác nhận lại 2026-07-10 (CMD_BUILD, per Mr.Long chỉ đạo "DEBT-003 cuối, LOW, không gấp"):** `curl` thử port 7865 (ACE-Step service) → không kết nối được (`NOT REACHABLE`) — blocker vẫn y nguyên như lúc mở ticket, không có gì thay đổi. Không tự implement giả (đúng nguyên tắc gốc "không fake return data để giả vờ đã implement"). Giữ nguyên OPEN, chờ Mr.Long cung cấp ACE-Step service/raw assets khi cần.

---

## DEBT-004: `scene_context` của `dialogue_generator.py` (G3) không khớp packet 12-knob thật của `decision_engine` (bp6/G6)

- **Phát hiện:** 2026-07-05, audit độc lập G3 (kiểm duyệt 5/7), khi đối chiếu interface `generate_line()` với `governance/blueprint/bp6/decision_contract.yaml`.
- **Vị trí (LƯU Ý: file này hiện CHỈ tồn tại trên branch `build/g3-dialogue-d0-d8`, CHƯA merge main — không có trên `main` tại thời điểm ghi entry này):**
  - `tools/dialogue_generator.py` (branch trên), hàm `generate_line(character_id, scene_context, ...)`: docstring khai `scene_context: {'emotion_beat':.., 'listener_call':.., 'ep_n':.., 'driver_trigger_window': [...], 'driver_target':..}` — 5 field tự đặt cho phạm vi G3.
  - `governance/blueprint/bp6/decision_contract.yaml` (đã LOCKED v1.0.0 trên main): packet thật của `decision_engine` là 12 knob chuẩn (`dialogue_ratio`, `narration_ratio`, `emotion_curve`, `fear_curve`, `suspense_curve`, `reveal_curve`, `pacing`, `scene_budget`, `information_budget`, `silence_budget`, `character_focus`, `pov`) — 2 tập field KHÔNG khớp nhau (5 field tự đặt của G3 vs 12 knob chuẩn của bp6/G6).
- **Nguyên nhân gốc:** G3 (dialogue) được build TRƯỚC G6 (decision_engine) chưa tồn tại (`bible/42_decision_policy.yaml`/`tools/decision_engine.py` 0% tại thời điểm audit) — generator phải tự đặt tạm 1 bộ field tối thiểu để chạy được, không phải lỗi thiết kế cố ý, nhưng tạo ra 1 interface tạm sẽ cần đối chiếu lại khi G6 build xong thật.
- **Phạm vi:** `tools/dialogue_generator.py` (nhánh G3, chưa merge). KHÔNG ảnh hưởng main hiện tại (file chưa tồn tại ở main). Sẽ ảnh hưởng khi G7 (generator) build và cần gọi cả dialogue lẫn decision_engine cùng lúc.
- **Không cần sửa ngay:** G6 (`decision_engine`) hiện 0% code (mới `claim` pack `g6_story_planner` 5/7, `bible/42` chưa tồn tại) — chưa có packet thật nào để đối chiếu cho khớp. Sửa bây giờ là đoán trước format của G6 (vi phạm nguyên tắc build-ahead đã bắt G3 lần trước).
- **Đề xuất fix:** khi G6a (`decision_engine`) build xong `tools/decision_engine.py` + packet builder thật, đối chiếu lại `scene_context` của `dialogue_generator.py` — 5 field tạm (`emotion_beat`/`listener_call`/`driver_trigger_window`/`driver_target`) cần map hoặc thay thế bằng field tương ứng trong packet 12-knob thật (`emotion_curve`, `character_focus`, v.v. — cần xác nhận map 1-1 hay cần field bổ sung, không tự suy đoán trước khi có packet thật).
- **Trạng thái:** **CLOSED — không phải bug, chỉ là hiểu sai giả định ban đầu** (2026-07-10, CMD_BUILD, pack `debt002_003_004_fix`, per Mr.Long authorization 10/7).
  - **Đã đối chiếu thật (G3 đã merge main + G6a đã build xong, đủ điều kiện đối chiếu như đề xuất fix yêu cầu):** đọc trực tiếp `tools/dialogue_generator.py::generate_line()` (dòng 135-142) — `scene_context` thật sự dùng đúng 3/5 field khai (`emotion_beat`, `listener_call`, `ep_n`; `driver_trigger_window`/`driver_target` CHỈ dùng trong `_generate_recurring()` cho logic Q1/Q2 driver, không liên quan knob). Đọc trực tiếp `governance/blueprint/bp6/decision_contract.yaml` dòng 52-58 (`emotion_curve`) và dòng 124-130 (`character_focus`) — **CẢ 2 knob đều khai rõ `consumer: {domain: generator, ...}`**, KHÔNG PHẢI `domain: dialogue`. Nghĩa là packet 12-knob của `decision_engine` **chưa từng được thiết kế để `dialogue_generator.py` tiêu thụ trực tiếp** — kiến trúc đúng từ đầu là `decision_engine` → `generator` (G7) → `dialogue` (G3), với G7 là tầng DỊCH bắt buộc (numeric/enum knob → nội dung cụ thể như text `emotion_beat`, tên `listener_call`).
  - **Xác nhận thêm:** `tools/episode_generator.py` (G7, đã build D1-D5, xem entry pack `g7_generator` lock v1.0) **CHƯA gọi `dialogue_generator.generate_line()` ở đâu cả** (grep xác nhận 0 kết quả) — tầng dịch G7↔G3 nói trên đúng là CHƯA xây, nhưng đây là 1 TÍNH NĂNG G7 cần làm trong tương lai (khi G7 mở rộng sang sinh dialogue thật), KHÔNG PHẢI 1 lỗi mismatch cần patch field-rename trong `dialogue_generator.py` hay `decision_engine.py` như giả định ban đầu của entry này.
  - **Kết luận:** 5 field tạm của `scene_context` (`emotion_beat`/`listener_call`/`ep_n`/`driver_trigger_window`/`driver_target`) là ĐÚNG thiết kế cho phạm vi hẹp của `dialogue_generator.py` (nội dung cụ thể cho 1 dòng thoại) — KHÔNG cần map 1-1 sang 12 knob (khác tầng trừu tượng: knob là chỉ số/enum vĩ mô cho G7 quyết định cấu trúc, không phải nội dung câu chữ cụ thể). KHÔNG có code nào cần sửa ở G3 hay G6. Việc còn lại (G7 gọi `generate_line()` + dịch packet→scene_context) là phạm vi tính năng của G7 khi mở rộng, đề xuất Mr.Long xác nhận có cần mở task riêng cho việc đó hay để tự nhiên phát sinh khi G7 làm dry-run sinh dialogue thật.

---

## DEBT-005: `tools/text_batch_fix.py::verify_post_fix()` + `tests/cases/test_audio_gate_regression.py` case_5 — an toàn khi chạy ĐƠN LẺ nhưng KHÔNG an toàn khi 2 phiên chạy `pytest` đồng thời trên CÙNG thư mục dùng chung → race-condition làm corrupt `output/ep_01/episode.md`/`episode_tts_ready.md` thật

- **Phát hiện:** 2026-07-05 tối, kiểm duyệt — push bị CI gate chặn 3 lần liên tiếp; 2 lần đầu là nhiễu thoáng qua (đã tự hết), lần 3 phát hiện **corruption thật**: `git status` cho thấy `output/ep_01/episode.md` (đã restore `git checkout --` ngay lập tức, xác nhận sạch) bị giảm từ ~630 dòng nội dung xuống gần rỗng (diff: 1284 dòng xóa, 8 dòng thêm) — đúng mẫu lỗi "ghi dở bị ngắt giữa chừng" đã biết trước đây (đã fix 1 lần trong `text_batch_fix.py`, nhưng vẫn còn 1 đường khác gây lại).
- **Cơ chế thật (đã đọc code, không suy đoán):**
  1. `tools/text_batch_fix.py::verify_post_fix()` (dòng 34-82) là nơi DUY NHẤT cố ý ghi thẳng `bad_text` vào file THẬT `output/ep_01/episode.md` (đúng thiết kế, có docstring giải thích) để chạy probe QA-rule. Dòng 56 gọi `subprocess.run([..., "tts_adapter_pre_render.py", "--ep", "1", "--apply"], ..., timeout=30)` **KHÔNG set `cwd`** → chạy trên thư mục thật, tái sinh `episode_tts_ready.md` THẬT từ `bad_text`. Có try/finally (dòng 54-82) khôi phục `episode.md` từ backup riêng của hàm này trước khi return/raise — đúng, an toàn cho 1 tiến trình.
  2. `tests/cases/test_audio_gate_regression.py::case_5_substitute_violates_r111()` (dòng ~148-215) tự backup/restore CẢ 2 file (`episode.md` + `episode_tts_ready.md`) trong try/finally riêng của nó, BỌC NGOÀI lời gọi `verify_post_fix()` — cũng đúng, an toàn cho 1 tiến trình.
  3. **VẤN ĐỀ:** cả 2 lớp backup đều dùng **đường dẫn file cố định** (`episode.md.batchfix_bak`, `episode.md.case5_bak`) trong CHÍNH thư mục `output/ep_01/` — không có khóa (file lock) nào giữa các tiến trình. Nếu 2 phiên (CMD_BUILD/CMD_BUILD_2/CMD_BUILD_3/kiểm duyệt) cùng lúc chạy `pytest tests/ -q` (hoặc `ci_gate.py`) trong CÙNG thư mục `C:\Users\Admin\SVHMP_git` (không phải worktree cách ly — chỉ kiểm duyệt luôn dùng worktree riêng cho audit, các phiên build khác làm việc trực tiếp trên thư mục dùng chung), tiến trình B có thể: (a) backup nhầm bản `bad_text` của tiến trình A làm "bản gốc", (b) ghi đè backup của A giữa lúc A đang chờ subprocess, (c) restore sai thời điểm — dẫn tới 1 trong 2 file bị bỏ lại ở trạng thái corrupt vĩnh viễn trong working tree (chưa commit, nên khôi phục được bằng `git checkout --`, nhưng nếu không ai để ý và lỡ tay `git add -A`/`git commit -A` thì sẽ commit luôn bản corrupt).
- **Đã làm ngay (an toàn, không mất dữ liệu):** `git checkout -- output/ep_01/episode.md output/ep_01/episode_tts_ready.md` — xác nhận `git status` sạch, nội dung khớp lại đúng commit gần nhất.
- **Đề xuất fix (chưa làm, cần CMD rảnh nhận):** (a) đổi tên file backup thành có suffix ngẫu nhiên/PID (`episode.md.batchfix_bak.{pid}`) để 2 tiến trình không giẫm lên nhau, HOẶC (b) dùng `filelock`/`msvcrt.locking` khóa file thật trong lúc probe chạy, HOẶC (c) triệt để nhất — sửa `verify_post_fix()` để hoạt động hoàn toàn trên 1 bản copy tạm (`tempfile`) ngay từ đầu thay vì ghi vào file thật dù chỉ tạm thời (loại bỏ hẳn rủi ro, không chỉ giảm thiểu). Khuyến nghị hướng (c).
- **Trạng thái:** **CLOSED VÒNG 3 (2026-07-09, CMD_BUILD_2)** — xem bằng chứng vòng 3 cuối mục này. Lịch sử: CLOSED (2026-07-05) → RESIDUAL/RE-CLOSED (2026-07-09) → RE-OPENED vòng 3 (2026-07-09) → **CLOSED VÒNG 3 (2026-07-09): vá đủ 7+ writer + enforcement test cưỡng chế máy chống tái diễn**.
  - **Đã sửa:** `tools/text_batch_fix.py::verify_post_fix()` viết lại hoàn toàn — tạo 1 `tempfile.TemporaryDirectory()` riêng cho MỖI lần gọi, copy `episode.md` (nội dung `text` cần kiểm) + các tool QA cần thiết (`tts_adapter_pre_render.py` + tool tương ứng từng rule trong `TOOL_MAP`, cộng `bible/27_fact_db.yaml` nếu rule cần) vào đó, rồi chạy TOÀN BỘ subprocess với `cwd=tmp_root`. Phát hiện quan trọng: cả 8 tool QA (`qa_eol_diacritic.py`, `qa_honorific.py`, `qa_continuity.py`, `qa_phonetic_safe.py`, `qa_repeat_action.py`, `qa_fact_check.py`, `qa_anti_generic.py`, `qa_ssot_diff.py`) tự tính đường dẫn `episode.md` bằng `Path(__file__).resolve().parents[1]` (dựa trên **vị trí script**, không phải cwd) — nên chỉ cần COPY tool sang thư mục tạm đúng cấu trúc tương đối (`tmp/tools/<tool>.py` + `tmp/output/ep_01/episode.md`) là mỗi tool TỰ ĐỘNG đọc đúng bản trong tmp, **không cần sửa 1 dòng logic nào trong 8 tool đó**.
  - `tests/cases/test_audio_gate_regression.py::case_5_substitute_violates_r111()`: bỏ toàn bộ khối backup/restore `episode.md`/`episode_tts_ready.md` thật + file `bad_registry` dead-code không dùng tới (code cũ đã tự bỏ ý định dùng registry, chỉ để sót lại việc tạo/xoá file) — không còn cần thiết vì `verify_post_fix()` không đụng file thật nữa. Xoá luôn import `shutil` không còn dùng.
  - **Bằng chứng (đã tự kiểm chứng, không suy đoán):**
    - Chạy `verify_post_fix()` trực tiếp trước/sau: `git status --porcelain output/ep_01/` **rỗng cả 2 lần** (trước: có sẵn rỗng; sau khi gọi hàm với `bad_text`: vẫn rỗng — không 1 byte nào của `episode.md`/`episode_tts_ready.md` thật bị chạm).
    - **Test đồng thời thật** (không chỉ chạy 1 lần rồi kết luận): chạy `python tests/cases/test_audio_gate_regression.py` ở **2 tiến trình nền song song thật** (không phải mô phỏng) — cả 2 đều exit 0, `✅ ALL 5 REGRESSION CASES PASS`, và `git status --porcelain output/ep_01/` **rỗng sau khi CẢ 2 đã hoàn tất**.
    - `python -m pytest tests/ -q`: xem `DEBT-006` bên dưới (chạy chung 1 lần cho cả 2 debt).
  - **RESIDUAL phát hiện + RE-CLOSED (2026-07-09, CMD_BUILD_2, kèm pack `g8_qa_runtime`):** fix 5/7 CHƯA triệt để — chỉ cô lập `verify_post_fix()`, **bỏ sót 2 writer khác** vẫn ghi vào `output/ep_01/episode.md`/`episode_tts_ready.md` THẬT: `tests/cases/test_publish_score.py::main()` (FAIL-case inject R86) + `tests/cases/test_forbidden_phrases.py::case()` (8 case) — đúng cảnh báo "còn 1 đường khác gây lại" (thực ra 2). Cả 2 tool `publish_score.py`/`tts_adapter_pre_render.py` resolve path từ `__file__`, KHÔNG nhận override → không dùng được cách tempfile như verify_post_fix. **Fix triệt để (đúng option (b) đề xuất dòng 81 — cross-process lock):** thêm `tests/_golden_lock.py` (file lock tempdir, best-effort không deadlock CI, stale-detect, reentrant) bọc mọi điểm mutate/observe `output/ep_01` thật; `test_golden_ep01_write_safety` (observer) cũng lấy lock bọc cửa sổ git-diff; `test_audio_gate_regression.py::case_5` đọc bản **committed** (`git show HEAD:...`) thay vì file live → miễn nhiễm + tránh deadlock lồng. **Bằng chứng (tự chạy thật):** 4/4 isolation PASS + ep_01 sạch; **PROOF concurrency THẬT** (3 mutator + 1 observer × 3 vòng song song, không mô phỏng) = all-pass + `git status output/ep_01/` rỗng sau khi cả 4 hoàn tất. Commit `11bbd94`.
  - **RESIDUAL VÒNG 3 — RE-OPENED (2026-07-09, CMD_AUDIT, sau khi Mr.Long hỏi thẳng "triệt để bug?"):**
    Vòng 2 chỉ tìm 2 writer đã BIẾT TRƯỚC (từ báo cáo cũ), không quét toàn diện — kiểm duyệt tự
    `grep` lại từ đầu TOÀN BỘ repo cho pattern ghi (`write_text`/`open(...,'w')`) gần đường dẫn
    `output/ep_01/`, loại bỏ file chỉ ĐỌC, đối chiếu file nào KHÔNG gọi `golden_lock` — tìm thêm
    **7 writer chưa từng được nhắc tới**, cùng chính xác lớp lỗi gốc (đọc `orig` → ghi đè
    `episode.md` THẬT → chạy check → `finally: restore`, KHÔNG khóa):
    `tests/cases/test_action_repeat.py` (đã đọc code xác nhận), `test_anti_generic.py`,
    `test_fact_contradiction.py`, `test_name_repetition.py`, `test_object_state.py`,
    `test_tts_pause.py` (đã đọc code xác nhận, cùng khuôn mẫu) — cả 6 dùng chung biến
    `EPISODE = BASE / "output/ep_01/episode.md"`, không có `golden_lock` nào bọc quanh
    `write_text`/`finally`. Thêm `tests/regression/generate_dataset.py` (đã đọc code xác nhận
    dòng 148-162) — tự backup bằng `shutil.copy` tên CỐ ĐỊNH `.md.posverify_bak` (không PID/random),
    ghi đè `EPISODE_PATH` thật, không `golden_lock` — rủi ro CAO HƠN 6 file kia vì backup tên cố
    định 2 tiến trình có thể giẫm lên nhau. **(Phụ, khác loại — không tính vào 7):**
    `tools/rewrite_ep01_final.py` là công cụ sửa nội dung 1 lần thủ công (không tự restore), rủi ro
    thấp hơn nhưng vẫn ghi trực tiếp EP01 thật không khóa — cần lưu ý nếu chạy khi có phiên khác
    đang test.
    **Nguyên nhân lặp lỗi (đúng R_SUPREME test_process_failure_principle):** cả 2 vòng fix trước
    đều vá ĐÚNG file đã biết, KHÔNG có bước quét toàn diện có hệ thống → đề xuất quy trình:
    xem `prompts/TASK_DEBT005_ENFORCEMENT_ROUND3.md` (viết bởi CMD_AUDIT 9/7) — thêm 1 test tự
    động quét TOÀN BỘ `tests/`/`tools/` chặn mọi writer mới vào `output/ep_01/` không qua
    `golden_lock`, biến việc "tự grep tay" thành cưỡng chế máy vĩnh viễn.
  - **CLOSED VÒNG 3 (2026-07-09, CMD_BUILD_2, theo `prompts/TASK_DEBT005_ENFORCEMENT_ROUND3.md`):**
    - **D1 — vá writer:** bọc `with golden_lock():` quanh đúng đoạn đọc-ghi-restore của 6 file
      `tests/cases/` (`test_action_repeat`, `test_anti_generic`, `test_fact_contradiction`,
      `test_name_repetition`, `test_object_state`, `test_tts_pause`) + `tests/regression/generate_dataset.py`
      (đổi backup cố định `.md.posverify_bak` → theo PID + thêm try/finally). KHÔNG đổi 1 assert nào —
      chỉ thêm khóa; cả 7 chạy standalone giữ nguyên hành vi (5+7+4+3+3+6 case + 3 pytest PASS).
    - **Writer thứ 8 + 9 TỰ TÌM THÊM (R9, ngoài 7 trong task doc):** enforcement test tự phát hiện
      `tests/regression_runner.py` (mutate EPISODE qua `shutil.copy(f, EPISODE)` vòng lặp, backup cố
      định, không khóa) → vá golden_lock + backup PID. Và `tools/text_batch_fix.py::main()` (`--apply`
      ghi `EPISODE`+`GOLDEN` thật — vòng 1 chỉ vá `verify_post_fix`, bỏ sót `main`). text_batch_fix là
      công cụ `--apply` THỦ CÔNG (0 caller tự động) nên xử như `rewrite_ep01_final.py`: whitelist +
      cảnh báo docstring (đúng luật task: manual tool không bắt buộc golden_lock, tránh import tools→tests).
    - **D2 — cưỡng chế máy (phần "quy trình"):** `tests/test_no_unlocked_ep01_writer.py` quét TĨNH
      `tests/**/*.py`+`tools/*.py`: bắt file có BIẾN trỏ ep_01 THẬT (loại tempfile ghép mảnh) + ghi
      vào biến đó (`.write_text`/`open(...,'w')`/`shutil.copy|move(...,VAR)`/`os.replace(...,VAR)`/
      helper `*write*(VAR`) mà THIẾU `golden_lock` → FAIL in rõ tên. Whitelist tường minh đóng
      (`_MANUAL_TOOL_EXCEPTION` = 2 manual tool, có test riêng chống "danh sách trắng mở"). **Mutation
      proof:** gỡ `golden_lock` khỏi từng file trong 7 file đã vá → `_classify` lật `guarded`→`offender`
      (chứng minh không phải test rỗng). Kết quả scan hiện tại: **0 offender, 11 guarded, 2 whitelisted**.
    - **Bằng chứng số:** `architecture_registry_check` 0/0/0 (đã đăng ký file test mới, total 366→367);
      `pytest tests/ -q` = **612 passed, 0 failed** (610 + 2 test registry đổi xanh sau khi map file mới);
      enforcement test 3/3 PASS. Baseline KHÔNG giảm (tăng do +3 test mới).

---

## DEBT-006: Rule R86 (`qa_eol_diacritic.py`, gọi qua `text_batch_fix.py::verify_post_fix`) KHÔNG bắt được lỗi EOL "cũ." như test kỳ vọng — nghi regression thật, chưa rõ nguyên nhân

- **Phát hiện:** 2026-07-05 tối, kiểm duyệt — trong lúc điều tra DEBT-005, `tests/cases/test_audio_gate_regression.py::case_5_substitute_violates_r111()` FAIL tại dòng `assert "R86" in failed, "R86 should fail on 'cũ.' EOL but didn't"` — reproduce được ổn định khi chạy riêng lẻ (không phải nhiễu đồng thời, khác hẳn DEBT-005).
- **Bằng chứng:** Case 5 thay câu gốc "Khải-Phong đang ngồi trên ghế số bảy của chuyến xe đêm." thành "Khải-Phong đang ngồi trên ghế số bảy đó cũ." (kết thúc bằng "cũ." — âm/dấu thanh mà R86 khai là phải bắt được theo tên rule `qa_eol_diacritic` broad NGA+NANG+HOI). `verify_post_fix(bad_text, ["R86"])` trả về danh sách `failed` KHÔNG chứa "R86" — nghĩa là `tools/qa_eol_diacritic.py` chạy qua câu này và KHÔNG báo lỗi, trái với kỳ vọng test đã ghi từ trước.
- **Chưa xác định:** đây là (a) `qa_eol_diacritic.py` bị thay đổi/suy yếu ở đợt sửa nào đó gần đây (cần `git log` riêng file này để tìm), hay (b) chữ "cũ." thực ra KHÔNG thuộc phạm vi R86 broad NGA+NANG+HOI đúng như thiết kế ban đầu và test case_5 đang kỳ vọng sai (test lỗi thời), hay (c) lỗi khác trong luồng gọi (`tool_map`/`subprocess` trong `verify_post_fix`). Kiểm duyệt CHƯA điều tra sâu tới mức kết luận, chỉ xác nhận hiện tượng thật + reproduce được.
- **Đề xuất fix:** CMD rảnh chạy `git log --oneline -- tools/qa_eol_diacritic.py` tìm thời điểm/lý do thay đổi gần nhất, đối chiếu trực tiếp logic hàm bắt EOL với câu "cũ." để xác định (a)/(b)/(c) ở trên trước khi sửa bất kỳ đâu — không tự đoán hướng sửa khi chưa rõ nguyên nhân.
- **Trạng thái:** **OPEN** — chặn CI gate của MỌI phiên cho tới khi sửa (pytest suite FAIL thật do assertion này, không phải do phiên nào cụ thể).
  - **Trạng thái cập nhật:** **CLOSED** (2026-07-05, CMD_BUILD_3, pack `debt005_006_fix`) — **KHÔNG phải (a) hay (b)**: đọc trực tiếp `check_word_eol()`/`scan()` trong `tools/qa_eol_diacritic.py` và tự chạy trên đúng câu "Khải-Phong đang ngồi trên ghế số bảy đó cũ." (kể cả gọi `scan()` trực tiếp trên file tạm chứa toàn văn `episode.md` đã substitute) — hàm **BẮT ĐÚNG** `NGA` trên "cũ" ngay lần thử đầu tiên, không cần sửa gì. `git log --oneline -- tools/qa_eol_diacritic.py` chỉ có 4 commit, không có commit nào gần đây làm suy yếu phạm vi bắt lỗi.
  - **Kết luận nguyên nhân gốc thật (loại (c), cụ thể hơn):** đây là **HỆ QUẢ TRỰC TIẾP của DEBT-005** — tại thời điểm kiểm duyệt phát hiện lỗi, `output/ep_01/episode.md` rất có thể đã bị 1 tiến trình khác ghi đè/làm nhiễu tạm thời do đúng cơ chế race-condition mô tả ở DEBT-005 (2 phiên cùng chạy `pytest`/`ci_gate.py` trên `C:\Users\Admin\SVHMP_git` dùng chung), khiến nội dung file lúc `case_5` chạy KHÔNG PHẢI bản gốc sạch — không phải lỗi logic trong `qa_eol_diacritic.py` hay assertion sai của test.
  - **Bằng chứng xác nhận (đã tự kiểm chứng, không suy đoán):**
    - Chạy `case_5_substitute_violates_r111()` **3 lần liên tiếp** trên worktree sạch (đơn tiến trình, dữ liệu gốc không nhiễu) → **cả 3 lần đều PASS** ("R86 self-verify caught bad substitute") — không tái hiện được hiện tượng "R86 không bắt".
    - Sau khi fix DEBT-005 (`verify_post_fix()` chạy trên tempfile riêng), nguyên nhân khiến file thật có thể bị nhiễu bởi tiến trình khác **không còn tồn tại** — đóng đồng thời cả 2 debt bằng cùng 1 fix.
  - **Không sửa** `tools/qa_eol_diacritic.py` (đã xác nhận đúng, không suy yếu) và **không sửa** assertion của `case_5` (kỳ vọng "R86 phải fail trên 'cũ.'" là ĐÚNG) — chỉ tài liệu hoá phát hiện tại đây.

**Ghi chú hợp nhất (merge G3 vào main, 5/7):** nhánh `build/g3-dialogue-d0-d8` có 1 bản DEBT-004 khác do CMD_BUILD_3 tự ghi độc lập (cùng phát hiện scene_context↔12-knob, sớm hơn về thời gian nhưng ít chi tiết hơn bản trên) — đã hợp nhất, giữ bản kiểm duyệt (đầy đủ hơn, đã có G6a thật để đối chiếu một phần), không nhân đôi entry.

---

## DEBT-007: `tools/decision_engine.py::build_packet()` tra `plan.get("plan_ref")` — key này KHÔNG tồn tại trong output thật của `tools/story_planner.py`, nên `plan_ref` luôn `null` dù đã compose 2 manager với nhau

- **Phát hiện:** 2026-07-09, CMD_BUILD khi build G7 D2 (`tools/episode_generator.py`), lần đầu tiên gọi `decision_engine.build_packet(1, plan=story_planner.build_episode_plan_ep01())` (2 manager G6a/G6b được ghép thật, chưa ai làm việc này trước đó — `decision_engine.py` dòng 61-62 tự ghi "story plan thật (G6b, runtime/story_planner.py CHƯA xây)" dù G6b đã build xong từ 5/7, tức comment đã lỗi thời).
- **Bằng chứng (đã tự chạy thật, không suy đoán):** `python tools/episode_generator.py 1` → `decision_packet.status: full` (đúng, vì `plan is not None`) NHƯNG `decision_packet.plan_ref: null`. Nguyên nhân: `build_packet()` dòng 56 gọi `plan.get("plan_ref")`, nhưng `story_planner.build_episode_plan_ep01()` trả về dict với field `episode_number`/`season_ref`/`scenes`/... (đúng theo `governance/blueprint/schemas/story_plan_schema.yaml` đã duyệt APPROVED_A) — **không có field nào tên `plan_ref`**. Đây là do `decision_engine.py` được viết trước khi `story_plan_schema.yaml` được field-hóa/duyệt, tự đặt tạm tên field `plan_ref` không khớp bản duyệt sau này.
- **Phạm vi:** `tools/decision_engine.py::build_packet()` — chỉ ảnh hưởng field `plan_ref` trong packet trả về; `per_scene`/`knobs` không bị ảnh hưởng (không phụ thuộc `plan_ref`).
- **Không tự sửa** `tools/decision_engine.py` (không phải file của pack `g7_generator` — thuộc domain `decision_engine`/G6a, per bài học #9 TASK_G7 "cross-domain tiện thể sửa luôn" đã xảy ra 2 lần trước, không lặp lại lần 3). `episode_generator.py` (D2) chỉ gọi đúng API có sẵn với tham số `plan` đã có sẵn trong signature — không cần sửa gì phía generator để expose đúng finding này (packet output đã trung thực tự thể hiện `plan_ref: null`).
- **Đề xuất fix:** đổi `plan.get("plan_ref")` thành 1 giá trị tổng hợp thật từ `episode_number`+`season_ref` (vd `f"ep{plan['episode_number']}_{plan['season_ref']}"`) hoặc thêm field `plan_ref` vào chính `story_plan_schema.yaml`/`build_episode_plan_ep01()` nếu Mr.Long muốn giữ tên field `plan_ref` xuyên suốt — cần Mr.Long chọn hướng (đổi bên đọc hay đổi bên nguồn), không tự quyết vì đụng 2 domain khác nhau.
- **QUYẾT ĐỊNH Mr.Long (9/7, qua CMD_AUDIT):** hướng **(a) — sửa bên đọc** (`decision_engine.py`), KHÔNG đụng `story_plan_schema.yaml`. Lý do: schema đã LOCKED v1.0 (duyệt chính thức qua RFC), sửa thêm field phải qua lại quy trình nặng; `decision_engine.py` tự thừa nhận `plan_ref` là tên đặt tạm TRƯỚC khi schema được duyệt — bên đọc đoán sai, không phải bên nguồn sai. Nguyên tắc: schema đã duyệt là chuẩn, reader theo schema.
  - **Fix cụ thể:** `build_packet()` dòng 56, đổi `plan.get("plan_ref")` → `f"ep{plan['episode_number']}_{plan['season_ref']}"` (dùng 2 field đã có sẵn thật trong `story_plan_schema.yaml` APPROVED_A, không bịa field mới).
  - **LƯU Ý — `decision_engine.py` đã LOCKED** (`architecture_registry.yaml` `enterprise_pack_progress.decision_engine: locked`, tag `g6a-decision-engine-v1.0`, dù `blueprint_domains.yaml` BP0 ghi `lifecycle: draft` — 2 nguồn tracking khác nhau, đã ghi nhận mâu thuẫn này trong `prompts/CMD_AUDIT_G7.md` dòng G7-4b). Đây là **TU CHỈNH có ủy quyền** (per Mr.Long authorization 9/7, mirror mẫu `bp4_runtime`/`bp6_decision` đã dùng trước — sửa 1 dòng cụ thể đã duyệt, KHÔNG đổi nội dung/hành vi nào khác của pack đã lock). CMD thực thi PHẢI ghi rõ "per Mr.Long authorization 9/7" trong commit message, và cập nhật dòng `decision_engine: locked` trong `architecture_registry.yaml` thêm 1 câu "TU CHINH 9/7" theo đúng mẫu 2 dòng kia — KHÔNG tạo lock mới, KHÔNG đổi tag.
  - **Regression bắt buộc:** chạy lại `python tools/episode_generator.py 1` sau khi sửa — xác nhận `decision_packet.plan_ref` KHÔNG còn `null`, đúng format `ep1_<season_ref thật>`. Chạy `pytest tests/test_g6a_decision_engine.py tests/test_g7_generator.py -q` xanh, không giảm baseline.
- **Trạng thái:** **CLOSED** (2026-07-09, CMD_BUILD, pack `debt007_fix`, per Mr.Long authorization 9/7).
  - **Đã sửa:** `tools/decision_engine.py::build_packet()` dòng 56, đúng nguyên văn hướng (a) đã duyệt — `plan.get("plan_ref")` → `f"ep{plan['episode_number']}_{plan['season_ref']}"`. `governance/architecture_registry.yaml` dòng `decision_engine: locked` bổ sung câu "TU CHINH 9/7" (mirror mẫu `bp4_runtime`/`bp6_decision`) — không tạo lock mới, không đổi tag.
  - **Bằng chứng (đã tự chạy thật):** `python tools/episode_generator.py 1` → `decision_packet.plan_ref: ep1_season_1` (không còn `null`). `pytest tests/test_g6a_decision_engine.py tests/test_g7_generator.py -q` → 30/30 PASS. Full suite `pytest tests/ -q` → 624 passed, 0 fail. `architecture_registry_check.py` → PASS 0/0/0.

---

## DEBT-008: `tools/dialogue_generator.py::write_episode_line()` — docstring cam kết "KHÔNG BAO GIỜ trỏ vào 50 tập thật đã locked" nhưng KHÔNG có guard code enforce

- **Phát hiện:** 2026-07-10, CMD_AUDIT (workflow audit đa-agent 222 agent, 32 finder × 4 lens, 3-skeptic phản biện độc lập, 9-10/7) — tự kiểm chứng độc lập lại bằng cách đọc trực tiếp code, xem `prompts/TASK_AUDIT_CRITICAL_G3_G5.md` Bug #1.
- **Bằng chứng (đã tự đọc code, không suy đoán):** Đọc trực tiếp dòng 214-234 (trước fix): docstring dòng 217 cam kết "KHÔNG BAO GIỜ trỏ vào 50 tập thật đã locked", nhưng thân hàm không có 1 dòng guard nào — `out.write_text(text, encoding='utf-8')` chạy vô điều kiện. Gọi `write_episode_line(REPO/'output', 5, line)` sẽ ghi đè thật `output/ep_05/episode.md` (tập đã lock).
  - **Rủi ro thật tại thời điểm phát hiện (đã grep toàn repo):** chỉ có 3 caller — 2 test dùng `tmp_path` (an toàn), 1 caller production (`tools/g3_dialogue_check.py:124`) gọi với `root=REPO/'output'` + `ep_n='g3_sample'` (chuỗi, an toàn nhờ KỶ LUẬT của caller, không phải do code chặn). Chưa bị khai thác, nhưng đúng lớp lỗi race/overwrite mà DEBT-005 đã xử lý cho 6+ writer khác — hàm này lọt hoàn toàn qua `tests/test_no_unlocked_ep01_writer.py` vì đường dẫn ghép động bằng f-string, không phải literal `"ep_01/episode.md"` mà regex quét tĩnh tìm.
- **Phạm vi:** `tools/dialogue_generator.py::write_episode_line()` — domain `dialogue` (G3), đã LOCKED (`dialogue-v1.0`).
- **Trạng thái:** **CLOSED** (2026-07-10, CMD_BUILD, pack `audit_critical_g3_g5`, per Mr.Long authorization 10/7 — TU CHỈNH file đã LOCKED, mirror mẫu `bp4_runtime`/`bp6_decision`/DEBT-007).
  - **Đã sửa:** thêm guard — nếu `Path(root).resolve() == (SVHMP/'output').resolve()` (production root) VÀ `ep_n` là số (int hoặc chuỗi toàn chữ số, `int(ep_n)` thành công) → `raise ValueError` rõ ràng. KHÔNG đổi hành vi 2 tổ hợp hợp lệ cũ (tmp_path bất kỳ ep_n nào; root production + ep_n chuỗi non-numeric — đúng pattern `g3_dialogue_check.py` đang dùng thật). `governance/architecture_registry.yaml` dòng `dialogue: locked` bổ sung câu "TU CHINH 10/7".
  - **Bằng chứng (đã tự chạy thật, mutation-proof):** `tests/test_write_episode_line_production_guard.py` (5 test, dùng `tmp_path` giả lập production root qua monkeypatch — TUYỆT ĐỐI không đụng `output/` thật kể cả khi mutate): (1) raise đúng tổ hợp nguy hiểm (numeric + string-numeric); (2)+(3) 2 tổ hợp hợp lệ cũ không đổi hành vi; (4) mutation-proof — đọc source thật, gỡ guard block trong bộ nhớ, `exec()` vào namespace riêng, xác nhận hàm mutated KHÔNG còn raise (chứng minh guard gốc thật sự là nguyên nhân chặn). `tests/test_g3_dialogue.py` (24 test, bao gồm 2 test `write_episode_line` cũ) + `g3_dialogue_check.py` (caller production thật) vẫn PASS y nguyên. Registry 0/0/0, full suite xanh.

---

## DEBT-009: `tools/supernatural_validator.py::run_all()` — composition 3 sub-check KHÔNG có test thật, xóa hết cả 3 vẫn có thể PASS

- **Phát hiện:** 2026-07-10, CMD_AUDIT (workflow audit đa-agent 222 agent, 9-10/7) — tự kiểm chứng độc lập kèm 1 mutation sống, xem `prompts/TASK_AUDIT_CRITICAL_G3_G5.md` Bug #2.
- **Bằng chứng (đã tự đọc code + tự mutation sống, không suy đoán):** Đọc dòng 157-162 (trước fix): `run_all()` cộng dồn 3 sub-check (`check_typology`/`check_possession_state_machine`/`check_no_duplicate_compliance_files`). Test DUY NHẤT gọi `run_all()` (`tests/test_supernatural_validator.py:30`) chỉ `assert run_all() == []` trên dữ liệu sạch — các test mutation khác (M2/M3/M4/M7) đều gọi THẲNG từng sub-check với dữ liệu giả, KHÔNG qua `run_all()`. CMD_AUDIT tự monkeypatch `run_all` thành hàm rỗng `return []` trong bộ nhớ → gọi lại → kết quả `[]`, y hệt baseline sạch — nếu ai vô tình xóa 1/3 hoặc cả 3 dòng `errs += check_*()` trong code thật, gate `g5_supernatural_check.py` (chạy `run_all()` qua CI) vẫn báo PASS trên dữ liệu sạch (2 sub-check còn lại không phát hiện lỗi trên chính dữ liệu đó). Đúng lớp lỗi `qa_post_render.audit_pause()` đã bắt ở G8 D3 (xem entry D3 pause-delegation, `governance/pack5` báo cáo), lần này ở G5 chưa ai vá.
- **Phạm vi:** `tools/supernatural_validator.py::run_all()` — domain `supernatural` (G5), đã LOCKED (`g5-supernatural-v1.0`).
- **Trạng thái:** **CLOSED** (2026-07-10, CMD_BUILD, pack `audit_critical_g3_g5`, per Mr.Long authorization 10/7 — TU CHỈNH file đã LOCKED).
  - **Đã sửa (phương án a — mutation-proof trực tiếp trên nguồn, ưu tiên theo task):** thêm hàm thuần `_run_all_body_ok(src)` vào `supernatural_validator.py` (generalize/mirror `tools/g8_qa_runtime_check.py::_pause_delegation_body_ok`, R211 không viết lại logic từ đầu) — kiểm body `run_all()` PHẢI chứa đủ 3 dòng `errs += check_*()`. `governance/architecture_registry.yaml` dòng `g5_supernatural: locked` bổ sung câu "TU CHINH 10/7".
  - **Bằng chứng (đã tự chạy thật, mutation-proof đủ cả 3 sub-check):** `tests/test_supernatural_run_all_composition.py` (7 test): static proof trên source thật + 3 mutation-proof RIÊNG BIỆT (gỡ từng dòng 1/3 sub-check — kể cả `check_no_duplicate_compliance_files` là sub-check cuối, dễ bị "quên" nhất) đều xác nhận `_run_all_body_ok` lật sang FAIL đúng như task yêu cầu ("đủ cả 3 sub-check, không sub-check nào bị quên") + 1 mutation gỡ cả 3 cùng lúc + 1 test injection bổ sung (phương án b, không thay thế a) qua `monkeypatch` `check_typology` trả lỗi giả, xác nhận `run_all()` propagate đúng qua đường composition thật (không gọi thẳng sub-check). `tests/test_supernatural_validator.py` (17 test cũ) + `g5_supernatural_check.py` vẫn PASS y nguyên. Registry 0/0/0, full suite xanh.
  - **BỔ SUNG 10/7 (follow-up, không mở lại — vá kín khoảng hở còn sót):** CMD_AUDIT tự mutation độc lập phát hiện thêm: `_run_all_body_ok()` mới chỉ được pytest gọi tới (qua `tests/test_supernatural_run_all_composition.py`) — chạy `python tools/g5_supernatural_check.py` RIÊNG LẺ (ngoài pytest, đúng cách CI thật gọi qua `ci_gate.py`) KHÔNG bắt được nếu ai xóa hết 3 dòng composition (gate cũ chỉ gọi `run_all()` rồi tin thẳng kết quả `[]`). Đã **wire `_run_all_body_ok()` làm invariant thứ 2** (`run_all_composition`) trực tiếp vào `tools/g5_supernatural_check.py::SUITE`, mirror đúng cách D3 wire `_pause_delegation_body_ok` vào `g8_qa_runtime_check.py` (đọc file source, in ma trận PASS/FAIL, R211 không viết lại logic). **Test lại trên đĩa THẬT (không dùng file production)**: tạo 2 bản copy tạm `tools/_mutation_test_supernatural_validator.py` + `tools/_mutation_test_g5_check.py` (đặt trong `tools/` để `SVHMP = Path(__file__).resolve().parent.parent` resolve đúng repo thật), xóa cả 3 dòng `errs += check_*()` trong bản copy, chạy gate copy độc lập → xác nhận **FAIL đúng** (`run_all_composition` FAIL, liệt kê đủ 3 sub-check thiếu, exit 1) — trước khi wire, cùng thao tác này cho kết quả PASS sai (đã tự bắt được lỗi trong chính phương pháp test lần đầu: quên trỏ `check_run_all_composition()` đọc đúng file copy thay vì file thật, sửa lại rồi mới ra kết quả đúng). Xóa sạch 2 file tạm ngay sau khi test, xác nhận `git status` không còn dấu vết, file production `tools/supernatural_validator.py` không hề bị đụng vào trong suốt quá trình. Thêm 2 test bảo vệ chính việc wiring (`test_g5_gate_has_run_all_composition_invariant_wired` + `test_g5_gate_pass_on_real_data`, unwire-guard mirror D3) vào `tests/test_supernatural_run_all_composition.py` (9 test tổng). Registry 0/0/0, full suite xanh.

---

## DEBT-010: `tools/architecture_registry_check.py` — không đối chiếu `ownership_matrix` với tác giả/commit thật (nợ quy trình, KHÔNG phải bug code)

- **Phát hiện:** 2026-07-10, audit đa-agent (workflow G2-G8, finding #1 MEDIUM `TASK_AUDIT_MEDIUM_LOW_G2_G8.md`).
- **Bằng chứng:** checker R211 chỉ kiểm MISSING/UNMAPPED/DUP theo path tĩnh; không có cơ chế đối chiếu `ownership_matrix` (dòng 49 registry) với tác giả/commit thực tế đã sửa file → vi phạm cross-domain-write (vd lớp DEBT `bp4_runtime`/`bp6_decision`) KHÔNG tự động bị bắt, phải chờ audit thủ công.
- **Phạm vi:** nợ quy trình. Xây checker đối chiếu `git log --follow -- <file>` tác giả gần nhất với `ownership_matrix` là việc lớn.
- **KHÔNG tự sửa** (per task: cần Mr.Long xác nhận phạm vi trước — tương tự DEBT-003 chờ ACE-Step). Chờ quyết định hướng.

---

## DEBT-011: `bible/37_character_schema.yaml` — invariant G5 dựa trên field `alive_status` chưa từng được điền (roster dùng `life_status` khác tên/enum)

- **Phát hiện:** 2026-07-10, audit đa-agent (finding #13 MEDIUM).
- **Bằng chứng (đã tự grep thật):** bible/37 khai `alive_status` BẮT BUỘC (tier_1_mandatory.core_id, dòng 29) + là căn cứ invariant G5 (dòng 126: `entity_class=linh_hon PHẢI khớp alive_status=ghost`). Nhưng `grep alive_status runtime/passenger_roster_100.yaml` = **0 lần**; `grep life_status` = **144 lần** (roster dùng field khác tên, enum khác). `roster_validator.py` TIER1_TOP cũng không kiểm `alive_status`.
- **Phạm vi:** đụng bible/37 (đã SIGNED) + roster schema — 2 hướng: (a) đổi tên field bible/37 thành `life_status` khớp data thật, hay (b) thêm `alive_status` thật vào roster + validator.
- **KHÔNG tự sửa** (per task: đụng bible SIGNED — cần Mr.Long chọn hướng trước). Chờ quyết định.

---

## DEBT-012: `tools/story_planner.py` — khai `BIBLE_16_KPI` + claim (blueprint) "đọc bible/16" nhưng `KPI_BUCKETS` hardcode, không có `_load(BIBLE_16_KPI)`

- **Phát hiện:** 2026-07-10, audit đa-agent (finding #17 MEDIUM).
- **Bằng chứng (đã tự đọc code + bible/16 thật):** `story_planner.py:24` khai hằng `BIBLE_16_KPI` nhưng grep toàn file KHÔNG có `_load(BIBLE_16_KPI)`; `KPI_BUCKETS` (dòng 37) hardcode `[("ep_1_10",1,10),("ep_11_30",11,30),("ep_31_90",31,90)]`. **bible/16 CÓ cấu trúc tương ứng:** `series_targets` với đúng 3 key `ep_1_10`/`ep_11_30`/`ep_31_90` (range mã hoá trong tên key). → option (a) đọc động khả thi (parse tên key `ep_X_Y` thành tuple), nhưng phải xử lý special_ep_targets (ep_73_PIVOT... không phải range đều).
- **KHUYẾN NGHỊ CMD_BUILD_2 (chờ Mr.Long chốt hướng):** thiên về **(b) — bỏ claim "đọc bible/16"** trong blueprint/registry, giữ `KPI_BUCKETS` hardcode + xoá hằng `BIBLE_16_KPI` chết. Lý do: (1) bible/16 IMMUTABLE, range đều đơn giản, hardcode ít rủi ro drift; (2) đọc động phải parse tên key + tách special_ep phức tạp hơn giá trị nó mang lại; (3) hằng chết `BIBLE_16_KPI` gây hiểu nhầm SSOT. Option (a) chỉ nên chọn nếu Mr.Long muốn KPI target thật (ctr/finish_rate...) được story_planner tiêu thụ — hiện KPI_BUCKETS chỉ dùng để map ep→tên bucket, KHÔNG đọc giá trị target.
- **KHÔNG tự sửa** (per task: nằm trong list "cần Mr.Long quyết định hướng"). Chờ chốt (a) hay (b).

---

## DEBT-013: `governance/blueprint/schemas/episode_schema.yaml` — `passenger_main required:true` mâu thuẫn hành vi EP01 (code luôn trả None, có test khoá None là đúng)

- **Phát hiện:** 2026-07-10, audit đa-agent (finding #24 MEDIUM).
- **Bằng chứng (đã tự grep thật):** `episode_schema.yaml:38` khai `passenger_main: {required: true, desc: "PHẢI là 1 PAS_id thật..."}`. Nhưng code EP01 luôn trả `None` và chính test `test_reality_passenger_main_none_not_fabricated_for_ep01` KHOÁ hành vi None này là ĐÚNG (EP01 pilot chưa có PAS_id thật — R195 "không bịa"). → schema và hành vi-đã-test mâu thuẫn.
- **Phạm vi:** đụng quyết định R195 cũ ("EP01 là pilot chưa có PAS_id"). 2 hướng: (a) `required: false` cho case EP01/pilot, hay (b) thêm điều kiện "required trừ pilot".
- **KHÔNG tự sửa** (per task: đụng quyết định R195 — cần Mr.Long chọn). Chờ quyết định hướng.

---

## DEBT-014: `tools/story_planner.py` — `scene_function` required:true nhưng 6 scene EP01 thiếu; `story_plan_schema_check.py` không kiểm hiện diện — **CLOSED 2026-07-11**

- **CLOSED:** Mr.Long chốt mapping 16:00 10/7 (đọc trực tiếp `episode_golden_text.md` dòng 96-515,
  không suy đoán): HOOK→`gay_nghi`, SETUP→`gay_nghi`, INCIDENT→`dan_chuyen`, REVEAL→`hy_sinh`,
  PAYOFF→`dan_chuyen`, CLIFFHANGER→`danh_lac_huong`. Đã thực thi cả 4 bước: (1) thêm hằng
  `EP01_COMPONENT_SCENE_FUNCTION` + field `scene_function` vào `build_episode_plan_ep01()`
  (`tools/story_planner.py`) — verify thật: `build_episode_plans()` trả đúng 6/6 giá trị khớp mapping.
  (2) thêm `check_scene_function_present()` (check 6/6) vào `story_plan_schema_check.py`, wired vào
  `run_checks()` — PASS 0 vi phạm trên dữ liệu thật. (3) +9 test mới `tests/test_g6b_story_planner.py`
  (M7: reality-anchor khớp mapping CHỐT + 4 mutation-proof thiếu/rỗng/enum-sai/hợp-lệ), cập nhật
  `test_m0_real_ep01_plan_clean` gộp check mới. (4) `g6_story_planner_check.py` 4/4 + `g7_generator_
  check.py` 5/5 vẫn PASS — domain `story_planner` LOCKED, TU CHỈNH ghi rõ dòng lock
  `architecture_registry.yaml`. pytest full suite xanh sau khi sửa.

- **Phát hiện:** 2026-07-10, audit đa-agent (finding #19 MEDIUM `TASK_AUDIT_MEDIUM_LOW_G2_G8.md`).
- **Bằng chứng (đã tự đọc code + schema thật):** `story_plan_schema.yaml:37-41` khai `scene_function: {required: true, values: [dan_chuyen, gay_nghi, danh_lac_huong, hy_sinh]}`. Nhưng `build_episode_plan_ep01()` (dòng 106-113) KHÔNG output field `scene_function` cho cả 6 scene, và `story_plan_schema_check.py` KHÔNG có check hiện diện field này → thiếu sót lọt qua PASS.
- **Tại sao KHÔNG tự sửa ngay (DEFER, per R195 + R_SUPREME):** gán giá trị `scene_function` cho 6 scene EP01 là **phán đoán narrative-design, KHÔNG có nguồn data thật** để đối chiếu:
  - 6 scene EP01 = component_ref HOOK/SETUP/INCIDENT/REVEAL/PAYOFF/CLIFFHANGER (cấu trúc beat).
  - Golden EP01 (`output/ep_01/episode_golden_text.md`) chỉ gắn **emotion beat** (TÒ MÒ/BẤT AN/ĐỒNG CẢM/NGHẸN/DƯ ÂM), KHÔNG map sang 4 giá trị scene_function.
  - BP2 facet `scene_act_structure` (bp2/domain_specs.yaml:280) chỉ liệt kê 4 giá trị, KHÔNG map chi tiết beat→function.
  - → Gán bất kỳ giá trị nào vào output LOCKED = **bịa** (vi phạm R195). Thêm presence-check cũng CHẶN vì EP01 chưa có value → vỡ build.
- **PROPOSAL (cho Mr.Long chốt, KHÔNG tự áp):** mapping đề xuất dựa trên chuẩn narrative + semantic tiếng Việt (dan_chuyen=dẫn chuyện, gay_nghi=gây nghi, danh_lac_huong=đánh lạc hướng, hy_sinh=hy sinh):
  - HOOK → `gay_nghi` (mở đầu tạo nghi/móc câu) · SETUP → `dan_chuyen` (thiết lập/dẫn chuyện) · INCIDENT → `gay_nghi` (biến cố đẩy nghi) · REVEAL → `dan_chuyen` (hé lộ đẩy mạch) · PAYOFF → `hy_sinh` (cao trào/trả giá) · CLIFFHANGER → `danh_lac_huong` (gài hướng tập sau).
  - **Các beat mơ hồ cần Mr.Long xác nhận:** INCIDENT/REVEAL/PAYOFF (không suy ra duy nhất từ nội dung). Sau khi Mr.Long chốt mapping thật → mới (a) thêm scene_function vào output 6 scene + (b) thêm presence-check vào story_plan_schema_check.py.
- **KHÔNG tự sửa** (per task: R195 "không bịa" + đụng output schema LOCKED). Chờ Mr.Long chốt mapping.
- **Cross-ref G6b-3** (`TASK_AUDIT_HIGH_G2_G8.md`, 2026-07-10): cùng vấn đề (scene_function ownership
  chưa enforce), Mr.Long quyết định **hoãn** — gộp vào đợt build generator EP02+ (D2 hiện chỉ có EP01,
  chưa cấp thiết). Không tạo entry mới, ghi chung tại đây để không trôi mất + tránh trùng nợ kỹ thuật.

---

## DEBT-015: G5-3 (`TASK_AUDIT_HIGH_G2_G8.md`) — enforcement `entity_class<->alive_status` trong `story_consistency_validator.py` BỊ CHẶN bởi DEBT-011 chưa fix — **CLOSED 2026-07-10**

- **CLOSED:** DEBT-011 đã được CMD_BUILD_2 hoàn tất (commit `ef7348b`, `bible/37_character_schema.yaml`
  đổi `alive_status`→`life_status` + enum `song|da_mat|linh_hon`). G5-3 đã thực thi tiếp theo:
  thêm `validate_entity_class_life_status()` thật trong `tools/story_consistency_validator.py`
  (đối chiếu 2 chiều đúng lời hứa `character_ext_schema.yaml:99`), + `_self_check_entity_class_
  life_status()` wired vào `__main__`. 7 test mới trong `tests/test_g4_world.py` (clean/forward-
  mismatch/reverse-mismatch/missing-field-default/self-check-reality/mutation-proof/gate-wired).
  `g4_world_check.py` D4 vẫn PASS (exit 0). Đồng bộ luôn `character_ext_schema.yaml` (TU CHỈNH,
  AMENDMENT note) + `tools/supernatural_validator.py` docstring còn ref `alive_status` cũ.
  Phát hiện phát sinh khi thực thi → xem DEBT-016 ngay dưới (không tự quyết mà ghi nợ mới).

- **Phát hiện:** 2026-07-10, khi thực thi nhóm G5 (`TASK_AUDIT_HIGH_G2_G8.md`).
- **Bối cảnh:** G5-3 quyết định "thêm check thật vào `story_consistency_validator.py`" đối chiếu
  `entity_class=linh_hon` khớp `alive_status=ghost` (`bible/37_character_schema.yaml:126` +
  `governance/blueprint/schemas/character_ext_schema.yaml:99`, claim đã SIGNED). Nhưng field
  `alive_status` **KHÔNG tồn tại** trong `runtime/passenger_roster_100.yaml` (0 lần, roster dùng
  `life_status` khác tên + enum khác: `song|da_mat|linh_hon` thay vì `alive|dead|ghost` — xem
  DEBT-011 ở trên).
- **Mr.Long ĐÃ chốt hướng DEBT-011** (`PING_CMD_LEAD_29_06.md` 16:26, đã ping):
  hướng (a) đổi tên bible/37 sang `life_status` + enum `song|da_mat|linh_hon` + sửa dòng invariant
  126 thành `khớp life_status=linh_hon` — **giao CMD_BUILD_2 thực thi**, CHƯA thấy commit áp dụng
  tại thời điểm này (đã tự grep lại `bible/37` xác nhận còn nguyên `alive_status`/`alive|dead|ghost`).
- **Tại sao KHÔNG tự làm G5-3 ngay:** nếu viết enforcement bây giờ dùng field `alive_status` (khớp
  invariant hiện tại) thì code sẽ THÀNH DEAD/SAI ngay khi CMD_BUILD_2 đổi tên field sang
  `life_status` (theo hướng Mr.Long đã chốt); nếu tự ý dùng `life_status` để "đón đầu" thì lại tự ý
  suy đoán enum mapping (`song|da_mat|linh_hon`) thay vì để CMD_BUILD_2 làm đúng theo quyết định đã
  giao — rủi ro va chạm/làm trùng việc 2 session cùng sửa 1 invariant (đúng loại va chạm
  kinh nghiệm suýt trùng lặp đã ghi nhận với DEBT-014).
- **KHÔNG tự sửa** — chờ CMD_BUILD_2 hoàn tất DEBT-011 (đổi field+enum+invariant trong bible/37 và
  character_ext_schema.yaml), sau đó G5-3 mới viết enforcement thật trong
  `story_consistency_validator.py` đối chiếu đúng field/enum cuối cùng.

---

## DEBT-016: `entity_class` chưa được backfill cho 47/139 passenger có `life_status=linh_hon`

- **Phát hiện:** 2026-07-10, khi thực thi G5-3 (viết `validate_entity_class_life_status()` thật).
- **Bằng chứng (đã tự chạy thật trên roster):** `grep -c "life_status: linh_hon"
  runtime/passenger_roster_100.yaml` = **47**. `grep -c "entity_class" runtime/passenger_roster_100.yaml`
  = **4** (chỉ 2 passenger có khai, cả 2 đều `entity_class: nguoi`) — **0/139** khai `entity_class:
  linh_hon`. Field `entity_class` cũng **CHƯA được khai làm dataclass field** trong
  `tools/character_manager.py::CharacterProfile` (`_from_dict()` lọc theo `core_names` từ
  `dc_fields(CharacterProfile)`, `entity_class` không nằm trong đó nên bị loại âm thầm nếu đọc
  qua `CharacterRegistry`).
- **Tại sao KHÔNG phải bug code:** `entity_class` là field MỚI (G5 extension, Mr.Long ký 5/7,
  SAU KHI phần lớn roster đã có `life_status` từ trước qua `migrate_roster_v2.py` 27/6) — 47 ca
  "linh_hon" chưa khai `entity_class` là gap BACKFILL DỮ LIỆU tự nhiên do thứ tự thời gian, không
  phải logic sai. Với default schema (`nguoi`), `validate_entity_class_life_status()` áp dụng
  ĐÚNG theo lời hứa "đối chiếu 2 chiều" (`character_ext_schema.yaml:99`) sẽ báo cả 47 ca này là
  MISMATCH nếu wire làm gate chặn build — nhưng đó là báo cáo TRUNG THỰC (field thật sự vắng/dùng
  default sai với thực tế narrative "xe buýt ma"), không phải lỗi hàm.
- **Quyết định đã áp dụng (KHÔNG tự leo thang thành BLOCK):** hàm `validate_entity_class_life_status()`
  đã viết THẬT + mutation-proof đầy đủ (xem G5-3 ở trên), nhưng **KHÔNG wire vào gate chặn**
  (`g4_world_check.py`/`ci_gate.py`) — mirror đúng pattern `roster_validator.py` completeness
  (WARN-default, chưa BLOCK, `bible/37_character_schema.yaml:138-143`). `_self_check_entity_class_
  life_status()` chỉ REPORT số liệu thật (`print`), không `sys.exit(1)` vì lý do backfill gap.
- **KHÔNG tự backfill 47 passenger** (đụng `runtime/passenger_roster_100.yaml`, CMD_CHARACTER
  ownership per `governance/architecture_registry.yaml` ownership_matrix + cần quyết định
  narrative thật cho từng nhân vật — không phải suy luận máy) và **KHÔNG tự quyết định wire
  thành BLOCK** (đổi hành vi gate = quyết định sản phẩm, không phải bug fix). Chờ Mr.Long chốt
  hướng: (a) backfill `entity_class: linh_hon` cho 47 passenger rồi wire BLOCK, hay (b) giữ
  WARN-report vĩnh viễn (roster hầu hết là "linh_hon" theo premise truyện, có thể entity_class
  chỉ cần thiết cho `thuc_the_sieu_nhien`/`nhan_vat_lich_su` — số ít — không cần backfill hàng loạt).

---

## CẬP NHẬT TRẠNG THÁI DEBT-010..013 (2026-07-10, CMD_BUILD_2, per Mr.Long authorization 16:26)

Mr.Long chốt hướng 4/4 (PING 16:26, qua CMD_AUDIT tự kiểm chứng từng số). CMD_BUILD_2 thực thi:

- **DEBT-010 — DEFER XÁC NHẬN (b):** để nợ, dựa R215 + audit thủ công; KHÔNG xây enforcer git-blame lúc này (ROI thấp). Không đổi code.
- **DEBT-011 — CLOSED (a):** `bible/37_character_schema.yaml` đổi 3 chỗ: (1) core_id `alive_status`→`life_status`, (2) enum comment `alive|dead|ghost`→`song|da_mat|linh_hon` (khớp 139 giá trị THẬT: da_mat 90/linh_hon 47/song 2 — đã grep xác nhận, KHÔNG dịch 1-1), (3) invariant dòng 126 `alive_status=ghost`→`life_status=linh_hon`. Verify: YAML OK, roster_validator 0 violation, r205 16/0. **Bàn giao CMD_BUILD (G5-3):** `character_ext_schema.yaml:95,99` + `supernatural_validator.py` docstring còn ref `alive_status` — thuộc scope G5-3 (enforcement `entity_class<->life_status`), reconcile khi làm G5-3 (DEBT-015 nay ĐƯỢC GỠ CHẶN).
- **DEBT-012 — CLOSED (b):** `tools/story_planner.py` xóa hằng chết `BIBLE_16_KPI` (0 caller) + comment KPI_BUCKETS hardcode chủ ý; `blueprint_domains.yaml` story_planner domain xóa `bible/16` khỏi source_of_truth + sửa comment manager. Củng cố: bible/16:3 tự khai "Loaded by Publisher P7/P8/P9", chưa từng định cho story_planner. Verify: story_planner OK, 18 test pass.
- **DEBT-013 — CLOSED (b):** `episode_schema.yaml` passenger_main giữ `required:true` + thêm `pilot_null_exception:true` + desc "required trừ pilot" — EP01/pilot được null (R195, test_reality_passenger_main_none khóa), required PAS_id thật cho ep>1. Verify: g7 13 + #20 test pass.

Registry 0/0/0 sau mỗi sửa. Domain LOCKED chạm: g6b_story_planner (DEBT-012) + g7_generator (DEBT-013) → TU CHINH registry. bible/37 (DEBT-011) là bible SIGNED domain character (không có pack-lock registry) → ghi commit.

---

## DEBT-017..023: từ audit 18 completeness gap (CMD_BUILD_2, 2026-07-11, `TASK_AUDIT_COMPLETENESS_GAPS.md`)

> Chi tiết bằng chứng đầy đủ ở phần "KẾT QUẢ AUDIT" cuối `TASK_AUDIT_COMPLETENESS_GAPS.md`. DEBT-017
> đã fix phần chống-corrupt; các mục 018-023 là finding thật nhưng chạm TỐI THƯỢNG/bible/cơ-chế-mới
> → escalate Mr.Long (R_SUPREME R1, KHÔNG tự quyết). Số bắt đầu 017 vì 016 đã dùng (entity_class backfill).

## DEBT-017: `build_claim._save()` + `auto_watch.save_state()` — TOCTOU giữa 2 session cùng claim (residual) — **PARTIAL (atomic đã fix)**
- **Đã fix (gap #16):** `build_claim._save()` chuyển sang atomic (tmp+os.replace, commit `3a8868f`) — chống TRUNCATE/half-write khi ghi bị kill / nhiều CMD ghi. +1 test regression.
- **CÒN NỢ:** atomic KHÔNG chống TOCTOU — 2 session cùng `_load` pack là free rồi cùng `_save` claim → cả 2 tin mình sở hữu (last-writer-wins âm thầm). Chính công cụ chống-đụng-độ vẫn bị đánh bại bởi đúng concurrency nó phải chặn. Cần lock/compare-and-set (file-lock hoặc atomic CAS) = **cơ chế mới** → chờ Mr.Long quyết có xây không (hiện mitigate bằng phối hợp người + serialize git-push).
- **Phụ:** `auto_watch.py` thiếu single-instance guard (supervisor CÓ, auto_watch KHÔNG) + `save_state()` non-atomic → 2 daemon ghi đè `runtime/auto_watch_state.yaml`. Áp cùng pattern khi xử lý.

## DEBT-018: R197 FULL_TEXT_GATE — claim "trước MỌI render, không ngoại lệ" KHÔNG machine-true (gap #2 + #1) — **QUYẾT ĐỊNH Mr.Long 10/7: hướng (a)**
- Verify tận tay: 0 render entrypoint gọi `svhmp_preflight_qa.py`; render thật (`svhmp_v13_render.py`) chỉ gọi 1 tool `qa_eol_diacritic.py` (đúng thứ R197 CẤM "Text Gate với 1 tool") + 2 bypass (missing-md skip, cờ `--skip-r86`). `pack5/19_qa_pipeline.md:10` + `TASK_PACK5_BUILD.md:14` đã ghi "render KHÔNG gọi nó" → R197 (CLAUDE.md TỐI THƯỢNG) là văn bản chưa reconcile. Đúng lớp R215 (rule khẳng định, enforcer không tồn tại trên đường thật).
- **Liên quan #1 audio_render:** (1a) `svhmp_audio_qa.py` docstring "POST-RENDER mandatory/Block ship" vs `bp8/render_chain.yaml:73` đã ghi `enforcement_mode: manual`; (1b) R199 guard `aggressive_trim_tail` chết (render dùng `qa_clean_tail`), docstring còn "hardlock active"; (1c) "LOCKED v1.3" không checksum enforcer.
- **QUYẾT ĐỊNH (10/7, qua CMD_AUDIT):** hướng **(a)** — wire `svhmp_preflight_qa` vào render entrypoint thật, KHÔNG sửa lời R197 (hạ rule TỐI THƯỢNG xuống khớp code là đi lùi an toàn). **Thực thi theo 2 giai đoạn bắt buộc, KHÔNG được gộp:**
  - **Giai đoạn 1 (LOG-ONLY):** wire `svhmp_preflight_qa.py` vào `svhmp_v13_render.py` + các entrypoint render khác ở chế độ chỉ ghi log (không chặn), chạy thử trên toàn bộ 50 tập hiện có, báo cáo đầy đủ những gì SẼ bị chặn nếu bật thật (bao nhiêu tập, lỗi gì). KHÔNG tự ý bật chặn ở giai đoạn này.
  - **Giai đoạn 2 (CHẶN THẬT + bỏ `--skip-r86`):** CHỈ làm sau khi Mr.Long xem báo cáo giai đoạn 1 và xác nhận tiếp — nếu giai đoạn 1 cho thấy nhiều tập cũ sẽ FAIL, cần bàn hướng xử lý riêng (waiver 50 tập cũ hay bắt buộc regen) trước khi bật chặn.
- **Giai đoạn 1 KẾT QUẢ (11/7):** `reports/DEBT018_R197_PHASE1_LOG_ONLY_REPORT.md` — 50/50 tập sẽ bị chặn nếu bật Giai đoạn 2 ngay; 49/50 tập có vi phạm R86 THẬT (đọc trực tiếp `episode.md`, độ tin cậy cao — chỉ EP01 golden sạch); EP01 cũng có 22 issue khác (R1/R5/R10/R17, độ tin cậy THẤP cho EP02-50 vì chưa có spec.json thật, KHÔNG dùng làm căn cứ quyết định lúc này).
- **QUYẾT ĐỊNH Mr.Long 11/7 (qua CMD_AUDIT, sau khi tự xác nhận 2 việc):** (1) R86 là **hardlock kỹ thuật thật** của Mr.Long (29/6, `qa_eol_diacritic.py:2-3`: "BigVGAN không model accurate glottal stop → âm cụt/hụt hơi/lệch tone") — không phải rule quá đà, mỗi vi phạm là rủi ro chất lượng audio thật. (2) Tự kiểm tra `output/ep_NN/spec.json` cho cả 49 tập EP02-50 = **0 tập có file này** — chưa tập nào được render TTS thật, đây toàn bộ là văn bản CHƯA sản xuất audio, chưa có sản phẩm lỗi thật nào bị ảnh hưởng.
  - **KHÔNG waiver** (chấp nhận trước audio lỗi thật khi render sau — đi ngược lý do đặt hardlock).
  - **KHÔNG regen toàn bộ** (lãng phí — chỉ cần sửa đúng câu kết mang R86, không cần viết lại cả tập).
  - **HƯỚNG: sửa câu kết R86 cho 49 tập EP02-50 TRƯỚC KHI bật Giai đoạn 2** — đây là thời điểm rẻ nhất để sửa (chưa tốn công TTS/audio QA nào). Xem `prompts/TASK_DEBT018_R86_FIX_49EP.md` cho chi tiết thực thi. Giai đoạn 2 CHỈ bật sau khi 49 tập sạch R86 (chạy lại Giai đoạn 1 xác nhận 0 vi phạm).
  - 22 issue R1/R5/R10/R17 của EP01: CHƯA quyết — chờ có spec.json thật cho EP02-50 (ngoài phạm vi lúc này).
  - (1a)/(1b)/(1c) audio docstring: sửa khớp `enforcement_mode` thật SAU khi giai đoạn 2 xong (tránh sửa 2 lần nếu giai đoạn 1 đổi hướng).
- **GIAI ĐOẠN 1 XONG (11/7, CMD_BUILD):** wire LOG-ONLY vào `svhmp_v13_render.py` +
  chạy thử 50/50 tập, báo cáo đầy đủ tại `reports/DEBT018_R197_PHASE1_LOG_ONLY_REPORT.md`.
  Tóm tắt: **50/50 tập SẼ bị chặn nếu bật Giai đoạn 2 ngay** — 49/50 có vi phạm R86 EOL
  thật (chỉ EP01 golden sạch); **ngay cả EP01 (spec.json thật) cũng có 22 issue khác R86**
  (R1/R5/R10/R17). Phát hiện thêm 1 bug trong lúc wire: `svhmp_preflight_qa.py` resolve
  sai `episode.md` path cho spec.json sản xuất thật (đã fix + test, xem báo cáo mục 4) —
  đây chính là cơ chế "missing-md skip" đã ghi ở dòng trên. **Chờ Mr.Long xem báo cáo
  quyết Giai đoạn 2** (waiver 50 tập cũ hay bắt buộc regen, có nên phủ luôn `render_
  chunk.py`/`render_section.py` không — 2 script này KHÔNG phải entrypoint chính theo
  `bp8/render_chain.yaml`, chưa được wire ở Giai đoạn 1).

## DEBT-019: security latent — `dialogue_generator.write_episode_line()` non-numeric `ep_n` chưa sanitize (gap #18) — **CLOSED (ghi nhận, không hành động)**
- 3 entrypoint chính (svhmp_v13_render/episode_generator/dialogue_generator) đều SẠCH với input trusted-operator + int-validate. Latent: `write_episode_line()` với `ep_n` non-numeric làm `Path(root)/f'ep_{str(ep_n)}'` — nếu `ep_n` chứa `../` sẽ traverse. KHÔNG reachable từ input untrusted (chỉ test/sandbox truyền literal), đã có guard production-overwrite.
- **QUYẾT ĐỊNH (10/7):** không cấp thiết, không hành động — rủi ro không tồn tại trên đường thật hiện tại. Nếu sau này `write_episode_line()` được wire tới input ngoài, thêm guard `str(ep_n).isidentifier()` lúc đó.

## DEBT-020: bible/23 naming — text khẳng định uniqueness tuyệt đối nhưng 139 có 3 waiver canon chỉ ở code (gap #4) — **QUYẾT ĐỊNH Mr.Long 10/7: bổ sung tài liệu**
- forbidden-15 sạch (0 hit), word-uniqueness enforce THẬT (validator `word_owner` map, sẽ bắt collision mới ngoài 3 waiver). Drift: `bible/23:27-31` "TUYỆT ĐỐI KHÔNG dùng cùng WORD" + hook `100/100 unique / 200/200 syllable` — ở 139 có PAS_0151 "Hạ Nhi" (chia syllable Hạ với PAS_0013, Nhi với PAS_0033) + PAS_0131 "Nguyễn" (1-syllable), đều là canon episode names waived TRONG code validator (`C1_RULE02_CANON_EXEMPT_WORDS`) nhưng bible chưa ghi.
- **QUYẾT ĐỊNH (10/7):** bổ sung 1 mục "canon waiver" vào `bible/23` liệt kê đúng 3 ngoại lệ đã tồn tại trong `C1_RULE02_CANON_EXEMPT_WORDS` — KHÔNG đổi rule uniqueness gốc, chỉ ghi nhận ngoại lệ đã chạy thật khớp code. Giao CMD_BUILD_2.

## DEBT-021: regret distribution — metadata `distribution_actual` stale (per-100) + không enforcer recompute (gap #5) — **QUYẾT ĐỊNH Mr.Long 10/7: hướng (b)**
- `passenger_roster_100.yaml:16-21` header `distribution_actual: {32/24/20/14/10}` (=100) là số CŨ; thật ở 139 = family 40 / love 31 / promise 29 / kindness 23 / self 15 + 1 RFC_PENDING (PAS_0151 pillar chưa gán, assigned_ep null). Tỷ lệ ~ tương đương target per-100 (drift nhẹ, kỳ vọng vì target là /100). 27 sub-archetype phủ đủ, 0 ID bịa.
- **QUYẾT ĐỊNH (10/7):** hướng **(b)** — KHÔNG rebalance 139 người (đụng dữ liệu nhân vật đã khoá, rủi ro lớn hơn lợi ích cho lệch nhẹ đã kỳ vọng). Cập nhật `distribution_actual` = số thật (40/31/29/23/15) + thêm enforcer tự tính lại mỗi khi roster đổi + xử nốt `PAS_0151` RFC_PENDING (gán pillar thật, không để treo). Giao CMD_BUILD_2.

## DEBT-022: R200 audit_ping honor-system — không có anti-omission gate (gap #6) — **CLOSED (defer, mirror DEBT-010)**
- `log_ping.py` thuần append, 0 verify. `verify_ping_claim.py` chỉ check claim→fact (chống BỊA trong log), KHÔNG check fact→claim (CMD fix+push mà QUÊN log = 0 gate bắt). git hooks chỉ `.sample` (không active). R200 "PHẢI log mỗi fix" là honor-system thuần — đúng lớp R215 "CHƯA CÓ ENFORCER".
- **QUYẾT ĐỊNH (10/7):** defer, giống hệt lý do DEBT-010 — xây gate đối chiếu commit↔ping là cơ chế mới, ROI thấp khi R215 + audit chéo giữa CMD đã che phần lớn rủi ro. Không xây thêm lúc này.

## DEBT-023: legal content-instance — chưa có tool quét NỘI DUNG THẬT 50 tập cho HB01/HB02 (gap #17) — **QUYẾT ĐỊNH Mr.Long 10/7: rà tay 1 đợt ngay**
- `bp9_compliance_check.py` chỉ kiểm CẤU TRÚC schema HB01/HB02 (Nghị định 38/2021 + Điều 320 BLHS), KHÔNG quét nội dung episode đã render. `publish_gate.py` (runtime scanner) vẫn `planned` (khai trung thực). Rủi ro pháp lý thật.
- **QUYẾT ĐỊNH (10/7):** KHÔNG chờ xây `publish_gate.py` tự động (việc lớn, để sau) — giao CMD_BUILD_2 rà tay/bán tự động NGAY 50 tập hiện có theo checklist HB01/HB02 (Nghị định 38/2021 + Điều 320 BLHS), báo cáo tập nào nghi vấn. Xây scanner tự động là việc riêng, tách khỏi đợt rà tay này.

## DEBT-024: R210 "completeness gate" chỉ thực chặn 1/7 nhóm field tier_1_mandatory (voice) — **QUYẾT ĐỊNH Mr.Long 11/7: escalate, giao quét hệ thống**
- Phát hiện 11/7, CMD_AUDIT thử lại đúng phương pháp đã bắt R197 (DEBT-018) cho rule TỐI THƯỢNG khác — trúng ngay lần 2.
- **Bằng chứng (đã tự đọc code):** `bible/37_character_schema.yaml:21-22` khẳng định "Voice Profile + Relationship Graph = BẮT BUỘC. Không để field tier_1 trống trước khi sinh dialog (completeness gate)." `tier_1_mandatory` khai 7 nhóm (~40 field): core_id, background, psyche, voice, story, visual_recognition, relationships. Nhưng `dialogue_generator.py:159-163` — cổng chặn thật DUY NHẤT trước khi sinh thoại (`Tier1IncompleteError`) — chỉ kiểm nhóm `voice` (qua `dvv.MANDATORY_VOICE`). 6/7 nhóm còn lại, kể cả `relationships` (Relationship Graph) được gọi "BẮT BUỘC" ngang hàng Voice trong CÙNG câu, KHÔNG có cổng chặn nào.
- **Phạm vi:** đúng lớp "enforcer hẹp hơn claim" (mirror DEBT-018/R197) — nguy hiểm hơn "chưa có enforcer" vì tạo cảm giác an toàn giả (có gate, tưởng đủ, thực ra chỉ 1/7).
- **QUYẾT ĐỊNH (11/7):** KHÔNG tự vá ngay (rủi ro sai phạm vi, đụng dialogue domain LOCKED + bible/37 SIGNED) — giao đợt quét hệ thống rộng hơn (xem `prompts/TASK_AUDIT_RULE_ENFORCER_SWEEP.md`) để tìm hết các case tương tự trước khi quyết hướng sửa (xây đủ 7/7 gate, hay hạ claim khớp thực tế 1/7 đang chạy) — quyết riêng cho R210 sau khi có bức tranh đầy đủ hơn từ đợt quét.

---

## DEBT-025: R196 (CLAUDE.md TỐI THƯỢNG) — cấm từ "complete/done/100% hoàn thành" cho module chưa Production validated: 0 enforcer — **CLOSED (defer, mirror DEBT-010/DEBT-022)**

- **Phát hiện:** 11/7, `TASK_AUDIT_RULE_ENFORCER_SWEEP.md` (đợt quét CLAUDE.md TỐI THƯỢNG).
- **Bằng chứng (đã tự grep toàn repo):** `CLAUDE.md:9` khẳng định "**CẤM dùng từ 'complete / done / 100% hoàn thành'** cho module chưa Production validated. Dùng 'Engineering Validation PASS / Ready for Production Validation' thay thế." — văn phong CẤM tuyệt đối, TỐI THƯỢNG (ngang hàng R197). `grep -rln "R196\|Production Validated\|100% hoan thanh" tools/*.py` = **0 kết quả** — không có bất kỳ script/gate/commit-hook nào grep các từ cấm này trong report/commit message/docstring để chặn. So sánh: `check_rule_mention_codified.py` (pre-commit hook THẬT đang chạy, section A của `git_hook_pre_commit.py`) chỉ chặn pattern `"R{N} codified"` thiếu entry bible/00 — **hoàn toàn khác phạm vi**, không liên quan đến R196.
- **Phân loại:** THIẾU ENFORCER (không phải "hẹp hơn claim" — là **0 enforcer tuyệt đối**) cho 1 rule TỐI THƯỢNG. Rủi ro thực: bất kỳ report/commit message nào (kể cả của tôi) dùng "hoàn thành"/"done"/"complete" cho module chưa qua Production run đều KHÔNG bị chặn — chỉ dựa vào tự-kỷ-luật của executor (đúng loại rủi ro R215 đã cảnh báo).
- **KHÔNG tự xây enforcer ngay** (rule TỐI THƯỢNG + văn bản CLAUDE.md — theo R211 domain `LEAD`, chỉ Mr.Long sửa; xây gate cũng là quyết định kỹ thuật loại "code mới" cần Change Request Gate 6 câu trả lời trước, không tự leo thang trong 1 lượt quét). Đề xuất 2 hướng cho Mr.Long chọn: (a) xây `check_r196_banned_words.py` grep report/commit-msg mới nhất theo pattern tương tự `check_rule_mention_codified.py`, chặn nếu thấy từ cấm mà không kèm "Engineering Validation PASS"; (b) chấp nhận đây là kỷ luật tự-giác thuần (honor-system), ghi rõ trong CLAUDE.md "CHƯA CÓ ENFORCER — rủi ro drift" đúng tinh thần R215 mục 1(b) thay vì để ngỏ như hiện tại.
- **QUYẾT ĐỊNH Mr.Long (11/7):** defer, giống hệt lý do DEBT-010/DEBT-022 — đây là rule về ngôn từ báo cáo, khó xây enforcer tin cậy (phải quét toàn bộ text tự do đối chiếu trạng thái "đã Production validated" chưa — rủi ro false positive/negative cao). Dựa vào kỷ luật + review chéo giữa CMD, như đã áp dụng cho R200. Không xây thêm lúc này.

---

## DEBT-026: R210 "cân bằng xuyên 100 tập" — `character_balance_report.py` KHÔNG có gate/exit-code, KHÔNG wired ci_gate, roster THẬT đang lệch 4 target

- **Phát hiện:** 11/7, `TASK_AUDIT_RULE_ENFORCER_SWEEP.md`.
- **Bằng chứng (đã tự đọc code + chạy thật):** `CLAUDE.md:20` (R210) khẳng định "**Cân bằng xuyên 100 tập** theo target (trẻ em 10-15%, người già 15-20%, ≥3 vùng giọng, 9 kiểu chết, 5-8 nhân vật/tập) — `character_balance_report`" — nêu tên tool như bằng chứng đã enforce. Đọc `tools/character_balance_report.py::main()` (dòng 104-123): **0 `sys.exit()`** trong toàn file — chỉ `print()` các flag lệch (`⚠ FLAG LECH CAN BANG`), không có cơ chế FAIL nào. `grep character_balance_report tools/ci_gate.py` = **0 kết quả** — tool này **KHÔNG được wire vào `ci_gate.py`** (không nằm trong `CHECKS` list nào chạy tự động lúc pre-push). Caller duy nhất khác (`tools/roster_validator.py:7`) chỉ là dòng comment liệt kê, không phải import/call thật.
- **Chạy thật xác nhận roster ĐANG lệch target ngay bây giờ, không ai biết vì không có gate:** `python tools/character_balance_report.py` → **4 FLAG LECH CAN BANG** (`child 8.6% < target 10-15%`, `youth 30.2% > target 25-30%`, `middle 41.0% > target 30-35%`, `elderly 12.9% < target 15-20%`). Thêm 2 gap khác claim R210 không nhắc tới: (a) `death_type` — 50/139 (36%) là `khong_ro` (chưa phân loại) trong khi claim "9 kiểu chết" ngụ ý đã phân bổ đủ; (b) tool tự ghi chú "Roster chỉ track FOCAL/ep; secondary cast (5-8/tập) CHƯA quản lý" — nghĩa là target "5-8 nhân vật/tập" trong R210 **chưa từng được đo/kiểm** (chỉ track 1 nhân vật focal/tập).
- **Phân loại:** THIẾU ENFORCER (claim rule TỐI THƯỢNG nêu tên tool cụ thể như bằng chứng "đã cân bằng", nhưng tool đó chỉ là báo cáo đọc tay, không chặn gì, và dữ liệu thật đang lệch mà không ai bị cảnh báo tự động).
- **KHÔNG tự sửa ngay** (đụng `runtime/passenger_roster_100.yaml` LOCKED + quyết định sản phẩm "có nên wire thành BLOCK không, ngưỡng bao nhiêu" — ngoài phạm vi 1 lượt quét đọc). Đề xuất cho Mr.Long: (a) wire `character_balance_report.py` vào `ci_gate.py` ở chế độ WARN-only trước (mirror pattern `roster_validator.py` hoàn thiện dần), rồi cân nhắc BLOCK sau khi roster đã cân bằng lại; (b) bổ sung tracking secondary cast (5-8/tập) — hiện hoàn toàn chưa đo được; (c) xử 50 passenger `khong_ro` death_type còn treo.

---

## DEBT-027: `bible/23_passenger_naming.yaml` rule_03 (tuổi ↔ thời tên) — 0 enforcer — **Mr.Long 11/7: chưa đủ dữ liệu quyết, giao CMD điều tra phạm vi cụ thể trước**

- **Phát hiện:** 11/7, `TASK_AUDIT_RULE_ENFORCER_SWEEP.md`.
- **Bằng chứng (đã tự đọc code):** `bible/23_passenger_naming.yaml:59` (rule_03) khẳng định "TUỔI ↔ THỜI TÊN: nhân vật 58 tuổi (sinh ~196x) mang tên thời đó; **CẤM** tên trend trẻ cho người già." `tools/roster_validator.py::check_c4_naming_framework()` (hàm duy nhất kiểm bible/23 v1.1) **chỉ** kiểm: (1) version = v1.1, (2) `NAMING_RULES_REQUIRED` tồn tại làm KEY trong bible/23 (chỉ kiểm SỰ HIỆN DIỆN của key, không kiểm nội dung), (3) `region_dialect` dùng trong roster khớp `rule_06_region_match.style_by_region` — **không có bất kỳ dòng nào đối chiếu tên nhân vật với năm sinh/độ tuổi** (rule_03). `grep -rln "thoi_ten|era_appropriate|name_era|birth_era" tools/*.py` = 0 kết quả.
- **Giới hạn khi đề xuất fix:** đây là claim khó tự động hoá đầy đủ (cần bộ dữ liệu tham chiếu "tên nào thuộc thời nào" — hiện KHÔNG tồn tại trong repo; không tự suy đoán/tạo bộ dữ liệu này vì dễ thành bịa theo R195). KHÔNG tự chạy đối chiếu 139 passenger thật để kết luận có vi phạm hay không (cần bộ tham chiếu era trước).
- **Phân loại:** THIẾU ENFORCER cho 1/5 rule bible/23 (rule_01/02/04/06 đều có check thật trong `roster_validator.py`; rule_02 word-uniqueness + waiver đã có DEBT-020).
- **KHÔNG tự sửa** — đề xuất cho Mr.Long: (a) xây bộ tham chiếu tên-theo-thời-kỳ tối thiểu (vd map thập niên sinh → nhóm tên phổ biến, dựa nguồn có căn cứ) rồi thêm check vào `roster_validator.py`, hoặc (b) hạ claim bible/23 thành "kiểm tay khi duyệt hồ sơ mới" (rule_03 vốn mang tính thẩm mỹ/văn học, khó số hoá tuyệt đối) — ghi rõ "CHƯA CÓ ENFORCER" theo R215 thay vì để ngỏ.

---

## DEBT-028: `bible/17_sfx_acquisition_pipeline.yaml` checksum lock — code tồn tại nhưng KHÔNG BAO GIỜ được gọi (dead code)

- **Phát hiện:** 11/7, `TASK_AUDIT_RULE_ENFORCER_SWEEP.md`.
- **Bằng chứng (đã tự đọc code):** `bible/17_sfx_acquisition_pipeline.yaml:2,9` khẳng định "Status: IMMUTABLE workflow — KHÔNG ad-hoc download. Mọi SFX trong bible/05 **PHẢI** có entry trong này + qua pipeline + **checksum lock**." `tools/sfx_acquire.py::checksum_and_register()` (dòng 377) — hàm THẬT, có logic sha256 đầy đủ — nhưng lời gọi duy nhất tới hàm này (dòng 478, trong `acquire_asset()`) **bị COMMENT OUT**: `# checksum_and_register(asset_id, final_path, spec, source_info)`. Dòng ngay trên (`process_asset()`, dòng 476) cũng bị comment tương tự. `find . -iname "CHECKSUMS.sha256"` = **0 file tìm thấy** trên toàn repo — xác nhận bước checksum chưa từng chạy thật lần nào.
- **Phân loại:** THIẾU ENFORCER dạng đặc biệt — không phải "chưa viết" mà là **viết rồi nhưng vô hiệu hoá** (dead code, có thể do dở dang mid-implementation chứ không phải chủ ý tắt).
- **KHÔNG tự bật lại 2 dòng comment** (không rõ TẠI SAO bị tắt — có thể do `process_asset()` phụ thuộc bước xử lý audio chưa xong, tự ý bật có thể vỡ luồng `acquire_asset()` hiện tại; đây là quyết định code thuộc domain SFX pipeline, cần Mr.Long/CMD phụ trách xác nhận trước). Đề xuất: (a) nếu pipeline đã đủ điều kiện chạy, bỏ comment + test thật; (b) nếu chưa, ghi rõ trong bible/17 "checksum lock: PLANNED, chưa wire — CHƯA CÓ ENFORCER" thay vì khẳng định PHẢI như hiện tại.

---

## DEBT-029: `bible/32_repair_contract.yaml` (R161) — schema "Vi phạm = REJECT" nhưng 0 code nào tham chiếu — **QUYẾT ĐỊNH Mr.Long 11/7: gộp vào task R86 đang chạy**

- **Phát hiện:** 11/7, `TASK_AUDIT_RULE_ENFORCER_SWEEP.md`.
- **Bằng chứng (đã tự grep toàn repo):** `bible/32_repair_contract.yaml:2,5` — "R161 — REPAIR CONTRACT (ChatGPT-verified, Mr.Long lock 30/6). Ràng buộc khi sửa episode: KHÔNG được rewrite tự do... Mọi propose fix **PHẢI** tuân schema này. **Vi phạm = REJECT**." Định nghĩa schema có cấu trúc rõ (`target`/`locked`/`allowed_actions`). `grep -rln "repair_contract\|32_repair\|R161" tools/*.py` = **0 kết quả tuyệt đối** — không có bất kỳ tool/validator nào tham chiếu file này hay số hiệu rule này.
- **Phân loại:** THIẾU ENFORCER hoàn toàn (0%, không phải "hẹp hơn claim") cho 1 rule TỐI THƯỢNG khác (R161, ngang hàng dạng với R41/R86 về mức độ nghiêm trọng theo văn phong "Vi phạm = REJECT").
- **Lưu ý khi đề xuất fix:** không rõ R161 vốn được thiết kế để MÁY validate (structured schema tự động check) hay là **quy ước hành vi cho AI khi đề xuất sửa tay** (tương tự nhóm R_SUPREME R1-R10 — không phải mọi rule TỐI THƯỢNG đều có 1 code-gate 1-1 tương ứng, một số là kỷ luật quy trình cho executor). KHÔNG tự đoán ý định gốc — chỉ ghi nhận trạng thái thật (0 tham chiếu code) cho Mr.Long xác nhận: nếu ý định là máy-validate, cần xây tool; nếu là quy ước hành vi, nên đổi văn phong "PHẢI tuân schema... REJECT" (nghe như code-gate) sang mô tả rõ đây là checklist tự-kỷ-luật khi review tay.
- **QUYẾT ĐỊNH Mr.Long (11/7):** task R86 fix 49 tập đang chạy (`prompts/TASK_DEBT018_R86_FIX_49EP.md`, claim `debt018_r86_fix_49ep`) sửa văn bản episode.md — CẦN tuân bible/32 nhưng hiện chưa có gì kiểm. **KHÔNG tách việc riêng** — thêm 1 bước xác nhận NHẸ (không cần gate chặn cứng) trực tiếp vào chính task R86: sau khi sửa mỗi câu, diff PHẢI nằm trong `allowed_actions` (đổi ≤5 từ/câu, KHÔNG đổi fact/timeline) — làm NGAY trong lúc thực thi R86 (self-check khi propose fix), không phải 1 tool/gate riêng biệt.
