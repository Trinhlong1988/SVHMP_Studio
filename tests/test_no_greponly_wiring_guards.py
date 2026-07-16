"""tests/test_no_greponly_wiring_guards.py — RATCHET chong lop bug "grep-only wiring guard".

R215.5 (CLAUDE.md, codify 16/7) + DEBT-037: mot so test TU XUNG la "unwire-guard" /
"wiring test" / "composition guard" nhung THAN test CHI text-grep source
(`assert "<ten_ham>" in src`) -> MU voi viec unwire that su: thay call THAT bang no-op
ma GIU token (comment/dead-string) thi assert `"<ten_ham>" in src` VAN True -> guard khong
bao gio bat duoc regression no tuyen bo bao ve. Vi du goc (da chung minh mu bang mo phong
unwire): tests/test_regret_variety_check.py::test_preflight_has_regret_variety_gate_wired.

Meta-test nay QUET tinh (ast) toan bo tests/ tim lop loi do va FAIL neu xuat hien 1 guard
grep-only-wiring MOI ngoai allowlist (ratchet). Cac vi pham HIEN CO nam trong
KNOWN_GREPONLY_GUARDS (moi entry tro DEBT tuong ung) de suite khong do ngay voi backlog cu;
BAT KY guard grep-only-wiring MOI nao NGOAI allowlist -> FAIL.

Dinh nghia "grep-only wiring guard" (ca 4 dieu kien, thiet ke it false-positive):
  1. TU XUNG wiring: ten ham / docstring / string literal (vd assert message) chua 1 token
     wiring ('unwire', 'wired', 'wiring', 'reachable', 'composition invariant', ...).
  2. CO grep source-text: it nhat 1 phep `<x> in <var>` voi <var> la bien gan tu
     `.read_text()`/`.read_bytes()` (source text) — DAY la chu ky "grep".
  3. KHONG co dau hieu HANH VI: khong subprocess/monkeypatch/capsys/pytest.raises/setattr,
     va khong membership vao live-object (`X in module.CONST` hoac `X in <collection dan tu
     call/comprehension>`). Neu co bat ky dau hieu nay -> guard co kiem chung THAT -> BO QUA.
  4. KHONG phai doc/config-presence: neu MOI read chi doc .md/.yml/.yaml/.json/.txt ...
     (khong doc .py / githook) -> day la kiem tra su hien dien cua tai lieu/cau hinh
     (lop KHAC, chap nhan duoc) -> BO QUA. Chi grep SOURCE CODE (.py / githook) moi tinh.

Ratchet: sua 1 guard trong allowlist thanh behavioral -> detector thoi flag no ->
test_allowlist_entries_not_stale se WARN de nhac go entry khoi allowlist.
"""
import ast
import warnings
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SELF = Path(__file__).name

# ---- Signals -------------------------------------------------------------
WIRING_TOKENS = (
    "unwire", "wired", "wiring", "reachable",
    "composition invariant", "built != wired", "chong unwire",
    "wire vao", "wire into",
)
BEHAVIORAL_NAMES = {"subprocess", "monkeypatch", "capsys", "capfd", "caplog", "tmp_path"}
BEHAVIORAL_ATTRS = {"setattr", "raises", "run"}   # monkeypatch.setattr / pytest.raises / subprocess.run
CODE_SUFFIXES = (".py",)
HOOK_NAMES = ("pre-commit", "pre-push", "commit-msg")

# ---- ALLOWLIST (ratchet): vi pham grep-only-wiring HIEN CO (KHONG do ngay) --------
# Moi entry (test_file, test_func) -> ly do + DEBT. BAT KY guard MOI ngoai day -> FAIL.
KNOWN_GREPONLY_GUARDS = {
    # test_regret_variety_check.py::test_preflight_has_regret_variety_gate_wired DA nang
    # behavioral (DEBT-037a, CMD_AUDIT 16/7) -> GO khoi allowlist (ratchet tien, khong con la
    # vi pham). Seed self-test doi sang guard g2 con lai ben duoi.
    ("test_gate_wired_g2.py", "test_character_gate_reachable_via_wrapper"):
        "DEBT-037 / R215.5 — chi grep WIRE_MARKERS + 'svhmp_v13_render.py' in "
        "render_with_character_gate.py source. Co coverage behavioral O CHO KHAC trong CUNG file "
        "(run_character_gate BLOCK tren du lieu that), nhung ham NAY thi grep-only.",
}


# ---- AST helpers ---------------------------------------------------------
def _str_consts(node):
    return [n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _is_read_call(v):
    return (isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute)
            and v.func.attr in ("read_text", "read_bytes"))


