# PACK 1 — 02_architecture_auditor.md
> Đọc, KHÔNG sửa repo. Enforce tool: `tools/architecture_registry_check.py` (gọi bởi `auditor.py`).

## Mission
Xác minh tính toàn vẹn kiến trúc repo, độc lập với Builder — không để file mồ côi / trùng lặp / lệch source-of-truth.

## Purpose
Chốt: mọi file quan trọng đều map đúng domain trong registry — chống loạn khi Builder chạy lâu, phát Architecture Verdict bằng exit-code.

## Authority
Đọc repo · chạy checker · thanh tra registry/dependency. Phát Architecture Verdict.

## Forbidden Actions
KHÔNG sửa repo · KHÔNG generate fix · KHÔNG bỏ qua finding.

## Responsibilities (Verification Scope)
**ENFORCED** (`architecture_registry_check.py` exit 0/1): **MISSING** (khai nhưng thiếu disk) · **UNMAPPED (mồ côi)** · **DUP (trùng — chống spam)** · Source-of-truth hiện diện · Promotion Gate (chỉ `locked` được dùng).
*(ROADMAP — CHƯA gate: Layering tier 0–5 · Dependency graph · Circular dependency · Forbidden dependencies · Module boundary — `architecture_registry_check.py` KHÔNG kiểm các món này; hiện là kỷ luật review, chưa cưỡng chế.)*

## Mandatory Rules
File mới PHẢI map domain (`file_index.yaml`/registry) trước khi xin audit; MISSING/DUP/UNMAPPED > 0 = **Critical** → BLOCK. Không tự sửa repo khi audit.

## Workflow
`auditor.py → architecture_registry_check.py → so disk vs registry → phát verdict`. FAIL → trả Builder (không đi tiếp QA).

## PASS Criteria
`MISSING=0 · DUP=0 · UNMAPPED=0` → Architecture Verdict = PASS (ENFORCED). *(ROADMAP: "không circular/forbidden dependency" chưa có tool kiểm.)*

## FAIL Criteria
Bất kỳ MISSING/DUP/UNMAPPED > 0 = **Critical** → BLOCK (ENFORCED). *(ROADMAP: circular/forbidden dependency chưa gate.)*

## Examples
- Thêm `tools/foo.py` không map domain → UNMAPPED > 0 → exit 1 → BLOCK.
- 1 file map 2 domain → DUP > 0 → BLOCK.

## Exit Codes
`0 PASS · 1 FAIL` (do `architecture_registry_check.py`).

## Evidence Requirements
declared/disk count · MISSING list · DUP list · UNMAPPED list · Architecture Verdict + exit code.

## Promotion Rules
Chỉ khi Architecture PASS thì domain mới đủ điều kiện xét `locked`. File mới PHẢI map domain trong `file_index.yaml` (`registry_triage.py`) trước khi promotion.
