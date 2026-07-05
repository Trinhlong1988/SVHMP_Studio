"""decision_policy_check.py — G6a D2: validator cho bible/42_decision_policy.yaml.

Kiem: (1) dung 12 knob so voi bp6/decision_contract.yaml (khong thieu/thua) (2) moi so
trong valid_range da khai BP6 (3) moi knob co calibrated_from voi source THAT ton tai tren
disk — TRU knob duoc khai status: BLOCKED_NOT_CALIBRATED + reason_not_calibrated (WARN,
khong phai FAIL — day la khoang trong da cong bo minh bach, khac oversight thuc su, R9/R10).

Exit 0 = 0 VI PHAM THAT (co the con WARN blocked-biet-truoc). Exit 1 = >=1 vi pham.
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CONTRACT = REPO / "governance" / "blueprint" / "bp6" / "decision_contract.yaml"
POLICY = REPO / "bible" / "42_decision_policy.yaml"

__version__ = "1.0.0"


def load_contract():
    d = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    return {k["knob_id"]: k for k in d["knobs"]}


def load_policy():
    return yaml.safe_load(POLICY.read_text(encoding="utf-8"))


def _iter_values(knob_data):
    """Tra ve list gia tri so THAT can kiem valid_range (scalar: [value]; curve: per_scene.values())."""
    if "value" in knob_data:
        return [knob_data["value"]]
    if "per_scene" in knob_data and knob_data["per_scene"]:
        vals = list(knob_data["per_scene"].values())
        # enum per_scene (string) khong check so-range o day
        return [v for v in vals if isinstance(v, (int, float))]
    return []


def check_knob_count(contract, policy):
    issues = []
    contract_ids = set(contract.keys())
    policy_ids = set(policy["knobs"].keys())
    missing = contract_ids - policy_ids
    extra = policy_ids - contract_ids
    if missing:
        issues.append(f"M3 THIEU knob (co trong BP6, khong co trong bible/42): {sorted(missing)}")
    if extra:
        issues.append(f"M3 THUA knob (co trong bible/42, khong co trong BP6): {sorted(extra)}")
    return issues


def check_valid_range(contract, policy):
    issues = []
    for knob_id, knob_data in policy["knobs"].items():
        if knob_id not in contract:
            continue  # da bao o check_knob_count
        contract_knob = contract[knob_id]
        if knob_data.get("status") == "BLOCKED_NOT_CALIBRATED":
            continue  # khong co so de check range
        vr = contract_knob.get("valid_range")
        if vr:
            lo, hi = vr
            for v in _iter_values(knob_data):
                if not (lo <= v <= hi):
                    issues.append(f"M1 {knob_id}: gia tri {v} ngoai valid_range {vr}")
        values_enum = contract_knob.get("values")
        if values_enum:
            # enum dong (vd pacing) - kiem moi gia tri string trong per_scene
            per_scene = knob_data.get("per_scene", {})
            for scene, v in per_scene.items():
                if isinstance(v, str) and v not in values_enum:
                    issues.append(f"M1 {knob_id}.{scene}: '{v}' khong nam trong enum {values_enum}")
    return issues


def check_calibrated_from(policy):
    issues = []
    warns = []
    for knob_id, knob_data in policy["knobs"].items():
        if knob_data.get("status") == "BLOCKED_NOT_CALIBRATED":
            if not knob_data.get("reason_not_calibrated"):
                issues.append(f"M2 {knob_id}: BLOCKED nhung THIEU reason_not_calibrated "
                              f"(khoang trong khong duoc cong bo ro = vi pham, khac 'da disclose')")
            else:
                warns.append(f"{knob_id}: BLOCKED_NOT_CALIBRATED (da cong bo ly do, cho Mr.Long quyet)")
            continue
        cf = knob_data.get("calibrated_from")
        if not cf:
            issues.append(f"M2 {knob_id}: THIEU calibrated_from")
            continue
        source = cf.get("source")
        if not source:
            issues.append(f"M2 {knob_id}: calibrated_from thieu field 'source'")
        else:
            source_path = REPO / source
            if not source_path.exists():
                issues.append(f"M2 {knob_id}: calibrated_from.source '{source}' KHONG TON TAI tren disk (bia duong dan)")
        if not cf.get("evidence") and not cf.get("method"):
            issues.append(f"M2 {knob_id}: calibrated_from thieu ca method lan evidence")
    return issues, warns


def run():
    contract = load_contract()
    policy = load_policy()
    issues = []
    issues += check_knob_count(contract, policy)
    issues += check_valid_range(contract, policy)
    cf_issues, warns = check_calibrated_from(policy)
    issues += cf_issues
    return issues, warns


def main():
    print(f"=== DECISION POLICY CHECK v{__version__} (G6a D2) ===")
    issues, warns = run()
    for w in warns:
        print(f"  [WARN] {w}")
    for i in issues:
        print(f"  [FAIL] {i}")
    if issues:
        print(f"=== FAIL — {len(issues)} vi pham that ===")
        return 1
    print(f"=== PASS — 0 vi pham that ({len(warns)} WARN da cong bo minh bach) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
