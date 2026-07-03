# BLUEPRINT — 02_domain_contract.md — Chuẩn hợp đồng domain (12 field + PLANNED HONESTY)
> Source-of-truth: `governance/blueprint/blueprint_domains.yaml` (machine-readable) · Enforce: `tools/blueprint_constitution_check.py` · chứng thực: `tests/test_blueprint_constitution.py`.

**Mission:** Mỗi domain của SYSTEM_BLUEPRINT là một hợp đồng đầy đủ, máy kiểm được — không domain nào tồn tại chỉ bằng lời kể.
**Purpose:** Khóa format 12-field bắt buộc cho cả 14 domain, và chuẩn khai báo trung thực `exists`/`planned` để contract không bao giờ overclaim.
**Scope:** Cấu trúc từng entry trong `blueprint_domains.yaml`. KHÔNG quản hướng phụ thuộc (doc 03) hay cổng audit (doc 04).
**Authority:** Đổi field-set hoặc ranh giới domain = Change Request Gate (R211) + Mr.Long duyệt. Builder không tự thêm/bớt field.
**Responsibilities — 12 field bắt buộc mỗi domain:**
`responsibility` · `non_responsibility` (ranh giới âm — chống chồng vai) · `source_of_truth` · `manager` · `schema` · `validator` · `reader` · `writer` (ai được đọc/ghi — domain khai báo hoặc `mr_long`) · `lifecycle` (**v2:** `draft|candidate|approved|deprecated|archived` + trường phụ `lock_type: bible|tool|none`) · `dependencies` · `forbidden_dependencies` · `audit_rule`. FACET (relationship/inventory/skill/narration...) khai trong `facets` của domain sở hữu theo FORMAT "1 facet = ĐÚNG 1 writer" — không phải domain riêng (bảng E).
**Workflow:** khai domain → mọi ref file gắn `status: exists|planned` → checker C3 (đủ field) + C7 (exists phải trên disk; planned phải đủ 5 metadata) → pytest → commit R200.
**Mandatory Rules:**
1. `exists` = path ĐANG tồn tại trên disk — khai láo = FAIL phantom (checker Test-Path từng ref).
2. **PLANNED HONESTY RULE:** mọi element `planned` PHẢI đủ 5 metadata: `planned_path` · `owner` · `reason_not_exists_yet` · `target_milestone` (phải nằm trong `milestones` map — chống milestone bịa) · `blocking_dependency`. Thiếu bất kỳ = FAIL.
3. KHÔNG FAIL vì `planned` — Video/Publisher/StoryPlanner chưa có manager thật thì khai planned là trung thực. CẤM tạo stub/vaporware chỉ để lật planned→exists qua test; **planned mà path xuất hiện trên disk = VIOLATION** (điều kiện 2 kiểm duyệt 3/7 — nâng từ WARN; cập nhật contract sang exists phải có duyệt trong cùng change). Status đủ 4 giá trị `exists|planned|deprecated|archived`: `archived` cấm mọi dep/reader/writer trỏ tới; dep vào domain `deprecated` = WARN di cư.
4. `writer` của bible luôn là `mr_long` (bible immutable); `reader`/`writer` chỉ được là domain đã khai hoặc `mr_long`.
5. `non_responsibility` phải chỉ đích danh domain nhận vai đó (chống vùng xám không ai chịu trách nhiệm).
**PASS Criteria:** checker C3+C7+C8 exit 0: 14/14 domain đủ 12 field, mọi `exists` có thật, mọi `planned` đủ 5 metadata, lifecycle/reader/writer hợp lệ (ENFORCED trong ci_gate qua pytest).
**FAIL Criteria:** thiếu field / field lõi rỗng / phantom exists / planned thiếu metadata / milestone bịa / owner không phải domain → checker exit 1.
**Examples:** `video.manager` khai planned đủ 5 metadata (reason: "chưa khởi công — audio-first", milestone M4, blocking R196) → PASS trung thực; cùng entry thiếu `reason_not_exists_yet` → `[VIOLATION] PLANNED HONESTY — thieu metadata`; tạo file `tools/video_builder.py` rỗng để "cho có" → WARN drift + auditor bác theo lesson built≠wired.
**Promotion Rules:** theo `governance/constitution/00_constitution.md` — candidate tới khi Mr.Long ký; reconcile, KHÔNG nhân đôi.
