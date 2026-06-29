"""TEST HARNESS — 10-vòng kiểm thử mọi QA tool.

Chạy:
  python tests/test_harness.py
  python tests/test_harness.py --rounds 10
"""
import sys
import subprocess
import time
import argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

QA_TOOLS = [
    ("R86 EOL", "qa_eol_diacritic.py"),
    ("R92b honorific", "qa_honorific.py"),
    ("R110 continuity", "qa_continuity.py"),
    ("R111 phonetic", "qa_phonetic_safe.py"),
    ("R113 action repeat", "qa_repeat_action.py"),
    ("R117 fact DB", "qa_fact_check.py"),
    ("R128 anti-generic", "qa_anti_generic.py"),
    ("R141 SSOT diff", "qa_ssot_diff.py"),
]


def run_tool(script):
    """Run QA tool, return (passed, elapsed_ms)."""
    start = time.time()
    result = subprocess.run(
        [sys.executable, str(BASE / "tools" / script)],
        capture_output=True, cwd=str(BASE), timeout=60,
        text=True, encoding="utf-8", errors="ignore",
    )
    elapsed_ms = int((time.time() - start) * 1000)
    return result.returncode == 0, elapsed_ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=10)
    args = ap.parse_args()

    print(f"=== TEST HARNESS — {args.rounds} VÒNG QA ===\n")

    results = {tool: {"pass": 0, "fail": 0, "times": []} for tool, _ in QA_TOOLS}
    overall_pass = 0
    overall_fail = 0

    for round_n in range(1, args.rounds + 1):
        print(f"--- VÒNG {round_n}/{args.rounds} ---")
        round_pass = True
        for tool_name, script in QA_TOOLS:
            passed, elapsed = run_tool(script)
            symbol = "✅" if passed else "❌"
            print(f"  {symbol} {tool_name:25s} {elapsed:>5}ms")
            if passed:
                results[tool_name]["pass"] += 1
            else:
                results[tool_name]["fail"] += 1
                round_pass = False
            results[tool_name]["times"].append(elapsed)
        if round_pass:
            overall_pass += 1
        else:
            overall_fail += 1
        print()

    print("=" * 60)
    print(f"SUMMARY {args.rounds} VÒNG: {overall_pass} PASS / {overall_fail} FAIL")
    print("=" * 60)
    print()
    print(f"{'Tool':<25s} {'Pass':>6s} {'Fail':>6s} {'Avg ms':>8s} {'Min':>6s} {'Max':>6s}")
    print("-" * 60)
    for tool, _ in QA_TOOLS:
        r = results[tool]
        times = r["times"]
        avg = int(sum(times) / len(times)) if times else 0
        mn = min(times) if times else 0
        mx = max(times) if times else 0
        print(f"{tool:<25s} {r['pass']:>6d} {r['fail']:>6d} {avg:>8d} {mn:>6d} {mx:>6d}")

    # Consistency check: every tool should be 100% stable across rounds
    flake = sum(1 for tool, _ in QA_TOOLS if results[tool]["pass"] != args.rounds and results[tool]["fail"] != args.rounds)
    print()
    if flake > 0:
        print(f"⚠️ {flake} tool(s) FLAKY (inconsistent across rounds)")
        sys.exit(1)
    else:
        print(f"✅ ALL TOOLS STABLE — KHÔNG FLAKE")
        sys.exit(0 if overall_fail == 0 else 1)


if __name__ == "__main__":
    main()
