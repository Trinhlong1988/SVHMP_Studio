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
    """Run QA tool, return (returncode, elapsed_ms, crashed).

    deep-audit F2 (2/7): rc 0 = clean, rc 1 = GATE tim ra vi pham CONTENT
    (tool KHOE, khong phai loi tool), rc khac / traceback = tool CRASH.
    Truoc day harness coi rc!=0 = 'tool fail' -> lan lon gate-bat-loi voi
    tool-hong. Gio phan biet: chi FLAKY (rc doi giua cac vong) hoac CRASH
    moi la loi TOOL."""
    start = time.time()
    result = subprocess.run(
        [sys.executable, str(BASE / "tools" / script)],
        capture_output=True, cwd=str(BASE), timeout=60,
        text=True, encoding="utf-8", errors="ignore",
    )
    elapsed_ms = int((time.time() - start) * 1000)
    crashed = (result.returncode not in (0, 1)) or ("Traceback" in (result.stderr or ""))
    return result.returncode, elapsed_ms, crashed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=10)
    args = ap.parse_args()

    print(f"=== TEST HARNESS — {args.rounds} VÒNG QA ===\n")

    results = {tool: {"rcs": [], "times": [], "crash": 0} for tool, _ in QA_TOOLS}

    for round_n in range(1, args.rounds + 1):
        print(f"--- VÒNG {round_n}/{args.rounds} ---")
        for tool_name, script in QA_TOOLS:
            rc, elapsed, crashed = run_tool(script)
            symbol = "💥" if crashed else ("✅" if rc == 0 else "⚠️")
            state = "CRASH" if crashed else ("clean" if rc == 0 else "gate-fail")
            print(f"  {symbol} {tool_name:25s} {elapsed:>5}ms  (rc={rc} {state})")
            results[tool_name]["rcs"].append(rc)
            results[tool_name]["times"].append(elapsed)
            if crashed:
                results[tool_name]["crash"] += 1
        print()

    # deep-audit F2: do SUC KHOE tool (on dinh + khong crash), KHONG do content.
    # gate-fail on dinh = tool KHOE (content co vi pham -> sua o content).
    print("=" * 64)
    print(f"TOOL HEALTH — {args.rounds} vòng (đo sức khoẻ TOOL, không đo content)")
    print("=" * 64)
    print(f"{'Tool':<25s} {'rc':>6s} {'state':>10s} {'avg ms':>8s}")
    print("-" * 64)
    flaky, crashed_tools, gate_fail = [], [], []
    for tool, _ in QA_TOOLS:
        r = results[tool]
        rcs, times = r["rcs"], r["times"]
        avg = int(sum(times) / len(times)) if times else 0
        stable = len(set(rcs)) == 1
        if r["crash"]:
            state = "CRASH"; crashed_tools.append(tool)
        elif not stable:
            state = "FLAKY"; flaky.append(tool)
        elif rcs and rcs[0] == 1:
            state = "gate-fail"; gate_fail.append(tool)
        else:
            state = "clean"
        print(f"{tool:<25s} {(rcs[0] if stable else 'var')!s:>6s} {state:>10s} {avg:>8d}")

    print()
    if gate_fail:
        print(f"ℹ️  {len(gate_fail)} gate báo vi phạm CONTENT (tool KHOẺ — sửa ở content, "
              f"không phải lỗi tool): {gate_fail}")
    if crashed_tools or flaky:
        print(f"❌ TOOL KHÔNG KHOẺ: CRASH={crashed_tools} FLAKY={flaky}")
        sys.exit(1)
    print("✅ MỌI TOOL KHOẺ — chạy ổn định, không crash/flaky")
    sys.exit(0)


if __name__ == "__main__":
    main()
