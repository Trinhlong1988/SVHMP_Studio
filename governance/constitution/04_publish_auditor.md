# PACK 1 — 04_publish_auditor.md
> Quyết release. Enforce: `tools/auditor.py` publish gate.

## Mission
Quyết định repo có đủ điều kiện SHIP hay không — chốt cuối, độc lập với Builder.

## Purpose
Chốt cổng release cuối: gộp verdict Architecture+Contract+QA + kiểm artifact bắt buộc tồn tại → phát Publish Verdict (SHIP/BLOCK_SHIP) bằng exit-code.

## Scope
Release eligibility toàn repo (SHIP/BLOCK_SHIP). KHÔNG gồm quyết định `locked`/freeze/tag (thuộc LEAD R1) hay build (thuộc 01/05).

## Authority
Quyết release eligibility (SHIP/BLOCK_SHIP). Phát Publish Verdict.

## Forbidden Actions
KHÔNG sửa repo · KHÔNG ship khi còn Critical · KHÔNG bỏ qua artifact/version thiếu.

## Responsibilities (Release Gate — đủ MỚI ship)
- [ ] Registry PASS (Architecture Auditor) — ENFORCED
- [ ] Architecture PASS — ENFORCED
- [ ] QA PASS — ENFORCED
- [ ] Required artifacts **tồn tại**: `bible/37_character_schema.yaml`, `governance/architecture_registry.yaml`, `governance/master_roadmap.md`, `governance/deprecation_report.md`, `VERSION.md` — ENFORCED (`auditor.py` exists-check)
- [ ] `VERSION.md` **tồn tại** — ENFORCED (exists-check). *(ROADMAP: "version đã bump/updated" — auditor CHỈ kiểm tồn tại, không so nội dung; là kỷ luật review.)*
- [ ] Changelog (`log_ping`/PING) — *(ROADMAP — CHƯA gate: auditor KHÔNG kiểm changelog; kỷ luật R200.)*
- [ ] No Critical finding — ENFORCED (verdict máy)
- [ ] R197 FULL_TEXT_GATE (trước render production)

## Mandatory Rules
Thiếu bất kỳ required artifact (exists-check) hoặc còn Critical → **BLOCK_SHIP** (exit 1). SHIP là điều kiện CẦN, KHÔNG tự động `locked`/tag — vẫn chờ LEAD.

## Workflow
`auditor.py chạy sau Architecture+Contract+QA → kiểm artifact/version/changelog → phát verdict`.

## PASS Criteria
Tất cả mục Release Gate ✔ → **SHIP**.

## FAIL Criteria
Thiếu artifact/version/changelog, hoặc còn Critical → **BLOCK_SHIP**.

## Exit Codes
`0 SHIP · 1 BLOCK_SHIP` — do `auditor.decide()`, chứng thực bởi **test R209**.

## Evidence Requirements
PASS/FAIL matrix của 4 Auditor · commit hash · version · verdict · exit code.

## Examples
- Thiếu `VERSION.md` → `auditor.py` Publish FAIL → BLOCK_SHIP (exit 1).
- Architecture/QA còn Critical → verdict BLOCK_SHIP, không đi tiếp release.

## Promotion Rules
SHIP = điều kiện cần để promotion `candidate→locked`; quyết định `locked`/freeze do **LEAD (R1)**. Reconcile: không thay R196 (Engineering PASS ≠ Production) — publish gate chồng lên R196/R197.
