# BP1 CORE ARCHITECTURE — REPORT (Builder, TASK_BP1_CORE bản đã vá)

**Executive verdict: PASS** (trong phạm vi thẩm quyền Builder — verdict máy = exit-code các tool dưới; Builder không tự PASS pipeline).

- Source commit khi build: `de83417` (origin/main, sau vá task bởi kiểm duyệt)
- BP0 constitution: **v2.0 LOCKED** — contract_version 2.0.0 · validator BP0 2.1.0 · tag `blueprint-constitution-v2.0` → commit `d92f145`
- Builder: CMD_BUILD · 2026-07-03

## Bảng deliverable (7/7 — mọi path Test-Path bởi chính validator, check 11)
| File | Vai trò | Cách sinh |
|---|---|---|
| `governance/blueprint/bp1/00_system_blueprint.md` | bản đồ toàn cảnh 11-element; khai FORMAT facet matrix (data ở BP3); quyết định domain_catalog+glossary = YAML machine-checkable | tay |
| `governance/blueprint/bp1/dependency_graph.yaml` | 23 domain · layer SỐ 1-12 + layer_groups COPY nguyên vẹn BP0 · depends_on/reads_from/writes_to | **SINH MÁY** từ BP0 (chống đếm tay) |
| `governance/blueprint/bp1/interface_contracts.yaml` | 92 contract (88 read-edge + 4 write-store) · PLANNED HONESTY: 4 exists / 88 planned đủ 5 metadata | **SINH MÁY** từ BP0 |
| `governance/blueprint/bp1/layer_contracts.yaml` | 4 nhãn nhóm đã LOCK: purpose/deps/outputs | tay |
| `tools/bp1_architecture_check.py` | validator v1.0.0 — 11 check + equality BP0 + DUP-KEY loader | tay |
| `tests/test_bp1_architecture.py` | M1-M10 + 5 positive + 3 chống pass-rỗng (FLAT trong tests/) | tay |
| `reports/BP1_CORE_ARCHITECTURE_REPORT.md` | file này | tay |

## Bảng validation (11 check của validator)
| # | Check | Kết quả |
|---|---|---|
| 1 | 23/23 domain BP0 có trong graph, mỗi domain 1 lần | PASS |
| 2 | 0 domain lạ (graph/iface) | PASS |
| 3 | DUP-KEY loader mọi file BP1 (tái dùng C10) | PASS |
| 4 | 8 canon L1 depends_on RỖNG (L1-CROSS-DEP mirror) | PASS |
| 5 | 0 tham chiếu archived/deprecated | PASS |
| 6 | 92/92 interface đủ owner/source/version/lifecycle/status; 4 exists đều Test-Path source thật; 88 planned đủ 5 metadata + milestone thuộc BP0 | PASS |
| 8 | 0 circular dependency | PASS |
| 9 | depends_on == BP0.dependencies từng domain; reads_from == reader grants; layers + layer_groups == BP0 NGUYÊN VẸN (chống layer-scheme lạ) | PASS |
| 10 | validator_version 1.0.0 khớp cả 3 YAML; source_constitution_version == 2.0.0 BP0 | PASS |
| 11 | REPORT-CLAIM: mọi path trong report tồn tại | PASS |
| + | IFACE 2 chiều: 88 read-contract phủ ĐÚNG 88 reader-edge (0 thiếu, 0 thừa); ràng buộc nhóm layer_contracts cho từng dep-edge | PASS |

## Bảng mutation M1-M10 (behavioral, tmp_path, scrub GIT_*)
| M | Đòn | Kỳ vọng | Kết quả |
|---|---|---|---|
| M1 | thêm domain `music` vào graph | DOMAIN-LA FAIL | FAIL đúng ✅ |
| M2 | xóa `timeline` khỏi graph | THIEU domain FAIL | FAIL đúng ✅ |
| M3 | location (L1) dep world (L1) | L1-CROSS-DEP FAIL | FAIL đúng ✅ |
| M4 | culture → archived (provider) | archived FAIL | FAIL đúng ✅ |
| M5 | dup key top-level trong YAML | DUP-KEY FAIL | FAIL đúng ✅ |
| M6 | contract mất version | thiếu version FAIL | FAIL đúng ✅ |
| M7 | character↔dialogue vòng | CIRCULAR FAIL | FAIL đúng ✅ |
| M8 | graph.depends_on lệch BP0 (bỏ decision_engine khỏi generator) | LECH-BP0 FAIL | FAIL đúng ✅ |
| M9 | report khai file không tồn tại | REPORT-CLAIM FAIL | FAIL đúng ✅ |
| M10 | contract exists với source giả | khai lao/phantom FAIL | FAIL đúng ✅ |
| + | xóa 1 read-contract → IFACE-THIEU · đổi scheme L0..L4 → LAYER-SCHEME · planned thiếu metadata → PLANNED HONESTY | FAIL đúng ✅ (3 test bổ sung) |

## Stub-drift + content-drift check
- **0 file code mới cho domain** (hard rule 2): deliverable chỉ md/yaml + 1 validator tool + 1 test — không manager/schema/validator domain nào được tạo. `git status --short` sạch sau commit (dán ở build_report).
- **0 content artifact** (hard rule 3): không episode/audio/video/script nào sinh ra; interface_contracts không tham chiếu output content.
- Bản nháp SAI SCHEME (L0_foundation..L4 + facet matrix tại governance/architecture/) đã bị **XÓA TRƯỚC COMMIT** khi đọc task bản vá — không dấu vết trong git.

## Known limitations
1. `writes_to` chỉ nhận store `runtime/*` — writer-semantics BP0 lỏng ở tts/audio/production (khai writer=self trên SOT bible/pack5-doc). **OBSERVATION BP0, không sửa BP0** (hard rule 5) — đề nghị RFC làm rõ trường `writer` nghĩa "ghi SOT" hay "ghi output" khi mở BP2.
2. 4 interface `exists` dựa trên bằng chứng code đọc trực tiếp 2-3/7 (render G2 L339; preflight `--strict-characters`; 2 store runtime tồn tại) — kiểm duyệt re-verify khi audit.
3. `planned_path` của 88 interface planned trỏ về doc spec BP2 (`governance/blueprint/bp2/interfaces_<provider>.md`) — đặt tên đề xuất, BP2 có thể đổi (rẻ, chỉ metadata planned).
4. Ràng buộc nhóm trong `governance/blueprint/bp1/layer_contracts.yaml` là ràng buộc THÔ trên nhóm; luật thật vẫn là layer-số-thấp-hơn-strictly của BP0 (checker kiểm cả hai).

## Next recommendation
1. Kiểm duyệt audit 7 bước → Mr.Long ký lock BP1.
2. Mở BP2 Domain Architecture: đặc tả nội bộ 5 domain L2-L3 + spec 88 interface planned (điền `interfaces_<provider>.md`).
3. RFC nhỏ làm rõ writer-semantics BP0 (limitation 1) trước khi BP2 viết contract chi tiết.

Final status: **READY_FOR_AUDIT**
