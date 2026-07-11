# TASK — Thí điểm mở rộng `story_planner.py` cho 10 tập EP02-11

> Viết bởi CMD_AUDIT 12/7, sau 2 vòng phản biện đối kháng (Agent tool) + tự kiểm chứng trực tiếp
> (1 vòng phản biện đầu SAI tiền đề — đã tự phát hiện và sửa, xem lịch sử hội thoại). Đây là field-hoá
> dữ liệu THẬT đã tồn tại (event_ledger_draft.yaml đã mine sẵn), KHÔNG phải sáng tác nội dung mới —
> khác hẳn bản chất so với mọi DEBT trước đó.

## Bối cảnh đã xác nhận (đọc trực tiếp, không suy đoán)

- `output/ep_02..ep_11/episode.md` **CÓ đánh dấu section thật** — format `# HOOK [section 1 — Mở
  đầu]` (khác EP01 dùng `## 1. HOOK (...)`) — đã tự grep xác nhận **6/6 header đủ cho cả 10 tập**,
  100% nhất quán.
- `runtime/event_ledger_draft.yaml` (do `tools/event_ledger_miner.py` mine thật, có bằng chứng
  ep:line) đã có sẵn `regret_sub`/`passenger_main`/`signature_object`/`signature_setting`/
  `stop_location` cho **9/10 tập đầy đủ** (chỉ `ep_11` thiếu `regret_sub` — xử theo R195, xem dưới).
- **Còn thiếu thật:** `driver_clue` — `event_ledger_draft.yaml` **0 dữ liệu** driver clue nào được
  mine cho bất kỳ tập nào. Cần 1 đợt mine riêng TRƯỚC khi field-hoá `driver_reveal_cumulative`.
- Domain `story_planner` đang **LOCKED** (`architecture_registry.yaml`, FROZEN v1.0, Mr.Long
  authorized 5/7) — việc này là TU CHỈNH có ủy quyền (per Mr.Long 12/7), phải ghi rõ trong commit +
  registry, không tạo lock mới/không đổi tag.

## Việc cần làm (4 bước, tuần tự)

### Bước 1 — Parser mới cho format header thật của EP02-50
Viết hàm mới trong `tools/story_planner.py` (KHÔNG sửa `parse_sections()` của
`calibrate_decision_policy.py` — hàm đó thuộc domain khác, chỉ dùng cho EP01 golden, giữ nguyên) nhận
dạng đúng format `# SECTIONNAME [section N — ...]`. Test trên cả 10 tập, xác nhận tách đúng 6
section/tập, đúng thứ tự HOOK→SETUP→INCIDENT→REVEAL→PAYOFF→CLIFFHANGER (BP7 invariant).

