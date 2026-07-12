"""decision_engine.py — G6a D3: manager TOI THIEU, CHI phan doc bible/42 (KHONG sinh text).

Doc bible/42_decision_policy.yaml -> build phan packet KHONG phu thuoc story_planner
(bp6/decision_io.yaml schema). plan_ref/cast_per_scene/reveals_allowed can INPUT tu story
plan that (G6b tools/story_planner.py DA xay+locked v1.0 5/7; neu goi build_packet KHONG
truyen plan= thi de status: planned trung thuc, KHONG bia gia tri gia).
(Sua docstring 10/7 audit MEDIUM/LOW #14 - ban cu ghi "G6b CHUA xay" da loi thoi.)

Day la manager doc-only: KHONG viet logic sinh episode text.

TU CHINH 12/7 (per Mr.Long authorization, DEBT-033, TASK_DEBT030_031_CONTENT_FIX.md Buoc 4):
bible/42_decision_policy.yaml da co gia tri dialogue_ratio/narration_ratio (0.3564/0.6436)
TU LUC calibrate, nhung la SO TINH TAY dan vao YAML - build_packet() truoc day CHI doc file
tinh (khong goi lai calibrate_decision_policy.py), nen neu golden text EP01 doi sau nay, bible/
42 se DRIFT ma khong ai biet (R215 rui ro). _live_dialogue_ratio_ep01() goi THANG cdp.main()
(R211, khong viet lai cong thuc dem word-count) de lay gia tri SONG, OVERRIDE 2 knob nay trong
per_scene[].knobs cho ep_number==1 - dam bao packet luon phan anh dung calibrate_decision_
policy.py THAT tai thoi diem build, khong phu thuoc YAML tinh co the loi thoi.
"""
import contextlib
import io
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
POLICY_PATH = REPO / "bible" / "42_decision_policy.yaml"

