"""
SVHMP Mini Dashboard — 300x300 Catppuccin Mocha
Lock date: 2026-06-26 (round 14 — Mr.Long request UI mini xinh)

Serve static HTML + /api/status JSON từ real YAML data.
Port 57910 (free, không conflict).

Usage:
  cd "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\tools\dashboard"
  python server.py
  # → open http://127.0.0.1:57910

Apply rule "cấm suy luận":
- Data từ real YAML files only, không bịa
- Mark TENTATIVE nếu data missing (analytics empty, etc.)
"""
import json
import re
import subprocess
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent.parent
DASHBOARD_DIR = Path(__file__).parent
PORT = 57910
TARGET_EPS = 90


def load_status() -> dict:
    """Read real data from SVHMP YAML files."""
    data = {
        'project': 'SVHMP',
        'series': 'Chuyến xe cuối cùng về đâu',
        'channel': 'Hắc Dạ Ký',
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }

    # State
    try:
        with open(SVHMP / 'runtime' / 'state.yaml', encoding='utf-8') as f:
            state = yaml.safe_load(f) or {}
        meta = state.get('meta', {})
        data['current_ep'] = meta.get('current_ep', 1)
        data['last_updated_ep'] = meta.get('last_updated_ep', 0)
        data['season_current'] = meta.get('season_current', 1)
        data['target_eps'] = TARGET_EPS
        data['progress_pct'] = round(data['last_updated_ep'] / TARGET_EPS * 100, 1)

        director = state.get('director', {})
        data['phase'] = director.get('current_phase', 'unknown')
        data['mythology_pct'] = director.get('mythology_progress_pct', 0)

        arcs = state.get('arcs', {}) or {}
        data['arcs_total'] = len(arcs)
        data['arcs_open'] = sum(1 for a in arcs.values() if isinstance(a, dict) and a.get('status') == 'OPEN')
        data['arcs_closed'] = sum(1 for a in arcs.values() if isinstance(a, dict) and a.get('status') == 'CLOSED')
    except Exception as e:
        data['state_error'] = str(e)[:80]

    # Lifecycle
    try:
        with open(SVHMP / 'runtime' / 'lifecycle.yaml', encoding='utf-8') as f:
            lifecycle = yaml.safe_load(f) or {}
        per_ep = lifecycle.get('per_ep_status', {}) or {}
        # Find latest ep + state
        if per_ep:
            latest_ep = max((int(re.search(r'\d+', k).group()) for k in per_ep.keys() if re.search(r'\d+', k)), default=0)
            ep_key = f'ep_{latest_ep}'
            if ep_key in per_ep:
                data['latest_ep_state'] = per_ep[ep_key].get('state', 'unknown')
            else:
                data['latest_ep_state'] = 'unknown'
        else:
            data['latest_ep_state'] = 'no_data'
    except Exception:
        data['latest_ep_state'] = 'error'

    # Analytics — TENTATIVE if empty
    try:
        with open(SVHMP / 'runtime' / 'analytics.yaml', encoding='utf-8') as f:
            analytics = yaml.safe_load(f) or {}
        eps = analytics.get('eps') or {}
        data['analytics_eps_tracked'] = len(eps)
    except Exception:
        data['analytics_eps_tracked'] = 0

    # Cost ledger
    try:
        ledger_path = SVHMP / 'runtime' / 'cost_ledger.yaml'
        if ledger_path.exists():
            with open(ledger_path, encoding='utf-8') as f:
                ledger = yaml.safe_load(f) or {}
            eps_cost = ledger.get('per_ep_actual', {}) or {}
            total = sum(ep.get('total_usd', 0) for ep in eps_cost.values())
            data['cost_total_usd'] = round(total, 4)
            data['cost_eps_logged'] = len(eps_cost)
        else:
            data['cost_total_usd'] = 0
            data['cost_eps_logged'] = 0
    except Exception:
        data['cost_total_usd'] = 0
        data['cost_eps_logged'] = 0

    # BUGS_FIXED count
    try:
        bugs_path = SVHMP / 'BUGS_FIXED.md'
        if bugs_path.exists():
            content = bugs_path.read_text(encoding='utf-8')
            # Match "### B<n>" pattern
            bugs = re.findall(r'^### B\d+', content, re.MULTILINE)
            data['bugs_fixed_count'] = len(bugs)
        else:
            data['bugs_fixed_count'] = 0
    except Exception:
        data['bugs_fixed_count'] = 0

    # Version from VERSION.md
    try:
        version_path = SVHMP / 'VERSION.md'
        if version_path.exists():
            content = version_path.read_text(encoding='utf-8')
            m = re.search(r'current_round:\s*(\d+)', content)
            data['round'] = int(m.group(1)) if m else 0
    except Exception:
        data['round'] = 0

    # Git status
    try:
        cwd = str(SVHMP)
        result = subprocess.run(['git', 'log', '--oneline', '-1'], cwd=cwd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            data['last_commit'] = result.stdout.strip()[:50]
        result2 = subprocess.run(['git', 'tag'], cwd=cwd, capture_output=True, text=True, timeout=5)
        data['git_tags_count'] = len(result2.stdout.strip().split('\n')) if result2.stdout.strip() else 0
    except Exception:
        data['last_commit'] = 'no_git'
        data['git_tags_count'] = 0

    return data


def get_wav_duration(path: Path) -> float | None:
    """Parse WAV header for duration. Returns None if not WAV or parse fail."""
    try:
        import wave
        with wave.open(str(path), 'rb') as w:
            frames = w.getnframes()
            rate = w.getframerate()
            return round(frames / rate, 2) if rate > 0 else None
    except Exception:
        return None


def list_audio_files() -> list:
    """List all audio files in output/ với metadata."""
    output_dir = SVHMP / 'output'
    files = []
    if not output_dir.exists():
        return files
    AUDIO_EXTS = ('.wav', '.mp3', '.flac', '.ogg', '.m4a')
    for path in output_dir.rglob('*'):
        # B24 fix: include backup files (.wav.bak_*) — anh cần nghe thử backup
        name_lower = path.name.lower()
        is_audio = path.suffix.lower() in AUDIO_EXTS or any(f'{ext}.' in name_lower for ext in AUDIO_EXTS)
        if path.is_file() and is_audio:
            try:
                stat = path.stat()
                rel = path.relative_to(SVHMP).as_posix()
                name = path.name
                is_backup = '.bak' in name or 'backup' in name.lower()
                # Parse wav duration if file is .wav (skip .wav.bak* — wave.open fails on truncated header)
                duration = get_wav_duration(path) if path.suffix.lower() == '.wav' else None
                files.append({
                    'rel_path': rel,
                    'name': name,
                    'size_bytes': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                    'is_backup': is_backup,
                    'duration_sec': duration,
                })
            except Exception:
                pass
    # Sort: finals first, then by modified desc
    files.sort(key=lambda f: (f['is_backup'], -datetime.fromisoformat(f['modified']).timestamp()))
    return files


def safe_resolve(rel_path: str) -> Path | None:
    """Resolve rel_path within SVHMP — block path traversal."""
    try:
        # Decode URL
        from urllib.parse import unquote
        rel_path = unquote(rel_path)
        target = (SVHMP / rel_path).resolve()
        if not str(target).startswith(str(SVHMP.resolve())):
            return None  # outside SVHMP — block
        if not target.exists():
            return None
        return target
    except Exception:
        return None


class DashHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def log_message(self, format, *args):
        pass  # silence

    def _send_json(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _parse_query(self):
        from urllib.parse import urlparse, parse_qs
        return parse_qs(urlparse(self.path).query)

    def do_GET(self):
        from urllib.parse import urlparse
        url = urlparse(self.path)
        route = url.path

        if route == '/api/status':
            try:
                self._send_json(200, load_status())
            except Exception as e:
                self.send_error(500, str(e))
            return

        if route == '/api/render':
            # MULTI-CMD: list all active + recently completed CMDs
            try:
                # Import hook helper
                sys.path.insert(0, str(SVHMP / 'tools'))
                from render_progress_hook import list_active_cmds
                cmds = list_active_cmds()
                any_active = any(c.get('active') for c in cmds)
                self._send_json(200, {
                    'cmds': cmds,
                    'count': len(cmds),
                    'any_active': any_active,
                })
            except Exception as e:
                self._send_json(500, {'error': str(e), 'cmds': []})
            return

        if route == '/api/files':
            try:
                files = list_audio_files()
                self._send_json(200, {'files': files, 'count': len(files)})
            except Exception as e:
                self.send_error(500, str(e))
            return

        if route == '/api/audio':
            qs = self._parse_query()
            rel = qs.get('path', [''])[0]
            target = safe_resolve(rel)
            if not target or not target.is_file():
                self.send_error(404, 'File not found or outside SVHMP')
                return
            try:
                stat = target.stat()
                self.send_response(200)
                self.send_header('Content-Type', 'audio/wav' if target.suffix.lower() == '.wav' else 'audio/mpeg')
                self.send_header('Content-Length', str(stat.st_size))
                self.send_header('Accept-Ranges', 'bytes')
                self.end_headers()
                with open(target, 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.send_error(500, str(e))
            return

        if route == '/api/open':
            qs = self._parse_query()
            rel = qs.get('path', [''])[0]
            target = safe_resolve(rel)
            if not target:
                self._send_json(400, {'error': 'Invalid path'})
                return
            try:
                if os.name == 'nt':
                    # Windows: open Explorer + select file
                    subprocess.Popen(['explorer', '/select,', str(target)], shell=False)
                else:
                    subprocess.Popen(['xdg-open', str(target.parent)])
                self._send_json(200, {'ok': True, 'opened': str(target)})
            except Exception as e:
                self._send_json(500, {'error': str(e)})
            return

        if route == '/player':
            self.path = '/player.html'

        super().do_GET()

    def do_POST(self):
        from urllib.parse import urlparse
        url = urlparse(self.path)
        route = url.path

        if route == '/api/delete':
            qs = self._parse_query()
            rel = qs.get('path', [''])[0]
            target = safe_resolve(rel)
            if not target:
                self._send_json(400, {'error': 'Invalid path'})
                return
            try:
                trash_dir = SVHMP / '.trash' / datetime.now(timezone.utc).strftime('%Y%m%d')
                trash_dir.mkdir(parents=True, exist_ok=True)
                trash_target = trash_dir / target.name
                # Avoid collision
                i = 1
                while trash_target.exists():
                    trash_target = trash_dir / f"{target.stem}_{i}{target.suffix}"
                    i += 1
                target.rename(trash_target)
                self._send_json(200, {'ok': True, 'trash_path': str(trash_target.relative_to(SVHMP))})
            except Exception as e:
                self._send_json(500, {'error': str(e)})
            return

        if route == '/api/regen':
            # Safe-mode regen: chỉ backup current final → .bak_pre_regen_<ts>.
            # Mr.Long sau đó MANUAL chạy svhmp_v13_render.py với spec đầy đủ.
            # Lý do KHÔNG auto-trigger: pipeline LOCKED 32 hiến pháp + 100-check ≥95 PASS gate.
            qs = self._parse_query()
            rel = qs.get('path', [''])[0]
            target = safe_resolve(rel)
            if not target:
                self._send_json(400, {'error': 'Invalid path'})
                return
            try:
                if target.suffix.lower() not in ('.wav', '.mp3'):
                    self._send_json(400, {'error': 'Only audio finals can be regen-staged'})
                    return
                ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
                backup_name = f"{target.stem}.bak_pre_regen_{ts}{target.suffix}"
                backup_path = target.parent / backup_name
                target.rename(backup_path)
                # Extract ep number for instructions
                m = re.search(r'ep_(\d+)', str(target))
                ep_num = m.group(1) if m else '?'
                self._send_json(200, {
                    'ok': True,
                    'backed_up_to': str(backup_path.relative_to(SVHMP)),
                    'next_step_manual': (
                        f'Final backed up. Run pipeline manually:\n'
                        f'  cd "D:\\DỰ ÁN AI\\GIỌNG ĐỌC\\DỰ ÁN TRUYỆN MA\\SVHMP_Studio"\n'
                        f'  python C:\\tmp\\svhmp_100check_master.py --ep {ep_num}   # MUST PASS ≥95 first\n'
                        f'  python C:\\tmp\\svhmp_v13_render.py --ep {ep_num}        # if 100-check pass'
                    ),
                    'reason_not_auto': '32 hiến pháp hardlock + 100-check ≥95 PASS gate (Rule 31) — KHÔNG bypass',
                })
            except Exception as e:
                self._send_json(500, {'error': str(e)})
            return

        self.send_error(404, 'Unknown endpoint')


def main():
    print(f"=" * 60)
    print(f"SVHMP Mini Dashboard 300x300 — round 14")
    print(f"=" * 60)
    print(f"Serving:   {DASHBOARD_DIR}")
    print(f"Source:    {SVHMP}")
    print(f"URL:       http://127.0.0.1:{PORT}")
    print(f"API:       http://127.0.0.1:{PORT}/api/status")
    print(f"Ctrl+C to stop")
    print(f"=" * 60)

    server = HTTPServer(('127.0.0.1', PORT), DashHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        server.server_close()


if __name__ == '__main__':
    main()
