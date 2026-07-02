"""
test_voice_profile_manager.py — R181b regression
Mr.Long approve Phase 1 30/6: tests MUST run 10 rounds with metrics.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from voice_profile_manager import (  # noqa: E402
    EmotionRangeError,
    LockedFieldError,
    ProfileNotFoundError,
    StateTransitionError,
    VoiceProfileManager,
    LOCKED_FIELDS,
)


@pytest.fixture(scope="module")
def mgr():
    return VoiceProfileManager.load_default()


def test_01_registry_has_four_required_profiles(mgr):
    """All 4 mandatory profiles (NARRATOR, KHAI_PHONG, DRIVER, GIRL_GHE7) loaded."""
    profiles = mgr.list_profiles()
    for required in ("NARRATOR", "KHAI_PHONG", "DRIVER", "GIRL_GHE7"):
        assert required in profiles, f"missing required profile {required}"


def test_02_locked_field_modification_raises(mgr):
    """R181b sealed invariant: setting voice_id MUST raise LockedFieldError."""
    p = mgr.get("KHAI_PHONG")
    with pytest.raises(LockedFieldError):
        p.voice_id = "OTHER"
    with pytest.raises(LockedFieldError):
        p.accent = "Nam"
    with pytest.raises(LockedFieldError):
        p.pitch_base_hz = 200


def test_03_emotion_override_within_range_succeeds(mgr):
    """Valid emotion vector sum<=1 accepted."""
    p = mgr.get("KHAI_PHONG")
    p.set_emotion([0.0, 0.0, 0.3, 0.05, 0.0, 0.3, 0.0, 0.35])
    assert sum(p.emotion_vector) == pytest.approx(1.0)


def test_04_emotion_override_oor_rejected(mgr):
    """R175b normalize: sum > 1.0 MUST raise EmotionRangeError."""
    p = mgr.get("KHAI_PHONG")
    with pytest.raises(EmotionRangeError):
        p.set_emotion([0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0])
    with pytest.raises(EmotionRangeError):
        p.set_emotion([1.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    with pytest.raises(EmotionRangeError):
        p.set_emotion([0.1] * 7)  # wrong length
    with pytest.raises(EmotionRangeError):
        p.set_emotion([-0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])


def test_05_emotion_sum_equals_one_accepted(mgr):
    """R175b boundary: sum exactly 1.0 PASS."""
    p = mgr.get("DRIVER")
    p.set_emotion([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    assert sum(p.emotion_vector) == pytest.approx(1.0)


def test_06_intensity_range_enforced(mgr):
    """Dynamic field bounds enforce."""
    p = mgr.get("NARRATOR")
    p.set_intensity(0.5)
    p.set_intensity(0.0)
    p.set_intensity(1.0)
    with pytest.raises(EmotionRangeError):
        p.set_intensity(1.01)
    with pytest.raises(EmotionRangeError):
        p.set_intensity(-0.01)


def test_07_speech_rate_modifier_bounds(mgr):
    """docx limit: 0.95-1.05."""
    p = mgr.get("NARRATOR")
    p.set_speech_rate_modifier(0.95)
    p.set_speech_rate_modifier(1.05)
    p.set_speech_rate_modifier(1.0)
    with pytest.raises(EmotionRangeError):
        p.set_speech_rate_modifier(1.10)
    with pytest.raises(EmotionRangeError):
        p.set_speech_rate_modifier(0.80)


def test_08_state_transition_valid_path(mgr):
    """NORMAL -> NGHEN allowed for KHAI_PHONG per bible/15 transitions."""
    p = mgr.get("KHAI_PHONG")
    p.transition_state("NORMAL")
    p.transition_state("NGHEN")
    assert p.current_state == "NGHEN"


def test_09_state_transition_invalid_rejected(mgr):
    """DRIVER allowed_states only [THI_THAM, NORMAL] — invalid state raises."""
    p = mgr.get("DRIVER")
    with pytest.raises(StateTransitionError):
        p.transition_state("HOANG")  # not in DRIVER allowed_states
    with pytest.raises(StateTransitionError):
        p.transition_state("XUC_DONG")


def test_10_profile_not_found_raises(mgr):
    """Unknown voice_id raises ProfileNotFoundError."""
    with pytest.raises(ProfileNotFoundError):
        mgr.get("NONEXISTENT_VOICE")
    with pytest.raises(ProfileNotFoundError):
        mgr.get("")


def test_11_validate_registry_passes(mgr):
    """All 4 profiles must have full LOCKED field set per R181b."""
    rpt = mgr.validate_registry()
    assert rpt["ok"], f"validate_registry FAIL: {rpt['issues']}"
    assert len(rpt["profiles"]) == 4


def test_12_snapshot_contains_locked_and_dynamic(mgr):
    """snapshot() exposes both layers separately."""
    p = mgr.get("GIRL_GHE7")
    snap = p.snapshot()
    assert snap["voice_id"] == "GIRL_GHE7"
    assert "locked" in snap and "dynamic" in snap
    for f in ("voice_id", "accent", "timbre", "pitch_base_hz"):
        assert f in snap["locked"]
    for f in ("emotion_vector", "intensity", "current_state"):
        assert f in snap["dynamic"]


def test_13_locked_fields_constant_matches_bible(mgr):
    """LOCKED_FIELDS constant must match bible declaration."""
    bible_locked = set(mgr.meta()["locked_fields"])
    assert LOCKED_FIELDS == frozenset(bible_locked), (
        f"mismatch: code={LOCKED_FIELDS} bible={bible_locked}"
    )


def test_14_artifact_types_five(mgr):
    """5 artifact types from Mr.Long docx must all be loaded."""
    types = set(mgr.meta()["artifact_types"])
    expected = {
        "voice_identity_drift",
        "pause_boundary_artifact",
        "breath_artifact",
        "onset_artifact",
        "prosody_collapse",
    }
    assert expected.issubset(types), f"missing artifact types: {expected - types}"


def test_15_driver_state_constrained(mgr):
    """DRIVER allowed_states tightly constrained to [THI_THAM, NORMAL]."""
    p = mgr.get("DRIVER")
    allowed = set(p.allowed_states)
    assert allowed == {"THI_THAM", "NORMAL"}
