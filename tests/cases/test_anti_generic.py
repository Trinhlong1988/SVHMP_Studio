"""Test R128 — Anti-generic AI phrase dedicated."""
import subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EPISODE = BASE / "output/ep_01/episode.md"
TOOL = BASE / "tools/qa_anti_generic.py"


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
            assert code != 0, f"{name} expected FAIL: {out[-200:]}"
            print(f"  ✅ {name}: caught")
        else:
            assert code == 0, f"{name} expected PASS: {out[-200:]}"
            print(f"  ✅ {name}: clean")
    finally:
        EPISODE.write_text(orig, encoding="utf-8")


def main():
    print("=== TEST R128 anti-generic ===")
    case("PASS clean", "## 1. HOOK\nCâu kể chuyện bình thường không có từ AI.\n", expect_fail=False)
    case("FAIL 'một cảm giác khó tả'", "## 1. HOOK\nMột cảm giác khó tả ập đến.\n", expect_fail=True)
    case("FAIL 'không ai biết rằng'", "## 1. HOOK\nKhông ai biết rằng đêm đó.\n", expect_fail=True)
    case("FAIL 'trong khoảnh khắc ấy'", "## 1. HOOK\nTrong khoảnh khắc ấy, anh hiểu ra.\n", expect_fail=True)
    case("FAIL 'có lẽ' x3", "## 1. HOOK\nCó lẽ vậy. Có lẽ thế. Có lẽ ngày mai.\n", expect_fail=True)
    case("FAIL 'rùng mình' x3", "## 1. HOOK\nAnh rùng mình. Cô rùng mình. Ông rùng mình.\n", expect_fail=True)
    case("EDGE 'có lẽ' x2 boundary", "## 1. HOOK\nCó lẽ thế. Có lẽ không.\n", expect_fail=False)
    print("=== 7 PASS ===")


if __name__ == "__main__":
    main()
