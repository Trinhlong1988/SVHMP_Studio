"""R213 — CHUNG THUC Evidence Standard gate CHAN report thieu bang chung (PACK2 07).
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import evidence_check as ev  # noqa: E402

SVHMP = Path(__file__).resolve().parent.parent
PY = sys.executable

GOOD = """Commit: 08a53e8abc
Branch: main
Commands: architecture_registry_check.py
PASS/FAIL matrix:
  [PASS] Architecture
Final verdict: SHIP
Exit code: 0
"""


def test_full_report_passes():
    assert ev.missing_fields(GOOD) == []


def test_missing_exit_is_blocked():
    # ca AM: bo 'Exit code' + 'SHIP/verdict' -> phai bi bat
    bad = "Commit: abc1234\nBranch: main\nCommands: x\n[PASS] y\n"
    miss = ev.missing_fields(bad)
    assert 'exit_code' in miss and 'verdict' in miss


def test_empty_report_all_missing():
    miss = ev.missing_fields("")
    assert set(miss) == set(ev.REQUIRED)


def test_live_auditor_output_has_evidence():
    # auditor that ra report -> phai du bang chung
    r = subprocess.run([PY, str(SVHMP / 'tools' / 'auditor.py')], capture_output=True, text=True)
    assert ev.missing_fields(r.stdout) == [], f"auditor output thieu: {ev.missing_fields(r.stdout)}"
