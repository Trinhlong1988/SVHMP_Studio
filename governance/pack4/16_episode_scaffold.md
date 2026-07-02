# PACK 4 — 16_episode_scaffold.md — Episode Scaffold + Moment Map
> Enforce: `prompts/ep_scaffold_template.md` (+ `tools/audit_ngan_opening_template.py`) · chứng thực: `tests/test_pack4_docs.py`.

**Mission:** Mọi episode khởi tạo từ MỘT scaffold chuẩn → cấu trúc nhất quán xuyên 100 tập, không dựng tay lệch nhịp.
**Purpose:** Định nghĩa khuôn scaffold episode + template `moment_map` (chuỗi khoảnh khắc) để Generator điền, không phát minh cấu trúc mỗi tập.
**Scope:** Khung episode + moment_map template. KHÔNG gồm nội dung dialog (đó là character/QA gate) hay project-level config (15).
**Authority:** Phái sinh registry R211 + `constitution/00`; scaffold là khuôn, không tạo quyền nội dung.
**Responsibilities:** Enforcer template `prompts/ep_scaffold_template.md` · audit mở đầu `tools/audit_ngan_opening_template.py` (chống opening lặp khuôn) · Certify `tests/test_pack4_docs.py`.
**Workflow:** lấy `ep_scaffold_template.md` → điền moment_map theo beat (từ 15) → audit opening (`audit_ngan_opening_template.py`) → chuyển QA pipeline.
**Mandatory Rules:** opening PHẢI qua `audit_ngan_opening_template.py` (không lặp khuôn mở) — ENFORCED. *(ROADMAP — CHƯA gate: "episode phải bám đủ moment_map" — KHÔNG tool nào check completeness moment_map; enforcer hiện chỉ soi opening.)*
**PASS Criteria:** opening audit exit 0 (ENFORCED). *(ROADMAP: "episode khớp scaffold" chưa có tool kiểm.)*
**FAIL Criteria:** opening trùng khuôn → audit flag (ENFORCED). *(ROADMAP: "thiếu moment bắt buộc → BLOCK" chưa gate.)*
**Examples:** opening 5 tập liền cùng khuôn → `audit_ngan_opening_template.py` flag (ENFORCED). *(ROADMAP: "moment_map thiếu reveal → FAIL" chưa gate.)*
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Moment map template (khung tham chiếu — completeness CHƯA gate)
| # | Moment | Vai trò |
|---|---|---|
| 1 | opening | thiết lập bối cảnh + hook (audit chống lặp khuôn) |
| 2 | rising | dồn nén, giới thiệu focal passenger |
| 3 | reveal | điểm lật / hé lộ (budget theo bible/18) |
| 4 | ending | đóng theo ENDING_RULES_2 (bible/00) |

## Reconcile
KHÔNG nhân đôi `bible/01_narrative_structure` — scaffold TRỎ tới cấu trúc đó. Beat lấy từ `15_project_config` (không định nghĩa lại). Reveal budget reconcile `bible/18` (EP73/EP90 reserved), scaffold không cấp thêm budget.
