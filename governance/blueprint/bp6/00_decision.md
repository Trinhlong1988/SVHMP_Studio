# BP6 — 00_decision.md — Decision Architecture (decision_engine L5)
> Enforce: `tools/bp6_decision_check.py` · chứng thực: `tests/test_bp6_decision.py` · data: `governance/blueprint/bp6/decision_contract.yaml` + `governance/blueprint/bp6/decision_io.yaml`.

**Mission:** Spec đầy đủ cho `decision_engine` (domain L5, khai BP-C finding #6) — nơi own NHỊP truyện, chống generator hallucination. FORMAT + CONTRACT, KHÔNG BỊA SỐ (R195).

**Purpose:** Khóa ranh giới ba tầng trước G-phase: **story_planner = CÁI GÌ xảy ra · decision_engine = NHỊP thế nào · generator = VIẾT ra sao.** Generator không còn nguồn nhịp nào ngoài decision packet — hết đường "tự nghĩ" ratio/pacing.

**Scope:** 12 knob (dialogue_ratio · narration_ratio · emotion_curve · fear_curve · suspense_curve · reveal_curve · pacing · scene_budget · information_budget · silence_budget · character_focus · pov) + IO contract (plan → packet). KHÔNG viết engine (tools/decision_engine.py = planned M2), KHÔNG sinh số policy (bible/42 = planned, calibrate G6), KHÔNG sửa render LOCKED.

**Authority:** BP0 v2.0 + BP1-BP5 LOCKED = nguồn luật. Phán quyết reconcile: `reveal_curve` (bp6) = nhịp nhả fact TRONG tập, KHÁC reveal TIMING xuyên tập (story_planner own, bible/18) và KHÁC reveal PERMISSION (character own, BP2b) — 3 chữ CẤM gộp. Đổi knob list = RFC + Mr.Long.

**Responsibilities:** `decision_contract`: 12 knob, mỗi knob knob_id/type(scalar|curve|enum)/units/valid_range/consumer(generator read-only theo BP3)/calibration_source(bible/31 + EP01 golden)/lifecycle/status planned. `decision_io`: input = REQUIREMENT từ story plan (schema planned của story_planner — bp6 CHỈ tham chiếu, không định nghĩa hộ); output = packet schema, per_scene.knobs keys PHẢI == đúng 12 knob_id.

**Workflow:** sửa data → `bp6_decision_check.py` exit 0 → pytest mutation → commit R200 → audit 7 bước → Mr.Long ký.

**Mandatory Rules:** (1) **R195 calibration bất di dịch**: số chỉ được nằm trong `valid_range`/enum định danh; `default/value/baseline/initial` trong knob = FAIL — số thật sinh ở G6 từ golden. (2) ĐÚNG 12 knob — thiếu/thừa = FAIL. (3) Consumer mọi knob = generator read_only (BP3); generator writable = VIOLATION leo thang. (4) Packet field ma (khác 12 knob) = FAIL. (5) Planned ref đủ 5 metadata. (6) DUP-KEY loader single-impl (import blueprint_constitution_check) + version khớp.

**PASS Criteria:** `bp6_decision_check.py` exit 0 + mutation battery xanh trong `pytest tests/` (ENFORCED qua ci_gate pytest_suite).

**FAIL Criteria:** hardcode số (vd dialogue_ratio default 0.45) / knob 13 lạ / thiếu knob / consumer ghi-được / packet field ma / dup-key → exit 1.

**Examples:** thêm `default: 0.45` vào dialogue_ratio → FAIL R195-HARDCODE; thêm knob `music_volume` → FAIL KNOB-LA (audio domain, không phải nhịp truyện); đổi consumer access `write` → FAIL LEO-THANG; packet thêm field `magic_number` → FAIL FIELD-MA.

**Promotion Rules:** `bp6_decision: candidate` — Builder không lock/tag; Mr.Long ký sau audit (reconcile `governance/constitution/00_constitution.md`). REALITY ANCHOR (luật 9): checker chạy trên data bp6 THẬT + số đo trong `reports/BP6_REPORT.md`.

## Ghi chú semantics (kiểm duyệt phán khi audit)
`values` của enum `pacing` là NHÃN ĐỊNH DANH format (rat_cham/cham/vua/nhanh) — không phải giá trị calibrate; scene nào mang nhãn nào là việc của G6 golden. `character_focus`/`pov` dùng `values_source` trỏ nguồn thật (roster/bible/01) thay vì liệt kê cứng — chống drift khi roster đổi.
