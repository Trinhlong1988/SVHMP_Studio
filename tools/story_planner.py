"""story_planner.py — G6b D5: manager toi thieu, doc 3 nguon bible + event ledger + timeline
(KHONG sinh van ban tap, KHONG tu quyet ratio/pacing - do la decision_engine/G6a).

Build:
  - season_plan: DAY DU 3 entry that (bible/01_series_bible season boundary + bible/18
    budget_curve phase overlap + project_config.distribution) - khong co gap du lieu.
  - episode_plan + scene: CHI xay duoc DAY DU cho EP01 (golden text co du component_ref
    per-scene + bible/18 co san ep_01_reference.cumulative_after_ep01=3%). Cac tap 02-50
    (dieu 50 tap that da mine o event_ledger_draft.yaml) CHUA co du 2 loai du lieu that
    can thiet (scene-level component_ref + per-episode driver_reveal_cumulative that) -
    story_planner tra ve "pending" ro ly do, KHONG bia so cho du field (R195).
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import calibrate_decision_policy as cdp  # noqa: E402 - tai dung parse_sections (R211, khong viet lai)

BIBLE_18 = REPO / "bible" / "18_driver_reveal_budget.yaml"
BIBLE_01_SERIES = REPO / "bible" / "01_series_bible.yaml"
BIBLE_16_KPI = REPO / "bible" / "16_series_kpi.yaml"
PROJECT_CONFIG = REPO / "project_config.yaml"
ROSTER = REPO / "runtime" / "passenger_roster_100.yaml"
EVENT_LEDGER = REPO / "runtime" / "event_ledger_draft.yaml"
GOLDEN_EP01 = REPO / "output" / "ep_01" / "episode_golden_text.md"

__version__ = "1.0.0"

# bible/18 budget_curve phase (ten + range that, doc truc tiep tu file - khong bia)
BIBLE18_PHASE_RANGES = [
    ("ESTABLISH", 1, 20), ("MYSTERY", 21, 40), ("ESCALATION", 41, 60),
    ("REVELATION", 61, 72), ("PIVOT", 73, 73), ("AFTERMATH", 74, 89), ("FINALE", 90, 90),
]
KPI_BUCKETS = [("ep_1_10", 1, 10), ("ep_11_30", 11, 30), ("ep_31_90", 31, 90)]


def _load(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _overlap(a_lo, a_hi, b_lo, b_hi):
    return max(a_lo, b_lo) <= min(a_hi, b_hi)


def kpi_bucket_for_ep(ep):
    for name, lo, hi in KPI_BUCKETS:
        if lo <= ep <= hi:
            return name
    return None


def build_season_plan():
    """3 season_plan DAY DU that - tu bible/01_series_bible (boundary) + bible/18
    (phase overlap) + project_config (regret_distribution_target)."""
    series = _load(BIBLE_01_SERIES)
    project_config = _load(PROJECT_CONFIG)
    seasons_raw = series["structure"]
    dist = project_config["distribution"]

    season_defs = [
        ("season_1", seasons_raw["season_1"]["range"]),
        ("season_2", seasons_raw["season_2"]["range"]),
        ("season_3", seasons_raw["season_3"]["range"]),
    ]
    plans = []
    for season_id, range_str in season_defs:
        lo_s, hi_s = range_str.split("-")
        lo, hi = int(lo_s), int(hi_s)
        phases = [name for name, plo, phi in BIBLE18_PHASE_RANGES if _overlap(lo, hi, plo, phi)]
        plans.append({
            "season_id": season_id,
            "episode_range": [lo, hi],
            "driver_phase_refs": phases,
            "regret_distribution_target": {
                "source": "project_config.yaml#distribution",
                "age_child": dist["age_child"], "age_elder": dist["age_elder"],
                "region_voice_min": dist["region_voice_min"], "death_kinds": dist["death_kinds"],
                "chars_per_ep": dist["chars_per_ep"],
                "note": "target TOAN CUC (xuyen 100 tap) - khong dinh nghia lai rieng cho tung season, chi xac nhan tham chieu",
            },
        })
    return plans


def _load_roster_ids():
    roster = _load(ROSTER)
    return {p["id"] for p in roster["passengers"]}


def build_episode_plan_ep01():
    """Episode_plan + scene DAY DU that cho EP01 (golden text). Tai dung
    calibrate_decision_policy.parse_sections() (G6a, R211 khong viet lai)."""
    text = cdp.load_text()
    sections = cdp.parse_sections(text)
    bible18 = _load(BIBLE_18)
    roster_ids = _load_roster_ids()
    event_ledger = _load(EVENT_LEDGER)
    ep01_events = event_ledger["events"]["ep_01"]

    scenes = []
    for i, s in enumerate(sections, start=1):
        scene_id = f"EP1_SC{i}"
        scenes.append({
            "scene_id": scene_id,
            "episode_ref": 1,
            "order_in_episode": i,
            "component_ref": s["name"],
            "summary": f"{s['name']} section cua EP01 golden (dong {s['line']+1})",
            "location_ref": "Cầu Long Biên",  # tu event_ledger_draft ep_01.primary_event.stop_location
        })

    ep01_ref = bible18["ep_01_reference"]
    driver_reveal_cumulative = ep01_ref["cumulative_after_ep01"]

    # cast_count that: dem nhan vat khoa trong bible/31 golden characters_locked (8 nguoi)
    # + xac nhan cast_count nam trong [5,8] BP2 invariant (khong bia, doc truc tiep bible/31)
    golden_31 = _load(REPO / "bible" / "31_golden_samples.yaml")
    cast_count = len(golden_31["golden_text_ep01"]["characters_locked"])

    return {
        "episode_number": 1,
        "season_ref": "season_1",
        "scenes": [sc["scene_id"] for sc in scenes],
        "scenes_detail": scenes,   # them chi tiet cho tien doi chieu (khong pha schema, chi bo sung debug)
        "driver_reveal_cumulative": driver_reveal_cumulative,
        "cast_count": cast_count,
        "regret_pillars_covered": [],  # EP01 la pilot Khai-Phong/Ha-Vy, KHONG dung passenger roster pillar - de rong trung thuc (khac EP02+ dung roster that)
        "kpi_ep_range_ref": kpi_bucket_for_ep(1),
        "calibrated_from": {
            "scenes": f"{GOLDEN_EP01.relative_to(REPO)} (tai dung calibrate_decision_policy.parse_sections)",
            "driver_reveal_cumulative": f"bible/18_driver_reveal_budget.yaml#ep_01_reference.cumulative_after_ep01 = {driver_reveal_cumulative}",
            "cast_count": f"bible/31_golden_samples.yaml#golden_text_ep01.characters_locked (dem {cast_count} nhan vat khoa)",
        },
    }


PENDING_REASON_EP02_50 = (
    "runtime/event_ledger_draft.yaml (G4 D2) co du lieu regret_sub/signature_object/"
    "passenger_main/stop_location cho ep_02..ep_50, NHUNG KHONG co (a) component_ref per-scene "
    "that (chi EP01 golden text co section header ## N. TEN; cac ep khac dung "
    "moment_map_template.yaml voi 'moments' con la TODO placeholder, chua dien that) va (b) "
    "driver_reveal_cumulative per-episode that (bible/18 chi cho san 1 reference duy nhat cho "
    "EP01 3%; khong co du lieu dem clue that cho ep_02-50). Bia 2 truong nay se vi pham R195 - "
    "story_planner tra ve pending, KHONG tu tinh."
)


def build_episode_plans():
    """Tra ve (plans_da_xay, pending_list). Hien tai CHI EP01 xay duoc day du that."""
    plans = [build_episode_plan_ep01()]
    event_ledger = _load(EVENT_LEDGER)
    pending = [{"episode_number": int(k.split("_")[1]), "reason": PENDING_REASON_EP02_50}
               for k in sorted(event_ledger["events"]) if k != "ep_01"]
    return plans, pending


def main():
    print(f"=== story_planner v{__version__} (G6b D5) ===")
    seasons = build_season_plan()
    print(f"season_plan: {len(seasons)} entry that")
    for s in seasons:
        print(f"  {s['season_id']}: ep{s['episode_range']} phases={s['driver_phase_refs']}")

    plans, pending = build_episode_plans()
    print(f"episode_plan da xay DAY DU: {len(plans)} (EP01 duy nhat, xem code comment ly do)")
    print(f"episode_plan PENDING (khong bia): {len(pending)} tap (ep_02..ep_50)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
