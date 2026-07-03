# TASK BP7 — NARRATIVE ARCHITECTURE (theo BP_PIPELINE_MASTER.md)

## MISSION
Kiến trúc truyện: cấu trúc Scene→Act→Episode→Season→Series→Ending (STRUCTURE trong
story_planner — phán quyết đã đóng, KHÔNG nâng domain) + spec Cultural (culture/belief/ritual).

## DELIVERABLES
1. `governance/blueprint/bp7/story_structure.yaml` — cấp cấu trúc: level_id · parent ·
   components bắt buộc (episode: HOOK/SETUP/INCIDENT/REVEAL/PAYOFF/CLIFFHANGER — RECONCILE
   `bible/01_narrative_structure.yaml` exists, TRỎ không chép; lệch bible = FAIL) ·
   ending rules trỏ ENDING_RULES (bible/00_constitution.yaml).
2. `governance/blueprint/bp7/cultural_spec.yaml` — facet data cho culture/belief/ritual
   (phong tục/giỗ/đình/miếu/Thành Hoàng/Phật giáo/Đạo Mẫu...): item · domain-facet (khớp BP2) ·
   source_of_truth (map từ `bible/02_lore_db.yaml` exists — đọc lore_db TRƯỚC, phân loại ra;
   mục lore chưa có = planned) · usage_rule 1 dòng.
3. `governance/blueprint/bp7/pacing_format.yaml` — FORMAT đường cong theo cấu trúc
   (curve áp trên scene/episode/series level nào; đơn vị; sample-rate) — knob & số thuộc BP6/G6,
   file này chỉ định HÌNH.
4. `governance/blueprint/bp7/00_narrative.md` (11-element).
5. Validator: structure khớp bible/01 · cultural item khớp facet BP2 · pacing format
   không chứa số hardcode · mọi SoT exists thật.
6. Negative test: thiếu component episode · cultural item trỏ facet ma · curve có số cứng ·
   structure mâu thuẫn bible/01.

## MUTATION AUDIT SẼ BẮN
xoá REVEAL khỏi components → FAIL · cultural item facet ma → FAIL · nhét fear_curve=0.8 → FAIL.
STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.
