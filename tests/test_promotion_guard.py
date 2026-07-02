"""Lock hanh vi tools/promotion_guard.py (PACK1 hard-gate HANH VI).

NEGATIVE THAT: commit gia doi promotion_status->locked KHONG authorization -> guard
exit 1; co "per Mr.Long authorization" -> exit 0. Test o repo git TAM (khong dung
repo chinh). + unit test logic thuan.
"""
import subprocess
import sys
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / 'tools' / 'promotion_guard.py'

# import module de test ham thuan
_spec = importlib.util.spec_from_file_location('promotion_guard', GUARD)
pg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pg)


# ---------- unit: logic thuan ----------
def test_decide_lock_without_auth_blocks():
    assert pg.decide(True, False, False)[0] == 1


def test_decide_lock_with_auth_allows():
    assert pg.decide(True, False, True)[0] == 0


def test_decide_tag_without_auth_blocks():
    assert pg.decide(False, True, False)[0] == 1


def test_decide_no_change_allows():
    assert pg.decide(False, False, False)[0] == 0


def test_added_yaml_locked_detected():
    diff = ('+++ b/governance/architecture_registry.yaml\n'
            '-      pack1_constitution: candidate\n'
            '+      pack1_constitution: locked\n')
    assert pg.added_yaml_sets_locked(diff) is True


def test_locked_in_md_not_flagged():
    """'locked' trong .md (prose doc) KHONG bi flag — chi .yaml key."""
    diff = ('+++ b/governance/constitution/00_constitution.md\n'
            '+ Freeze v1.0 = trang thai locked sau khi LEAD duyet.\n')
    assert pg.added_yaml_sets_locked(diff) is False


def test_tag_pattern():
    assert pg.tag_from_ref('refs/tags/pack1-constitution-v1.0') == 'pack1-constitution-v1.0'
    assert pg.tag_from_ref('refs/tags/random-tag') is None
    assert pg.tag_from_ref('refs/heads/main') is None


def test_is_authorized():
    assert pg.is_authorized('feat: freeze pack1 per Mr.Long authorization') is True
    assert pg.is_authorized('feat: freeze pack1') is False


# ---------- integration: repo git tam (NEGATIVE that) ----------
def _git(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True)


def _init_repo(tmp_path):
    d = tmp_path / 'repo'
    d.mkdir()
    _git(d, 'init', '-q')
    _git(d, 'config', 'user.email', 't@t')
    _git(d, 'config', 'user.name', 't')
    reg = d / 'governance'
    reg.mkdir()
    f = reg / 'architecture_registry.yaml'
    f.write_text('enterprise_pack_progress:\n  pack1_constitution: candidate\n', encoding='utf-8')
    _git(d, 'add', '-A')
    _git(d, 'commit', '-qm', 'baseline candidate')
    return d, f


def _run_guard(cwd, base, head, pushed_ref=None):
    args = [sys.executable, str(GUARD), '--base', base, '--head', head]
    if pushed_ref:
        args += ['--pushed-ref', pushed_ref]
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def test_integration_lock_without_auth_exit_1(tmp_path):
    d, f = _init_repo(tmp_path)
    f.write_text('enterprise_pack_progress:\n  pack1_constitution: locked\n', encoding='utf-8')
    _git(d, 'commit', '-aqm', 'freeze pack1 (khong uy quyen)')
    r = _run_guard(d, 'HEAD~1', 'HEAD')
    assert r.returncode == 1, r.stdout + r.stderr


def test_integration_lock_with_auth_exit_0(tmp_path):
    d, f = _init_repo(tmp_path)
    f.write_text('enterprise_pack_progress:\n  pack1_constitution: locked\n', encoding='utf-8')
    _git(d, 'commit', '-aqm', 'freeze pack1 per Mr.Long authorization')
    r = _run_guard(d, 'HEAD~1', 'HEAD')
    assert r.returncode == 0, r.stdout + r.stderr


def test_integration_tag_without_auth_exit_1(tmp_path):
    d, f = _init_repo(tmp_path)
    # commit thuong (khong lock), nhung push tag pack*-v* -> BLOCK
    f.write_text('enterprise_pack_progress:\n  pack1_constitution: candidate\n# touch\n', encoding='utf-8')
    _git(d, 'commit', '-aqm', 'chore: touch')
    r = _run_guard(d, 'HEAD~1', 'HEAD', pushed_ref='refs/tags/pack1-constitution-v1.0')
    assert r.returncode == 1, r.stdout + r.stderr


def test_integration_normal_change_exit_0(tmp_path):
    d, f = _init_repo(tmp_path)
    f.write_text('enterprise_pack_progress:\n  pack1_constitution: candidate\n  note: x\n', encoding='utf-8')
    _git(d, 'commit', '-aqm', 'chore: add note')
    r = _run_guard(d, 'HEAD~1', 'HEAD')
    assert r.returncode == 0, r.stdout + r.stderr
