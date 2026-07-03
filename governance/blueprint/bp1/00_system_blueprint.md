# BP1 — 00_system_blueprint.md — Bản đồ toàn cảnh SVHMP_Studio (Core Architecture)
> Enforce: `tools/bp1_architecture_check.py` (11 check + equality BP0; mutation M1-M10 tại `tests/test_bp1_architecture.py`) · nguồn luật: Blueprint Constitution **v2.0 LOCKED** (`governance/blueprint/blueprint_domains.yaml`, tag `blueprint-constitution-v2.0`).

**Mission:** Một bản đồ duy nhất của toàn Studio — 22 domain + quest RESERVED trên layer số 1-12 + 4 nhãn nhóm ĐÃ LOCK, mọi cạnh phụ thuộc/quyền đọc/quyền ghi máy-kiểm-được, để từ G2 trở đi không module nào mọc ngoài bản vẽ.
**Purpose:** BP1 chỉ trả lời "CÁI GÌ đứng ở ĐÂU, được nói chuyện với AI, qua HỢP ĐỒNG nào" — không đặc tả nội bộ domain (BP2), không ownership sâu từng facet (BP3), không runtime flow chi tiết (BP4).
**Scope:** 3 artifact máy-đọc tại `governance/blueprint/bp1/`: `dependency_graph.yaml` (SINH MÁY từ BP0 — 23 domain, layer số 1-12 + layer_groups copy nguyên vẹn) · `interface_contracts.yaml` (SINH MÁY — 92 contract từ reader/writer edges, PLANNED HONESTY: 4 exists có bằng chứng code / 88 planned đủ 5 metadata) · `layer_contracts.yaml` (4 nhãn nhóm). KHÔNG runtime app code, KHÔNG stub domain, KHÔNG content production (hard rules).
**Authority:** Domain Inventory ĐÓNG theo BP0 v2.0 — thêm/sửa/xóa domain = RFC + chữ ký Mr.Long. Layer model = số 1-12 + 4 nhãn LOCKED — đổi = RFC BP0 (CẤM scheme mới kiểu L0..L4). Mâu thuẫn BP0 phát hiện khi build → STOP, report FAIL, không sửa BP0.

## Quyết định thiết kế có chủ đích (thay doc bằng máy-kiểm-được)
- **`01_domain_catalog` + `04_blueprint_glossary` KHÔNG viết dạng prose** — catalog = chính `dependency_graph.yaml` (danh mục 23 domain + layer + cạnh, máy so với BP0 mỗi lần chạy); glossary = các trường định nghĩa NGAY trong 3 YAML + BP0 contract (một nguồn, không bản sao prose để lệch). Doc prose chỉ giữ file này (bản đồ + luật đọc).
- **`facet_ownership_matrix` CHUYỂN pack BP3** (roadmap đã ký — cần facet inventory từ BP2 trước). FORMAT khai sẵn tại đây để BP3 điền DATA:
  `facets[] = {facet_id · owning_domain (ĐÚNG 1) · readable_by[] · writable_by[] ⊆ {owner, mr_long} · forbidden_writers[] · lifecycle · owner_artifact}` — khớp `formats.facet` trong BP0 (1 facet = 1 writer).

## Bản đồ 4 nhóm trên layer số (Responsibilities)
```
narrative (L1-L5)     8 canon (deps RỖNG, reader-only ngang) → character · object (L2)
                      → dialogue · event (L3) → story_planner · quest≋RESERVED (L4)
                      → decision_engine (L5 — budget sheet, chống generator tự nghĩ)
runtime               generator (L6) → qa_runtime (L7, ĐỘC LẬP generator) · production (L10)
presentation          tts (L8) → audio (L9) → video (L11)
business              publisher (L12) · analytics (L12; feedback → story_planner QUA Mr.Long)
```
**Workflow:** đổi kiến trúc = RFC sửa BP0 → chạy lại generator (scratchpad) sinh graph/contracts → `bp1_architecture_check.py` exit 0 (equality BP0 — sửa tay lệch là đỏ) → `pytest` (M1-M10) → commit R200 (pull --rebase trước, log_ping + push sau, CẤM --no-verify) → audit 7 bước.
**Mandatory Rules:** (1) `depends_on` graph == `dependencies` BP0 từng domain (máy so — drift FAIL). (2) `layers` + `layer_groups` graph == BP0 nguyên vẹn. (3) `interface_contracts` phủ ĐÚNG tập reader-edge BP0 (2 chiều: không thiếu, không thừa). (4) Interface `status: exists` CHỈ khi có bằng chứng code wire thật (hiện 4/92: character→tts qua `svhmp_v13_render.py` G2 L339; character→qa_runtime qua `svhmp_preflight_qa.py --strict-characters`; 2 write-store roster + qa_waivers); còn lại `planned` đủ 5 metadata. (5) Không domain lạ; không tham chiếu archived; DUP-KEY loader mọi file BP1. (6) `source_constitution_version` == `contract_version` BP0 (máy so).
**PASS Criteria:** `bp1_architecture_check.py` exit 0 + mutation M1-M10 FAIL đúng chỗ trong `pytest tests/` (ENFORCED qua ci_gate).
**FAIL Criteria:** bất kỳ check đỏ → BP1 vô hiệu; mâu thuẫn BP0 → STOP + report FAIL (hard rule 5).
**Examples:** thêm domain `music` vào graph không RFC → `DOMAIN-LA` FAIL; sửa tay `character.depends_on` += `dialogue` → `LECH-BP0` FAIL; đổi layer model về L0..L4 → `LAYER-SCHEME` FAIL; khai contract `status: exists` với source_artifact không tồn tại → FAIL.
**Promotion Rules:** BP1 = `candidate`; Builder không lock/tag — Mr.Long ký sau audit (theo `governance/constitution/00_constitution.md`, reconcile không nhân đôi).

## Ghi chú semantics
`reads_from` (reader grant) ĐƯỢC ngược tầng có kiểm soát (analytics→story_planner feedback qua Mr.Long); `depends_on` CHỈ xuôi layer-số strictly + thỏa ràng buộc nhóm (`layer_contracts.yaml`). `writes_to` chỉ nhận store `runtime/*` (bible/prompts/governance = lãnh địa Mr.Long/doc — writer-semantics lỏng ở vài domain BP0 được ghi OBSERVATION trong `reports/BP1_CORE_ARCHITECTURE_REPORT.md`, KHÔNG sửa BP0).
