"""Guard chong ORPHAN test (deep-audit 2/7): cam file PYTEST-FUNC bi conftest
collect_ignore nuot ma khong co cau noi -> khong gate nao chay = 'built != wired'
cho test. Bat lop loi F3 (test_full_text_gate) + orphan-fix (test_character_gate_g2).

Heuristic: file 'pytest-func' = co 'def test_' VA khong phai script-style
(khong '__main__'/'sys.exit'). File nhu vay KHONG duoc nam trong collect_ignore_glob.

debt3 (5/7): ho trong TRUOC day — file SCRIPT-STYLE (case_N()/main() duoi
`if __name__ == "__main__":`, khong co 'def test_') bi conftest ignore CO CHU DICH
lai khong duoc kiem tra xem co "dang ky" o dau khac (vd test_ci_suite.py SCRIPTS,
chay qua subprocess bridge) hay khong. test_harness.py la vi du: bi ignore co ly do
(script-style + phu thuoc content/daemon, flaky — xem comment trong conftest.py)
NHUNG khong nam trong SCRIPTS -> khong pytest nao, khong subprocess-bridge nao chay
no -> orphan that su ma 2 test cu o tren KHONG bat duoc (chung chi nhin pytest-func).
Them test_script_style_ignored_are_registered_or_documented() de dong khe ho nay:
WARN (khong FAIL) cho loai tru co chu dich da duoc document trong
_DOCUMENTED_SCRIPT_EXCLUSIONS; FAIL cho truong hop khong co ly do (orphan moi,
chua ai xac nhan).
"""
import ast
import fnmatch
import re
import warnings
from pathlib import Path

TESTS = Path(__file__).resolve().parent

# File script-style bi conftest.collect_ignore_glob nuot CO CHU DICH (ly do neu ro
# trong comment cua conftest.py ngay canh entry tuong ung) nhung KHONG dang ky vao
# test_ci_suite.py SCRIPTS. Day la EXCEPTION duoc xac nhan thu cong — khong FAIL,
# chi WARN moi lan pytest chay, de khong ai quen mat no ma khong lam "mu" luon ca
# guard. Them file moi vao day CHI SAU KHI da doc ly do trong conftest.py va xac
# nhan viec khong dang ky la co chu y (khong phai bo quen).
_DOCUMENTED_SCRIPT_EXCLUSIONS = {
    "test_harness.py",  # conftest.py: "script-style + phu thuoc content/daemon
                          # (flaky)" — chay thu cong / qua tools/qa_watch.py,
                          # KHONG dua vao pytest subprocess-bridge.
}


def _ignore_globs():
    txt = (TESTS / "conftest.py").read_text(encoding="utf-8")
    m = re.search(r"collect_ignore_glob\s*=\s*(\[.*?\])", txt, re.S)
    assert m, "khong parse duoc collect_ignore_glob trong conftest.py"
    return ast.literal_eval(m.group(1))


def _is_pytest_func(path):
    t = path.read_text(encoding="utf-8", errors="replace")
    return "def test_" in t and "__main__" not in t and "sys.exit" not in t


def _is_script_style(path):
    """File chay nhu script doc lap: co main-guard (if __name__ == '__main__')
    va KHONG dinh nghia pytest-func nao (khong co 'def test_'). Day la pattern
    da dung boi toan bo test_ci_suite.py SCRIPTS (case_N()/main() + sys.exit)."""
    t = path.read_text(encoding="utf-8", errors="replace")
    has_main_guard = re.search(r"if\s+__name__\s*==\s*['\"]__main__['\"]", t) is not None
    return has_main_guard and "def test_" not in t


def _registered_scripts():
    """Doc SCRIPTS list trong test_ci_suite.py — day la 'cau noi' subprocess-bridge
    khien mot file script-style van duoc pytest thuc thi (qua subprocess + assert
    exit 0) dau khi bi collect_ignore_glob loai khoi collection truc tiep."""
    txt = (TESTS / "test_ci_suite.py").read_text(encoding="utf-8")
    m = re.search(r"SCRIPTS\s*=\s*(\[.*?\])", txt, re.S)
    assert m, "khong parse duoc SCRIPTS trong test_ci_suite.py"
    scripts = ast.literal_eval(m.group(1))
    return {Path(s).name for s in scripts if s.replace("\\", "/").startswith("tests/")}


def test_no_pytest_func_is_ignored():
    globs = _ignore_globs()
    orphans = [
        p.name for p in TESTS.glob("test_*.py")
        if _is_pytest_func(p) and any(fnmatch.fnmatch(p.name, g) for g in globs)
    ]
    assert not orphans, (
        f"pytest-func test bi conftest ignore (orphan — khong gate nao chay): "
        f"{orphans}. Bo khoi collect_ignore_glob HOAC neu that su script-style thi "
        f"them '__main__'/sys.exit + dua vao test_ci_suite.py SCRIPTS."
    )


def test_ignore_list_files_exist():
    # Moi entry trong ignore phai la file that (tranh ignore ma khong con file).
    globs = _ignore_globs()
    missing = [g for g in globs if "*" not in g and not (TESTS / g).exists()]
    assert not missing, f"collect_ignore_glob tro file khong ton tai: {missing}"


def test_script_style_ignored_are_registered_or_documented():
    """debt3: file SCRIPT-STYLE bi conftest ignore ma khong nam trong
    test_ci_suite.py SCRIPTS thi khong gate/bridge nao chay no — orphan, du day
    khong phai la 'pytest-func' nen 2 test o tren khong thay. Phan biet 2 truong
    hop: da document (WARN, biet va chap nhan) vs chua document (FAIL, orphan moi
    chua ai xac nhan)."""
    globs = _ignore_globs()
    script_style_ignored = sorted(
        p.name for p in TESTS.glob("test_*.py")
        if any(fnmatch.fnmatch(p.name, g) for g in globs) and _is_script_style(p)
    )
    registered = _registered_scripts()
    unregistered = [f for f in script_style_ignored if f not in registered]
    undocumented = [f for f in unregistered if f not in _DOCUMENTED_SCRIPT_EXCLUSIONS]

    if unregistered:
        warnings.warn(
            "Script-style test bi conftest ignore nhung KHONG co trong "
            f"test_ci_suite.py SCRIPTS (khong pytest/bridge nao chay): {unregistered}. "
            f"Da document ly do khong-dang-ky (xem conftest.py + "
            f"_DOCUMENTED_SCRIPT_EXCLUSIONS): "
            f"{[f for f in unregistered if f not in undocumented]}."
        )

    assert not undocumented, (
        f"Script-style test bi conftest ignore, KHONG dang ky vao SCRIPTS, VA "
        f"KHONG co ly do document — orphan that su (khong phai loai tru co chu "
        f"dich): {undocumented}. Dang ky vao test_ci_suite.py SCRIPTS, HOAC neu "
        f"loai tru la co chu y thi them vao _DOCUMENTED_SCRIPT_EXCLUSIONS kem ly "
        f"do (va ghi ro trong comment cua conftest.py)."
    )
