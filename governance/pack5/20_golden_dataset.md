# PACK 5 — 20_golden_dataset.md — Golden Samples + Calibration Policy (R195)
> Enforce: `bible/31_golden_samples.yaml` (data source-of-truth) + `tools/hardcode_classifier.py` (inventory threshold) · chứng thực: `tests/test_pack5_docs.py` + confusion-matrix R203 (`tests/test_qa_confusion_200_r203.py` trong `test_ci_suite.py` SCRIPTS).

**Mission:** Không tin detector chưa calibrate — mọi threshold audio-QA phải neo vào Golden Audio đã được tai người duyệt, không phải trực giác.
**Purpose:** Codify chính sách R195: threshold detector PHẢI calibrate từ golden samples, chứng minh bằng confusion-matrix; phân loại trung thực hardcode nào là nợ calibrate.
**Scope:** Golden dataset (`bible/31_golden_samples.yaml`) + chính sách calibrate threshold cho detector suite (`21_detector_suite.md` liệt kê detector; doc này quản NGUỒN threshold). KHÔNG gồm text-QA (doc 19) và waiver (doc 22).
**Authority:** Phái sinh R195 + R203 (240-case confusion) + R211 registry; doc không tự tạo quyền. Golden samples chỉ Mr.Long duyệt bổ sung (tai người = thẩm quyền cuối về audio).
**Responsibilities:**
- `bible/31_golden_samples.yaml` = data source-of-truth mẫu ĐÃ DUYỆT (positive/negative theo rule).
- `tools/hardcode_classifier.py` = INVENTORY: phân loại hardcode Tier 2.1 theo category (threshold cần calibrate theo R195 / DSP-const / dimension / duration / ratio / magic_unknown). Nó KHÔNG tự calibrate — chỉ trả lời "bao nhiêu hardcode là nợ calibrate".
- Confusion-matrix R203: `tests/test_qa_confusion_200_r203.py` (script-style, chạy qua `test_ci_suite.py` SCRIPTS — ENFORCED trong pytest/ci_gate).
**Workflow:** thêm mẫu golden (Mr.Long duyệt) → `bible/31_golden_samples.yaml` → chạy detector trên bộ golden → đối chiếu confusion-matrix (R203 240-case) → threshold nào lệch = nợ calibrate (tra `hardcode_classifier.py` để biết thuộc category nào) → đề xuất chỉnh threshold + bằng chứng → Mr.Long duyệt.
**Mandatory Rules:** (1) CẤM khai "detector PASS" khi threshold thuộc category `threshold` của classifier mà CHƯA có bằng chứng calibrate từ golden. (2) CẤM sửa `bible/31_golden_samples.yaml` không có duyệt của Mr.Long (bible = immutable trừ LEAD ký). (3) Mọi thay đổi threshold phải kèm confusion-matrix trước/sau.
**PASS Criteria:** confusion-matrix trên golden set đạt mức đã duyệt (R203 suite exit 0 trong ci_gate — ENFORCED) · classifier chạy exit 0 và số `magic_unknown` không tăng.
**FAIL Criteria:** R203 suite exit khác 0 → ci_gate đỏ · threshold đổi mà không có bằng chứng golden → auditor bác (per `pack2/07_evidence_standard.md`).
**Examples:** hạ threshold click-detect theo cảm tính → bị bác vì thiếu confusion trước/sau trên golden; thêm 1 golden negative mới được Mr.Long duyệt → chạy lại R203 → matrix giữ xanh → threshold giữ nguyên hợp lệ.
*(ROADMAP — CHƯA gate: tool calibrate-từ-Golden TỰ ĐỘNG (đọc 31_golden_samples → đề xuất threshold) CHƯA CÓ; hiện calibrate là quy trình tay + bằng chứng. `hardcode_classifier.py` chỉ inventory, KHÔNG phải golden-calibrator — ghi thẳng, không overclaim.)*
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Reconcile
Doc này KHÔNG định nghĩa lại detector (đó là `21_detector_suite.md`); chỉ quản nguồn threshold + chính sách calibrate. Không nhân đôi R203 test — chỉ trỏ.
