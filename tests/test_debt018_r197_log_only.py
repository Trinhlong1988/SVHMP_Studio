"""DEBT-018 R197 giai doan 1 (11/7, per Mr.Long authorization) — wire svhmp_preflight_
qa.py vao tools/svhmp_v13_render.py o che do LOG-ONLY (tuyet doi KHONG chan render o
giai doan nay, cho Mr.Long xem bao cao roi moi quyet giai doan 2 - CHAN THAT).

svhmp_v13_render.py can torch/TTS stack de chay that main() -> khong the goi end-to-end
trong pytest (mirror ly do QA-logic functions duoc tach rieng, xem docstring dau file
do). Test o day kiem tren SOURCE TEXT (mirror pattern _run_all_body_ok/_pause_delegation_
body_ok da dung nhieu lan trong session nay: pure check + mutation-proof).

TASK_G2_CHARACTER.md dong 32-33: "KHONG sua svhmp_v13_render.py LOCKED — bat qua flag/
wrapper" — ap dung rieng cho CHARACTER_GATE flag logic (da fix truoc, xem test_gate_
wired_g2.py::test_locked_render_file_has_no_character_gate_code). Doan LOG-ONLY nay
mirror pattern R90 STAGE 1 da co san trong CHINH file nay (subprocess QA call in-line,
khong flag/state moi, khong doi hanh vi block hien co) - KHAC ban chat voi vi pham cu.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RENDER = REPO / "tools" / "svhmp_v13_render.py"
PREFLIGHT = REPO / "tools" / "svhmp_preflight_qa.py"

_BLOCK_RE = re.compile(r"# DEBT-018 R197 GIAI DOAN 1.*?(?=\n    # Round 14 hook)", re.DOTALL)


def _log_only_block_ok(src):
    """Pure check tren source text: khoi R197-LOG-ONLY PHAI (1) goi subprocess toi
    svhmp_preflight_qa.py voi args.spec, (2) KHONG chua sys.exit ben trong khoi do
    (LOG-ONLY tuyet doi khong duoc chan giai doan nay)."""
    m = _BLOCK_RE.search(src)
    if not m:
        return False, "khong tim thay khoi R197-LOG-ONLY (bi go khoi svhmp_v13_render.py?)"
    block = m.group(0)
    if "svhmp_preflight_qa.py" not in block:
        return False, "khoi khong goi svhmp_preflight_qa.py"
    if "args.spec" not in block:
        return False, "khoi khong truyen args.spec cho preflight (sai input)"
    if "sys.exit" in block:
        return False, "khoi R197-LOG-ONLY co sys.exit - VI PHAM 'khong chan render' giai doan 1"
    return True, "khoi R197-LOG-ONLY: goi preflight voi args.spec, khong sys.exit"


def test_r197_log_only_block_present_and_safe_on_real_source():
    src = RENDER.read_text(encoding="utf-8")
    ok, detail = _log_only_block_ok(src)
    assert ok, detail


def test_r197_log_only_block_does_not_reintroduce_character_gate_string():
    """Guard doi voi chinh minh: khoi moi KHONG duoc chua chuoi 'CHARACTER_GATE'
    (tranh trung lai chinh loi da fix truoc khi commit - mirror test_gate_wired_g2.py
    ::test_locked_render_file_has_no_character_gate_code, KHONG lam vo guard do)."""
    src = RENDER.read_text(encoding="utf-8")
    m = _BLOCK_RE.search(src)
    assert m, "khong tim thay khoi R197-LOG-ONLY"
    assert "CHARACTER_GATE" not in m.group(0)
    assert "strict-characters" not in m.group(0) and "strict_characters" not in m.group(0)


def test_mutation_removing_preflight_call_is_detected():
    src = RENDER.read_text(encoding="utf-8")
    mutated = src.replace(
        '[sys.executable, os.path.join(_tools_dir, "svhmp_preflight_qa.py"), args.spec],',
        '[sys.executable, "-c", "pass"],', 1)
    assert mutated != src, "chuoi can mutate khong ton tai - kiem tra lai source that"
    ok, detail = _log_only_block_ok(mutated)
    assert not ok, "mutation go loi goi preflight khong bi bat"


def test_mutation_adding_sys_exit_is_detected():
    """MUTATION-PROOF quan trong nhat: neu ai vo tinh/co y them sys.exit vao khoi
    LOG-ONLY (bien no thanh chan that som trai voi giai doan 1 da duyet), test PHAI
    bat duoc."""
    src = RENDER.read_text(encoding="utf-8")
    marker = 'print(f"[v13] [R197-LOG-ONLY] preflight_qa exit='
    assert marker in src, "marker can mutate khong ton tai - kiem tra lai source that"
    mutated = src.replace(marker, "sys.exit(3)  # MUTATION\n        " + marker, 1)
    ok, detail = _log_only_block_ok(mutated)
    assert not ok, "mutation them sys.exit vao khoi LOG-ONLY khong bi bat"


def test_r90_stage1_hardlock_still_present_unchanged():
    """Regression: R90 STAGE 1 (gate THAT, van chan nhu cu) KHONG duoc bi doan
    LOG-ONLY moi lam vo hieu/xoa mat."""
    src = RENDER.read_text(encoding="utf-8")
    assert "R90 HARDLOCK" in src and "R90 STAGE 1 pre-render gate" in src
    assert 'sys.exit(2)' in src, "R90 STAGE 1 phai con nguyen kha nang chan that (exit 2)"


def test_preflight_tool_accepts_spec_path_directly():
    """Reality anchor: svhmp_preflight_qa.py PHAI ton tai va nhan spec path lam
    argv[1] (khop dung cach svhmp_v13_render.py goi no qua args.spec)."""
    assert PREFLIGHT.exists()
    src = PREFLIGHT.read_text(encoding="utf-8")
    assert "sys.argv[1]" in src
