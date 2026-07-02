"""PACK1 — Builder Hard Gate Constitution v2 hard-rules LOCK.

Chan viec silently gut hien phap: 05_builder_hard_gate.md PHAI con giu cac hard
MUST-NOT (cam Builder tuyen PASS/FREEZE/SHIP, cam doi promotion_status->locked,
cam tao release tag, cam rewrite history, enforcement Governance-wins). Precedent
2/7: executor2 tu freeze PACK2 -> doc + test nay chan tai dien.

pytest-func -> chay trong `pytest tests/` va ci_gate.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC = REPO / 'governance' / 'constitution' / '05_builder_hard_gate.md'


def _text():
    assert DOC.exists(), '05_builder_hard_gate.md missing'
    return DOC.read_text(encoding='utf-8')


def test_doc_exists_nonempty():
    assert DOC.exists() and DOC.stat().st_size > 0


def test_hard_must_not_rules_present():
    t = _text().lower()
    required = [
        'pass', 'freeze', 'ship',      # output ban PASS/FREEZE/SHIP
        'promotion_status',            # cam Builder doi ->locked
        'release tag',                 # cam tao tag
        'rewrite history',             # cam rewrite history giau loi
        'report conflict',             # enforcement Governance-wins
    ]
    missing = [r for r in required if r not in t]
    assert not missing, f'05_builder_hard_gate.md mat hard-rule: {missing}'


def test_only_independent_auditor_certifies():
    """Doc phai con khang dinh chi independent auditor/owner moi FREEZE/PASS."""
    t = _text().lower()
    assert 'independent auditor' in t
