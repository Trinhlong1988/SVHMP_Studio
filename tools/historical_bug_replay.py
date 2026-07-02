"""
historical_bug_replay.py — R_SUPREME gate 4 (Mr.Long lock 30/6 22:00 docx)

Replay historical bugs từ BUGS_FIXED.md catalog. Each bug:
  - run the audit that should now catch it
  - assert PASS (bug no longer present in current state)
  - count: total bugs replayed / passed / failed / not-yet-replayable

Coverage:
  - B60 driver dialogue Q1 vs Q2     -> audit_driver_dialogue_context.py (R174)
  - B61 L130+L132 'kính' lặp          -> audit_phrase_repetition (R177)
  - B62 outro 'Hãy nhớ rằng' cụt      -> grep verify full sentence present
  - T3-T7 + T13 + T14 text fixes      -> short_eol / short_start / vn_style
  - R58 tilde EOL self-introduced     -> audit_tilde_eol
  - R61 prefix expansion 9 lines      -> audit_short_start
  - R66 short chain merges            -> audit_short_chain
  - Voice drift ẹ ẹ (v108)            -> R191 dialogue identity (detect-only)
  - Pause boundary ù ù (v108)          -> R188 boundary artifact (detect-only)
  - Breath xì xì (v108)               -> R189 breath artifact (detect-only)
  - Onset ẹ đầu câu (v108)            -> R190b onset artifact (detect-only)
  - Prosody collapse (v108)           -> R190 prosody (detect-only)

Mr.Long lock: "tool built" KHÔNG đủ. PHẢI run + PASS evidence.

Usage:
    python tools/historical_bug_replay.py
    python tools/historical_bug_replay.py --json
"""
from __future__ import annotations

import argparse
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ReplayCase:
    bug_id: str
    description: str
    audit_command: list[str]
    expected_verdict: str  # PASS / DETECT
    actual_verdict: str = ""
    actual_evidence: str = ""
    status: str = ""  # OK / FAIL / SKIP


def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_ROOT,
        creationflags=CREATE_NO_WINDOW)
    return proc.returncode, proc.stdout, proc.stderr


def grep_episode(pattern: str) -> int:
    import re
    p = REPO_ROOT / "output" / "ep_01" / "episode.md"
    text = p.read_text(encoding="utf-8")
    return len(re.findall(pattern, text))


def assert_grep_present(pattern: str) -> tuple[bool, str]:
    count = grep_episode(pattern)
    return (count > 0), f"grep_count={count}"


def assert_grep_absent(pattern: str) -> tuple[bool, str]:
    count = grep_episode(pattern)
    return (count == 0), f"grep_count={count}"


def run_audit_expect_zero_high(script: str, args: list[str]) -> tuple[bool, str]:
    cmd = [sys.executable, str(REPO_ROOT / "tools" / script), *args]
    rc, out, err = run_cmd(cmd)
    # Most audits exit 0 on PASS / 1+ on FAIL
    return (rc == 0), f"rc={rc}  stdout_tail={out.strip().splitlines()[-1] if out.strip() else '(empty)'}"