_TOOLS = str(REPO / "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
import calibrate_decision_policy as cdp  # noqa: E402 - tai dung cong thuc dem word-count (R211)

__version__ = "1.0.0"


def _live_dialogue_ratio_ep01():
    """DEBT-033: goi THANG cdp.main() (golden EP01, R211 khong viet lai cong thuc) de lay
    dialogue_ratio/narration_ratio SONG. Nen stdout (cdp.main() in verbose) de khong spam
    log moi lan build_packet() duoc goi. Tra ve (dialogue_ratio, narration_ratio) float."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        stats = cdp.main()
    return stats["dialogue_ratio"], stats["narration_ratio"]


def load_policy(path=None):
    path = path or POLICY_PATH
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _knob_value_for_scene(knob_id, knob_data, scene_id):
    """Tra ve gia tri 1 knob cho 1 scene cu the. Scalar (value) -> dung chung moi scene
    (budget/ceiling ap dung toan tap). Curve/enum (per_scene) -> tra dung gia tri scene do.
    Knob BLOCKED -> None (khong bia)."""
    if knob_data.get("status") == "BLOCKED_NOT_CALIBRATED":
        return None
    if "value" in knob_data:
        return knob_data["value"]
    if "per_scene" in knob_data:
        return knob_data["per_scene"].get(scene_id)
    return None


REQUIRED_PLAN_FIELDS = ("cast_per_scene", "reveals_allowed")   # bp6/decision_io.yaml
# required_fields_from_plan (chi 2 field decision_engine THAT doc/dung o day; ep_number/
# scenes da kiem rieng qua plan_ref+scene_id, regret_pillar_context chua co consumer code).


def _packet_completeness(plan, per_scene):
    """G6a-2/G7-2 (audit HIGH, TASK_AUDIT_HIGH_G2_G8.md): truoc day status='full' CHI
    dua vao 'plan is not None', KHONG kiem plan THAT co du field bat buoc theo bp6/
    decision_io.yaml required_fields_from_plan (cast_per_scene/reveals_allowed) hay
    tung scene_id trong per_scene (namespace bible/42 component: HOOK/SETUP/...) co
    khop VOI cac scene THAT cua plan hay khong - story_planner.py THAT (build_episode_
    plan_ep01) hien CHUA sinh cast_per_scene/reveals_allowed, nen packet tu nhan 'full'
    la SAI (tu xung du trong khi thieu 2/5 required field).

    LUU Y namespace: plan['scenes'] la list scene_id INSTANCE (vd 'EP1_SC1') - KHAC
    namespace voi packet's scene_id (component bible/42: 'HOOK'/'SETUP'/...). Doi
    chieu dung phai qua plan['scenes_detail'][i]['component_ref'] (cau lam cau,
    da tu kiem tren du lieu that: component_ref set == bible/42 scenes_order set).

    Tra ve (status, status_note): 'planned' (khong co plan), 'partial' (co plan that
    nhung thieu field bat buoc/scene component lech - CHAP NHAN rui ro nhieu packet
    roi ve day, an toan hon tu nhan du khi chua du, dung tinh than R195 khong bia),
    'full' (du dieu kien)."""
    if plan is None:
        return "planned", ("khong co story plan input (goi build_packet khong truyen "
                           "plan=) - de planned trung thuc, KHONG bia. tools/story_planner.py "
                           "DA ton tai+locked 5/7, truyen plan= de co status full/partial")
    missing = [f for f in REQUIRED_PLAN_FIELDS if plan.get(f) is None]
    if missing:
        return "partial", (f"plan THAT nhung thieu field bat buoc theo bp6/decision_io.yaml "
                           f"required_fields_from_plan: {missing} - story_planner.py hien CHUA "
                           "sinh field nay, KHONG bia gia tri gia (G6a-2/G7-2 10/7)")
    plan_components = {d.get("component_ref") for d in (plan.get("scenes_detail") or [])}
    packet_scene_ids = {s["scene_id"] for s in per_scene}
    mismatched = packet_scene_ids - plan_components
    if mismatched:
        return "partial", (f"scene component trong packet KHONG khop plan['scenes_detail']"
                           f"[].component_ref: {sorted(mismatched)} (G6a-2/G7-2 10/7)")
    return "full", None


def build_packet(ep_number, policy=None, plan=None):
    """Build decision packet THEO bp6/decision_io.yaml. plan=None -> chua co story plan
    that (G6b) -> dung scene_order cua chinh bible/42 lam fallback demo, danh dau
    status: planned cho cac field can plan that. plan!=None nhung thieu field bat
    buoc (cast_per_scene/reveals_allowed) -> status: partial (G6a-2/G7-2 10/7, xem
    _packet_completeness)."""
    policy = policy or load_policy()
    scenes_order = policy["meta"]["scenes_order"]
    knob_ids = list(policy["knobs"].keys())

    # DEBT-033 (12/7): EP01 co nguon SONG (calibrate_decision_policy.py doc golden that) cho
    # dialogue_ratio/narration_ratio - goi 1 lan truoc vong lap scene de tranh goi lai cdp.main()
    # (I/O + parse golden text) moi scene. ep_number != 1 -> None (CHUA co golden khac de calibrate
    # song, R195 khong bia) - _knob_value_for_scene() fallback ve gia tri YAML tinh nhu cu.
    _live_dialogue, _live_narration = (None, None)
    if ep_number == 1:
        _live_dialogue, _live_narration = _live_dialogue_ratio_ep01()

    per_scene = []
    for scene_id in scenes_order:
        knobs = {kid: _knob_value_for_scene(kid, policy["knobs"][kid], scene_id)
                 for kid in knob_ids}
        if ep_number == 1:
            if "dialogue_ratio" in knobs:
                knobs["dialogue_ratio"] = _live_dialogue
            if "narration_ratio" in knobs:
                knobs["narration_ratio"] = _live_narration
        per_scene.append({"scene_id": scene_id, "knobs": knobs})

    has_real_plan = plan is not None
    status, status_note = _packet_completeness(plan, per_scene)
    packet = {
        "packet_id": f"decision_packet_ep{ep_number}_v1_{status}",
        "ep_number": ep_number,
        "plan_ref": f"ep{plan['episode_number']}_{plan['season_ref']}" if has_real_plan else None,
        "calibration_evidence": f"{POLICY_PATH.relative_to(REPO)} (calibrated_from {policy['meta']['calibrated_from']})",
        "per_scene": per_scene,
        "status": status,
        "status_note": status_note,
    }
    return packet


# DEBT-033 phan 2 (12/7, per Mr.Long authorization, TASK_DEBT030_031_CONTENT_FIX.md Buoc 4):
# do dialogue_ratio/narration_ratio cho EP02-11 - CHI DO DE BAO CAO (khong wire vao build_packet()
# chinh thuc, ngoai pham vi task nay - build_packet() van CHI ho tro EP01 nhu truoc). Tai dung
# story_planner.parse_sections_v2() (parser da xay o TASK_STORY_PLANNER_EP02_11_PILOT.md, KHONG
# viet lai) + calibrate_decision_policy.compute_word_split() (cung cong thuc dem word EP01, R211).
import story_planner as _sp  # noqa: E402 - tai dung parse_sections_v2 (R211, khong viet lai)


def measure_dialogue_ratio_ep02_11(ep_number):
    """Do dialogue_ratio/narration_ratio THAT cho 1 tap EP02-11 (KHONG wire vao build_packet()
    chinh thuc - xem ghi chu tren). Raise ValueError neu ep_number ngoai [2,11] (giu nguyen
    pham vi da xac nhan cua parse_sections_v2, R195 khong bia cho EP12+ chua doi chieu format)."""
    if not (2 <= ep_number <= 11):
        raise ValueError(f"measure_dialogue_ratio_ep02_11: ep_number={ep_number} ngoai pham vi [2,11]")
    sections = _sp.parse_sections_v2(ep_number)
    total_narr, total_dial = 0, 0
    per_section = []
    for s in sections:
        narr, dial = cdp.compute_word_split(s["body"])
        total_narr += narr
        total_dial += dial
        per_section.append({"name": s["name"], "narration_words": narr, "dialogue_words": dial})
    total = total_narr + total_dial
    dialogue_ratio = (total_dial / total) if total else 0.0
    narration_ratio = 1 - dialogue_ratio
    return {
        "ep_number": ep_number,
        "dialogue_ratio": round(dialogue_ratio, 4),
        "narration_ratio": round(narration_ratio, 4),
        "total_words": total,
        "per_section": per_section,
        "wired_into_build_packet": False,
        "note": "Do de bao cao (DEBT-033 Buoc 4) - build_packet() van CHI ho tro EP01 chinh thuc.",
    }


def main():
    ep_number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    packet = build_packet(ep_number)
    print(f"=== decision_engine v{__version__} — packet ep{ep_number} (status={packet['status']}) ===")
    print(yaml.safe_dump(packet, allow_unicode=True, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
