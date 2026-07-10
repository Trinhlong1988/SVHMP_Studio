"""deep-audit (2/7) — guard chong lop bug tai dien 'built != wired'.

Bug class: mot gate/tool duoc VIET (built) nhung KHONG duoc goi tu diem thuc thi
(wired). Da tai dien >=3 lan: git hooks (F1), cap_peak (R198), va G2
CHARACTER_GATE (commit a171120 khai 'wire into render' nhung svhmp_v13_render.py
0 reference — verified). commit-msg guard chi bat 'R{N} codified', ci_gate khong
verify wiring -> claim prose sai lot vao git history + DoD.

Test nay bien lop do thanh loi CI-bat-duoc: render PATH (qua wrapper) PHAI tham
chieu character completeness gate.

CAP NHAT (audit doc lap G2-6, 2026-07): commit 8dbcecc tung chen CHARACTER_GATE
THANG vao giua main() cua file LOCKED tools/svhmp_v13_render.py — vi pham ro
TASK_G2_CHARACTER.md dong 32-33 ("KHONG sua svhmp_v13_render.py LOCKED — bat qua
flag/wrapper"). Da tach ra tools/render_with_character_gate.py (wrapper goi
svhmp_v13_render.py nhu subprocess, KHONG import/sua noi bo file LOCKED). Test
nay gio kiem 2 chieu: (1) wrapper PHAI co gate that; (2) file LOCKED PHAI SACH
(khong con code CHARACTER_GATE) — dam bao khong tai dien vi pham cu.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
RENDER = REPO / "tools" / "svhmp_v13_render.py"
WRAPPER = REPO / "tools" / "render_with_character_gate.py"

# cac hinh thuc wire hop le: subprocess preflight, in-proc completeness, ...
WIRE_MARKERS = (
    "preflight",
    "render_gate",
    "episode_completeness",
    "character_manager",
    "CHARACTER_GATE",
    "completeness(",
)


def test_character_gate_reachable_via_wrapper():
    assert WRAPPER.exists(), "tools/render_with_character_gate.py missing"
    txt = WRAPPER.read_text(encoding="utf-8")
    hits = [m for m in WIRE_MARKERS if m in txt]
    assert hits, (
        "render_with_character_gate.py KHONG tham chieu character completeness "
        "gate (built != wired)."
    )
    assert "svhmp_v13_render.py" in txt, (
        "wrapper phai goi svhmp_v13_render.py (subprocess) sau khi qua gate"
    )


def test_run_character_gate_blocks_on_real_low_completeness_strict():
    """G2-1 (10/7, per Mr.Long authorization, TASK_AUDIT_HIGH_G2_G8.md): test hanh vi
    THAT (khong chi text-grep) - goi truc tiep run_character_gate() voi du lieu THAT
    (ep_02, roster completeness ~23%, duoi threshold 0.5 mac dinh) - PHAI tra False
    (BLOCK) khi strict=True. Neu ai doi 'return False' -> 'return True' trong ham,
    test nay se bat duoc (khac 2 test cu chi grep text, khong goi ham)."""
    from render_with_character_gate import run_character_gate
    result = run_character_gate("dummy_spec.json", ep_num=2, strict=True, threshold=0.5)
    assert result is False, (
        "run_character_gate(strict=True) tren du lieu THAT completeness thap phai BLOCK "
        "(False) - neu tra True, guard bi vo hieu hoa (finding G2-1)")


def test_run_character_gate_warns_not_blocks_when_not_strict():
    """Doi xung: cung du lieu THAT nhung strict=False (WARN-default hien tai) PHAI
    van cho phep tiep tuc (True) - khong doi hanh vi WARN-default da duyet (GOV-2)."""
    from render_with_character_gate import run_character_gate
    result = run_character_gate("dummy_spec.json", ep_num=2, strict=False, threshold=0.5)
    assert result is True, "WARN-default (strict=False) khong duoc BLOCK render"


def test_main_exits_2_on_strict_block_real_data(monkeypatch, capsys):
    """G2-1: main() voi --strict-characters + spec tro ep co completeness thap PHAI
    sys.exit(2) TRUOC KHI goi subprocess render (khong render duoc du lieu chua sach)."""
    import sys as _sys
    from render_with_character_gate import main
    monkeypatch.setattr(_sys, "argv", [
        "render_with_character_gate.py",
        "--spec", "dummy_spec.json",
        "--output", "output/ep_02/hook.wav",
        "--strict-characters",
    ])
    with __import__("pytest").raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2, (
        "main() voi --strict-characters tren ep completeness thap phai exit(2) - "
        f"thuc te exit({exc_info.value.code})")


def test_locked_render_file_has_no_character_gate_code():
    """Doi xung voi test tren: file LOCKED KHONG duoc tu y chen lai
    CHARACTER_GATE (commit 8dbcecc cu, da go). Vi pham TASK_G2_CHARACTER.md
    dong 32-33 neu tai dien."""
    assert RENDER.exists(), "svhmp_v13_render.py missing"
    txt = RENDER.read_text(encoding="utf-8")
    assert "CHARACTER_GATE" not in txt, (
        "svhmp_v13_render.py (LOCKED) lai chua code CHARACTER_GATE — phai o "
        "wrapper rieng (tools/render_with_character_gate.py), khong duoc sua "
        "file LOCKED nay (TASK_G2_CHARACTER.md dong 32-33)."
    )
    assert "strict-characters" not in txt and "strict_characters" not in txt, (
        "svhmp_v13_render.py (LOCKED) khong duoc co flag --strict-characters — "
        "flag nay thuoc wrapper."
    )