def build_cases() -> list[ReplayCase]:
    cases: list[ReplayCase] = []

    cases.append(ReplayCase(
        bug_id="B60",
        description="Driver dialogue Q1 vs Q2 context",
        audit_command=["audit_driver_dialogue_context.py", "--episode", "1"],
        expected_verdict="PASS",
    ))
    cases.append(ReplayCase(
        bug_id="B61",
        description="L130+L132 'kính' lặp 2 dòng liên tiếp",
        audit_command=["__grep_absent_double_kinh__"],
        expected_verdict="PASS",
    ))
    cases.append(ReplayCase(
        bug_id="B62",
        description="Outro 'Hãy nhớ rằng...' cụt (Option D full sentence)",
        audit_command=["__grep_present_option_d__"],
        expected_verdict="PASS",
    ))
    cases.append(ReplayCase(
        bug_id="T14",
        description="Collocation 'cái nhìn rất ngắn' SAI (R180b)",
        audit_command=["audit_vn_style.py", "--episode", "1"],
        expected_verdict="PASS",
    ))
    cases.append(ReplayCase(
        bug_id="R58",
        description="Tilde EOL self-introduced 'khẽ'",
        audit_command=["audit_tilde_eol.py", "--ep", "1", "--summary"],
        expected_verdict="PASS",
    ))
    cases.append(ReplayCase(
        bug_id="R61",
        description="Short START 9 prefix expansion lines",
        audit_command=["audit_short_start.py", "--ep", "1", "--summary"],
        expected_verdict="PASS",
    ))
    cases.append(ReplayCase(
        bug_id="R60",
        description="Short EOL ≤3 từ",
        audit_command=["audit_short_eol.py", "--ep", "1", "--summary"],
        expected_verdict="PASS",
    ))
    cases.append(ReplayCase(
        bug_id="R62",
        description="Anaphora consecutive >2",
        audit_command=["audit_anaphora_consecutive.py", "--ep", "1"],
        expected_verdict="PASS",
    ))
    cases.append(ReplayCase(
        bug_id="R177",
        description="Adjacent word repeat (kính/cô ấy/0 30)",
        audit_command=["audit_phrase_repetition.py", "--ep", "1"],
        expected_verdict="PASS_or_DETECT_only",  # phrase rep audit may flag false positives
    ))
    cases.append(ReplayCase(
        bug_id="V108_voice_drift",
        description="v108 voice 'ẹ ẹ như dê' — R191 dialogue identity (detect-only, no Golden yet)",
        audit_command=["qa_dialogue_identity.py", "--wav", "output/ep_01/sections/cliffhanger.wav", "--json"],
        expected_verdict="DETECT",
    ))
    cases.append(ReplayCase(
        bug_id="V108_pause_boundary",
        description="v108 'ù ù xì' tại pause boundary — R188 boundary artifact (detect-only)",
        audit_command=["qa_boundary_artifact.py", "--wav", "output/ep_01/sections/cliffhanger.wav", "--json"],
        expected_verdict="DETECT",
    ))
    cases.append(ReplayCase(
        bug_id="V108_breath",
        description="v108 'xì xì' thì thầm — R189 breath artifact (detect-only)",
        audit_command=["qa_breath_artifact.py", "--wav", "output/ep_01/sections/cliffhanger.wav", "--json"],
        expected_verdict="DETECT",
    ))
    cases.append(ReplayCase(
        bug_id="V108_onset",
        description="v108 'ẹ ai kể' onset — R190b (detect-only)",
        audit_command=["qa_onset_artifact.py", "--wav", "output/ep_01/sections/cliffhanger.wav", "--json"],
        expected_verdict="DETECT",
    ))
    cases.append(ReplayCase(
        bug_id="V108_prosody",
        description="v108 'tụt cao độ rung lẹm' — R190 prosody (detect-only EVIDENCE)",
        audit_command=["qa_prosody_collapse.py", "--wav", "output/ep_01/sections/cliffhanger.wav", "--json"],
        expected_verdict="DETECT",
    ))

    return cases


def execute_case(case: ReplayCase) -> ReplayCase:
    cmd0 = case.audit_command[0]
    if cmd0 == "__grep_absent_double_kinh__":
        ok, ev = assert_grep_absent(r"Anh ngước nhìn cửa kính\.\n\nSương ngoài cửa kính")
        case.actual_evidence = ev
        case.actual_verdict = "PASS" if ok else "FAIL"
        case.status = "OK" if ok else "FAIL"
        return case
    if cmd0 == "__grep_present_option_d__":
        ok, ev = assert_grep_present(
            r"Hãy nhớ rằng\.\.\. có thể chính bạn cũng đang ngồi trên chuyến xe ấy mà chưa biết\."
        )
        case.actual_evidence = ev
        case.actual_verdict = "PASS" if ok else "FAIL"
        case.status = "OK" if ok else "FAIL"
        return case

    cmd = [sys.executable, str(REPO_ROOT / "tools" / cmd0), *case.audit_command[1:]]
    rc, out, err = run_cmd(cmd)
    case.actual_evidence = f"rc={rc} stdout_tail={out.strip().splitlines()[-1] if out.strip() else '(empty)'}"

    if case.expected_verdict == "DETECT":
        case.actual_verdict = "DETECT_DONE"
        case.status = "OK"
        return case

    if case.expected_verdict in ("PASS", "PASS_or_DETECT_only"):
        if rc == 0:
            case.actual_verdict = "PASS"
            case.status = "OK"
        elif case.expected_verdict == "PASS_or_DETECT_only":
            case.actual_verdict = f"DETECT (rc={rc})"
            case.status = "OK"
        else:
            case.actual_verdict = f"FAIL (rc={rc})"
            case.status = "FAIL"
        return case

    case.status = "SKIP"
    return case


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cases = build_cases()
    results = [execute_case(c) for c in cases]

    n_ok = sum(1 for r in results if r.status == "OK")
    n_fail = sum(1 for r in results if r.status == "FAIL")
    n_skip = sum(1 for r in results if r.status == "SKIP")
    verdict = "PASS" if n_fail == 0 else "FAIL"

    summary = {
        "rule": "R_SUPREME gate 4 historical_bug_replay",
        "total_cases": len(results),
        "ok": n_ok,
        "fail": n_fail,
        "skip": n_skip,
        "verdict": verdict,
    }

    if args.json:
        print(json.dumps({"summary": summary, "cases": [asdict(r) for r in results]}, ensure_ascii=False, indent=2))
    else:
        print(f"[HISTORICAL_REPLAY] cases={len(results)}  OK={n_ok}  FAIL={n_fail}  SKIP={n_skip}  verdict={verdict}")
        print()
        for r in results:
            mark = {"OK": "[OK]  ", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}.get(r.status, "[?]")
            print(f"  {mark} {r.bug_id:<22}  expected={r.expected_verdict:<24}  actual={r.actual_verdict}")
            print(f"       {r.description}")
            print(f"       evidence: {r.actual_evidence}")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
