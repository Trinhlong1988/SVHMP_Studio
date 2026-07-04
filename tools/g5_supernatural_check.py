"""D5 — G5 Supernatural CLI Gate (mirror pattern bp1-4_check.py / roster_validator.py).
Goi supernatural_validator.run_all(), in ket qua, exit 0/1. Wire vao tools/ci_gate.py
CHECKS (stage 'g5_supernatural', ma ONT5001 — governance/error_code_standard.yaml).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from supernatural_validator import run_all


def main():
    print("=== G5 SUPERNATURAL CHECK (typology + possession state machine) ===")
    errs = run_all()
    for e in errs:
        print(f"  [VIOLATION ONT5001] {e}")
    if errs:
        print(f"=== FAIL — {len(errs)} vi pham ===")
        return 1
    print("=== PASS — typology + possession state machine hop le ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())
