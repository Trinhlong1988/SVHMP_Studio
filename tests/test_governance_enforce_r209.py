"""R209 — CHUNG THUC governance enforce (PACK1, Boss 2/7).
Chung minh: Independent Auditor BLOCK khi bat ky gate FAIL (khong the tu tuyen PASS).
pytest-native -> `pytest -q` chay truc tiep.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import auditor  # noqa: E402

PASS = ('X', True, 'ok', 0)
FAIL = ('Y', False, 'bad', 1)


def test_all_pass_ships():
    assert auditor.decide([PASS, PASS, PASS]) == ('SHIP', 0)


def test_one_fail_blocks():
    # ca AM: chi 1 gate do -> PHAI BLOCK (chong tu tuyen PASS)
    assert auditor.decide([PASS, FAIL, PASS]) == ('BLOCK_SHIP', 1)


def test_all_fail_blocks():
    assert auditor.decide([FAIL, FAIL, FAIL]) == ('BLOCK_SHIP', 1)


def test_empty_blocks():
    # fail-safe: khong co auditor nao chay -> PHAI BLOCK (khong mac dinh SHIP)
    assert auditor.decide([]) == ('BLOCK_SHIP', 1)


def test_live_architecture_and_publish_healthy():
    a = auditor.architecture_auditor()
    p = auditor.publish_auditor()
    assert len(a) == 4 and len(p) == 4
    assert a[1] is True, f"architecture unhealthy: {a}"
    assert p[1] is True, f"publish artifacts missing: {p}"
