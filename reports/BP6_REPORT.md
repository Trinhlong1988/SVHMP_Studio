# BP6 REPORT — Decision Architecture (candidate, chờ audit 7 bước + Mr.Long ký)

## Số đo (REALITY ANCHOR — luật 9: validator PASS trên dữ liệu THẬT)

| Số đo | Giá trị | Nguồn máy |
|---|---|---|
| Knob khai | **12/12** (đúng danh sách TASK đóng) | `bp6_decision_check.py` máy đếm, `assert set == EXPECTED` |
| Checker trên data thật | **exit 0, 0 violation** | `tools/bp6_decision_check.py` |
| Mutation battery | **17/17 pass** | `tests/test_bp6_decision.py` (pytest) |
| Số hardcode trong contract | **0** (numeric-leak scan: số chỉ trong valid_range) | check R195 |
| Consumer read-only | **12/12 knob** generator read_only (BP3) | check LEO-THANG |
| Packet field | **5 field đóng** + per_scene.knobs == 12 knob_id (field ma = FAIL) | check FIELD-MA |

## Deliverables

1. `governance/blueprint/bp6/decision_contract.yaml` — 12 knob: dialogue_ratio · narration_ratio · emotion_curve · fear_curve · suspense_curve · reveal_curve · pacing · scene_budget · information_budget · silence_budget · character_focus · pov. Mỗi knob: knob_id/type(scalar|curve|enum)/units/valid_range/consumer/calibration_source/lifecycle/status planned.
2. **Luật calibration R195**: mọi default = `calibrate_from: bible/31_golden_samples.yaml + EP01 golden`; file KHÔNG chứa số ngoài valid_range — validator numeric-leak scan FAIL nếu vi phạm. Số thật sinh ở G6 (bible/42_decision_policy.yaml giữ planned với 5 metadata).
3. `governance/blueprint/bp6/decision_io.yaml` — input = REQUIREMENT 5 field từ story plan (schema planned của story_planner, bp6 chỉ tham chiếu — không định nghĩa hộ); output = decision packet: nguồn nhịp DUY NHẤT của generator (mirror audit_rule BP-C), bắt buộc `calibration_evidence`.
4. `governance/blueprint/bp6/00_decision.md` — 11-element; ranh giới: story_planner = CÁI GÌ · decision_engine = NHỊP · generator = VIẾT. Reconcile reveal 3 tầng: PERMISSION (character) ≠ TIMING xuyên tập (story_planner) ≠ NHỊP nhả trong tập (decision_engine).
5. `tools/bp6_decision_check.py` — loader single-impl import từ blueprint_constitution_check (chuẩn BP5, utf-8-sig).
6. `tests/test_bp6_decision.py` — 17 test; đủ 4 đòn mutation TASK báo trước: hardcode dialogue_ratio=0.45 → FAIL R195-HARDCODE · knob 13 `music_volume` → FAIL KNOB-LA · generator writable → FAIL LEO-THANG · packet `magic_number` → FAIL FIELD-MA; cộng dup-key, numeric-leak lạc chỗ, reader ngoài grant BP0, writer leo thang, planned thiếu metadata.

## Ghi chú cho auditor

- **KHÔNG sửa BP5 LOCKED**: `bp6_check` đứng riêng (như bp4_check trước BP5); wire vào `blueprint_suite_check` SUITE = quyết định lúc lock BP6 (sửa tool pack locked cần Mr.Long).
- Registry: `bp6_decision: candidate` (1 dòng, không dup-key — auditor REPLACE in-place khi lock theo ROOT-FIX 8af9682).
- Builder không kết luận PASS/FREEZE — chỉ READY FOR AUDIT.
