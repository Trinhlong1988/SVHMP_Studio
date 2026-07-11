"""story_planner.py — G6b D5: manager toi thieu, doc 3 nguon bible + event ledger
(KHONG sinh van ban tap, KHONG tu quyet ratio/pacing - do la decision_engine/G6a).
G6b-1 sync 10/7: KHONG doc timeline/world/supernatural domain (blueprint_domains.yaml
dependencies dong bo lai chi con [character, event] cho khop code that).

Build:
  - season_plan: DAY DU 3 entry that (bible/01_series_bible season boundary + bible/18
    budget_curve phase overlap + project_config.distribution) - khong co gap du lieu.
  - episode_plan + scene: DAY DU that cho EP01 (golden text, parse boi calibrate_decision_
    policy.parse_sections()) + EP02-11 (TU CHINH 12/7, per Mr.Long authorization, TASK_STORY_
    PLANNER_EP02_11_PILOT.md - xem build_episode_plan_ep02_11(), parser rieng parse_sections_
    v2() cho format header that "# TEN [section N ...]" cua output/ep_02..11/episode.md).
    Cac tap 12-50 (con lai trong 50 tap da mine o event_ledger_draft.yaml) CHUA doc/xac nhan
    cung format - story_planner tra ve "pending" ro ly do, KHONG bia so cho du field (R195).
"""
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import calibrate_decision_policy as cdp  # noqa: E402 - tai dung parse_sections (R211, khong viet lai)

BIBLE_18 = REPO / "bible" / "18_driver_reveal_budget.yaml"
BIBLE_13_SETTING = REPO / "bible" / "13_setting_library.yaml"
BIBLE_11_REGRET = REPO / "bible" / "11_regret_catalog.yaml"
BIBLE_01_SERIES = REPO / "bible" / "01_series_bible.yaml"
PROJECT_CONFIG = REPO / "project_config.yaml"
ROSTER = REPO / "runtime" / "passenger_roster_100.yaml"
EVENT_LEDGER = REPO / "runtime" / "event_ledger_draft.yaml"
GOLDEN_EP01 = REPO / "output" / "ep_01" / "episode_golden_text.md"
OUTPUT_DIR = REPO / "output"

# DEBT-014 (10/7, per Mr.Long authorization, mapping CHOT 16:00 10/7 dua tren doc
# TRUC TIEP output/ep_01/episode_golden_text.md dong 96-515 - KHONG suy doan): moi
# component_ref (bible/01, 6 section co dinh) map DUNG 1 scene_function (story_plan_
# schema.yaml, 4 gia tri enum). Bang nay CHI dung cho EP01 (golden that da doc) - CAM
# tai su dung cho tap khac khi chua co nguon doc tuong tu (R195 khong bia).
EP01_COMPONENT_SCENE_FUNCTION = {
    "HOOK": "gay_nghi",
    "SETUP": "gay_nghi",
    "INCIDENT": "dan_chuyen",
    "REVEAL": "hy_sinh",
    "PAYOFF": "dan_chuyen",
    "CLIFFHANGER": "danh_lac_huong",
}

__version__ = "1.0.0"

# bible/18 budget_curve phase (ten + range that, doc truc tiep tu file - khong bia)
BIBLE18_PHASE_RANGES = [
    ("ESTABLISH", 1, 20), ("MYSTERY", 21, 40), ("ESCALATION", 41, 60),
    ("REVELATION", 61, 72), ("PIVOT", 73, 73), ("AFTERMATH", 74, 89), ("FINALE", 90, 90),
]
KPI_BUCKETS = [("ep_1_10", 1, 10), ("ep_11_30", 11, 30), ("ep_31_90", 31, 90)]  # DEBT-012 10/7: hardcode CHU Y (chi map ep->ten bucket, KHONG doc gia tri target). bible/16 IMMUTABLE do Publisher P7/P8/P9 doc (bible/16:3), story_planner KHONG doc - da xoa hang chet BIBLE_16_KPI + claim source_of_truth bible/16


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
            "location_ref": ep01_events["primary_event"]["stop_location"]["value"],  # audit ML #16 (10/7): doc DONG tu event_ledger (bien ep01_events dong 101), KHONG hardcode literal (truoc 'Cau Long Bien' - R195 khop ngau nhien, drift neu ledger doi)
            "scene_function": EP01_COMPONENT_SCENE_FUNCTION[s["name"]],  # DEBT-014 (10/7, per Mr.Long authorization): mapping CHOT tu doc truc tiep golden text, KHONG bia
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


