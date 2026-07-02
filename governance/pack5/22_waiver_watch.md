# PACK 5 — 22_waiver_watch.md — Waiver Policy (R204) + QA Watch Daemon
> Enforce: `runtime/qa_waivers.json` (data) + `_is_waived/_load_waivers` trong `tools/svhmp_audio_qa.py` (consumer) + `tools/qa_watch.py` + `tools/qa_watch_supervisor.py` · chứng thực: `tests/test_supervisor_dedup.py` (pytest-func, ENFORCED) + `tests/test_qa_waiver_r204.py` (script-style trong `test_ci_suite.py` SCRIPTS — ENFORCED).

**Mission:** QA không spam lại lỗi ĐÃ PHÁT HIỆN + ĐÃ ĐƯỢC LEAD DUYỆT — và daemon canh QA không bao giờ chết im lặng.
**Purpose:** Codify 2 cơ chế vận hành: (1) waiver explicit R204 chống re-spam violation đã duyệt; (2) watch daemon + supervisor chống vector "qa_watch loop die silent" (sự cố thật 2h45 overnight, 92+ iter VIOLATION không ai bắt).
**Scope:** Vòng đời waiver + vận hành daemon QA. KHÔNG gồm nội dung rule QA (doc 19/21) hay threshold (doc 20).
**Authority:** Waiver CHỈ Mr.Long (LEAD) duyệt — QA/Builder không tự waiver. Phái sinh R204 + R211; doc không tự tạo quyền.
**Responsibilities:**
- `runtime/qa_waivers.json` — danh sách waiver explicit (rule + type + phạm vi), mỗi entry = một lần LEAD duyệt.
- Consumer: `_is_waived` / `_load_waivers` trong `tools/svhmp_audio_qa.py` — violation khớp waiver → không báo lại (đúng vai: `qa_watch.py` KHÔNG tự đọc waiver, nó chạy vòng QA).
- `tools/qa_watch.py` — daemon poll QA; `tools/qa_watch_supervisor.py` — auto-restart khi worker die (5s), **single-instance lock** (`runtime/qa_watch_supervisor.lock`, PID-check, fail-open) + **circuit-breaker** `MAX_RESTARTS_PER_HOUR=12` chống restart-storm (đọc code thật 2/7).
- Certify: `tests/test_supervisor_dedup.py` + `tests/test_qa_waiver_r204.py` (cả hai đang chạy trong ci_gate).
**Workflow:** detector đỏ → Mr.Long xem → nếu chấp nhận (trade-off chủ ý) → thêm entry `qa_waivers.json` (ghi rõ rule/phạm vi) → lần QA sau `_is_waived` lọc, không spam lại; daemon: `qa_watch_supervisor.py` giữ `qa_watch.py` sống, die → restart 5s, quá 12 lần/giờ → trip breaker + VIOLATION.
**Mandatory Rules:** (1) CẤM thêm waiver không có duyệt Mr.Long. (2) Waiver phải CỤ THỂ (rule + type) — CẤM waiver wildcard cả rule-class. (3) Waiver rỗng → không lọc gì (fail-safe, đã test). (4) Supervisor chạy ≤1 instance (lock) — CẤM chạy tay instance thứ hai.
**PASS Criteria:** `test_qa_waiver_r204.py` exit 0 (load ≥2 lớp waiver + waiver rỗng không lọc) · `test_supervisor_dedup.py` xanh · cả hai trong ci_gate (ENFORCED).
**FAIL Criteria:** violation bị ẩn mà không có entry waiver tương ứng = bug nghiêm trọng (che lỗi) · supervisor restart-storm quá breaker → VIOLATION · 2 test trên đỏ → ci_gate đỏ.
**Examples:** click 1 sample tại 3.2s ep01 Mr.Long nghe và chấp nhận → waiver entry `R80.click` phạm vi ep01 → run sau không spam; qa_watch crash vì Ollama VRAM → supervisor restart sau 5s, log WATCHDOG; ai đó mở supervisor thứ hai → lock PID chặn.
*(ROADMAP — CHƯA gate, known-limitation thật deep-audit 2/7 F2: harness end-to-end cho daemon (`tests/test_harness.py`) còn trong ignore vì script-style + phụ thuộc content/daemon flaky — vòng đời daemon CHƯA có gate tự động đầy đủ; hiện chứng thực qua supervisor-dedup + vận hành thật.)*
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Reconcile
Waiver policy ở ĐÂY là source duy nhất — `pack2/10_exception_policy.md` quản exception quy trình governance, doc này quản waiver QA runtime (hai tầng khác nhau, không nhân đôi). Daemon không định nghĩa rule QA — chỉ vận hành.