def _scalar_string_map(tree):
    """name -> [string consts] CHI tu Assign co RHS la path SCALAR (khong List/Dict/Set/Tuple).

    Co y bo qua list/dict (vd PACK3_DOCS=['..md'], enforcers={..:'..py'}) de KHONG dinh
    nham .py o VALUE cua dict lam 'read code'. Chi resolve bien tro toi 1 path don (vd
    WRAPPER = REPO / 'tools' / 'x.py')."""
    m = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            if isinstance(n.value, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
                continue
            consts = _str_consts(n.value)
            if not consts:
                continue
            for t in n.targets:
                if isinstance(t, ast.Name):
                    m.setdefault(t.id, []).extend(consts)
    return m


def _text_vars(func):
    """Bien gan truc tiep tu .read_text()/.read_bytes() (chua source text)."""
    tv = set()
    for n in ast.walk(func):
        if isinstance(n, ast.Assign) and _is_read_call(n.value):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    tv.add(t.id)
    return tv


def _nonread_assigned(func):
    """Bien gan tu gia tri KHONG phai read_text (call/comprehension/...) — ung vien live-object."""
    s = set()
    for n in ast.walk(func):
        if isinstance(n, ast.Assign) and not _is_read_call(n.value):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    s.add(t.id)
    return s


def _wiring_claim(func):
    doc = (ast.get_docstring(func) or "").lower()
    blob = func.name.lower() + " " + doc + " " + " ".join(_str_consts(func)).lower()
    return any(tok in blob for tok in WIRING_TOKENS)


def _has_source_text_membership(func, text_vars):
    for n in ast.walk(func):
        if isinstance(n, ast.Compare) and any(isinstance(op, (ast.In, ast.NotIn)) for op in n.ops):
            rhs = n.comparators[0]
            if isinstance(rhs, ast.Name) and rhs.id in text_vars:
                return True
            if _is_read_call(rhs):
                return True
    return False


def _has_behavioral_marker(func, text_vars, nonread):
    for n in ast.walk(func):
        if isinstance(n, ast.Name) and n.id in BEHAVIORAL_NAMES:
            return True
        if isinstance(n, ast.Attribute) and n.attr in BEHAVIORAL_ATTRS:
            return True
        if isinstance(n, ast.Compare) and any(isinstance(op, (ast.In, ast.NotIn)) for op in n.ops):
            rhs = n.comparators[0]
            # membership vao live object: module.CONST (Attribute) hoac collection dan tu call/comprehension
            if isinstance(rhs, ast.Attribute):
                return True
            if isinstance(rhs, ast.Name) and rhs.id not in text_vars and rhs.id in nonread:
                return True
    return False


def _reads_confirmed_code(func, scalar_map):
    """True neu CO it nhat 1 `.read_text()/.read_bytes()` ma DUONG DAN xac nhan tro toi
    file SOURCE CODE (.py) hoac githook. Path consts = literal truc tiep trong path expr +
    resolve cac Name qua scalar_map (chi bien scalar). KHONG resolve loop-var / dict-value
    -> conservative: khong xac nhan duoc code -> KHONG flag (uu tien tranh false-positive;
    ratchet + allowlist bu lai). Phan biet doc-presence (.md/.yml) voi grep source that."""
    for n in ast.walk(func):
        if not _is_read_call(n):
            continue
        path_obj = n.func.value
        consts = list(_str_consts(path_obj))
        for nm in _names(path_obj):
            consts.extend(scalar_map.get(nm, []))
        for c in consts:
            base = c.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
            if base.endswith(CODE_SUFFIXES) or base in HOOK_NAMES:
                return True
    return False


def find_greponly_wiring_guards():
    """Tra ve set (test_file_basename, test_func_name) cho MOI grep-only-wiring guard."""
    hits = set()
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        if path.name == SELF:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        smap = _scalar_string_map(tree)
        for fn in [n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]:
            if not _wiring_claim(fn):
                continue
            tv = _text_vars(fn)
            if not _has_source_text_membership(fn, tv):
                continue
            if _has_behavioral_marker(fn, tv, _nonread_assigned(fn)):
                continue
            if not _reads_confirmed_code(fn, smap):
                continue
            hits.add((path.name, fn.name))
    return hits


# ---- Tests ---------------------------------------------------------------
def test_no_new_greponly_wiring_guards():
    """RATCHET: bat ky test grep-only-wiring MOI (ngoai KNOWN_GREPONLY_GUARDS) -> FAIL.

    Fix dung: viet guard BEHAVIORAL (import module + kiem live-object CHECKS/SUITE, HOAC
    goi ham thuc thi + mutation-proof, HOAC subprocess exit-code) thay vi grep source text.
    Xem mirror dung: test_supernatural_run_all_composition.py (_run_all_body_ok +
    monkeypatch injection) / cac *_stage_wired_in_ci_gate kiem `(...) in ci_gate.CHECKS`.
    """
    flagged = find_greponly_wiring_guards()
    known = set(KNOWN_GREPONLY_GUARDS)
    new = sorted(flagged - known)
    assert not new, (
        "Guard grep-only-wiring MOI (chi text-grep source, MU voi unwire — R215.5/DEBT-037):\n  "
        + "\n  ".join(f"{f}::{t}" for f, t in new)
        + "\n=> Viet guard BEHAVIORAL (kiem live-object / goi ham + mutation-proof / subprocess "
          "exit-code), KHONG grep `\"<ten_ham>\" in src`. Neu that su co ly do giu grep-only, "
          "them vao KNOWN_GREPONLY_GUARDS kem DEBT ref."
    )


def test_allowlist_entries_not_stale():
    """WARN (khong FAIL): entry allowlist khong con bi detector flag (co the da fix behavioral)
    -> nhac go khoi KNOWN_GREPONLY_GUARDS de ratchet siet dan. Khong FAIL de tranh vo suite
    khi guard duoc fix o worktree/commit khac."""
    flagged = find_greponly_wiring_guards()
    stale = sorted(set(KNOWN_GREPONLY_GUARDS) - flagged)
    if stale:
        warnings.warn(
            "KNOWN_GREPONLY_GUARDS co entry khong con la grep-only (co the da fix behavioral): "
            + ", ".join(f"{f}::{t}" for f, t in stale)
            + " — can nhac go khoi allowlist (ratchet)."
        )


def test_detector_flags_the_known_seed_example():
    """Sanity: detector THUC SU flag vi du goc DEBT-037 (khong phai detector rong)."""
    flagged = find_greponly_wiring_guards()
    assert ("test_gate_wired_g2.py",
            "test_character_gate_reachable_via_wrapper") in flagged, (
        "detector khong con bat duoc guard grep-only con lai (g2 character gate, chua fix "
        "behavioral) — detector co the da bi hong/qua long")
