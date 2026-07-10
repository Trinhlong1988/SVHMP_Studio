# TASK — 27 finding MEDIUM/LOW còn lại từ audit đa-agent 222-agent (9-10/7, workflow G2-G8)

> Viết bởi CMD_AUDIT 10/7. Đây là phần MEDIUM/LOW của cùng báo cáo gốc đã sinh ra
> `TASK_AUDIT_CRITICAL_G3_G5.md` (2 CRITICAL, đã CLOSED) và `TASK_AUDIT_HIGH_G2_G8.md`
> (25 HIGH, 8 đã xong domain G8, 16-17 còn lại vừa giao CMD_BUILD riêng — KHÔNG trộn 2 việc).
> Gốc: `C:/tmp/g2g8_audit_confirmed.json` (56 finding, đã qua 3-skeptic phản biện độc lập trong
> workflow). Severity gốc: 21 medium + 7 low = 28, nhưng #27/#28 dưới đây trùng gốc (cùng 1 lỗi
> `phase_h_version` lỗi thời), đã gộp còn **27 mục thật**.

## RÀNG BUỘC CHUNG (áp cho toàn bộ)
- KHÔNG đổi hành vi test/case hiện có — chỉ sửa docstring/comment lỗi thời, thêm test/guard mới,
  hoặc field-hoá enforcement còn thiếu (tuỳ từng mục, xem "Đề xuất" mỗi mục).
- `python tools/architecture_registry_check.py` phải vẫn PASS 0/0/0 sau khi sửa.
- `pytest tests/ -q` full suite phải xanh, KHÔNG giảm baseline (hiện 658+ passed).
- Nhiều file thuộc domain đã LOCKED (character/dialogue/world/supernatural/decision_engine/
  story_planner/generator/qa_runtime) — sửa là **TU CHỈNH có ủy quyền** (per Mr.Long authorization
  10/7, mirror mẫu `bp4_runtime`/`bp6_decision`/DEBT-007/DEBT-008/DEBT-009). Mỗi domain bị chạm:
  commit ghi rõ "per Mr.Long authorization 10/7" + `architecture_registry.yaml` dòng lock domain đó
  thêm 1 câu "TU CHỈNH 10/7" theo đúng mẫu 2 dòng cũ — KHÔNG tạo lock mới, KHÔNG đổi tag.
- Ưu tiên: sửa docstring/comment lỗi thời trước (rủi ro thấp, nhanh), rồi tới thêm test/enforcement
  còn thiếu (rủi ro cao hơn 1 chút vì đụng logic thật). KHÔNG cần làm theo đúng thứ tự domain.
- Mục nào ghi "KHÔNG cần sửa ngay / chỉ ghi nhận" — chỉ cần thêm 1 dòng vào `TECH_DEBT.md` hoặc
  comment tại chỗ, không cần code mới.

---

## G2_character (3 mục)

### #1 (medium) `tools/architecture_registry_check.py` — không đối chiếu ownership_matrix với git blame
Checker R211 chỉ kiểm MISSING/UNMAPPED/DUP theo path tĩnh, không có cơ chế nào đối chiếu
`ownership_matrix` (dòng 49 registry) với tác giả/commit thực tế đã sửa file — đây là lỗ hổng
**quy trình** khiến vi phạm cross-domain-write (vd DEBT tương tự bp4_runtime/bp6_decision) không tự
động bị phát hiện, phải chờ audit thủ công.
**Đề xuất:** ghi nhận vào `TECH_DEBT.md` là nợ quy trình (không phải bug code) — xây 1 checker mới
đối chiếu `git log --follow -- <file>` tác giả gần nhất với `ownership_matrix` là việc lớn, KHÔNG tự
làm ngay, cần Mr.Long xác nhận phạm vi trước (tương tự cách DEBT-003 đang chờ ACE-Step).

