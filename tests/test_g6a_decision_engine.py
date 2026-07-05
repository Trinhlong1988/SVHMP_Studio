"""G6a D4 — negative + mutation test cho decision_policy_check.py + decision_engine.py.

M1 gia tri ngoai valid_range -> FAIL
M2 thieu calibrated_from -> FAIL
M3 knob thieu/thua vs 12 BP6 -> FAIL
M4 packet field la ngoai bp6/decision_io.yaml -> FAIL (kiem tra packet_schema thuc)
Reality anchor: decision_policy_check PASS tren bible/42 that + decision_engine build
packet tren du lieu that khong crash + moi scene co dung 12 knob key.
"""
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import decision_policy_check as dpc  # noqa: E402
import decision_engine as de  # noqa: E402

REAL_CONTRACT = REPO / "governance" / "blueprint" / "bp6" / "decision_contract.yaml"
REAL_GOLDEN = REPO / "output" / "ep_01" / "episode_golden_text.md"


def _base_policy():
    """Bien ban policy hop le toi thieu (12 knob, dung format) de mutate."""
    return {
        "meta": {"scenes_order": ["A", "B"], "calibrated_from": str(REAL_GOLDEN.relative_to(REPO))},
        "knobs": {
            "dialogue_ratio": {"value": 0.5, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
            "narration_ratio": {"value": 0.5, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
            "emotion_curve": {"per_scene": {"A": 0.5, "B": 0.5}, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
            "fear_curve": {"per_scene": {"A": 0.1, "B": 0.1}, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
            "suspense_curve": {"status": "BLOCKED_NOT_CALIBRATED",
                                "reason_not_calibrated": "khong co nguon that"},
            "reveal_curve": {"per_scene": {"A": 1, "B": 2}, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
            "pacing": {"per_scene": {"A": "vua", "B": "cham"}, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
            "scene_budget": {"value": 2, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
            "information_budget": {"value": 2, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
            "silence_budget": {"value": 3, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
            "character_focus": {"per_scene": {"A": "X", "B": "Y"}, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
            "pov": {"per_scene": {"A": "p1", "B": "p1"}, "calibrated_from": {
                "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}},
        },
    }


def _write_policy(tmp_path, policy):
    p = tmp_path / "policy.yaml"
    p.write_text(yaml.safe_dump(policy, allow_unicode=True), encoding="utf-8")
    return p


def _patched_check(monkeypatch, tmp_path, policy):
    p = _write_policy(tmp_path, policy)
    monkeypatch.setattr(dpc, "POLICY", p)
    monkeypatch.setattr(dpc, "CONTRACT", REAL_CONTRACT)
    return dpc.run()


def test_m0_valid_minimal_policy_clean(monkeypatch, tmp_path):
    """Sanity: policy toi thieu hop le (12 knob dung ten) -> 0 issue that (co the co warn)."""
    issues, warns = _patched_check(monkeypatch, tmp_path, _base_policy())
    assert issues == [], f"policy hop le toi thieu KHONG duoc co issue: {issues}"


def test_m1_value_out_of_range_bites(monkeypatch, tmp_path):
    policy = _base_policy()
    policy["knobs"]["dialogue_ratio"]["value"] = 1.5  # valid_range [0,1]
    issues, _ = _patched_check(monkeypatch, tmp_path, policy)
    assert any("ngoai valid_range" in i for i in issues), issues


def test_m1_curve_value_out_of_range_bites(monkeypatch, tmp_path):
    policy = _base_policy()
    policy["knobs"]["reveal_curve"]["per_scene"]["A"] = 999  # valid_range [0,5]
    issues, _ = _patched_check(monkeypatch, tmp_path, policy)
    assert any("reveal_curve" in i and "ngoai valid_range" in i for i in issues), issues


def test_m2_missing_calibrated_from_bites(monkeypatch, tmp_path):
    policy = _base_policy()
    del policy["knobs"]["dialogue_ratio"]["calibrated_from"]
    issues, _ = _patched_check(monkeypatch, tmp_path, policy)
    assert any("THIEU calibrated_from" in i for i in issues), issues


def test_m2_calibrated_from_source_not_on_disk_bites(monkeypatch, tmp_path):
    policy = _base_policy()
    policy["knobs"]["dialogue_ratio"]["calibrated_from"]["source"] = "khong/ton/tai.md"
    issues, _ = _patched_check(monkeypatch, tmp_path, policy)
    assert any("KHONG TON TAI tren disk" in i for i in issues), issues


def test_m2_blocked_without_reason_bites(monkeypatch, tmp_path):
    """BLOCKED nhung khong ghi ly do = vi pham THAT (khac 'da cong bo minh bach')."""
    policy = _base_policy()
    policy["knobs"]["suspense_curve"] = {"status": "BLOCKED_NOT_CALIBRATED"}
    issues, _ = _patched_check(monkeypatch, tmp_path, policy)
    assert any("THIEU reason_not_calibrated" in i for i in issues), issues


def test_m2_blocked_with_reason_is_warn_not_fail(monkeypatch, tmp_path):
    """Nguoc lai: BLOCKED CO ly do -> KHONG phai FAIL, chi WARN (thiet ke co chu dich)."""
    issues, warns = _patched_check(monkeypatch, tmp_path, _base_policy())
    assert issues == []
    assert any("suspense_curve" in w for w in warns)


def test_m3_missing_knob_bites(monkeypatch, tmp_path):
    policy = _base_policy()
    del policy["knobs"]["pov"]
    issues, _ = _patched_check(monkeypatch, tmp_path, policy)
    assert any("THIEU knob" in i and "pov" in i for i in issues), issues


def test_m3_extra_knob_bites(monkeypatch, tmp_path):
    policy = _base_policy()
    policy["knobs"]["knob_moi_13"] = {"value": 1, "calibrated_from": {
        "source": str(REAL_GOLDEN.relative_to(REPO)), "method": "m", "evidence": "e"}}
    issues, _ = _patched_check(monkeypatch, tmp_path, policy)
    assert any("THUA knob" in i for i in issues), issues


def test_m1_enum_value_outside_declared_set_bites(monkeypatch, tmp_path):
    policy = _base_policy()
    policy["knobs"]["pacing"]["per_scene"]["A"] = "sieu_toc_do_khong_ton_tai"
    issues, _ = _patched_check(monkeypatch, tmp_path, policy)
    assert any("khong nam trong enum" in i for i in issues), issues


# ============================================================
# REALITY ANCHOR — chay tren du lieu THAT (bible/42 that, khong phai policy gia)
# ============================================================

def test_reality_decision_policy_check_pass_on_real_data():
    """decision_policy_check.py chay tren bible/42 that (repo goc) phai PASS (0 issue that)."""
    issues, warns = dpc.run()
    assert issues == [], f"bible/42 that dang co vi pham THAT can Mr.Long fix: {issues}"
    assert len(warns) == 1 and "suspense_curve" in warns[0], (
        "ky vong dung 1 WARN da biet truoc (suspense_curve blocked) — neu so WARN doi, "
        "kiem tra lai bible/42 that co thay doi khong")


def test_reality_decision_engine_builds_packet_no_crash():
    packet = de.build_packet(1)
    assert packet["status"] == "planned"
    assert packet["plan_ref"] is None
    assert len(packet["per_scene"]) == 6


def test_reality_packet_per_scene_has_exactly_12_knob_keys_matching_bp6():
    """M4-tuong-duong: packet field per scene PHAI dung 12 knob_id BP6, khong thieu/thua."""
    contract = dpc.load_contract()
    expected_ids = set(contract.keys())
    packet = de.build_packet(1)
    for scene in packet["per_scene"]:
        actual_ids = set(scene["knobs"].keys())
        assert actual_ids == expected_ids, (
            f"scene {scene['scene_id']}: knob key le {actual_ids ^ expected_ids}")


def test_reality_suspense_curve_is_none_not_fabricated_in_packet():
    """Knob BLOCKED phai la None trong packet (KHONG duoc tu dien 1 so gia de 'du field')."""
    packet = de.build_packet(1)
    for scene in packet["per_scene"]:
        assert scene["knobs"]["suspense_curve"] is None, (
            "suspense_curve BLOCKED nhung packet lai co gia tri — nghi bia so (R195)")


def test_bp6_contract_checker_still_pass_untouched():
    """G6a KHONG duoc dung vao bp6/decision_contract.yaml, decision_io.yaml da LOCKED."""
    import subprocess
    r = subprocess.run([sys.executable, str(REPO / "tools" / "bp6_decision_check.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_g6_gate_wired_in_ci_gate():
    """Unwire-guard (bai hoc G2_roster): stage G6_story_planner PHAI co trong ci_gate.CHECKS,
    khong duoc de sot lai sau khi build xong gate."""
    sys.path.insert(0, str(REPO / "tools"))
    import ci_gate
    assert ("G6_story_planner", "tools/g6_story_planner_check.py") in ci_gate.CHECKS


def test_g6_gate_pass_on_real_data():
    import subprocess
    r = subprocess.run([sys.executable, str(REPO / "tools" / "g6_story_planner_check.py")],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
