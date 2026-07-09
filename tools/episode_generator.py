"""tools/episode_generator.py — G7 D2 (9/7): manager RAP packet tu 14 domain that
thanh 1 EPISODE PACKET (cau truc trung gian dung governance/blueprint/schemas/
episode_schema.yaml, D1) - KHONG viet van ban tu su (prose): buoc do van la CMD
prompt-based (nguoi + LLM theo prompts/generator.md, xem BP0 domain generator
responsibility "Episode hien sinh boi CMD prompt-based, chua dong goi thanh tool
tai lap duoc"). episode_generator.py CHI RAP DU LIEU THAT lam dau vao cho buoc do,
dung 12-knob budget cua decision_engine + ke hoach cua story_planner, KHONG tu
quyet ratio/pacing/noi dung moi (viec do la decision_engine, xem TASK_G7 D2).

Pham vi v1 (verify Test-Path/API that 9/7, xem PING_CMD_LEAD): CHI ep_number=1 xay
duoc DAY DU packet - EP01 la episode DUY NHAT co du du lieu that o ca 14 domain de
doi chieu (story_planner.build_episode_plan_ep01() + bible/09/12/13/21 co gia tri
that cho ep 1). ep_number khac tra ve pending + ly do that (mirror pattern
story_planner.build_episode_plans(), KHONG bia).

R211 Promotion Gate: decision_engine domain lifecycle=draft (blueprint_domains.yaml),
KHONG phai approved - packet nay ghi ro canh bao, KHONG gia vo la du dieu kien.

4/14 domain (weather/culture/belief/ritual) CHUA co bat ky file bible nao tren dia
(Test-Path verified 9/7) - tra ve no_data_source, KHONG bia.
5/14 domain (world/timeline/location/supernatural/object) manager code CHUA co
(status planned) NHUNG bible nguon DA ton tai + approved - doc TRUC TIEP file.

KHONG tao nhan vat/vat pham moi (bible/03/12 CAM) - CHI doc.
KHONG ghi vao 14 domain nguon (forbidden_operations: write, bp1/interface_contracts.yaml).
KHONG tu phong PASS (qa_runtime/auditor lam). KHONG render (production lam).
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import decision_engine  # noqa: E402 - tai dung, khong viet lai (R211)
import story_planner  # noqa: E402 - tai dung, khong viet lai (R211)
from character_manager import CharacterRegistry  # noqa: E402
from dialogue_manager import DialogueManager  # noqa: E402

__version__ = "1.0.0"

BIBLE_09 = REPO / "bible" / "09_emotion_intensity.yaml"
BIBLE_12 = REPO / "bible" / "12_object_library.yaml"
BIBLE_13 = REPO / "bible" / "13_setting_library.yaml"
BIBLE_21 = REPO / "bible" / "21_series_arc_design.yaml"
SCAFFOLD = REPO / "prompts" / "ep_scaffold_template.md"

MILESTONE_EPS = [10, 20, 30, 40, 50, 60, 70, 80, 90]

# 4/14 domain KHONG co bat ky nguon du lieu nao tren dia (Test-Path verified 9/7,
# bible file chinh chua ton tai - status: planned trong blueprint_domains.yaml).
# KHONG bia, tra ve reason that thay vi crash hoac gia lap gia tri.
NO_DATA_DOMAINS = {
    "weather": "bible/41_weather_bible.yaml chua ton tai tren dia (blueprint_domains.yaml: status planned)",
    "culture": "bible/38_culture_bible.yaml chua ton tai tren dia (status planned)",
    "belief": "bible/39_belief_bible.yaml chua ton tai tren dia (status planned)",
    "ritual": "bible/40_ritual_bible.yaml chua ton tai tren dia (status planned)",
}

# 5/14 domain: manager code chua co (status planned) NHUNG bible nguon DA ton tai +
# lifecycle approved -> generator doc TRUC TIEP file (khong qua manager gia lap
# vi manager that chua ton tai - Test-Path verified 9/7).
BIBLE_ONLY_DOMAINS = {
    "world": REPO / "bible" / "02_lore_db.yaml",
    "timeline": REPO / "bible" / "01_narrative_structure.yaml",
    "location": BIBLE_13,
    "supernatural": REPO / "bible" / "11_regret_catalog.yaml",
    "object": BIBLE_12,
}


def _load(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _scaffold_prompt_version():
    """prompts/ep_scaffold_template.md dong 89 - version THAT cua chinh scaffold,
    khong phai version noi dung tap (dung desc field trong episode_schema.yaml)."""
    text = SCAFFOLD.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.strip().startswith("prompt_version"):
            return line.split(":", 1)[1].strip()
    return None


def _phase_intensity_for_ep(ep_number):
    """bible/09 intensity_curve - CHI doc nguong that, khong bia. Tra ve
    (phase_name, intensity_level) hoac (None, None) neu ep ngoai pham vi curve.

    CANH BAO (ghi lai, KHONG tu sua): bible/09 dung ten "deepening"/"climactic" cho
    ep_31_60/ep_61_90, nhung episode_schema.yaml (D1, field-hoa dung ban duyet B)
    chi cho phep enum [introductory, warming, heightening, peak, climax] - 2 nguon
    LECH TEN cho 2 muc do do. EP01 (pham vi v1 duy nhat) dung "introductory" - KHOP
    ca 2 nguon nen KHONG bi chan o day; se chan that neu mo rong ep_number>30 sau
    nay - can Mr.Long doi chieu lai enum truoc khi build tiep (khong tu sua bible/09
    hay episode_schema.yaml, ca 2 deu can duyet)."""
    b09 = _load(BIBLE_09)
    ranges = [
        ("ep_1_to_10", 1, 10), ("ep_11_to_30", 11, 30),
        ("ep_31_to_60", 31, 60), ("ep_61_to_90", 61, 90),
    ]
    for key, lo, hi in ranges:
        if lo <= ep_number <= hi:
            entry = b09["intensity_curve"][key]
            return entry["name"], entry["level"]
    return None, None


def _pillar_for_ep(ep_number):
    """bible/21 pillar_interleave_ep01_50 - status file: PROPOSAL (chua Mr.Long
    duyet chinh thuc), NHUNG da dung san trong post_render_gate.py check 11 cho 50
    tap thuc te - doc that, ghi ro provenance trong packet (khong gia vo la locked)."""
    b21 = _load(BIBLE_21)
    key = f"ep_{ep_number:02d}"
    return b21.get("pillar_interleave_ep01_50", {}).get(key)


def _quang_memory_fragment_for_ep(ep_number):
    """bible/21 quang_memory_arc M1-M18 - tra ve 'M{n}' neu ep nam trong range that,
    None neu khong tim thay (khong bia)."""
    b21 = _load(BIBLE_21)
    for frag_id, data in b21.get("quang_memory_arc", {}).items():
        if ep_number in data.get("eps", []):
            return frag_id
    return None


def _callback_target_for_ep(ep_number):
    """bible/21 callback_schedule_s1 - CHI ep nao duoc khai lam SOURCE 1 callback moi
    co gia tri (vd ep_12 callback_to ep_01). ep khong trong schedule = 'none' THAT,
    khong phai thieu du lieu (EP01 tu no khong callback ve ep nao truoc do)."""
    b21 = _load(BIBLE_21)
    key = f"ep_{ep_number:02d}"
    entry = b21.get("callback_schedule_s1", {}).get(key)
    return entry["callback_to"] if entry else "none"


def _milestone(ep_number):
    return ep_number in MILESTONE_EPS


def _driver_lines(ep_number, milestone):
    """episode_schema.yaml: allowed_values [2,3] - 3 CHI hop le ep73/90/milestone."""
    return 3 if (ep_number in (73, 90) or milestone) else 2


def build_episode_frontmatter(ep_number):
    """RAP frontmatter tu cac nguon that (bible/09/12/13/21 + scaffold). CHI ho tro
    ep_number=1 day du (EP01 golden reference co du du lieu 14/14 domain de doi
    chieu) - ep khac tra ve dict {'pending': True, 'reason': ...}, KHONG bia."""
    if ep_number != 1:
        return {
            "pending": True,
            "reason": (
                "episode_generator v1 chi build day du frontmatter cho ep_number=1 "
                "(EP01 golden reference co du du lieu 14/14 domain de doi chieu). Cac "
                "ep khac can story_planner scene-level that (hien CHI EP01 xay duoc, "
                "xem story_planner.PENDING_REASON_EP02_50) truoc khi build day du - "
                "KHONG bia du lieu con thieu (R195)."
            ),
        }

    phase, intensity_level = _phase_intensity_for_ep(ep_number)
    pillar = _pillar_for_ep(ep_number)
    quang_memory_fragment = _quang_memory_fragment_for_ep(ep_number)
    callback_target = _callback_target_for_ep(ep_number)
    milestone = _milestone(ep_number)

    return {
        "prompt_version": _scaffold_prompt_version(),
        "ep_number": ep_number,
        "phase": phase,
        "pillar": pillar,
        "intensity_level": intensity_level,
        "quang_memory_fragment": quang_memory_fragment,
        "callback_target": callback_target,
        "object_sub_arc": None,  # field required:false trong schema - EP01 khong co, de None trung thuc
        "milestone": milestone,
        "passenger_main": None,  # xem "_provenance_note" - EP01 KHONG co PAS_id that (truoc he thong roster 100, verify by_ep(1)=[])
        "signature_object": "OBJ_DONG_HO_XA_CU",  # bible/12 dong 83 display_name "dong ho nu vo xa cu" khop dung
        "signature_setting": "setting_cau_dem_mua",  # bible/13 notes ghi ro "ep_01 Cau Long Bien"
        "stop_location": "Cầu Long Biên",  # tu chinh output/ep_01/episode.md that + bible/13 xac nhan
        "word_count_target": 2300,
        "bell_count": 1,
        "ghost_manifest": 1,
        "driver_lines": _driver_lines(ep_number, milestone),
        "hand_crafted": True,  # EP01 la ban CMD prompt-based cu (truoc G7), KHONG phai G7 tu sinh
        "_provenance_note": (
            "passenger_main=None: EP01 la pilot dung Khai-Phong/Ha-Vy truc tiep, KHONG "
            "dung runtime/passenger_roster_100.yaml (schema field yeu cau PAS_id that - "
            "verify CharacterRegistry().by_ep(1) = [] rong that, EP01 khong co trong "
            "roster; story_planner.py da tu ghi chu tuong tu cho regret_pillars_covered "
            "cua EP01). pillar/quang_memory_fragment/callback_target doc tu bible/21 "
            "(status file: PROPOSAL, chua Mr.Long duyet chinh thuc rieng - nhung DA dung "
            "san trong post_render_gate.py check 10-12 cho 50 tap that, ghi ro de khong "
            "gia vo day la da locked chinh thuc)."
        ),
    }


def _domain_reads():
    """Bao cao trang thai doc-duoc that cho 9/14 domain con lai (khong ke character/
    dialogue/story_planner/decision_engine da co manager rieng, xem build_episode_packet).
    KHONG bia gia tri - chi bao cao source path + status."""
    reads = {}
    for domain, path in BIBLE_ONLY_DOMAINS.items():
        reads[domain] = {"source": str(path.relative_to(REPO)), "status": "read_direct_no_manager"}
    for domain, reason in NO_DATA_DOMAINS.items():
        reads[domain] = {"source": None, "status": "no_data_source", "reason": reason}
    return reads


def build_episode_packet(ep_number):
    """Packet trung gian day du (KHONG phai episode.md prose) - RAP tat ca domain
    that theo dung bp1/interface_contracts.yaml (14 contract, allowed_operations:
    [read] CHI). Output nay la dau vao cho buoc viet prose (van con la nguoi/LLM
    theo prompts/generator.md - xem docstring module ve BP0 responsibility)."""
    frontmatter = build_episode_frontmatter(ep_number)
    if frontmatter.get("pending"):
        return {"ep_number": ep_number, "pending": True, "reason": frontmatter["reason"]}

    story_plan = None
    decision_packet = None
    if ep_number == 1:
        story_plan = story_planner.build_episode_plan_ep01()
        decision_packet = decision_engine.build_packet(ep_number, plan=story_plan)

    # character/dialogue doc-duoc that (CharacterRegistry/DialogueManager) nhung
    # EP01 khong co passenger trong roster 100 (verify by_ep(1)=[]) - ghi nhan rong
    # THAT, khong goi API voi id gia.
    registry = CharacterRegistry()
    _ = DialogueManager(registry)  # instantiate de xac nhan manager doc-duoc, EP01 khong co context de goi (khong co PAS_id that)

    return {
        "episode_frontmatter": frontmatter,
        "episode_plan_ref": story_plan,           # story_planner (lifecycle: approved)
        "decision_packet": decision_packet,        # decision_engine (lifecycle: draft - xem canh bao duoi)
        "decision_packet_lifecycle_warning": (
            None if decision_packet is None else
            "decision_engine domain lifecycle=draft trong blueprint_domains.yaml, KHONG "
            "phai approved - per audit_rule cua chinh domain generator ('Output chi dung "
            "domain lifecycle=approved, Promotion Gate R211'), packet nay la PROVISIONAL, "
            "CHUA du dieu kien de coi la nguon chinh thuc."
        ),
        "character_domain_note": (
            "EP01 khong co passenger trong runtime/passenger_roster_100.yaml (verify "
            "CharacterRegistry().by_ep(1) = [] rong that) - character/dialogue manager "
            "doc-duoc (co code that) nhung khong co context de goi cho EP01 cu the."
        ),
        "domain_reads": _domain_reads(),
        "generated_by": f"tools/episode_generator.py v{__version__}",
    }


def main():
    ep_number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    packet = build_episode_packet(ep_number)
    print(f"=== episode_generator v{__version__} — packet ep{ep_number} ===")
    print(yaml.safe_dump(packet, allow_unicode=True, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
