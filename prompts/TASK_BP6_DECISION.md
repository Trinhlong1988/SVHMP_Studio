# TASK BP6 — DECISION ARCHITECTURE (theo BP_PIPELINE_MASTER.md)

## MISSION
Spec đầy đủ cho `decision_engine` (domain L5, đã khai BP-C) — nơi own NHỊP truyện,
chống generator hallucination. **FORMAT + CONTRACT, KHÔNG BỊA SỐ.**

## DELIVERABLES
1. `governance/blueprint/bp6/decision_contract.yaml` — 12 knob (dialogue_ratio ·
   narration_ratio · emotion_curve · fear_curve · suspense_curve · reveal_curve · pacing ·
   scene_budget · information_budget · silence_budget · character_focus · pov); mỗi knob:
   knob_id · type (scalar|curve|enum) · range/units · consumer (generator — read-only theo BP3) ·
   calibration_source · lifecycle · status planned.
2. **LUẬT CALIBRATION (R195 — bất di dịch):** mọi giá trị mặc định = `calibrate_from:
   bible/31_golden_samples.yaml + EP01 golden` — file này CẤM chứa số cụ thể nào ngoài
   range hợp lệ; số thật sinh ở G6 từ golden. Validator: knob có giá trị hardcode → FAIL.
3. `governance/blueprint/bp6/decision_io.yaml` — input (story_planner plan schema) →
   output (decision packet schema mà generator nhận); mọi field generator được đọc phải
   nằm trong packet — generator KHÔNG có nguồn nhịp nào khác (mirror audit_rule đã khai BP-C).
4. `governance/blueprint/bp6/00_decision.md` (11-element) — ghi rõ ranh giới:
   story_planner = CÁI GÌ xảy ra · decision_engine = NHỊP thế nào · generator = VIẾT ra sao.
5. Validator: 12 knob đủ · consumer đúng BP3 · không hardcode số · packet schema khớp io.
6. Negative test: knob thiếu · knob hardcode 45% · consumer ghi-được (vi phạm read-only) ·
   packet chứa field ma.

## MUTATION AUDIT SẼ BẮN
hardcode dialogue_ratio=0.45 → FAIL · knob thứ 13 lạ → FAIL · generator writable knob → FAIL.
STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.
