"""
test_full_text_gate_r86_broad.py — Regression for process gap PV-01..04
Mr.Long lock 30/6 23:00 — Add regression case proving R86 NGA/NANG/HOI
cannot bypass Phase 0 again.

Prove svhmp_preflight_qa.py now chains qa_eol_diacritic.py and blocks
NGA + NANG + HOI EOL violations introduced by any future text edit.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PREFLIGHT = REPO_ROOT / "tools" / "svhmp_preflight_qa.py"
QA_EOL = REPO_ROOT / "tools" / "qa_eol_diacritic.py"


@pytest.fixture
def fake_ep_dir(tmp_path):
    """Create a fake ep_99 dir layout with episode.md + sections/spec_test.json."""
    ep_dir = tmp_path / "ep_99"
    sections = ep_dir / "sections"
    sections.mkdir(parents=True)
    return ep_dir, sections


def make_spec(sections_dir: Path, sentences: list[dict]) -> Path:
    spec = {"sentences": sentences, "sample_prompt": "TEST"}
    p = sections_dir / "spec_test.json"
    p.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def run_preflight(spec_path: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(PREFLIGHT), str(spec_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def test_preflight_chains_qa_eol_diacritic_NGA(fake_ep_dir):
    """R86 NGA EOL must block preflight (PV-01 regression)."""
    ep_dir, sections = fake_ep_dir
    (ep_dir / "episode.md").write_text(
        "Đêm đã buông xuống thật chậm rãi. Một câu kết thúc bình thường.\n",
        encoding="utf-8",
    )
    spec_path = make_spec(sections, [{"text": "Đêm đã buông xuống thật chậm rãi.", "pause_after_ms": 1000, "is_dialogue": False, "emo_vector": [0]*8}])
    rc, out = run_preflight(spec_path)
    assert rc != 0, f"Expected FAIL on NGA EOL 'rãi', got rc=0 with output:\n{out}"
    assert "NGA" in out or "R86" in out, f"Expected R86/NGA marker in output:\n{out}"


def test_preflight_chains_qa_eol_diacritic_NANG(fake_ep_dir):
    """R86 NANG EOL must block preflight (PV-02 regression)."""
    ep_dir, sections = fake_ep_dir
    (ep_dir / "episode.md").write_text(
        "Cô ấy mỉm cười, vẫy tay một cái rất nhẹ.\n",
        encoding="utf-8",
    )
    spec_path = make_spec(sections, [{"text": "Cô ấy mỉm cười, vẫy tay một cái rất nhẹ.", "pause_after_ms": 1000, "is_dialogue": False, "emo_vector": [0]*8}])
    rc, out = run_preflight(spec_path)
    assert rc != 0, f"Expected FAIL on NANG EOL 'nhẹ', got rc=0 with output:\n{out}"
    assert "NANG" in out or "R86" in out, f"Expected R86/NANG marker in output:\n{out}"


def test_preflight_chains_qa_eol_diacritic_HOI(fake_ep_dir):
    """R86 HOI EOL must block preflight (PV-03 regression)."""
    ep_dir, sections = fake_ep_dir
    (ep_dir / "episode.md").write_text(
        "Cô ấy không hề trả lời gì cả.\n",
        encoding="utf-8",
    )
    spec_path = make_spec(sections, [{"text": "Cô ấy không hề trả lời gì cả.", "pause_after_ms": 1000, "is_dialogue": False, "emo_vector": [0]*8}])
    rc, out = run_preflight(spec_path)
    assert rc != 0, f"Expected FAIL on HOI EOL 'cả', got rc=0 with output:\n{out}"
    assert "HOI" in out or "R86" in out, f"Expected R86/HOI marker in output:\n{out}"


def test_preflight_clean_text_passes_r86_broad(fake_ep_dir):
    """Clean text with safe EOL tones (HUYEN/SAC/KHONG) must PASS."""
    ep_dir, sections = fake_ep_dir
    (ep_dir / "episode.md").write_text(
        "Đêm đã buông xuống lặng lẽ trên thành phố. Anh chậm rãi bước về nhà mình.\n",
        encoding="utf-8",
    )
    spec_path = make_spec(sections, [
        {"text": "Đêm đã buông xuống lặng lẽ trên thành phố.", "pause_after_ms": 1000, "is_dialogue": False, "emo_vector": [0]*8},
        {"text": "Anh chậm rãi bước về nhà mình.", "pause_after_ms": 1000, "is_dialogue": False, "emo_vector": [0]*8, "_signature_tail": True},
    ])
    rc, out = run_preflight(spec_path)
    # R86 broad must PASS. R1/R5 (existing rules) may still flag (short last chunk / missing ending phrase)
    # but R86 line must be present and PASS.
    assert "FULL_TEXT_GATE" in out, f"Expected FULL_TEXT_GATE invocation:\n{out}"
    # Look for "R86 EOL violations: 0" line from qa_eol_diacritic
    assert "R86 EOL violations: 0" in out, f"R86 broad must report 0 violations:\n{out}"


def test_preflight_skip_r86_flag_works(fake_ep_dir):
    """--skip-r86 must bypass R86 broad check (escape hatch for emergencies)."""
    ep_dir, sections = fake_ep_dir
    (ep_dir / "episode.md").write_text(
        "Đêm đã buông xuống thật chậm rãi.\n",
        encoding="utf-8",
    )
    spec_path = make_spec(sections, [{"text": "Đêm đã buông xuống thật chậm rãi.", "pause_after_ms": 1000, "is_dialogue": False, "emo_vector": [0]*8, "_signature_tail": True}])
    proc = subprocess.run(
        [sys.executable, str(PREFLIGHT), str(spec_path), "--skip-r86"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    # R86 should NOT block when --skip-r86 passed
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "FULL_TEXT_GATE" not in out or "R86" not in out, f"--skip-r86 must bypass R86:\n{out}"
