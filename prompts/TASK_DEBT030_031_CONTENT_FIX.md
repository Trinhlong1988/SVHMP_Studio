# TASK — Sửa nội dung thật DEBT-031 (biến thiên pillar hối tiếc) + enforcer DEBT-032 (phần variety) + DEBT-033 (dialogue_ratio)

> Viết bởi CMD_AUDIT 12/7, per Mr.Long "fix triệt để vì đây coi như làm thật" — đây là VIẾT LẠI NỘI
> DUNG THẬT trên tập đã ship (EP02-11), không phải field-hoá dữ liệu như task story_planner trước.
> Coi là sản xuất thật, không phải nháp bỏ đi.
>
> **DEBT-030 (thoại bác tài) đã bị RÚT KHỎI task này sau khi phản biện đối kháng phát hiện đây là
> mạch truyện cố ý, không phải bug — xem chi tiết trong Bước 1 bên dưới. Không thực thi Bước 1.**

## Bước 1 — DEBT-030: TẠM DỪNG, KHÔNG xoá nội dung (đảo hướng sau phản biện đối kháng)

> **QUAN TRỌNG — đọc kỹ trước khi làm bất cứ gì với EP07-11:** kế hoạch ban đầu (xoá câu thừa của bác
> tài) đã bị THU HỒI. Phản biện đối kháng bắt buộc + CMD_AUDIT tự đọc toàn văn CLIFFHANGER cả 5 tập
> xác nhận: đây là **1 mạch truyện dàn dựng có chủ đích** (bác tài nói tăng dần đúng thứ tự "câu thứ
> ba/tư/năm", song song hành khách nhặt "vật thứ 3/4/5/6" mỗi tập, EP10 bác tài lần đầu quay đầu nhìn
> thẳng, EP11→EP12 có callback trực tiếp "hai đêm liên tục"). KHÔNG được xoá bất kỳ câu nào trong mạch
> này. Xem `TECH_DEBT.md` DEBT-030 (2 vòng quyết định, vòng 2 là bản đúng).
> **CMD KHÔNG làm Bước 1 trong task này** — chờ Mr.Long xác nhận trực tiếp ý đồ truyện (có thể hướng
> đúng là cập nhật `bible/03` công nhận cơ chế escalation, không phải sửa episode.md). Sẽ giao task
> riêng sau khi có xác nhận.

## Bước 2 — DEBT-031: đổi pillar cho 6 tập (EP03/04/06/07/09/10) — BẢNG ĐÃ SỬA LẠI

> Bảng gốc SAI (EP03→love_regret tự vi phạm distance với EP01, vốn đã là love_regret — phản biện đối
> kháng phát hiện). Dùng ĐÚNG bảng dưới đây, đã tính cả EP01 vào chuỗi:

| Tập | Pillar mới | Sub-archetype gợi ý (chọn 1, có thể điều chỉnh cho hợp mạch truyện đã có) |
|---|---|---|
| EP03 | `promise_regret` | xem `bible/11:120-` — REG_PRO_001 "hứa đưa con đi công viên — không kịp" hoặc phù hợp hơn |
| EP04 | `love_regret` | xem `bible/11:74-` — chọn sub-archetype KHÁC REG_LOV_001 (đã dùng cho EP01, `archetype_distance≥6` — EP01→EP04 chỉ cách 3, cần archetype khác dù pillar giống) |
| EP06 | `kindness_regret` | xem `bible/11:165-` — REG_KIN_001 "cô giáo cũ mất — chưa kịp đến thăm" hoặc phù hợp hơn |
| EP07 | `self_regret` | xem `bible/11:203-` — REG_SELF_001 "bỏ giấc mơ vẽ — theo nghề an toàn" hoặc phù hợp hơn. **THẬN TRỌNG:** tập này có mạch bác tài escalation ở CLIFFHANGER (xem Bước 1) — đã tự đọc xác nhận nội dung "gia đình" hiện tại nằm ở INCIDENT (chuyện "em ghế sáu", tách biệt hoàn toàn khỏi mạch bác tài về Khải Phong) — CHỈ sửa INCIDENT/REVEAL, TUYỆT ĐỐI không đụng CLIFFHANGER |
| EP09 | `promise_regret` | khác sub-archetype với EP03 (cách 6 tập, đủ archetype_distance) |
| EP10 | `love_regret` | khác sub-archetype với EP01 và EP04 |

