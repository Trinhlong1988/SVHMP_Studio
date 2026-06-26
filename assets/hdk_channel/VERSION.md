---
project: HDK channel
current_round: 1
last_update_ts: 2026-06-26
last_update_by: TBD
schema_version: 1
---

# VERSION — HDK channel

**Rule cứng (memory):** `feedback_fix_registry_rule.md` — Session start protocol bắt buộc đọc file này trước work.

---

## Session start protocol (mọi AI/CMD bắt buộc theo)

```
1. Read CLAUDE.md workspace (C:\Users\Administrator\CLAUDE.md)
2. Read VERSION.md project (THIS FILE) — compare với last_known_version
3. If mismatch → re-read changed artifacts
4. Read BUGS_FIXED.md project
5. Read memory feedback_* relevant
6. THEN start work
```

---

## Current versions per artifact

(empty — fill khi project có artifacts versioned)

| Artifact | Version | Lock date | Notes |
|---|---|---|---|
| (TBD) | | | |

---

## Recent changes (newest first)

(empty — log mọi update từ giờ)

---

## Breaking changes

(empty)

---

## How to check version mismatch

```bash
# CMD/AI session start:
cat VERSION.md | grep -E "^current_round|^last_update_ts"
```

---

## Audit verification

(TBD — link audit script project nếu có)
