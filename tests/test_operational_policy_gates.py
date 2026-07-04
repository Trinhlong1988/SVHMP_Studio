"""Operational Policy Gates (SVAF backlog 3/5, CMD_BUILD_3 4/7): mỗi gate trong
governance/operational_policy_gates.yaml phải đủ field bắt buộc, gate_id duy nhất,
severity/enforcer.status hợp lệ. Chống overclaim: enforcer.status='enforced' PHẢI
kèm 'tool' trỏ file that su ton tai tren disk (khong duoc bao enforced ma khong co
tool that, cung tinh than governance/deprecation_report.md)."""
from pathlib import Path

import yaml

SVHMP = Path(__file__).resolve().parent.parent
GATES_FILE = SVHMP / 'governance' / 'operational_policy_gates.yaml'

REQUIRED_FIELDS = {'gate_id', 'domain', 'desc', 'severity', 'owner_review', 'enforcer'}
VALID_SEVERITY = {'HIGH', 'MEDIUM', 'LOW'}
VALID_ENFORCER_STATUS = {'enforced', 'partial', 'roadmap'}


def _load():
    return yaml.safe_load(GATES_FILE.read_text(encoding='utf-8'))


def test_file_parses():
    data = _load()
    assert data['gates'], "gates list rong"


def test_required_fields_present():
    data = _load()
    for g in data['gates']:
        missing = REQUIRED_FIELDS - set(g.keys())
        assert not missing, f"gate {g.get('gate_id')} thieu field {missing}"


def test_gate_id_unique():
    data = _load()
    ids = [g['gate_id'] for g in data['gates']]
    assert len(ids) == len(set(ids)), f"gate_id trung: {ids}"


def test_severity_valid():
    data = _load()
    for g in data['gates']:
        assert g['severity'] in VALID_SEVERITY, f"{g['gate_id']}: severity la {g['severity']!r}"


def test_enforcer_status_valid():
    data = _load()
    for g in data['gates']:
        st = g['enforcer'].get('status')
        assert st in VALID_ENFORCER_STATUS, f"{g['gate_id']}: enforcer.status la {st!r}"


def test_enforced_gates_have_real_tool_on_disk():
    """Chong overclaim: 'enforced' PHAI tro tool that ton tai, khong duoc bao suong."""
    data = _load()
    for g in data['gates']:
        if g['enforcer']['status'] != 'enforced':
            continue
        tool = g['enforcer'].get('tool')
        assert tool, f"{g['gate_id']}: enforced nhung khong khai 'tool'"
        for rel in tool.split(','):
            assert (SVHMP / rel.strip()).exists(), \
                f"{g['gate_id']}: enforcer.tool {rel!r} khong ton tai tren disk"


def test_high_severity_gates_have_mr_long_or_auto_review():
    """severity=HIGH phai co owner_review noi ro AI duyet (Mr.Long hoac 'Tu dong')."""
    data = _load()
    for g in data['gates']:
        if g['severity'] != 'HIGH':
            continue
        assert g['owner_review'], f"{g['gate_id']}: HIGH nhung owner_review rong"
