# BLUEPRINT — 01_required_documents.md — Bộ tài liệu bắt buộc của SYSTEM_BLUEPRINT v1.0
> Enforce: `tests/test_blueprint_constitution.py` (exist+nonempty + 11-element + no-placeholder + reference-real-enforcer cho cả 5 doc) · nguồn dữ liệu: `governance/blueprint/blueprint_domains.yaml`.

**Mission:** Mọi phần của Blueprint Constitution đều có tài liệu chuẩn hóa, không doc mồ côi, không doc thiếu chuẩn.
**Purpose:** Khóa danh mục deliverable: cái gì PHẢI tồn tại để Blueprint Constitution được coi là đủ, và bar chất lượng từng file.
**Scope:** Bộ file trong `governance/blueprint/` + tool + test đi kèm. KHÔNG quản nội dung domain (doc 02) hay luật phụ thuộc (doc 03).
**Authority:** Danh mục này chỉ Mr.Long được thêm/bớt; Builder muốn thêm doc mới phải qua Change Request Gate (R211).
**Responsibilities — danh mục bắt buộc:**
| File | Vai trò | Kiểm bởi |
|---|---|---|
| `00_system_blueprint_constitution.md` | hiến pháp tổng | doc-bar test |
| `01_required_documents.md` | danh mục deliverable (file này) | doc-bar test |
| `02_domain_contract.md` | chuẩn 12-field hợp đồng domain | doc-bar test |
| `03_dependency_rules.md` | luật layer + hướng phụ thuộc | doc-bar test |
| `04_blueprint_audit_gate.md` | cổng audit blueprint | doc-bar test |
| `blueprint_domains.yaml` | source-of-truth machine-readable | `blueprint_constitution_check.py` |
| `tools/blueprint_constitution_check.py` | enforcer C1–C8 | `tests/test_blueprint_constitution.py` |
| `tests/test_blueprint_constitution.py` | certify (9 negative + doc bar) | pytest/ci_gate |
**Workflow:** thêm/sửa doc → tự kiểm doc-bar (11-element + 0 placeholder + trỏ enforcer thật) → pytest → commit R200 → audit.

## Danh mục phase BP (~20 doc, roadmap 9 pack — bảng E Mr.Long ký 3/7)
| Pack | Nội dung | Doc dự kiến |
|---|---|---|
| BP0 | Blueprint Constitution (bộ này) — amendment v2 rồi Mr.Long lock | 5 doc + contract + checker + test |
| BP1 | Core Architecture | 5 doc (system_blueprint/domain_catalog/dependency_rules/runtime_boundary/glossary) |
| BP2 | Domain Architecture (canon + character + object + dialogue + event) | ~5 doc |
| BP3 | Ownership + Dependency (facet matrix: 1 facet = 1 writer, machine-checkable) | ~2 doc + data |
| BP4 | Runtime + Event (flow, state machine, event bus, memory mở rộng) | ~3 doc + data |
| BP5 | Validation (checker suite + review flow) | ~2 doc |
| BP6 | Decision Architecture (decision_engine: ratio/curve/budget + calibrate R195) | ~2 doc |
| BP7 | Narrative Architecture (story structure Scene→Series, pacing format, cultural spec) | ~2 doc |
| BP8 | Production Architecture (render chain, golden output R196, video/publisher gates) | ~2 doc |
Mỗi pack: BUILD → self-test → audit adversarial → Mr.Long ký lock → pack sau. Tier-2 Engines để SAU SYSTEM_BLUEPRINT v1.0 lock.
**Mandatory Rules:** (1) Mỗi doc đủ 11 element: Mission/Purpose/Scope/Authority/Responsibilities/Workflow/Mandatory/PASS/FAIL/Promotion/Examples. (2) 0 placeholder marker. (3) Mỗi doc trỏ ≥1 enforcer THẬT tồn tại trên disk. (4) File mới map `governance/file_index.yaml` + registry ngay (0/0/0).
**PASS Criteria:** cả 5 doc + yaml + tool + test tồn tại, non-empty, qua đủ 4 lớp doc-bar test trong `pytest tests/` (ENFORCED).
**FAIL Criteria:** thiếu file / doc rỗng / thiếu element / dính placeholder / trỏ enforcer không tồn tại → test đỏ → ci_gate đỏ.
**Examples:** xóa `03_dependency_rules.md` → `test_blueprint_docs_exist_nonempty` FAIL; doc 02 quên mục Promotion → `test_blueprint_docs_have_11_elements` FAIL; doc trỏ tool chưa có trên disk → `test_blueprint_docs_reference_real_enforcers` FAIL.
**Promotion Rules:** theo `governance/constitution/00_constitution.md` — candidate cho tới khi Mr.Long ký; reconcile, KHÔNG nhân đôi.
