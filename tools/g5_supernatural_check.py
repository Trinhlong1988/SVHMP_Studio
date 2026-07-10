"""D5 — G5 Supernatural CLI Gate (mirror pattern bp1-4_check.py / roster_validator.py).
Wire vao tools/ci_gate.py CHECKS (stage 'g5_supernatural', ma ONT5001 —
governance/error_code_standard.yaml).

Invariant kiem:
  1. typology_possession — supernatural_validator.run_all() tren du lieu that = [] (0 vi pham).
  2. run_all_composition — them 10/7 (per Mr.Long authorization, follow-up sau DEBT-009,
     CMD_AUDIT phat hien): body run_all() PHAI goi du 3/3 sub-check qua _run_all_body_ok()
     (dinh nghia trong supernatural_validator.py, mirror DUNG cach D3 lam voi
     tools/g8_qa_runtime_check.py::_pause_delegation_body_ok - R211 khong viet lai logic).
     TRUOC KHI WIRE invariant nay: chay gate nay DOC LAP (ngoai pytest) khong bat duoc neu ai
     xoa het 3 dong composition trong run_all() (chi pytest test_supernatural_run_all_
     composition.py moi bat) - day chinh la khoang ho CMD_AUDIT phat hien va yeu cau va kin.

Exit 0 = PASS, exit 1 = FAIL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from supernatural_validator import run_all, _run_all_body_ok  # noqa: E402

REPO = Path(__file__).resolve().parent.parent


def check_typology_possession():
    errs = run_all()
    if errs:
        for e in errs:
            print(f"  [VIOLATION ONT5001] {e}")
        return False, f"{len(errs)} vi pham"
    return True, "0 vi pham"


def check_run_all_composition():
    """10/7 follow-up (per Mr.Long authorization, sau DEBT-009): xac nhan run_all() body
    that su goi du 3/3 sub-check - khong chi tin ket qua run_all() tren du lieu sach (co the
    PASS gia neu ca 3 sub-check bi xoa het khoi composition, xem invariant 1 o tren)."""
    src = (REPO / "tools" / "supernatural_validator.py").read_text(encoding="utf-8")
    return _run_all_body_ok(src)


SUITE = [
    ("typology_possession", check_typology_possession),
    ("run_all_composition", check_run_all_composition),
]


def main():
    print("=== G5 SUPERNATURAL CHECK (typology + possession state machine + composition guard) ===")
    fails = []
    for key, fn in SUITE:
        ok, detail = fn()
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {key:<20} {detail}")
        if not ok:
            fails.append(key)
    if fails:
        print(f"=== FAIL — {len(fails)}/{len(SUITE)} invariant: {', '.join(fails)} ===")
        return 1
    print(f"=== PASS — {len(SUITE)}/{len(SUITE)} invariant G5 xanh ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())
