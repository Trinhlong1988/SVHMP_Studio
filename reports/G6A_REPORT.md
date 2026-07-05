# G6a — DECISION ENGINE (TASK_G6_STORY_PLANNER.md, chỉ phần G6a — G6b blocked bởi G4→story_planner)

CMD_BUILD, 2026-07-05. Claim `g6_story_planner`.

## Deliverables

- **D1** `tools/calibrate_decision_policy.py` — đo THẬT trên `output/ep_01/episode_golden_text.md`
  (golden LOCKED, bible/31) + `bible/42_decision_policy.yaml` — field-hóa 12 knob BP6.
- **D2** `tools/decision_policy_check.py` — validator: range/calibrated_from/knob-đóng.
- **D3** `tools/decision_engine.py` — manager tối thiểu, chỉ đọc bible/42, build phần packet
  không phụ thuộc story_planner (field cần plan G6b → `status: planned`, không bịa).
- **D4** `tests/test_g6a_decision_engine.py` — 17 test (M1-M3 mutation + reality anchor).
- **D6** `tools/g6_story_planner_check.py` — gate 1 cửa (G6a portion), wire `ci_gate.py`
  (`G6_story_planner`/`ONT6001`) + unwire-guard (đòn thử 2 chiều: gỡ dòng → test đỏ,
  khôi phục → xanh lại).

## Kết quả calibrate — 11/12 knob xong, 1 BLOCKED (không bịa số, R195)

| Knob | Giá trị | Nguồn |
|---|---|---|
| dialogue_ratio | 0.3564 | word-count thoại/tổng golden |
| narration_ratio | 0.6436 | 1 - dialogue_ratio |
| emotion_curve | per-scene 0.6-0.95 | tổng emo-value bảng EMOTION CURVE v7 (golden dòng ~579-589) |
| fear_curve | per-scene 0-0.3 | giá trị "afraid" trong bảng trên, vắng = 0 |
| **suspense_curve** | **BLOCKED** | method BP6 (map bible/25 template) không khớp EP01 (pilot, không phải passenger-arc EP51-90) — không có số thay thế thật, để trống thay vì bịa |
| reveal_curve | per-scene 0-4 | đếm TAY fact-mới có trích dẫn dòng cụ thể |
| pacing | per-scene rat_cham/cham | avg_sentence_words (KHÔNG dùng wpm — xem finding) |
| scene_budget | 6 | đếm section HOOK..CLIFFHANGER |
| information_budget | 4 | max(reveal_curve) |
| silence_budget | 8 | max [pause:*ms]/scene |
| character_focus | Khai-Phong / Co_gai_ghe_bay_moi | quan sát trực tiếp CLIFFHANGER đổi focal |
| pov | 2 giá trị tự đề xuất | enum CHƯA có trong bible/01, đề xuất mới cho bible/42 (cần Mr.Long xác nhận) |

## Finding quan trọng (tự phát hiện khi verify, không giấu)

1. **wpm tính từ section-header timestamp SAI** — HOOK cho ra ~789 wpm, CLIFFHANGER ~469 wpm,
   mâu thuẫn trực tiếp với target 142 wpm ghi rõ trong CHÍNH golden text (dòng 68-71). Kết luận:
   timestamp header là ước lượng soạn thảo cũ (từ bản draft khác `EP01_FULL_v103.mp3` đã render),
   không phải đo thật trên audio. Đã đổi tín hiệu pacing sang `avg_sentence_words` (đo độc lập,
   vẫn từ golden thật) — có note rõ trong `calibrated_from.finding` của knob `pacing`.
2. **suspense_curve không calibrate được với method BP6 đã ghi.** `bible/25_suspense_arc_templates.yaml`
   chỉ định nghĩa 6 arc CATEGORICAL cho passenger backstory EP51-90, không phải curve số 0-1,
   và EP01 (pilot/establish) không khớp template nào trong 6 cái. Tự nghĩ 1 công thức quy đổi
   beat-label sang số sẽ là BỊA (vi phạm R195) — để BLOCKED, ghi rõ 3 phương án cho Mr.Long chọn
   trong `bible/42_decision_policy.yaml#knobs.suspense_curve.reason_not_calibrated`.