EP01 **giữ nguyên `love_regret`** (không đổi — chỉ tính vào chuỗi để kiểm khoảng cách).
EP02/05/08/11 **giữ nguyên `family_regret`** — không sửa 4 tập này (EP11 gán mới = family, cách EP08
đúng 3 tập, đủ 4 lần gia đình = đúng trần cho phép).

**Với mỗi tập cần đổi (03/04/06/07/09/10):**
1. Đọc toàn văn tập đó — xác định đoạn nào mang nội dung "hối tiếc gia đình" (thường ở INCIDENT/REVEAL,
   gắn với `signature_object`/nhân vật liên quan cụ thể — xem `runtime/event_ledger_draft.yaml` để biết
   `signature_object`/`passenger_main` hiện tại của tập đó).
2. Viết lại đoạn đó theo pillar MỚI — đổi tình huống/mối quan hệ/kỷ vật cho khớp pillar mới (vd EP03
   đổi từ "mẹ đợi Tết" sang 1 câu chuyện tình yêu dang dở) — **đây là sáng tác nội dung thật**, cần giữ
   văn phong/nhịp điệu nhất quán với phần còn lại của tập (HOOK/SETUP/PAYOFF/CLIFFHANGER không đổi trừ
   khi nhắc trực tiếp tới regret cũ).
3. Cập nhật `runtime/event_ledger_draft.yaml` cho tập đó: `regret_sub` (ID mới từ bible/11),
   `signature_object` (đổi theo `signature_objects` của sub-archetype mới), có thể cần đổi
   `passenger_main` nếu nhân vật cũ gắn chặt với câu chuyện gia đình cũ (tuỳ mức độ viết lại).
4. Chạy lại `python tools/event_ledger_miner.py` cho tập đó (hoặc cập nhật tay + ghi rõ lý do không
   chạy lại miner) để xác nhận evidence ep:line khớp nội dung mới — KHÔNG để evidence cũ trỏ sai.

**Sau bước 2:** chạy lại toàn bộ pipeline story_planner cho EP02-11 (đã field-hoá ở task trước) —
`regret_pillars_covered` phải đổi theo đúng bảng trên, `story_plan_schema_check.py` vẫn PASS.

## Bước 3 — DEBT-032: xây enforcer chống tái diễn (KHÔNG tách việc riêng, làm luôn trong task này)

Chỉ làm **check #2** trong task này — check #1 (driver dialogue) TẠM HOÃN cùng Bước 1 (chờ Mr.Long xác
nhận ý đồ truyện; nếu hướng đúng là "công nhận cơ chế escalation" thay vì "chỉ 2 câu", thì bản chất
check #1 sẽ hoàn toàn khác — viết check bây giờ theo giả định "chỉ 2 câu" có thể phải viết lại từ đầu).

2. **Regret variety check:** wire vào `svhmp_preflight_qa.py` (tái dùng khung sẵn có — R211). Đọc
   `regret_sub` của N tập gần nhất từ `event_ledger_draft.yaml` (đã có sẵn, không cần mine lại), đối
   chiếu `bible/11_regret_catalog.yaml` `variety_rules` (`pillar_distance`, `family_regret_max_per_10_ep`,
   `pillar_per_10_ep_min_distinct`). FAIL nếu vi phạm. Viết mutation-proof test (mirror mẫu
   `_pause_delegation_body_ok`/`_run_all_body_ok` đã dùng nhiều lần trong dự án). Chạy lại trên EP01-11
   SAU KHI sửa xong Bước 2 — phải PASS, xác nhận vá đúng.

## Bước 4 — DEBT-033: wire dialogue_ratio/narration_ratio vào decision_engine + đo cho EP02-11

`tools/calibrate_decision_policy.py` đã tính đúng cho EP01 (`dialogue_ratio=0.3564`) nhưng chưa nối
vào đâu cả. Việc cần làm:
1. Sửa `tools/decision_engine.py::build_packet()` đọc/gọi kết quả từ `calibrate_decision_policy.py`
   (tái dùng hàm tính có sẵn, KHÔNG viết lại công thức) — thêm `dialogue_ratio`/`narration_ratio` vào
   output packet thật cho EP01.
2. Cập nhật `governance/blueprint/bp6/decision_contract.yaml` dòng 33-51: đổi `status: planned` →
   `status: calibrated` (hoặc tên trạng thái phù hợp theo quy ước file này đang dùng), ghi rõ giá trị
   + nguồn (`calibrate_decision_policy.py`, EP01 golden).
