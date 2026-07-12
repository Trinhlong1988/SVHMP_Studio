"""TASK_STORY_PLANNER_EP02_11_PILOT.md — test cho parser moi (Buoc 1) + field-hoa EP02-11
(Buoc 2-4), per Mr.Long authorization 12/7 (TU CHINH domain story_planner LOCKED).

M8  parse_sections_v2() tra dung 6/6 header + dung thu tu tren CA 10 tap EP02-11 (reality anchor)
M9  parse_sections_v2() mutation-proof: thieu section / sai thu tu -> raise ValueError
M10 build_episode_plan_ep02_11() reality anchor: scene_function/cast_count/driver_reveal_
    cumulative/season_ref/kpi_ep_range_ref dung cho ca 10 tap
M11 regret_pillars_covered: EP02-10 co pillar that (tu regret_sub), EP11 pending (regret_sub
    null trong event_ledger, KHONG tu suy doan - R195). CAP NHAT 12/7 (DEBT-031,
    TASK_DEBT030_031_CONTENT_FIX.md): EP03/04/06/07/09/10 da doi pillar (khong con toan
    family_regret) - xem EP02_10_EXPECTED_PILLAR duoi day.
M12 characters_present: EP02-10 resolve PAS_id that trong roster, EP11 rong + pending_fields
    ghi ly do (passenger_main khong co PAS_id)
M13 location_ref: CA 10 tap deu pending (stop_location la dia danh vat ly, 0/20 khop bible/13)
M14 build_episode_plan_ep02_11() tu choi ep_number ngoai [2,11] (mutation-proof)
M15 driver_reveal_cumulative KHONG vuot cap bible/18 ep_1_to_20 (5%) cho ca 10 tap
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import story_planner as sp  # noqa: E402
import story_plan_schema_check as check  # noqa: E402

EP_RANGE = range(2, 12)


# ============================================================
# M8/M9 — parse_sections_v2() (Buoc 1)
# ============================================================

def test_reality_parse_sections_v2_all_10_episodes_6_headers_in_order():
    for ep in EP_RANGE:
        headers = sp.parse_sections_v2(ep)
        assert [h["name"] for h in headers] == sp.COMPONENT_ORDER_V2, (
            f"ep_{ep:02d}: header order sai/thieu: {[h['name'] for h in headers]}")
        assert len(headers) == 6


def test_m9_parse_sections_v2_missing_section_raises(tmp_path, monkeypatch):
    ep_dir = tmp_path / "ep_99"
    ep_dir.mkdir()
    (ep_dir / "episode.md").write_text(
        "# HOOK [section 1]\nfoo\n---\n# SETUP [section 2]\nbar\n", encoding="utf-8")
    monkeypatch.setattr(sp, "OUTPUT_DIR", tmp_path)
    with pytest.raises(ValueError):
        sp.parse_sections_v2(99)


def test_m9_parse_sections_v2_wrong_order_raises(tmp_path, monkeypatch):
    ep_dir = tmp_path / "ep_99"
    ep_dir.mkdir()
    text = "\n".join(
        f"# {name} [section {i}]\nbody\n---"
        for i, name in enumerate(
            ["SETUP", "HOOK", "INCIDENT", "REVEAL", "PAYOFF", "CLIFFHANGER"], start=1)
    )
    (ep_dir / "episode.md").write_text(text, encoding="utf-8")
    monkeypatch.setattr(sp, "OUTPUT_DIR", tmp_path)
    with pytest.raises(ValueError):
        sp.parse_sections_v2(99)


def test_m9_parse_sections_v2_valid_order_clean(tmp_path, monkeypatch):
    ep_dir = tmp_path / "ep_99"
    ep_dir.mkdir()
    text = "\n".join(
        f"# {name} [section {i}]\nbody cua {name}\n---"
        for i, name in enumerate(sp.COMPONENT_ORDER_V2, start=1)
    )
    (ep_dir / "episode.md").write_text(text, encoding="utf-8")
    monkeypatch.setattr(sp, "OUTPUT_DIR", tmp_path)
    headers = sp.parse_sections_v2(99)
    assert [h["name"] for h in headers] == sp.COMPONENT_ORDER_V2


# ============================================================
# M10 — build_episode_plan_ep02_11() reality anchor
# ============================================================

def test_reality_ep02_11_scene_function_matches_grounded_mapping():
    for ep in EP_RANGE:
        plan = sp.build_episode_plan_ep02_11(ep)
        actual = {sc["component_ref"]: sc["scene_function"] for sc in plan["scenes_detail"]}
        assert actual == sp.EP02_11_SCENE_FUNCTION_BY_COMPONENT, (
            f"ep_{ep:02d}: scene_function lech mapping da doc truc tiep: {actual}")


def test_reality_ep02_11_cast_count_and_season_and_kpi():
    for ep in EP_RANGE:
        plan = sp.build_episode_plan_ep02_11(ep)
        assert plan["cast_count"] == 5
        assert 5 <= plan["cast_count"] <= 8
        assert plan["season_ref"] == "season_1"
        expected_bucket = "ep_1_10" if ep <= 10 else "ep_11_30"
        assert plan["kpi_ep_range_ref"] == expected_bucket


def test_reality_ep02_11_driver_reveal_cumulative_within_cap():
    bible18 = sp._load(sp.BIBLE_18)
    cap = bible18["budget_curve"]["ep_1_to_20"]["cumulative_cap"]
    for ep in EP_RANGE:
        plan = sp.build_episode_plan_ep02_11(ep)
        assert plan["driver_reveal_cumulative"] == 3
        assert plan["driver_reveal_cumulative"] <= cap


# ============================================================
# M11 — regret_pillars_covered
# ============================================================

# DEBT-031 (TASK_DEBT030_031_CONTENT_FIX.md Buoc 2, per Mr.Long authorization 12/7): noi dung
# that EP03/04/06/07/09/10 da duoc viet lai (doi pillar) de dat bible/11 variety_rules
# (pillar_distance>=3, family_regret_max_per_10_ep<=4, pillar_per_10_ep_min_distinct>=4).
# EP02/05/08/11 GIU NGUYEN family_regret (khong sua, xem TASK doc). Bang duoi day la SU THAT
# hien tai trong runtime/event_ledger_draft.yaml sau khi sua (khong phai gia dinh).
EP02_10_EXPECTED_PILLAR = {
    2: "family_regret",
    3: "promise_regret",
    4: "love_regret",
    5: "family_regret",
    6: "kindness_regret",
    7: "self_regret",
    8: "family_regret",
    9: "promise_regret",
    10: "love_regret",
}


def test_reality_regret_pillars_covered_ep02_10_populated_ep11_pending():
    for ep in range(2, 11):
        plan = sp.build_episode_plan_ep02_11(ep)
        expected = EP02_10_EXPECTED_PILLAR[ep]
        assert plan["regret_pillars_covered"] == [expected], (
            f"ep_{ep:02d}: regret_pillars_covered phai co {expected} that (DEBT-031 fix)")
    # bible/11 variety_rules kiem chung tren toan batch EP02-10 sau fix
    assert len(set(EP02_10_EXPECTED_PILLAR.values())) >= 4, (
        "pillar_per_10_ep_min_distinct>=4 (bible/11) phai dat sau DEBT-031 fix")
    family_count = sum(1 for v in EP02_10_EXPECTED_PILLAR.values() if v == "family_regret")
    assert family_count <= 4, (
        "family_regret_max_per_10_ep<=4 (bible/11) phai dat sau DEBT-031 fix")
    plan11 = sp.build_episode_plan_ep02_11(11)
    assert plan11["regret_pillars_covered"] == []
    reasons = [pf["field"] for pf in plan11["pending_fields"]]
    assert "regret_pillars_covered" in reasons, (
        "ep_11 regret_sub=null trong event_ledger PHAI duoc ghi pending, KHONG suy doan")


# ============================================================
# M12 — characters_present
# ============================================================

def test_reality_characters_present_ep02_10_resolves_real_pas_id():
    roster_ids = sp._load_roster_ids()
    for ep in range(2, 11):
        plan = sp.build_episode_plan_ep02_11(ep)
        non_cliffhanger = [sc for sc in plan["scenes_detail"] if sc["component_ref"] != "CLIFFHANGER"]
        for sc in non_cliffhanger:
            assert len(sc["characters_present"]) == 1
            pid = sc["characters_present"][0]
            assert pid in roster_ids, f"ep_{ep:02d}.{sc['scene_id']}: PAS_id '{pid}' KHONG co that trong roster"
        cliffhanger = [sc for sc in plan["scenes_detail"] if sc["component_ref"] == "CLIFFHANGER"][0]
        assert cliffhanger["characters_present"] == [], (
            "hanh khach da xuong xe truoc CLIFFHANGER - khong duoc liet ke lai")


def test_reality_characters_present_ep11_empty_and_flagged_pending():
    plan = sp.build_episode_plan_ep02_11(11)
    for sc in plan["scenes_detail"]:
        assert sc["characters_present"] == []
    reasons = [pf["field"] for pf in plan["pending_fields"]]
    assert any("characters_present" in f for f in reasons), (
        "ep_11 passenger_main khong co PAS_id -> PHAI ghi pending, KHONG tu gan PAS_id doan")


# ============================================================
# M13 — location_ref pending cho ca 10 tap (stop_location khong khop bible/13)
# ============================================================

def test_reality_location_ref_pending_all_10_episodes():
    bible13 = sp._load(sp.BIBLE_13_SETTING)
    setting_ids = set(bible13["setting_library"].keys())
    assert not any("ngã ba" in k or "nga_ba" in k for k in setting_ids), (
        "reality-anchor: bible/13 khong duoc co entry dia danh - neu co, code + test nay phai "
        "cap nhat lai logic pending")
    for ep in EP_RANGE:
        plan = sp.build_episode_plan_ep02_11(ep)
        for sc in plan["scenes_detail"]:
            assert sc["location_ref"] is None
        reasons = [pf["field"] for pf in plan["pending_fields"]]
        assert "location_ref" in reasons


# ============================================================
# M14 — mutation-proof: pham vi ep_number
# ============================================================

def test_m14_build_episode_plan_ep02_11_rejects_out_of_range():
    with pytest.raises(ValueError):
        sp.build_episode_plan_ep02_11(1)
    with pytest.raises(ValueError):
        sp.build_episode_plan_ep02_11(12)


# ============================================================
# REALITY ANCHOR toan cuc — gate + build_episode_plans()
# ============================================================

def test_reality_build_episode_plans_11_built_39_pending():
    plans, pending = sp.build_episode_plans()
    assert len(plans) == 11
    assert {p["episode_number"] for p in plans} == set(range(1, 12))
    assert len(pending) == 39
    assert {p["episode_number"] for p in pending} == set(range(12, 51))


def test_reality_schema_check_0_violation_on_ep02_11():
    errs, plans, pending = check.run_checks()
    assert errs == []
