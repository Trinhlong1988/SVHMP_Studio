"""audit ML #4/#5 (10/7) — dialogue_manager.py:
#4 name-match guard (_recent_lines chi lay quote khi ten passenger trich tu episode.md KHOP
   char_name - tranh gan nham quote passenger khac) truoc KHONG co test hanh vi. Them test
   mutation-proof: bo dieu kien `name != c.char_name` -> test mismatch se flip.
#5 claim SSOT (module KHONG doc lai roster YAML lan 2, di qua CharacterRegistry) truoc KHONG
   co test. Them grep test tren source that.
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import dialogue_manager as dm_mod
from dialogue_manager import DialogueManager
from character_manager import CharacterProfile


def _make_ep(tmp_path, ep):
    d = tmp_path / 'output' / f'ep_{ep:02d}'
    d.mkdir(parents=True)
    (d / 'episode.md').write_text('noi dung episode', encoding='utf-8')


def _dm():
    # __new__ tranh __init__ (load CharacterRegistry that) - _recent_lines khong dung self.registry
    return DialogueManager.__new__(DialogueManager)


def test_recent_lines_returns_quotes_when_name_matches(tmp_path, monkeypatch):
    _make_ep(tmp_path, 5)
    monkeypatch.setattr(dm_mod, 'SVHMP', tmp_path)
    monkeypatch.setattr(dm_mod, 'get_passenger_info', lambda text: ('Le Thi Test', 30))
    monkeypatch.setattr(dm_mod, 'extract_quotes', lambda text: [('Cau thoai du dai roi', None)])
    c = CharacterProfile(id='PAS_ml4', char_name='Le Thi Test', assigned_ep=5)
    assert _dm()._recent_lines(c) == ['Cau thoai du dai roi']


def test_recent_lines_empty_when_name_mismatch(tmp_path, monkeypatch):
    # ten passenger trong episode.md KHAC char_name -> guard tra [] (khong gan nham quote).
    # Mutation-proof: neu bo `name != c.char_name`, ham se tra quote -> test nay flip FAIL.
    _make_ep(tmp_path, 5)
    monkeypatch.setattr(dm_mod, 'SVHMP', tmp_path)
    monkeypatch.setattr(dm_mod, 'get_passenger_info', lambda text: ('Nguoi Hoan Toan Khac', 40))
    monkeypatch.setattr(dm_mod, 'extract_quotes', lambda text: [('Cau thoai du dai roi', None)])
    c = CharacterProfile(id='PAS_ml4', char_name='Le Thi Test', assigned_ep=5)
    assert _dm()._recent_lines(c) == []


def test_recent_lines_empty_when_no_passenger_name(tmp_path, monkeypatch):
    # guard `not name` — get_passenger_info tra None -> []
    _make_ep(tmp_path, 5)
    monkeypatch.setattr(dm_mod, 'SVHMP', tmp_path)
    monkeypatch.setattr(dm_mod, 'get_passenger_info', lambda text: (None, None))
    monkeypatch.setattr(dm_mod, 'extract_quotes', lambda text: [('Cau thoai du dai roi', None)])
    c = CharacterProfile(id='PAS_ml4', char_name='Le Thi Test', assigned_ep=5)
    assert _dm()._recent_lines(c) == []


def test_dialogue_manager_is_ssot_no_roster_yaml_read():
    # #5: module KHONG duoc load roster YAML truc tiep (SSOT qua CharacterRegistry)
    src = Path(dm_mod.__file__).read_text(encoding='utf-8')
    assert 'yaml.safe_load' not in src, "dialogue_manager khong duoc tu load YAML (SSOT)"
    assert 'passenger_roster' not in src, "khong duoc mo file roster truc tiep"
    assert not re.search(r'^\s*import\s+yaml', src, re.M), "khong duoc import yaml"
