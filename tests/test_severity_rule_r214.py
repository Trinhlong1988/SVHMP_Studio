"""R214 — CHUNG THUC Severity rule: CHI Critical chan (PACK2 06).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import severity_gate as sg  # noqa: E402


def test_critical_blocks():
    # ca AM: co Critical -> PHAI BLOCK
    assert sg.gate([{'severity': 'Critical'}]) == ('BLOCK', 1)


def test_critical_among_others_blocks():
    assert sg.gate([{'severity': 'Info'}, {'severity': 'Critical'}, {'severity': 'Minor'}]) == ('BLOCK', 1)


def test_major_minor_info_pass():
    # khong Critical -> khong tu chan (chong spam chan)
    assert sg.gate([{'severity': 'Major'}, {'severity': 'Minor'}, {'severity': 'Info'}]) == ('PASS', 0)


def test_empty_pass():
    assert sg.gate([]) == ('PASS', 0)


def test_string_findings_supported():
    assert sg.gate(['Critical']) == ('BLOCK', 1)
    assert sg.gate(['Minor']) == ('PASS', 0)


def test_invalid_severity_raises():
    try:
        sg.gate([{'severity': 'Bogus'}])
        assert False, "phai raise ValueError"
    except ValueError:
        pass
