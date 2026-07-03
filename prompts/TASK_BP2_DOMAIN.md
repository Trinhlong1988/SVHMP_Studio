# TASK BP2 — DOMAIN ARCHITECTURE (theo BP_PIPELINE_MASTER.md, luật chung áp toàn bộ)

## MISSION
Contract CHI TIẾT cho 13 domain tầng thấp (canon 8: world/timeline/location/weather/culture/
belief/ritual/supernatural + character/object/dialogue/event + story_planner) + **SUB-SCOPE
(FACET) INVENTORY bên trong từng domain** — chốt một lần (phán quyết BPC_V2_FINAL_ADJUDICATION:
facet KHÔNG nâng top-level).

## DELIVERABLES
1. `governance/blueprint/bp2/domain_specs.yaml` — mỗi domain: facets[] (facet_id · mô tả 1 dòng ·
   data_type · source_of_truth status:exists|planned) · entities[] · invariants[] (luật bất biến,
   vd "1 passenger có đúng 1 voice profile" — trỏ enforcer thật nếu có).
2. `governance/blueprint/bp2/00_domain_architecture.md` (11-element, mỏng).
3. Validator mở rộng: facet_id duy nhất toàn cục · mọi facet thuộc đúng 1 domain · SoT exists thật.
4. `tests/` negative: facet trùng id 2 domain → FAIL · SoT exists láo → FAIL · domain thiếu facets → FAIL.

## RECONCILE BẮT BUỘC (cấm rebuild — trỏ hệ THẬT, path đã verify 3/7)
character → `bible/37_character_schema.yaml` + `bible/03_character_bible.yaml` +
`runtime/passenger_roster_100.yaml` + `tools/character_manager.py` (exists) ·
object → `bible/12_object_library.yaml` · location → `bible/13_setting_library.yaml` ·
supernatural/belief/ritual → facet tách từ `bible/02_lore_db.yaml` (đọc nó trước, map ra) ·
dialogue → `bible/15_voice_bible.yaml` + `bible/06_lexical_style.yaml` ·
story_planner structure (Scene/Act/Episode/Series/Ending) → `bible/01_narrative_structure.yaml`.
Facet đã có trường trong bible/37 (Relationship/Emotion/Memory/Occupation/Voice...) = exists,
trỏ đúng key; facet chưa có = planned 5-metadata. CẤM bịa facet không phục vụ truyện ma audio.

## MUTATION AUDIT SẼ BẮN (tự test trước)
facet 2 domain · facet_id trùng · SoT giả · domain canon thiếu block · invariant trỏ enforcer ma.
STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.

## BỘ FACET TỐI THIỂU cho CHARACTER (Mr.Long duyệt 3/7 — advisor đề xuất, kiểm duyệt phân xử)
identity · appearance · voice · relationship · memory · emotion · occupation · health · belief ·
inventory · **knowledge** (QUAN TRỌNG NHẤT truyện dài tập: nhân vật KHÔNG được biết bí mật chưa
tiết lộ — nền cho QA gate sau) · location_state (giá trị PHẢI trỏ entity domain location) ·
life_timeline (mốc đời — trỏ entity domain timeline) · speech_style.
RANH GIỚI: speech_style = NẾT NÓI của người, character OWN, dialogue chỉ ĐỌC — KHÁC facet
tone/accent cấp-câu-thoại thuộc domain dialogue (2 tầng, cấm gộp). Facet đã có trường trong
bible/37 = exists trỏ key; chưa có = planned 5-metadata. Domain khác: bộ tối thiểu tự suy
từ bible tương ứng (object: material/origin/curse_state...; supernatural: entity_type/trigger/
rule...), cùng chuẩn.