### Bước 2 — Field-hoá dữ liệu đã mine từ `event_ledger_draft.yaml`
Với mỗi tập trong 10 tập, dùng dữ liệu `event_ledger_draft.yaml` đã có sẵn cho:
`regret_pillars_covered` (từ `regret_sub`), `characters_present`/cast (từ `passenger_main` + đối
chiếu thêm nhân vật phụ nếu event_ledger có), `location_ref` (từ `stop_location`, đối chiếu
`bible/13_setting_library.yaml` có entry khớp không — nếu không khớp, để `pending` + lý do, KHÔNG tự
tạo setting mới).
- **`ep_11` thiếu `regret_sub`:** KHÔNG tự suy đoán/gán — trả `pending` với lý do rõ ("event_ledger
  chưa mine regret_sub cho ep_11"), đúng nguyên tắc R195 đã áp dụng xuyên suốt project này.
- **`scene_function` cho mỗi scene:** KHÔNG áp máy móc bảng `EP01_COMPONENT_SCENE_FUNCTION` (chỉ
  đúng cho nội dung EP01) — đọc thật nội dung từng section của TỪNG tập (đúng cách đã làm cho DEBT-014
  EP01: trích dẫn cụ thể rồi mới gán) để xác định `gay_nghi`/`dan_chuyen`/`danh_lac_huong`/`hy_sinh`
  đúng ngữ cảnh tập đó. Đây là bước tốn công nhất — làm cẩn thận, ghi bằng chứng trích dẫn như
  `TASK_DEBT018...`/DEBT-014 đã làm mẫu.

### Bước 3 — Mine driver_clue mới (đợt mine bổ sung, chưa ai làm)
Quét `episode.md` của 10 tập tìm nhắc tới driver/73 clue (theo `clue_weight_taxonomy` của bible/18 —
đọc kỹ định nghĩa từng mức weight [1,2,5,10,30] trước khi gán, KHÔNG tự bịa weight). Nếu tập nào
KHÔNG có clue nào (hợp lệ, không phải mọi tập đều cần có) → `driver_clue: null` cho scene đó, không
ép có. Sau khi có danh sách clue thật/tập → tính `driver_reveal_cumulative` (cộng dồn weight qua các
tập theo đúng công thức mô tả tại `bible/18:246-248` `during_pre_write`), đối chiếu
`budget_curve[ep_1_10 hoặc ep_11_30].cumulative_cap` — **BLOCK nếu vượt cap** (đúng logic
`bible/18` đã định nghĩa), không tự nới cap.

### Bước 4 — Validate + field-hoá còn lại
- `cast_count`: đối chiếu `tools/character_balance_report.py` (đã wired WARN — DEBT-026), range
  [5,8] theo schema.
- `kpi_ep_range_ref`: `ep_1_10` cho EP02-10, `ep_11_30` cho EP11 (theo đúng `KPI_BUCKETS` đã có).
- Chạy `tools/story_plan_schema_check.py` xác nhận PASS cho cả 10 episode_plan mới.

## Ràng buộc

- **KHÔNG động EP01** (giữ nguyên `build_episode_plan_ep01()`, không refactor chung nếu không cần).
- **KHÔNG bịa bất kỳ field nào thiếu nguồn thật** — pending + lý do rõ, đúng nguyên tắc R195 đã dùng
  xuyên suốt (DEBT-004/013/014/021/027 đều theo mẫu này).
- Domain LOCKED → mọi commit ghi rõ "per Mr.Long authorization 12/7 (TU CHỈNH, TASK_STORY_PLANNER_
  EP02_11_PILOT.md)" + `architecture_registry.yaml` dòng `story_planner: locked` thêm 1 câu "TU CHỈNH
  12/7" theo đúng mẫu đã dùng cho các domain khác — KHÔNG tạo lock mới, KHÔNG đổi tag.
- Không cần làm hết 10 tập cùng lúc — báo tiến độ qua `log_ping.py` sau mỗi vài tập.
- `pytest tests/ -q` + `architecture_registry_check.py` phải xanh sau mỗi bước.
- Thêm test mutation-proof cho parser mới (Bước 1) — mirror mẫu `test_reality_*` đã dùng cho
  `build_episode_plan_ep01()` trong `tests/test_g6a_decision_engine.py`/tương tự.

## DoD
10 episode_plan (EP02-11) field-hoá đầy đủ theo `story_plan_schema.yaml`, mỗi field có nguồn thật
truy được (ep_ledger/parse trực tiếp episode.md/bible tham chiếu) — không có field nào bịa. Field nào
thiếu nguồn (vd `ep_11.regret_pillars_covered`) ghi rõ `pending` + lý do, không giả vờ đủ. `driver_
reveal_cumulative` mỗi tập đúng công thức, không vượt cap bible/18. Registry 0/0/0, pytest xanh, domain
`story_planner` có ghi TU CHỈNH 12/7.

## THAM CHIẾU
`governance/blueprint/schemas/story_plan_schema.yaml`, `bible/18_driver_reveal_budget.yaml`,
`runtime/event_ledger_draft.yaml`, `tools/story_planner.py::build_episode_plan_ep01()` (mẫu tham
khảo cách field-hoá + note R195), `governance/TECH_DEBT.md` DEBT-014 (mẫu cách xác định
`scene_function` có trích dẫn bằng chứng).