# ============================================================
# EP02-11 PILOT (TASK_STORY_PLANNER_EP02_11_PILOT.md, per Mr.Long authorization 12/7,
# TU CHINH domain story_planner LOCKED - xem architecture_registry.yaml dong story_planner).
# KHAC EP01 (golden text dung header "## N. TEN", parse boi calibrate_decision_policy):
# output/ep_02..ep_11/episode.md dung header that "# TENSECTION [section N ...]" - can parser
# MOI (Buoc 1 task doc), KHONG sua parse_sections() cua calibrate_decision_policy (domain khac).
# ============================================================

COMPONENT_ORDER_V2 = ["HOOK", "SETUP", "INCIDENT", "REVEAL", "PAYOFF", "CLIFFHANGER"]
_SECTION_HEADER_RE_V2 = re.compile(r"^# ([A-Z]+) \[section (\d+)")


def parse_sections_v2(ep_number):
    """Buoc 1 TASK_STORY_PLANNER_EP02_11_PILOT.md: parser MOI cho format header that
    output/ep_{N}/episode.md (# TENSECTION [section N ...], N=2..11 da tu grep xac nhan 6/6
    header du + dung thu tu tren ca 10 tap). Tra ve list 6 dict {name, line, body} dung thu tu
    HOOK->SETUP->INCIDENT->REVEAL->PAYOFF->CLIFFHANGER (BP7 invariant). Raise ValueError neu
    thieu/thua/sai thu tu - KHONG am tham bo qua (R195, khong bia du lieu neu file that khac
    ky vong)."""
    path = OUTPUT_DIR / f"ep_{ep_number:02d}" / "episode.md"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    headers = []
    for i, line in enumerate(lines):
        m = _SECTION_HEADER_RE_V2.match(line)
        if m:
            headers.append({"name": m.group(1), "line": i})
    got_order = [h["name"] for h in headers]
    if got_order != COMPONENT_ORDER_V2:
        raise ValueError(
            f"ep_{ep_number:02d}: component order that {got_order} != {COMPONENT_ORDER_V2} "
            "(BP7 invariant vi pham - xem output/ep_{:02d}/episode.md that)".format(ep_number)
        )
    for i, h in enumerate(headers):
        start = h["line"] + 1
        end = headers[i + 1]["line"] if i + 1 < len(headers) else len(lines)
        h["body"] = "\n".join(lines[start:end])
    return headers


# Buoc 2 (DEBT-014-style, doc truc tiep - KHONG ap may moc bang EP01_COMPONENT_SCENE_FUNCTION):
# da tu doc TOAN VAN ca 10 tap (output/ep_02..ep_11/episode.md) va xac nhan DOC LAP cau truc
# 6-beat GIONG NHAU tren ca 10 tap (format templated "1 tap = 1 hanh khach len xe dem"):
#   HOOK: gioi thieu xe + bac tai + hanh khach len xe (vd ep_02 dong 74-89 "Mot co gai... Tay
#     trai co om mot cuon vai") -> tao cau hoi "ai day, mang gi" = gay_nghi.
#   SETUP: mo ta chi tiet vat + driver tic (nhip ngon/lien guong) + ong cu radio, CHUA co bien
#     co (vd ep_02 dong 92-110) -> tiep tuc dan nghi = gay_nghi (giong HOOK, chua dan chuyen).
#   INCIDENT: bien co sieu nhien xuc tac - hanh khach nhin thay canh ngoai xe khoi voi tiec
#     nuoi + dong ho nhich + driver liec guong lau hon (vd ep_02 dong 114-134) -> day mach
#     truyen sang hoi tuong = dan_chuyen.
#   REVEAL: hanh khach ke toan bo hoi uc/tiec nuoi + hon xuat hien trong guong + cau hoi chuan
#     "Con da nho ra chua?" (vd ep_02 dong 138-194) - noi dung mat mat/tiec nuoi cot loi cua
#     tap = hy_sinh.
#   PAYOFF: tiep tuc/ket thuc hoi uc + xe toi nga ba + hanh khach xuong xe (vd ep_02 dong
#     198-262) - noi tiep dan_chuyen cua INCIDENT, dua toi ket = dan_chuyen.
#   CLIFFHANGER: chuyen huong ve Khai Phong (POV co dinh) + driver nhin lau hon + goi mo tap
#     sau, KHONG giai quyet gi moi (vd ep_02 dong 266-294) = danh_lac_huong.
# Da doc xac nhan tuong tu cho ep_03..ep_11 (bao gom bien the EP07-11 co them cau thoai bac tai
# ngoai "2 cau chuan" - xem TECH_DEBT.md DEBT-030, KHONG anh huong ket luan scene_function vi
# do la NOI DUNG duoc ke trong REVEAL/CLIFFHANGER, khong doi VAI TRO KE CHUYEN cua scene).
EP02_11_SCENE_FUNCTION_BY_COMPONENT = {
    "HOOK": "gay_nghi",
    "SETUP": "gay_nghi",
    "INCIDENT": "dan_chuyen",
    "REVEAL": "hy_sinh",
    "PAYOFF": "dan_chuyen",
    "CLIFFHANGER": "danh_lac_huong",
}

