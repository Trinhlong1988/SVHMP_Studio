"""
SVHMP Render Progress Hook — round 14 v2 MULTI-CMD
Lock date: 2026-06-26 (anh approve self-decide multi-CMD architecture)

Multi-CMD support: each script writes own file `runtime/cmd_progress/<cmd_name>.yaml`.
Dashboard `/api/render` lists all active CMDs.

Usage in any pipeline script:
    from tools.render_progress_hook import RenderProgress

    prog = RenderProgress(cmd='v13_render', ep=1, total_steps=24)
    prog.start('preflight')
    prog.tick(1, 'Loading bibles')
    prog.start('generator')
    # ...
    prog.done(success=True, final_path='output/ep_01/narration.wav')

Stale detection: dashboard mark CMD likely_crashed if >30s no update.
Cleanup: completed CMDs auto-remove after 60s (avoid stale list pollution).
"""
import os
import sys
import yaml
import time
import tempfile
import glob
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

SVHMP = Path(__file__).parent.parent
PROGRESS_DIR = SVHMP / 'runtime' / 'cmd_progress'
STALE_SECONDS = 30           # >30s no update → likely crashed
COMPLETED_TTL_SECONDS = 60   # remove completed files after 60s


def cleanup_old_completed():
    """Remove completed CMD files older than COMPLETED_TTL_SECONDS."""
    if not PROGRESS_DIR.exists():
        return
    now = time.time()
    for f in PROGRESS_DIR.glob('*.yaml'):
        try:
            with open(f, encoding='utf-8') as fp:
                data = yaml.safe_load(fp) or {}
            if not data.get('active', True):
                # Check last_update_ts age
                last = data.get('last_update_ts', '')
                if last:
                    last_dt = datetime.fromisoformat(last.replace('Z', '+00:00'))
                    age = (datetime.now(timezone.utc) - last_dt).total_seconds()
                    if age > COMPLETED_TTL_SECONDS:
                        f.unlink()
        except Exception:
            pass


class RenderProgress:
    """Per-CMD write-only progress tracker. Atomic + crash-safe."""

    def __init__(self, cmd: str, ep: int, total_steps: int = 24, pipeline_version: str = 'v1.3'):
        self.cmd = cmd
        self.ep = ep
        self.total_steps = total_steps
        self.pipeline_version = pipeline_version
        self.current_step = 0
        self.current_stage = 'init'
        self.start_ts = time.time()
        self.stage_start_ts = self.start_ts
        self.log_tail = []
        self.extra_data = {}
        self.progress_file = PROGRESS_DIR / f'{cmd}.yaml'
        cleanup_old_completed()
        self._write()

    def _atomic_write(self, data: dict):
        PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
        tmp_fd, tmp_path = tempfile.mkstemp(
            prefix=f'.{self.cmd}_', suffix='.tmp', dir=str(PROGRESS_DIR)
        )
        try:
            with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            os.replace(tmp_path, self.progress_file)
        except Exception:
            try: os.unlink(tmp_path)
            except Exception: pass
            raise

    def _build_payload(self, active: bool = True, success: Optional[bool] = None,
                       final_path: Optional[str] = None) -> dict:
        now = time.time()
        elapsed = now - self.start_ts
        stage_elapsed = now - self.stage_start_ts
        pct = round(self.current_step / max(self.total_steps, 1) * 100, 1)
        eta_s = round(elapsed / self.current_step * (self.total_steps - self.current_step), 1) if (self.current_step > 0 and active) else None
        return {
            'cmd': self.cmd,
            'active': active,
            'ep': self.ep,
            'pipeline_version': self.pipeline_version,
            'stage': self.current_stage,
            'step': self.current_step,
            'total_steps': self.total_steps,
            'progress_pct': pct,
            'elapsed_seconds': round(elapsed, 1),
            'stage_elapsed_seconds': round(stage_elapsed, 1),
            'eta_seconds': eta_s,
            'start_ts': datetime.fromtimestamp(self.start_ts, timezone.utc).isoformat(),
            'last_update_ts': datetime.now(timezone.utc).isoformat(),
            'log_tail': self.log_tail[-20:],
            'success': success,
            'final_path': final_path,
            'extra': self.extra_data,
            'pid': os.getpid(),
        }

    def _write(self, **kwargs):
        try:
            self._atomic_write(self._build_payload(**kwargs))
        except Exception as e:
            print(f"  [progress_hook:{self.cmd}] write fail: {e}", file=sys.stderr)

    def start(self, stage: str):
        self.current_stage = stage
        self.stage_start_ts = time.time()
        self.log_tail.append(f"[{datetime.now().strftime('%H:%M:%S')}] ▶ {stage}")
        self._write()

    def tick(self, step: int, message: str = '', extra: Optional[dict] = None):
        self.current_step = step
        if message:
            self.log_tail.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        if extra:
            self.extra_data.update(extra)
        self._write()

    def done(self, success: bool = True, final_path: Optional[str] = None):
        if success:
            self.current_step = self.total_steps
        self.log_tail.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] {'✓ DONE' if success else '✗ FAIL'}"
            + (f' → {final_path}' if final_path else '')
        )
        self._write(active=False, success=success, final_path=final_path)

    def fail(self, error: str):
        self.log_tail.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ {error[:100]}")
        self.done(success=False)


