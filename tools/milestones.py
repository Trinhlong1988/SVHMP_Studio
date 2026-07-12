"""SVHMP — Single source of truth for "milestone episode" constants.

Fixes tech-debt MEDIUM finding: MILESTONE_EPS was declared independently in
8 files with 3 different literal values ({10..90}, {10..73..90}, {1..73..90}),
including a self-contradiction between two lines of tools/post_render_gate.py
itself. This module is now the ONLY place any of these sets are literal;
every other file imports from here.

--------------------------------------------------------------------------
Ground truth used to decide the "real" milestone list
--------------------------------------------------------------------------
bible/00_constitution.yaml (version 1.3, "Status: IMMUTABLE — KHÔNG sửa sau
khi lock", lock_date 2026-06-30) — the highest-authority governance doc —
defines, verbatim:

    R37_milestone_ep_rule:
      list: [10, 20, 30, 40, 50, 60, 70, 80, 90]

bible/21_series_arc_design.yaml (arc map, cross-ref'd by R37) tags exactly
these 9 EPs with `milestone_ep: N` / `milestone_special: ...`. EP1 and EP73
are NOT tagged `milestone_ep` anywhere in that file.

Two tools already implemented this correctly and cite R37 explicitly:
tools/pre_write_enforcer.py ("milestone = ep_num in [10,20,...,90]") and
tools/pre_render_checklist.py ("# 2.5 Milestone R37").

=> MILESTONE_EPS below is exactly bible/00 R37's list. EP1 and EP73 are
   deliberately EXCLUDED — see the two constants below for why they still
   show up in some call sites.

--------------------------------------------------------------------------
EP73 — real but SEPARATE rule (driver-line budget), not an R37 milestone
--------------------------------------------------------------------------
bible/21_series_arc_design.yaml M15 (eps 71-75) carries a `note` (not a
`milestone_ep`/`milestone_special` tag):
    "EP73 = driver reveal budget peak — driver có thể nói câu thứ 3 (bible/18)"
tools/pre_render_checklist.py independently encodes the same rule:
    driver_lines_max = 2 if not milestone and ep_number not in [73, 90] else 3
i.e. driver-line budget peak = R37 milestones ∪ {73}. Use
DRIVER_BUDGET_PEAK_EPS (not MILESTONE_EPS) for any check about the
driver-line / soft-ceiling budget rather than the R37 arc-milestone rule.

--------------------------------------------------------------------------
EP1 — NO governance backing found as milestone or driver-budget-peak
--------------------------------------------------------------------------
No bible file tags EP1 as `milestone_ep`, and tools/pre_write_enforcer.py /
tools/pre_render_checklist.py (the two implementations that cite R37
directly) do not include it either. tools/post_render_gate.py already
handles "EP01 golden reference" as its OWN dedicated branch
(`if ep_number == 1: ... # ceiling exception`), independent of any
milestone set — so EP1's presence inside other files' milestone-shaped sets
looks like copy/paste drift from that unrelated exception.

HOWEVER: empirically, EP01's actual output/ep_01/episode.md trips the
`Bác tài ... "..."` driver-quote regex used by tools/audit_100_check.py
(check 3.7) and tools/audit_hidden_bugs.py (check 3) MORE than twice
(verified: 4 regex matches vs. the 2 canonical standard lines — EP1's
golden/legacy content includes a folk-song fragment and a farewell line
that the loose regex also captures). Those two files include EP1 in their
exemption set today, which suppresses that known false-positive rather
than asserting EP1 is a real milestone. Removing it would be a genuine
behavior change to two non-blocking, informational audit reports (neither
is wired into tools/ci_gate.py or any pre-commit/pre-push hook — verified
via grep, only tools/post_render_gate.py is hook-enforced).

Because it is genuinely ambiguous whether that EP1 carve-out is (a) a
deliberate, still-desired false-positive suppression or (b) copy/paste
drift that happens to hide a real EP1 content issue, this module does NOT
silently resolve it. LEGACY_AUDIT_EXEMPT_EPS preserves the exact existing
behavior of the two files that had EP1 in their set, byte-for-byte, so
consolidating the constant causes ZERO test/behavior regression. Whether
EP1 should keep this carve-out permanently (and whether the regex should
instead be tightened) is a policy call left for Mr.Long / Boss — flagged
in the tech-debt fix commit rather than decided here.
"""

# R37 (bible/00_constitution.yaml, IMMUTABLE) — the only real "milestone_ep" list.
MILESTONE_EPS = frozenset({10, 20, 30, 40, 50, 60, 70, 80, 90})

# R37 milestones + EP73's separate bible/21 "driver reveal budget peak" note.
DRIVER_BUDGET_PEAK_EPS = frozenset(MILESTONE_EPS | {73})

# DRIVER_BUDGET_PEAK_EPS + EP1 — preserves pre-existing exemption behavior in
# tools/audit_100_check.py and tools/audit_hidden_bugs.py exactly as-is.
# See "EP1" section above — NOT asserted to be governance-backed, kept only
# for zero-regression parity pending a Boss decision.
LEGACY_AUDIT_EXEMPT_EPS = frozenset(DRIVER_BUDGET_PEAK_EPS | {1})

# --------------------------------------------------------------------------
# EXTRA_BEAT_HOOK_EPS — bible/21_series_arc_design.yaml#extra_beat_HOOK (added
# 2026-07-12, per governance/proposals/bible03_driver_memory_arc_proposal.yaml
# quyet_dinh_cuoi, Mr.Long APPROVED_A).
# --------------------------------------------------------------------------
# 9 EPs where CHAR_DRIVER legitimately says an ADDITIONAL "câu thứ ba" at the HOOK
# position (section 1, before boarding) — distinct from the section-6 CLIFFHANGER
# baseline beat_3 that bible/00#R42/#R55 already recognized for ALL 40/40 tagged
# EPs. Formula (confirmed against episode text, not speculation — see proposal
# quyet_dinh_cuoi.cau_tra_loi_3_diem_mo.extra_beat_HOOK_cong_thuc): PEAK-of-M-block
# (quang_memory_arc) OR first-instance of the mechanism (EP12 — the one exception,
# not a PEAK, but the night the "đếm thêm" device is introduced for the first time).
EXTRA_BEAT_HOOK_EPS = frozenset({12, 15, 20, 25, 30, 35, 40, 45, 50})
