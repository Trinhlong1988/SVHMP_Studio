"""Evidence Schema cho Cultural KB (SVAF backlog 4/5, CMD_BUILD_3 4/7): kiem tra
governance/proposals/cultural_kb_evidence_sample.yaml khop dung schema khai bao trong
governance/evidence_schema_cultural_kb.yaml — chong bia du lieu (hypothesis khong duoc
gan confidence, verified phai co source that)."""
from pathlib import Path

import yaml

SVHMP = Path(__file__).resolve().parent.parent
SCHEMA_FILE = SVHMP / 'governance' / 'evidence_schema_cultural_kb.yaml'
SAMPLE_FILE = SVHMP / 'governance' / 'proposals' / 'cultural_kb_evidence_sample.yaml'


def _load(p):
    return yaml.safe_load(p.read_text(encoding='utf-8'))


def test_schema_and_sample_parse():
    schema = _load(SCHEMA_FILE)
    sample = _load(SAMPLE_FILE)
    assert schema['schema']['status']['values'] == ['verified', 'hypothesis']
    assert sample['entries'], "sample rong"


def test_every_entry_has_evidence_block():
    sample = _load(SAMPLE_FILE)
    for e in sample['entries']:
        assert 'evidence' in e, f"{e.get('item_id')}: thieu block evidence"
        ev = e['evidence']
        for field in ('status', 'source', 'volume', 'page', 'confidence'):
            assert field in ev, f"{e['item_id']}: evidence thieu field '{field}'"


def test_status_values_valid():
    sample = _load(SAMPLE_FILE)
    for e in sample['entries']:
        assert e['evidence']['status'] in ('verified', 'hypothesis'), \
            f"{e['item_id']}: status la {e['evidence']['status']!r}"


def test_hypothesis_has_no_confidence():
    """Chong bia do tin cay cho thu con chua co nguon xac nhan."""
    sample = _load(SAMPLE_FILE)
    for e in sample['entries']:
        if e['evidence']['status'] == 'hypothesis':
            assert e['evidence']['confidence'] is None, \
                f"{e['item_id']}: hypothesis nhung lai co confidence (bia so)"


def test_verified_has_source_and_confidence():
    sample = _load(SAMPLE_FILE)
    for e in sample['entries']:
        if e['evidence']['status'] == 'verified':
            assert e['evidence']['source'], f"{e['item_id']}: verified nhung khong co source"
            conf = e['evidence']['confidence']
            assert conf is not None and 0.0 <= conf <= 1.0, \
                f"{e['item_id']}: verified confidence khong hop le ({conf})"


def test_item_id_unique():
    sample = _load(SAMPLE_FILE)
    ids = [e['item_id'] for e in sample['entries']]
    assert len(ids) == len(set(ids)), f"item_id trung: {ids}"
