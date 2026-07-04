# ARCHITECTURE PRINCIPLES — invariant, không phải module (chính thức hóa 4/7/2026)
> Đối chiếu SVAF v6 Lean Core §9 "Locked Principles" (spec ngoài, đọc 4/7) — xác nhận HDK đã tự có
> 4/5 nguyên tắc này ĐỘC LẬP qua quá trình vật lộn thật (không phải copy) — văn bản hóa chính thức
> thay vì để ngầm hiểu rải rác trong nhiều file. Nguyên tắc, KHÔNG phải pack — không cần audit 7 bước,
> nhưng vi phạm về sau bị coi ngang vi phạm hiến pháp `bible/00_constitution.yaml`.

## 1. Source of Truth Policy
Bible/Ontology là nguồn gốc DUY NHẤT. Episode.md, prompt, ảnh, audio luôn là **output sinh ra** —
không bao giờ là nguồn. Sửa nội dung = sửa bible rồi sinh lại, KHÔNG sửa trực tiếp file sinh ra.
**Bằng chứng HDK đã làm đúng:** `governance/blueprint/*` mọi field trỏ `bible/NN_*.yaml` bằng
`status: exists, path, key` — không chép giá trị (BP6/BP7 audit 4/7 bắt lỗi này 2 lần khi builder
định chép thay vì trỏ). `output/ep_*/episode.md` luôn generate từ bible+roster, không phải nguồn.

## 2. Immutability Policy
Bible đã "khóa" (locked) không sửa trực tiếp — muốn đổi PHẢI bump version (v1.0→v1.1/v2.0), giữ
nguyên nội dung cũ trong lịch sử git. Bible writer = **chỉ Mr.Long** (không phải Builder/kiểm duyệt
tự quyết nội dung).
**Bằng chứng HDK đã làm đúng:** `bible/23_passenger_naming.yaml` v1.0→v1.1 (rule_01-05 giữ nguyên
văn, chỉ thêm rule_06-09) · `bible/37_character_schema.yaml` v2.0→v2.1 (g2_extension thêm, tier_1
gốc không đổi) — cả 2 đều "per Mr.Long authorization" mới sửa (4/7).

## 3. Canonical ID Convention
Định danh nhất quán mọi entity: `{domain}_{loại}_{số}` hoặc `R{số}` cho luật — KHÔNG đổi ID sau khi
tạo (đổi nội dung = version mới, không đổi ID). Chốt CÀNG SỚM CÀNG TỐT, trước khi có nhiều dữ liệu.
**Bằng chứng HDK đã làm đúng:** `PAS_NNNN` cho hành khách/nhân vật (100 slot khóa cứng, `test_
character_manager_r205.py` assert `len==100`) · `R{N}` cho rule hiến pháp · `bp{N}_<name>` cho pack —
3 quy ước ID sống song song, ổn định từ đầu dự án tới nay không đổi format.

## 4. Package Dependency Rules
Chiều phụ thuộc 1 hướng, không vòng, không xuyên tầng: nền tảng (governance/core) không import
tầng cao hơn (content/production). Agent (Builder/CMD) KHÔNG được bypass core — mọi ghi vào state
phải qua đúng cổng máy (validator/gate), không ghi thẳng.
**Bằng chứng HDK đã làm đúng:** BP1-BP8 layer 1-chiều (`layer_groups`: narrative→runtime→
presentation→business, không vòng) · `bible writer=mr_long only` (Agent không tự ghi bible) ·
PACK CLAIM (luật 11) là hàng rào "agent không được tự tiện đụng pack người khác đang giữ".
**Khoảng trống thật (khác SVAF):** SVAF có "Architecture Fitness Test" tự động (assert import
không vòng, chạy mỗi commit) — HDK hiện dựa vào kỷ luật thủ công + audit người, CHƯA có test tự
động kiểm tra chiều import. Backlog, không cấp thiết (governance hiện đã đủ mạnh qua audit người).

## 5. Determinism Contract
Cùng input (bible+roster+seed) → cùng KẾT QUẢ LOGIC (manifest/state/QA-decision) — KHÔNG yêu cầu
pixel/audio-sample y hệt tuyệt đối (bất khả thi qua thay đổi driver/model). Đừng săn bit-identical.
**Trạng thái HDK:** CHƯA chính thức hóa — pipeline render hiện chưa có test "chạy lại cùng input
→ cùng QA-decision" rõ ràng. Đáng làm khi S1 EP01 vertical slice chạy (đúng lúc có golden để so).

---
**Tóm tắt:** 4/5 nguyên tắc đã có bằng chứng thật đang vận hành (không phải lời hứa) — nguyên tắc 4
có 1 khoảng trống nhỏ (fitness test tự động, backlog) — nguyên tắc 5 chưa chính thức, gắn với S1.
Nguồn đối chiếu: `SVAF_v6_LEAN_CORE_MVP.md` §9 (Boss cung cấp 4/7).
