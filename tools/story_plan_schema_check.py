"""story_plan_schema_check.py — G6b D6a: validator cho story_planner output.

Dung 5 check DA KHAI SAN trong governance/proposals/story_plan_schema_proposal.yaml
mục enforcer_planned.checks_to_implement_later (khong tu nghi them/bot):
  1. component_ref moi scene trong 1 episode_plan PHAI dung 6 gia tri + dung thu tu bible/01
  2. driver_reveal_cumulative moi episode_plan PHAI <= cap cua bible/18 dung ep_range
  3. cast_count moi episode_plan PHAI trong [5,8]
  4. characters_present moi scene PHAI resolve that trong roster (khong PAS_id bia)
  5. driver_clue.weight PHAI thuoc {1,2,5,10,30} dung clue_weight_taxonomy
  6. scene_function moi scene PHAI hien dien + thuoc 4 gia tri enum (DEBT-014 10/7,
     per Mr.Long authorization - finding #19 goc yeu cau: schema khai required:true
     nhung truoc do KHONG co check hien dien nao, thieu sot lot qua PASS)

Exit 0 = 0 vi pham, exit 1 = >=1 vi pham.
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import story_planner as sp  # noqa: E402

__version__ = "1.0.0"

COMPONENT_ORDER = ["HOOK", "SETUP", "INCIDENT", "REVEAL", "PAYOFF", "CLIFFHANGER"]
CAST_COUNT_RANGE = (5, 8)
CLUE_WEIGHTS = {1, 2, 5, 10, 30}
SCENE_FUNCTION_VALUES = {"dan_chuyen", "gay_nghi", "danh_lac_huong", "hy_sinh"}


def _bible18_cap_for_ep(ep, bible18):
    for key, block in bible18["budget_curve"].items():
        rng = _ep_range_of_key(key)
        if rng and rng[0] <= ep <= rng[1]:
            return block.get("cumulative_cap", block.get("cumulative_after"))
    return None


def _ep_range_of_key(key):
    """'ep_1_to_20' -> (1,20); 'ep_18'/'ep_73'/'ep_90' -> (N,N)."""
    parts = key.replace("ep_", "").split("_to_")
    try:
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
        return int(parts[0]), int(parts[0])
    except ValueError:
        return None


def check_component_order(episode_plan):
    """1. scenes_detail component_ref phai dung 6 ten + dung thu tu."""
    errs = []
    got = [sc["component_ref"] for sc in episode_plan.get("scenes_detail", [])]
    if got != COMPONENT_ORDER:
        errs.append(f"ep{episode_plan['episode_number']}: component_ref {got} != {COMPONENT_ORDER}")
    return errs


def check_driver_reveal_cap(episode_plan, bible18):
    """2. driver_reveal_cumulative <= cap dung ep_range."""
    errs = []
    ep = episode_plan["episode_number"]
    cap = _bible18_cap_for_ep(ep, bible18)
    val = episode_plan["driver_reveal_cumulative"]
    if cap is not None and val > cap:
        errs.append(f"ep{ep}: driver_reveal_cumulative {val}% > cap {cap}% (bible/18)")
    return errs


def check_cast_count(episode_plan):
    """3. cast_count trong [5,8]."""
    errs = []
    cc = episode_plan["cast_count"]
    if not (CAST_COUNT_RANGE[0] <= cc <= CAST_COUNT_RANGE[1]):
        errs.append(f"ep{episode_plan['episode_number']}: cast_count {cc} ngoai {CAST_COUNT_RANGE}")
    return errs


def check_characters_present(episode_plan, roster_ids):
    """4. characters_present moi scene phai resolve that trong roster."""
    errs = []
    for sc in episode_plan.get("scenes_detail", []):
        for pid in sc.get("characters_present", []):
            if pid not in roster_ids:
                errs.append(f"ep{episode_plan['episode_number']}.{sc['scene_id']}: "
                            f"characters_present '{pid}' KHONG ton tai trong roster (bia PAS_id)")
    return errs


def check_driver_clue_weight(episode_plan):
    """5. driver_clue.weight thuoc {1,2,5,10,30}."""
    errs = []
    for sc in episode_plan.get("scenes_detail", []):
        clue = sc.get("driver_clue")
        if clue and clue.get("weight") not in CLUE_WEIGHTS:
            errs.append(f"ep{episode_plan['episode_number']}.{sc['scene_id']}: "
                        f"driver_clue.weight {clue.get('weight')} khong thuoc {sorted(CLUE_WEIGHTS)}")
    return errs


def check_scene_function_present(episode_plan):
    """6. scene_function moi scene PHAI hien dien (khong None/thieu key) + thuoc dung
    4 gia tri enum story_plan_schema.yaml (DEBT-014, finding #19 goc)."""
    errs = []
    for sc in episode_plan.get("scenes_detail", []):
        sf = sc.get("scene_function")
        if not sf:
            errs.append(f"ep{episode_plan['episode_number']}.{sc['scene_id']}: "
                        "THIEU scene_function (required:true theo story_plan_schema.yaml)")
        elif sf not in SCENE_FUNCTION_VALUES:
            errs.append(f"ep{episode_plan['episode_number']}.{sc['scene_id']}: "
                        f"scene_function '{sf}' khong thuoc {sorted(SCENE_FUNCTION_VALUES)}")
    return errs


def run_checks():
    bible18 = sp._load(sp.BIBLE_18)
    roster_ids = sp._load_roster_ids()
    plans, pending = sp.build_episode_plans()
    errs = []
    for ep_plan in plans:
        errs += check_component_order(ep_plan)
        errs += check_driver_reveal_cap(ep_plan, bible18)
        errs += check_cast_count(ep_plan)
        errs += check_characters_present(ep_plan, roster_ids)
        errs += check_driver_clue_weight(ep_plan)
        errs += check_scene_function_present(ep_plan)
    return errs, plans, pending


def main():
    print(f"=== STORY PLAN SCHEMA CHECK v{__version__} (G6b D6a) ===")
    errs, plans, pending = run_checks()
    print(f"  episode_plan kiem tra: {len(plans)} (day du that) + {len(pending)} pending (khong bia)")
    for e in errs:
        print(f"  [FAIL] {e}")
    if errs:
        print(f"=== FAIL — {len(errs)} vi pham ===")
        return 1
    print("=== PASS — 0 vi pham ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