# Buoc 4: cast_count - KHONG co nguon roster PAS_id lien tuc 5-8/tap that (character_balance_
# report.py tu nhan "Roster chi track FOCAL/ep; secondary cast (5-8/tap) CHUA quan ly" - xem
# note_secondary_cast trong tool do). Dem THAT nhan vat xuat hien tren canh moi tap (doc truc
# tiep 10/10 output/ep_02..ep_11/episode.md, CUNG phuong phap bible/31_golden_samples.yaml
# characters_locked dung cho EP01 - dem nhan vat XUAT HIEN, khong yeu cau moi nguoi co PAS_id):
# (1) Khai Phong (POV co dinh, ngoi ghe 3 xuyen 10 tap) (2) bac tai (CHAR_DRIVER)
# (3) hanh khach chinh (passenger_main) (4) ong cu ghe dau voi radio xua (xuat hien 10/10 tap,
# vd ep_02 dong 104, ep_11 dong 85) (5) hon/bong nguoi than hien trong guong REVEAL/PAYOFF (vd
# ep_02 dong 174, ep_11 dong 219) = 5 nguoi/tap, nam trong [5,8] BP2 invariant.
EP02_11_CAST_COUNT = 5

PAS_ID_RE = re.compile(r"PAS_\d{4}")

# Buoc 2: mapping prefix regret_sub -> pillar, GROUNDED tu bible/11_regret_catalog.yaml (khoa
# "pillars.family_regret" chua cac id "REG_FAM_00X" - xem bible/11 dong 21-61). Batch EP02-11
# CHI dung REG_FAM (da tu grep xac nhan qua event_ledger_draft.yaml) nen chi can 1 entry - KHONG
# tu bia them prefix chua gap (REG_LOVE/REG_PROMISE/... se can bo sung khi gap that, R195).
REGRET_SUB_PREFIX_TO_PILLAR = {
    "REG_FAM": "family_regret",
}


def _regret_pillar_from_regret_sub(regret_sub_value):
    """Tra ve pillar that (vd 'family_regret') tu prefix cua regret_sub_value (vd
    'REG_FAM_001 - Me doi con ve Tet...'), hoac None neu prefix chua co trong mapping THAT
    (KHONG bia - R195)."""
    if not regret_sub_value:
        return None
    for prefix, pillar in REGRET_SUB_PREFIX_TO_PILLAR.items():
        if regret_sub_value.startswith(prefix):
            return pillar
    return None


