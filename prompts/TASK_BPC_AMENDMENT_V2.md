# LỆNH: BP-C AMENDMENT v2 — Mr.Long ĐÃ KÝ BẢNG E (3/7/2026)

CMD_BUILD chạy **A1-A8** đúng theo `reports/BP_PHASE_PLAN_PROPOSAL.md` (mục B bảng phân tầng
+ mục C roadmap 9 pack + mục D scope) — tất cả 5 mục bảng E đã được ký.

## + 2 ĐIỀU KIỆN CỦA KIỂM DUYỆT (gắn vào A1, bắt buộc)
1. **Canon L1 đồng-tầng:** 8 domain canon (world/timeline/location/weather/culture/belief/
   ritual/supernatural) cùng L1 → tham chiếu nhau **CHỈ qua `reader`** (vd location đọc world);
   `dependencies` giữa các domain L1 = CẤM tuyệt đối (DAG cấm dep cùng tầng) — ghi tường minh
   vào 03_dependency_rules + checker bắt + negative test.
2. **Chống stub tuyệt đối cho domain mới** (location/weather/culture/belief/ritual/object/
   decision_engine/analytics + RESERVED quest): chưa có tool thật → manager/schema/validator
   = `planned` đủ 5 metadata. **Xuất hiện file code MỚI cho các domain này trong amendment
   = kiểm duyệt BÁC** (drift trong phạm vi A1-A8 = VIOLATION, không phải WARN).

## Nhắc R200 + guard
Commit qua worktree · pull --rebase trước · log_ping + push sau · KHÔNG --no-verify ·
message chứa "per Mr.Long authorization" khi đụng registry. Registry đã mở RFC
(`blueprint_constitution: candidate`) — Builder KHÔNG tự re-lock (chữ ký Mr.Long sau audit).

## Self-test (dán lệnh + exit + tail)
```
python tools/blueprint_constitution_check.py     # exit 0 (checker v2)
python tools/architecture_registry_check.py      # 0/0/0
python -m pytest tests/ -q                       # all pass (negative mới: archived-dep,
                                                 #   version-lệch, L1-cross-dep, facet-2-writer)
python tools/cmd_pipeline_gate.py --ref origin/main --skip-build   # ARCH+QA PASS
```
Sign-off `reports/build_report.md`. Dòng cuối: STATUS: READY_FOR_AUDIT / NOT_READY.
Sau READY → kiểm duyệt audit 7 bước (CMD_AUDIT_PROTOCOL.md) → Mr.Long ký re-lock
`blueprint-constitution-v2.0`.
