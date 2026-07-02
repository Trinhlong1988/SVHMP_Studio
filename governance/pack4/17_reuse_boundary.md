# PACK 4 — 17_reuse_boundary.md — Reuse Boundary (shared-code vs per-project data)
> Enforce: `tools/detect_template_repetition.py` · chứng thực: `tests/test_pack4_docs.py`.

**Mission:** Vẽ ranh giới cứng giữa **shared-code** (dùng lại mọi project) và **per-project data** (khai theo project) → tái sử dụng an toàn, không rò cấu hình project vào engine.
**Purpose:** Định nghĩa cái gì được share (engine/tool/schema) vs cái gì per-project (config/data/roster), và cấm lẫn.
**Scope:** Ranh giới code↔data. KHÔNG gồm hợp đồng field (15) hay scaffold (16); doc này định biên GIỮA chúng.
**Authority:** Phái sinh registry R211 (source-of-truth per domain) + `constitution/00`.
**Responsibilities:** Enforcer `tools/detect_template_repetition.py` (phát hiện copy-paste per-project lẽ ra phải share) · Certify `tests/test_pack4_docs.py` · giữ engine trung tính project.
**Workflow:** phân loại file (shared vs per-project) → `detect_template_repetition.py` quét trùng lặp → trùng vượt ngưỡng = ứng viên đưa về shared.
**Mandatory Rules:** shared-code CẤM chứa giá trị per-project hard-code; per-project data CẤM chứa logic. Lặp template vượt ngưỡng = vi phạm ranh giới.
**PASS Criteria:** detect_template_repetition dưới ngưỡng + phân loại đúng phía ranh giới.
**FAIL Criteria:** engine hard-code giá trị project, hoặc lặp template vượt ngưỡng → BLOCK.
**Examples:** tên vùng giọng hard-code trong tool → phải chuyển sang `project_config`; 3 project copy cùng scaffold → đưa về shared template.
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Ranh giới (phân phía)
| Phía | Ví dụ | Quy tắc |
|---|---|---|
| shared-code | engine, tools/, schema, template khuôn | trung tính project, KHÔNG hard-code data |
| per-project data | project_config, roster, bible values | KHÔNG chứa logic; nạp vào engine qua config |

## Reconcile
Ghép R211 (file↔domain↔quyền sửa) — doc này chỉ codify NGUYÊN TẮC ranh giới, không map lại từng file. Ngưỡng lặp reconcile `detect_template_repetition.py` (không định nghĩa lại ngưỡng ở prose). `18_template_governance` lo versioning template share, doc này lo phân phía.
