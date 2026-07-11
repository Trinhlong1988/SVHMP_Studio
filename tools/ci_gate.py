"""SVHMP — CI GATE (Boss 2/7): bat buoc chay TRUOC push (git pre-push hook goi).
Chay registry check + regression test lõi. FAIL bat ky -> exit 1 -> chan push.
"""
import os
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
PY = sys.executable

# Re-entrancy guard: the pytest suite (tests/) contains R213 which runs auditor.py,
# which runs ci_gate.py again. Without this guard the pytest step below would recurse
# infinitely (ci_gate -> pytest -> R213 -> auditor -> ci_gate -> pytest -> ...).
# We only launch pytest at the OUTERMOST ci_gate; nested invocations skip it.
_PYTEST_GUARD = 'SVHMP_CI_GATE_PYTEST_RUNNING'

CHECKS = [
    ('registry',  'tools/architecture_registry_check.py'),
    ('blueprint', 'tools/blueprint_suite_check.py'),   # BP5: 1 cua BP0-BP4 (unwire = test_bp5 do)
    ('R199_tail', 'tests/test_tail_pathology_r199.py'),
    ('R203_conf', 'tests/test_qa_confusion_200_r203.py'),
    ('R205_char', 'tests/test_character_manager_r205.py'),
    ('R206_voice', 'tests/test_character_system_1000_r206.py'),
    ('R207_canon', 'tests/test_story_consistency_1000_r207.py'),
    ('R208_age',  'tests/test_dialogue_appropriateness_1000_r208.py'),
    ('G3_dialogue', 'tools/g3_dialogue_check.py'),   # G3 (TASK_G3_DIALOGUE.md D7): generator + 3 validator smoke + D5 confusion, 1 cua
    ('project_config', 'tools/validate_project_config.py'),   # PACK4/15: hop dong project_config (scan repo)
    ('G2_roster',  'tools/roster_validator.py'),   # G2 B4: naming bible/23 + que<->giong R210 (WARN mode; --strict sau khi fill dat nguong Tier1 100%)
    ('g5_supernatural', 'tools/g5_supernatural_check.py'),   # G5: typology + possession SM cau truc (KHONG quet noi dung episode - do la G8)
    ('G4_world',  'tools/g4_world_check.py'),   # G4: timeline+event_ledger+story_consistency 1-cua (D1/D2/D3/D4)
    ('G6_story_planner', 'tools/g6_story_planner_check.py'),   # G6a: decision_policy_check + decision_engine packet self-check (G6b chua build)
    ('G7_generator', 'tools/g7_generator_check.py'),   # G7 D4: episode_generator pytest + self-check + budget_sheet M4 + no-write-domain + static no-write
    ('G8_qa_runtime', 'tools/g8_qa_runtime_check.py'),   # G8 D7: reconcile invariant qa_runtime (D2 domain + D4 pack5/19 + VNQA H1-H10 + DEBT-005 golden_lock) — static-check, khong pytest
]

# WARN-ONLY (R210/DEBT-026, Mr.Long 11/7): surface roster imbalance canh bao KHONG chan push.
# character_balance_report.py CO CHU DICH khong co sys.exit (la report tool, khong phai gate) —
# ta chay + hien "FLAG LECH CAN BANG" nhung KHONG BAO GIO cong vao `fail`. Quyet WARN-only vi
# KHONG rebalance 139 nguoi da khoa (mirror DEBT-021 — khong dung du lieu nhan vat LOCKED).
# CAM chuyen vao CHECKS (se thanh blocking) khi roster chua can bang lai — se chan moi push.
WARN_CHECKS = [
    ('char_balance', 'tools/character_balance_report.py'),
]

# Error Code Standard (SVAF backlog 2/5, governance/error_code_standard.yaml) — chi
# THEM 1 bracket rieng cuoi dong hien thi, KHONG dung vao [PASS]/[FAIL] goc (bi
# tools/auditor.py dem chuoi cung out.count('[PASS]')).
STAGE_CODES = {
    'registry': 'REG2000', 'blueprint': 'ART4001', 'R199_tail': 'QA1010',
    'R203_conf': 'QA1011', 'R205_char': 'QA1012', 'R206_voice': 'QA1013',
    'R207_canon': 'QA1014', 'R208_age': 'QA1015', 'G3_dialogue': 'QA1016', 'project_config': 'ART4002',
    'G2_roster': 'QA1001', 'pytest_suite': 'QA1099', 'g5_supernatural': 'ONT5001',
    'G4_world': 'ONT4001', 'G6_story_planner': 'ONT6001', 'G7_generator': 'ONT7001',
    'G8_qa_runtime': 'ONT8001',
}