# Buoc 3: driver_clue baseline - CHI mine 3 loai weight_1_micro DA CO VI DU CHINH XAC trong
# bible/18_driver_reveal_budget.yaml (clue_weight_taxonomy.weight_1_micro.examples, dong
# 144-151): "Bac tai nhin guong chieu hau truoc khi noi." / "Bac tai hai tay vo-lang." /
# "Gang tay trang." Day CHINH LA 3 clue da tinh vao ep_01_reference.cumulative_after_ep01=3%
# (dem lai: 4 muc trong driver_clues_in_ep01 nhung 1 muc la "2 cau chuan" - hoi thoai co dinh
# SERIES_RULES, KHONG phai driver_clue lam lo thong tin moi - 3 muc con lai x weight 1 = 3%,
# khop dung cumulative_after_ep01). KHONG tu gan weight_2_minor/weight_5_moderate cho bat ky
# noi dung nao khac du co xuat hien (vd "bac tai liec guong lau hon", cau thoai bac tai vuot
# "2 cau chuan" o EP07-11) - day la quyet dinh san pham/kien truc, ghi TECH_DEBT.md DEBT-030
# de Mr.Long xac nhan, KHONG tu quyet (R_SUPREME R1/R10).
_DRIVER_CLUE_SENTENCE_RE = re.compile(r"[^.]*(?:nhìn|liếc) gương(?: chiếu hậu)?[^.]*\.")


def _driver_baseline_clue_citation(scene_body):
    """Tra ve {'weight':1,'content':...} neu tim thay cau mo ta driver nhin/liec guong that
    trong body cua scene (trich dan nguyen van, khong bia), hoac None neu khong co."""
    m = _DRIVER_CLUE_SENTENCE_RE.search(scene_body)
    if not m:
        return None
    return {"weight": 1, "content": m.group(0).strip()}


