"""SVHMP — INDEPENDENT AUDITOR (PACK1 Constitution, Boss 2/7).
Enforce nguyen tac "Verification independent from implementation":
Builder (Claude) CAM tu tuyen PASS. Verdict PASS/SHIP CHI do gate MAY nay phat ra,
kem Evidence Standard (commit/branch/commands/PASS-FAIL matrix/exit code).

3 Auditor doc lap (khong sua repo, chi doc + chay verify):
  Architecture Auditor -> tools/architecture_registry_check.py (registry 0 MISSING/DUP/UNMAPPED)
  QA Auditor           -> tools/ci_gate.py (registry + regression tests)
  Publish Auditor      -> artifact/version ton tai
Exit 0 = SHIP, 1 = BLOCK_SHIP.
"""
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
PY = sys.executable


def _run(rel):
    r = subprocess.run([PY, str(SVHMP / rel)], capture_output=True, text=True)
    return r.returncode, (r.stdout or '')


def _git(args):
    return subprocess.run(['git', '-C', str(SVHMP)] + args, capture_output=True, text=True).stdout.strip()


def architecture_auditor():
    code, out = _run('tools/architecture_registry_check.py')
    detail = 'registry PASS (0 MISSING/DUP/UNMAPPED)' if code == 0 else 'registry FAIL'
    return ('Architecture', code == 0, detail, code)


def qa_auditor():
    code, out = _run('tools/ci_gate.py')
    npass = out.count('[PASS]')
    return ('QA', code == 0, f'ci_gate {npass} checks PASS', code)


def publish_auditor():
    required = ['bible/37_character_schema.yaml', 'governance/architecture_registry.yaml',
                'governance/master_roadmap.md', 'governance/deprecation_report.md', 'VERSION.md']
    missing = [f for f in required if not (SVHMP / f).exists()]
    return ('Publish', not missing, 'artifacts OK' if not missing else f'MISSING {missing}', 0 if not missing else 1)


def decide(results):
    """results: list[(name, ok, detail, code)] -> (verdict, exit_code).
    Enforce: BAT KY auditor FAIL -> BLOCK_SHIP. Tach ra de test R209 chung thuc."""
    fail = sum(1 for _, ok, _, _ in results if not ok)
    return ('SHIP', 0) if not fail else ('BLOCK_SHIP', 1)


def main():
    commit = _git(['rev-parse', 'HEAD'])
    branch = _git(['rev-parse', '--abbrev-ref', 'HEAD'])
    results = [architecture_auditor(), qa_auditor(), publish_auditor()]

    print("# INDEPENDENT AUDITOR REPORT")
    print("(Builder KHONG tu tuyen PASS — verdict do gate may nay phat ra)")
    print(f"Commit: {commit}")
    print(f"Branch: {branch}")
    print(f"Commands: architecture_registry_check.py + ci_gate.py + artifact check")
    print("PASS/FAIL matrix:")
    for name, ok, detail, code in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} Auditor — {detail} (exit {code})")
    verdict, ec = decide(results)
    print(f"Final verdict: {verdict}")
    print(f"Exit code: {ec}")
    sys.exit(ec)


if __name__ == '__main__':
    main()
