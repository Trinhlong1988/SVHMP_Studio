"""PACK5 quality governance-doc integrity (enterprise 19-22, 2026-07-02).

PACK5 formalize ha tang content/audio-QA DA CO THAT: render-time pipeline (19),
golden dataset + calibration R195 (20), detector suite R188-R191 (21),
waiver R204 + watch daemon (22). Doc PHAI du 11-element (bar freeze-gate v1.0)
+ 0 placeholder + tro toi enforcer THAT ton tai (chong doc mo coi built!=wired).
Copy khuon test_pack4_docs.

pytest-func -> chay trong `pytest tests/` va ci_gate.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACK5 = REPO / 'governance' / 'pack5'

PACK5_DOCS = ['19_qa_pipeline.md', '20_golden_dataset.md',
              '21_detector_suite.md', '22_waiver_watch.md']

# 11 element bat buoc / doc (bar v1.0). Match nhan (case-insensit).
REQUIRED_ELEMENTS = ['mission', 'purpose', 'scope', 'authority', 'responsibilit',
                     'workflow', 'mandatory', 'pass', 'fail', 'promotion', 'example']


def test_all_pack5_docs_exist_nonempty():
    for name in PACK5_DOCS:
        p = PACK5 / name
        assert p.exists(), f'PACK5 doc missing: {name}'
        assert p.stat().st_size > 0, f'PACK5 doc empty: {name}'


def test_pack5_docs_have_11_elements():
    """Moi doc PACK5 PHAI co du 11 element enterprise template."""
    missing = {}
    for name in PACK5_DOCS:
        text = (PACK5 / name).read_text(encoding='utf-8').lower()
        gaps = [e for e in REQUIRED_ELEMENTS if e not in text]
        if gaps:
            missing[name] = gaps
    assert not missing, f'PACK5 docs thieu element: {missing}'


def test_pack5_docs_no_placeholder():
    """Governance integrity: khong TODO/FIXME/PLACEHOLDER/TBD/DRAFT marker."""
    bad = re.compile(r'TODO|FIXME|PLACEHOLDER|TBD|\bDRAFT\b')  # 'draft' lifecycle != DRAFT
    for name in PACK5_DOCS:
        text = (PACK5 / name).read_text(encoding='utf-8')
        assert not bad.search(text), f'{name} chua placeholder/draft marker'


def test_pack5_docs_reference_real_enforcers():
    """Moi doc phai tro toi enforcer THAT ton tai (chong doc mo coi built!=wired)."""
    enforcers = {
        '19_qa_pipeline.md': 'tools/svhmp_preflight_qa.py',
        '20_golden_dataset.md': 'tools/hardcode_classifier.py',
        '21_detector_suite.md': 'tools/qa_prosody_collapse.py',
        '22_waiver_watch.md': 'tools/qa_watch_supervisor.py',
    }
    for name, rel in enforcers.items():
        assert (REPO / rel).exists(), f'{name} enforcer thieu tren disk: {rel}'
        doc_text = (PACK5 / name).read_text(encoding='utf-8')
        basename = rel.split('/')[-1]
        assert basename in doc_text, f'{name} khong reference enforcer {rel}'
