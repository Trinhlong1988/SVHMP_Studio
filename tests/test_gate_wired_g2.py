"""deep-audit (2/7) — guard chong lop bug tai dien 'built != wired'.

Bug class: mot gate/tool duoc VIET (built) nhung KHONG duoc goi tu diem thuc thi
(wired). Da tai dien >=3 lan: git hooks (F1), cap_peak (R198), va G2
CHARACTER_GATE (commit a171120 khai 'wire into render' nhung svhmp_v13_render.py
0 reference — verified). commit-msg guard chi bat 'R{N} codified', ci_gate khong
verify wiring -> claim prose sai lot vao git history + DoD.

Test nay bien lop do thanh loi CI-bat-duoc: render entrypoint PHAI tham chieu
character completeness gate.

Trang thai HIEN TAI: xfail(strict) vi a171120 chua wire that. Khi ai do wire
gate vao render (#2), test XPASS -> strict lat thanh FAIL -> BUOC go marker
xfail nay -> tu do thanh guard song (block neu ai un-wire lai).
"""
from pathlib import Path

import pytest

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


@pytest.mark.xfail(
    reason="G2 gate chua wire vao render (a171120: 0 reference) — XPASS khi #2 wire that thi go marker",
    strict=True,
)
def test_character_gate_reachable_from_render():
    assert RENDER.exists(), "svhmp_v13_render.py missing"
    txt = RENDER.read_text(encoding="utf-8")
    hits = [m for m in WIRE_MARKERS if m in txt]
    assert hits, (
        "svhmp_v13_render.py KHONG tham chieu character completeness gate "
        "(built != wired). Wire gate vao render roi go xfail o test nay."
    )
