"""G2 — Character DoD completeness-gate wired vao render (svhmp_preflight_qa).

CharacterRegistry.episode_completeness(ep, threshold) tra ve char trong ep +
danh sach DUOI nguong; render_gate_lines(cg, strict) format thanh WARN (khong
chan) hoac BLOCK (chan render). Preflight goi 2 ham nay -> single-source, test
va render dung CHUNG logic (khong nhan doi).

WARN-by-default vi roster hien "vo dien" (avg completeness ~0.23) -> HARD-block
se chan MOI episode. --strict-characters bat block khi roster da day.

pytest-func -> chay trong `pytest tests/` va ci_gate.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
from character_manager import CharacterRegistry, CharacterProfile  # noqa: E402


def _reg(*chars):
    """Registry synthetic — skip file-load, inject chars truc tiep."""
    r = CharacterRegistry.__new__(CharacterRegistry)
    r.chars = {c.id: c for c in chars}
    return r


def _full(cid, ep):
    """7/13 EXT_GROUPS filled -> completeness ~0.54 (> nguong 0.5)."""
    return CharacterProfile(
        id=cid, char_name='Full Char', assigned_ep=ep,
        physical={'build': 'gay'}, attire={'clothing': 'ao dai'},
        personality={'traits': 'hien'}, background={'occupation': 'giao vien'},
        relationships=[{'who': 'X', 'relation': 'ban'}],
        dob='1990-01-01', life_status='song',
    )


# ---------- episode_completeness ----------

def test_skeleton_char_flagged_below_threshold():
    skel = CharacterProfile(id='PAS_0001', char_name='Skeleton', assigned_ep=1)
    res = _reg(skel).episode_completeness(1, threshold=0.5)
    assert res['total'] == 1
    assert [c['id'] for c in res['below']] == ['PAS_0001']
    assert 'background' in res['below'][0]['missing']  # occupation/role gap


def test_full_char_passes_threshold():
    res = _reg(_full('PAS_0002', 1)).episode_completeness(1, threshold=0.5)
    assert res['total'] == 1
    assert res['below'] == []  # completeness > 0.5 -> khong flag


def test_threshold_zero_flags_nothing():
    skel = CharacterProfile(id='PAS_0003', assigned_ep=1)
    res = _reg(skel).episode_completeness(1, threshold=0.0)
    assert res['below'] == []  # completeness 0.0 KHONG < 0.0


def test_ep_without_chars_is_empty():
    res = _reg(_full('PAS_0004', 1)).episode_completeness(99, threshold=0.5)
    assert res['total'] == 0 and res['below'] == []


# ---------- render_gate_lines (WARN vs STRICT) ----------

def test_warn_mode_never_blocks():
    skel = CharacterProfile(id='PAS_0005', char_name='Skel', assigned_ep=1)
    cg = _reg(skel).episode_completeness(1, threshold=0.5)
    warns, blocks = CharacterRegistry.render_gate_lines(cg, strict=False)
    assert len(warns) == 1 and blocks == []  # WARN -> render KHONG bi chan


def test_strict_mode_blocks_incomplete():
    skel = CharacterProfile(id='PAS_0006', char_name='Skel', assigned_ep=1)
    cg = _reg(skel).episode_completeness(1, threshold=0.5)
    warns, blocks = CharacterRegistry.render_gate_lines(cg, strict=True)
    assert warns == [] and len(blocks) == 1  # STRICT -> chan render
    assert 'PAS_0006' in blocks[0]


def test_full_char_neither_warn_nor_block():
    cg = _reg(_full('PAS_0007', 1)).episode_completeness(1, threshold=0.5)
    warns, blocks = CharacterRegistry.render_gate_lines(cg, strict=True)
    assert warns == [] and blocks == []  # day du -> khong warn/block du strict
