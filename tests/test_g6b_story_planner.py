"""G6b — mutation test cho story_plan_schema_check.py + reality anchor tren du lieu that.

M1 component_ref sai/thieu -> FAIL
M2 driver_reveal_cumulative vuot cap -> FAIL
M3 cast_count ngoai [5,8] -> FAIL
M4 characters_present chua PAS_id bia -> FAIL
M5 driver_clue.weight ngoai tap hop -> FAIL
M6 entity "act" KHONG duoc xuat hien trong schema/output (bao ve rang buoc 3-entity da khoa)
M7 scene_function thieu/sai enum -> FAIL (DEBT-014 10/7, finding #19 goc)
"""
import copy
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import story_planner as sp  # noqa: E402
import story_plan_schema_check as check  # noqa: E402

SCHEMA_PATH = REPO / "governance" / "blueprint" / "schemas" / "story_plan_schema.yaml"


def _real_ep01_plan():
    return copy.deepcopy(sp.build_episode_plan_ep01())


def test_m0_real_ep01_plan_clean():
    plan = _real_ep01_plan()
    bible18 = sp._load(sp.BIBLE_18)
    roster_ids = sp._load_roster_ids()
    errs = (check.check_component_order(plan) + check.check_driver_reveal_cap(plan, bible18)
            + check.check_cast_count(plan) + check.check_characters_present(plan, roster_ids)
            + check.check_driver_clue_weight(plan) + check.check_scene_function_present(plan))
    assert errs == [], f"EP01 that KHONG duoc co vi pham: {errs}"


def test_m1_component_order_missing_bites():
    plan = _real_ep01_plan()
    plan["scenes_detail"] = plan["scenes_detail"][:-1]  # xoa CLIFFHANGER
    errs = check.check_component_order(plan)
    assert errs, "thieu 1 component phai bi bat"


def test_m1_component_order_wrong_sequence_bites():
    plan = _real_ep01_plan()
    plan["scenes_detail"][0], plan["scenes_detail"][1] = plan["scenes_detail"][1], plan["scenes_detail"][0]
    errs = check.check_component_order(plan)
    assert errs, "sai thu tu component phai bi bat"


def test_m2_driver_reveal_cumulative_over_cap_bites():
    plan = _real_ep01_plan()
    plan["driver_reveal_cumulative"] = 999
    bible18 = sp._load(sp.BIBLE_18)
    errs = check.check_driver_reveal_cap(plan, bible18)
    assert errs, "vuot cap PHAI bi bat"


def test_m2_driver_reveal_cumulative_within_cap_clean():
    plan = _real_ep01_plan()
    bible18 = sp._load(sp.BIBLE_18)
    errs = check.check_driver_reveal_cap(plan, bible18)
    assert errs == [], f"gia tri that (3%) KHONG duoc bi bat: {errs}"


def test_m3_cast_count_out_of_range_bites():
    plan = _real_ep01_plan()
    plan["cast_count"] = 99
    errs = check.check_cast_count(plan)
    assert errs, "cast_count ngoai [5,8] phai bi bat"


def test_m4_characters_present_fake_pas_id_bites():
    plan = _real_ep01_plan()
    plan["scenes_detail"][0]["characters_present"] = ["PAS_9999_BIA"]
    roster_ids = sp._load_roster_ids()
    errs = check.check_characters_present(plan, roster_ids)
    assert errs, "PAS_id bia phai bi bat"


def test_m4_characters_present_real_pas_id_clean():
    plan = _real_ep01_plan()
    roster_ids = sp._load_roster_ids()
    real_id = next(iter(roster_ids))
    plan["scenes_detail"][0]["characters_present"] = [real_id]
    errs = check.check_characters_present(plan, roster_ids)
    assert errs == [], f"PAS_id THAT khong duoc bi bat: {errs}"


def test_m5_driver_clue_weight_invalid_bites():
    plan = _real_ep01_plan()
    plan["scenes_detail"][0]["driver_clue"] = {"weight": 999, "content": "gia"}
    errs = check.check_driver_clue_weight(plan)
    assert errs, "weight ngoai {1,2,5,10,30} phai bi bat"


def test_m5_driver_clue_weight_valid_clean():
    plan = _real_ep01_plan()
    plan["scenes_detail"][0]["driver_clue"] = {"weight": 1, "content": "gang tay trang"}
    errs = check.check_driver_clue_weight(plan)
    assert errs == [], f"weight hop le KHONG duoc bi bat: {errs}"


# ============================================================
# M7 (DEBT-014, 10/7 per Mr.Long authorization) — scene_function CHOT mapping
# (dua tren doc truc tiep output/ep_01/episode_golden_text.md dong 96-515, khong
# doan): HOOK/SETUP=gay_nghi, INCIDENT/PAYOFF=dan_chuyen, REVEAL=hy_sinh,
# CLIFFHANGER=danh_lac_huong.
# ============================================================

