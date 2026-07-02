"""deep-audit (2/7) — guard chong lop bug tai dien 'built != wired'.

Bug class: mot gate/tool duoc VIET (built) nhung KHONG duoc goi tu diem thuc thi
(wired). Da tai dien >=3 lan: git hooks (F1), cap_peak (R198), va G2
CHARACTER_GATE (commit a171120 khai 'wire into render' nhung svhmp_v13_render.py
0 reference — verified). commit-msg guard chi bat 'R{N} codified', ci_gate khong
verify wiring -> claim prose sai lot vao git history + DoD.

Test nay bien lop do thanh loi CI-bat-duoc: render entrypoint PHAI tham chieu
character completeness gate.

Trang thai: GUARD SONG (2026-07-02). Gate da wire that vao svhmp_v13_render.py
(CHARACTER_GATE, WARN-default + --strict-characters). xfail marker DA GO -> test
nay gio BLOCK neu ai un-wire gate khoi render.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RENDER = REPO / "tools" / "svhmp_v13_render.py"

# cac hinh thuc wire hop le: subprocess preflight, in-proc completeness, ...
WIRE_MARKERS = (
    "preflight",
    "render_gate",
    "episode_completeness",
    "character_manager",
    "CHARACTER_GATE",
    "completeness(",
)


def test_character_gate_reachable_from_render():
    assert RENDER.exists(), "svhmp_v13_render.py missing"
    txt = RENDER.read_text(encoding="utf-8")
    hits = [m for m in WIRE_MARKERS if m in txt]
    assert hits, (
        "svhmp_v13_render.py KHONG tham chieu character completeness gate "
        "(built != wired). Wire gate vao render roi go xfail o test nay."
    )