3. Mở rộng đo `dialogue_ratio` cho EP02-11 — dùng `parse_sections_v2()` mới xây ở Bước story_planner
   trước (tái dùng, không viết lại) để đếm word thoại/tổng word mỗi tập. Ghi kết quả vào
   `calibration_evidence` của packet tương ứng nếu `decision_engine.py` được gọi cho các tập đó (nếu
   `build_packet()` hiện chỉ hỗ trợ EP01, ghi `pending` cho EP02-11 kèm lý do — KHÔNG tự mở rộng
   `build_packet()` sang xử lý EP02-90 nếu việc đó ngoài phạm vi task này, chỉ cần trả về SỐ ĐO ĐƯỢC
   cho báo cáo, không nhất thiết phải wire hết vào packet chính thức).

Domain `decision_engine` (G6a) đang LOCKED — TU CHỈNH per Mr.Long 12/7, ghi rõ trong commit +
`architecture_registry.yaml` dòng lock `decision_engine`.

## Ràng buộc chung

- **Bước 1 KHÔNG LÀM trong task này** — chờ Mr.Long xác nhận riêng. CMD tuyệt đối không tự ý xoá/sửa
  bất kỳ câu thoại nào của bác tài ở EP07-11.
- **R197 FULL_TEXT_GATE:** chạy `svhmp_preflight_qa.py` cho MỌI tập đã sửa (Bước 2) trước khi commit —
  đây là nội dung sản xuất thật, không phải test data.
- **`bible/32_repair_contract.yaml`:** Bước 2 (đổi pillar) là ngoại lệ có ý thức — viết lại 1 phần nội
  dung theo pillar mới là cần thiết để fix đúng bản chất vấn đề, không phải rewrite tuỳ tiện — nhưng
  vẫn PHẢI giữ nguyên `locked` facts khác của bible/32 (timeline 7:10/8 năm, immutable_dialogues bác
  tài, mạch escalation CLIFFHANGER của EP07 — xem lưu ý riêng trong bảng Bước 2 — object_state nếu
  không liên quan tới đoạn đang sửa).
- KHÔNG động EP01 (chỉ tham chiếu để tính khoảng cách, không đổi nội dung), EP12-50 (ngoài phạm vi).
- `pytest tests/ -q` + `architecture_registry_check.py` xanh sau mỗi bước.
- Domain LOCKED (`story_planner`/`decision_engine`) nếu Bước 3/4 chạm code → TU CHỈNH per Mr.Long
  12/7, ghi rõ trong commit + registry (mirror mẫu đã dùng cho task story_planner pilot).
- Báo tiến độ qua `log_ping.py` sau mỗi bước lớn (không đợi cả 4 bước xong mới báo 1 lần).

## DoD
EP03/04/06/07/09/10: pillar mới đúng BẢNG ĐÃ SỬA (Bước 2), nội dung viết lại nhất quán, event_ledger
cập nhật khớp — EP07 giữ nguyên CLIFFHANGER, chỉ đổi INCIDENT/REVEAL. EP01/02/05/08/11: giữ nguyên,
không đổi. Enforcer regret-variety PASS trên EP01-11 sau sửa, có mutation-proof test.
`dialogue_ratio`/`narration_ratio` EP01 wired vào `decision_engine.py` output + `bp6/decision_
contract.yaml` status cập nhật; EP02-11 đo được (hoặc pending có lý do rõ). Registry 0/0/0, pytest
xanh, DEBT-031/033 đóng trong TECH_DEBT.md với bằng chứng. **DEBT-030/032 (driver dialogue) VẪN MỞ,
KHÔNG đóng trong task này** — chờ Mr.Long xác nhận riêng.

## THAM CHIẾU
`governance/TECH_DEBT.md` DEBT-030 (2 vòng quyết định — đọc kỹ vòng 2)/031/032/033, `bible/03_character_
bible.yaml`, `bible/11_regret_catalog.yaml`, `bible/32_repair_contract.yaml`,
`runtime/event_ledger_draft.yaml`, `governance/blueprint/bp6/decision_contract.yaml`,
`tools/calibrate_decision_policy.py`, `prompts/TASK_STORY_PLANNER_EP02_11_PILOT.md` (task trước, đã
xong, field-hoá phần này dựa trên).
