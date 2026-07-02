"""PACK3 CI/CD governance-doc integrity (enterprise 18-doc, 2026-07-02).

PACK3 formalize ha tang CI/CD DA CO (ci_gate / githooks / conftest / auditor)
vao enterprise pack. Doc PHAI du 11-element (bar freeze-gate v1.0) + 0 placeholder.
Gate hoa -> chong doc thieu element / smuggle TBD nhu PACK2 tung bi.

pytest-func -> chay trong `pytest tests/` va ci_gate.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACK3 = REPO / 'governance' / 'pack3'

PACK3_DOCS = ['11_ci_pipeline.md', '12_git_hooks.md',
              '13_test_policy.md', '14_release_gate.md']

# 11 element bat buoc / doc (bar v1.0). Match nhan (case-insensit).
REQUIRED_ELEMENTS = ['mission', 'purpose', 'scope', 'authority', 'responsibilit',
                     'workflow', 'mandatory', 'pass', 'fail', 'promotion', 'example']


def test_all_pack3_docs_exist_nonempty():
    for name in PACK3_DOCS:
        p = PACK3 / name
        assert p.exists(), f'PACK3 doc missing: {name}'
        assert p.stat().st_size > 0, f'PACK3 doc empty: {name}'


def test_pack3_docs_have_11_elements():
    """Moi doc PACK3 PHAI co du 11 element enterprise template."""
    missing = {}
    for name in PACK3_DOCS:
        text = (PACK3 / name).read_text(encoding='utf-8').lower()
        gaps = [e for e in REQUIRED_ELEMENTS if e not in text]
        if gaps:
            missing[name] = gaps
    assert not missing, f'PACK3 docs thieu element: {missing}'


def test_pack3_docs_no_placeholder():
    """Governance integrity: khong TBD/TODO/FIXME/PLACEHOLDER/DRAFT marker."""
    bad = re.compile(r'TODO|FIXME|PLACEHOLDER|TBD|\bDRAFT\b')  # 'draft' lifecycle != DRAFT
    for name in PACK3_DOCS:
        text = (PACK3 / name).read_text(encoding='utf-8')
        assert not bad.search(text), f'{name} chua placeholder/draft marker'


def test_pack3_docs_reference_real_enforcers():
    """Moi doc phai tro toi enforcer THAT ton tai (chong doc mo coi built!=wired)."""
    enforcers = {
        '11_ci_pipeline.md': 'tools/ci_gate.py',
        '12_git_hooks.md': '.githooks/pre-commit',
        '13_test_policy.md': 'tests/conftest.py',
        '14_release_gate.md': 'tools/auditor.py',
    }
    for name, rel in enforcers.items():
        assert (REPO / rel).exists(), f'{name} enforcer thieu tren disk: {rel}'
        assert rel.split('/')[-1] in (PACK3 / name).read_text(encoding='utf-8'), \
            f'{name} khong reference enforcer {rel}'
