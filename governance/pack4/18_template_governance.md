# PACK 4 — 18_template_governance.md — Template Governance (version / validate / promote / anti-repeat)
> Enforce: `tools/vary_templates.py` (+ `tools/detect_template_repetition.py`) · chứng thực: `tests/test_pack4_docs.py`.

**Mission:** Template dùng lại phải được **quản trị vòng đời** (version → validate → promote) và **chống lặp**, để tái sử dụng không sinh ra sản phẩm rập khuôn.
**Purpose:** Định nghĩa quy trình versioning template + cổng validate/promote + cơ chế vary chống lặp khuôn.
**Scope:** Vòng đời template share (scaffold/opening/moment_map). KHÔNG gồm per-project data (15) hay ranh giới code↔data (17).
**Authority:** Independent auditor / LEAD (R1) ký promote template; Builder chỉ ĐỀ XUẤT. Phái sinh `constitution/05_builder_hard_gate`.
**Responsibilities:** Enforcer `tools/vary_templates.py` (biến thể chống lặp) + `tools/detect_template_repetition.py` (đo lặp) · Certify `tests/test_pack4_docs.py` · Builder CẤM tự promote template.
**Workflow:** sửa template → bump version → `detect_template_repetition.py` (dưới ngưỡng?) → `vary_templates.py` (đủ biến thể?) → auditor + LEAD promote.
**Mandatory Rules:** lặp vượt ngưỡng = flag `detect_template_repetition.py` (ENFORCED); promote template theo release gate (14) — Builder KHÔNG tự promote (ENFORCED qua `05_builder_hard_gate` + `auditor.py`). *(ROADMAP — CHƯA gate: "mọi template phải có version / bump version" — KHÔNG tool nào check version.)*
**PASS Criteria:** repetition dưới ngưỡng + `vary_templates.py` sinh biến thể + auditor/LEAD duyệt (ENFORCED). *(ROADMAP: "version bump" chưa có tool kiểm.)*
**FAIL Criteria:** lặp vượt ngưỡng → flag, hoặc Builder tự promote → vi phạm `05` (ENFORCED). *(ROADMAP: "template không version → FAIL" chưa gate.)*
**Examples:** 1 khuôn opening lặp 6 tập → `vary_templates.py` sinh biến thể (ENFORCED). *(ROADMAP: "thêm opening mới không bump version → FAIL" chưa gate.)*
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Vòng đời template (4 bước)
| Bước | Ai | Điều kiện | Trạng thái |
|---|---|---|---|
| Version | Builder | mỗi thay đổi template phải bump version | ROADMAP — chưa tool check |
| Validate | gate máy | `detect_template_repetition.py` dưới ngưỡng + `vary_templates.py` đủ biến thể | ENFORCED |
| Đề xuất | Builder | `READY_FOR_AUDIT=YES` | ENFORCED (`05`) |
| Promote | **Independent** auditor + LEAD | theo release gate `14_release_gate.md` | ENFORCED (`auditor.py`) |

## Reconcile
Ghép `14_release_gate` (promote do auditor+LEAD) + `17_reuse_boundary` (cái gì được share) + `05_builder_hard_gate` (Builder cấm tự promote) — KHÔNG nhân đôi. Ngưỡng lặp reconcile `detect_template_repetition.py`, không định nghĩa lại ở prose.
