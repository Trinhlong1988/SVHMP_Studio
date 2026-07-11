"""BUG P0 PACK5 (kiem duyet tai hien 2/7) — negative-test khoa preflight path.

Bug: svhmp_final_verify.py L95 + svhmp_100check_master.py L31 goi preflight qua
hard-path C:\\tmp\\svhmp_preflight_qa.py KHONG ton tai + 'python' tran (Store-stub
PATH) -> buoc preflight cua final_verify DANG CHET (chay ma khong kiem gi).

Khoa 2 lop bug cu tai xuat: (1) hard-path C:\\tmp cho preflight, (2) 'python' tran
cho subprocess preflight. Fix chuan: path resolve TRONG repo (theo __file__) +
sys.executable. KHONG doi logic preflight.

pytest-func -> tu dong collect trong `pytest tests/` va ci_gate.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FINAL_VERIFY = REPO / 'tools' / 'svhmp_final_verify.py'
CHECK_MASTER = REPO / 'tools' / 'svhmp_100check_master.py'
PREFLIGHT = REPO / 'tools' / 'svhmp_preflight_qa.py'


def test_preflight_tool_exists_in_repo():
    """Dich resolve phai ton tai that trong repo (khong phai C:\\tmp)."""
    assert PREFLIGHT.exists(), 'tools/svhmp_preflight_qa.py thieu tren disk'


def test_no_ctmp_hardpath_for_preflight():
    """Negative: cam hard-path C:\\tmp toi svhmp_preflight_qa.py tai xuat."""
    for f in (FINAL_VERIFY, CHECK_MASTER):
        src = f.read_text(encoding='utf-8')
        assert re.search(r'C:[\\/]+tmp[\\/]+svhmp_preflight_qa', src) is None, (
            f'{f.name} van tro preflight qua hard-path C:\\tmp (bug P0 tai xuat)')


def test_no_bare_python_for_preflight_subprocess():
    """Negative: cam 'python' tran trong lenh subprocess goi preflight
    (Store-stub PATH tren Windows -> im lang khong chay gi).
    CHONG PASS RONG: phai tim thay it nhat 1 call-site preflight."""
    src = FINAL_VERIFY.read_text(encoding='utf-8')
    call_sites = [l for l in src.splitlines() if 'svhmp_preflight_qa' in l]
    assert call_sites, 'final_verify mat call-site preflight (buoc preflight bien mat?)'
    for line in call_sites:
        assert "'python'" not in line and '"python"' not in line, (
            'final_verify goi preflight bang python tran thay vi sys.executable')
    assert any('sys.executable' in l for l in call_sites), (
        'final_verify phai goi preflight qua sys.executable')


def test_preflight_paths_resolve_inside_repo():
    """PREFLIGHT cua 100check_master + arg preflight cua final_verify phai
    resolve theo vi tri file (__file__/_TOOLS), khong absolute ngoai repo."""
    cm = CHECK_MASTER.read_text(encoding='utf-8')
    m = re.search(r'^PREFLIGHT\s*=\s*(.+)$', cm, flags=re.M)
    assert m, '100check_master mat dinh nghia PREFLIGHT'
    assert '_TOOLS' in m.group(1) or '__file__' in m.group(1), (
        f'PREFLIGHT khong resolve theo __file__: {m.group(1).strip()}')


# ============================================================
# DEBT-018 (11/7, per Mr.Long authorization) — md_path resolution bug ben trong
# svhmp_preflight_qa.py: spec_path.parents[1] gia dinh spec.json long 2 cap (vd
# output/ep_01/sections/spec_hook.json) nhung spec.json san xuat THAT cua svhmp_
# v13_render.py (output/ep_01/spec.json) chi long 1 cap -> episode.md KHONG
# resolve duoc -> R86 broad EOL AM THAM bi SKIP (chinh 1/2 "bypass" DEBT-018 da
# ghi nhan tu truoc). Fix: thu nhieu vi tri ung vien, fallback REPO/output/ep_NN.
# ============================================================

def test_r86_broad_resolves_for_real_production_spec_single_level():
    """MUTATION-PROOF hanh vi that: goi preflight tren spec.json SAN XUAT THAT
    (output/ep_01/spec.json, chi long 1 cap duoi output/) - R86 broad PHAI CHAY
    (khong duoc roi vao nhanh WARN 'episode.md not found, skip')."""
    import subprocess
    import sys as _sys
    r = subprocess.run([_sys.executable, str(PREFLIGHT), str(REPO / 'output' / 'ep_01' / 'spec.json')],
                       capture_output=True, text=True, encoding='utf-8', cwd=str(REPO))
    out = r.stdout
    assert '[FULL_TEXT_GATE] R86 broad EOL check via qa_eol_diacritic.py' in out, (
        f"R86 broad KHONG chay tren spec.json san xuat THAT (bug md_path resolution "
        f"tai xuat) - stdout: {out[-800:]}")
    assert 'episode.md not found' not in out, f"van con nhanh SKIP am tham: {out[-800:]}"


def test_r86_broad_still_resolves_for_legacy_nested_section_spec():
    """Khong pha hanh vi CU (spec.json long 2 cap kieu output/ep_01/sections/
    spec_hook.json) - phai VAN chay R86 broad dung nhu truoc khi fix."""
    import subprocess
    import sys as _sys
    section_spec = REPO / 'output' / 'ep_01' / 'sections' / 'spec_hook.json'
    if not section_spec.exists():
        return  # khong co du lieu legacy nay tren may - khong gia dinh, khong FAIL sai
    r = subprocess.run([_sys.executable, str(PREFLIGHT), str(section_spec)],
                       capture_output=True, text=True, encoding='utf-8', cwd=str(REPO))
    assert '[FULL_TEXT_GATE] R86 broad EOL check via qa_eol_diacritic.py' in r.stdout, (
        f"regression: spec long 2 cap (hanh vi cu) khong con chay R86 broad: {r.stdout[-800:]}")
