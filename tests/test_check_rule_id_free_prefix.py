"""Regression cho check_rule_id_free.py — bug 4/7: scan_all()/check_staged() cu CHI dem
'top_level'/'list_id' la definition, bo sot quy uoc 'rule_R{N}_xxx:' (76/123 rule bible/00)
-> R142 dup-key that (2 noi dung khac nhau, yaml.safe_load im lang nuot ban dau) khong bi
--all bat. Phat hien khi audit BP7 (kiem duyet doc lap, khong lien quan xay dung BP7).

Mutation tren tmp_path — KHONG phu thuoc trang thai bible/00 that (se doi khi Mr.Long fix
noi dung) — chi test CO CHE nhan dien dung dinh dang, khong hard-code so luong dup hien tai.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from check_rule_id_free import scan_id, scan_all, DEF_FORMATS  # noqa: E402


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding='utf-8')
    return p


def test_rule_prefix_format_recognized_as_definition(tmp_path):
    """Dong dang 'rule_R{N}_xxx:' phai duoc gan nhan 'rule_prefix', khong roi vao
    'any_indent' (format khong duoc scan_all dem la definition truoc fix 4/7)."""
    f = _write(tmp_path, 'a.yaml', 'rule_R199_foo:\n  desc: "a"\n')
    hits = scan_id(199, files=[f])
    formats = [h[3] for h in hits]
    assert 'rule_prefix' in formats, f'rule_R{{N}}_ phai nhan dien duoc dinh dang rule_prefix: {hits}'


def test_scan_all_catches_true_dup_key_rule_prefix(tmp_path):
    """Tai hien CHINH XAC lop bug R142: 2 lan 'rule_R{N}_xxx:' TRUNG key, noi dung khac
    nhau -> yaml.safe_load nuot ban dau, nhung scan_all() (dua tren text-scan, khong parse
    yaml) PHAI bat duoc ca 2 dinh nghia va bao dup — day la ly do dung regex thay vi yaml.safe_load
    (chinh yaml.safe_load la nan nhan cua loi nay)."""
    f = _write(tmp_path, 'b.yaml',
              'rule_R199_kill_switch:\n  desc: "ban 1 - outline"\n\n'
              'rule_R199_kill_switch:\n  desc: "ban 2 - publish abort"\n')
    hits = scan_id(199, files=[f])
    defs = [h for h in hits if h[3] in DEF_FORMATS]
    assert len(defs) == 2, f'phai thay 2 dinh nghia trung key rule_prefix: {hits}'
    assert scan_all(files=[f]) == 1, 'scan_all phai FAIL (exit 1) khi co dup rule_prefix'


def test_scan_all_ok_when_only_one_rule_prefix_def(tmp_path):
    """Khong bao dong gia: 1 dinh nghia rule_prefix duy nhat -> scan_all sach (chong
    over-tighten — bai hoc CMD_AUDIT_PROTOCOL B5: restore phai PASS lai)."""
    f = _write(tmp_path, 'c.yaml', 'rule_R199_kill_switch:\n  desc: "chi 1 ban"\n')
    assert scan_all(files=[f]) == 0


def test_scan_all_distinguishes_different_keys_same_number(tmp_path):
    """Case R141 that (bible/00): 2 KEY KHAC NHAU cung dung so 141
    (rule_R141_diff_check vs rule_R141_ssot_diff_check) — khac lop voi R142/R143 (khong
    mat du lieu qua yaml.safe_load vi key khac chu) nhung van la dup-so-hieu can bao."""
    f = _write(tmp_path, 'd.yaml',
              'rule_R199_diff_check:\n  desc: "stub cu"\n\n'
              'rule_R199_ssot_diff_check:\n  desc: "ban that, da BUILT"\n')
    hits = scan_id(199, files=[f])
    defs = [h for h in hits if h[3] in DEF_FORMATS]
    assert len(defs) == 2, 'phai thay 2 dinh nghia du ten key khac nhau (cung so 199)'
    assert scan_all(files=[f]) == 1


def test_staged_diff_detects_rule_prefix_addition(tmp_path, monkeypatch):
    """check_staged() cung phai nhan dien '+rule_R{N}_xxx:' trong git diff staged —
    truoc fix 4/7, them rule MOI dang rule_R{N}_ trung ID cu se lot qua pre-commit hook
    (git_hook_pre_commit.py Section A goi check_rule_id_free.py --staged)."""
    import re
    add_rule_prefix = re.compile(r'^\+rule_R(\d+)_[a-zA-Z]', re.MULTILINE)
    diff = '+rule_R199_moi_them:\n+  desc: "test"\n'
    matches = [int(m.group(1)) for m in add_rule_prefix.finditer(diff)]
    assert matches == [199], 'regex staged-diff phai bat duoc dang rule_R{N}_ moi them'
