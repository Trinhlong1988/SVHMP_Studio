"""decision_engine.py — G6a D3: manager TOI THIEU, CHI phan doc bible/42 (KHONG sinh text).

Doc bible/42_decision_policy.yaml -> build phan packet KHONG phu thuoc story_planner
(bp6/decision_io.yaml schema). plan_ref/cast_per_scene/reveals_allowed can INPUT tu story
plan that (G6b, CHUA xay) -> de status: planned trung thuc, KHONG bia gia tri gia.

Day la manager doc-only: KHONG viet logic sinh episode text.
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
POLICY_PATH = REPO / "bible" / "42_decision_policy.yaml"

__version__ = "1.0.0"


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


def build_packet(ep_number, policy=None, plan=None):
    """Build decision packet THEO bp6/decision_io.yaml. plan=None -> chua co story plan
    that (G6b) -> dung scene_order cua chinh bible/42 lam fallback demo, danh dau
    status: planned cho cac field can plan that."""
    policy = policy or load_policy()
    scenes_order = policy["meta"]["scenes_order"]
    knob_ids = list(policy["knobs"].keys())

    per_scene = []
    for scene_id in scenes_order:
        knobs = {kid: _knob_value_for_scene(kid, policy["knobs"][kid], scene_id)
                 for kid in knob_ids}
        per_scene.append({"scene_id": scene_id, "knobs": knobs})

    has_real_plan = plan is not None
    packet = {
        "packet_id": f"decision_packet_ep{ep_number}_v1_{'full' if has_real_plan else 'partial'}",
        "ep_number": ep_number,
        "plan_ref": plan.get("plan_ref") if has_real_plan else None,
        "calibration_evidence": f"{POLICY_PATH.relative_to(REPO)} (calibrated_from {policy['meta']['calibrated_from']})",
        "per_scene": per_scene,
        "status": "full" if has_real_plan else "planned",
        "status_note": (None if has_real_plan else
                        "plan_ref/cast_per_scene/reveals_allowed can story plan that (G6b, "
                        "runtime/story_planner.py chua xay) - KHONG bia, de planned trung thuc"),
    }
    return packet


def main():
    ep_number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    packet = build_packet(ep_number)
    print(f"=== decision_engine v{__version__} — packet ep{ep_number} (status={packet['status']}) ===")
    print(yaml.safe_dump(packet, allow_unicode=True, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