def extract_warn_flags(output):
    """Trich cac dong canh bao (⚠ / FLAG LECH) tu stdout 1 WARN-only tool.
    Tach rieng (pure fn) de test mutation-proof khong phu thuoc roster live."""
    return [ln.strip() for ln in (output or '').splitlines()
            if '⚠' in ln or 'FLAG LECH' in ln]


def run_warn_checks():
    """Chay cac WARN_CHECKS. Tra ve list[(name, flag_lines)]. TUYET DOI khong sys.exit /
    khong tra ve fail-count — WARN-only theo DEBT-026 (canh bao lech can bang, khong chan push)."""
    results = []
    for name, rel in WARN_CHECKS:
        r = subprocess.run([PY, str(SVHMP / rel)], capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        results.append((name, extract_warn_flags(r.stdout)))
    return results


def _pytest_summary(out):
    """Trich dong tom tat cuoi cua pytest (vd '32 passed in 27s') de lam evidence."""
    for line in reversed((out or '').strip().splitlines()):
        if 'passed' in line or 'failed' in line or 'error' in line:
            return line.strip()
    return '(no pytest summary)'


def main():
    fail = 0
    print("=== CI GATE ===")
    for name, rel in CHECKS:
        # encoding utf-8 + errors replace: script con in tieng Viet (UTF-8); mac dinh text=True
        # decode bang locale Windows (cp1252) -> UnicodeDecodeError trong reader thread (bay ENVIRONMENT_GOTCHAS 9/7).
        r = subprocess.run([PY, str(SVHMP / rel)], capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        ok = r.returncode == 0
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} (exit {r.returncode}) [{STAGE_CODES.get(name, '?')}]")
        if not ok:
            fail += 1
            print((r.stdout or '')[-400:])
            print((r.stderr or '')[-200:])
    # WARN-only (DEBT-026): hien canh bao lech can bang roster, KHONG cong vao `fail`.
    for name, flags in run_warn_checks():
        print(f"  [WARN] {name} (WARN-only, khong chan push): {len(flags)} canh bao [ONT2100]")
        for f in flags:
            print(f"        {f}")

    # Constitution 03_qa_auditor.md: PASS = "ci_gate exit 0, pytest all pass";
    # scope bao gom governance enforce R209/R212/R213/R214 (pytest-func tests).
    # Chay ca pytest suite (tests/) de dong khe ho: script-style tests o tren KHONG
    # phu R209/R212/R213/R214 va cac case pytest-func khac.
    if os.environ.get(_PYTEST_GUARD):
        # Nested ci_gate (goi tu pytest R213 -> auditor). Bo qua de tranh de quy vo han;
        # pytest tang ngoai cung da/dang enforce toan bo suite.
        print("  [SKIP] pytest_suite (re-entrant: da o trong pytest do ci_gate khoi chay)")
    else:
        # SU CO 2/7: ci_gate chay TRONG git hook -> git export GIT_DIR/GIT_INDEX_FILE/
        # GIT_WORK_TREE tro ve repo that -> fixture 'git commit' cua test trong tmp_path
        # van danh vao repo that (origin bi wipe 1037 file). Scrub GIT_* cho pytest.
        env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        env[_PYTEST_GUARD] = '1'
        env.setdefault('PYTHONUTF8', '1')   # ep con (pytest) emit UTF-8 on dinh tren Windows
        pt = subprocess.run([PY, '-m', 'pytest', 'tests/', '-q'],
                            capture_output=True, text=True, encoding='utf-8', errors='replace',
                            cwd=str(SVHMP), env=env)
        pt_ok = pt.returncode == 0
        summary = _pytest_summary(pt.stdout)
        print(f"  [{'PASS' if pt_ok else 'FAIL'}] pytest_suite (exit {pt.returncode}) — {summary} "
              f"[{STAGE_CODES['pytest_suite']}]")
        if not pt_ok:
            fail += 1
            print((pt.stdout or '')[-600:])
            print((pt.stderr or '')[-200:])
    print(f"=== CI GATE: {'PASS ✅' if not fail else f'FAIL ❌ ({fail})'} ===")
    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
