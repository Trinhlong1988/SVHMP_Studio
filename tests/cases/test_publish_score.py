"""Test R140 — Publish Score gate dedicated."""
import subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EPISODE = BASE / "output/ep_01/episode.md"
TOOL = BASE / "tools/publish_score.py"


def run():
    r = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True,
                       cwd=str(BASE), encoding="utf-8", errors="ignore", timeout=120)
    return r.returncode, r.stdout


def main():
    print("=== TEST R140 publish_score gate ===")

    # PASS case: use current clean episode (should PASS)
    code, out = run()
    print(f"  Clean episode → exit_{code}")
    has_pass = "PUBLISH GATE: PASS" in out or "SHIP ALLOWED" in out
    has_fail = "KILL SWITCH" in out
    if has_pass:
        print(f"  ✅ PASS: gate detected PUBLISH GATE: PASS")
    elif has_fail:
        print(f"  ⚠️ FAIL: gate said KILL — current episode has violation")
    else:
        print(f"  ⚠️ AMBIGUOUS output")

    # FAIL case: inject R86 violation
    orig = EPISODE.read_text(encoding="utf-8")
    bad = orig.replace("## 1. HOOK", "## 1. HOOK\n\nĐây là câu test với từ cũ.\n", 1)
    EPISODE.write_text(bad, encoding="utf-8")
    # rebuild tts_ready
    subprocess.run([sys.executable, str(BASE / "tools/tts_adapter_pre_render.py"), "--ep", "1", "--apply"],
                   capture_output=True, cwd=str(BASE), timeout=30)
    try:
        code, out = run()
        if "KILL SWITCH" in out or code != 0:
            print(f"  ✅ FAIL injected R86 → gate triggered KILL SWITCH")
        else:
            print(f"  ❌ Gate FAILED to catch R86 inject: {out[-300:]}")
            sys.exit(1)
    finally:
        EPISODE.write_text(orig, encoding="utf-8")
        subprocess.run([sys.executable, str(BASE / "tools/tts_adapter_pre_render.py"), "--ep", "1", "--apply"],
                       capture_output=True, cwd=str(BASE), timeout=30)

    print("=== TEST DONE ===")


if __name__ == "__main__":
    main()
