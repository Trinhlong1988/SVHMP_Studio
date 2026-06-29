"""Test R113 — Action verb repeat dedicated."""
import subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EPISODE = BASE / "output/ep_01/episode.md"
TOOL = BASE / "tools/qa_repeat_action.py"


def run():
    r = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True,
                       cwd=str(BASE), encoding="utf-8", errors="ignore", timeout=30)
    return r.returncode, r.stdout


def case(name, text, expect_fail):
    orig = EPISODE.read_text(encoding="utf-8")
    EPISODE.write_text(text, encoding="utf-8")
    try:
        code, out = run()
        if expect_fail:
            assert code != 0, f"{name} expected FAIL but got PASS: {out[-200:]}"
            print(f"  ✅ {name}: caught (FAIL detected)")
        else:
            assert code == 0, f"{name} expected PASS but got FAIL: {out[-200:]}"
            print(f"  ✅ {name}: passed clean")
    finally:
        EPISODE.write_text(orig, encoding="utf-8")


def main():
    print("=== TEST R113 action verb repeat ===")
    case("PASS clean", "## 1. HOOK\nAnh ngước nhìn cửa kính.\n", expect_fail=False)
    case("FAIL liếc gương x4", "## 1. HOOK\n" + ("Bác tài liếc gương chiếu hậu một lần.\n" * 4), expect_fail=True)
    case("FAIL đưa mắt x3", "## 1. HOOK\nAnh đưa mắt nhìn sang. Anh đưa mắt nhìn xuống. Anh đưa mắt nhìn ra.\n", expect_fail=True)
    case("FAIL cúi đầu x3", "## 1. HOOK\nCô cúi đầu nhẹ. Anh cúi đầu chào. Ông cúi đầu lễ phép.\n", expect_fail=True)
    case("EDGE liếc gương x2", "## 1. HOOK\nBác tài liếc gương chiếu hậu. Bác tài lại liếc gương chiếu hậu.\n", expect_fail=False)
    print("=== 5 PASS ===")


if __name__ == "__main__":
    main()
