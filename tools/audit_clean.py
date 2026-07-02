"""audit_clean.py — deep-audit (2/7): audit DETERMINISTIC tren ref SACH.

Bai hoc rut kinh nghiem (2/7): may Admin co 2 session chung 1 working-tree/index.
Chay gate tren tree dang bi session kia sua LIVE -> ket qua chop-chop
(MISSING/UNMAPPED thoang qua tu file dang tao/xoa) -> BAO DONG GIA. Da bi lua 2
lan trong 1 phien (MISSING=1 roi UNMAPPED=1, ca 2 tu het khi chay lai).

Fix cung: tool nay LUON tao git worktree DETACHED tai <ref> (mac dinh origin/main),
chay cac gate BEN TRONG worktree do (immune shared dirty tree), roi don sach.
Ket qua tai lap duoc, khong phu thuoc trang thai working tree hien tai.

Gates:
  - ci_gate.py                     (registry 0/0/0 + regression pytest)
  - freeze_gate.py --skip-remote   (chi khi --with-freeze)
Exit 0 = ref SACH, 1 = co gate FAIL, 2 = setup loi (git/worktree).

Dung:
  python tools/audit_clean.py                       # audit origin/main
  python tools/audit_clean.py --ref 22ce08c
  python tools/audit_clean.py --with-freeze
  python tools/audit_clean.py --keep                # giu worktree de soi tay
"""
import argparse
import subprocess
import sys
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
PY = sys.executable
WT = SVHMP.parent / ".audit_clean_wt"  # sibling; ten co dinh, don truoc khi dung


def _git(*a):
    return subprocess.run(["git", "-C", str(SVHMP), *a], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def gate_cmds(wt, py, with_freeze):
    """Danh sach (label, argv) gate chay trong worktree. Tach de test."""
    cmds = [("ci_gate", [py, str(Path(wt) / "tools" / "ci_gate.py")])]
    if with_freeze:
        cmds.append(("freeze_gate", [py, str(Path(wt) / "tools" / "freeze_gate.py"),
                                     "--skip-remote"]))
    return cmds


def _cleanup():
    _git("worktree", "remove", str(WT), "--force")
    _git("worktree", "prune")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--with-freeze", action="store_true")
    ap.add_argument("--keep", action="store_true", help="giu worktree sau khi chay")
    a = ap.parse_args()

    resolved = _git("rev-parse", "--short", a.ref).stdout.strip()
    if not resolved:
        print(f"[audit_clean] ERR: ref khong resolve duoc: {a.ref}")
        return 2

    _cleanup()  # phong worktree cu ket lai
    add = _git("worktree", "add", "--detach", str(WT), a.ref)
    # LUU Y: git-lfs post-checkout hook fail (may Admin khong co lfs) lam
    # `git worktree add` tra returncode != 0 DU worktree DA tao thanh cong.
    # -> xac minh bang rev-parse trong worktree, KHONG tin returncode (giong
    # pre-push da coi lfs la optional).
    head = subprocess.run(["git", "-C", str(WT), "rev-parse", "HEAD"],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.strip()
    if not head:
        print(f"[audit_clean] ERR tao worktree:\n{add.stderr.strip()}")
        return 2

    print("# AUDIT CLEAN — deterministic tren ref sach (deep-audit 2/7)")
    print(f"Ref: {a.ref} ({resolved})   Worktree: {WT}")
    print("PASS/FAIL matrix:")
    fails = 0
    try:
        for label, argv in gate_cmds(str(WT), PY, a.with_freeze):
            r = subprocess.run(argv, cwd=str(WT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            ok = r.returncode == 0
            print(f"  [{'PASS' if ok else 'FAIL'}] {label} (exit {r.returncode})")
            if not ok:
                tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-6:])
                print("    " + tail.replace("\n", "\n    "))
                fails += 1
    finally:
        if not a.keep:
            _cleanup()
        else:
            print(f"[audit_clean] --keep: worktree giu tai {WT}")

    verdict = "CLEAN" if not fails else "DIRTY (co gate FAIL)"
    print(f"Final verdict: {a.ref} = {verdict}")
    ec = 0 if not fails else 1
    print(f"Exit code: {ec}")
    return ec


if __name__ == "__main__":
    sys.exit(main())
