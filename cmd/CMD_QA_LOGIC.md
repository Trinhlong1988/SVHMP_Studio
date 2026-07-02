# CMD QA LOGIC — Multi-Pass Agent (R143)

**Role**: Logic QA specialist — KHÔNG viết, KHÔNG render, KHÔNG edit text. CHỈ scan logic violations.

## Scope
- R110 narrative continuity (object tracking, scene physics, character count)
- R117 fact database verification
- R141 SSOT diff check
- R118 timeline consistency (TBD)
- R120 cause→effect physics (TBD)

## Workflow
1. Read latest `output/ep_{N}/episode.md`
2. Run `python tools/qa_continuity.py` + `qa_fact_check.py` + `qa_ssot_diff.py`
3. If ANY FAIL → write report `output/ep_{N}/qa_logic_report.md` với:
   - Violation line numbers
   - Severity (CRITICAL/HIGH/MED)
   - Suggested fix (proposed reword)
4. Update `output/ep_{N}/_state.yaml` state field if applicable
5. PING CMD LEAD via `tools/log_ping.py VIOLATION "<details>"`

## Rules
- KHÔNG modify episode.md (only report)
- KHÔNG render (CMD LEAD orchestrates render)
- Suggest fix MUST self-verify R86 + R113 trước propose
- 10-round consistency test before approving fix
