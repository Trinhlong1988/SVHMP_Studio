"""tests/test_debt033_dialogue_ratio_wire.py — DEBT-033, per Mr.Long authorization 12/7
(TASK_DEBT030_031_CONTENT_FIX.md Buoc 4).

Truoc fix: bible/42_decision_policy.yaml co gia tri dialogue_ratio/narration_ratio (0.3564/
0.6436) nhung la SO TINH TAY dan vao YAML - build_packet() CHI doc file tinh, KHONG goi lai
tools/calibrate_decision_policy.py, nen neu golden text EP01 doi sau nay, bible/42 se DRIFT
ma khong ai biet (R215). Fix: decision_engine._live_dialogue_ratio_ep01() goi THANG cdp.main()
(R211, khong viet lai cong thuc) de OVERRIDE 2 knob nay trong build_packet(ep_number=1).

M1 reality: build_packet(1) dialogue_ratio/narration_ratio la SO SONG tu cdp.main(), khong
    phai chi doc YAML tinh (mutation-proof qua monkeypatch cdp.main).
M2 constraint dialogue_ratio + narration_ratio == 1.0 (toan hoc, bp6 da khai).
M3 ep_number != 1 (chua co golden khac de calibrate song) -> fallback YAML tinh nhu cu,
    KHONG bia gia tri song gia (R195).
M4 bp6/decision_contract.yaml status field cua 2 knob nay da tu 'planned' -> 'calibrated'.
"""
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import calibrate_decision_policy as cdp  # noqa: E402
import decision_engine as de  # noqa: E402

CONTRACT_PATH = REPO / "governance" / "blueprint" / "bp6" / "decision_contract.yaml"


def test_reality_build_packet_ep01_has_live_dialogue_ratio():
    """Reality anchor: packet EP01 that co dialogue_ratio/narration_ratio, khop cdp.main()
    goi truc tiep (cung nguon, khong lech)."""
    packet = de.build_packet(1)
    live_dialogue, live_narration = de._live_dialogue_ratio_ep01()
    for scene in packet["per_scene"]:
        assert scene["knobs"]["dialogue_ratio"] == live_dialogue
        assert scene["knobs"]["narration_ratio"] == live_narration


def test_constraint_dialogue_plus_narration_equals_one():
    packet = de.build_packet(1)
    for scene in packet["per_scene"]:
        total = scene["knobs"]["dialogue_ratio"] + scene["knobs"]["narration_ratio"]
        assert abs(total - 1.0) < 1e-9, f"dialogue_ratio + narration_ratio phai = 1.0, that {total}"


def test_mutation_proof_packet_reflects_live_cdp_not_static_yaml(monkeypatch):
    """MUTATION-PROOF quan trong nhat: monkeypatch cdp.main() tra ve gia tri KHAC han YAML
    tinh (0.3564) - build_packet(1) PHAI phan anh gia tri MOI nay, chung minh dang goi SONG
    chu khong chi doc bible/42 tinh san (neu ai vo tinh xoa wiring, test nay se FAIL vi packet
    van tra ve 0.3564 cu thay vi 0.9999 injected)."""
    def fake_main():
        return {"dialogue_ratio": 0.9999, "narration_ratio": 0.0001,
                "scene_budget": 6, "silence_budget": 8, "reveal_curve": {}, "per_scene": [],
                "information_budget": 4, "emotion_curve_table": {}}

    monkeypatch.setattr(cdp, "main", fake_main)
    packet = de.build_packet(1)
    assert packet["per_scene"][0]["knobs"]["dialogue_ratio"] == 0.9999, (
        "build_packet(1) KHONG phan anh gia tri SONG tu cdp.main() - wiring bi go/vo hieu")
    assert packet["per_scene"][0]["knobs"]["narration_ratio"] == 0.0001


def test_ep_not_1_falls_back_to_static_yaml_no_fabrication():
    """R195: EP02+ chua co golden khac de calibrate song - PHAI fallback ve gia tri YAML
    tinh (0.3564/0.6436 hien tai), KHONG duoc bia gia tri song gia cho tap khac EP01."""
    packet = de.build_packet(2)
    assert packet["per_scene"][0]["knobs"]["dialogue_ratio"] == 0.3564
    assert packet["per_scene"][0]["knobs"]["narration_ratio"] == 0.6436


def test_reality_decision_contract_status_calibrated_for_2_knobs():
    """DEBT-033 Buoc 4 phan 2: bp6/decision_contract.yaml status cua dialogue_ratio/
    narration_ratio da doi tu 'planned' -> 'calibrated' (hoac tuong duong, KHONG con
    'planned' du bien) sau khi co gia tri that + wiring song."""
    contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    knobs = {k["knob_id"]: k for k in contract["knobs"]}
    for kid in ("dialogue_ratio", "narration_ratio"):
        assert knobs[kid]["status"] != "planned", (
            f"{kid}.status van con 'planned' - Buoc 4 chua cap nhat status that")
        assert knobs[kid]["calibration_source"]["status"] != "planned_G6", (
            f"{kid}.calibration_source.status van con 'planned_G6' - chua cap nhat")


def test_reality_cdp_main_still_returns_expected_shape():
    """Sanity giu nguyen hanh vi cu (khong doi test hien co): cdp.main() van tra ve dict
    co du 2 key can dung."""
    stats = cdp.main()
    assert "dialogue_ratio" in stats and "narration_ratio" in stats
    assert 0.0 <= stats["dialogue_ratio"] <= 1.0


# ============================================================
# Buoc 4 phan 2: measure_dialogue_ratio_ep02_11() — DO DE BAO CAO, KHONG wire vao build_packet
# ============================================================

def test_measure_ep02_11_all_10_episodes_real_data():
    """Reality anchor: do THAT tren ca 10 tap EP02-11, dialogue_ratio hop le [0,1] va
    constraint + narration = 1.0."""
    for ep in range(2, 12):
        r = de.measure_dialogue_ratio_ep02_11(ep)
        assert r["ep_number"] == ep
        assert 0.0 <= r["dialogue_ratio"] <= 1.0
        assert abs(r["dialogue_ratio"] + r["narration_ratio"] - 1.0) < 1e-6
        assert r["total_words"] > 0
        assert r["wired_into_build_packet"] is False, (
            "measure_dialogue_ratio_ep02_11 KHONG duoc tu wire vao build_packet chinh thuc"
            " (ngoai pham vi DEBT-033 Buoc 4)")


def test_measure_rejects_out_of_range_ep():
    """R195: EP12+ chua doi chieu format parse_sections_v2 - PHAI raise, khong bia."""
    with pytest.raises(ValueError):
        de.measure_dialogue_ratio_ep02_11(12)
    with pytest.raises(ValueError):
        de.measure_dialogue_ratio_ep02_11(1)


def test_measure_reuses_parse_sections_v2_not_reimplemented(monkeypatch):
    """MUTATION-PROOF: monkeypatch story_planner.parse_sections_v2 - measure phai goi
    THANG ham nay (R211 tai dung), khong tu parse rieng."""
    called = {}

    def fake_parse(ep_number):
        called["ep"] = ep_number
        return [{"name": "HOOK", "line": 1, "body": "Anh nói: \"xin chào bạn hiền của tôi ơi\"."}]

    monkeypatch.setattr(de._sp, "parse_sections_v2", fake_parse)
    r = de.measure_dialogue_ratio_ep02_11(5)
    assert called["ep"] == 5, "measure_dialogue_ratio_ep02_11 khong goi story_planner.parse_sections_v2"
    assert r["total_words"] > 0
