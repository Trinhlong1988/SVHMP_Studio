"""Test R149 — Episode state machine dedicated."""
import subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
TOOL = BASE / "tools/episode_state.py"


def run(args):
    r = subprocess.run([sys.executable, str(TOOL)] + args, capture_output=True, text=True,
                       cwd=str(BASE), encoding="utf-8", errors="ignore", timeout=30)
    return r.returncode, r.stdout


def main():
    print("=== TEST R149 episode_state ===")

    # 1. status command exit 0
    code, out = run(["--ep", "99", "status"])
    assert code == 0, f"status should exit_0: code={code} out={out[-200:]}"
    assert "STATE:" in out, f"status output missing STATE: {out[-200:]}"
    print(f"  ✅ status exit_0 + has 'STATE:'")

    # 2. transition draft → outline_approved exit 0
    code, out = run(["--ep", "99", "reset"])
    assert code == 0, f"reset should exit_0"
    code, out = run(["--ep", "99", "transition", "--to", "outline_approved"])
    assert code == 0, f"transition should exit_0: {out[-200:]}"
    print(f"  ✅ transition draft→outline_approved OK")

    # 3. backward transition rejected
    code, out = run(["--ep", "99", "transition", "--to", "draft"])
    assert code != 0, f"backward transition should FAIL"
    print(f"  ✅ backward transition rejected exit_{code}")

    # 4. skip state rejected
    code, out = run(["--ep", "99", "reset"])
    code, out = run(["--ep", "99", "transition", "--to", "published"])
    assert code != 0, f"skip to published should FAIL"
    print(f"  ✅ skip state rejected exit_{code}")

    # 5. validate exit 0
    code, out = run(["--ep", "99", "validate"])
    assert code == 0, f"validate should exit_0"
    print(f"  ✅ validate exit_0")

    # Cleanup
    state_file = BASE / "output" / "ep_99" / "_state.yaml"
    if state_file.exists():
        state_file.unlink()
    print("=== 5 PASS ===")


if __name__ == "__main__":
    main()
