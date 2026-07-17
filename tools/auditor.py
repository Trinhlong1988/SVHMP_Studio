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
import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
PY = sys.executable


def _run(rel):
    r = subprocess.run([PY, str(SVHMP / rel)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '')


def _git(args):
    return subprocess.run(['git', '-C', str(SVHMP)] + args, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.strip()


def architecture_auditor():
    code, out = _run('tools/architecture_registry_check.py')
    detail = 'registry PASS (0 MISSING/DUP/UNMAPPED)' if code == 0 else 'registry FAIL'
    return ('Architecture', code == 0, detail, code)


def contract_auditor():
    code, out = _run('tools/artifact_contract_check.py')
    return ('Contract', code == 0, 'DoD matrix — 0 phantom artifact' if code == 0 else 'phantom artifact khai != disk', code)


def qa_auditor():
    code, out = _run('tools/ci_gate.py')
    npass = out.count('[PASS]')
    return ('QA', code == 0, f'ci_gate {npass} checks PASS', code)


def publish_auditor():
    required = ['bible/37_character_schema.yaml', 'governance/architecture_registry.yaml',
                'governance/master_roadmap.md', 'governance/deprecation_report.md', 'VERSION.md']
    missing = [f for f in required if not (SVHMP / f).exists()]
    return ('Publish', not missing, 'artifacts OK' if not missing else f'MISSING {missing}', 0 if not missing else 1)


def _parse_version_ts(version_path=None):
    """last_update_ts trong VERSION.md (ISO-8601) hoac None."""
    p = Path(version_path) if version_path else (SVHMP / 'VERSION.md')
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        return None
    m = re.search(r'last_update_ts:\s*([0-9T:\-]+)', text)
    return m.group(1).strip() if m else None


def _max_released_at(claim_path=None):
    """released_at moi nhat trong build_claim.yaml (ISO-8601) hoac None."""
    p = Path(claim_path) if claim_path else (SVHMP / 'runtime' / 'build_claim.yaml')
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        return None
    ts = re.findall(r"released_at:\s*'?([0-9T:\-]+)'?", text)
    return max(ts) if ts else None


def version_freshness_advisory(version_path=None, claim_path=None):
    """ADVISORY (KHONG gate — khong dua vao decide()): VERSION.md phai duoc cap nhat
    it nhat ngang moc pack duoc release moi nhat. Bat bien tu chinh workflow
    (MASTER luat 11: release SAU khi push) — KHONG dung nguong tuy tien.
    R195: KHONG hard-gate tu baseline chua chuan -> advisory truoc, LEAD promote hard-gate sau.
    So sanh ISO-8601 cung dinh dang = so sanh thoi gian.
    Tra ('VersionFreshness', is_fresh, detail) — is_fresh=True khi khong du du lieu (skip)."""
    ver_ts = _parse_version_ts(version_path)
    rel_ts = _max_released_at(claim_path)
    if not ver_ts or not rel_ts:
        return ('VersionFreshness', True, 'khong du du lieu de danh gia (skip)')
    if ver_ts >= rel_ts:
        return ('VersionFreshness', True, f'VERSION.md ({ver_ts}) >= pack release moi nhat ({rel_ts})')
    return ('VersionFreshness', False,
            f'STALE: last_update_ts {ver_ts} < pack release moi nhat {rel_ts} -> can cap nhat VERSION.md')


def decide(results):
    """results: list[(name, ok, detail, code)] -> (verdict, exit_code).
    Enforce: BAT KY auditor FAIL -> BLOCK_SHIP.
    Fail-safe: KHONG co auditor nao chay -> BLOCK_SHIP (khong duoc mac dinh SHIP).
    Tach ra de test R209 chung thuc."""
    if not results:
        return ('BLOCK_SHIP', 1)
    fail = sum(1 for _, ok, _, _ in results if not ok)
    return ('SHIP', 0) if not fail else ('BLOCK_SHIP', 1)


def main():
    commit = _git(['rev-parse', 'HEAD'])
    branch = _git(['rev-parse', '--abbrev-ref', 'HEAD'])
    results = [architecture_auditor(), contract_auditor(), qa_auditor(), publish_auditor()]

    print("# INDEPENDENT AUDITOR REPORT")
    print("(Builder KHONG tu tuyen PASS — verdict do gate may nay phat ra)")
    print(f"Commit: {commit}")
    print(f"Branch: {branch}")
    print(f"Commands: architecture_registry_check.py + ci_gate.py + artifact check")
    print("PASS/FAIL matrix:")
    for name, ok, detail, code in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} Auditor — {detail} (exit {code})")
    adv_name, adv_ok, adv_detail = version_freshness_advisory()
    print(f"Advisory (KHONG gate — R195 promote sau): [{'OK' if adv_ok else 'STALE'}] {adv_name} — {adv_detail}")
    verdict, ec = decide(results)
    print(f"Final verdict: {verdict}")
    print(f"Exit code: {ec}")
    sys.exit(ec)


if __name__ == '__main__':
    main()
