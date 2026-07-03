# TASK: BP1 CORE ARCHITECTURE (Mr.Long duyệt 3/7 — bản đã vá 2 lỗi chặn + 6 thiếu sót bởi kiểm duyệt)

## INPUT SOURCE OF TRUTH
- Blueprint Constitution **v2.0 LOCKED** (`blueprint-constitution-v2.0`, registry locked).
- Domain Inventory **22+1 RESERVED — ĐÓNG**. CẤM thêm/sửa/xoá domain không có RFC.

## MISSION
Xây BP1 Core Architecture cho SVHMP_Studio — CHỈ tầng kiến trúc, KHÔNG build nội dung production.

## HARD RULES
1. KHÔNG tạo runtime app code. 2. KHÔNG stub code cho domain. 3. KHÔNG sinh episode/audio/video/script.
4. KHÔNG tự lock/tag/freeze. 5. KHÔNG sửa BP0 — phát hiện mâu thuẫn BP0 → **STOP, report FAIL**.
6. **LAYER MODEL:** dùng ĐÚNG **layer số 1-12 + `layer_groups` 4 nhãn** (narrative/runtime/
   presentation/business) đã LOCK trong `blueprint_domains.yaml`. **CẤM tạo scheme layer mới**
   (kiểu L0_foundation..L4_production) — đổi layer model = RFC BP0.
7. R200: commit qua worktree riêng · `git pull --rebase origin main` trước · log_ping + push sau ·
   **CẤM --no-verify**. Test spawn git phải scrub `GIT_*`.

## DELIVERABLES (7 — facet_ownership_matrix CHUYỂN BP3 theo roadmap đã ký)
1. `governance/blueprint/bp1/00_system_blueprint.md` — bản đồ toàn studio (11-element, 0 placeholder);
   ghi rõ: domain_catalog + glossary thay bằng YAML machine-checkable (quyết định có chủ đích);
   khai FORMAT của facet_ownership_matrix (data ở BP3).
2. `governance/blueprint/bp1/dependency_graph.yaml`
3. `governance/blueprint/bp1/interface_contracts.yaml`
4. `governance/blueprint/bp1/layer_contracts.yaml`
5. `tools/bp1_architecture_check.py`
6. `tests/test_bp1_architecture.py` (FLAT trong tests/ — không tạo subdir)
7. `reports/BP1_CORE_ARCHITECTURE_REPORT.md`
+ Map TẤT CẢ file mới vào `governance/file_index.yaml` (+manifest nếu có) → registry 0/0/0.

## SCHEMA
**dependency_graph.yaml:** `validator_version` · `source_constitution_version` (=2.0, máy-so tag/registry)
· `generated_at` · `layers` (số 1-12, khớp blueprint_domains) · `layer_groups` (4 nhãn khớp) ·
`domains[]`: domain_id · layer · depends_on · reads_from · writes_to · lifecycle · owner_artifact.
**interface_contracts.yaml:** validator_version · source_constitution_version · `contracts[]`:
contract_id · provider_domain · consumer_domain · interface_type · allowed_operations ·
forbidden_operations · version · lifecycle · owner_artifact · source_artifact ·
**`status: exists|planned`** (PLANNED HONESTY: planned đủ 5 metadata — hầu hết interface CHƯA có
code thật, khai planned là trung thực; khai exists láo = FAIL).
**layer_contracts.yaml:** validator_version · source_constitution_version · `layers[]`: layer_id ·
purpose · allowed_dependencies · forbidden_dependencies · allowed_outputs · forbidden_outputs.

## VALIDATOR (tools/bp1_architecture_check.py) PHẢI CHECK
1. Mọi domain trong blueprint_domains.yaml xuất hiện trong dependency_graph (22+1).
2. Không domain lạ ngoài inventory. 3. **DUP-KEY loader mọi file BP1** (tái dùng C10 pattern).
4. L1 canon không dep ngang tầng (mirror L1-CROSS-DEP). 5. Active không trỏ archived/deprecated.
6. Interface thiếu owner/source/version/lifecycle/status = FAIL. 7. (chuyển BP3: facet 2-owner).
8. Circular dependency = FAIL (belt-and-braces trên luật layer-thấp-hơn-strictly).
9. dependency_graph.depends_on phải NHẤT QUÁN với blueprint_domains.dependencies (drift = FAIL).
10. Version: validator_version == `__version__` checker; source_constitution_version khớp BP0.
11. Mọi claim trong REPORT phải có file-path tồn tại (validator đọc report, Test-Path từng claim).

## MUTATION TESTS BẮT BUỘC (behavioral trong tests/test_bp1_architecture.py)
M1 thêm domain lạ → FAIL · M2 xoá 1 domain thật → FAIL · M3 L1 dep L1 → FAIL ·
M4 provider trỏ archived → FAIL · M5 dup-key YAML → FAIL · M6 interface thiếu version → FAIL ·
M7 circular dep → FAIL · M8 depends_on lệch blueprint_domains → FAIL ·
M9 report khai file không tồn tại → FAIL · M10 status exists với path giả → FAIL.
(Stub-drift/content-drift: `git status --short` sạch + kiểm duyệt diff baseline độc lập.)

## SELF-TEST (dán lệnh + exit-code + tail)
```
python tools/blueprint_constitution_check.py     # exit 0 (BP0 nguyên vẹn)
python tools/bp1_architecture_check.py           # exit 0
python tools/architecture_registry_check.py      # 0/0/0
python -m pytest tests/ -q                       # all pass
python tools/cmd_pipeline_gate.py --ref origin/main --skip-build   # ARCH+QA PASS
git status --short                               # sạch (không file lạ)
```

## REPORT `reports/BP1_CORE_ARCHITECTURE_REPORT.md`
Executive verdict PASS/FAIL · source commit + BP0 version/hash · bảng deliverable · bảng validation ·
bảng mutation M1-M10 · stub-drift + content-drift check · known limitations · next recommendation.
Sign-off `reports/build_report.md` (local). Dòng cuối: `STATUS: READY_FOR_AUDIT` / `FAIL_NEEDS_FIX`.
