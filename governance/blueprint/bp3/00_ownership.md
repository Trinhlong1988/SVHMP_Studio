# BP3 — 00_ownership.md — Ownership + Dependency (ma trận sở hữu facet máy-kiểm-được)
> Enforce: `tools/bp3_ownership_check.py` · chứng thực: `tests/test_bp3_ownership.py` · data: `governance/blueprint/bp3/facet_ownership_matrix.yaml` + `governance/blueprint/bp3/dependency_detail.yaml`.

**Mission:** "Emotion ai own?" trả lời bằng MÁY, không bằng tranh luận — 70 facet, mỗi facet ĐÚNG 1 writer-domain; 52 dependency, mỗi cái có lý do 1 dòng, 3 nguồn khớp tuyệt đối.
**Purpose:** Chặn lớp bug "3 manager cùng sửa" trước khi G2+ code song song, và khóa lý-do-tồn-tại của từng dep để không ai thêm cạnh "tiện tay".
**Scope:** Ownership cho 70 facet BP2 + chi tiết 52 dep BP0. KHÔNG thêm facet/domain mới (inventory ĐÓNG), không runtime flow (BP4).
**Authority:** Phán quyết ngữ nghĩa đã chốt KHÔNG mở lại: Emotion owner=character (dialogue/story_planner/decision_engine read-only) · bible writer duy nhất = mr_long · narration = facet dialogue. Đổi ownership = RFC + Mr.Long.
**Responsibilities:** Matrix SINH MÁY từ BP2+BP0 (cấm lệch tay): `readable_by` = reader grant BP0 của owner · `writable_by` = [mr_long] khi SoT là bible/prompts/tools/governance (catalog/gate bất biến), ngược lại = writer list BP0 của owner (⊆ {owner, mr_long}) · `forbidden_writers` = readable_by (reader grant = READ-ONLY, cấm ghi). Dependency detail: 52/52 cạnh đúng tập BP0, `data_flow: read` toàn bộ — không domain nào GHI domain khác (hệ quả luật 1-writer).
**Workflow:** đổi ownership/dep = RFC sửa BP0/BP2 → chạy lại generator sinh matrix/detail → `bp3_ownership_check.py` exit 0 (coverage 2 chiều + 3-nguồn-khớp) → pytest → commit R200 → audit 7 bước.
**Mandatory Rules:** (1) LUẬT VÀNG: 1 facet = ĐÚNG 1 writer-domain; `writable_by ⊆ {owner, mr_long}`; vượt = FAIL. (2) Matrix phủ ĐÚNG tập 70 facet BP2 — thiếu facet đã khai = FAIL, facet ma = FAIL. (3) `owning_domain` phải khớp domain block BP2 chứa facet. (4) Dep 3-nguồn-khớp exact: `blueprint_domains.dependencies` == `bp1/dependency_graph.depends_on` == `bp3/dependency_detail` — lệch 1 cạnh bất kỳ = FAIL. (5) Mỗi dep có reason 1 dòng; thiếu = FAIL. (6) DUP-KEY loader + version cross-check mọi file BP3.
**PASS Criteria:** `bp3_ownership_check.py` exit 0 (70 facet coverage · 1-writer · 52 dep khớp 3 nguồn) + negative tests xanh trong `pytest tests/` (ENFORCED qua ci_gate).
**FAIL Criteria:** facet 2 writer / facet ma / matrix thiếu facet / writable leo thang / dep lệch bất kỳ nguồn nào → exit 1.
**Examples:** thêm `dialogue` vào `writable_by` của `emotion_trigger` → FAIL "LUAT VANG"; xóa facet `goal` khỏi matrix → FAIL "THIEU facet BP2 da khai"; thêm dep `dialogue→event` chỉ vào detail → FAIL "DEP-3-NGUON lech".
**Promotion Rules:** `bp3_ownership: candidate` — Builder không lock/tag; Mr.Long ký sau audit (reconcile `governance/constitution/00_constitution.md`, không nhân đôi).

## Ghi chú suy dẫn (máy, không tay)
Ví dụ phán quyết mẫu chạy đúng: `emotion_trigger` → owner character, readable [dialogue, event, story_planner, decision_engine, generator, qa_runtime, tts], writable [mr_long] (SoT bible/37 = catalog), forbidden = toàn bộ readable. Facet data runtime (vd `character_state` data sống ở roster tương lai) giữ writable theo writer BP0 của owner — phân tầng schema-bible (mr_long ký) vs data-runtime (owner ghi) sẽ tinh chỉnh ở G2 khi data thật xuất hiện (ghi limitation trong report).
