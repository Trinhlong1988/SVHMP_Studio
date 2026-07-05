"""D1 (TASK_G3_DIALOGUE.md, per Mr.Long ky 5/7) - reality anchor cho SSOT que<->giong reconcile.

Truoc fix: tools/dialog_voice_validator.py::HOMETOWN_REGION la dict tu viet tay, rieng biet voi
tools/migrate_roster_v2.py::HOME (nguon that roster_validator.py dang dung cho C2/R210) -> "Hai Duong"
co trong HOME['bac'] nhung THIEU trong HOMETOWN_REGION -> false negative cam lang (validate_profile()
khong bao gio bat duoc mismatch cho que nay). Sau fix: HOMETOWN_REGION suy nguoc TU HOME (object-identity
qua import, khong copy gia tri tay) nen MOI que trong HOME deu duoc bao phu tu dong.

Test nay PHAI do truoc-fix (neu ai lo hoan tac ve hand-code) va bat dung sau-fix.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

import dialog_voice_validator as dvv
from migrate_roster_v2 import HOME


def test_hai_duong_resolved_bac():
    """Bang chung cu the tu audit 5/7: 'Hai Duong' phai resolve dung vung 'bac'."""
    assert dvv.HOMETOWN_REGION.get('hải dương') == 'bac'


def test_hai_duong_mismatch_detected():
    """Khai 'Hai Duong' voi region 'nam' (sai) PHAI bi validate_profile() bat — truoc fix se lot qua."""
    issues = dvv.validate_profile({'region_dialect': 'nam', 'hometown': 'Hải Dương', 'pronoun_system': 'con'})
    codes = {i['code'] for i in issues}
    assert 'HOMETOWN_REGION_MISMATCH' in codes


def test_every_home_town_covered_by_object_identity():
    """Object-identity qua import (khong copy gia tri tay): MOI que trong HOME phai co trong
    HOMETOWN_REGION va tro dung vung — ai dan lai dict cung sau nay se do ngay vi khong con dong bo
    tu dong voi HOME khi HOME doi (vd them que moi)."""
    for region, towns in HOME.items():
        for town in towns:
            key = town.lower()
            assert key in dvv.HOMETOWN_REGION, f"{town} (vung {region}) thieu trong HOMETOWN_REGION"
            assert dvv.HOMETOWN_REGION[key] == region, f"{town}: HOMETOWN_REGION tro sai vung"


def test_extra_regions_tay_do_thi_not_lost():
    """2 vung tay/do_thi (dialogue-only, khong co trong HOME) van phai giu duoc — khong bi fix D1
    lam mat du lieu cu."""
    assert dvv.HOMETOWN_REGION.get('bến tre') == 'tay'
    assert dvv.HOMETOWN_REGION.get('cần thơ') == 'tay'


def test_no_hardcoded_duplicate_home_dict():
    """R211 guard: HOMETOWN_REGION khong con la dict tu-viet-tay doc lap — phai duoc SINH TU HOME,
    khong phai 1 bang hang so thu 3 song song."""
    rebuilt = {t.lower(): r for r, towns in HOME.items() for t in towns}
    for k, v in rebuilt.items():
        assert dvv.HOMETOWN_REGION.get(k) == v
