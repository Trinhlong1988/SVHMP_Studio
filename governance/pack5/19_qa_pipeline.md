# PACK 5 — 19_qa_pipeline.md — Render-time Content-QA Pipeline
> Enforce: `tools/character_manager.py` (gate G2 TRONG render) · `tools/svhmp_preflight_qa.py` (FULL_TEXT_GATE standalone) · chứng thực: `tests/test_pack5_docs.py` + `tests/test_preflight_repo_path.py`.

**Mission:** Không một dòng nội dung nào tới tai người nghe mà chưa qua chuỗi content-QA: preflight → render-gate → verify.
**Purpose:** Codify pipeline content-QA render-time ĐANG CHẠY THẬT — phân biệt rõ cái gì ENFORCED trong render, cái gì là bước standalone, chống tái diễn "built ≠ wired" (a171120 khai sai).
**Scope:** Content-QA quanh render: (1) preflight `tools/svhmp_preflight_qa.py`, (2) render-gate G2 trong wrapper `tools/render_with_character_gate.py`, (3) verify `tools/svhmp_final_verify.py` + `tools/svhmp_100check_master.py`. KHÔNG gồm code-QA (pytest/ci_gate = `pack3/11_ci_pipeline.md` — reconcile, không nhân đôi) và audio-detector (= `21_detector_suite.md`).
**Authority:** Phái sinh R197 (FULL_TEXT_GATE TỐI THƯỢNG) + R211 registry; doc chỉ codify, không tự tạo quyền. `svhmp_v13_render.py` LOCKED v1.3 — doc chỉ mô tả + trỏ, CẤM sửa.
**Responsibilities:**
- Gate TRONG render (ENFORCED): `character_manager.CharacterRegistry.episode_completeness` + `render_gate_lines` — wire tại `tools/render_with_character_gate.py` (audit G2-6, 2026-07: gate TỪNG chèn thẳng vào `svhmp_v13_render.py` L339/L344 — vi phạm CẤM sửa file LOCKED, đã tách ra wrapper riêng gọi `svhmp_v13_render.py` như subprocess). Mặc định WARN; `--strict-characters` → BLOCK `sys.exit(2)`. Muốn có gate PHẢI gọi qua wrapper, không gọi `svhmp_v13_render.py` trực tiếp.
- `tools/svhmp_preflight_qa.py` = FULL_TEXT_GATE (R86 broad NGA+NANG+HOI + 11 rule text) — STANDALONE: render KHÔNG gọi nó; nó là bước verify-chain riêng, được `svhmp_final_verify.py` gọi per-section.
- Verify sau fix/trước render: `svhmp_final_verify.py` (bug-pattern scan + preflight 6 section) · `svhmp_100check_master.py` (100-check trước render Season 2+).
**Workflow:** spec/episode text → `svhmp_preflight_qa.py <spec.json>` exit 0/1 (1 = block render) → `render_with_character_gate.py` chạy CHARACTER_GATE G2 (WARN / STRICT-BLOCK exit 2) rồi gọi `svhmp_v13_render.py` như subprocess (KHÔNG sửa file LOCKED) → `svhmp_final_verify.py` gọi preflight qua `sys.executable` + path resolve trong repo theo `__file__` (BUG P0 fix 2/7: trước trỏ `C:\tmp` không tồn tại + `python` trần → bước preflight CHẾT im lặng; chứng minh sống lại: chạy thật exit 0).
**Mandatory Rules:** (1) Mọi text modification qua FULL_TEXT_GATE trước render (R197). (2) Render-gate = single-source `character_manager` — CẤM nhân đôi logic gate. (3) Subprocess QA: `sys.executable` + path theo `__file__` — CẤM `'python'` trần, CẤM hard-path `C:\tmp` (khóa bằng `tests/test_preflight_repo_path.py`, có chống pass-rỗng). (4) CẤM sửa `svhmp_v13_render.py` (LOCKED v1.3) — gate/flag mới PHẢI đi qua wrapper riêng (`tests/test_gate_wired_g2.py::test_locked_render_file_has_no_character_gate_code` khóa cứng).
**PASS Criteria:** preflight exit 0 · render không BLOCK · `tests/test_preflight_repo_path.py` 4/4 xanh trong `pytest tests/` + ci_gate (ENFORCED).
**FAIL Criteria:** preflight exit 1 → block render · STRICT gate → render exit 2 · hard-path `C:\tmp\svhmp_preflight_qa` hoặc `'python'` trần tái xuất → test khóa đỏ → ci_gate đỏ.
**Examples:** focal char thiếu Tier1 → G2 STRICT in `[BLOCK]` + exit 2; spec dính R86 NGA cuối câu → preflight exit 1; sửa `svhmp_final_verify.py` về `'python'` trần → `test_no_bare_python_for_preflight_subprocess` FAIL.
*(ROADMAP — CHƯA gate: render tự gọi preflight như stage bắt buộc trong entrypoint — hiện render chỉ có R86 STAGE1 + G2; preflight vẫn do verify-chain gọi. Cùng lớp nợ: `svhmp_100check_master.py` L30 `PIPELINE` còn trỏ `C:\tmp` — ngoài scope fix 2/7, cần task riêng.)*
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Luồng #3 — Orchestrator VNQA/Skeptic (CODIFY G8 D4, 2026-07-09 — chuỗi ĐANG CHẠY THẬT, trước đây governance IM LẶNG)
> **Lỗ hổng đã đóng (G8 D4):** `qa_skeptic_orchestrator.py` = **manager chính thức** của domain `qa_runtime` (blueprint_domains.yaml:613) và chạy thật trong production, NHƯNG trước 9/7 KHÔNG doc pack5 nào ghi nhận (governance blind spot — task doc G8 lesson #14). Đây là verify-chain POST-generation trên episode text, TÁCH khỏi render-gate của 2 luồng trên (không nhân đôi).

**Entry:** `tools/qa_skeptic_orchestrator.py::orchestrate(ep, episode_path)` — chuỗi: **AUTO_FIX → VNQA → (đọc Claude QA) → Skeptic → final verdict**.

**Chuỗi thật (file:line):**
1. **AUTO_FIX** (Phase H4): `vnqa/auto_fix.py --apply` (registry literal map Mr.Long duyệt, atomic ghi + backup) — `qa_skeptic_orchestrator.py:74-90`, timeout 60s.
2. **Tiền đề:** cần `runtime/qa_output_ep_{N}.json` (Claude QA ghi qua `qa_output_writer.py`) — thiếu → abort có recommendation (`:96-102`).
3. **VNQA** library check: `vnqa/pipeline.py` → `runtime/vnqa_ep_{N}.json` (`:108-119`, timeout 120s). **`VietnameseQAChecker.run_all()` chạy H1-H10** (`vnqa/pipeline.py:372-381`):
   - H1 POS-rhythm (adverb>15%, token-repeat, tier-1 AI word) · H2 neologism/compound (skeleton) · H3 collocation (skeleton) · H4 idiom overuse · H5 journalistic-tone · H6 sentence run-on (skeleton PhoNLP) · H7 n-gram repetition · H8 vnsl_lexicon forbidden (verb_misuse/logic_violations→critical/temporal/phonetic) · H9 BigVGAN stop-consonant-tail · H10 duration 15-18p (EP01 grandfathered).
   - VNQA verdict: `critical→FAIL`, `warning≥5 hoặc (warning≥1 || minor≥3)→WARN`, else `PASS` (`:387-398`).
   - ⚠️ **NHÃN NỘI BỘ LỖI THỜI (D1 phát hiện, chưa sửa code — ngoài scope D4):** `phase_h_version` trả `"H1-H7 v1.0"` (`:402`), orchestrator log "H1-H7" (`:114`), docstring pipeline "H1-H8", blueprint "VNQA H1-H9" — TẤT CẢ đếm thiếu; **code thật chạy H1-H10**. Doc này dùng H1-H10.
4. **Skeptic** đối kháng (Ollama local): nếu `qa_verdict==REGEN` → bỏ skeptic, final=REGEN (`:130-141`); ngược lại gọi `adversarial_skeptic.py --provider ollama_local` (`:145-153`, timeout 300s).
5. **Decision tree final_verdict** (`:174-201`): Skeptic `ACCEPT` & 0 critical-missed → **PASS**; `ACCEPT` & có critical-missed → **REVIEW_REQUIRED**; `REJECT` → **REGEN**; `NEEDS_HUMAN`/lỗi skeptic → **REVIEW_REQUIRED**. Tích hợp VNQA: `VNQA FAIL` → escalate **REGEN**; `VNQA WARN` + PASS → chỉ ghi chú (không hạ cấp).

**Output:** `runtime/final_verdict_ep_{N}.json` với `final_verdict ∈ {PASS, REGEN, REVIEW_REQUIRED}` (+ REGEN từ nhánh sớm). 3 format verdict (orchestrator/VNQA/preflight) hiện CHƯA hợp nhất — field-hóa `qa_verdict_schema.yaml` là việc **D5 (chờ Mr.Long duyệt)**, không phải D4.

**Reconcile (chống nhân đôi R211):** luồng #3 = content-QA POST-generation trên text; luồng #1/#2 = gate TRONG/QUANH render; `21_detector_suite.md` = audio-detector SAU render. Ba tầng tách bạch, KHÔNG chồng logic. `qa_post_render.py` (audio, luồng #4/#5) có trùng lặp với `qa_pause_silence`/`qa_boundary_artifact` — thuộc **D3 dedupe** (chờ Mr.Long xác nhận tolerance R96), không phải luồng #3.

## Reconcile
`pack3/11` = code-QA (pytest/ci_gate); doc này = content-QA render-time + POST-generation verify-chain (luồng #3) — các tầng bổ sung. G2 dùng chung `character_manager` với preflight (single-source R210), không có bản sao logic thứ hai.
