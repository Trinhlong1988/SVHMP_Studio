# TASK G8 — QA RUNTIME (RECONCILE trước, KHÔNG build mới — phần lớn code đã tồn tại rời rạc)

> Viết bởi kiểm duyệt 5/7, sau điều tra sâu (không phải đoán): domain `qa_runtime` đã có
> `manager`/`validator` EXISTS trong `blueprint_domains.yaml` (dòng 610-631), và thực tế có **hơn
> 50 tool** `qa_*.py`/`audit_*.py` liên quan QA đã tồn tại từ trước — nhưng **KHÔNG PHẢI 1 pipeline
> thống nhất, mà 6 luồng song song rời rạc**, có trùng lặp logic thật và có lỗ hổng governance
> nghiêm trọng (1 luồng đang chạy thật nhưng chưa từng được ghi vào pack5). G8 KHÔNG PHẢI "viết
> manager mới" như G7 — là **RECONCILE + DEDUPE + CODIFY** trước, chỉ bổ sung code thật cần thiết.

> **Đã qua 2 lớp (điều tra + phản biện độc lập, 5/7 tối):** 5/5 claim cốt lõi được phản biện xác
> nhận ĐÚNG bằng đọc code thật (không tin lời kể lớp 1). 3 chỗ đã SỬA LẠI theo phản biện (đánh dấu
> `[SỬA theo phản biện]` trong bảng dưới) — lớp điều tra đầu có 2 chỗ hơi quá tay (gán domain
> `dialogue`/liệt kê "3 domain" khi bằng chứng thật chỉ ủng hộ kết luận hẹp hơn). Tin cậy được để
> giao CMD_BUILD, nhưng CMD_BUILD vẫn nên tự verify lại D1 trước khi code D2 trở đi (đừng tin
> task doc này 100% mù quáng — đúng tinh thần dự án).

## HIỆN TRẠNG THẬT (đã điều tra 5/7, không suy đoán — đọc kỹ trước khi động vào bất kỳ file nào)