def build_episode_plan_ep02_11(ep_number):
    """Buoc 2-4 TASK_STORY_PLANNER_EP02_11_PILOT.md: field-hoa 1 tap (2<=ep_number<=11) tu du
    lieu THAT da mine (runtime/event_ledger_draft.yaml) + doc truc tiep output/ep_{N}/episode.md
    that (frontmatter + 6 section that). KHONG bia field nao thieu nguon (R195) - field thieu
    nguon tra None/[] + ghi ly do vao 'pending_fields' (debug field bo sung, khong pha schema -
    cung pattern 'scenes_detail'/'calibrated_from' cua build_episode_plan_ep01())."""
    if not (2 <= ep_number <= 11):
        raise ValueError(f"build_episode_plan_ep02_11 chi ho tro ep_number 2..11, nhan {ep_number}")

    ep_key = f"ep_{ep_number:02d}"
    event_ledger = _load(EVENT_LEDGER)
    ev = event_ledger["events"][ep_key]["primary_event"]
    bible18 = _load(BIBLE_18)
    bible13 = _load(BIBLE_13_SETTING)
    roster_ids = _load_roster_ids()

    headers = parse_sections_v2(ep_number)  # raise neu thu tu sai (BP7 invariant)

    pending_fields = []

    # passenger_main -> PAS_id (co the None neu khong co PAS_id that, vd ep_11)
    passenger_main_field = ev.get("passenger_main") or {}
    passenger_main_raw = passenger_main_field.get("value")
    passenger_pas_id = None
    if passenger_main_raw:
        m = PAS_ID_RE.search(passenger_main_raw)
        if m:
            candidate = m.group(0)
            if candidate in roster_ids:
                passenger_pas_id = candidate
    if passenger_main_raw and not passenger_pas_id:
        pending_fields.append({
            "field": "characters_present (passenger_main)",
            "reason": (
                f"event_ledger_draft.yaml passenger_main = '{passenger_main_raw}' KHONG co "
                "PAS_id dang PAS_XXXX resolve duoc trong runtime/passenger_roster_100.yaml "
                "(vd ep_11 dung mo ta POV-shift 'nu_45 -> nam 26 Duc Ha Dong', khong phai PAS_"
                "id). characters_present chi duoc chua PAS_id THAT ton tai trong roster (check_"
                "characters_present, story_plan_schema_check.py) - de trong, KHONG tu gan PAS_id "
                "doan (R195)."
            ),
        })

    # regret_pillars_covered - tu regret_sub (event_ledger), KHONG tu dung frontmatter field
    # 'regret_pillar'/'pillar' (template khac nhau EP02-10 vs EP11, R195 chi theo dung nguon
    # task doc chi dinh "tu regret_sub")
    regret_sub_field = ev.get("regret_sub")
    regret_sub_value = regret_sub_field.get("value") if regret_sub_field else None
    pillar = _regret_pillar_from_regret_sub(regret_sub_value)
    regret_pillars_covered = [pillar] if pillar else []
    if not regret_sub_value:
        pending_fields.append({
            "field": "regret_pillars_covered",
            "reason": (
                f"event_ledger_draft.yaml events.{ep_key}.primary_event.regret_sub = null "
                "(chua mine). De trong TRUNG THUC, KHONG tu suy doan/gan (R195, dung nguyen "
                "van chi dan TASK_STORY_PLANNER_EP02_11_PILOT.md Buoc 2 cho ep_11)."
            ),
        })

    # location_ref - task doc chi dinh doi chieu stop_location voi bible/13_setting_library.
    # Da tu grep xac nhan: bible/13 CHI co 20 setting mood/thoi tiet/boi canh (setting_mua_nho..
    # setting_phong_doi_benh_vien), KHONG co entry nao la dia danh vat ly (0/20 khop chu "nga
    # ba"). stop_location that (vd 'nga ba Phu Yen (que Ha Dieu, vung dong bang)') la dia danh
    # vat ly - KHONG co entry bible/13 nao khop => location_ref de pending cho CA 10 tap, dung
    # nguyen van "neu khong khop, de pending + ly do, KHONG tu tao setting moi" cua task doc.
    stop_location_field = ev.get("stop_location") or {}
    stop_location_raw = stop_location_field.get("value")
    signature_setting_field = ev.get("signature_setting") or {}
    signature_setting_raw = signature_setting_field.get("value")
    location_ref = None
    setting_ids = bible13.get("setting_library", {})
    pending_fields.append({
        "field": "location_ref",
        "reason": (
            f"stop_location that = '{stop_location_raw}' la dia danh vat ly (nga ba...), doi "
            "chieu 20 key that trong bible/13_setting_library.yaml#setting_library (setting_"
            "mua_nho..setting_phong_doi_benh_vien, deu la setting mood/thoi tiet/boi canh) - 0 "
            "khop (da tu grep xac nhan). KHONG tu tao setting moi (R195, dung nguyen van task "
            "doc). GHI CHU rieng (KHONG tu quyet dinh thay doi field): signature_setting = "
            f"'{signature_setting_raw}' LAI khop 100% dung format id bible/13 ("
            f"{'CO trong bible/13' if signature_setting_raw in setting_ids else 'KHONG trong bible/13'}"
            ") - co the day la nguon dung cho location_ref thay vi stop_location, nhung task "
            "doc chi dinh ro 'tu stop_location' nen KHONG tu doi nguon - can Mr.Long xac nhan."
        ),
    })

    # scenes_detail: 6 scene, dung parse_sections_v2() + EP02_11_SCENE_FUNCTION_BY_COMPONENT
    scenes = []
    for i, h in enumerate(headers, start=1):
        scene_id = f"EP{ep_number}_SC{i}"
        characters_present = [passenger_pas_id] if (passenger_pas_id and h["name"] != "CLIFFHANGER") else []
        driver_clue = _driver_baseline_clue_citation(h["body"]) if h["name"] == "SETUP" else None
        scenes.append({
            "scene_id": scene_id,
            "episode_ref": ep_number,
            "order_in_episode": i,
            "component_ref": h["name"],
            "summary": f"{h['name']} section cua {ep_key} (dong {h['line'] + 1}, output/{ep_key}/episode.md)",
            "location_ref": location_ref,
            "characters_present": characters_present,
            "scene_function": EP02_11_SCENE_FUNCTION_BY_COMPONENT[h["name"]],
            "driver_clue": driver_clue,
        })

    # driver_reveal_cumulative: GIU 3 (khong doi tu EP01) - cumulative_reveal_score la % LUY KE
    # xuyen CA SERIES toi ep N (bible/18 dong 18 "max % driver mystery exposed toi ep N"), 3
    # loai weight_1_micro (gang/vo-lang/guong) DA duoc tinh vao cumulative_after_ep01=3% roi;
    # doc lai toan van 10 tap (output/ep_02..ep_11/episode.md) xac nhan KHONG co loai clue MOI
    # nao (ngoai 3 loai da tinh) duoc gioi thieu - cac bien the tu ngu (vd EP09/EP10 khong noi
    # ro "vo-lang", EP11 khong noi "gang tay") van CHI la mo ta LAI hanh vi da biet, KHONG lam
    # lo THEM thong tin => cumulative KHONG tang. Cau thoai bac tai vuot "2 cau chuan" (EP07-11)
    # CHUA duoc gan weight (xem TECH_DEBT.md DEBT-030, can Mr.Long quyet dinh truoc khi field-
    # hoa chinh thuc vao model nay).
    driver_reveal_cumulative = bible18["ep_01_reference"]["cumulative_after_ep01"]
    cap = None
    for key, block in bible18["budget_curve"].items():
        if key == "ep_1_to_20":
            cap = block.get("cumulative_cap")
            break
    if cap is not None and driver_reveal_cumulative > cap:
        raise ValueError(
            f"{ep_key}: driver_reveal_cumulative {driver_reveal_cumulative}% > cap {cap}% "
            "(bible/18 budget_curve.ep_1_to_20) - BLOCK, khong tu noi cap (task doc Buoc 3)."
        )

    return {
        "episode_number": ep_number,
        "season_ref": "season_1",
        "scenes": [sc["scene_id"] for sc in scenes],
        "scenes_detail": scenes,
        "driver_reveal_cumulative": driver_reveal_cumulative,
        "cast_count": EP02_11_CAST_COUNT,
        "regret_pillars_covered": regret_pillars_covered,
        "kpi_ep_range_ref": kpi_bucket_for_ep(ep_number),
        "pending_fields": pending_fields,
        "calibrated_from": {
            "scenes": f"output/{ep_key}/episode.md (parse_sections_v2, header that '# TEN [section N ...]')",
            "driver_reveal_cumulative": f"bible/18_driver_reveal_budget.yaml#ep_01_reference.cumulative_after_ep01 = {driver_reveal_cumulative} (giu nguyen, xem comment ham)",
            "cast_count": f"doc truc tiep output/{ep_key}/episode.md (dem 5 nhan vat xuat hien tren canh - xem comment EP02_11_CAST_COUNT)",
            "regret_pillars_covered": f"runtime/event_ledger_draft.yaml#events.{ep_key}.primary_event.regret_sub (prefix -> bible/11 pillar)",
        },
    }


