# BP7 — 00_narrative.md — Narrative Architecture (story_planner cấu trúc + Cultural spec)
> Enforce: `tools/bp7_narrative_check.py` · chứng thực: `tests/test_bp7_narrative.py` · data: `governance/blueprint/bp7/story_structure.yaml` + `governance/blueprint/bp7/cultural_spec.yaml` + `governance/blueprint/bp7/pacing_format.yaml`.

**Mission:** Kiến trúc truyện: cấu trúc Scene→Act→Episode→Season→Series→Ending (STRUCTURE trong story_planner — phán quyết đã đóng ở BP2, KHÔNG nâng domain) + spec Cultural (culture/belief/ritual) + FORMAT đường cong pacing theo cấp cấu trúc.

**Purpose:** Khóa "truyện cấu trúc thế nào" trước G-phase: episode PHẢI đủ 6 section đúng thứ tự (khớp bible/01 nhịp câu đã khóa), phong tục/tín ngưỡng/nghi thức KHÔNG được bịa (mọi item trỏ facet BP2 đã khai, phần lớn còn planned — chờ Mr.Long duyệt taxonomy), pacing curve chỉ định HÌNH THỨC (số/knob thuộc BP6, KHÔNG hardcode).

**Scope:** `story_structure`: 6 cấp cấu trúc + component bắt buộc cấp Episode. `cultural_spec`: 7 facet culture/belief/ritual (đã đọc bible/02_lore_db.yaml xác nhận 0 nội dung — giữ planned, KHÔNG bịa). `pacing_format`: áp dụng 5 curve BP6 theo cấp scene/episode/series, KHÔNG số cụ thể. KHÔNG viết engine story_planner.py (tier-2, planned M2), KHÔNG sửa render LOCKED.

**Authority:** BP0 v2.0 + BP1-BP6 LOCKED/candidate = nguồn luật. Phán quyết: facet ≠ domain (BPC_V2_FINAL_ADJUDICATION) — BP7 KHÔNG nâng story_planner/culture/belief/ritual thành domain mới, chỉ field-hoá kiến trúc chi tiết hơn (mirror cách BP6 làm với decision_engine: BP2 sot facet liên quan vẫn `planned`, BP6/BP7 là tầng kiến trúc bổ sung song song). Đổi cấp cấu trúc/facet = RFC + Mr.Long.

**Responsibilities:** `story_structure`: level_id/parent/components_required/sot cho 6 cấp; Episode component list PHẢI == đúng thứ tự `bible/01_narrative_structure.yaml#bimodal_sentence_length_per_section.pattern_per_section` (TRỎ không chép — lệch bible = FAIL); Ending trỏ `bible/00_constitution.yaml#ENDING_RULES`. `cultural_spec`: 7 item (xung_ho_convention/le_gio_custom/kieng_ky_daily/tin_nguong_he/am_duong_quan_niem/nghi_thuc_catalog/ritual_steps), mỗi item domain_facet PHẢI resolve thật trong `bp2/domain_specs.yaml`; lore_classification ghi rõ bằng chứng đã đọc `bible/02_lore_db.yaml` (0 nội dung culture → giữ planned, không bịa). `pacing_format`: 5 curve_ref trỏ đúng knob_id trong `bp6/decision_contract.yaml`, level áp dụng (scene/episode/series) + đơn vị mẫu — KHÔNG chứa số.

**Workflow:** sửa data → `bp7_narrative_check.py` exit 0 → pytest mutation → commit R200 → audit 7 bước → Mr.Long ký.

**Mandatory Rules:** (1) Component Episode PHẢI khớp CHÍNH XÁC 6 khóa bible/01 (thiếu/thừa/sai thứ tự = FAIL). (2) Cultural item facet_id phải tồn tại thật trong bp2/domain_specs.yaml đúng domain khai (facet ma = FAIL). (3) pacing_format KHÔNG chứa số (int/float) bất kỳ đâu — numeric-leak scan toàn file (mirror bài học BP6 audit 4/7: scan phải toàn file, không chỉ 1 phần). (4) curve_ref PHẢI khớp đúng knob_id đã khai trong bp6/decision_contract.yaml (curve ma = FAIL). (5) DUP-KEY loader single-impl (import blueprint_constitution_check) + version khớp 3 file bp7.

**PASS Criteria:** `bp7_narrative_check.py` exit 0 + mutation battery xanh trong `pytest tests/` (ENFORCED qua ci_gate pytest_suite).

**FAIL Criteria:** xoá REVEAL khỏi components / cultural item trỏ facet ma / pacing_format nhét số (vd fear_curve=0.8) / structure mâu thuẫn bible/01 → exit 1.

**Examples:** xoá `REVEAL` khỏi episode.components_required → FAIL COMPONENT-THIEU; cultural item `domain_facet: culture.gio_le_ma` (facet không tồn tại) → FAIL FACET-MA; pacing_format thêm `default_fear: 0.8` → FAIL R195-HARDCODE; đổi thứ tự thành `[SETUP, HOOK, ...]` → FAIL THU-TU-SAI (lệch bible/01).

**Promotion Rules:** `bp7_narrative: candidate` — Builder không lock/tag; Mr.Long ký sau audit (reconcile `governance/constitution/00_constitution.md`). REALITY ANCHOR (luật 9): checker chạy trên data bp7 THẬT + số đo trong `reports/BP7_REPORT.md`.

## Ghi chú semantics (kiểm duyệt phán khi audit)
Level `act` không có component/facet riêng field-hoá (BP2 story_planner.entities chỉ có `[season_plan, episode_plan, scene]`, không có "act") — TASK_BP7 chỉ định Act nằm trong chuỗi cấp cấu trúc để mô tả nhịp nhóm-scene, KHÔNG bịa thêm rule/component cho Act khi chưa có căn cứ bible. Nếu kiểm duyệt thấy cần field-hoá Act riêng, đó là RFC mới (thêm entity vào BP2 — facet list đã đóng, cần Mr.Long duyệt), không phải lỗi thiếu sót của BP7 candidate này.
