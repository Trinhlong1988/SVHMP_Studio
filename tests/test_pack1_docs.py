"""PACK1 constitution governance-doc integrity (enterprise 00-05, 2026-07-02).

Khuon test_pack4_docs: exist+nonempty · 11-element enterprise template ·
0 placeholder · reference enforcer THAT ton tai (chong doc mo coi built!=wired).

pytest-func -> chay trong `pytest tests/` va ci_gate.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACK1 = REPO / 'governance' / 'constitution'

PACK1_DOCS = ['00_constitution.md', '01_builder.md', '02_architecture_auditor.md',
              '03_qa_auditor.md', '04_publish_auditor.md', '05_builder_hard_gate.md']

# 11 element bat buoc / doc (bar v1.0). Match nhan (case-insensit).
REQUIRED_ELEMENTS = ['mission', 'purpose', 'scope', 'authority', 'responsibilit',
                     'workflow', 'mandatory', 'pass', 'fail', 'promotion', 'example']


def test_all_pack1_docs_exist_nonempty():
    for name in PACK1_DOCS:
        p = PACK1 / name
        assert p.exists(), f'PACK1 doc missing: {name}'
        assert p.stat().st_size > 0, f'PACK1 doc empty: {name}'


def test_pack1_docs_have_11_elements():
    """Moi doc PACK1 PHAI co du 11 element enterprise template."""
    missing = {}
    for name in PACK1_DOCS:
        text = (PACK1 / name).read_text(encoding='utf-8').lower()
        gaps = [e for e in REQUIRED_ELEMENTS if e not in text]
        if gaps:
            missing[name] = gaps
    assert not missing, f'PACK1 docs thieu element: {missing}'


def test_pack1_docs_no_placeholder():
    """Governance integrity: khong TBD/TODO/FIXME/PLACEHOLDER/DRAFT marker."""
    bad = re.compile(r'TODO|FIXME|PLACEHOLDER|TBD|\bDRAFT\b')  # 'draft' lifecycle != DRAFT
    for name in PACK1_DOCS:
        text = (PACK1 / name).read_text(encoding='utf-8')
        assert not bad.search(text), f'{name} chua placeholder/draft marker'


def test_pack1_docs_reference_real_enforcers():
    """Moi doc phai tro toi enforcer THAT ton tai (chong doc mo coi built!=wired)."""
    enforcers = {
        '00_constitution.md': 'tools/auditor.py',
        '01_builder.md': 'tools/ci_gate.py',
        '02_architecture_auditor.md': 'tools/architecture_registry_check.py',
        '03_qa_auditor.md': 'tools/ci_gate.py',
        '04_publish_auditor.md': 'tools/auditor.py',
        '05_builder_hard_gate.md': 'tests/test_builder_hard_gate.py',
    }
    for name, rel in enforcers.items():
        assert (REPO / rel).exists(), f'{name} enforcer thieu tren disk: {rel}'
        doc_text = (PACK1 / name).read_text(encoding='utf-8')
        basename = rel.split('/')[-1]
        assert basename in doc_text, f'{name} khong reference enforcer {rel}'
