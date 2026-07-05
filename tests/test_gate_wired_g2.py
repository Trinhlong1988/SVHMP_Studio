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
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
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
