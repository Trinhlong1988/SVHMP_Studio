"""R212 — CHUNG THUC artifact contract (PACK2 08, Boss 2/7).
Chung minh: contract check bat artifact KHAI != disk (chong bao cao lao),
va repo hien tai 0 phantom.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import artifact_contract_check as acc  # noqa: E402


def test_no_phantom_artifact_in_repo():
    _, missing = acc.check()
    assert missing == [], f"phantom artifact (khai != disk): {missing}"


def test_matrix_covers_all_registry_domains():
    matrix, _ = acc.check()
    assert {'governance', 'character', 'audio_render'} <= set(matrix)


def test_matrix_reflects_real_dims():
    matrix, _ = acc.check()
    assert matrix['character']['schema'] is True
    assert matrix['governance']['test'] is True


def test_phantom_path_would_be_detected():
    # ca AM: co che bat file khong ton tai
    p = []
    acc._paths({'k': 'tools/__nope_does_not_exist__.py'}, p)
    assert 'tools/__nope_does_not_exist__.py' in p
    assert not (acc.SVHMP / 'tools/__nope_does_not_exist__.py').exists()
