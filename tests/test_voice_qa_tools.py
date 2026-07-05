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


def _assert_valid_qa_report(rpt: dict, rule_prefix: str, require_n_medium: bool = True) -> None:
    """Kiem tra KIEU + gia tri hop le toi thieu cho report QA (khong chi CO key,
    ma con dung KIEU va nam trong mien gia tri hop ly). Fix LOW finding: truoc day
    chi `assert k in rpt` nen report gia {"n_high": "oops", "verdict": "", ...} van pass.
    """
    assert isinstance(rpt.get("rule"), str) and rpt["rule"].startswith(rule_prefix), (
        f"'rule' phai la string bat dau bang {rule_prefix!r}, got {rpt.get('rule')!r}"
    )
    assert isinstance(rpt.get("wav"), str) and rpt["wav"], (
        f"'wav' phai la string non-empty, got {rpt.get('wav')!r}"
    )
    n_high = rpt.get("n_high")
    assert isinstance(n_high, int) and not isinstance(n_high, bool) and n_high >= 0, (
        f"'n_high' phai la int >= 0, got {n_high!r}"
    )
    if require_n_medium:
        n_medium = rpt.get("n_medium")
        assert isinstance(n_medium, int) and not isinstance(n_medium, bool) and n_medium >= 0, (
            f"'n_medium' phai la int >= 0, got {n_medium!r}"
        )
    verdict = rpt.get("verdict")
    assert isinstance(verdict, str) and verdict in ("PASS", "FAIL"), (
        f"'verdict' phai la string trong {{PASS, FAIL}}, got {verdict!r}"
    )
    findings = rpt.get("findings")
    assert isinstance(findings, list), (
        f"'findings' phai la list, got {type(findings).__name__}"
    )


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


# DEBT-002 (governance/TECH_DEBT.md): cliffhanger.wav / hook.wav bi xoa khoi
# output/ep_01/sections/ (chi con lai .whisper_compare.json ben canh) sau su co 2/7.
# Day KHONG phai "file not found" ngau nhien - day la no ky thuat da duoc ghi
# nhan chinh thuc. Skip reason phai neu ro: file gi thieu, vi sao thieu (nghi
# van), can gi de het skip, va tro ve dung entry TECH_DEBT de nguoi doc theo
# duoc bang chung day du (khong chi dua vao 1 dong message ngan).
_DEBT_002_REASON_CLIFFHANGER = (
    "SKIP (khong phai loi ngau nhien): fixture that "
    "output/ep_01/sections/cliffhanger.wav bi thieu (nghi van: xoa trong su co "
    "2/7, chi con lai cliffhanger.whisper_compare.json ben canh no). "
    "Xem governance/TECH_DEBT.md muc DEBT-002 de biet day du phat hien/bang "
    "chung/de xuat. Can Boss cung cap lai audio that (khong the tu tao gia lap) "
    "de chay lai 5 test case R188/R189/R190/R190b/R191 dang phu thuoc fixture "
    "nay. Trang thai: OPEN."
)
_DEBT_002_REASON_HOOK = (
    "SKIP (khong phai loi ngau nhien): fixture that "
    "output/ep_01/sections/hook.wav bi thieu (nghi van: xoa trong su co 2/7, "
    "chi con lai hook.whisper_compare.json ben canh no). "
    "Xem governance/TECH_DEBT.md muc DEBT-002 de biet day du phat hien/bang "
    "chung/de xuat. Can Boss cung cap lai audio that (khong the tu tao gia lap) "
    "de chay lai test case R181c (embedding cross-section similarity) dang phu "
    "thuoc fixture nay. Trang thai: OPEN."
)


@pytest.fixture(scope="module")
def real_cliffhanger():
    p = SECTIONS / "cliffhanger.wav"
    if not p.exists():
        pytest.skip(_DEBT_002_REASON_CLIFFHANGER)
    return p


@pytest.fixture(scope="module")
def real_hook():
    p = SECTIONS / "hook.wav"
    if not p.exists():
        pytest.skip(_DEBT_002_REASON_HOOK)
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
        _assert_valid_qa_report(rpt, "R188")

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
        _assert_valid_qa_report(rpt, "R189")

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
        segments = rpt.get("segments")
        assert isinstance(segments, int) and not isinstance(segments, bool) and segments >= 0, (
            f"'segments' phai la int >= 0, got {segments!r}"
        )
        threshold = rpt.get("threshold")
        assert isinstance(threshold, (int, float)) and not isinstance(threshold, bool) and threshold > 0, (
            f"'threshold' phai la number > 0, got {threshold!r}"
        )
        n_high = rpt.get("n_high")
        assert isinstance(n_high, int) and not isinstance(n_high, bool) and n_high >= 0, (
            f"'n_high' phai la int >= 0, got {n_high!r}"
        )
        verdict = rpt.get("verdict")
        assert isinstance(verdict, str) and verdict in ("PASS", "FAIL"), (
            f"'verdict' phai la string trong {{PASS, FAIL}}, got {verdict!r}"
        )
        findings = rpt.get("findings")
        assert isinstance(findings, list), (
            f"'findings' phai la list, got {type(findings).__name__}"
        )


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
