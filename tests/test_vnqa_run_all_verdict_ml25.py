"""audit ML #25 (10/7) — VNQA H1-H10: G8 gate check_vnqa_h1_h10() chi regex-verify ham h1..h10
duoc dinh nghia+goi (text-grep), KHONG kiem logic tong hop verdict (critical->FAIL, warning->WARN,
sach->PASS). 0 test truoc do khoi tao VietnameseQAChecker/goi run_all(). Test nay:
(1) chay run_all() THAT tren text thuc - end-to-end execution;
(2) doi chieu VERDICT AGGREGATION bang cach neutralize 10 h-method + inject severity (mirror D9
    test_supernatural_run_all_composition.py): critical->FAIL, warning->WARN, sach->PASS.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from vnqa.pipeline import VietnameseQAChecker

H_METHODS = [
    'h1_underthesea_pos_rhythm', 'h2_vietnamese_dict_existence', 'h3_phobert_collocation_skeleton',
    'h4_idiom_detection', 'h5_formality_journalistic', 'h6_phonlp_dependency_skeleton',
    'h7_ngram_anomaly', 'h8_collocation_lexicon', 'h9_stop_consonant_tail', 'h10_duration_range',
]


def _verdict_with(monkeypatch, severities):
    c = VietnameseQAChecker("van ban mau test ML25", ep_number=1)
    for h in H_METHODS:
        monkeypatch.setattr(c, h, lambda: None)   # neutralize: khong sinh issue that
    if severities:
        def inject():
            for s in severities:
                c._flag('TEST_ML25', s, 'evidence gia lap')
        monkeypatch.setattr(c, H_METHODS[0], inject)
    return c.run_all()['verdict']


def test_run_all_executes_end_to_end_on_real_text():
    c = VietnameseQAChecker("Đêm đó trời mưa rất to. Cô ấy đứng đợi ở bến xe cũ.", ep_number=1)
    report = c.run_all()
    assert report['verdict'] in ('PASS', 'WARN', 'FAIL')
    assert report['phase_h_version'] == 'H1-H10 v1.1'   # khop audit ML #26


def test_verdict_clean_is_pass(monkeypatch):
    assert _verdict_with(monkeypatch, []) == 'PASS'


def test_verdict_critical_is_fail(monkeypatch):
    assert _verdict_with(monkeypatch, ['critical']) == 'FAIL'


def test_verdict_single_warning_is_warn(monkeypatch):
    assert _verdict_with(monkeypatch, ['warning']) == 'WARN'


def test_verdict_five_warnings_is_warn(monkeypatch):
    assert _verdict_with(monkeypatch, ['warning'] * 5) == 'WARN'


def test_verdict_critical_dominates_warnings(monkeypatch):
    # critical + warning van FAIL (critical uu tien)
    assert _verdict_with(monkeypatch, ['warning', 'critical', 'warning']) == 'FAIL'
