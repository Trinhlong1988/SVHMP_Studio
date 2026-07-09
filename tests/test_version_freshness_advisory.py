"""Version freshness ADVISORY — chung thuc phat hien VERSION.md drift.
KHONG gate (khong duoc doi verdict cua decide()). R195: advisory truoc, LEAD promote hard-gate sau.
Test tren TEMPFILE (bai hoc DEBT-005: khong dung file that -> khong race voi phien khac).
pytest-native -> `pytest -q`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import auditor  # noqa: E402


def _fixture(tmp_path, ver_ts, released):
    v = tmp_path / 'VERSION.md'
    v.write_text(f"---\ncurrent_round: 1\nlast_update_ts: {ver_ts}\n---\n", encoding='utf-8')
    c = tmp_path / 'build_claim.yaml'
    body = "claims:\n"
    for i, r in enumerate(released):
        body += f"  p{i}:\n    session: X\n    released_at: '{r}'\n    status: released\n"
    c.write_text(body, encoding='utf-8')
    return v, c


def test_stale_detected(tmp_path):
    # VERSION.md cu hon pack release moi nhat -> STALE
    v, c = _fixture(tmp_path, '2026-06-30T19:30:00', ['2026-07-05T22:18:22', '2026-07-04T10:00:00'])
    name, ok, detail = auditor.version_freshness_advisory(v, c)
    assert name == 'VersionFreshness'
    assert ok is False and 'STALE' in detail


def test_fresh_ok(tmp_path):
    # VERSION.md moi hon pack release moi nhat -> OK
    v, c = _fixture(tmp_path, '2026-07-06T00:00:00', ['2026-07-05T22:18:22'])
    _, ok, _ = auditor.version_freshness_advisory(v, c)
    assert ok is True


def test_equal_is_fresh(tmp_path):
    # bang nhau -> khong stale (>=)
    v, c = _fixture(tmp_path, '2026-07-05T22:18:22', ['2026-07-05T22:18:22'])
    _, ok, _ = auditor.version_freshness_advisory(v, c)
    assert ok is True


def test_missing_data_skips(tmp_path):
    # thieu du lieu -> skip (khong bao dong gia)
    v = tmp_path / 'VERSION.md'; v.write_text('khong co ts', encoding='utf-8')
    c = tmp_path / 'build_claim.yaml'; c.write_text('claims: {}\n', encoding='utf-8')
    _, ok, detail = auditor.version_freshness_advisory(v, c)
    assert ok is True and 'skip' in detail.lower()


def test_advisory_never_changes_verdict():
    # BAT BIEN: advisory KHONG duoc gate — decide() chi phu thuoc results
    P = ('X', True, 'ok', 0)
    assert auditor.decide([P, P, P]) == ('SHIP', 0)
    F = ('Y', False, 'bad', 1)
    assert auditor.decide([P, F]) == ('BLOCK_SHIP', 1)
