# PACK 4 — 15_project_config.md — Project Config Contract
> Enforce: `tools/validate_project_config.py` · chứng thực: `tests/test_pack4_docs.py`.

**Mission:** Cho phép **same code, khác project** — mọi khác biệt thể loại/thị trường được nạp từ `project_config`, KHÔNG hard-code trong engine.
**Purpose:** Định nghĩa hợp đồng field bắt buộc của `project_config` để một project mới chỉ cần khai config, không sửa shared-code.
**Scope:** Per-project data contract (genre / distribution / dialect / beat / taxonomy). KHÔNG gồm shared engine logic (đó là `17_reuse_boundary.md`).
**Authority:** Phái sinh từ registry R211 + `constitution/00`; doc không tự tạo quyền, chỉ codify hợp đồng.
**Responsibilities:** Enforcer `tools/validate_project_config.py` (kiểm 5 field bắt buộc, exit 0/1) · Certify `tests/test_pack4_docs.py` · project_config = per-project data, KHÔNG phải source-of-truth engine.
**Workflow:** khai `project_config.yaml` → `validate_project_config.py` (đủ + non-empty + đúng kiểu field?) → exit 0/1. *(ROADMAP — CHƯA gate: bước "engine đọc config → render theo project"; hiện KHÔNG code nào đọc `project_config` — validator chỉ kiểm hợp đồng field, không tiêu thụ config.)*
**Mandatory Rules:** 5 field bắt buộc (bảng dưới) phải hiện diện **+ non-empty + đúng kiểu**; thiếu/rỗng/sai-kiểu 1 field = INVALID (exit 1). *(Nguyên tắc "cấm engine hard-code" thuộc `17_reuse_boundary` — CHƯA có tool cưỡng chế, xem doc 17.)*
**PASS Criteria:** mọi `project_config.yaml` đủ 5 field non-empty + đúng kiểu → `validate_project_config.py` exit 0 (ENFORCED).
**FAIL Criteria:** thiếu / rỗng / sai kiểu 1 field → validator exit 1 (ENFORCED).
**Examples:** config đủ 5 field non-empty (genre=horror, dialect=south…) → validator exit 0; `genre:''`/`beat:[]`/`taxonomy:{}` → exit 1. *(ROADMAP — CHƯA gate: "đổi genre → khác output" cần engine đọc config, chưa wire.)*
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Field contract (5 bắt buộc)
| Field | Ý nghĩa | Ví dụ |
|---|---|---|
| genre | thể loại truyện | horror / romance |
| distribution | phân bổ mục tiêu xuyên tập | age/region/death targets |
| dialect | vùng giọng chủ đạo | south / north / central |
| beat | khung nhịp episode | opening→rising→reveal→ending |
| taxonomy | phân loại object/setting/regret | OBJ_ / setting_ / regret archetypes |

## Reconcile
KHÔNG nhân đôi bible (11 regret / 12 object / 13 setting) — `taxonomy` chỉ TRỎ tới các bible đó cho từng project. `distribution` reconcile target R210 (age/region/death balance), không định nghĩa lại. Validator chỉ kiểm hiện diện + kiểu field, KHÔNG phán nội dung (đó là QA gate).
