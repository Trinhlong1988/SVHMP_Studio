# G6b — STORY PLANNER (PROMPT_HANDOFF_CMD_BUILD_G6B.md, field-hóa schema đã duyệt)

CMD_BUILD, 2026-07-05. Claim `g6b_story_planner`.

## Deliverables

- **D5a** `governance/blueprint/schemas/story_plan_schema.yaml` — field-hóa NGUYÊN VĂN
  `schema_draft` từ `governance/proposals/story_plan_schema_proposal.yaml` (`proposal_status:
  APPROVED`, `mr_long_decision: APPROVED_A`, commit `9f5ccbd`) — không sửa 1 field nào.
- **D5b** `tools/story_planner.py` — manager tối thiểu, đọc `bible/18`/`bible/01_series_bible`/
  `bible/16` + `runtime/event_ledger_draft.yaml` (G4 D2) + tái dùng `calibrate_decision_policy.
  parse_sections()` (G6a, R211 không viết lại) để build:
  - `season_plan`: **3 entry ĐẦY ĐỦ thật** (season boundary từ `bible/01_series_bible` +
    driver_phase_refs từ overlap thật với `bible/18.budget_curve` + regret_distribution_target
    từ `project_config.yaml`).
  - `episode_plan` + `scene`: **CHỈ EP01 xây được đầy đủ thật** (component_ref từ golden text,
    driver_reveal_cumulative=3% từ `bible/18#ep_01_reference` có sẵn, cast_count=8 từ
    `bible/31#characters_locked`). ep_02-50 trả về **pending minh bạch** (xem finding #1).
- **D6a** `tools/story_plan_schema_check.py` — đúng 5 check đã khai sẵn trong proposal
  (`enforcer_planned.checks_to_implement_later`), không tự nghĩ thêm/bớt.
- Mở rộng `tools/g6_story_planner_check.py` (v1.0.0→v1.1.0) — thêm 2 stage G6b vào SUITE có
  sẵn (không tạo gate riêng, đúng R211, đúng comment cũ đã tự ghi trước).
- `tests/test_g6b_story_planner.py` — 15 test (M1-M5 mutation + M6 bảo vệ ràng buộc
  "3 entity, cấm act" + reality anchor).

## Finding quan trọng (tự phát hiện khi build, không giấu)

1. **episode_plan/scene chỉ xây được đầy đủ thật cho EP01, KHÔNG phải 50 tập đã mine.**
   `runtime/event_ledger_draft.yaml` (G4 D2) có regret_sub/signature_object/passenger_main/
   stop_location cho ep_02-50, NHƯNG thiếu 2 loại dữ liệu thật cần cho schema:
   - `component_ref` per-scene: chỉ EP01 (golden text) có header `## N. TEN` (HOOK/SETUP/...);
     ep_02-50 dùng `moment_map_template.yaml` với field `moments` còn là **TODO placeholder**
     (đã tự đọc trực tiếp `output/ep_02/moment_map_template.yaml` xác nhận, không suy đoán).
   - `driver_reveal_cumulative` per-episode: `bible/18` chỉ cho sẵn **1 reference duy nhất**
     (EP01 = 3%), không có dữ liệu đếm clue thật cho ep_02-50.
   Bịa 2 field này để "cho đủ 50 tập" sẽ vi phạm R195 — `story_planner.py` trả về `pending`
   với lý do cụ thể cho từng tập, KHÔNG tự tính. Đây là giới hạn THẬT của dữ liệu hiện có,
   không phải tool yếu (mirror cách G6a xử lý `suspense_curve` BLOCKED).
2. **`characters_present` để trống cho EP01 — không map được vào `passenger_roster_100.yaml`.**
   Nhân vật EP01 (Khải-Phong/Hạ-Vy/Cô_gái_ghế_tám...) là dàn nhân vật PILOT riêng
   (`bible/31#characters_locked`), KHÔNG dùng hệ `PAS_id` của roster 100 hành khách procedural
   (dùng từ ep_02 trở đi). Populate PAS_id giả cho EP01 sẽ vi phạm R195 — để trống trung thực.
3. **2 nguồn bible mâu thuẫn về season boundary — đã chọn nguồn LOCKED, ghi rõ để tránh nhầm
   sau này.** `bible/01_series_bible.yaml` (LOCKED, immutable) khai season_1/2/3 = 1-30/31-60/
   61-90; `bible/21b_ep51_90_spec.yaml` lại nói "Season 2 = EP51-90" — nhưng file này tự khai
   `status: PROPOSAL — pending Mr.Long approve` (CHƯA authoritative). Đã dùng `bible/01_series_
   bible` (nguồn LOCKED) làm season boundary chính thức, KHÔNG cố gắng dung hòa với bible/21b
   (khác milestone, cần RFC riêng nếu muốn đồng bộ 2 file).
4. **2 hệ phase-range khác nhau giữa bible/01_series_bible và bible/18 — dùng đúng nguồn field
   yêu cầu.** `bible/01_series_bible.phase_per_ep` (establish=1-10, mystery=11-25...) KHÁC
   `bible/18.budget_curve` (ESTABLISH=ep_1_to_20, MYSTERY=ep_21_to_40...). Field
   `season_plan.driver_phase_refs` yêu cầu tham chiếu đúng `bible/18.budget_curve` (ghi rõ
   trong schema desc) — đã dùng ĐÚNG nguồn đó, không nhầm sang bible/01's phase_per_ep.
5. **Path double-declaration lặp lại đúng bài học G6a — đã rà và fix NGAY trong lượt này**
   (không để pytest bắt rồi mới sửa từng cái): `tools/story_planner.py` +
   `governance/blueprint/schemas/story_plan_schema.yaml` được khai `planned` ở **CẢ BP0**
   (`blueprint_domains.yaml`) **VÀ BP2** (`bp2/domain_specs.yaml` facet `scene_act_structure`
   + invariant enforcer) **VÀ BP7** (`bp7/story_structure.yaml` level `scene`). Đã flip cả 3
   file trong cùng 1 lượt, verify bằng `grep -rn` trước khi chạy pytest.
6. **Entity "act" — xác nhận KHÔNG xuất hiện ở đâu** (bảo vệ đúng ràng buộc đã khóa
   APPROVED_A): `test_m6_schema_file_has_no_act_entity` + `test_m6_story_planner_output_has_
   no_act_key` xác nhận cả file schema lẫn output runtime đều không có entity/key "act" nào.
   `bp7/story_structure.yaml` level `act` giữ nguyên `status: planned` (chủ ý, không flip),
   chỉ cập nhật lý do cho đúng thực tế hiện tại (không còn nói "chờ duyệt format" vì đã duyệt,
   mà nói rõ "Act cố ý không có entity, cần RFC riêng nếu muốn field-hóa sau").

## Field-hóa BP0/BP2/BP7 (domain/facet/level `story_planner`)

- BP0 (`blueprint_domains.yaml`): `manager` (tools/story_planner.py) + `schema`
  (story_plan_schema.yaml) flip planned→exists.
- BP2 (`bp2/domain_specs.yaml`): facet `scene_act_structure.sot` + invariant enforcer
  (Reveal driver ngoài budget) flip planned→exists.
- BP7 (`bp7/story_structure.yaml`): level `scene.sot` flip planned→exists (trỏ đúng
  `schema.scene` key trong file mới); level `act.sot` GIỮ NGUYÊN planned (chủ ý, xem finding #6).

## Bằng chứng self-test

| # | Lệnh | Kết quả | Exit |
|---|---|---|---|
| 1 | `architecture_registry_check.py` | 0/0/0 | 0 |
| 2 | `blueprint_constitution_check.py` (BP0) | 23 domain, 0 vi phạm | 0 |
| 3 | `bp2_domain_check.py` | 13/13 domain, 71 facet (58 exists/13 planned), 0 vi phạm | 0 |
| 4 | `bp7_narrative_check.py` | 6/6 level, 0 vi phạm | 0 |
| 5 | `bp6_decision_check.py` | 12/12 knob, không bị đụng | 0 |
| 6 | `story_plan_schema_check.py` | 1 episode_plan đầy đủ (EP01) + 49 pending minh bạch, 0 vi phạm | 0 |
| 7 | `g6_story_planner_check.py` | 4/4 tầng (G6a+G6b) xanh | 0 |
| 8 | `pytest tests/test_g6b_story_planner.py -v` | 15/15 passed | 0 |
| 9 | `pytest tests/ -q` (full suite) | xem log push CI gate | — |

## DoD G6b

Field-hóa schema đúng nguyên văn APPROVED_A ✅ · story_planner.py đọc đủ 3 nguồn bible +
event ledger + golden EP01 ✅ · KHÔNG bịa entity "act" (test bảo vệ) ✅ · KHÔNG bịa số cho
ep_02-50 (pending minh bạch thay vì fabricate) ✅ · gate wired (mở rộng SUITE có sẵn) ✅ ·
BP0/BP2/BP7 đồng bộ planned→exists ✅ · registry 0/0/0 ✅ · pytest xanh (xem log push).

**READY FOR AUDIT = YES**
