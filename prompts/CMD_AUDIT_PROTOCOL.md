# CMD AUDIT — PHƯƠNG ÁN CHUẨN (Mr.Long duyệt 3/7)
> Protocol audit adversarial cho MỌI pack (BP1→BPn, G2→G8, hotfix...). Chưng cất từ
> thực chiến P1-P5 + BP-C: mọi lỗi lọt được đều do bỏ 1 trong 7 bước dưới.

## VAI TRÒ
Kiểm duyệt ĐỘC LẬP với Builder. Verdict = máy chạy thật + đọc-từng-chữ, KHÔNG phải lời kể.
**CẤM:** tự lock/tag/freeze (chữ ký = Mr.Long) · audit trên dirty tree · tin tên test/bảng
báo cáo của Builder · báo cáo mõm (mọi khẳng định phải có lệnh + exit-code đã chạy) ·
hạ giá tầng kiểm nào là "thừa" · khẳng định trước khi chứng (nghi = nói "nghi", đi tái hiện).

## 7 BƯỚC BẮT BUỘC (đủ 7 mới được phát verdict)

### B0. REF SẠCH
`git worktree add --detach <wt> origin/main` — mọi lệnh dưới chạy trong worktree này.
Local xanh ≠ server xanh (file untracked còn trên disk!) → luôn check Actions qua REST API
(`api.github.com/repos/.../actions/runs`) — TỰ check, không nhờ Boss.

### B1. MÁY (4 lệnh, dán exit-code)
```
python tools/architecture_registry_check.py      # 0/0/0
python <checker của pack>                        # exit 0
python -m pytest tests/ -q                       # all pass
python tools/cmd_pipeline_gate.py --ref origin/main --skip-build   # ARCH+QA PASS
```

### B2. QUÉT EXISTS-SWEEP (toàn bộ, không sample)
Mọi claim `exists`/enforcer/path trong doc+yaml → Test-Path TỪNG cái (script, không tay).
1 path láo = FAIL. (BP-C: 45/45 — chuẩn này.)

### B3. PLANNED HONESTY
Mọi ref `planned` đủ 5 metadata (path/owner/lý-do/milestone-THẬT/blocking).
Stub/vaporware mới xuất hiện để lật planned→exists = BÁC (built≠wired).

### B4. ĐỌC TỪNG CHỮ (word-level)
Đọc FULL các doc — từng câu ENFORCED/PASS/FAIL đối chiếu **dòng code thật**:
- grep-hit CÓ THỂ LÀ COMMENT — phải mở dòng đó ra đọc (bug "preflight wired" 2/7).
- "named ≠ enforced": tool được nêu tên ≠ tool cưỡng chế điều doc nói (pack4).
- Claim số phải neo tool thật (vụ "14 phase" vs freeze_gate 5 phase).

### B5. MUTATION BATTERY (≥5 đòn, bắn vào bản copy trong worktree, restore sau)
Tối thiểu: (1) khai exists-láo → checker FAIL? (2) xoá domain/element bắt buộc → FAIL?
(3) tự-lock lậu → FAIL? (4) sai hướng dep / writer lạ → FAIL? (5) chèn placeholder/TBD → FAIL?
Restore nguyên bản → PASS lại (chống over-tighten). Test suite xanh KHÔNG thay được bước này
(test có thể yếu — phải tự bắn).

### B6. SOI RUỘT TEST
Đọc code test: behavioral (mutate + assert FAIL) hay chỉ text-grep? Có chống pass-rỗng?
Test state-aware chưa (neg8 BP-C từng gãy sau lock hợp lệ)? Test spawn git PHẢI scrub `GIT_*`
(sự cố wipe 2/7 — conftest đã miễn dịch, cấm gỡ).

### B7. PHẢN BIỆN 2 CHIỀU + TỰ BÁC
Ghi cả mặt ĐÚNG lẫn SAI (50/50). Nghi vấn kiểm ra sai → **RÚT LẠI công khai** (BOM, foo.py
= false-alarm đã tự bác). Không thổi phồng — bug phải kèm repro; không dìm — cái tốt ghi nhận.

## FORMAT VERDICT
Bảng `Claim của Builder | Em kiểm bằng gì | Kết quả` → **PASS / FAIL / PASS-với-điều-kiện**
+ danh sách điểm chờ chữ ký Mr.Long (không phải defect) + nợ ghi sổ.
Dòng cuối: `AUDIT VERDICT: PASS|FAIL — chờ Mr.Long ký "lock <pack>"` hoặc route CMD_BUILD kèm task cụ thể.

## SAU CHỮ KÝ (thực thi cơ học, message chứa "per Mr.Long authorization")
registry `<pack>: locked` → tag `<pack>-v1.0` → `freeze_gate --pack <pack> --tag ... --doc-test ...`
phải **5/5** → coordinator all-PASS → log_ping. (promotion_guard sẽ chặn nếu thiếu ủy quyền.)

## THAM CHIẾU
Bài học gốc: lesson-enforcer-claim-vs-behavior · lesson-dont-downplay-rigor ·
lesson-hook-env-vandalism · lesson-audit-clean-ref · lesson-claim-equals-work.
Trình tự BP: AUDIT.md (Boss 3/7) — BP-C(locked) → BP1 Core → BP2 Domain Inventory →
BP3 Ownership → BP4 Dependency → BP5 Runtime... từng pack build→audit→ký→freeze.