### #2 (medium) `governance/architecture_registry.yaml` — thiếu 2 validator thật trong domain character
Domain `character` (dòng 264-266) chỉ khai `dialog_voice_validator.py` + `story_consistency_validator.py`,
thiếu `tools/roster_validator.py` + `tools/roster_backfill_miner.py` (2 file thật, có test riêng,
đang chạy). `ownership_matrix.CMD_CHARACTER` dùng glob `tools/character_*` không khớp tên 2 file này.
**Đề xuất:** thêm 2 file vào `validators:` list của domain `character` trong `architecture_registry.yaml`
+ sửa glob ownership_matrix nếu cần (hoặc liệt kê tường minh thay vì glob). Chạy lại
`architecture_registry_check.py` xác nhận vẫn 0/0/0.

### #3 (low) `tools/character_manager.py::completeness()` — dict rỗng-nội-dung tính là "đã điền"
Các nhóm EXT_GROUPS ngoài `voice` dùng `if v:` trên dict thô — `{'build': ''}` vẫn truthy dù giá trị
rỗng. Hiện 0 bản ghi thật bị lỗi này (latent, chưa khai thác).
**Đề xuất:** áp cùng pattern lọc rỗng đã dùng cho `voice` (dòng 89-92) sang các nhóm còn lại. Thêm
test xác nhận dict `{'build': ''}` KHÔNG được tính là filled.

---

## G3_dialogue (5 mục)

### #4 (medium) `tools/dialogue_manager.py` — name-match guard không có test hành vi
`_recent_lines()`/`get_dialogue_context()` claim "tránh gán nhầm quote passenger khác" nhưng
`recent_lines`/`known_facts_upto_ep` không xuất hiện trong bất kỳ file test nào — nếu logic bị xoá,
không test nào đỏ.
**Đề xuất:** thêm test gọi `get_dialogue_context()` trực tiếp, xác nhận guard `name != c.char_name`
hoạt động đúng (mutation-proof: xoá điều kiện, xác nhận test flip).

### #5 (low) `tools/dialogue_manager.py` — claim SSOT (không đọc lại roster YAML) không có test
Test hiện có (`test_no_production_publisher_import`) chỉ bắt keyword "production"/"publisher", không
liên quan việc đọc YAML.
**Đề xuất:** thêm test grep riêng xác nhận module không có `yaml.safe_load`/`open(...roster...)`.

### #6 (medium) `tools/dialogue_generator.py` comment lỗi thời — catchphrase "hầu như rỗng"
Dữ liệu thật hiện 139/139 passenger đã có catchphrase (không rỗng) — comment viết trước khi roster
được enrich.
**Đề xuất:** sửa comment khớp thực tế hiện tại (chỉ đổi text, không đổi logic).

### #7 (medium) `tools/dialogue_generator.py` — placeholder `'...'` giả mạo khi pronoun malformed
Khi `pronoun_system` qua Tier1 gate nhưng không tách được token + catchphrase/scene_context rỗng,
generator trả `status='OK'` với line placeholder `'...'` thay vì REFUSED/pending rõ ràng. Chưa kích
hoạt trên data thật (0/139 passenger hiện rơi vào case này) — rủi ro tiềm ẩn cho dữ liệu tương lai.
**Đề xuất:** đổi nhánh `out[:RETRY_LIMIT] or ['...']` thành trả `status='REFUSED'`/`pending` kèm lý do
cụ thể thay vì `'...'`, đúng nguyên tắc R195 "không bịa placeholder" chính file tự tuyên bố. Thêm test
tái hiện case pronoun malformed, xác nhận không còn trả OK+`'...'`.

### #8 (low) `tools/dialogue_generator.py` — field `particles` thiếu không được log
28% roster (39/139) thiếu `particles` nhưng bị âm thầm default `[]`, không nằm trong
`OPTIONAL_VOICE_FIELDS` nên không xuất hiện trong `missing_optional_fields`/report.
**Đề xuất:** thêm `particles` vào `OPTIONAL_VOICE_FIELDS`. Xác nhận báo cáo `G3_MISSING_VOICE_FIELDS.md`
sau khi chạy lại có liệt kê đúng 39 passenger thiếu field này.

