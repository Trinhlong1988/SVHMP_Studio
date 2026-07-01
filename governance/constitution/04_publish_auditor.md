# PACK 1 — 04_publish_auditor.md
> Quyết release. Enforce: `tools/auditor.py` publish gate.

## Release Gate (đủ MỚI ship)
- [ ] Architecture Auditor PASS
- [ ] QA Auditor PASS
- [ ] Required artifacts tồn tại: `bible/37_character_schema.yaml`, `governance/architecture_registry.yaml`, `governance/master_roadmap.md`, `governance/deprecation_report.md`, `VERSION.md`
- [ ] No Critical finding
- [ ] R197 FULL_TEXT_GATE (trước render production)

## Final Verdict
`SHIP` (exit 0) / `BLOCK_SHIP` (exit 1) — do `auditor.decide()` phát, chứng thực bởi **test R209**.

## Reconcile
Không thay R196 (Engineering PASS ≠ Production) — publish gate là bước SAU cùng, chồng lên R196/R197.