PENDING_REASON_EP02_50 = (
    "runtime/event_ledger_draft.yaml (G4 D2) co du lieu regret_sub/signature_object/"
    "passenger_main/stop_location cho ep_02..ep_50, NHUNG (tinh tu TU CHINH 12/7 EP02-11 pilot,"
    " TASK_STORY_PLANNER_EP02_11_PILOT.md) CHI ep_02..ep_11 da co component_ref per-scene that "
    "(header '# TEN [section N ...]' trong output/ep_02..11/episode.md, xac nhan 6/6 dung thu "
    "tu). ep_12..ep_50 CHUA duoc xac nhan cung format (chua doc), va TOAN BO 12..50 van CHUA co "
    "driver_reveal_cumulative per-episode that rieng (dung 3% baseline ke thua EP01, xem "
    "build_episode_plan_ep02_11() cho ep_02-11; ep_12+ can doc lai truoc khi ap dung cung cach). "
    "Bia cac truong nay cho ep_12-50 se vi pham R195 - story_planner tra ve pending, KHONG tu tinh."
)


def build_episode_plans():
    """Tra ve (plans_da_xay, pending_list). EP01 + EP02-11 (TU CHINH 12/7 pilot) xay duoc day
    du that; ep_12..ep_50 van pending (chua doc/xac nhan format tuong tu)."""
    plans = [build_episode_plan_ep01()]
    plans += [build_episode_plan_ep02_11(n) for n in range(2, 12)]
    event_ledger = _load(EVENT_LEDGER)
    built_eps = {"ep_01"} | {f"ep_{n:02d}" for n in range(2, 12)}
    pending = [{"episode_number": int(k.split("_")[1]), "reason": PENDING_REASON_EP02_50}
               for k in sorted(event_ledger["events"]) if k not in built_eps]
    return plans, pending


def main():
    print(f"=== story_planner v{__version__} (G6b D5) ===")
    seasons = build_season_plan()
    print(f"season_plan: {len(seasons)} entry that")
    for s in seasons:
        print(f"  {s['season_id']}: ep{s['episode_range']} phases={s['driver_phase_refs']}")

    plans, pending = build_episode_plans()
    print(f"episode_plan da xay DAY DU: {len(plans)} (EP01 + EP02-11 pilot, xem code comment ly do)")
    print(f"episode_plan PENDING (khong bia): {len(pending)} tap (ep_12..ep_50)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
