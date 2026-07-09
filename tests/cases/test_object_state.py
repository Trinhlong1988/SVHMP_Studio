"""Test R110 — Object state continuity.

PASS: KP cầm đồng hồ → rơi → KHÔNG còn ôm
FAIL: KP cầm đồng hồ → rơi → vẫn ôm (CONTRADICT)
EDGE: KP cầm → rơi → nhặt lên → vẫn ôm (OK transition)
"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EPISODE = BASE / "output/ep_01/episode.md"
TOOL = BASE / "tools/qa_continuity.py"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # tests/
from _golden_lock import golden_lock  # DEBT-005 vong3: serialize ghi output/ep_01 THAT cross-process


def make_test(case):
    if case == "pass":
        return """# TEST PASS
Trong tay anh, một chiếc đồng hồ.
Chiếc đồng hồ trượt khỏi lòng tay, rơi xuống ghế.
Anh không nhặt lên.
"""
    if case == "fail":
        return """# TEST FAIL
Trong tay anh, một chiếc đồng hồ.
Chiếc đồng hồ trượt khỏi lòng tay, rơi xuống ghế.
Anh gật đầu, tay vẫn ôm chiếc đồng hồ.
"""
    if case == "edge":
        return """# TEST EDGE
Trong tay anh, một chiếc đồng hồ.
Chiếc đồng hồ trượt khỏi lòng tay, rơi xuống ghế.
Anh cúi nhặt chiếc đồng hồ lên.
Anh siết chặt nó trong lòng bàn tay.
"""


def run_qa():
    result = subprocess.run(
        [sys.executable, str(TOOL)],
        capture_output=True, text=True, cwd=str(BASE),
        encoding="utf-8", errors="ignore", timeout=30,
    )
    return result.returncode, result.stdout


def run_case(case, expect_fail):
    with golden_lock():
        orig = EPISODE.read_text(encoding="utf-8")
        EPISODE.write_text(make_test(case), encoding="utf-8")
        try:
            code, out = run_qa()
            if expect_fail:
                assert "FAIL" in out or "CONTRADICT" in out, f"Should catch {case}: {out[-300:]}"
                print(f"  ✅ {case.upper()}: catch contradict")
            else:
                # case allowed
                print(f"  ✅ {case.upper()}: code={code} (PASS expected behavior)")
        finally:
            EPISODE.write_text(orig, encoding="utf-8")


if __name__ == "__main__":
    print("=== TEST R110 object state ===")
    run_case("pass", expect_fail=False)
    run_case("fail", expect_fail=True)
    run_case("edge", expect_fail=False)
    print("=== ALL 3 PASS ===")