### 6 luồng QA đang chạy song song (xác nhận qua đọc code, không phải đoán từ tên file)
| # | Entry point | Gọi thật | Có trong governance/pack5 chưa? |
|---|---|---|---|
| 1 | `svhmp_preflight_qa.py` (FULL_TEXT_GATE) | gọi `qa_eol_diacritic.py` | ✅ Có (doc19) |
| 2 | `render_with_character_gate.py` → `svhmp_v13_render.py` | gọi thẳng `qa_eol_diacritic.py` | ✅ Có (doc19) |
| 3 | `qa_skeptic_orchestrator.py` (= manager chính thức của qa_runtime theo BP0) | `vnqa/auto_fix.py` → `vnqa/pipeline.py` (tự chứa H1-H10) → `adversarial_skeptic.py` | ❌ **KHÔNG — lỗ hổng codify nghiêm trọng nhất, chạy thật nhưng vô hình với governance** |
| 4 | `qa_watch.py` + `qa_watch_supervisor.py` (daemon) | STAGE1=`qa_eol_diacritic.py`, STAGE3=`qa_post_render.py` (tự viết lại logic, KHÔNG gọi `qa_pause_silence.py`/`qa_boundary_artifact.py`/`qa_onset_artifact.py`) | 🟡 Có nhắc daemon (doc22) nhưng không nói rõ STAGE3 tự viết lại |
| 5 | `audio_pre_ship_gate.py` | `audio_qa_metrics.py` + `qa_concat_silence.py` + `qa_post_render.py` (lặp lại #4) | ❌ Không nhắc trong doc19 |
| 6 | Batch legacy: `deep_200_rounds.py`, `verify_50_rounds.py`, `sequential_full_auto.py` | gọi `audit_short_*`, `audit_style_stats`, `audit_vn_style`, `audit_phrase_repetition`, `audit_pronoun_pov`... | ❌ Vô hình với governance |

### Trùng lặp logic ĐÃ XÁC NHẬN (đọc code, không phải nghi ngờ)
- `qa_post_render.py::audit_pause()` (ngưỡng -70dB/1200ms, thuật toán 20ms-window) gần như **giống hệt** `qa_pause_silence.py::audit()` — 2 bản cài đặt song song của cùng 1 rule.
- `qa_post_render.py::audit_boundary()`/`audit_head_onset()` là bản **thô hơn** so với `qa_boundary_artifact.py`/`qa_onset_artifact.py` (bản chính thức, spectral analysis, R188).
- `audit_60_dimensions.py` và `audit_100_check.py`: chính comment trong `tools/ha_patterns.py` đã tự ghi "4 pattern giống nhau" — trùng lặp ĐÃ được biết nhưng chưa reconcile hết.
- **[Phản biện độc lập xác nhận 5/7, thêm chi tiết quan trọng]** `qa_post_render.audit_pause()` và
  `qa_pause_silence.audit()` dùng Y HỆT window 20ms/`min_pause_ms=1200`/`silence_thr_db=-55`/
  `pass_thr_db=-70`/margin 100ms — đúng là bản sao 1-1. NHƯNG có 1 khác biệt thật: `audit_pause()`
  cho phép tolerance (`noisy<=1`, theo R96), còn `qa_pause_silence.audit()` strict (`noisy==0`).
  **D3 KHÔNG được hợp nhất mù** — phải xác định trước tolerance nào là ý định thật (hỏi Mr.Long
  nếu không rõ), không tự chọn 1 bên rồi coi là "đã dedupe xong".

### Domain gán SAI (file_index.yaml/blueprint mismatch — cần sửa manifest, KHÔNG sửa code)
- `qa_skeptic_orchestrator.py` bị gắn `domain: generation` trong `file_index.yaml`, mâu thuẫn với `blueprint_domains.yaml` gọi nó là manager của `qa_runtime`. **[Phản biện xác nhận đúng]** — 2 nguồn field chính thức mâu thuẫn thật, sửa an toàn.
- **[SỬA LẠI theo phản biện độc lập 5/7 — bản đầu SAI, đây là bản đúng]:** `audit_dialogue_hierarchy.py`/`audit_driver_dialogue_context.py` ĐÚNG là được gọi bởi `dialogue_generator.py`/`g3_dialogue_check.py` (G3 dùng qua wrapper) — NHƯNG domain SỞ HỮU thật của 2 file này (theo `file_index.yaml:359-366` VÀ `architecture_registry.yaml:290-295` ghi rõ "vẫn thuộc sở hữu domain character/text_qa") là **`text_qa`**, KHÔNG PHẢI `dialogue`. **KHÔNG đổi domain 2 file này sang `dialogue`** — đó sẽ là sửa sai theo đúng lỗi agent điều tra đầu tiên mắc phải. Giữ nguyên `text_qa`, chỉ ghi chú rõ "G3 dialogue tiêu thụ qua wrapper, không sở hữu".
- `story_consistency_validator.py` được gọi bởi `roster_validator.py`/`g4_world_check.py` → **thuộc G4 world** (chưa bị phản biện bác, giữ nguyên).
- `qa_dialogue_identity.py` bị gắn tín hiệu domain KHÔNG NHẤT QUÁN — **[SỬA theo phản biện 5/7]**:
  CHỈ 2/3 là field domain CHÍNH THỨC thật sự mâu thuẫn (`text_qa` trong `file_index.yaml` vs
  `tts` trong `blueprint_domains.yaml` phần validator) + `architecture_registry.yaml` xác nhận lại
  `character/text_qa`. Cái thứ 3 ("audio detector" trong pack5/21) chỉ là NGỮ CẢNH văn bản (file
  này được liệt kê trong mục "Voice/Audio Detector Suite") — KHÔNG có field `domain:` tường minh ở
  đó, không nên trình bày như 1 domain chính thức thứ 3. Khi báo cáo D2, ghi đúng: "2 field domain
  chính thức mâu thuẫn (text_qa/tts) + 1 tín hiệu ngữ cảnh không chính thức (audio)" — tránh bị bắt
  bẻ "gán nhầm 1 domain không tồn tại trong hệ thống".

### Ranh giới domain (trích nguyên văn pack5, đã xác nhận)
Pack5/19: *"KHÔNG gồm... audio-detector (= 21_detector_suite.md)"*. Pack5/21: *"Detector chạy trên
AUDIO đã render. KHÔNG gồm text-QA trước render (doc 19)."* → `qa_boundary_artifact`/`breath`/
`onset`/`prosody`/`pause` thuộc domain **audio** (tầng 9, presentation layer_group), KHÔNG phải
`qa_runtime` (tầng 7, runtime layer_group) — dù domain "audio" chưa có block riêng tường minh
trong `blueprint_domains.yaml` (chỉ xuất hiện trong `layer_groups.presentation`).

## DELIVERABLE (thứ tự bắt buộc — KHÔNG nhảy cóc sang D-sau khi D-trước chưa xong)

### D1 — Ghi lại bản đồ hiện trạng thành báo cáo chính thức (KHÔNG sửa code, chỉ ghi nhận)
Viết `reports/G8_QA_REALITY_MAP.md` — chép đúng bảng "6 luồng" + "trùng lặp" + "domain sai" ở trên
kèm bằng chứng dòng code cụ thể (đã điều tra sẵn, chỉ cần format lại thành report chính thức). Đây
là REALITY ANCHOR bắt buộc trước khi sửa bất cứ gì — tránh vừa sửa vừa quên hiện trạng gốc.

### D2 — Sửa domain gán sai trong `governance/file_index.yaml` (an toàn, cơ học, làm ngay được)
`qa_skeptic_orchestrator.py`: `generation` → `qa_runtime`. `audit_dialogue_hierarchy.py`/
`audit_driver_dialogue_context.py`: → gắn về G3 dialogue (đối chiếu đúng domain đã khai trong
`blueprint_domains.yaml` dialogue.reader/dependencies). `story_consistency_validator.py`: → G4
world. KHÔNG sửa nội dung tool, chỉ sửa manifest.

### D3 — Diệt trùng lặp `qa_post_render.py` (CẦN xác nhận Mr.Long trước vì đổi hành vi gate đang chạy thật)
Sửa `qa_post_render.py::audit_pause()`/`audit_boundary()`/`audit_head_onset()` để GỌI LẠI
`qa_pause_silence.py`/`qa_boundary_artifact.py`/`qa_onset_artifact.py` (bản đã calibrate theo
pack5/20) thay vì tự viết lại logic — đúng R211. **CẢNH BÁO:** đây là gate ĐANG CHẠY THẬT trong
`qa_watch.py` daemon + `audio_pre_ship_gate.py` — đổi ngưỡng/thuật toán có thể đổi verdict PASS/FAIL
của nội dung đã qua gate trước đó. PHẢI chạy A/B trên toàn bộ golden set trước/sau, báo cáo có bao
nhiêu case đổi verdict, KHÔNG tự ý merge nếu có case đổi mà chưa hiểu vì sao.

### D4 — Codify chuỗi VNQA/skeptic vào `governance/pack5/19_qa_pipeline.md` (lỗ hổng nghiêm trọng nhất)
Thêm đúng luồng #3 (`qa_skeptic_orchestrator.py` → `vnqa/auto_fix.py` → `vnqa/pipeline.py` →
`adversarial_skeptic.py`) vào doc19 — đây là chuỗi ĐANG CHẠY THẬT, không phải chuyện mới, chỉ là
chưa ai ghi vào governance. Đọc kỹ `vnqa/pipeline.py` (H1-H10) trước khi viết mô tả, không suy đoán
từ tên biến.

