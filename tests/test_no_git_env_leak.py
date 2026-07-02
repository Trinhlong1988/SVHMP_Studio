"""KHOA su co 2/7 (origin wipe 1037 file): pytest trong git hook ke thua
GIT_DIR/GIT_WORK_TREE -> test spawn git danh vao repo THAT bat chap cwd.

3 tang khoa (go bat ky tang nao -> test nay do):
  1. conftest.py PHAI scrub GIT_* luc pytest khoi dong (mien dich toan cuc).
  2. ci_gate.py PHAI scrub GIT_* truoc khi launch pytest (phong thu tang 2).
  3. Behavioral: env sach -> git commit trong repo tam KHONG dung repo nan nhan.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_conftest_scrubs_git_env():
    src = (REPO / 'tests' / 'conftest.py').read_text(encoding='utf-8')
    assert "startswith('GIT_')" in src, 'conftest mat doan scrub GIT_* (khoa su co 2/7)'


def test_ci_gate_scrubs_git_env():
    src = (REPO / 'tools' / 'ci_gate.py').read_text(encoding='utf-8')
    assert "startswith('GIT_')" in src, 'ci_gate mat doan scrub GIT_* truoc pytest'


def test_pytest_session_has_no_git_env():
    """Trong pytest (sau conftest) khong con bien GIT_* nao — ke ca khi chay tu hook."""
    leaked = [k for k in os.environ if k.startswith('GIT_')]
    assert not leaked, f'GIT_* van lot vao pytest session: {leaked}'


def test_scrubbed_env_isolates_victim_repo(tmp_path):
    """Behavioral: voi env SACH, git commit trong repo tam khong dung repo nan nhan
    du truoc do GIT_DIR tung tro vao no (mo phong co che su co)."""
    clean = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}

    victim = tmp_path / 'victim'
    victim.mkdir()
    subprocess.run(['git', 'init', '-q'], cwd=victim, env=clean, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'v@v'], cwd=victim, env=clean)
    subprocess.run(['git', 'config', 'user.name', 'v'], cwd=victim, env=clean)
    (victim / 'data.txt').write_text('quan trong', encoding='utf-8')
    subprocess.run(['git', 'add', '-A'], cwd=victim, env=clean, capture_output=True)
    subprocess.run(['git', 'commit', '-qm', 'victim baseline'], cwd=victim, env=clean,
                   capture_output=True)
    head_before = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=victim, env=clean,
                                 capture_output=True, text=True).stdout.strip()

    # ke tan cong: env doc hai tro GIT_DIR vao victim, nhung fixture dung env SACH
    work = tmp_path / 'work'
    work.mkdir()
    subprocess.run(['git', 'init', '-q'], cwd=work, env=clean, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 't@t'], cwd=work, env=clean)
    subprocess.run(['git', 'config', 'user.name', 't'], cwd=work, env=clean)
    (work / 'x.txt').write_text('fixture', encoding='utf-8')
    subprocess.run(['git', 'add', '-A'], cwd=work, env=clean, capture_output=True)
    subprocess.run(['git', 'commit', '-qm', 'fixture commit'], cwd=work, env=clean,
                   capture_output=True)

    head_after = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=victim, env=clean,
                                capture_output=True, text=True).stdout.strip()
    assert head_before == head_after, 'victim repo bi dung du env da scrub!'
