# PACK 4 — 17_reuse_boundary.md — Reuse Boundary (shared-code vs per-project data)
> Enforce: `tools/detect_template_repetition.py` · chứng thực: `tests/test_pack4_docs.py`.

**Mission:** Vẽ ranh giới cứng giữa **shared-code** (dùng lại mọi project) và **per-project data** (khai theo project) → tái sử dụng an toàn, không rò cấu hình project vào engine.
**Purpose:** Định nghĩa cái gì được share (engine/tool/schema) vs cái gì per-project (config/data/roster), và cấm lẫn.
**Scope:** Ranh giới code↔data. KHÔNG gồm hợp đồng field (15) hay scaffold (16); doc này định biên GIỮA chúng.
**Authority:** Phái sinh registry R211 (source-of-truth per domain) + `constitution/00`.
**Responsibilities:** Enforcer `tools/detect_template_repetition.py` (phát hiện copy-paste per-project lẽ ra phải share) · Certify `tests/test_pack4_docs.py` · giữ engine trung tính project.
**Workflow:** phân loại file (shared vs per-project) → `detect_template_repetition.py` quét trùng lặp → trùng vượt ngưỡng = ứng viên đưa về shared.
**Mandatory Rules:** lặp TEXT-template across EP vượt ngưỡng = flag `detect_template_repetition.py` (ENFORCED). *(ROADMAP — CHƯA gate: nguyên tắc "shared-code cấm hard-code per-project / per-project data cấm logic" — KHÔNG tool nào dò hard-code trong engine; đây là kỷ luật review, chưa cưỡng chế.)*
**PASS Criteria:** `detect_template_repetition.py` dưới ngưỡng (ENFORCED). *(ROADMAP: "phân loại đúng phía ranh giới" chưa có tool.)*
**FAIL Criteria:** lặp TEXT-template across EP vượt ngưỡng → flag (ENFORCED). *(ROADMAP: "engine hard-code giá trị project → BLOCK" — CHƯA gate; tool chỉ bắt lặp text, không dò hardcode.)*
**Examples:** cùng câu HOOK/REVEAL lặp qua nhiều EP → `detect_template_repetition.py` flag (ENFORCED). *(ROADMAP: "tên vùng giọng hard-code trong tool → chuyển sang project_config" — cần dò hardcode, chưa có tool.)*
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Ranh giới (phân phía)
| Phía | Ví dụ | Quy tắc |
|---|---|---|
| shared-code | engine, tools/, schema, template khuôn | trung tính project, KHÔNG hard-code data |
| per-project data | project_config, roster, bible values | KHÔNG chứa logic; nạp vào engine qua config |

## Reconcile
Ghép R211 (file↔domain↔quyền sửa) — doc này chỉ codify NGUYÊN TẮC ranh giới, không map lại từng file. Ngưỡng lặp reconcile `detect_template_repetition.py` (không định nghĩa lại ngưỡng ở prose). `18_template_governance` lo versioning template share, doc này lo phân phía.
