"""audit ML #3 (10/7) — CharacterProfile.completeness()/missing_ext(): dict group chi chua
value RONG ({'build': ''}) KHONG duoc tinh la 'da dien'. Truoc fix chi 'voice' loc value rong,
cac dict group khac dung 'if v:' tho -> {'build': ''} truthy -> filled sai (latent, 0 record
that dinh nhung van la lo hong). Fix: _group_nonempty() loc value rong nhat quan moi dict group.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from character_manager import CharacterProfile


def test_dict_group_all_empty_values_not_filled():
    # physical = {'build': ''} — dict truthy nhung value rong -> KHONG duoc tinh filled
    p = CharacterProfile(id='PAS_ml3_a', physical={'build': '', 'skin': ''})
    assert p._group_nonempty('physical') == {}, "value rong phai bi loc het"
    assert 'physical' in p.missing_ext(), "dict rong-noi-dung phai nam trong missing_ext"


def test_dict_group_with_real_value_is_filled():
    p = CharacterProfile(id='PAS_ml3_b', physical={'build': 'gay', 'skin': ''})
    assert p._group_nonempty('physical') == {'build': 'gay'}
    assert 'physical' not in p.missing_ext()


def test_completeness_treats_empty_valued_dicts_same_as_truly_empty():
    # profile RONG hoan toan vs profile co dict group nhung value rong -> completeness PHAI bang nhau
    p_empty = CharacterProfile(id='PAS_ml3_empty')
    p_fake = CharacterProfile(id='PAS_ml3_fake',
                              physical={'build': ''}, attire={'hat': ''},
                              personality={'fear': ''}, background={'que': ''})
    assert p_fake.completeness() == p_empty.completeness(), (
        "dict rong-noi-dung khong duoc lam completeness cao gia")


def test_scalar_and_list_groups_unaffected():
    # dob (str) va relationships (list) van hoat dong dung sau khi refactor
    p = CharacterProfile(id='PAS_ml3_c', dob='1990', relationships=[{'who': 'X', 'relation': 'ban'}])
    assert 'dob' not in p.missing_ext()
    assert 'relationships' not in p.missing_ext()
    p2 = CharacterProfile(id='PAS_ml3_d')  # dob='' , relationships=[]
    assert 'dob' in p2.missing_ext()
    assert 'relationships' in p2.missing_ext()
