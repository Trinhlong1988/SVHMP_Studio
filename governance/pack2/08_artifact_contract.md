# PACK 2 — 08_artifact_contract.md
> Enforce: `tools/artifact_contract_check.py` · chứng thực: test R212.

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
