# PACK 5 — 19_qa_pipeline.md — Render-time Content-QA Pipeline
> Enforce: `tools/character_manager.py` (gate G2 TRONG render) · `tools/svhmp_preflight_qa.py` (FULL_TEXT_GATE standalone) · chứng thực: `tests/test_pack5_docs.py` + `tests/test_preflight_repo_path.py`.

**Mission:** Không một dòng nội dung nào tới tai người nghe mà chưa qua chuỗi content-QA: preflight → render-gate → verify.
**Purpose:** Codify pipeline content-QA render-time ĐANG CHẠY THẬT — phân biệt rõ cái gì ENFORCED trong render, cái gì là bước standalone, chống tái diễn "built ≠ wired" (a171120 khai sai).
**Scope:** Content-QA quanh render: (1) preflight `tools/svhmp_preflight_qa.py`, (2) render-gate G2 trong `svhmp_v13_render.py`, (3) verify `tools/svhmp_final_verify.py` + `tools/svhmp_100check_master.py`. KHÔNG gồm code-QA (pytest/ci_gate = `pack3/11_ci_pipeline.md` — reconcile, không nhân đôi) và audio-detector (= `21_detector_suite.md`).
**Authority:** Phái sinh R197 (FULL_TEXT_GATE TỐI THƯỢNG) + R211 registry; doc chỉ codify, không tự tạo quyền. `svhmp_v13_render.py` LOCKED v1.3 — doc chỉ mô tả + trỏ, CẤM sửa.
**Responsibilities:**
- Gate TRONG render (ENFORCED): `character_manager.CharacterRegistry.episode_completeness` + `render_gate_lines` — wire tại `svhmp_v13_render.py` L339/L344 (kiểm duyệt đọc code 2/7). Mặc định WARN; `--strict-characters` → BLOCK `sys.exit(2)`.
- `tools/svhmp_preflight_qa.py` = FULL_TEXT_GATE (R86 broad NGA+NANG+HOI + 11 rule text) — STANDALONE: render KHÔNG gọi nó (chỉ 2 comment L331/L334); nó là bước verify-chain riêng, được `svhmp_final_verify.py` gọi per-section.
- Verify sau fix/trước render: `svhmp_final_verify.py` (bug-pattern scan + preflight 6 section) · `svhmp_100check_master.py` (100-check trước render Season 2+).
**Workflow:** spec/episode text → `svhmp_preflight_qa.py <spec.json>` exit 0/1 (1 = block render) → render `svhmp_v13_render.py` tự chạy CHARACTER_GATE G2 (WARN / STRICT-BLOCK exit 2) → `svhmp_final_verify.py` gọi preflight qua `sys.executable` + path resolve trong repo theo `__file__` (BUG P0 fix 2/7: trước trỏ `C:\tmp` không tồn tại + `python` trần → bước preflight CHẾT im lặng; chứng minh sống lại: chạy thật exit 0).
**Mandatory Rules:** (1) Mọi text modification qua FULL_TEXT_GATE trước render (R197). (2) Render-gate = single-source `character_manager` — CẤM nhân đôi logic gate. (3) Subprocess QA: `sys.executable` + path theo `__file__` — CẤM `'python'` trần, CẤM hard-path `C:\tmp` (khóa bằng `tests/test_preflight_repo_path.py`, có chống pass-rỗng). (4) CẤM sửa `svhmp_v13_render.py` (LOCKED v1.3).
**PASS Criteria:** preflight exit 0 · render không BLOCK · `tests/test_preflight_repo_path.py` 4/4 xanh trong `pytest tests/` + ci_gate (ENFORCED).
**FAIL Criteria:** preflight exit 1 → block render · STRICT gate → render exit 2 · hard-path `C:\tmp\svhmp_preflight_qa` hoặc `'python'` trần tái xuất → test khóa đỏ → ci_gate đỏ.
**Examples:** focal char thiếu Tier1 → G2 STRICT in `[BLOCK]` + exit 2; spec dính R86 NGA cuối câu → preflight exit 1; sửa `svhmp_final_verify.py` về `'python'` trần → `test_no_bare_python_for_preflight_subprocess` FAIL.
*(ROADMAP — CHƯA gate: render tự gọi preflight như stage bắt buộc trong entrypoint — hiện render chỉ có R86 STAGE1 + G2; preflight vẫn do verify-chain gọi. Cùng lớp nợ: `svhmp_100check_master.py` L30 `PIPELINE` còn trỏ `C:\tmp` — ngoài scope fix 2/7, cần task riêng.)*
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Reconcile
`pack3/11` = code-QA (pytest/ci_gate); doc này = content-QA render-time — hai tầng bổ sung. G2 dùng chung `character_manager` với preflight (single-source R210), không có bản sao logic thứ hai.