### D5 — Field-hóa `qa_verdict_schema.yaml` (CẦN Mr.Long duyệt TRƯỚC — giống pattern G6b/G7)
3 format verdict thật hiện có: orchestrator (`final_verdict`: PASS/PASS_WITH_WARNING/REGEN/
REVIEW_REQUIRED + reasoning), VNQA (`verdict`: PASS/WARN/FAIL + issues[] theo severity), preflight
(**chỉ có exit code 0/1/2, KHÔNG có JSON verdict**). **Điều kiện tiên quyết:** preflight phải được
nâng cấp phát JSON verdict trước — soạn đề xuất format hợp nhất, trình Mr.Long duyệt (mirror đúng
quy trình `episode_schema_proposal.yaml`/`story_plan_schema_proposal.yaml` đã dùng), KHÔNG tự field-
hóa khi chưa có bản duyệt.

### D6 — Xử lý lớp batch legacy (`deep_200_rounds.py`, `verify_50_rounds.py`, `sequential_full_auto.py`)
Báo cáo cho kiểm duyệt/Boss quyết định: khai tử (nếu xác nhận không ai còn chạy — kiểm `git log`
xem lần cuối dùng khi nào) hoặc đăng ký chính thức thành "batch-mode" của qa_runtime. KHÔNG tự
quyết — đây là nợ governance cũ, không phải lỗi của G8.