---

## G4_world (3 mục)

### #9 (medium) `tools/timeline_check.py` — docstring nói M4 chặn exit code, code thật không
Module docstring (dòng 23-26) nói Exit 0 cần "0 M4 lệch mùa CHẮC CHẮN", nhưng `main()` (dòng 252-254)
chỉ tính `fail` từ M1, M4 chỉ WARN không ảnh hưởng exit code — khớp đúng ý định thật (function-level
docstring dòng 195 nói đúng "WARN không FAIL"), chỉ có docstring đầu file bị sai.
**Đề xuất:** sửa docstring đầu file (dòng 23-26) khớp hành vi thật (M4 chỉ WARN, không chặn exit) —
KHÔNG đổi logic `fail` (logic hiện tại đúng chủ ý, chỉ text sai).

### #10 (medium) `blueprint_domains.yaml` — domain timeline/event vẫn "planned" dù đã LOCKED
`domains.timeline`/`domains.event` (dòng 116-141, 447-468, 823-833) vẫn ghi `status:planned` với lý
do lỗi thời ("100 tập chưa render đủ", "chưa có tập nào ghi ledger"), trong khi `g4_world` đã
`locked v1.0` và `event_ledger_draft.yaml` đã có draft đủ 50/50 tập từ `event_ledger_miner.py`.
**Đề xuất:** cập nhật `status: exists`/`locked` cho 2 domain này, xoá lý do lỗi thời, trỏ đúng tên
file thật (`event_ledger_miner.py`, `timeline_check.py`, `event_ledger_draft.yaml`) — chỉ sửa
văn bản registry, không đổi code.

### #11 (medium) `tools/story_consistency_validator.py` — self-test dùng sai key có dấu
Self-test dòng 117 dùng key `"nguyên_nhân"` (có dấu) trong khi `EVENT_LOCKED_FIELDS` khai
`"nguyen_nhan"` (không dấu) — nhánh kiểm khoá field này chưa từng thực sự chạy đúng (đã tự chạy thật
xác nhận: đổi key có dấu → không phát hiện gì; đổi key đúng không dấu → phát hiện đúng).
**Đề xuất:** sửa self-test dùng đúng key không dấu `"nguyen_nhan"`. Thêm test pytest riêng (ngoài
self-test) xác nhận đổi field `nguyen_nhan` bị phát hiện đúng (hiện `tests_g4_world.py` chỉ test
field `thoi_diem`, thiếu `nguyen_nhan`).

---

## G5_supernatural (2 mục)

### #12 (medium) `tools/supernatural_validator.py` — docstring M6 lỗi thời
Docstring khẳng định D2 (`entity_class` vào bible/37) "không làm trong phạm vi CMD_BUILD_3 lần này",
nhưng bible/37 thực tế ĐÃ có field `entity_class` (g5_extension v2.2) từ TRƯỚC thời điểm docstring
này được viết/giữ lại (xác nhận qua git log: field thêm ở `ae706e5` trước lần sửa cuối docstring).
**Đề xuất:** sửa docstring M6 khớp thực tế (field đã tồn tại), xoá câu "cần RFC + Mr.Long authorization
riêng" nếu đã có sẵn — chỉ sửa text, không đổi logic.

### #13 (medium) `bible/37_character_schema.yaml` — invariant dựa trên field chưa từng được điền
`alive_status` khai BẮT BUỘC (tier_1_mandatory.core_id) và là căn cứ cho invariant G5
(`entity_class=linh_hon` PHẢI khớp `alive_status=ghost`), nhưng field này **0 lần xuất hiện** trong
roster thật (roster dùng field khác tên `life_status` với enum khác). `roster_validator.py`
TIER1_TOP cũng không kiểm field này.
**Đề xuất:** KHÔNG tự sửa ngay (đụng bible/37 đã SIGNED + roster schema — cần Mr.Long xác nhận hướng:
đổi tên field trong bible/37 thành `life_status` khớp data thật, hay thêm `alive_status` thật vào
roster + validator). Ghi nhận vào `TECH_DEBT.md` làm nợ riêng, chờ quyết định hướng trước khi sửa.

