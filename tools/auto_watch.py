"""SVHMP Auto-Watch daemon — Option A round 14 Phase H5.

Poll output/ep_*/episode.md every 5s. New or modified episode → trigger orchestrator
(autofix → vnqa → qa → skeptic chain).

State persists in runtime/auto_watch_state.yaml — file hash + last_processed_ts per ep.
Log: runtime/auto_watch_log.jsonl (1 line per event).

Usage:
  python tools/auto_watch.py                    # Default poll 5s, full chain
  python tools/auto_watch.py --interval 10      # Custom poll interval
  python tools/auto_watch.py --no-autofix       # Skip autofix step
  python tools/auto_watch.py --once             # 1-shot scan + exit (cron mode)

Graceful shutdown: Ctrl+C.
"""
import argparse
import hashlib
import json
import os
import signal
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
OUTPUT_DIR = SVHMP / 'output'
RUNTIME_DIR = SVHMP / 'runtime'
STATE_PATH = RUNTIME_DIR / 'auto_watch_state.yaml'
LOG_PATH = RUNTIME_DIR / 'auto_watch_log.jsonl'
PID_PATH = RUNTIME_DIR / 'auto_watch.pid'

_shutdown = False


def _signal_handler(signum, frame):
    global _shutdown
    print(f'\n[auto_watch] Signal {signum} → graceful shutdown.')
    _shutdown = True


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    import yaml
    return yaml.safe_load(STATE_PATH.read_text(encoding='utf-8')) or {}


def save_state(state: dict):
    import yaml
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(yaml.safe_dump(state, allow_unicode=True), encoding='utf-8')


def log_event(event: dict):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    event['ts'] = datetime.now(timezone.utc).isoformat()
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')


def scan_episodes() -> list:
    """Return list of (ep_number, episode_path) for all output/ep_*/episode.md."""
    found = []
    if not OUTPUT_DIR.exists():
        return found
    for ep_dir in sorted(OUTPUT_DIR.iterdir()):
        if not ep_dir.is_dir() or not ep_dir.name.startswith('ep_'):
            continue
        try:
            ep_num = int(ep_dir.name.split('_')[1])
        except (IndexError, ValueError):
            continue
        ep_path = ep_dir / 'episode.md'
        if ep_path.exists():
            found.append((ep_num, ep_path))
    return found


def trigger_orchestrator(ep_num: int, episode_path: Path, run_autofix: bool) -> dict:
    """Spawn orchestrator subprocess. Return result dict."""
    cmd = [
        'python', str(SVHMP / 'tools' / 'qa_skeptic_orchestrator.py'),
        '--ep', str(ep_num), '--episode', str(episode_path),
    ]
    if not run_autofix:
        cmd.append('--no-autofix')

    print(f'[auto_watch] EP{ep_num} CHANGED → trigger orchestrator...')
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding='utf-8', errors='replace', timeout=600, creationflags=CREATE_NO_WINDOW)
        return {
            'ep': ep_num,
            'rc': result.returncode,
            'elapsed_sec': round(time.time() - start, 1),
            'stdout_tail': (result.stdout or '')[-300:],
            'stderr_tail': (result.stderr or '')[-200:] if result.returncode != 0 else None,
        }
    except subprocess.TimeoutExpired:
        return {'ep': ep_num, 'rc': -1, 'error': 'TIMEOUT 600s'}
    except Exception as e:
        return {'ep': ep_num, 'rc': -1, 'error': str(e)}


def watch_loop(interval: int, run_autofix: bool, once: bool):
    PID_PATH.parent.mkdir(parents=True, exist_ok=True)
    PID_PATH.write_text(str(os.getpid()))
    log_event({'event': 'daemon_start', 'pid': os.getpid(), 'interval': interval, 'once': once})
    print(f'[auto_watch] Daemon started PID={os.getpid()} interval={interval}s once={once}')

    state = load_state()
    try:
        while not _shutdown:
            episodes = scan_episodes()
            for ep_num, ep_path in episodes:
                if _shutdown:
                    break
                current_hash = hash_file(ep_path)
                key = f'ep_{ep_num}'
                prev_hash = state.get(key, {}).get('hash')
                if current_hash != prev_hash:
                    log_event({'event': 'change_detected', 'ep': ep_num,
                               'prev_hash': prev_hash, 'new_hash': current_hash})
                    result = trigger_orchestrator(ep_num, ep_path, run_autofix)
                    log_event({'event': 'orchestrator_done', **result})
                    # Re-hash AFTER orchestrator (autofix may have modified file)
                    new_hash_after = hash_file(ep_path)
                    state[key] = {
                        'hash': new_hash_after,
                        'last_run_ts': datetime.now(timezone.utc).isoformat(),
                        'last_rc': result.get('rc'),
                    }
                    save_state(state)
                    print(f'[auto_watch] EP{ep_num} done rc={result.get("rc")} elapsed={result.get("elapsed_sec")}s')
            if once:
                break
            # Sleep with shutdown check
            for _ in range(interval):
                if _shutdown:
                    break
                time.sleep(1)
    finally:
        try:
            PID_PATH.unlink()
        except Exception:
            pass
        log_event({'event': 'daemon_stop'})
        print('[auto_watch] Stopped.')


def cli():
    parser = argparse.ArgumentParser(description='SVHMP Auto-Watch daemon (Phase H5 Option A)')
    parser.add_argument('--interval', type=int, default=5, help='Poll interval seconds (default 5)')
    parser.add_argument('--no-autofix', action='store_true', help='Skip autofix in orchestrator chain')
    parser.add_argument('--once', action='store_true', help='1-shot scan + exit')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, _signal_handler)

    watch_loop(args.interval, run_autofix=not args.no_autofix, once=args.once)


if __name__ == '__main__':
    cli()
