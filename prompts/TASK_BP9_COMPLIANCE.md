# TASK BP9 — COMPLIANCE / PUBLISH GATE ARCHITECTURE (theo BP_PIPELINE_MASTER.md)

## MISSION
Kiến trúc gate cuối trước xuất bản: ranh giới hư-cấu-giải-trí vs mê-tín-dị-đoan/vi-phạm-pháp-luật —
lỗ hổng đã xác nhận "không ai own" (audit 4/7). RECONCILE domain `publisher` đã khai BP0 (planned
validator `tools/publish_gate.py` + planned schema `publish_manifest_schema.yaml`) — KHÔNG nâng
domain mới, chỉ field-hóa 2 slot đó. FORMAT + CONTRACT, KHÔNG quét nội dung episode thật (đó là G8
QA Runtime wire vào pipeline — BP9 chỉ định nghĩa LUẬT + kiểm cấu trúc luật, mirror cách BP6/BP7 chỉ
định FORMAT cho G6/G7 dùng sau).

## CĂN CỨ ĐÃ CÓ (không nghiên cứu lại — tái dùng nguyên văn)
Deep-research 4/7 đã xác nhận nguồn thật:
- **Nghị định 38/2021/NĐ-CP** Điều 14: tổ chức mê tín dị đoan trong lễ hội = phạt 15-20tr (cá nhân),
  tổ chức-pháp-nhân gấp đôi (Đ.5 khoản 3); tham gia (nhẹ hơn) = 3-5tr.
- **Điều 320 Bộ luật Hình sự 2015**: tái phạm sau xử phạt hành chính → hình sự, 10-100tr hoặc tù
  6 tháng-3 năm, tới 3-10 năm nếu hậu quả nghiêm trọng/thu lợi ≥200tr.
- Pháp luật KHÔNG định nghĩa cứng "mê tín dị đoan" — ranh giới thực tế: tin điều mơ hồ + **lấy trục
  lợi làm mục đích chính** + gây hậu quả xấu, đối lập "hoạt động tín ngưỡng" hợp pháp (Luật Tín
  ngưỡng Tôn giáo 2016).
→ 2 LẰN RANH CỨNG rút ra (không phải suy đoán, có căn cứ điều luật): **(1) KHÔNG mô tả nghi thức đủ
chi tiết để làm theo thật · (2) KHÔNG gắn nội dung với hoạt động trục lợi/kêu gọi đóng góp thật.**

## DELIVERABLES
1. `governance/blueprint/bp9/content_policy.yaml` — field-hóa `publisher.schema` (BP0 planned_path
   `governance/blueprint/schemas/publish_manifest_schema.yaml`): 2 lằn ranh cứng trên (mỗi lằn:
   rule_id · mô_tả · căn_cứ_pháp_lý trỏ đúng điều luật trên, KHÔNG chép lại toàn văn) + sensitivity
   tier (low/medium/high — mirror `CULTURAL_EVENTS_KB` schema đã có draft) + yêu cầu disclaimer hư
   cấu khi sensitivity≥medium + quy tắc tôn giáo-đang-thực-hành = tôn kính không nhại.
2. `governance/blueprint/bp9/policy_gates.yaml` — danh sách gate KHAI BÁO (mirror pattern SVAF Policy
   Gates — KHÔNG viết 1 hàm to): mỗi gate = gate_id · áp_dụng_domain[] · loại_check (mo_ta_chi_tiet |
   truc_loi_gan_kem | ton_giao_khong_ton_kinh | thieu_disclaimer) · severity · owner_review (sensitivity
   cao → Mr.Long duyệt case-by-case, KHÔNG máy tự quyết).
3. `governance/blueprint/bp9/00_compliance.md` (11-element, theo mẫu BP6/BP7) — Authority trỏ chính
   Nghị định/Điều luật trên (không diễn giải lại nội dung pháp lý, chỉ trích dẫn số điều/khoản).
4. `tools/bp9_compliance_check.py` — validator CẤU TRÚC (mirror bp6/bp7_check pattern): DUP-KEY loader
   single-impl · đủ 2 lằn ranh trong content_policy · mọi gate trong policy_gates trỏ domain đã khai
   BP0 (domain-ma = FAIL) · KHÔNG số/ngưỡng hardcode ngoài chỗ cho phép · publisher.validator/schema
   BP0 (`blueprint_domains.yaml`) khớp đúng path file này (field-hóa đúng slot, không lệch).
5. `tests/test_bp9_compliance.py` — negative test theo mục dưới.

## RÀNG BUỘC RIÊNG
- KHÔNG viết `tools/compliance_check.py` runtime quét episode thật + KHÔNG wire vào `ci_gate.py` —
  đó là việc G8 QA Runtime ("audit theo blueprint + vá gap" đã ghi sẵn trong roadmap), BP9 chỉ ra
  LUẬT để G8 áp dụng sau, đúng ranh giới BP-vs-G đã giữ nhất quán từ BP6/BP7.
- KHÔNG tự diễn giải mở rộng phạm vi pháp lý ngoài 2 điều luật đã dẫn — nếu thấy cần thêm căn cứ,
  đánh dấu `status: needs_legal_review` thay vì tự suy luận (R_SUPREME không bịa).
- Claim pack trước khi build: `python tools/build_claim.py claim bp9_compliance <phiên>` (luật 11).

## MUTATION AUDIT SẼ BẮN
gate trỏ domain ma (không có trong BP0) → FAIL · content_policy thiếu 1 trong 2 lằn ranh → FAIL ·
threshold/số hardcode ngoài chỗ cho phép → FAIL · publisher.schema BP0 KHÔNG khớp path file thật đã
field-hóa (drift) → FAIL · dup-key trong 2 file bp9 → FAIL · gỡ stage khỏi doc Mandatory Rules mà
không xóa validator tương ứng (unwire ngầm) → FAIL.
STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.
