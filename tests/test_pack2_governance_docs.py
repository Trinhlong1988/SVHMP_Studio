"""PACK2 governance-doc integrity (enterprise audit remediation 2/7).

Dong 2 lo hong enterprise-audit tim ra:
  1. Decision-matrix doc <-> auditor.decide() DRIFT: doc mo ta bang PASS/FAIL
     nhung khong test nao assert impl khop doc -> doc co the stale am tham.
  2. PACK2 doc thieu 11-element enterprise template (Mission/Purpose/Scope/
     Authority/Responsibilities/Workflow/Mandatory/PASS/FAIL/Promotion/Examples).

pytest-func -> chay trong `pytest tests/` va ci_gate.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACK2 = REPO / 'governance' / 'pack2'
sys.path.insert(0, str(REPO / 'tools'))
from auditor import decide  # noqa: E402

PACK2_DOCS = ['05_decision_matrix.md', '06_severity_matrix.md',
              '07_evidence_standard.md', '08_artifact_contract.md',
              '09_review_workflow.md', '10_exception_policy.md']

# 11 element bat buoc / doc (enterprise freeze-gate v1.0). Match nhan (case-insensit).
REQUIRED_ELEMENTS = ['mission', 'purpose', 'scope', 'authority', 'responsibilit',
                     'workflow', 'mandatory', 'pass', 'fail', 'promotion', 'example']


# ---------- (1) DECISION MATRIX <-> IMPL DRIFT GUARD ----------

def test_decision_matrix_matches_auditor_decide():
    """05_decision_matrix.md khai: all PASS->SHIP/0, >=1 FAIL->BLOCK_SHIP/1,
    khong auditor->BLOCK_SHIP/1. Assert auditor.decide() SINH DUNG 3 hang do
    (neu decide() doi hanh vi ma doc khong doi -> test DO -> bat drift)."""
    doc = (PACK2 / '05_decision_matrix.md').read_text(encoding='utf-8')
    # doc phai con khai ca SHIP lan BLOCK_SHIP voi exit 0/1
    assert 'SHIP' in doc and 'BLOCK_SHIP' in doc
    assert re.search(r'SHIP\D+0', doc) and re.search(r'BLOCK_SHIP\D+1', doc)
    # impl khop tung hang cua bang
    assert decide([('A', True, '', 0)]) == ('SHIP', 0)            # all PASS
    assert decide([('A', True, '', 0),
                   ('B', False, '', 1)]) == ('BLOCK_SHIP', 1)     # >=1 FAIL
    assert decide([]) == ('BLOCK_SHIP', 1)                        # fail-safe


def test_decide_never_defaults_ship_on_empty():
    """Fail-safe cot loi: khong auditor nao chay KHONG duoc mac dinh SHIP."""
    verdict, ec = decide([])
    assert verdict == 'BLOCK_SHIP' and ec == 1


# ---------- (2) PACK2 DOC 11-ELEMENT COMPLETENESS ----------

def test_all_pack2_docs_exist_nonempty():
    for name in PACK2_DOCS:
        p = PACK2 / name
        assert p.exists(), f'PACK2 doc missing: {name}'
        assert p.stat().st_size > 0, f'PACK2 doc empty: {name}'


def test_pack2_docs_have_11_elements():
    """Moi doc PACK2 PHAI co du 11 element enterprise template (Phase 3 freeze-gate v1.0)."""
    missing = {}
    for name in PACK2_DOCS:
        text = (PACK2 / name).read_text(encoding='utf-8').lower()
        gaps = [e for e in REQUIRED_ELEMENTS if e not in text]
        if gaps:
            missing[name] = gaps
    assert not missing, f'PACK2 docs thieu element: {missing}'


def test_pack2_docs_no_placeholder():
    """Governance integrity: khong TODO/FIXME/PLACEHOLDER/DRAFT marker."""
    bad = re.compile(r'TODO|FIXME|PLACEHOLDER|TBD|\bDRAFT\b')  # v1.0: +TBD; 'draft' lifecycle != DRAFT
    for name in PACK2_DOCS:
        text = (PACK2 / name).read_text(encoding='utf-8')
        assert not bad.search(text), f'{name} chua placeholder/draft marker'
