# BP9 REPORT — Compliance / Publish Gate Architecture (candidate, chờ audit 7 bước + Mr.Long ký)
> Pack chèn thêm vào MASTER chain trước FINAL AUDIT (không phải BP8 → FINAL AUDIT ngay như dự kiến ban đầu).

## Số đo (REALITY ANCHOR — luật 9: validator PASS trên dữ liệu THẬT)

| Số đo | Giá trị | Nguồn máy |
|---|---|---|
| Hard boundaries khai | **2/2** (HB01 mô_tả_chi_tiết, HB02 trục_lợi_gắn_kèm) | `bp9_compliance_check.py` máy đếm |
| Policy gates khai | **7/7** — mỗi gate domain thật (resolve trong 23-domain BP0) | máy đếm |
| Checker trên data thật | **exit 0, 0 violation** | `tools/bp9_compliance_check.py` |
| Mutation test | **18/18 pass** | `tests/test_bp9_compliance.py` |
| BP0 reconcile | `publisher.schema`/`publisher.validator` flip planned→exists, path khớp đúng 2 file bp9 | `blueprint_constitution_check.py` PASS 0 vi phạm |

## Field-hóa 2 slot BP0 (theo đúng MISSION TASK_BP9)

- `domains.publisher.schema` (blueprint_domains.yaml, LOCKED v2.0): `planned` → **`exists`**, path → `governance/blueprint/bp9/content_policy.yaml`.
- `domains.publisher.validator`: `planned` → **`exists`**, path → `tools/bp9_compliance_check.py`.

**Quyết định thiết kế cần auditor xác nhận:** `publisher.validator` field-hóa thành **BP-layer structural checker** (kiểm 2 file YAML bp9 hợp lệ, giống bp6/bp7/bp8_check), **KHÔNG PHẢI** runtime episode-scanner thật lúc publish. Runtime scanner thật (`tools/publish_gate.py`) vẫn `planned`, chờ G8 QA Runtime xây + wire vào `ci_gate.py` sau (đúng RÀNG BUỘC RIÊNG của TASK_BP9: "KHÔNG viết tools/compliance_check.py runtime quét episode thật + KHÔNG wire vào ci_gate.py"). Đây là cách hiểu chủ động của Builder — nếu kiểm duyệt/Mr.Long thấy lệch ý, đây là điểm cần làm rõ đầu tiên (không phải lỗi cấu trúc).

## Căn cứ pháp lý (chỉ trích dẫn số điều/khoản, không diễn giải lại — đúng RÀNG BUỘC TASK)

- Nghị định 38/2021/NĐ-CP Điều 14 + Điều 5 khoản 3.
- Bộ luật Hình sự 2015 Điều 320.
- Không nghiên cứu lại (tái dùng nguyên văn kết luận deep-research 4/7 đã có trong TASK_BP9).

## Ghi chú kỹ thuật

`sensitivity_tiers` (low/medium/high): TASK nhắc "mirror CULTURAL_EVENTS_KB schema đã có draft" — đã tìm trong repo (grep toàn bộ), **không thấy draft này tồn tại** ở đâu ngoài chính TASK_BP9_COMPLIANCE.md. Thiết kế trực tiếp theo đúng spec low/medium/high mà TASK nêu rõ, KHÔNG bịa thêm cấu trúc mirror một draft không tìm thấy được.

## Deliverables

1. `governance/blueprint/bp9/content_policy.yaml` — 2 hard_boundaries có căn cứ pháp lý thật + sensitivity tier + disclaimer rule + quy tắc tôn giáo-đang-thực-hành = tôn kính không nhại.
2. `governance/blueprint/bp9/policy_gates.yaml` — 7 gate khai báo (domain thật, 4 loại_check enum, severity, owner_review) — KHÔNG viết runtime scanner.
3. `governance/blueprint/bp9/00_compliance.md` — 11-element, Authority chỉ trích dẫn số điều/khoản.
4. `tools/bp9_compliance_check.py` — DUP-KEY loader single-impl; 2 hard_boundaries đủ + có luật; domain-má gate; loai_check enum; severity=HIGH bắt buộc nhắc Mr.Long; numeric-leak toàn file (tái dùng `_numeric_leaks`); BP0 reconcile drift check.
5. `tests/test_bp9_compliance.py` — 18 test: đủ 6 đòn TASK báo trước (domain má, thiếu 1 lằn ranh, hardcode, drift BP0, dup-key, doc-mandatory-rules-unwire-guard).

## Ghi chú cho auditor

- Registry: `bp9_compliance: candidate` (1 dòng, không dup-key).
- **Sau BP9 lock: kiểm duyệt tiếp tục FINAL AUDIT BP0-BP9** → Mr.Long tag `system-blueprint-v1.0`.
- Builder không kết luận PASS/FREEZE — chỉ READY FOR AUDIT.
