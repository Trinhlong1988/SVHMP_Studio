"""
Enforcer LOP (DEBT-hook, 16/7) — bien "quet dinh ky text=True thieu encoding="
(chi la de xuat trong docs/ENVIRONMENT_GOTCHAS.md tu 9/7, KHONG co gate) thanh
gate that. Ngan tai dien lop bug cp1252: subprocess.run(text=True) tren Windows
decode output con bang cp1252 -> child in tieng Viet (byte non-cp1252) -> reader-
thread crash UnicodeDecodeError -> treo/nuot data. Fix chuan = encoding='utf-8',
errors='replace' (xem tools/ci_gate.py, tools/promotion_guard.py::_git).

Cach lam (ratchet allowlist theo FILE + COUNT — R215.5, mutation-proof):
  - Quet AST moi tools/**/*.py tim call .run/.Popen/.check_output/.call co
    text=True (hoac universal_newlines=True) NHUNG THIEU encoding=.
  - File CHUA co trong allowlist ma co vi pham  -> FAIL (instance/file MOI).
  - File trong allowlist nhung so instance TANG hon con so ghi -> FAIL (them moi).
  - So instance GIAM (ai do da fix) -> nhac cap nhat allowlist (khong FAIL cung).
Backlog 11 instance legacy nam trong KNOWN_* kem ref DEBT-hook — sua dan, moi lan
sua thi ha con so trong allowlist. promotion_guard._git ĐA fix (khong con trong list).

Mutation-proof: test_detector_flags_a_synthetic_violation dung 1 file gia co
subprocess.run(text=True) thieu encoding -> detector PHAI bat.
"""
import ast
import warnings
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"

# Backlog legacy (16/7): {relpath: so_instance_duoc_phep}. HA khi fix bot, KHONG tang.
KNOWN_TEXT_TRUE_NO_ENCODING = {
    "auditor.py": 2,
    "dashboard/server.py": 2,
    "event_logger.py": 1,
    "music_loop.py": 2,
    "pre_render_audit.py": 1,
    "project_bootstrap.py": 1,
    "sfx_acquire.py": 2,
}

_CALL_ATTRS = {"run", "Popen", "check_output", "call"}


def _kw_true(call, name):
    for k in call.keywords:
        if k.arg == name and isinstance(k.value, ast.Constant) and k.value.value is True:
            return True
    return False


def _has_kw(call, name):
    return any(k.arg == name for k in call.keywords)


def _violations_in_source(src):
    """Tra ve list lineno cua call text=True/universal_newlines=True thieu encoding=."""
    out = []
    with warnings.catch_warnings():
        # legacy tool files co escape hong (vd '\D') -> DeprecationWarning khi parse; bo qua
        warnings.simplefilter("ignore", DeprecationWarning)
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in _CALL_ATTRS:
            txt = _kw_true(n, "text") or _kw_true(n, "universal_newlines")
            if txt and not _has_kw(n, "encoding"):
                out.append(n.lineno)
    return out


def find_violations():
    """{relpath: [lineno,...]} cho moi tools/**/*.py co vi pham."""
    res = {}
    for p in sorted(TOOLS.rglob("*.py")):
        try:
            v = _violations_in_source(p.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        if v:
            res[p.relative_to(TOOLS).as_posix()] = v
    return res


def test_no_new_text_true_without_encoding():
    found = find_violations()
    new_files = sorted(set(found) - set(KNOWN_TEXT_TRUE_NO_ENCODING))
    grew = {f: (len(found[f]), KNOWN_TEXT_TRUE_NO_ENCODING[f])
            for f in found if f in KNOWN_TEXT_TRUE_NO_ENCODING
            and len(found[f]) > KNOWN_TEXT_TRUE_NO_ENCODING[f]}
    msg = []
    if new_files:
        msg.append("FILE MOI co subprocess text=True THIEU encoding= (them 'encoding=\"utf-8\", "
                    "errors=\"replace\"'): " + ", ".join(f"{f}:{found[f]}" for f in new_files))
    if grew:
        msg.append("File allowlist TANG so instance (them moi -> sua ngay): "
                    + ", ".join(f"{f} now={a} allowed={b}" for f, (a, b) in grew.items()))
    assert not msg, "\n".join(msg)


def test_known_backlog_not_stale():
    """Neu ai do da fix bot 1 instance legacy -> nhac ha con so trong allowlist."""
    found = find_violations()
    shrank = {f: (len(found.get(f, [])), c) for f, c in KNOWN_TEXT_TRUE_NO_ENCODING.items()
              if len(found.get(f, [])) < c}
    assert not shrank, ("Allowlist stale — cac file da giam vi pham, ha con so cho khop:\n"
                        + "\n".join(f"  {f}: thuc te={a} < allowed={b}" for f, (a, b) in shrank.items()))


def test_detector_flags_a_synthetic_violation():
    """Mutation anchor: detector PHAI bat 1 call gia vi pham va BO QUA call co encoding."""
    bad = "import subprocess\nsubprocess.run(['x'], capture_output=True, text=True)\n"
    good = "import subprocess\nsubprocess.run(['x'], capture_output=True, text=True, encoding='utf-8')\n"
    assert _violations_in_source(bad) == [2]
    assert _violations_in_source(good) == []