### D7 — Gate 1 cửa (chỉ làm SAU D1-D4, D6 xong; D3/D5 có thể chưa xong nếu cần thêm thời gian A/B test)
`tools/g8_qa_runtime_check.py` — mirror pattern `g6_story_planner_check.py`. Wire ci_gate +
unwire-guard. KHÔNG chờ D3/D5 nếu 2 việc đó cần thêm vòng xác nhận Mr.Long — gate D7 chỉ cần
xác nhận D1/D2/D4/D6 đã xong, D3/D5 có thể là bước tiếp theo riêng.

## MUTATION AUDIT SẼ BẮN (khai trước)
M1 sửa file_index.yaml domain mà KHÔNG đối chiếu đúng blueprint_domains.yaml thật → FAIL · M2
`qa_post_render.py` sau khi sửa D3 mà KHÔNG có báo cáo A/B verdict trước/sau → FAIL (build-ahead
kiểu khác: đổi hành vi gate đang chạy thật mà không đo tác động) · M3 field-hóa `qa_verdict_schema.yaml`
không có bằng chứng Mr.Long duyệt ĐÚNG bản đề xuất → FAIL · M4 D7 gate build trước khi D1/D2/D4/D6
xong → FAIL build-ahead · M5 tự ý xóa/khai tử batch legacy (D6) mà không có xác nhận Boss → FAIL.

## RÚT KINH NGHIỆM TOÀN BỘ LỖI THẬT ĐÃ XẢY RA (phiên G1-G7, 2/7-5/7) — ÁP DỤNG BẮT BUỘC CHO G8

1. **Build-ahead tự-duyệt (G3 D2):** mọi field-hóa schema cần bằng chứng duyệt TRƯỚC commit code —
   áp dụng cho D5 (qa_verdict_schema.yaml).
2. **Đếm/liệt kê tay sai (G3 "11 vs 12"):** D1 (bản đồ hiện trạng) phải dựa lệnh `grep`/đọc code
   thật, không liệt kê theo trí nhớ hay theo tên file đoán ý nghĩa.
3. **Fabricate narrative (G3 D2):** nếu D3 (dedupe) phát hiện gate cũ có bug (case PASS sai/FAIL
   sai), ghi ĐÚNG sự thật, không suy diễn "chắc không ai để ý".
4. **Fork-bomb pytest đệ quy (G3 D7, G14):** `g8_qa_runtime_check.py` (D7) nếu gọi lại pytest trên
   test của chính nó, PHẢI có `_PYTEST_GUARD` theo đúng pattern `ci_gate.py`.
5. **Debt logging trễ (DEBT-004):** mọi nợ kỹ thuật phát hiện lúc làm D1-D6 (rất có thể phát sinh
   nhiều, vì đây là domain rối nhất) phải ghi `TECH_DEBT.md` NGAY, không để trôi.
6. **Kết luận "thiếu" khi thật ra có sẵn nơi khác (DEBT-002):** trước khi báo "chưa có schema
   thống nhất", đã xác nhận 3 format thật đang tồn tại (không phải 0) — chỉ CHƯA HỢP NHẤT, khác hẳn
   "chưa có gì".
