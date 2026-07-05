# BP9 — 00_compliance.md — Compliance / Publish Gate Architecture
> Enforce: `tools/bp9_compliance_check.py` · chứng thực: `tests/test_bp9_compliance.py` · data: `governance/blueprint/bp9/content_policy.yaml` + `governance/blueprint/bp9/policy_gates.yaml`.

**Mission:** Kiến trúc gate cuối trước xuất bản: ranh giới hư-cấu-giải-trí vs mê-tín-dị-đoan/vi-phạm-pháp-luật — lỗ hổng đã xác nhận "không ai own" (audit 4/7). RECONCILE domain `publisher` đã khai BP0 (planned validator + planned schema) — KHÔNG nâng domain mới, chỉ field-hóa 2 slot đó.

**Purpose:** Khóa ranh giới pháp lý TRƯỚC khi G8 (QA Runtime) wire scanner thật vào pipeline: 2 lằn ranh cứng (không mô tả nghi thức đủ chi tiết làm theo thật · không gắn nội dung với trục lợi/kêu gọi đóng góp thật) phải tồn tại dưới dạng LUẬT có căn cứ điều luật rõ ràng, không phải cảm tính, để mọi gate sau này (generator pre-write, qa_runtime, publisher final) đều tham chiếu CÙNG MỘT nguồn.

**Scope:** `content_policy`: 2 hard_boundaries (HB01/HB02) + sensitivity tier (low/medium/high) + disclaimer rule + quy tắc tôn giáo-đang-thực-hành. `policy_gates`: 7 gate khai báo (domain thật BP0, loại_check, severity, owner_review). KHÔNG viết `tools/compliance_check.py` runtime quét episode thật, KHÔNG wire vào `ci_gate.py` — đó là việc G8. KHÔNG tự diễn giải mở rộng phạm vi pháp lý ngoài 2 điều luật đã dẫn.

**Authority:** Nghị định 38/2021/NĐ-CP Điều 14 (tổ chức mê tín dị đoan trong lễ hội) + Điều 5 khoản 3 (mức phạt gấp đôi pháp nhân) · Bộ luật Hình sự 2015 Điều 320 (tái phạm sau xử phạt hành chính → hình sự). File này CHỈ trích dẫn số điều/khoản — KHÔNG diễn giải lại nội dung pháp lý (đúng RÀNG BUỘC RIÊNG TASK_BP9). Đổi phạm vi pháp lý = RFC + Mr.Long (không tự suy diễn thêm căn cứ).

**Responsibilities:** `content_policy`: mỗi hard_boundary có `can_cu_phap_ly` (≥1, không được luật rỗng); sensitivity_tier quyết `disclaimer_required`; field-hóa `publisher.schema` (BP0) — flip planned→exists trỏ `bp9/content_policy.yaml`. `policy_gates`: mỗi gate `ap_dung_domain` phải resolve thật trong 23-domain inventory BP0 (domain má = FAIL); `loai_check` đúng 1 trong 4 enum khai ở meta; severity=HIGH bắt buộc `owner_review` nhắc rõ "Mr.Long" (không máy tự quyết); field-hóa `publisher.validator` (BP0) — flip planned→exists trỏ `tools/bp9_compliance_check.py` (tầng kiến trúc BP-layer structural checker, KHÁC runtime episode-scanner mà G8 sẽ xây riêng sau — 2 tầng khác nhau, mirror cách BP6 decision_contract.yaml khác tools/decision_engine.py).

**Workflow:** sửa data → `bp9_compliance_check.py` exit 0 → pytest mutation → commit R200 → audit 7 bước → Mr.Long ký → sau BP9 lock: kiểm duyệt tiếp tục FINAL AUDIT BP0-BP9 → tag `system-blueprint-v1.0`.

**Mandatory Rules:** (1) ĐÚNG 2 hard_boundaries — thiếu 1 = FAIL. (2) Mỗi hard_boundary phải có căn cứ pháp lý thật (chống bịa luật). (3) Gate domain phải thật (BP0 23-domain đã đóng) — domain má = FAIL. (4) loai_check phải đúng 1 trong 4 enum khai báo — enum lạ = FAIL. (5) Gate HIGH thiếu owner_review nhắc Mr.Long = FAIL (chống máy tự quyết nội dung nhạy cảm). (6) `publisher.schema`/`publisher.validator` BP0 phải khớp ĐÚNG path 2 file bp9 (field-hóa đúng slot, không lệch — drift = FAIL). (7) DUP-KEY loader single-impl + version khớp 2 file bp9.

**PASS Criteria:** `bp9_compliance_check.py` exit 0 + mutation battery xanh trong `pytest tests/` (ENFORCED qua ci_gate pytest_suite).

**FAIL Criteria:** gate trỏ domain má / content_policy thiếu 1 trong 2 lằn ranh / threshold/số hardcode ngoài chỗ cho phép / publisher.schema BP0 KHÔNG khớp path file thật đã field-hóa (drift) / dup-key trong 2 file bp9 / gỡ stage khỏi doc Mandatory Rules mà không xóa validator tương ứng (unwire ngầm) → exit 1.

**Examples:** gate mới `ap_dung_domain: [khong_ton_tai]` → FAIL DOMAIN-MA; xóa HB02 khỏi content_policy → FAIL HARD-BOUNDARY-THIEU; thêm `min_disclaimer_words: 15` vào content_policy → FAIL R195-HARDCODE; BP0 publisher.schema path lệch bp9/content_policy.yaml → FAIL DRIFT-BP0.

**Promotion Rules:** `bp9_compliance: locked` — FROZEN v1.0 (Mr.Long authorized 4/7), tag `bp9-compliance-v1.0` (xem `governance/architecture_registry.yaml#bp9_compliance`). REALITY ANCHOR (luật 9): checker chạy trên data bp9 THẬT + số đo trong `reports/BP9_REPORT.md`. Pack này chèn vào MASTER chain trước FINAL AUDIT (không phải sau BP8 như dự kiến ban đầu).

## Ghi chú semantics (kiểm duyệt phán khi audit)
`publisher.validator` (BP0) field-hóa trỏ `tools/bp9_compliance_check.py` mang nghĩa "validator cấu trúc luật" (BP-layer, giống bp6/bp7/bp8_check), KHÔNG phải "validator quét episode thật lúc publish" — cái sau là `tools/publish_gate.py` (vẫn CHƯA build, chờ G8 QA Runtime theo đúng RÀNG BUỘC RIÊNG TASK_BP9). Đây là diễn giải CHỦ ĐỘNG của Builder khi field-hóa 2 slot BP0 cùng lúc; nếu kiểm duyệt thấy cách hiểu này sai lệch với ý Mr.Long, đây là điểm cần làm rõ đầu tiên khi audit (không phải lỗi cấu trúc — là quyết định thiết kế cần xác nhận).
