"""Test R111 — TTS phonetic safe-word.

PASS: safe phrasing
FAIL: trigger phrases ("thở ra một hơi" / "tới nơi an toàn" / "cao vút.")
EDGE: phrase at boundary
"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EPISODE = BASE / "output/ep_01/episode.md"
TOOL = BASE / "tools/qa_phonetic_safe.py"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # tests/
from _golden_lock import golden_lock  # DEBT-005 vong3: serialize ghi output/ep_01 THAT cross-process


def run_tool():
    result = subprocess.run(
        [sys.executable, str(TOOL)],
        capture_output=True, text=True, cwd=str(BASE),
        encoding="utf-8", errors="ignore", timeout=30,
    )
    return result.returncode, result.stdout


def case(name, text, expect_fail):
    with golden_lock():
        orig = EPISODE.read_text(encoding="utf-8")
        EPISODE.write_text(text, encoding="utf-8")
        try:
            code, out = run_tool()
            if expect_fail:
                assert code != 0, f"{name} should FAIL: {out[-200:]}"
                print(f"  ✅ {name}: caught phonetic unsafe")
            else:
                assert code == 0, f"{name} should PASS: {out[-200:]}"
                print(f"  ✅ {name}: passed (safe)")
        finally:
            EPISODE.write_text(orig, encoding="utf-8")


def main():
    print("=== TEST R111 TTS phonetic safe ===")
    case("PASS safe phrasing", "## 1. HOOK\nAnh buông một hơi dài. Lồng ngực anh chậm lại.\n", expect_fail=False)
    case("FAIL 'thở ra một hơi'", "## 1. HOOK\nAnh thở ra một hơi dài.\n", expect_fail=True)
    case("FAIL 'tới nơi an toàn'", "## 1. HOOK\nMáy bay tới nơi an toàn.\n", expect_fail=True)
    case("FAIL 'cao vút.' EOL", "## 1. HOOK\nTóc cột cao vút.\n", expect_fail=True)
    case("FAIL 'Hơi thở chậm lại'", "## 1. HOOK\nHơi thở chậm lại từng nhịp.\n", expect_fail=True)
    case("EDGE 'cao vút,' (comma OK)", "## 1. HOOK\nTóc cột cao vút, áo dài lượt thượt.\n", expect_fail=False)
    print("=== ALL 6 PASS ===")


if __name__ == "__main__":
    main()
