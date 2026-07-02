"""
test_voice_qa_tools.py — Voice QA validation suite
Per Mr.Long APPROVED 30/6 21:30:
  - unit tests + regression for 5 Voice QA tools (R188-R191 + R181c)
  - No threshold tune. No new features. No re-render.

Synthetic audio fixtures generated in-memory for deterministic tests.
Real audio fixtures use existing output/ep_01/sections/*.wav.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
SECTIONS = REPO_ROOT / "output" / "ep_01" / "sections"
TMP_DIR = REPO_ROOT / "runtime" / "test_voice_qa_fixtures"
TMP_DIR.mkdir(parents=True, exist_ok=True)


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout, proc.stderr


def _write_wav(arr: np.ndarray, sr: int, name: str) -> Path:
    import soundfile as sf
    p = TMP_DIR / name
    sf.write(p, arr.astype(np.float32), sr)
    return p


@pytest.fixture(scope="module")
def synth_clean():
    sr = 22050
    t = np.linspace(0, 4.0, sr * 4, endpoint=False)
    sig = 0.3 * np.sin(2 * np.pi * 200 * t)
    sig += 0.001 * np.random.RandomState(42).randn(len(sig))
    return _write_wav(sig, sr, "synth_clean.wav"), sr


@pytest.fixture(scope="module")
def synth_silence_boundary():
    sr = 22050
    t = np.linspace(0, 1.5, int(sr * 1.5), endpoint=False)
    seg = 0.3 * np.sin(2 * np.pi * 200 * t)
    silence = np.zeros(int(sr * 1.5))
    full = np.concatenate([seg, silence, seg])
    return _write_wav(full, sr, "synth_silence_boundary.wav"), sr


@pytest.fixture(scope="module")
def synth_pitch_drop():
    sr = 22050
    n = sr * 3
    t1 = np.linspace(0, 1.5, n // 2, endpoint=False)
    t2 = np.linspace(0, 1.5, n // 2, endpoint=False)
    seg1 = 0.3 * np.sin(2 * np.pi * 220 * t1)
    seg2 = 0.3 * np.sin(2 * np.pi * 110 * t2)
    return _write_wav(np.concatenate([seg1, seg2]), sr, "synth_pitch_drop.wav"), sr


@pytest.fixture(scope="module")
def real_cliffhanger():
    p = SECTIONS / "cliffhanger.wav"
    if not p.exists():
        pytest.skip(f"missing real audio {p}")
    return p


@pytest.fixture(scope="module")
def real_hook():
    p = SECTIONS / "hook.wav"
    if not p.exists():
        pytest.skip(f"missing real audio {p}")
    return p


# ===========================================
# R188 — qa_boundary_artifact.py
# ===========================================

class TestR188Boundary:
    SCRIPT = TOOLS / "qa_boundary_artifact.py"

    def test_01_script_exists(self):
        assert self.SCRIPT.exists()

    def test_02_help_runs(self):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--help"])
        assert rc == 0

    def test_03_run_on_real_section_returns_valid_report(self, real_cliffhanger):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--wav", str(real_cliffhanger), "--json"])
        assert rc in (0, 1)
        rpt = json.loads(out)
        for k in ("rule", "wav", "n_high", "n_medium", "verdict", "findings"):
            assert k in rpt
        assert rpt["rule"].startswith("R188")

    def test_04_synthetic_clean_passes(self, synth_clean):
        wav, _ = synth_clean
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--wav", str(wav), "--json"])
        rpt = json.loads(out)
        assert rpt["n_high"] == 0


# ===========================================
# R189 — qa_breath_artifact.py
# ===========================================

class TestR189Breath:
    SCRIPT = TOOLS / "qa_breath_artifact.py"

    def test_01_script_exists(self):
        assert self.SCRIPT.exists()

    def test_02_help_runs(self):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--help"])
        assert rc == 0

    def test_03_run_on_real_section_returns_valid_report(self, real_cliffhanger):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--wav", str(real_cliffhanger), "--json"])
        assert rc in (0, 1)
        rpt = json.loads(out)
        for k in ("rule", "wav", "n_high", "n_medium", "verdict", "findings"):
            assert k in rpt
        assert rpt["rule"].startswith("R189")

    def test_04_synthetic_clean_passes(self, synth_clean):
        wav, _ = synth_clean
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--wav", str(wav), "--json"])
        rpt = json.loads(out)
        assert rpt["n_high"] == 0


# ===========================================
# R190 — qa_prosody_collapse.py
# ===========================================

class TestR190Prosody:
    SCRIPT = TOOLS / "qa_prosody_collapse.py"

    def test_01_script_exists(self):
        assert self.SCRIPT.exists()

    def test_02_help_runs(self):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--help"])
        assert rc == 0

    def test_03_run_on_real_section_returns_valid_report(self, real_cliffhanger):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--wav", str(real_cliffhanger), "--json"])
        assert rc in (0, 1)
        rpt = json.loads(out)
        assert rpt["rule"].startswith("R190")

    def test_04_synthetic_pitch_drop_detects(self, synth_pitch_drop):
        wav, _ = synth_pitch_drop
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--wav", str(wav), "--json"])
        rpt = json.loads(out)
        assert rpt["n_high"] >= 1, "Synthetic 220Hz->110Hz drop must trigger >=1 HIGH"


# ===========================================
# R190b — qa_onset_artifact.py
# ===========================================

class TestR190bOnset:
    SCRIPT = TOOLS / "qa_onset_artifact.py"

    def test_01_script_exists(self):
        assert self.SCRIPT.exists()

    def test_02_help_runs(self):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--help"])
        assert rc == 0

    def test_03_run_on_real_section_returns_valid_report(self, real_cliffhanger):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--wav", str(real_cliffhanger), "--json"])
        assert rc in (0, 1)
        rpt = json.loads(out)
        assert rpt["rule"].startswith("R190b")


# ===========================================
# R191 — qa_dialogue_identity.py
# ===========================================

class TestR191DialogueIdentity:
    SCRIPT = TOOLS / "qa_dialogue_identity.py"

    def test_01_script_exists(self):
        assert self.SCRIPT.exists()

    def test_02_help_runs(self):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--help"])
        assert rc == 0

    def test_03_run_on_real_section_returns_valid_report(self, real_cliffhanger):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--wav", str(real_cliffhanger), "--json"])
        assert rc in (0, 1)
        rpt = json.loads(out)
        assert rpt["rule"].startswith("R191")
        for k in ("segments", "threshold", "n_high", "verdict", "findings"):
            assert k in rpt


# ===========================================
# R181c — extract_speaker_embedding.py
# ===========================================

class TestR181cEmbedding:
    SCRIPT = TOOLS / "extract_speaker_embedding.py"

    def test_01_script_exists(self):
        assert self.SCRIPT.exists()

    def test_02_help_runs(self):
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--help"])
        assert rc == 0

    def test_03_extract_embedding_192dim(self, real_cliffhanger, tmp_path):
        out_npy = tmp_path / "emb.npy"
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--wav", str(real_cliffhanger), "--output", str(out_npy)])
        assert rc == 0
        emb = np.load(out_npy)
        assert emb.shape == (192,)
        assert abs(np.linalg.norm(emb) - 1.0) < 1e-3

    def test_04_self_similarity_is_one(self, real_cliffhanger, tmp_path):
        a = tmp_path / "a.npy"
        b = tmp_path / "b.npy"
        for out in (a, b):
            _run([sys.executable, str(self.SCRIPT), "--wav", str(real_cliffhanger), "--output", str(out)])
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--compare", str(a), str(b)])
        rpt = json.loads(out)
        assert rpt["cosine_similarity"] >= 0.999

    def test_05_cross_section_similarity_within_speaker(self, real_cliffhanger, real_hook, tmp_path):
        a = tmp_path / "cliff.npy"
        b = tmp_path / "hook.npy"
        _run([sys.executable, str(self.SCRIPT), "--wav", str(real_cliffhanger), "--output", str(a)])
        _run([sys.executable, str(self.SCRIPT), "--wav", str(real_hook), "--output", str(b)])
        rc, out, err = _run([sys.executable, str(self.SCRIPT), "--compare", str(a), str(b)])
        rpt = json.loads(out)
        assert rpt["cosine_similarity"] >= 0.85, (
            f"Hook+Cliffhanger (same TTS+voice) cosine {rpt['cosine_similarity']} < 0.85"
        )
