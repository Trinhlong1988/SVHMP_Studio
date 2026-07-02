# PACK 2 — 08_artifact_contract.md
> Enforce: `tools/artifact_contract_check.py` · chứng thực: test R212.

**Mission:** Chống phantom DoD — mọi artifact khai trong registry PHẢI tồn tại thật trên disk.
**Purpose:** Ràng buộc artifact KHAI == file thật (chống phantom/báo cáo láo).
**Scope:** Mọi domain/milestone theo DoD 8 chiều.
**Authority:** Phái sinh từ PACK1 Constitution (`constitution/00`) + registry (R211); doc không tự tạo quyền.
**Responsibilities:** Enforcer `tools/artifact_contract_check.py` · Certify `test R212` · Builder sinh artifact bằng máy, không tay.
**Workflow:** Chặng Contract Auditor — verify trước QA/Publish trong `auditor.py`.
**Mandatory Rules · PASS Criteria · FAIL Criteria · Examples:** xem dưới (PASS=0 phantom; FAIL=artifact khai != disk → Critical BLOCK; ví dụ G2 thiếu validator → block).
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Hợp đồng: mỗi domain khai artifact nào PHẢI có file đó trên disk
DoD 8 chiều: `schema · manager · validator · report · test · md_doc · sample_yaml · regression`.
- **Critical:** artifact KHAI trong registry mà KHÔNG có trên disk (phantom) → `BLOCK` (chống báo cáo láo).
- **Minor:** chiều DoD chưa có (gap thật) → report, backlog (G2+ lấp).

## Artifact bắt buộc theo G (milestone)
| G | Phải sinh |
|---|---|
| G1 governance | registry · file_index · deprecation_report · manifests · checker/ci_gate/auditor · test |
| G2 character | schema bible/37 · manager · validator ×2 · report · test ×4 · sample roster |
| G3 dialogue | generator · validator dialect · golden set · test confusion |
| G4 world/time | schema · store · consistency validator · test |

## Máy sinh, không tay
`artifact_contract_check.py` in DoD matrix từ registry + verify tồn tại. Verdict thay ma trận viết tay (chống láo).