7. **Push bị reject do phiên khác (G4/G5/nhiều lần):** luôn fetch+rebase trước push.
8. **Vai trò kiểm duyệt tự build:** kiểm duyệt viết task doc này, KHÔNG tự sửa `file_index.yaml`
   hay code — giao CMD_BUILD rảnh.
9. **Cross-domain "tiện thể sửa luôn" (G6a/bp4, G6b/bp6, LẶP LẠI 2 LẦN):** D2 sửa domain gán sai
   là việc CỦA G8, nhưng nếu phát hiện cần sửa NỘI DUNG file thuộc domain khác (vd sửa lại
   `dialogue_generator.py` để nó tự khai đúng domain), PHẢI báo domain đó/kiểm duyệt trước, không
   tự tiện sửa "cho gọn".
10. **Công thức hóa thay vì thật (G2-1):** không áp dụng trực tiếp cho G8 (G8 không sinh nội dung),
    nhưng tinh thần tương tự: D3 dedupe KHÔNG được "làm cho gọn" bằng cách hạ chuẩn (dùng bản đơn
    giản `qa_post_render.py` thay vì bản chính xác `qa_boundary_artifact.py`) — phải giữ bản NGHIÊM
    NGẶT HƠN khi hợp nhất, không phải bản dễ làm hơn.
11. **Sửa file LOCKED trực tiếp (G2-6):** D3 tuyệt đối không đụng `svhmp_v13_render.py` (LOCKED).
12. **Nhân đôi logic (G5, R211):** đây là TRỌNG TÂM của toàn bộ D3 — không phải 1 lần, mà ít nhất
    2 cặp trùng lặp đã xác nhận (pause/boundary/onset, và audit_60/audit_100).
13. **Ghi vào file dùng chung khi test (DEBT-005) + hardcode snapshot lỗi thời (DEBT-006):** D1
    report và mọi test mới của G8 PHẢI ghi vào đường dẫn riêng, không đụng `output/ep_01/` thật.
14. **[MỚI — phát hiện chính lúc điều tra G8] Governance blind spot — code chạy thật nhưng
    KHÔNG có doc pack5 nào ghi nhận (chuỗi VNQA/skeptic):** đây là lớp lỗi CHƯA từng ghi ở đâu
    trước đây trong dự án — không phải "docs nói sai code" (đã bắt nhiều lần) mà là "docs HOÀN
    TOÀN IM LẶNG về code đang chạy thật". Bài học: định kỳ soát NGƯỢC (code → docs), không chỉ
    xuôi (docs → code) — nếu 1 tool được gọi thật trong production nhưng grep toàn bộ
    `governance/` không ra tên nó, đó là dấu hiệu domain đó chưa được audit đầy đủ, bất kể checker
    máy báo PASS.

## DoD
D1 report đầy đủ bằng chứng, không thiếu luồng nào trong 6 luồng đã biết ✅ · D2 domain gán đúng,
`architecture_registry_check.py` 0/0/0 ✅ · D3 CÓ báo cáo A/B verdict trước/sau, không tự ý merge
nếu có case đổi chưa giải thích được ✅ · D4 pack5/19 phản ánh đúng chuỗi VNQA/skeptic thật ✅ · D5
CHỈ field-hóa khi có bằng chứng Mr.Long duyệt ✅ · D6 có quyết định rõ ràng (khai tử hoặc đăng ký),
không để lửng lơ ✅ · D7 gate 1 cửa + unwire-guard, wire ci_gate ✅ · pytest xanh, không giảm baseline.

## RÀNG BUỘC
Claim pack: `python tools/build_claim.py claim g8_qa_runtime <phiên>`. Làm ĐÚNG THỨ TỰ D1→D2→
(D3+D4+D6 có thể song song)→D5→D7 — không nhảy sang D7 khi D1-D4/D6 chưa xong. KHÔNG bịa số/verdict
(R195). KHÔNG tự quyết D5/D6 khi chưa có xác nhận Mr.Long.

STATUS cuối: KHUNG_CHUAN_BI (đủ điều kiện claim D1/D2 ngay — không cần chờ gì; D3/D5/D6 cần thêm
xác nhận Mr.Long giữa chừng, không phải build-ahead nếu dừng đúng chỗ chờ).