---

## G6a_decision_engine (2 mục)

### #14 (low) `tools/decision_engine.py` — docstring/status_note nói story_planner "CHƯA xây"
Dòng 3-4 và 60-62 vẫn khẳng định "story plan thật (G6b, CHƯA xây)" dù `story_planner.py` đã LOCKED
v1.0 từ 5/7 — đúng drift mà `TECH_DEBT.md` DEBT-007 đã tự ghi nhận nhưng fix DEBT-007 (`3f4c2dd`)
chỉ sửa dòng 56 (`plan_ref` key), chưa sửa comment lỗi thời này.
**Đề xuất:** sửa 2 đoạn docstring/status_note khớp thực tế (`story_planner.py` đã tồn tại + locked)
— chỉ sửa text, không đổi logic `build_packet()`.

### #15 (medium) `tools/bp6_decision_check.py` — enforcer chỉ đọc schema tĩnh, không gọi packet thật
`check_io()` chỉ đối chiếu `packet_schema` khai trong `decision_io.yaml` (text), KHÔNG bao giờ gọi
`decision_engine.build_packet()` để lấy packet THẬT — nên 2 field `status`/`status_note` mà
`build_packet()` thực tế thêm vào (ngoài 5 field khai `PACKET_REQUIRED`) không bị bất kỳ check nào
bắt nếu bị field-creep thêm nữa.
**Đề xuất:** thêm 1 bước trong `check_io()` (hoặc test riêng) gọi thật `decision_engine.build_packet(1, plan=...)`,
đối chiếu top-level keys thực tế với `PACKET_REQUIRED ∪ {status, status_note}` — FAIL nếu có key lạ
ngoài danh sách đã biết.

---

## G6b_story_planner (4 mục)

### #16 (medium) `tools/story_planner.py` — `location_ref` hardcode, biến event_ledger không được dùng
Comment dòng 112 nói lấy từ `event_ledger_draft ep_01.primary_event.stop_location`, nhưng code hardcode
literal `"Cầu Long Biên"` — biến `ep01_events` (đã load dòng 100-101) không hề được đọc. Hiện trùng
khớp với data thật là ngẫu nhiên, không phải do đọc động (đã audit trước, biết giá trị đúng nhưng đọc
sai cách — vi phạm R195 tiềm ẩn nếu event_ledger đổi giá trị sau này mà code không cập nhật theo).
**Đề xuất:** sửa dòng 112 đọc thật từ `ep01_events["primary_event"]["stop_location"]["value"]` thay vì
hardcode. Thêm test xác nhận đổi giá trị trong `event_ledger_draft.yaml` (mock) → `location_ref` đổi
theo.

### #17 (medium) `blueprint_domains.yaml` — khai đọc `bible/16_series_kpi.yaml` nhưng code không đọc
`BIBLE_16_KPI` là hằng số khai nhưng chưa từng có lệnh `_load(BIBLE_16_KPI)` — `KPI_BUCKETS` hardcode
thẳng trong Python.
**Đề xuất:** 1 trong 2 hướng — (a) sửa code đọc thật từ `bible/16_series_kpi.yaml` thay vì hardcode,
hoặc (b) sửa comment/registry bỏ claim "đọc bible/16" nếu hardcode là chủ ý. KHÔNG tự chọn hướng —
CMD_BUILD_2 đọc `bible/16_series_kpi.yaml` xem có field tương ứng `KPI_BUCKETS` không rồi quyết, ghi
rõ lý do trong commit.

### #18 (medium) `blueprint_domains.yaml` — trường `validator` trỏ nhầm file
Trường `validator` chính thức trỏ `character_balance_report.py` (chỉ kiểm cân bằng roster, không
import story_planner), trong khi validator thật của schema story_plan là `story_plan_schema_check.py`
(chỉ được nhắc trong comment). `file_index.yaml` cũng xếp `character_balance_report.py` vào domain
`unclassified`.
**Đề xuất:** sửa trường `validator` trỏ đúng `tools/story_plan_schema_check.py`, sửa `file_index.yaml`
gán domain đúng cho `character_balance_report.py` (không phải `unclassified`).

