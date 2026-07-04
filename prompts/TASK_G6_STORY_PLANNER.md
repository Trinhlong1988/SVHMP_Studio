# TASK G6 — STORY PLANNER + DECISION ENGINE (finalize từ Desktop draft 4/7, kiểm chứng + phản biện 5/7)

> Nền vững: BP6 Decision (LOCKED, 12 knob format, MỖI knob đã có sẵn `calibration_source` +
> method cụ thể) + BP7 Narrative (LOCKED, 6 cấp Scene→Act→Episode→Season→Series→Ending) — đã
> re-verify trực tiếp cả 2, khớp draft gốc. G6 = ĐỔ SỐ THẬT vào khung 2 pack đó, calibrate từ
> golden, KHÔNG tự nghĩ số (R195).

## ⚠️ PHẢN BIỆN QUAN TRỌNG — draft gốc gộp nhầm 2 domain khác nhau
Draft gốc (4/7) tiêu đề "STORY PLANNER" nhưng cả 4 deliverable D1-D4 CHỈ làm phần
`decision_engine` (bible/42 policy). Đọc trực tiếp `blueprint_domains.yaml` dòng 486-514 phát
hiện: BP0 khai **`story_planner` và `decision_engine` là 2 domain TÁCH BIỆT, mỗi domain 1
`blocking_dependency` KHÁC NHAU**:

| Domain | Trách nhiệm | blocking_dependency (BP0 khai, đã đọc trực tiếp) | Sẵn sàng chưa? |
|---|---|---|---|
| `decision_engine` | 12 knob nhịp truyện (dialogue_ratio...pov) | "EP01 golden production output (R196) làm dữ liệu calibrate" | **✅ ĐÃ SẴN SÀNG** — `bible/31_golden_samples.yaml` đã có `EP01_FULL_v103.mp3` (Mr.Long accept 30/6 12:08), `publish_score_text: PASS (Logic 100, Language 100, TTS 100)` — golden data đã tồn tại thật |
| `story_planner` | "Kế hoạch 100 tập: driver reveal budget (bible/18), phân bổ regret/arc, series KPI" — `tools/story_planner.py` | "event ledger + timeline manager (M1) — planner cần dữ liệu thật để xếp" | **❌ CHƯA SẴN SÀNG** — phụ thuộc trực tiếp `runtime/event_ledger_draft.yaml` (G4 D2) + `tools/timeline_check.py` (G4 D1), G4 CHƯA xong tại thời điểm viết task này |

**Kết luận:** KHÔNG chờ G4 xong mới bắt đầu G6 toàn bộ — CHIA làm 2 mảng độc lập, chạy G6a NGAY,
để G6b lại đúng lúc G4 báo D1/D2 xong.

## ĐIỀU KIỆN CHẠY
Phụ thuộc thật theo BP3 (`dependency_detail.yaml`): `story_planner` đọc từ `character`(G2),
`event`/`timeline`/`world`(G4), `supernatural`(G5) — **KHÔNG phụ thuộc `dialogue`(G3)**, khác
với thứ tự liệt kê G2→G3→G4→G5→G6 trong bảng roadmap (đó chỉ là thứ tự trình bày, không phải
dependency graph thật). G2 đã đóng batch (37/37 Tier1 + fix PAS_0126), G5 đã xong — G6a có thể
claim và chạy NGAY.

## MISSION
"Đạo diễn tập truyện" — chưa viết chữ nào, chỉ quyết NHỊP: bao nhiêu % thoại/dẫn, cảm xúc/căng
thẳng lên xuống ra sao, ngân sách cảnh — VÀ kế hoạch dài hạn 100 tập (driver reveal, cân bằng
regret/arc). Generator (G7) sau này CHỈ đọc quyết định này, không tự nghĩ.

