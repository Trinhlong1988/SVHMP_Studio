# CMD AUDIT — PHỤ LỤC RIÊNG G2 (Character Fill & Gate)

> KHÔNG thay thế `CMD_AUDIT_PROTOCOL.md` (7 bước chung — vẫn bắt buộc chạy đủ, không rút gọn).
> Cùng mẫu `CMD_AUDIT_G4_G5.md`/`CMD_AUDIT_G6.md` — viết TRƯỚC khi xem chi tiết implementation
> hiện tại, chỉ dựa trên `TASK_G2_CHARACTER.md` (DoD đã khai từ 3/7) + lịch sử lỗi dự án, tránh
> thiên vị xác nhận (dữ liệu roster hiện đã 0 violation/0 warn KHÔNG có nghĩa domain đã audit).

## THỨ TỰ CHẠY (bắt buộc, không đảo)
1. `CMD_AUDIT_PROTOCOL.md` đủ 7 bước (B0-B7) trên worktree sạch từ origin/main.
2. Bảng checkpoint domain-specific dưới đây — MỌI dòng phải có verdict.
3. Đối chiếu ĐỦ 7 mục DoD gốc trong `TASK_G2_CHARACTER.md` — thiếu 1 mục = chưa DONE, không
   được coi "dữ liệu đủ 0/0" là toàn bộ DoD.

## QUY TẮC PHÂN ĐỊNH 100-ĐÚNG / 100-SAI
Giống hệt `CMD_AUDIT_G4_G5.md`. Nhóm **G2-1 (bịa dữ liệu đời tư nhân vật, R195)** và **G2-5
(sửa bible không authorization)** KHÔNG có mức giữa.

## BẢNG RỦI RO ĐÃ BIẾT ← BÀI HỌC LỊCH SỬ (viết trước khi xem code thật)

