# BP5 VALIDATION ARCHITECTURE — REPORT (Builder, MASTER chain sau BP4 lock)

**Executive verdict: READY FOR AUDIT = YES** (phạm vi Builder — verdict máy = exit-code; Builder không tự PASS).

- Source commit khi build: `3fa53fd` (BP4 locked tag `bp4-runtime-v1.0`, freeze_gate 5/5) · BP0-BP4 LOCKED
- Builder: CMD_BUILD · 2026-07-03

## Bảng deliverable
| File | Vai trò |
|---|---|
| `tools/blueprint_suite_check.py` | v1.0.0 — MỘT cửa GỌI tuần tự 5 checker (bp0 constitution · bp1 core · bp2 domain · bp3 ownership · bp4 runtime) qua subprocess, KHÔNG viết lại checker con; matrix PASS/FAIL từng tầng, không short-circuit; exit 0 chỉ khi 5/5 xanh; pass-through `--bp{N} "<args>"` cho negative test/audit |
| `tools/ci_gate.py` (+1 dòng) | wire stage `('blueprint', 'tools/blueprint_suite_check.py')` vào CHECKS — mọi commit/push/server-CI tự kiểm blueprint (named→ENFORCED thật) |
| `governance/blueprint/bp5/00_validation.md` | doc 11-element; review flow trỏ `prompts/CMD_AUDIT_PROTOCOL.md` (không chép lại); promotion trỏ constitution |
| `tests/test_bp5_validation.py` | 7 case (5 positive + 2 mutation): coverage 5 tầng, loader-1-impl, suite thật 5/5, unwire-guard ci_gate, doc bar, 1-tầng-fail→exit 1 (bắt đúng DUP-KEY), dup-key tầng khác (bp4) → suite đỏ |
| registry | `governance/file_index.yaml` +4 file (total 260→264) · `architecture_registry.yaml` +`bp5_validation`/`bp5_check`/test entry/`bp5_validation: candidate` |

## Bảng validation
| Check | Kết quả |
|---|---|
| Suite gọi ĐỦ 5 tầng bp0-bp4, script tồn tại thật, matrix in đủ kể cả khi có tầng đỏ (không short-circuit — audit thấy toàn cảnh) | PASS (exit 0, 5/5 trên ref sạch) |
| DUP-KEY loader dùng chung: đúng 1 implementation (`blueprint_constitution_check.py`), bp1-bp4 checker IMPORT — máy-khóa bởi `test_dup_key_loader_single_impl` (quét regex toàn tools/) | PASS |
| Wire ci_gate: stage `blueprint` trong CHECKS + unwire-guard `test_blueprint_stage_wired_in_ci_gate` (mirror test_server_side_ci_wired) | PASS |
| Không viết lại checker con: diff tools/ chỉ +blueprint_suite_check.py mới + ci_gate +1 dòng; 5 checker con 0 byte đổi | PASS |
| Thời gian: suite ~3.3s (5 subprocess) — ci_gate pre-push vẫn < ~3 phút (pytest full 2:38 là thành phần lớn nhất, có sẵn từ trước) | PASS |

## Bảng mutation (đòn audit báo trước — tự bắn hết)
| Đòn | Kết quả |
|---|---|
| làm hỏng 1 yaml BP2 (dup-key top-level) → suite đỏ từ 1 lệnh | FAIL đúng ✅ `[FAIL] bp2` + `DUP-KEY` + exit 1, bp0/bp1/bp3/bp4 vẫn chạy đủ matrix |
| gỡ stage blueprint khỏi ci_gate CHECKS | test unwire đỏ ✅ (assert tuple in ci_gate.CHECKS) |
| dup-key ở file blueprint tầng KHÁC (bp4 event_bus) | suite đỏ ✅ (loader chung phủ mọi tầng) |
| copy-paste loader bản 2 vào tools/ | test single-impl đỏ ✅ (regex quét mọi *.py) |
| copy loader kèm UTF-8 BOM đầu file (BOM evasion — audit BP5 Minor) | bị bắt ✅ (guard đọc `utf-8-sig`; neg-test `test_mut_loader_copy_with_bom_detected`) |

## Sự cố bắt được TRONG KHI BUILD (bằng chứng suite có giá trị)
Chạy suite lần đầu ở clone chính: `[FAIL] bp2 — 7 vi phạm PLANNED-DRIFT` do `governance/blueprint/schemas/{character_ext_schema,naming_extension_rules}.yaml` (UNTRACKED, tạo 3/7 20:13 bởi phiên G2 song song) chạm `planned_path` của 7 facet character trong domain_specs. Ref committed origin/main vẫn sạch (suite 5/5 trong worktree). **Heads-up G2/Mr.Long:** sau khi BP5 wire, G2 commit các file này mà không flip `planned→exists` trong `bp2/domain_specs.yaml` (pack LOCKED — cần Mr.Long ký) sẽ bị ci_gate chặn. Đây là PLANNED HONESTY vận hành đúng thiết kế, không phải false-alarm.

## Fix trong build
Audit BP5 (3/7 tối, Minor): guard single-impl đọc `utf-8` thường → file copy loader có BOM đầu (vẫn là Python hợp lệ) làm `^def` re.M trượt match dòng 1 = evasion. Fix: helper `_scan_loader_impls` đọc `utf-8-sig` + neg-test BOM-copy tự chứng minh cắn.

`shlex.split` posix mode nuốt backslash Windows → pass-through path nát → checker con fail SAI LOẠI LỖI (file-not-found thay vì DUP-KEY). Bắt được nhờ luật "negative test phải assert đúng loại lỗi". Fix: `posix=False` + strip quote.

## Drift check
0 domain mới · 0 content · 0 checker con bị sửa · BP0-BP4 + render LOCKED không đụng · không thêm luật nội dung mới (BP5 chỉ luật THI HÀNH).

## Known limitations
1. Suite chạy tuần tự (không parallel) — 5 tầng ~3.3s, chưa cần tối ưu; parallel = RFC nếu pack sau chậm.
2. Pass-through `--bp{N}` tin argv thô (chỉ dành test/audit, không phải surface production).
3. Stage `blueprint` đo sức khỏe TREE hiện tại — file untracked chạm planned_path sẽ đỏ pre-push (đúng chủ đích: chặn từ máy dev, trước cả server-CI).

## Next recommendation
Audit 7 bước → Mr.Long ký lock `bp5-validation-v1.0` → MASTER chain tự chạy `TASK_BP6_DECISION`. Đồng thời G2 cần lộ trình flip `planned→exists` cho 7 facet character (chữ ký Mr.Long vì bp2 locked).

Final status: **READY_FOR_AUDIT**
