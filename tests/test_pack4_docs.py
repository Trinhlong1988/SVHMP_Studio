"""PACK4 template governance-doc integrity (enterprise 15-18, 2026-07-02).

PACK4 formalize "same code, khac project": project_config contract, episode
scaffold, ranh gioi shared-code vs per-project data, template governance.
Doc PHAI du 11-element (bar freeze-gate v1.0) + 0 placeholder + tro toi enforcer
THAT ton tai (chong doc mo coi built!=wired). Copy khuon test_pack3_docs.

pytest-func -> chay trong `pytest tests/` va ci_gate.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACK4 = REPO / 'governance' / 'pack4'

PACK4_DOCS = ['15_project_config.md', '16_episode_scaffold.md',
              '17_reuse_boundary.md', '18_template_governance.md']

# 11 element bat buoc / doc (bar v1.0). Match nhan (case-insensit).
REQUIRED_ELEMENTS = ['mission', 'purpose', 'scope', 'authority', 'responsibilit',
                     'workflow', 'mandatory', 'pass', 'fail', 'promotion', 'example']


def test_all_pack4_docs_exist_nonempty():
    for name in PACK4_DOCS:
        p = PACK4 / name
        assert p.exists(), f'PACK4 doc missing: {name}'
        assert p.stat().st_size > 0, f'PACK4 doc empty: {name}'


def test_pack4_docs_have_11_elements():
    """Moi doc PACK4 PHAI co du 11 element enterprise template."""
    missing = {}
    for name in PACK4_DOCS:
        text = (PACK4 / name).read_text(encoding='utf-8').lower()
        gaps = [e for e in REQUIRED_ELEMENTS if e not in text]
        if gaps:
            missing[name] = gaps
    assert not missing, f'PACK4 docs thieu element: {missing}'


def test_pack4_docs_no_placeholder():
    """Governance integrity: khong TBD/TODO/FIXME/PLACEHOLDER/DRAFT marker."""
    bad = re.compile(r'TODO|FIXME|PLACEHOLDER|TBD|\bDRAFT\b')  # 'draft' lifecycle != DRAFT
    for name in PACK4_DOCS:
        text = (PACK4 / name).read_text(encoding='utf-8')
        assert not bad.search(text), f'{name} chua placeholder/draft marker'


def test_pack4_docs_reference_real_enforcers():
    """Moi doc phai tro toi enforcer THAT ton tai (chong doc mo coi built!=wired)."""
    enforcers = {
        '15_project_config.md': 'tools/validate_project_config.py',
        '16_episode_scaffold.md': 'prompts/ep_scaffold_template.md',
        '17_reuse_boundary.md': 'tools/detect_template_repetition.py',
        '18_template_governance.md': 'tools/vary_templates.py',
    }
    for name, rel in enforcers.items():
        assert (REPO / rel).exists(), f'{name} enforcer thieu tren disk: {rel}'
        doc_text = (PACK4 / name).read_text(encoding='utf-8')
        basename = rel.split('/')[-1]
        assert basename in doc_text, f'{name} khong reference enforcer {rel}'
