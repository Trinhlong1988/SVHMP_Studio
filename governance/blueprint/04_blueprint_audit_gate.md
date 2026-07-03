# BLUEPRINT — 04_blueprint_audit_gate.md — Cổng audit của Blueprint Constitution
> Enforce: `tools/blueprint_constitution_check.py` (exit-code là verdict duy nhất) + `tools/cmd_pipeline_gate.py` (coordinator, audit committed ref) · chứng thực: `tests/test_blueprint_constitution.py` trong pytest/ci_gate.

**Mission:** Verdict về Blueprint chỉ đến từ máy chạy thật trên ref sạch — không ai (kể cả Builder viết ra nó) tự phong PASS.
**Purpose:** Định nghĩa trình tự audit bắt buộc + phân định rõ verdict nào áp cho Blueprint (candidate) để không lẫn với RELEASE gate của pack đã lock.
**Scope:** Quy trình audit Blueprint Constitution. KHÔNG thay coordinator 4-CMD (PIPELINE_PROTOCOL) — chỉ nối vào.
**Authority:** Thứ tự audit + tiêu chí do Mr.Long duyệt; auditor độc lập với Builder (nguyên tắc PACK1); lock/tag chỉ Mr.Long ký.
**Responsibilities — 4 lệnh verification bắt buộc (dán lệnh + exit-code + tail):**
```
python tools/architecture_registry_check.py     # 0/0/0
python tools/blueprint_constitution_check.py    # exit 0
pytest -q                                       # all pass (gồm test_blueprint_constitution)
python tools/cmd_pipeline_gate.py --ref origin/main --skip-build
```
**Workflow:** Builder xong → tự chạy 4 lệnh trên → ghi `reports/build_report.md` (`READY FOR AUDIT = YES/NO`) → auditor chạy LẠI trên committed ref qua worktree sạch (CẤM tree bẩn) → PASS → Mr.Long ký lock.
**Mandatory Rules:** (1) Verdict = exit-code của tool, câu chữ "PASS" trong chat KHÔNG phải bằng chứng. (2) Chỉ audit COMMITTED REF (`--ref origin/main` hoặc SHA). (3) Kỳ vọng đúng của gate cho task Blueprint: **ARCH + QA PASS**; RELEASE chấm điều kiện freeze của pack đã lock — KHÔNG áp cho blueprint candidate, RELEASE PASS/FAIL không tính vào verdict task này. (4) Mọi FAIL ở ARCH/QA → quay về Builder, mọi cổng sau = NOT_VERIFIED. (5) Blueprint chỉ được coi hoàn tất thiết kế khi Mr.Long ký — Engineering PASS ≠ hoàn thành (R196 tinh thần).
**PASS Criteria:** registry 0/0/0 + blueprint_constitution_check **v2.0.0** exit 0 (C1–C9: versioning máy-so, 22 domain + RESERVED, L1-CROSS-DEP, drift planned = VIOLATION, archived cấm tham chiếu, layer_groups đúng-1-nhóm, FORMAT facet/event/state-machine) + pytest all pass (negative behavioral: 9 gốc + planned-honesty + L1-cross-dep + archived-dep + version-lệch + facet-2-writer + drift-stub + event-chain-phạm-quyền) + coordinator ARCH✓ QA✓ trên committed ref (ENFORCED).
**FAIL Criteria:** bất kỳ lệnh nào exit ≠ 0 (trừ RELEASE theo Rule 3) → NOT READY; audit trên tree bẩn → kết quả vô hiệu (báo động giả).
**Examples:** Builder sửa contract nhưng quên map file mới → registry UNMAPPED → FAIL tầng ARCH (đã xảy ra thật với test_preflight_repo_path 2/7 — bắt đúng); checker xanh local nhưng chưa push → auditor không có ref để soi → NOT_VERIFIED, phải push trước.
**Promotion Rules:** `blueprint_constitution: candidate` trong registry; Builder CẤM tự lock/tag (checker C1 bắt SELF-LOCK); lock = chữ ký Mr.Long sau khi cổng này xanh — theo `governance/constitution/00_constitution.md`, reconcile KHÔNG nhân đôi.
