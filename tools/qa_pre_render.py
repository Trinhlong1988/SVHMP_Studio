"""STAGE 1 — PRE-RENDER GATE (R86 + R76 + R85 + sanity).
BLOCK render if any check fails.

Usage:
  python tools/qa_pre_render.py [episode.md_path]
"""
import sys
import subprocess
from pathlib import Path

TOOLS = Path(__file__).parent
DEFAULT_MD = Path(r"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/output/ep_01/episode.md")


def check(name, cmd):
    print(f"\n[STAGE 1] {name}")
    print(f"  cmd: {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout)
    if r.returncode != 0:
        print(f"  FAIL (exit {r.returncode})")
        return False
    print(f"  PASS")
    return True


def main():
    fp = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MD
    checks = [
        ("R86 EOL diacritic", [sys.executable, str(TOOLS / "qa_eol_diacritic.py"), str(fp)]),
    ]
    results = []
    for name, cmd in checks:
        results.append((name, check(name, cmd)))

    print("\n== STAGE 1 PRE-RENDER GATE SUMMARY ==")
    all_pass = True
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if not ok:
            all_pass = False
    print(f"\nGATE: {'PASS - RENDER ALLOWED' if all_pass else 'FAIL - RENDER BLOCKED'}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
