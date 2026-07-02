"""Guard chong ORPHAN test (deep-audit 2/7): cam file PYTEST-FUNC bi conftest
collect_ignore nuot ma khong co cau noi -> khong gate nao chay = 'built != wired'
cho test. Bat lop loi F3 (test_full_text_gate) + orphan-fix (test_character_gate_g2).

Heuristic: file 'pytest-func' = co 'def test_' VA khong phai script-style
(khong '__main__'/'sys.exit'). File nhu vay KHONG duoc nam trong collect_ignore_glob.
"""
import ast
import fnmatch
import re
from pathlib import Path

TESTS = Path(__file__).resolve().parent


def _ignore_globs():
    txt = (TESTS / "conftest.py").read_text(encoding="utf-8")
    m = re.search(r"collect_ignore_glob\s*=\s*(\[.*?\])", txt, re.S)
    assert m, "khong parse duoc collect_ignore_glob trong conftest.py"
    return ast.literal_eval(m.group(1))


def _is_pytest_func(path):
    t = path.read_text(encoding="utf-8", errors="replace")
    return "def test_" in t and "__main__" not in t and "sys.exit" not in t


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