3. **Path mismatch phát hiện khi field-hóa BP0**: task file (D3 heading) ghi `runtime/decision_engine.py`
   nhưng BP0/BP4/BP6/BP9 (LOCKED) đều khai `tools/decision_engine.py` nhất quán — đã tạo đúng
   `tools/` theo governance LOCKED, không theo heading task (task tự mâu thuẫn nội bộ, dòng 41
   của chính nó cũng trích BP0 đúng là `tools/`). Tương tự D2 dùng tên `tools/decision_policy_check.py`
   (đúng theo task) khác với `tools/decision_validator.py` mà BP0 từng dự kiến (audit 3/7,
   trước khi task 5/7 chốt tên cụ thể hơn) — đã flip BP0 `validator.path` trỏ đúng file thật.

4. **BP4 runtime_flow.yaml cũng khai `tools/decision_engine.py` là `planned`** (hop 2.via) —
   phát hiện qua `pytest` full suite (test_bp4_runtime.py/test_bp5_validation.py tự bắt DRIFT/STUB
   khi planned_path đã tồn tại trên disk). Đã flip `hop2.via.status: planned→exists` (giữ
   `hop.status: planned` vì input `episode_plan` từ story_planner — hop 1 — vẫn chưa có, nên
   luồng đầy đủ chưa vận hành thật). Bài học: field-hóa 1 path phải rà TẤT CẢ file governance
   tham chiếu path đó (BP0 + BP4 + BP6 + BP9 đều có thể cùng khai 1 đường dẫn), không chỉ sửa
   nơi đầu tiên tìm thấy.

## Field-hóa BP0 (governance/blueprint/blueprint_domains.yaml, domain decision_engine)

Flip planned→exists cho `source_of_truth` (bible/42) + `manager` (tools/decision_engine.py) +
`validator` (tools/decision_policy_check.py) — đúng theo task này tự commission field-hóa slot đó
(mirror tiền lệ BP9 publisher.schema/validator). `schema` (decision_schema.yaml) giữ nguyên
`planned` vì KHÔNG nằm trong D1-D4 deliverable của G6a.

## Bằng chứng self-test

| # | Lệnh | Kết quả | Exit |
|---|---|---|---|
| 1 | `tools/decision_policy_check.py` | 0 vi phạm thật (1 WARN đã công bố: suspense_curve) | 0 |
| 2 | `tools/decision_engine.py 1` | packet 6 scene, đủ 12 knob key/scene, suspense_curve=null (không bịa) | 0 |
| 3 | `tools/g6_story_planner_check.py` | 2/2 tầng xanh | 0 |
| 4 | `tools/bp6_decision_check.py` | 12/12 knob, PASS (bp6 không bị đụng) | 0 |
| 5 | `tools/blueprint_constitution_check.py` | 23 domain, 0 vi phạm (sau flip decision_engine) | 0 |
| 6 | `tools/architecture_registry_check.py` | 0/0/0 | 0 |
| 7 | `pytest tests/test_g6a_decision_engine.py -v` | 17/17 passed | 0 |
| 8 | `pytest tests/ -q` (full suite) | xem log push CI gate | — |

## G6b — CHƯA bắt đầu (đúng ràng buộc task)

`build_claim.py status g4_world` xác nhận `g4_world` đã `released` (session CMD_BUILD, phiên trước)
— G4 D1/D2 đã tồn tại thật trên disk (`tools/timeline_check.py`, `runtime/event_ledger_draft.yaml`).
G6b VẪN CHƯA bắt đầu trong lượt này (ngoài phạm vi "thực hiện prompt g6a" được giao) — để dành
cho lượt tiếp theo nếu Boss giao tiếp, tránh làm vượt phạm vi claim hiện tại.

## DoD G6a

12 knob calibrate: 11/12 xong + 1 blocked minh bạch (không bịa) · decision_policy_check 0 FAIL
trên bible/42 thật ✅ · decision_engine.py packet builder chạy được ✅ · gate wired + unwire-guard ✅ ·
registry 0/0/0 ✅ · BP0 constitution 0 vi phạm ✅ · pytest xanh (xem log push).

**READY FOR AUDIT = YES** (kèm 2 điểm cần Mr.Long quyết: suspense_curve method + tên enum `pov`)