### #19 (medium) `tools/story_planner.py` — field `scene_function` required nhưng không được điền
Schema khai `scene_function` `required:true` nhưng cả 6 scene EP01 đều thiếu field này, và
`story_plan_schema_check.py` không kiểm sự hiện diện của field — nên thiếu sót lọt qua PASS.
**Đề xuất:** thêm `scene_function` vào output `build_episode_plan_ep01()` cho cả 6 scene (giá trị
thật theo enum `[dan_chuyen, gay_nghi, danh_lac_huong, hy_sinh]`, không bịa — đối chiếu nội dung scene
thật để gán đúng), + thêm check `scene_function` hiện diện vào `story_plan_schema_check.py`.

---

## G7_generator (5 mục)

### #20 (medium) `episode_schema.yaml` — ràng buộc enum/range không có test đối chiếu giá trị thật
Test hiện có (`test_reality_frontmatter_has_every_schema_field_key`) chỉ kiểm TÊN key đủ, không kiểm
GIÁ TRỊ hợp lệ theo `allowed_values`/`range`/`const` khai trong schema — đã tự mô phỏng xác nhận: gán
giá trị ngoài enum (`driver_lines=5`, `bell_count=2`) vẫn qua được test key-subset.
**Đề xuất:** thêm 1 test mới đọc `episode_schema.yaml`, đối chiếu từng field trong frontmatter thật
với `allowed_values`/`range`/`const` khai trong schema — FAIL nếu giá trị ngoài phạm vi.

### #21 (low) `tools/g7_generator_check.py` — bảo vệ "read-only" chỉ là text-grep substring
Chỉ kiểm chuỗi `'open('`/`'.write_text('`/`'.write_bytes('` trong source — cách ghi gián tiếp
(`shutil.copy`, `os.system`, `getattr` indirection) sẽ lọt qua cả gate lẫn test mirror.
**Đề xuất:** mở rộng danh sách pattern cấm (`shutil.copy`, `shutil.move`, `os.system`, `subprocess`,
`os.replace`) trong cả gate và test mirror — vẫn là text-grep (nhất quán với cách tiếp cận hiện có
của codebase, không cần AST parse), chỉ mở rộng độ phủ.

### #22 (medium) `blueprint_domains.yaml` + `architecture_registry.yaml` — DEBT-007 ghi sai "chưa fix"
Cả 2 file governance vẫn ghi DEBT-007 là "chưa fix"/"mở", dù code thật + `TECH_DEBT.md` xác nhận đã
CLOSED từ 9/7 (`decision_engine.py:56` đã sửa, `episode_generator.py 1` trả `plan_ref: ep1_season_1`
đúng).
**Đề xuất:** sửa 2 đoạn text lỗi thời này khớp `TECH_DEBT.md` (CLOSED) — chỉ sửa text, không đổi code.

### #23 (low) `tools/g7_generator_check.py` docstring — số lượng test sai
Docstring ghi "9 test" nhưng file thật hiện có 13 test (`pytest tests/test_g7_generator.py -q` →
"13 passed").
**Đề xuất:** sửa số trong docstring thành 13 (hoặc bỏ số cụ thể, chỉ ghi "reality anchor" chung chung
để tránh lệch lại lần sau).

### #24 (medium) `episode_schema.yaml` — `passenger_main` required:true nhưng code luôn trả None
Schema khai `required:true` (phải là PAS_id thật), nhưng code EP01 luôn trả `None` và chính test riêng
(`test_reality_passenger_main_none_not_fabricated_for_ep01`) đã khoá hành vi None này là đúng —
mâu thuẫn giữa schema và hành vi đã test.
**Đề xuất:** KHÔNG tự chọn hướng sửa (đụng ranh giới "EP01 là pilot chưa có PAS_id thật" đã quyết từ
trước, xem R195 "không bịa"). Ghi nhận vào `TECH_DEBT.md`: hoặc sửa schema `passenger_main` thành
`required: false` cho case EP01/pilot, hoặc thêm điều kiện "required trừ pilot" — cần Mr.Long chọn.