def list_active_cmds() -> list:
    """For dashboard: list all CMD progress files (active + recently completed)."""
    cleanup_old_completed()
    if not PROGRESS_DIR.exists():
        return []
    cmds = []
    for f in sorted(PROGRESS_DIR.glob('*.yaml')):
        try:
            with open(f, encoding='utf-8') as fp:
                data = yaml.safe_load(fp) or {}
            # Compute stale
            last = data.get('last_update_ts', '')
            if last:
                last_dt = datetime.fromisoformat(last.replace('Z', '+00:00'))
                stale_s = (datetime.now(timezone.utc) - last_dt).total_seconds()
                data['stale_seconds'] = round(stale_s, 1)
                data['likely_crashed'] = stale_s > STALE_SECONDS and data.get('active', False)
            cmds.append(data)
        except Exception:
            pass
    # Active first, then most recent
    cmds.sort(key=lambda c: (not c.get('active'), -datetime.fromisoformat(c['last_update_ts'].replace('Z','+00:00')).timestamp() if c.get('last_update_ts') else 0))
    return cmds


def main():
    """CLI: smoke test simulate render OR list active."""
    import argparse
    parser = argparse.ArgumentParser(description='SVHMP render progress hook v2 multi-CMD')
    parser.add_argument('--cmd', default='test_cmd', help='CMD name (filename prefix)')
    parser.add_argument('--ep', type=int, default=99)
    parser.add_argument('--simulate', action='store_true')
    parser.add_argument('--list', action='store_true', help='List active CMDs')
    args = parser.parse_args()

    if args.list:
        cmds = list_active_cmds()
        if not cmds:
            print("(no active CMDs)")
            return
        for c in cmds:
            status = '⚡ ACTIVE' if c.get('active') else ('✓ DONE' if c.get('success') else '✗ FAIL')
            print(f"{status} {c.get('cmd'):20s} ep={c.get('ep')} {c.get('stage'):12s} {c.get('progress_pct')}%  pid={c.get('pid')}")
        return

    if args.simulate:
        prog = RenderProgress(cmd=args.cmd, ep=args.ep, total_steps=20)
        prog.start('preflight')
        time.sleep(1)
        prog.tick(2, 'Bible loaded')
        time.sleep(1)
        prog.start('generator')
        for i in range(3, 9):
            prog.tick(i, f'Section {i-2}/6')
            time.sleep(1.5)
        prog.start('qa')
        prog.tick(10, 'PHASE 12.14 arc check')
        time.sleep(1)
        prog.start('tts')
        for chunk in range(11, 19):
            prog.tick(chunk, f'TTS chunk {chunk-10}/8', extra={'chunk_dur_s': 5.2})
            time.sleep(1)
        prog.start('post')
        prog.tick(19, 'Loudnorm + concat')
        time.sleep(1)
        prog.done(success=True, final_path=f'output/ep_{args.ep}/narration.wav')
        print(f"✓ Simulated {args.cmd} ep {args.ep}")


if __name__ == '__main__':
    main()