| # | Rủi ro cụ thể | Bài học lịch sử áp dụng | Cách kiểm — tiêu chí 100đ/100s |
|---|---|---|---|
| G2-1 | 4 field voice (`speaking_speed`/`catchphrase`/`forbidden_words`/`dialogue_sample`) của 139 passenger bị điền bằng CÔNG THỨC MÁY MÓC hàng loạt thay vì khớp hồ sơ từng người (R195 — đã cảnh báo tường minh trong `PROMPT_HANDOFF_G2_EXECUTOR_B4_VOICE_FIELDS.md`) | R195 + lesson-audio-first-character-schema (giọng gắn quê, không vô diện) | Lấy mẫu ngẫu nhiên 15/139 passenger khác vùng miền/tính cách — đọc `catchphrase`/`dialogue_sample` đối chiếu `region_dialect` + `dominant_traits` trong chính hồ sơ đó. Thấy pattern LẶP giống hệt giữa các vùng miền khác nhau (đổi tên, giữ nguyên câu) = 100% SAI, bằng chứng cụ thể là 2 hồ sơ khác vùng có câu giống nhau |
| G2-2 | `bible/37_character_schema.yaml` v2 (10 facet G2-core mới) field-hóa không khớp `bp2/domain_specs.yaml` đã khóa (drift = FAIL theo chính TASK_G2 khai) | bp2-domain-v1.0 LOCKED, facet list ĐÓNG sau BP2 | Đối chiếu từng facet_id mới trong bible/37 với `governance/blueprint/bp2/domain_specs.yaml` — facet nào có tên/id KHÔNG khớp = 100% SAI |
| G2-3 | `tools/roster_backfill_miner.py` ghi thẳng vào `runtime/passenger_roster_100.yaml` thay vì `runtime/roster_backfill_draft.yaml` (status: draft) — bỏ qua bước người duyệt trước khi merge (TASK khai rõ "KHÔNG tự ghi vào roster chính") | R211 + nguyên lý "máy trích xuất → người DUYỆT, AI không sáng tác đời tư" (TASK_G2 dòng 7) | `git log --all -- runtime/roster_backfill_draft.yaml` phải có commit riêng TRƯỚC mọi commit merge vào `passenger_roster_100.yaml` cùng nội dung — nếu roster chính có dữ liệu mới mà KHÔNG có bước draft trước đó = 100% SAI (build-ahead kiểu khác: bỏ qua gate người duyệt) |
| G2-4 | `G2_CONTINUITY_FINDINGS.md` (mâu thuẫn đã phát hiện: chết rồi xuất hiện lại...) chưa thực sự được xử lý, chỉ nằm im trong report | lesson-claim-equals-work (báo cáo ≠ đã sửa) | Mở từng mục trong `reports/G2_CONTINUITY_FINDINGS.md`, đối chiếu `runtime/passenger_roster_100.yaml`/`output/ep_*` hiện tại xem mâu thuẫn đã được sửa hay vẫn còn nguyên. Còn ≥1 mâu thuẫn đã biết mà chưa route/chưa sửa VÀ không có ghi chú lý do hoãn = FAIL mục đó |
| G2-5 | `bible/37_character_schema.yaml` v2 hoặc `bible/23_passenger_naming.yaml` v1.1 bị sửa mà commit message KHÔNG có "per Mr.Long authorization" | bible writer=mr_long, immutable — đã áp dụng nhiều lần (R142/R143, bible/31) | `git log --follow` 2 file này — mọi commit sửa nội dung (không phải chỉ format) PHẢI có cụm "per Mr.Long authorization". Thiếu = 100% SAI dù nội dung đúng |
| G2-6 | `--strict-characters` bật bằng cách SỬA TRỰC TIẾP `tools/svhmp_v13_render.py` (LOCKED) thay vì qua flag/wrapper riêng (TASK khai rõ "KHÔNG sửa svhmp_v13_render.py LOCKED — bật qua flag/wrapper") | bible/tool lock discipline | `git diff` — `tools/svhmp_v13_render.py` KHÔNG được xuất hiện trong bất kỳ commit G2 nào liên quan tới bật strict. Có sửa = 100% SAI ngay |
| G2-7 | "Confusion-run nhân vật 500/500" (DoD dòng 37) không có bằng chứng thật đã chạy — chỉ ghi con số trong report mà không có artifact/log thật | lesson-dont-downplay-rigor (cấm khẳng định trước khi chứng) | Tìm script/report thật tạo ra con số 500/500 (tên file, lệnh chạy, log). KHÔNG tìm thấy artifact nào tái lập được con số này = **CHƯA ĐỦ BẰNG CHỨNG** (không tự quy về PASS), phải ghi rõ thiếu gì |
| G2-8 | "Mr.Long tận tay duyệt 5 hồ sơ mẫu" (DoD dòng 38) không có bằng chứng — chỉ có audit/miner tự động, không có bước người thật xem | nguyên lý B3 TASK_G2 "AI chỉ đề xuất", cần review thật | Grep PING/commit message tìm bằng chứng cụ thể Mr.Long đã xem 5 hồ sơ nào, ngày nào. Không có = CHƯA ĐỦ BẰNG CHỨNG, liệt vào "điểm chờ chữ ký Mr.Long" trong verdict, không phải defect kỹ thuật |
| G2-9 | `roster_validator.py` hiện báo "0 violation, 0 warn" nhưng thực chất KHÔNG có khả năng phát hiện lỗi thật (checker rỗng/luôn PASS) — named≠enforced | lesson-enforcer-claim-vs-behavior | Mutation: tự sửa 1 record thật thành sai rõ ràng (region_dialect≠giọng dùng, tuổi mâu thuẫn năm sinh, catchphrase rỗng) trên bản copy worktree → chạy lại `roster_validator.py` → PHẢI thấy violation/warn tăng đúng số lượng đã mutate. Không phát hiện = 100% SAI (checker vô dụng dù báo cáo "0/0" đẹp) |
| Cross-G2/G3 | Dữ liệu voice 139 passenger (G2 B4) không thực sự được `dialogue_generator.py` (G3) đọc dùng — 2 domain khai tương thích trên giấy nhưng không nối thật | lesson-enforcer-claim-vs-behavior (built≠wired) | Đọc `tools/dialogue_generator.py` (nhánh `build/g3-dialogue-d0-d8`) xác nhận có gọi field `catchphrase`/`dialogue_sample` mới của roster hay không — nếu code G3 vẫn chỉ dùng field cũ (particles/pronoun_system) và 4 field mới của G2 B4 không có điểm đọc nào = ghi nợ kỹ thuật (không phải FAIL G2, nhưng phải ghi nhận dữ liệu đang "có nhưng chưa dùng") |

## KHÔNG COI "DỮ LIỆU ĐỦ" LÀ "DOMAIN ĐÃ AUDIT"
`roster_validator.py` báo 0 violation/0 warn (139/139) chỉ xác nhận ĐIỀU KIỆN CẦN để audit —
KHÔNG phải kết quả audit. Runs trước đó (KIEM_DUYET release `g2_character` 01:32:22, CMD_BUILD_2
release `g2_b4_voice_fill`/`g2_b4_voice_req_fix`) đều là claim BUILD, chưa từng có claim/verdict
AUDIT độc lập nào cho pack này.

## SAU KHI CÓ VERDICT
Theo format `CMD_AUDIT_PROTOCOL.md`. G2-1/G2-3/G2-5/G2-6 FAIL → route CMD_BUILD_2 (đang sở hữu
domain character) kèm đúng dòng trích từ `TASK_G2_CHARACTER.md` đã dẫn ở trên. G2-7/G2-8 nếu
"CHƯA ĐỦ BẰNG CHỨNG" → liệt vào mục điểm chờ Mr.Long, KHÔNG quy thành FAIL kỹ thuật.

## THAM CHIẾU
`CMD_AUDIT_PROTOCOL.md` · `prompts/TASK_G2_CHARACTER.md` · `governance/blueprint/bp2/domain_specs.yaml`
· `reports/G2_CONTINUITY_FINDINGS.md` · `reports/G2_HYBRID_CLASSIFICATION.md` ·
lesson-audio-first-character-schema · lesson-enterprise-audit · lesson-claim-equals-work ·
lesson-dont-downplay-rigor.
