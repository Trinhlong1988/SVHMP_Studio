"""Event Log wrapper (SVAF backlog #1, CMD_BUILD_3 4/7): validate JSONL schema
{ts, ep_id, event, from_state, to_state, gpu, duration_sec} + subprocess wrap
success/fail transitions. KHONG dung runtime/event_log.jsonl that (log_path override)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from event_logger import log_event, wrap_and_log

SCHEMA_KEYS = {'ts', 'ep_id', 'event', 'from_state', 'to_state', 'gpu', 'duration_sec'}


def _read_records(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def test_log_event_schema(tmp_path):
    log_path = tmp_path / 'event_log.jsonl'
    rec = log_event('ep_99', 'unit_test', 'queued', 'running', gpu='cpu-only', log_path=log_path)
    assert SCHEMA_KEYS.issubset(rec.keys())
    assert rec['ep_id'] == 'ep_99' and rec['event'] == 'unit_test'
    records = _read_records(log_path)
    assert len(records) == 1
    assert records[0]['from_state'] == 'queued' and records[0]['to_state'] == 'running'


def test_log_event_appends_not_overwrites(tmp_path):
    log_path = tmp_path / 'event_log.jsonl'
    log_event('ep_01', 'a', 'x', 'y', log_path=log_path)
    log_event('ep_01', 'b', 'y', 'z', log_path=log_path)
    records = _read_records(log_path)
    assert len(records) == 2
    assert [r['event'] for r in records] == ['a', 'b']


def test_wrap_and_log_success(tmp_path):
    log_path = tmp_path / 'event_log.jsonl'
    rc = wrap_and_log('unit_ok', 'ep_02', [sys.executable, '-c', 'import sys; sys.exit(0)'],
                       log_path=log_path)
    assert rc == 0
    records = _read_records(log_path)
    assert len(records) == 2
    assert records[0]['to_state'] == 'running'
    assert records[1]['to_state'] == 'done'
    assert records[1]['duration_sec'] is not None


def test_wrap_and_log_failure(tmp_path):
    log_path = tmp_path / 'event_log.jsonl'
    rc = wrap_and_log('unit_fail', 'ep_03', [sys.executable, '-c', 'import sys; sys.exit(2)'],
                       log_path=log_path)
    assert rc == 2
    records = _read_records(log_path)
    assert records[-1]['to_state'] == 'failed'


def test_duration_sec_rounded(tmp_path):
    log_path = tmp_path / 'event_log.jsonl'
    rec = log_event('ep_04', 'c', 'x', 'y', duration_sec=1.23456789, log_path=log_path)
    assert rec['duration_sec'] == 1.235
