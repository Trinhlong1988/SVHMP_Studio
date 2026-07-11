"""DEBT-021 (completeness gap #5, Mr.Long auth 11/7): enforcer TU TINH LAI distribution.

Truoc DEBT-021, header distribution_actual = so CU cho 100 passenger goc (32/24/20/14/10),
KHONG khop 139 that -> khong enforcer nao recompute (R215: claim distribution_lock khong co gate).
Test nay recompute pillar distribution TU roster THAT moi lan chay va doi chieu voi header
distribution_actual -> neu ai them/xoa passenger hoac doi pillar ma quen cap nhat header, FAIL.

Mirror pattern cac enforcer R215 khac (behavioral, khong hardcode so - so lay tu chinh 2 nguon
trong file de luon dong bo).
"""
import sys
from collections import Counter
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
ROSTER = REPO / "runtime" / "passenger_roster_100.yaml"


def _load():
    return yaml.safe_load(ROSTER.read_text(encoding="utf-8"))


def test_distribution_actual_matches_recompute():
    """Header distribution_actual PHAI == pillar distribution tinh lai tu passengers THAT."""
    d = _load()
    actual = dict(Counter(p.get("pillar") for p in d["passengers"]))
    declared = dict(d["distribution_actual"])
    assert actual == declared, (
        f"distribution_actual LECH voi roster THAT.\n  recompute: {actual}\n  header:    {declared}\n"
        f"  -> cap nhat distribution_actual moi khi roster doi (DEBT-021 enforcer).")


def test_distribution_actual_sums_to_total_passengers():
    d = _load()
    declared = dict(d["distribution_actual"])
    assert sum(declared.values()) == len(d["passengers"]), (
        f"tong distribution_actual {sum(declared.values())} != so passenger {len(d['passengers'])}")


def test_distribution_target_unchanged_bible11_lock():
    """distribution_target la bible/11 lock (forbidden_edit) - GIU 32/24/20/14/10, KHONG duoc doi
    (DEBT-021 chi sua distribution_actual, khong dung vao target)."""
    d = _load()
    assert d["distribution_target"] == {
        "family_regret": 32, "love_regret": 24, "promise_regret": 20,
        "kindness_regret": 14, "self_regret": 10}, d.get("distribution_target")
