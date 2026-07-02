# SVHMP — 4-CMD GATED PIPELINE PROTOCOL v1.0

Nguồn: `CMD_QA_AUDIT_CONSTITUTION_v1.0` + deep-audit 2/7. **Máy-thẩm-quyền, tuần tự, không chồng chéo.**

```
Mr.Long → giao TASK/PACK
   → CMD_BUILD        (xây; kết luận: READY FOR AUDIT = YES/NO)
   → CMD_ARCH_AUDIT   (kiến trúc/registry)
   → CMD_QA_AUDIT     (chất lượng/ci_gate)
   → CMD_RELEASE_AUDIT(điều kiện freeze)
   → OVERALL (auditor.py) → Mr.Long ký FREEZE
FAIL bất kỳ cổng → về CMD_BUILD (mọi cổng sau = NOT_VERIFIED).
```

## Nguyên tắc bất di (đọc kỹ — vi phạm = pipeline vô hiệu)
1. **Không CMD nào tự khai PASS.** Verdict cuối chỉ do `tools/cmd_pipeline_gate.py` tính (chạy tool thật, đọc exit-code). Chat KHÔNG được coi câu chữ "STATUS: PASS" là bằng chứng.
2. **Chỉ audit COMMITTED REF sạch** (`--ref origin/main` hoặc SHA), qua worktree biệt lập. **CẤM** đọc/kết luận từ working-tree bẩn (kết quả chớp-chớp = báo động giả).
3. **Không chồng chéo:** 1 lúc 1 CMD. Coordinator có lock `runtime/cmd_pipeline.lock`.
4. **Kết quả 100%:** chỉ `READY_FOR_OWNER_FREEZE` khi BUILD ready + ARCH+QA+RELEASE+OVERALL đều PASS. Thiếu tool → `NOT_VERIFIED` (exit 2). Mặc định nghi ngờ.
5. **Mỗi CMD phải TỰ KIỂM THỬ + CHỨNG MINH** trước khi finish (xem "Self-test bắt buộc").
6. **Controller = CMD kiểm duyệt** (điều phối 4 CMD qua coordinator).

## Giao thức giao tiếp (communication protocol)
- **File trạng thái máy:** `reports/cmd_pipeline_gate_report.{md,json}` (do coordinator ghi; runtime, gitignore).
- **File Builder ký:** `reports/build_report.md` — dòng bắt buộc: `READY FOR AUDIT = YES` (hoặc `= NO`).
- **Dòng STATUS cuối của mỗi chat** (chỉ để người đọc — KHÔNG phải verdict máy):
  - CMD_BUILD: `STATUS: READY_FOR_AUDIT` | `STATUS: NOT_READY`
  - CMD_ARCH/QA_AUDIT: `STATUS: PASS` | `FAIL` | `NOT_VERIFIED`
  - CMD_RELEASE_AUDIT: `STATUS: READY_TO_FREEZE` | `NOT_READY` | `NOT_VERIFIED`
- **Chuyển bước:** chỉ khi coordinator in `ACTION_ROUTE` sang CMD kế thì mới mở CMD đó.

## Self-test bắt buộc (mỗi CMD, trước khi báo xong)
Mỗi CMD PHẢI chạy và dán bằng chứng (lệnh + exit-code + tail output):
```
python tools/cmd_pipeline_gate.py --ref origin/main
```
CMD chỉ được kết luận dựa trên FINAL của coordinator, không tự phong.

## RÚT KINH NGHIỆM — CẤM LẶP LẠI (lessons deep-audit 2/7)
1. **Claim = việc.** Nhãn commit/PING/DoD phải khớp diff. "built" ≠ "wired" (grep điểm thực thi). "no logic change" phải AST-equal. "freeze" phải `freeze_gate.py` exit 0.
2. **Audit ref sạch**, không tree bẩn (MISSING/UNMAPPED chớp = giả).
3. **File mới → map `governance/file_index.yaml`** (registry 0/0/0) ngay.
4. **Test phải được collect:** pytest-func KHÔNG đặt tên dính ignore-glob; script-style phải vào `test_ci_suite.py` SCRIPTS + `conftest` list. Guard: `test_no_orphan_tests.py`.
5. **EOL/format defect → đếm byte của BLOB** (`git show <sha>:<file>` → đếm `\r`/`\n`), KHÔNG tin PowerShell pipeline (tự chèn CR = báo động giả).
6. **Shared-index:** commit qua **worktree riêng**; `pull --rebase` trước; `log_ping` + commit + push sau (R200). **Không `--no-verify`.**
7. **Không tự-PASS** (Builder lẫn Auditor). Coordinator là trọng tài máy.
