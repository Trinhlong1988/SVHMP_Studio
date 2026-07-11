"""DEBT-020 (completeness gap #4): bible/23 canon_waivers PHAI dong bo voi hang so THAT
trong tools/roster_validator.py (C1_RULE02_CANON_EXEMPT_WORDS + C1_CANON_SINGLE_SYLLABLE_EXEMPT).

Enforcer chong doc-code drift (R215): neu ai them/xoa waiver trong code ma quen cap nhat bible/23
(hoac nguoc lai), test nay FAIL. Truoc DEBT-020, waiver CHI nam trong code, bible/23 khang dinh
uniqueness tuyet doi -> drift am tham. Test nay khoa 2 nguon luon khop.
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import roster_validator as rv  # noqa: E402

BIBLE_23 = REPO / "bible" / "23_passenger_naming.yaml"


def _waiver_words():
    d = yaml.safe_load(BIBLE_23.read_text(encoding="utf-8"))
    cw = d["canon_waivers"]
    r02 = {w["word"] for w in cw["rule_02_word_uniqueness"]}
    r01 = {w["word"] for w in cw["rule_01_two_syllable_min"]}
    return r02, r01


def test_bible23_rule02_waivers_match_code():
    r02, _ = _waiver_words()
    assert r02 == set(rv.C1_RULE02_CANON_EXEMPT_WORDS), (
        f"bible/23 canon_waivers.rule_02 {r02} LECH voi roster_validator."
        f"C1_RULE02_CANON_EXEMPT_WORDS {set(rv.C1_RULE02_CANON_EXEMPT_WORDS)}")


def test_bible23_rule01_waivers_match_code():
    _, r01 = _waiver_words()
    assert r01 == set(rv.C1_CANON_SINGLE_SYLLABLE_EXEMPT), (
        f"bible/23 canon_waivers.rule_01 {r01} LECH voi roster_validator."
        f"C1_CANON_SINGLE_SYLLABLE_EXEMPT {set(rv.C1_CANON_SINGLE_SYLLABLE_EXEMPT)}")


def test_bible23_waivers_have_passenger_and_source():
    """Moi waiver PHAI ghi ro passenger id + nguon episode (chong nhet ten bia khong nguon)."""
    d = yaml.safe_load(BIBLE_23.read_text(encoding="utf-8"))
    cw = d["canon_waivers"]
    for group in ("rule_02_word_uniqueness", "rule_01_two_syllable_min"):
        for w in cw[group]:
            assert w.get("passenger", "").startswith("PAS_"), f"{group} {w} thieu passenger id"
            assert w.get("source"), f"{group} {w} thieu nguon episode"
