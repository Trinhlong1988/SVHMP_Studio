"""
voice_profile_manager.py — R181b enforcement (Voice Identity LOCKED + Emotion DYNAMIC)
Mr.Long approve Phase 1 — 30/6 19:00.

Architecture (per Mr.Long docx 30/6):
  Voice Identity = LOCKED (cannot change between chunks)
  Emotion Layer = DYNAMIC (allowed change within bounds)

Schema source: bible/15_voice_bible.yaml v2.0.

Usage:
    from voice_profile_manager import VoiceProfileManager, LockedFieldError

    mgr = VoiceProfileManager.load_default()
    p = mgr.get('KHAI_PHONG')
    p.transition_state('NGHEN')             # OK if NORMAL -> NGHEN allowed
    p.set_emotion([0,0,0.3,0.05,0,0.3,0,0.35])  # validate sum<=1
    try:
        p.voice_id = 'OTHER'                # raises LockedFieldError
    except LockedFieldError as e:
        ...

CLI:
    python tools/voice_profile_manager.py --list
    python tools/voice_profile_manager.py --validate
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BIBLE = REPO_ROOT / "bible" / "15_voice_bible.yaml"

LOCKED_FIELDS = frozenset(
    [
        "voice_id",
        "speaker_embedding_path",
        "speaker_embedding_sha256",
        "golden_reference_wav",
        "accent",
        "timbre",
        "gender",
        "age_range",
        "pitch_base_hz",
        "speaking_rate_base_wps",
    ]
)


class LockedFieldError(RuntimeError):
    """Raised when caller tries to mutate a LOCKED field on VoiceProfile."""


class EmotionRangeError(ValueError):
    """Raised when emotion override violates dynamic range bounds."""


class StateTransitionError(ValueError):
    """Raised when transition is not allowed by state machine."""


class ProfileNotFoundError(KeyError):
    """Raised when caller requests an unknown profile id."""


@dataclass
class _DynamicState:
    """Mutable runtime state for a VoiceProfile (Emotion Layer)."""

    emotion_vector: list[float] = field(
        default_factory=lambda: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    )
    intensity: float = 0.5
    pause_ms: int = 0
    speech_rate_modifier: float = 1.0
    breath_intensity: float = 0.0
    current_state: str = "NORMAL"


class VoiceProfile:
    """
    Locked voice identity + dynamic emotion layer.

    LOCKED fields are read-only after init.
    DYNAMIC fields are mutated only via explicit methods that validate bounds.
    """

    def __init__(
        self,
        locked: dict,
        allowed_states: list[str],
        state_defaults: dict[str, list[float]],
        state_transitions: dict[str, list[str]],
        dynamic_bounds: dict,
        notes: str = "",
    ):
        object.__setattr__(self, "_locked", dict(locked))
        object.__setattr__(self, "_allowed_states", list(allowed_states))
        object.__setattr__(self, "_state_defaults", dict(state_defaults))
        object.__setattr__(self, "_state_transitions", dict(state_transitions))
        object.__setattr__(self, "_dynamic_bounds", dict(dynamic_bounds))
        object.__setattr__(self, "_notes", notes)
        initial = locked.get("initial_state") or self._allowed_states[0] if self._allowed_states else "NORMAL"
        dyn = _DynamicState(current_state=initial)
        if initial in self._state_defaults:
            dyn.emotion_vector = list(self._state_defaults[initial])
        object.__setattr__(self, "_dynamic", dyn)
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, key: str, value: Any) -> None:
        if getattr(self, "_sealed", False) and key in LOCKED_FIELDS:
            raise LockedFieldError(
                f"Cannot modify LOCKED field '{key}' on VoiceProfile "
                f"'{self._locked.get('voice_id')}'. "
                f"Use a new profile or update bible/15_voice_bible.yaml v2.0."
            )
        object.__setattr__(self, key, value)

    @property
    def voice_id(self) -> str:
        return self._locked["voice_id"]

    @property
    def speaker_embedding_path(self) -> str:
        return self._locked["speaker_embedding_path"]

    @property
    def golden_reference_wav(self) -> str:
        return self._locked["golden_reference_wav"]

    @property
    def accent(self) -> str:
        return self._locked["accent"]

    @property
    def timbre(self) -> str:
        return self._locked["timbre"]

    @property
    def gender(self) -> str:
        return self._locked["gender"]

    @property
    def age_range(self) -> list[int]:
        return list(self._locked["age_range"])

    @property
    def pitch_base_hz(self) -> float:
        return float(self._locked["pitch_base_hz"])

    @property
    def speaking_rate_base_wps(self) -> float:
        return float(self._locked["speaking_rate_base_wps"])

    @property
    def current_state(self) -> str:
        return self._dynamic.current_state

    @property
    def emotion_vector(self) -> list[float]:
        return list(self._dynamic.emotion_vector)

    @property
    def intensity(self) -> float:
        return self._dynamic.intensity

    @property
    def pause_ms(self) -> int:
        return self._dynamic.pause_ms

    @property
    def speech_rate_modifier(self) -> float:
        return self._dynamic.speech_rate_modifier

    @property
    def breath_intensity(self) -> float:
        return self._dynamic.breath_intensity

    @property
    def notes(self) -> str:
        return self._notes

    @property
    def allowed_states(self) -> list[str]:
        return list(self._allowed_states)

    def set_emotion(self, vec: list[float]) -> None:
        if not isinstance(vec, (list, tuple)):
            raise EmotionRangeError("emotion must be list/tuple of 8 floats")
        if len(vec) != 8:
            raise EmotionRangeError(f"emotion length must be 8, got {len(vec)}")
        for v in vec:
            if not isinstance(v, (int, float)):
                raise EmotionRangeError(f"emotion contains non-numeric: {v!r}")
            if v < 0.0 or v > 1.0:
                raise EmotionRangeError(f"emotion[i]={v} outside [0,1]")
        total = sum(vec)
        max_sum = float(self._dynamic_bounds["emotion_vector"]["sum_max"])
        if total > max_sum + 1e-9:
            raise EmotionRangeError(
                f"emotion sum={total:.4f} > {max_sum} (R175b normalize hardlock)"
            )
        self._dynamic.emotion_vector = list(vec)

    def set_intensity(self, value: float) -> None:
        lo, hi = self._dynamic_bounds["intensity"]["range"]
        if not (lo <= value <= hi):
            raise EmotionRangeError(f"intensity {value} outside [{lo},{hi}]")
        self._dynamic.intensity = float(value)

    def set_pause_ms(self, value: int) -> None:
        lo, hi = self._dynamic_bounds["pause_ms"]["range"]
        if not (lo <= value <= hi):
            raise EmotionRangeError(f"pause_ms {value} outside [{lo},{hi}]")
        self._dynamic.pause_ms = int(value)

    def set_speech_rate_modifier(self, value: float) -> None:
        lo, hi = self._dynamic_bounds["speech_rate_modifier"]["range"]
        if not (lo <= value <= hi):
            raise EmotionRangeError(
                f"speech_rate_modifier {value} outside [{lo},{hi}]"
            )
        self._dynamic.speech_rate_modifier = float(value)

    def set_breath_intensity(self, value: float) -> None:
        lo, hi = self._dynamic_bounds["breath_intensity"]["range"]
        if not (lo <= value <= hi):
            raise EmotionRangeError(
                f"breath_intensity {value} outside [{lo},{hi}]"
            )
        self._dynamic.breath_intensity = float(value)

    def transition_state(self, target_state: str) -> None:
        if target_state not in self._allowed_states:
            raise StateTransitionError(
                f"state '{target_state}' not in allowed_states for "
                f"{self.voice_id}: {self._allowed_states}"
            )
        current = self._dynamic.current_state
        valid_targets = self._state_transitions.get(current, [])
        if target_state not in valid_targets and target_state != current:
            raise StateTransitionError(
                f"transition '{current}' -> '{target_state}' not allowed. "
                f"Valid: {valid_targets}"
            )
        self._dynamic.current_state = target_state
        if target_state in self._state_defaults:
            self._dynamic.emotion_vector = list(self._state_defaults[target_state])

    def snapshot(self) -> dict:
        return {
            "voice_id": self.voice_id,
            "locked": dict(self._locked),
            "dynamic": {
                "current_state": self.current_state,
                "emotion_vector": self.emotion_vector,
                "intensity": self.intensity,
                "pause_ms": self.pause_ms,
                "speech_rate_modifier": self.speech_rate_modifier,
                "breath_intensity": self.breath_intensity,
            },
        }


class VoiceProfileManager:
    def __init__(
        self,
        profiles: dict[str, VoiceProfile],
        bible_meta: dict,
    ):
        self._profiles = dict(profiles)
        self._bible_meta = dict(bible_meta)

    @classmethod
    def from_dict(cls, bible: dict) -> "VoiceProfileManager":
        states = bible.get("states", {})
        state_defaults = {
            name: list(s.get("default_emotion_vector", []))
            for name, s in states.items()
        }
        transitions = {k: list(v) for k, v in bible.get("state_transitions", {}).items()}
        bounds = bible.get("dynamic_fields", {})
        all_state_names = list(states.keys())

        profiles: dict[str, VoiceProfile] = {}
        for name, raw in bible.get("profiles", {}).items():
            locked_subset = {k: raw[k] for k in LOCKED_FIELDS if k in raw}
            locked_subset["initial_state"] = raw.get("initial_state", "NORMAL")
            allowed = raw.get("allowed_states", all_state_names)
            notes = raw.get("notes", "")
            profile = VoiceProfile(
                locked=locked_subset,
                allowed_states=allowed,
                state_defaults=state_defaults,
                state_transitions=transitions,
                dynamic_bounds=bounds,
                notes=notes,
            )
            profiles[name] = profile

        meta = {
            "version": bible.get("version"),
            "lock_date": bible.get("lock_date"),
            "authority": bible.get("authority"),
            "locked_fields": list(bible.get("locked_fields", [])),
            "artifact_types": list(bible.get("artifact_types", {}).keys()),
        }
        return cls(profiles=profiles, bible_meta=meta)

    @classmethod
    def load_default(cls, path: Path | None = None) -> "VoiceProfileManager":
        if yaml is None:
            raise RuntimeError("PyYAML required: pip install pyyaml")
        p = path or DEFAULT_BIBLE
        bible = yaml.safe_load(p.read_text(encoding="utf-8"))
        return cls.from_dict(bible)

    def list_profiles(self) -> list[str]:
        return sorted(self._profiles.keys())

    def get(self, voice_id: str) -> VoiceProfile:
        if voice_id not in self._profiles:
            raise ProfileNotFoundError(f"unknown voice_id: {voice_id!r}")
        return self._profiles[voice_id]

    def meta(self) -> dict:
        return dict(self._bible_meta)

    def validate_registry(self) -> dict:
        report = {"ok": True, "profiles": [], "issues": []}
        for vid, p in self._profiles.items():
            entry = {"voice_id": vid, "locked_ok": True, "issues": []}
            for f in LOCKED_FIELDS:
                if f not in p._locked:
                    entry["locked_ok"] = False
                    entry["issues"].append(f"missing LOCKED field: {f}")
                    report["ok"] = False
            try:
                p.transition_state(p.current_state)
            except StateTransitionError as e:
                entry["issues"].append(f"self-transition fail: {e}")
                report["ok"] = False
            report["profiles"].append(entry)
        return report


def _cli() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--bible", type=str, default=str(DEFAULT_BIBLE))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--snapshot", type=str, default=None, help="voice_id")
    args = ap.parse_args()

    mgr = VoiceProfileManager.load_default(Path(args.bible))
    if args.list:
        print("[R181b] Profiles:", mgr.list_profiles())
        print("[R181b] Meta:", mgr.meta())
    if args.validate:
        rpt = mgr.validate_registry()
        print(json.dumps(rpt, ensure_ascii=False, indent=2))
        return 0 if rpt["ok"] else 1
    if args.snapshot:
        p = mgr.get(args.snapshot)
        print(json.dumps(p.snapshot(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
