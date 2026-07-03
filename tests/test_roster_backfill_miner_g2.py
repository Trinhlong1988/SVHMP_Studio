"""G2 B2 — roster_backfill_miner: máy đào trích ĐÚNG + negative test cắn.

Fixture episode tự dựng trong tmp_path (KHÔNG đụng output/ thật). Mỗi test
assert kết quả CỤ THỂ (bài học 3/7: negative test phải chứng minh nó cắn —
call-site >=1, không pass-rỗng).

pytest-func -> tự động collect trong `pytest tests/` và ci_gate.
"""
import sys
from pathlib import Path

import yaml

SVHMP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SVHMP / 'tools'))
from roster_backfill_miner import (  # noqa: E402
    mine, parse_passenger_main, check_name_bible23)


def _make_ep(root, n, header_lines, body):
    d = root / f'ep_{n:02d}'
    d.mkdir(parents=True)
    content = '\n'.join(['# TẬP TEST', '', '```'] + header_lines + ['```', ''] + body)
    (d / 'episode.md').write_text(content, encoding='utf-8')


def _roster(tmp, passengers):
    f = tmp / 'roster.yaml'
    f.write_text(yaml.safe_dump({'passengers': passengers}, allow_unicode=True),
                 encoding='utf-8')
    return f


PAS = {'id': 'PAS_9001', 'char_name': 'Thục Đoan', 'assigned_ep': 2}
PAS2 = {'id': 'PAS_9002', 'char_name': 'Kiên Bách', 'assigned_ep': 3}


# ---------- POSITIVE: trích đúng ----------

def test_pas_header_mined_with_speech_and_knowledge(tmp_path):
    out = tmp_path / 'output'
    _make_ep(out, 2, ['passenger_main : PAS_9001 (Thục Đoan, nu 26-35)'],
             ['Thục Đoan ngồi im.', '"Tôi chưa từng kể ai chuyện này."', ''])
    r = mine(output_root=out, roster_path=_roster(tmp_path, [PAS]))
    entry = r['characters']['PAS_9001']
    assert entry['appearances'][0] == {'ep': 2, 'source': 'header_passenger_main'}
    assert len(entry['speech_evidence']) == 1
    assert entry['speech_evidence'][0]['speaker'] == 'UNATTRIBUTED_can_nguoi_duyet'
    assert len(entry['knowledge_candidates']) >= 1          # marker 'chưa từng kể'
    assert 'biet_bi_mat' in entry['continuity_risk']['flags']
    assert entry['status'] == 'draft'


def test_freeform_header_parsed_low_confidence():
    pas_id, info = parse_passenger_main('nu 36 Vy An Long Biên (chia tay anh Khôi)')
    assert pas_id is None
    assert info['name_guess'] == 'Vy An'
    assert info['hometown_guess'] == 'Long Biên'
    assert info['parse_confidence'] == 'low'


def test_malformed_header_no_fake_name():
    """Header dị dạng -> KHÔNG đoán bừa tên (nguyên lý không bịa)."""
    _, info = parse_passenger_main('nu_45 → nam 26 Đức Hà Đông (em chị mất)')
    assert info['name_guess'] is None
    assert 'needs_human' in info


# ---------- NEGATIVE: findings phải cắn ----------

def test_roster_drift_flagged(tmp_path):
    out = tmp_path / 'output'
    _make_ep(out, 11, ['passenger_main: nu 36 Vy An Long Biên (test)'], ['Nội dung.'])
    r = mine(output_root=out, roster_path=_roster(tmp_path, [PAS]))
    drift = r['findings']['F1_roster_drift']
    assert len(drift) == 1 and 'ep_11' in drift[0]
    un = r['unmatched_episode_characters']
    assert len(un) == 1
    assert un[0]['continuity_risk']['flags'] == ['roster_drift_no_pas_id']
    assert un[0]['continuity_risk']['level'] == 'high'


def test_assigned_ep_mismatch_flagged(tmp_path):
    out = tmp_path / 'output'
    _make_ep(out, 5, ['passenger_main : PAS_9001 (Thục Đoan, nu 26-35)'], ['X.'])
    r = mine(output_root=out, roster_path=_roster(tmp_path, [PAS]))  # assigned_ep=2
    mm = r['findings']['F2_assigned_ep_mismatch']
    assert len(mm) == 1 and 'PAS_9001' in mm[0] and 'ep 2' in mm[0]


def test_cross_episode_reappearance_flagged(tmp_path):
    """One-shot bible/03: tên roster xuất hiện ngoài tập gán -> F3 + flag high."""
    out = tmp_path / 'output'
    _make_ep(out, 2, ['passenger_main : PAS_9001 (Thục Đoan, nu 26-35)'], ['A.'])
    _make_ep(out, 3, ['passenger_main : PAS_9002 (Kiên Bách, nam 36-50)'],
             ['Thục Đoan bước lên xe lần nữa.'])
    r = mine(output_root=out, roster_path=_roster(tmp_path, [PAS, PAS2]))
    f3 = r['findings']['F3_cross_episode_appearance']
    assert len(f3) == 1 and 'Thục Đoan' in f3[0] and 'ep_03' in f3[0]
    cr = r['characters']['PAS_9001']['continuity_risk']
    assert 'recurring_cross_ep' in cr['flags'] and cr['level'] == 'high'
    assert cr['evidence']                        # kèm ep:line, không suy luận


def test_substring_name_not_false_matched(tmp_path):
    """'Đoan' đứng trong từ khác KHÔNG được match (whole-word VN)."""
    out = tmp_path / 'output'
    _make_ep(out, 3, ['passenger_main : PAS_9002 (Kiên Bách, nam 36-50)'],
             ['Đoạn đường Thục Đoanh vắng.'])   # 'Thục Đoanh' != 'Thục Đoan'
    r = mine(output_root=out, roster_path=_roster(tmp_path, [PAS, PAS2]))
    assert r['findings']['F3_cross_episode_appearance'] == []


def test_naming_violation_forbidden_and_dup_bites():
    used = {'Hoàng': 'Hoàng Lâm'}
    forb = {'Linh'}
    v1 = check_name_bible23('Hoàng Yến', used, forb)
    assert any('rule_02' in x for x in v1), v1
    v2 = check_name_bible23('Thục Linh', used, forb)
    assert any('từ cấm' in x for x in v2), v2
    v3 = check_name_bible23('Loan', used, forb)
    assert any('rule_01' in x for x in v3), v3


def test_recurring_whitelist_not_flagged(tmp_path):
    """Khải Phong (recurring bible/03) xuất hiện mọi tập -> KHÔNG F3."""
    out = tmp_path / 'output'
    _make_ep(out, 2, ['passenger_main : PAS_9001 (Thục Đoan, nu 26-35)'],
             ['Khải Phong ngồi ghế thứ ba.'])
    _make_ep(out, 3, ['passenger_main : PAS_9002 (Kiên Bách, nam 36-50)'],
             ['Khải Phong nhìn ra cửa kính.'])
    r = mine(output_root=out, roster_path=_roster(tmp_path, [PAS, PAS2]))
    assert r['findings']['F3_cross_episode_appearance'] == []


# ---------- guard: miner KHÔNG ghi roster chính ----------

def test_mine_does_not_touch_roster(tmp_path):
    out = tmp_path / 'output'
    _make_ep(out, 2, ['passenger_main : PAS_9001 (Thục Đoan, nu 26-35)'], ['A.'])
    rf = _roster(tmp_path, [PAS])
    before = rf.read_bytes()
    mine(output_root=out, roster_path=rf)
    assert rf.read_bytes() == before