EP01_EXPECTED_SCENE_FUNCTION = {
    "EP1_SC1": "gay_nghi", "EP1_SC2": "gay_nghi", "EP1_SC3": "dan_chuyen",
    "EP1_SC4": "hy_sinh", "EP1_SC5": "dan_chuyen", "EP1_SC6": "danh_lac_huong",
}


def test_reality_ep01_scene_function_matches_chot_mapping():
    """Reality anchor: build_episode_plan_ep01() PHAI tra ve DUNG mapping da CHOT
    (khong bia, khong lech thu tu) cho ca 6 scene."""
    plan = _real_ep01_plan()
    actual = {sc["scene_id"]: sc["scene_function"] for sc in plan["scenes_detail"]}
    assert actual == EP01_EXPECTED_SCENE_FUNCTION, (
        f"scene_function lech mapping da CHOT 16:00 10/7: {actual}")


def test_m7_scene_function_missing_bites():
    plan = _real_ep01_plan()
    del plan["scenes_detail"][0]["scene_function"]
    errs = check.check_scene_function_present(plan)
    assert errs, "scene_function thieu PHAI bi bat"


def test_m7_scene_function_empty_string_bites():
    plan = _real_ep01_plan()
    plan["scenes_detail"][0]["scene_function"] = ""
    errs = check.check_scene_function_present(plan)
    assert errs, "scene_function rong PHAI bi bat"


def test_m7_scene_function_invalid_enum_bites():
    plan = _real_ep01_plan()
    plan["scenes_detail"][0]["scene_function"] = "gia_tri_bia_khong_ton_tai"
    errs = check.check_scene_function_present(plan)
    assert errs, "scene_function ngoai 4 enum PHAI bi bat"


def test_m7_scene_function_valid_clean():
    plan = _real_ep01_plan()
    errs = check.check_scene_function_present(plan)
    assert errs == [], f"EP01 that (mapping da CHOT) KHONG duoc co vi pham: {errs}"


# ============================================================
# M6 — bao ve rang buoc "3 entity, cam act" da Mr.Long khoa (APPROVED_A)
# ============================================================

def test_m6_schema_file_has_no_act_entity():
    """Reality anchor: schema THAT field-hoa KHONG duoc co entity 'act'."""
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    entities = set(schema["schema"].keys())
    assert entities == {"scene", "episode_plan", "season_plan"}, (
        f"schema PHAI dung 3 entity, khong co 'act': {entities}")
    assert "act" not in entities


def test_m6_story_planner_output_has_no_act_key():
    """Reality anchor: output THAT cua story_planner (season_plan + episode_plan)
    khong duoc chua key/entity 'act' duoi bat ky ten nao."""
    seasons = sp.build_season_plan()
    plans, _ = sp.build_episode_plans()
    for obj in seasons + plans:
        assert "act" not in obj, f"phat hien key 'act' trong output: {obj.keys()}"
        for v in obj.values():
            if isinstance(v, str):
                assert v.lower() != "act", f"gia tri 'act' xuat hien: {obj}"


# ============================================================
# REALITY ANCHOR — chay tren du lieu THAT
# ============================================================

def test_reality_story_plan_schema_check_pass_on_real_data():
    errs, plans, pending = check.run_checks()
    assert errs == [], f"story_plan_schema_check tren du lieu that phai 0 vi pham: {errs}"
    assert len(plans) == 1, "hien tai CHI EP01 xay duoc day du that"
    assert len(pending) == 49, "ep_02..ep_50 phai o trang thai pending minh bach (khong bia)"


def test_reality_season_plan_3_entries_real_boundaries():
    seasons = sp.build_season_plan()
    assert len(seasons) == 3
    assert seasons[0]["episode_range"] == [1, 30]
    assert seasons[1]["episode_range"] == [31, 60]
    assert seasons[2]["episode_range"] == [61, 90]


def test_reality_g6_gate_pass_on_real_data():
    import subprocess
    r = subprocess.run([sys.executable, str(REPO / "tools" / "g6_story_planner_check.py")],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr


def test_g6b_stages_wired_in_g6_gate_suite():
    """Unwire-guard cho SUITE (khac ci_gate.py CHECKS da wired san tu G6a) - 2 stage G6b
    PHAI co trong SUITE cua g6_story_planner_check.py."""
    sys.path.insert(0, str(REPO / "tools"))
    import g6_story_planner_check as gate
    keys = [k for k, _ in gate.SUITE]
    assert "G6b_D5_story_planner_selfcheck" in keys
    assert "G6b_D6a_schema_check" in keys
    assert ("G6b_D5_story_planner_selfcheck", "tools/story_planner.py") in gate.SUITE
    assert ("G6b_D6a_schema_check", "tools/story_plan_schema_check.py") in gate.SUITE
