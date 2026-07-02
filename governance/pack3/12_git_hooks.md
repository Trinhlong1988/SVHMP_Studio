# PACK 3 — 12_git_hooks.md — Git Hooks Gate
> Enforce: `.githooks/pre-commit` + `.githooks/pre-push` · chứng thực: `tests/test_hooks_wired.py`.

**Mission:** Chặn commit/push vi phạm NGAY tại máy dev (shift-left) — không đợi CI xa.
**Purpose:** Định nghĩa hook gate: pre-commit guards + pre-push `ci_gate`.
**Scope:** Mọi `git commit`/`git push` local; yêu cầu `core.hooksPath=.githooks` (self-heal, chống inert).
**Authority:** Phái sinh từ PACK1 Constitution (`constitution/00`) + R41 HARDLOCK; doc không tự tạo quyền.
**Responsibilities:** Enforcer `.githooks/*` (Python wrapper, MinGit-safe) · Certify `tests/test_hooks_wired.py` (chống "built≠wired" F1).
**Workflow:** pre-commit (R-ID conflict + rule-mention codified + mass-replace + R41 post_render_gate) → cho commit; pre-push (`ci_gate.py`) → cho push.
**Mandatory Rules:** hook guards (bảng dưới) chạy tại commit/push.
**PASS Criteria:** mọi guard exit 0 → cho commit/push.
**FAIL Criteria:** guard exit 1 → commit/push BLOCK.
**Examples:** R{N} occupied → commit block; ci_gate FAIL → push block.
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Hooks
| Hook | Guard | Chặn |
|---|---|---|
| pre-commit | R-ID conflict · rule-mention codified · mass-replace log · R41 post_render_gate | commit EP FAIL gate / R{N} trùng / rule claim mồ côi |
| pre-push | `ci_gate.py` | push khi registry hoặc test FAIL |

## Reconcile
Hook = tầng shift-left của cùng gate `11_ci_pipeline` (KHÔNG nhân đôi luật, chỉ chạy sớm hơn). Máy Admin = MinGit no-bash → shebang `#!/bin/sh` + Python wrapper (F1 hooks-inert). CẤM `--no-verify` (01_builder Forbidden).
