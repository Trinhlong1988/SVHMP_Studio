"""PACK CLAIM guard (Mr.Long ky 4/7) — behavioral: claim-de-phien-khac PHAI do,
release dung chu, MASTER luat 11 khong bi go (unwire-guard tinh than test_bp5).

pytest-func FLAT -> collect trong `pytest tests/` va ci_gate.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / 'tools' / 'build_claim.py'


def _run(tmp_file, *args):
    return subprocess.run([sys.executable, str(CLI), *args, '--file', str(tmp_file)],
                          capture_output=True, text=True, encoding='utf-8')


def test_claim_fresh_ok(tmp_path):
    r = _run(tmp_path / 'c.yaml', 'claim', 'bp7_narrative', 'CMD_BUILD')
    assert r.returncode == 0 and 'CLAIM-OK' in r.stdout, r.stdout


def test_claim_taken_by_other_session_bites(tmp_path):
    f = tmp_path / 'c.yaml'
    assert _run(f, 'claim', 'bp7_narrative', 'CMD_BUILD').returncode == 0
    r = _run(f, 'claim', 'bp7_narrative', 'G2_EXECUTOR')
    assert r.returncode == 1, 'claim de phien khac PHAI exit 1'
    assert 'CLAIM-FAIL' in r.stdout and 'CMD_BUILD' in r.stdout, r.stdout


def test_reclaim_same_session_idempotent(tmp_path):
    f = tmp_path / 'c.yaml'
    _run(f, 'claim', 'bp7_narrative', 'CMD_BUILD')
    assert _run(f, 'claim', 'bp7_narrative', 'CMD_BUILD').returncode == 0


def test_release_then_other_can_claim(tmp_path):
    f = tmp_path / 'c.yaml'
    _run(f, 'claim', 'bp7_narrative', 'CMD_BUILD')
    assert _run(f, 'release', 'bp7_narrative', 'CMD_BUILD').returncode == 0
    assert _run(f, 'claim', 'bp7_narrative', 'G2_EXECUTOR').returncode == 0


def test_release_wrong_session_bites(tmp_path):
    f = tmp_path / 'c.yaml'
    _run(f, 'claim', 'bp7_narrative', 'CMD_BUILD')
    r = _run(f, 'release', 'bp7_narrative', 'G2_EXECUTOR')
    assert r.returncode == 1 and 'RELEASE-FAIL' in r.stdout, r.stdout


def test_master_rule11_wired():
    """Go luat 11 khoi BP_PIPELINE_MASTER = test nay do (chong unwire)."""
    text = (REPO / 'prompts' / 'BP_PIPELINE_MASTER.md').read_text(encoding='utf-8')
    assert 'build_claim.py claim' in text, 'MASTER luat 11 PACK CLAIM bi go!'


def test_claim_file_exists_and_parses():
    """Fix LOW finding: truoc day chi check 'claims' in data nen claims: {} hoac
    claims: null van pass. Gio check KIEU + gia tri hop le toi thieu cho tung claim
    that (dict non-empty, moi record co status hop le + session non-empty)."""
    import yaml
    data = yaml.safe_load((REPO / 'runtime' / 'build_claim.yaml').read_text(encoding='utf-8'))
    assert isinstance(data, dict), f"build_claim.yaml top-level phai la dict, got {type(data).__name__}"
    claims = data.get('claims')
    assert isinstance(claims, dict) and len(claims) > 0, (
        f"'claims' phai la dict non-empty (it nhat 1 pack claim that da tung xay ra), got {claims!r}"
    )
    for pack, rec in claims.items():
        assert isinstance(rec, dict), f"claim '{pack}' phai la dict, got {type(rec).__name__}"
        status = rec.get('status')
        assert isinstance(status, str) and status in ('active', 'released'), (
            f"claim '{pack}' status phai la 'active' hoac 'released', got {status!r}"
        )
        session = rec.get('session')
        assert isinstance(session, str) and session, (
            f"claim '{pack}' thieu 'session' (string non-empty), got {session!r}"
        )