## NỀN ĐÃ CÓ (reconcile — CẤM nhân đôi R211; đã re-verify trực tiếp 5/7)
| Đã có | Ở đâu | Verify |
|---|---|---|
| 12 knob FORMAT + calibration_source/method sẵn cho từng knob | `bp6/decision_contract.yaml` (LOCKED v1.0) | ✅ đếm trực tiếp: đúng 12 knob (dialogue_ratio, narration_ratio, emotion_curve, fear_curve, suspense_curve, reveal_curve, pacing, scene_budget, information_budget, silence_budget, character_focus, pov), MỖI knob có sẵn `calibration_source: {calibrate_from, method, status: planned_G6}` — chỉ cần THI HÀNH method đã ghi, không tự nghĩ cách đo |
| Decision packet schema | `bp6/decision_io.yaml` | Chưa re-đọc chi tiết field — D3 tự đối chiếu khi build |
| 6 cấp cấu trúc + pacing_format | `bp7/story_structure.yaml` + `bp7/pacing_format.yaml` (LOCKED v1.0) | ✅ xác nhận đúng Scene→Act→Episode→Season→Series→Ending |
| Golden reference | `bible/31_golden_samples.yaml` | ✅ `EP01_FULL_v103.mp3`, `approved_by: Mr.Long`, `publish_score_text: PASS (Logic 100, Language 100, TTS 100)` — có thật, đọc trực tiếp dòng 80-106 |
| Domain đã khai (decision_engine) | BP0 dòng 555-592: `source_of_truth planned → bible/42_decision_policy.yaml`, `manager planned → tools/decision_engine.py` | ✅ khớp draft |
| Domain đã khai (story_planner, KHÁC decision_engine) | BP0 dòng 486-514: `manager planned → tools/story_planner.py`, `schema planned → schemas/story_plan_schema.yaml`, nguồn thật đã có `bible/18_driver_reveal_budget.yaml` + `bible/01_series_bible.yaml` + `bible/16_series_kpi.yaml` (cả 3 status: exists) | ✅ mới phát hiện — KHÔNG có trong draft gốc |

## DELIVERABLES

### === G6a — DECISION ENGINE (chạy NGAY, không chờ G4) ===

#### D1 — `bible/42_decision_policy.yaml` (field-hóa đúng slot BP0 đã khai)
Số THẬT cho 12 knob — **dùng ĐÚNG method đã ghi sẵn trong từng `knob.calibration_source.method`
của `bp6/decision_contract.yaml`** (KHÔNG tự nghĩ cách đo khác). Mỗi giá trị PHẢI có
`calibrated_from: {source: bible/31, evidence: <cách tính>}`. VD `dialogue_ratio`: method đã ghi
"đo word-count thoại/tổng trên golden" → chạy đúng phép đo đó trên `EP01_FULL` text, ghi số đo
được, KHÔNG đoán 0.45.

#### D2 — `tools/decision_policy_check.py`
Validator: mọi số trong bible/42 PHẢI trong `valid_range` đã khai BP6 · mọi `calibrated_from`
PHẢI trỏ evidence thật trong bible/31 (path+key resolve, không bịa) · KHÔNG số nào thiếu nguồn
calibrate (số mồ côi = FAIL) · đủ đúng 12 knob (không thiếu/thừa so BP6).

#### D3 — `runtime/decision_engine.py` (manager tối thiểu — CHỈ phần đọc bible/42)
Đọc `bible/42` → build phần packet KHÔNG phụ thuộc story_planner (12 knob value) theo schema
`bp6/decision_io.yaml`. Field packet nào cần input từ story plan (G6b) → để `status: planned`
trung thực, KHÔNG bịa giá trị giả để "cho đủ field". KHÔNG viết logic sinh text.

#### D4 — Negative test + mutation
Số ngoài valid_range → FAIL · thiếu calibrated_from → FAIL · knob thiếu/thừa vs BP6 → FAIL ·
packet field lạ ngoài `bp6/decision_io.yaml` → FAIL.