---

## G8_qa_runtime (2 mục, gộp từ 3)

### #25 (medium) `tools/vnqa/pipeline.py` — VNQA H1-H10 không có test thật gọi `run_all()`
G8 gate `check_vnqa_h1_h10()` chỉ regex-verify các hàm `h1..h10` được định nghĩa+gọi (text-grep tên
hàm), KHÔNG kiểm ngưỡng phát hiện hay logic tổng hợp verdict (`critical→FAIL`, `warning>=5→WARN`) có
tính đúng không. 0 test trong `tests/` khởi tạo `VietnameseQAChecker` hay gọi `run_all()`.
**Đề xuất:** thêm test mới khởi tạo `VietnameseQAChecker` thật, gọi `run_all()` với 1-2 case mô phỏng
(text sạch → verdict PASS; text có lỗi critical → verdict FAIL) — mirror pattern
`test_supernatural_run_all_composition.py` (D9) đã dùng cho G5.

### #26 (medium, gộp #27+#28) `phase_h_version` báo sai "H1-H7 v1.0" dù chạy đủ H1-H10
`run_all()` (dòng 402) trả `'phase_h_version': 'H1-H7 v1.0'` dù thực thi đủ 10 hàm H1-H10;
`qa_skeptic_orchestrator.py:114` cũng in "H1-H7"; `blueprint_domains.yaml:608` ghi "VNQA H1-H9" — cả
3 chỗ đếm thiếu. Đã tự chạy `g8_qa_runtime_check.py` xác nhận code thật chạy đủ 10/10. Bug này ĐÃ được
`pack5/19_qa_pipeline.md:31` tự ghi nhận là biết-nhưng-chưa-sửa (không phải phát hiện mới, nhưng vẫn
tồn tại thật tại thời điểm audit).
**Đề xuất:** sửa cả 3 chỗ (`phase_h_version` → `"H1-H10 v1.1"` hoặc tương đương, orchestrator log,
blueprint_domains.yaml) khớp thực tế — cosmetic, không đổi logic QA. Xoá dòng cảnh báo lỗi thời tại
`pack5/19_qa_pipeline.md:31` sau khi sửa xong (đóng nợ đã ghi).

---

## KHÔNG tự sửa ngay (cần Mr.Long quyết định hướng trước — chỉ ghi nhận vào TECH_DEBT.md)
- **#1** (ownership_matrix enforcer — việc lớn, cần xác nhận phạm vi)
- **#13** (bible/37 `alive_status` vs `life_status` — đụng bible đã SIGNED)
- **#17** (BIBLE_16_KPI đọc thật hay bỏ claim — cần đọc bible/16 trước khi chọn)
- **#24** (passenger_main required cho pilot — đụng quyết định R195 cũ)

## DoD
27 mục (trừ 4 mục "không tự sửa" chỉ cần ghi TECH_DEBT.md): mỗi mục có fix + bằng chứng chạy thật
(không suy đoán) + test/mutation-proof nếu đề xuất yêu cầu. Registry 0/0/0, pytest full suite xanh
không giảm baseline, domain nào bị chạm (LOCKED) đều có dòng "TU CHỈNH 10/7" trong
`architecture_registry.yaml`.

## THAM CHIẾU
Gốc dữ liệu: `C:/tmp/g2g8_audit_confirmed.json` (56 finding, severity field). Cùng đợt với
`prompts/TASK_AUDIT_CRITICAL_G3_G5.md` (2 CRITICAL, CLOSED) và `prompts/TASK_AUDIT_HIGH_G2_G8.md`
(25 HIGH, đang thực thi riêng bởi CMD_BUILD).
