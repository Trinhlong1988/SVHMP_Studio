# TASK BP5 — VALIDATION ARCHITECTURE (theo BP_PIPELINE_MASTER.md)

## MISSION
Hợp nhất bộ checker blueprint thành MỘT cửa + luật review — để BP6-BP8 và G2+ chỉ cần 1 lệnh.

## DELIVERABLES
1. `tools/blueprint_suite_check.py` — runner gọi tuần tự: blueprint_constitution_check +
   bp1_architecture_check + validator BP2/BP3/BP4 (dù nằm chung file hay riêng) → matrix
   PASS/FAIL từng tầng, exit 0 chỉ khi TẤT CẢ xanh. DUP-KEY loader dùng chung (1 implementation,
   import — không copy-paste 5 bản).
2. Wire: thêm stage `('blueprint', 'tools/blueprint_suite_check.py')` vào `tools/ci_gate.py`
   CHECKS — từ đây mọi commit/push/server-CI tự kiểm blueprint (named→ENFORCED thật).
3. `governance/blueprint/bp5/00_validation.md` (11-element) — review flow: Builder self-test →
   kiểm duyệt 7 bước (`prompts/CMD_AUDIT_PROTOCOL.md` — trỏ, không chép lại) → Mr.Long ký;
   promotion rules trỏ constitution/00.
4. Negative test: 1 tầng con FAIL → suite exit 1 · suite bị gỡ khỏi ci_gate → test đỏ
   (mirror test_server_side_ci_wired — chống unwire).

## RÀNG BUỘC RIÊNG
- KHÔNG viết lại các checker con (regression-by-overwrite 3/7!) — chỉ GỌI chúng;
  sửa checker con nếu cần = diff tối thiểu + `git log` file đó để không đè fix cũ.
- ci_gate stage mới phải giữ tổng thời gian pre-push chấp nhận được (< ~3 phút).

## MUTATION AUDIT SẼ BẮN
làm hỏng 1 yaml BP2 → suite phải đỏ từ 1 lệnh · gỡ stage khỏi ci_gate → test unwire đỏ ·
dup-key ở bất kỳ file blueprint nào → suite đỏ.
STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.
