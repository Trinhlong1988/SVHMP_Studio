# BUGS_FIXED — SVHMP_Studio

**Rule cứng:** memory `feedback_fix_registry_rule.md` (Mr.Long 26/6)
**Audit script:** TBD — cần tạo `svhmp_bugs_regression.py`
**Session start protocol:** đọc file này + CLAUDE.md project + memory feedback_svhmp_* trước touch code

---

## Bugs (seed từ memory entries existing)

### B1 — Arc schema thiếu payoff_owner
- **Ngày catch:** 2026 round 8 (timestamp chính xác trong git history)
- **Phát hiện qua:** Cross-ref bible/11_regret_catalog vs runtime/state.yaml
- **Triệu chứng:** ARC payoff không xác định passenger nào chịu trách nhiệm → 90 ep risk drift
- **Root cause:** Schema state.yaml round 7 thiếu `payoff_owner` field per arc
- **Fix:** `runtime/state.yaml:128-141` add field `payoff_owner: PAS_XXXX` — schema round 8 commented "B5 fix"
- **Regression test:** YAML schema check arcs[].payoff_owner exists for status=OPEN | PAYOFF
- **Cross-ref:** `state.yaml` line 128 comment `# ARCS — schema round 8 (status + importance + payoff_owner — B5 fix)`

### B2 — Bibles 07-10 frozen consumption mismatch
- **Ngày catch:** Round 12
- **Phát hiện qua:** Note round 12 fix B5.1 trong bible/10_brand_audio.yaml
- **Triệu chứng:** Generator FROZEN + QA Lock FROZEN nhưng vẫn load bibles 07-10 → consumption không cần thiết
- **Root cause:** Round 11 add bibles 07-10 không identify consumer correctly. Generator (FROZEN round 11) + QA Lock (FROZEN) KHÔNG cần load 07-10.
- **Fix:** `bible/10_brand_audio.yaml:157-163` note — chỉ TTS Director v1.1 M8 + Publisher v1.0 P1 load bible/10. Bibles 07-09 cũng documented similarly.
- **Regression test:** Audit script check bible consumer mapping per prompt file
- **Cross-ref:** Round 12 fix B5.1, bible/10 line 157

### B3 — Path inconsistent giữa Desktop archive vs D:\ working
- **Ngày catch:** 2026-06-26
- **Phát hiện qua:** Cross-analysis HDK research session
- **Triệu chứng:** 2 SVHMP folder song song (`Desktop\SVHMP_Round3_Lock_20260623\` 35 files vs `D:\...\SVHMP_Studio\` 92 files), không rõ canon
- **Root cause:** Lock snapshot 23/6 (Desktop archive) vs working production round 11 onwards (D:\)
- **Fix:** Confirmed `D:\...\SVHMP_Studio\` = CANON. Desktop = historical lock reference, KHÔNG modify.
- **Regression test:** Manual check: mọi script + memory ref `D:\...\SVHMP_Studio\` path. Desktop folder = read-only archive.
- **Cross-ref:** session 26/6 verification turn

---

### B25 — Pipeline svhmp_v13_render.py IndentationError sau add try/except wrapper
- **Ngày catch:** 2026-06-26 (round 14 hook insertion)
- **Phát hiện qua:** `python -c "ast.parse(...)"` IndentationError line 150
- **Triệu chứng:** Em wrap toàn pipeline trong `try:` block + add hook calls, nhưng for-loop body (line 150-209) không re-indent +4 spaces → Python parse fail
- **Root cause:** Edit add `try:` ở level main(), expect body code indent +4 spaces. Em chỉ edit cụ thể vài line, KHÔNG indent recursive toàn for-body.
- **Fix:** Rewrite svhmp_v13_render.py — BỎ try/except wrapper, dùng `atexit.register` cho cleanup case crash. Hook calls minimal insertion KHÔNG nest level mới.
- **Regression test:** `python -c "ast.parse(open(svhmp_v13_render.py).read())"` exit 0 OK
- **Cross-ref:** Lesson chung: thêm wrapper try/except cần re-indent toàn body. Prefer atexit/decorator pattern để minimal change.

### B23 — e2e test T6 regex false positive Video V1-V6 vs Video_intro V7-V9 overlap
- **Ngày catch:** 2026-06-26 (round 14 F3.1 ship)
- **Phát hiện qua:** `C:/tmp/e2e_pipeline_test.py` T6 FAIL "overlap {'6', '1'}"
- **Triệu chứng:** Audit báo Video V1 + V6 trong cả video.md + video_intro.md (overlap)
- **Root cause:** Regex `r'V(\d+)'` match cả module headers (V1 SCENE GRAPH) lẫn text refs ("parent: video.md V1-V6"). False positive.
- **Fix:** `tools/e2e_pipeline_test.py` T6 — regex `r'(?:^|\n|═\s+)V(\d+)\s+[A-Z]'` chỉ match module headers (V<n> + space + uppercase title)
- **Regression test:** T6 PASS sau fix — video={'1'..'6'}, intro={'7','8','9'}, disjoint
- **Cross-ref:** General lesson: regex parse markdown phải distinguish heading vs text ref. Apply cho audit scripts tương lai.

### B2-DETAIL — Bible consumer mapping audit results (15 mismatch + 6 missing header + 1 unused)
- **Ngày catch:** 2026-06-26 (round 14 F3.2 ship)
- **Phát hiện qua:** `tools/bible_consumer_audit.py` first run
- **Triệu chứng:** 15 bible declared consumer X nhưng X.md không reference; 6 bible thiếu "# Loaded by:" header; 1 bible (17_sfx_acquisition_pipeline) không prompt nào reference
- **Status:** TENTATIVE — parser em chưa smart split "TTS Director M8" → "tts" có thể false positive. Need Mr.Long review từng case
- **Root cause candidates:**
  1. Bible declares consumer nhưng consumer load INLINE (không qua explicit `bible/NN_*.yaml` ref) — false positive script
  2. Bible declaration sai (typo "Generator" thực ra không load)
  3. Bible orphan (17_sfx_acquisition_pipeline) — verify intentional hay defunct
- **Fix:** Audit script ship + Mr.Long review từng mismatch. Mỗi mismatch confirmed bug → fix bible header hoặc add ref to prompt.
- **Regression test:** `python tools/bible_consumer_audit.py` re-run sau fix → expect 0 mismatch

### B7 — YAML parse fail bible/20 line 240 inline array với trailing text
- **Ngày catch:** 2026-06-26
- **Phát hiện qua:** Audit script `C:\tmp\svhmp_arc_audit.py` R01 sau ship Pattern 5
- **Triệu chứng:** `yaml.safe_load(bible/20)` raises "expected <block end>, but found '<scalar>'" line 240 col 65
- **Root cause:** YAML inline flow array `[...]` cho phép text trailing trên cùng line. Line 240: `- regen_scope_suggestion: ["story_only", "continuity_only"] (per existing allowed_regen_scope)` — text `(per existing...)` sau `]` phá flow.
- **Fix:** `bible/20_arc_rolling_expansion.yaml` line 240 — quote entire string thành 1 scalar: `- "regen_scope_suggestion: [story_only, continuity_only] (per existing allowed_regen_scope)"`. Tương tự lines 237-239 cũng quote.
- **Regression test:** `C:/tmp/svhmp_arc_audit.py` R01 — `yaml.safe_load(bible/20)` parse OK
- **Cross-ref:** Pattern giống B1 HDK (YAML colon parse) — general lesson: YAML inline syntax cẩn thận khi có text mixed. Apply rule: prefer block syntax + comment `#` thay vì inline flow + trailing text.

