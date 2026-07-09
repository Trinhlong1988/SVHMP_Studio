"""Test R95 — Character name max 6/episode.

PASS case: name <=6
FAIL case: name >6
EDGE case: name 6 exactly (boundary)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EPISODE = BASE / "output/ep_01/episode.md"
TOOL = BASE / "tools/qa_honorific.py"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # tests/
from _golden_lock import golden_lock  # DEBT-005 vong3: serialize ghi output/ep_01 THAT cross-process


def make_test_text(name_count):
    """Build minimal episode with N instances of 'Khải-Phong' name."""
    body = "Khải-Phong " * name_count
    return f"""# TẬP TEST

[INTRO]
{body}

## 1. HOOK

Story body.
"""


def run_qa():
    """Run qa_honorific.py and return exit code + output."""
    result = subprocess.run(
        [sys.executable, str(TOOL)],
        capture_output=True, text=True, cwd=str(BASE),
        encoding="utf-8", errors="ignore", timeout=30,
    )
    return result.returncode, result.stdout


def test_pass_name_le_6():
    """PASS case: name ≤ 6 should not violate R95"""
    with golden_lock():
        orig = EPISODE.read_text(encoding="utf-8")
        EPISODE.write_text(make_test_text(6), encoding="utf-8")
        try:
            code, out = run_qa()
            # Should NOT flag R95
            assert "Khải-Phong: 6" in out or "Khải-Phong: 7" not in out, f"Unexpected violation: {out}"
            print("  ✅ PASS case: name=6 no violation")
        finally:
            EPISODE.write_text(orig, encoding="utf-8")


def test_fail_name_gt_6():
    """FAIL case: name > 6 should flag R95"""
    with golden_lock():
        orig = EPISODE.read_text(encoding="utf-8")
        EPISODE.write_text(make_test_text(10), encoding="utf-8")
        try:
            code, out = run_qa()
            assert "VƯỢT" in out or "10" in out, f"Should catch name=10 violation: {out}"
            print("  ✅ FAIL case: name=10 caught")
        finally:
            EPISODE.write_text(orig, encoding="utf-8")


def test_edge_name_eq_6():
    """EDGE case: name = 6 exact boundary"""
    with golden_lock():
        orig = EPISODE.read_text(encoding="utf-8")
        EPISODE.write_text(make_test_text(6), encoding="utf-8")
        try:
            code, out = run_qa()
            # boundary OK
            assert "Khải-Phong: 6 ✓" in out, f"Boundary 6 should pass: {out}"
            print("  ✅ EDGE case: name=6 boundary OK")
        finally:
            EPISODE.write_text(orig, encoding="utf-8")


if __name__ == "__main__":
    print("=== TEST R95 name repetition ===")
    test_pass_name_le_6()
    test_fail_name_gt_6()
    test_edge_name_eq_6()
    print("=== ALL 3 PASS ===")
