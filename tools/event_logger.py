"""Event Log (SVAF pattern #1, TASK_BACKLOG_SVAF_PATTERNS.md — CMD_BUILD_3 4/7).
Append-only KPI trail: runtime/event_log.jsonl, 1 JSON object/line, schema
{ts, ep_id, event, from_state, to_state, gpu, duration_sec}.

Wires into the existing pipeline WITHOUT touching LOCKED sources
(svhmp_v13_render.py v1.3, character_manager.py, roster_validator.py):
this module wraps whatever CLI command runs around them and records the
start/done/fail transition — the locked scripts stay untouched.

Usage (wrap any pipeline CLI call, e.g. render / character_manager / roster_validator):
  python tools/event_logger.py --event render --ep ep_05 -- \
      python tools/svhmp_v13_render.py --spec output/ep_05/spec.json --output output/ep_05/narration.wav

Library usage (no subprocess, log a transition directly, e.g. from auto_watch.py):
  from event_logger import log_event
  log_event(ep_id='ep_05', event='qa_orchestrator', from_state='running', to_state='done', duration_sec=12.3)
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
EVENT_LOG = SVHMP / 'runtime' / 'event_log.jsonl'


def _gpu_name():
    """Best-effort GPU identify via nvidia-smi. 'unknown' if unavailable (no GPU / no driver)."""
    try:
        out = subprocess.run(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip().splitlines()[0]
    except Exception:
        pass
    return 'unknown'


def log_event(ep_id, event, from_state, to_state, duration_sec=None, gpu=None,
              extra=None, log_path=None):
    """Append 1 event record to the JSONL log. Returns the record written."""
    path = Path(log_path) if log_path else EVENT_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'ep_id': ep_id,
        'event': event,
        'from_state': from_state,
        'to_state': to_state,
        'gpu': gpu if gpu is not None else _gpu_name(),
        'duration_sec': round(duration_sec, 3) if duration_sec is not None else None,
    }
    if extra:
        record['extra'] = extra
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    return record


def wrap_and_log(event, ep_id, cmd, from_state='queued', log_path=None):
    """Run `cmd` (arg list) as a subprocess; log queued->running then running->done/failed."""
    log_event(ep_id, event, from_state, 'running', log_path=log_path)
    t0 = time.time()
    proc = subprocess.run(cmd)
    duration = time.time() - t0
    to_state = 'done' if proc.returncode == 0 else 'failed'
    log_event(ep_id, event, 'running', to_state, duration_sec=duration, log_path=log_path)
    return proc.returncode


def main():
    ap = argparse.ArgumentParser(
        description='Event log wrapper — ghi transition quanh 1 lenh pipeline, KHONG sua lenh that.')
    ap.add_argument('--event', required=True, help='ten event, vd render/character_manager/roster_validate')
    ap.add_argument('--ep', required=True, help='ep_id, vd ep_05')
    ap.add_argument('cmd', nargs=argparse.REMAINDER, help='lenh that su, dat sau --')
    args = ap.parse_args()

    cmd = args.cmd[1:] if args.cmd and args.cmd[0] == '--' else args.cmd
    if not cmd:
        print('ERROR: thieu lenh can wrap, dat sau "--" (vd ... -- python tools/x.py)', file=sys.stderr)
        sys.exit(1)
    sys.exit(wrap_and_log(args.event, args.ep, cmd))


if __name__ == '__main__':
    main()