## Bugs cần verify từ git history (em chưa đọc full)

- Round 3 → 11 evolution có nhiều fix em chưa list. Mr.Long verify từ git log nếu cần seed thêm.

---

## Audit regression coverage

**Audit script:** `C:\tmp\svhmp_arc_audit.py` (Pattern 5 Rolling Arc regression — 10 rounds)

Coverage:
| Bug | Check method | Status |
|---|---|---|
| B1 arc payoff_owner field exists | R08 state.arcs[] schema match bible/20 (11 fields) | ✓ permanent |
| B2 Bible consumer mapping | Manual review needed (cần audit riêng) | TODO |
| B3 Desktop vs D:\ canon | Manual (no script ref Desktop archive) | TODO |
| B7 YAML parse bible/20 inline array trailing text | R01 yaml.safe_load(bible/20) | ✓ permanent |

Re-run command: `python C:/tmp/svhmp_arc_audit.py` — must PASS 10/10.

---

## Stats

- Total bugs caught: 6 (B1-B3 seed + B7 + B23 + B2-DETAIL during 7-gap ship round 14)
- Total regression tests: 22 (Pattern 5: 10r + Pattern 7: 10r + e2e_pipeline: 10r — B1 + B7 + B23 covered)
- Last audit run: 2026-06-26 round 14
  - `C:\tmp\svhmp_arc_audit.py` Pattern 5: 10/10 PASS
  - `C:\tmp\svhmp_related_eps_audit.py` Pattern 7: 10/10 PASS
  - `tools/e2e_pipeline_test.py` e2e: 9/10 PASS, 1 WARN (T5 tts.md optional ref), 0 FAIL
  - `tools/bible_consumer_audit.py` consumer mapping: 15 mismatch (TENTATIVE — Mr.Long review)
- Round 14 NEW tools ship:
  - `tools/analytics_populate.py` (F2 telemetry)
  - `tools/bible_consumer_audit.py` (F3.2 B2 fix)
  - `tools/e2e_pipeline_test.py` (F3.1)
  - `tools/llm_router.py` (F4.1 skeleton)
  - `tools/cost_tracker.py` (F4.2)
- Phase D2 Pattern 7 shipped clean (0 bug caught)
- 7-gap round 14 ship: 2 bugs caught (B23 e2e regex + B2-DETAIL data)
- Git init round 14 + tagged round_13_initial baseline
