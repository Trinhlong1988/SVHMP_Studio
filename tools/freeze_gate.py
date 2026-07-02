"""freeze_gate.py — deep-audit (2/7): lam FREEZE tai lap duoc bang MAY.

Van de: claim "freeze-gate 16-phase PASS" chi ton tai duoi dang PROSE trong tag
annotation + PING (tu nhac chinh no), KHONG co tool tai lap -> vi pham chuan
"moi rule phai co tool + test". Con so phase (14 trong PACK1 vs 16 trong tag)
khong neo vao dinh nghia nao.

Tool nay gom bang chung freeze cua 1 enterprise pack thanh cac PHASE chay duoc.
So phase = so check THAT o day (neo con so, het mau thuan prose):
  P1 registry: enterprise_pack_progress.<pack> == 'locked'
  P2 auditor.py -> SHIP (exit 0)  [gom registry 0/0/0 + ci_gate + pytest + publish]
  P3 doc-completeness test PASS
  P4 git tag <tag> ton tai (local)
  P5 git tag <tag> da push remote
Exit 0 = FREEZE-READY (reproducible), 1 = thieu phase, 2 = input loi.
In theo Evidence Standard (commit/branch/commands/matrix/verdict/exit) ->
pipe duoc vao evidence_check.py.

Dung:
  python tools/freeze_gate.py --pack pack2_governance --tag pack2-governance-v1.0 \
      --doc-test tests/test_pack2_governance_docs.py
"""
import argparse
import subprocess
import sys
from pathlib import Path

import yaml

SVHMP = Path(__file__).resolve().parent.parent
PY = sys.executable
REG = SVHMP / "governance" / "architecture_registry.yaml"


def _run(args):
    return subprocess.run(args, capture_output=True, text=True, cwd=str(SVHMP),
                          encoding="utf-8", errors="replace")


def find_pack_progress(node):
    """Tim dict enterprise_pack_progress bat ky dau trong registry (tach de test)."""
    if isinstance(node, dict):
        p = node.get("enterprise_pack_progress")
        if isinstance(p, dict):
            return p
        for v in node.values():
            r = find_pack_progress(v)
            if r is not None:
                return r
    elif isinstance(node, list):
        for v in node:
            r = find_pack_progress(v)
            if r is not None:
                return r
    return None


def check_pack_locked(pack):
    reg = yaml.safe_load(REG.read_text(encoding="utf-8"))
    prog = find_pack_progress(reg) or {}
    val = prog.get(pack)
    return val == "locked", f"{pack}={val}"


def check_auditor():
    r = _run([PY, str(SVHMP / "tools" / "auditor.py")])
    return r.returncode == 0, ("auditor SHIP" if r.returncode == 0
                               else f"auditor exit {r.returncode} (BLOCK_SHIP)")


def check_doc_test(rel):
    r = _run([PY, "-m", "pytest", rel, "-q", "-p", "no:cacheprovider"])
    name = rel.rsplit("/", 1)[-1]
    return r.returncode == 0, f"{name} " + ("PASS" if r.returncode == 0 else f"FAIL exit {r.returncode}")


def check_tag_local(tag):
    ok = bool(_run(["git", "tag", "-l", tag]).stdout.strip())
    return ok, f"tag {tag} " + ("exists" if ok else "MISSING")


def check_tag_remote(tag):
    ok = tag in _run(["git", "ls-remote", "--tags", "origin", tag]).stdout
    return ok, f"tag {tag} " + ("pushed" if ok else "NOT on remote")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default="pack2_governance")
    ap.add_argument("--tag", default="pack2-governance-v1.0")
    ap.add_argument("--doc-test", default="tests/test_pack2_governance_docs.py")
    ap.add_argument("--skip-remote", action="store_true",
                    help="bo qua P5 (khi khong co mang / CI offline)")
    a = ap.parse_args()

    commit = _run(["git", "rev-parse", "HEAD"]).stdout.strip()
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

    phases = [
        ("P1 registry locked", check_pack_locked, (a.pack,)),
        ("P2 auditor SHIP", check_auditor, ()),
        ("P3 doc completeness", check_doc_test, (a.doc_test,)),
        ("P4 tag exists", check_tag_local, (a.tag,)),
    ]
    if not a.skip_remote:
        phases.append(("P5 tag pushed", check_tag_remote, (a.tag,)))

    print("# FREEZE GATE — reproducible (deep-audit 2/7)")
    print(f"Pack: {a.pack}   Commit: {commit}   Branch: {branch}")
    print(f"Commands: auditor.py + pytest {a.doc_test} + registry/tag checks")
    print("PASS/FAIL matrix:")
    fails = 0
    for name, fn, args in phases:
        try:
            ok, detail = fn(*args)
        except Exception as e:
            ok, detail = False, f"ERR {e}"
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} — {detail}")
        fails += 0 if ok else 1
    verdict = "FREEZE-READY" if not fails else "NOT FREEZE-READY"
    print(f"Final verdict: {verdict}  ({len(phases) - fails}/{len(phases)} phase PASS)")
    ec = 0 if not fails else 1
    print(f"Exit code: {ec}")
    return ec


if __name__ == "__main__":
    sys.exit(main())
