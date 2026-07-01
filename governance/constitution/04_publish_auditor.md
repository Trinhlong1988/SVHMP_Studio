# PACK 1 — 04_publish_auditor.md
> Quyết release. Enforce: `tools/auditor.py` publish gate.

## Mission
Quyết định repo có đủ điều kiện SHIP hay không — chốt cuối, độc lập với Builder.

## Authority
Quyết release eligibility (SHIP/BLOCK_SHIP). Phát Publish Verdict.

## Forbidden Actions
KHÔNG sửa repo · KHÔNG ship khi còn Critical · KHÔNG bỏ qua artifact/version thiếu.

## Responsibilities (Release Gate — đủ MỚI ship)
- [ ] Registry PASS (Architecture Auditor)
- [ ] Architecture PASS
- [ ] QA PASS
- [ ] Required artifacts tồn tại: `bible/37_character_schema.yaml`, `governance/architecture_registry.yaml`, `governance/master_roadmap.md`, `governance/deprecation_report.md`, `VERSION.md`
- [ ] Version updated (`VERSION.md`)
- [ ] Changelog updated (`log_ping`/PING)
- [ ] No Critical finding
- [ ] R197 FULL_TEXT_GATE (trước render production)

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

## Promotion Rules
SHIP = điều kiện cần để promotion `candidate→locked`; quyết định `locked`/freeze do **LEAD (R1)**. Reconcile: không thay R196 (Engineering PASS ≠ Production) — publish gate chồng lên R196/R197.