### === G6b — STORY PLANNER (CHỈ bắt đầu sau khi G4 báo D1 timeline_check + D2 event_ledger_miner xong — check `python tools/build_claim.py status g4_world` trước, KHÔNG tự đoán G4 đã xong) ===

#### D5 — `tools/story_planner.py` (manager tối thiểu)
Đọc `bible/18_driver_reveal_budget.yaml` (EP73+EP90 reserved) + `bible/01_series_bible.yaml` +
`bible/16_series_kpi.yaml` (cả 3 đã `status: exists`, KHÔNG bịa thêm) + `runtime/event_ledger_draft.yaml`
(G4 D2, BẮT BUỘC đã tồn tại) + `tools/timeline_check.py` output (G4 D1) → build kế hoạch
100 tập (driver reveal timing, phân bổ regret/arc, series KPI target) → field-hóa đúng slot BP0
`schemas/story_plan_schema.yaml` (đang planned, cần Mr.Long duyệt format trước khi field-hóa —
RÀNG BUỘC RIÊNG, không tự quyết format).

#### D6 — Gate 1 cửa + wire (gộp cả G6a+G6b)
`tools/g6_story_planner_check.py` (mirror pattern blueprint_suite/g3_dialogue_gate/g4_world_check):
gọi D2+D4 (G6a) và validator D5 (G6b, khi đã build), matrix PASS/FAIL, KHÔNG short-circuit. Wire
ci_gate stage `G6_story_planner` + unwire-guard test NGAY commit đầu (bài học G2_roster).

## REALITY ANCHOR (luật 9)
- `decision_policy_check.py` chạy PASS trên `bible/42` thật, MỌI số trace được về bible/31 golden
  thật đã tồn tại trên disk — không phải giả định.
- G6b KHÔNG được field-hóa `story_plan_schema.yaml` bằng số/cấu trúc tự nghĩ nếu Mr.Long chưa
  duyệt format (đúng blocking_dependency BP0 đã khai) — để `planned` trung thực nếu chưa tới lượt.

## MUTATION AUDIT SẼ BẮN (khai trước)
M1 knob value ngoài valid_range → FAIL · M2 thiếu calibrated_from → FAIL · M3 knob thiếu/thừa
(11 hoặc 13) vs 12 đã khóa BP6 → FAIL · M4 packet field lạ ngoài `bp6/decision_io.yaml` → FAIL ·
M5 gỡ stage G6_story_planner → unwire test đỏ · M6 D5 build TRƯỚC khi G4 D1/D2 thật sự tồn tại
trên disk → FAIL (chống build-ahead, REALITY ANCHOR luật 9) · M7 story_plan_schema field-hóa mà
KHÔNG có bằng chứng Mr.Long duyệt format → FAIL (R211 tinh thần: không tự quyết hộ owner khác).

## DoD
G6a: 12 knob calibrate xong + evidence bible/31 ✅ · decision_policy_check 0 FAIL trên bible/42
thật ✅ · decision_engine.py packet builder (phần không cần story plan) chạy được ✅ · gate wired
+ unwire-guard ✅ · registry 0/0/0 · pytest xanh.
G6b (RIÊNG, có thể DoD sau, không chặn G6a đóng gói): story_planner.py đọc đủ 3 nguồn bible đã
exists + event ledger G4 thật ✅ · KHÔNG bịa format story_plan_schema nếu chưa có chữ ký Mr.Long ✅.

## RÀNG BUỘC
Claim pack trước khi build (`build_claim.py claim g6_story_planner <phiên>`) · KHÔNG sửa bp6/bp7
đã LOCK (RFC nếu cần đổi contract) · KHÔNG sinh content episode · số bịa = BÁC (R195) · nhân đôi
tool sẵn = BÁC (R211) · G6b KHÔNG được bắt đầu nếu chưa xác nhận G4 D1/D2 tồn tại thật trên disk
(check bằng lệnh máy, không suy đoán từ tên claim "released").

STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX (báo riêng G6a và G6b nếu 1 trong 2 chưa tới lượt).
