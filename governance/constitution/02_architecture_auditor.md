# PACK 1 — 02_architecture_auditor.md
> Đọc, KHÔNG sửa repo. Enforce tool: `tools/architecture_registry_check.py` (gọi bởi `auditor.py`).

## Verification Scope
Registry · Source-of-truth · Ownership · Module boundary · **File mồ côi (UNMAPPED)** · **Trùng lặp (DUP — chống spam)** · Dependency map.

## PASS Criteria (exit 0)
`MISSING=0 · DUP=0 · UNMAPPED=0`. Bất kỳ >0 = **Critical** → BLOCK.

## Output (Evidence Standard)
declared/disk count · MISSING list · DUP list · UNMAPPED list · verdict + exit.

## Chống phá hệ thống cũ
Mọi file mới PHẢI map domain trong `file_index.yaml` (chạy `registry_triage.py`) — không để lọt ngoài quản lý.
