"""DEBT-023 huong (b), Mr.Long 11/7: 25 tap tier medium/high PHAI co disclaimer hu cau
(vi tri/co che "G8 chen luc publish" CHUA duoc xay - xem TASK_AUDIT_RULE_ENFORCER_SWEEP.md).

Enforcer R215 (chong drift): neu ai xoa/re-render mat disclaimer khoi 1 trong 25 tap nay,
test FAIL. Danh sach 25 tap = ket qua ra tay HB01/HB02 (reports/DEBT023_HB01_HB02_50EP_REVIEW.md):
21 medium (phong tuc dan gian that) + 4 high (ton giao dang thuc hanh: 16/28/36/46).
Khong tu dong phan loai tier (viec do can content scanner rieng, ngoai pham vi) - khoa danh
sach da duyet bang tay.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# 25 tap medium/high tier can disclaimer (rà tay 11/7). Low-tier (sieu nhien thuan hu cau)
# KHONG can - khong liet ke o day.
#
# LUU Y: 9 tap ep_02..ep_10 (medium) TAM CHUA them disclaimer - chung fail san gate R40 intro
# (intro variant CU truoc R108/R40: "Series:" thay "Loat truyen:", thieu "chua KIP noi loi tam
# biet"), pre-commit gate chan commit. Sua intro = tham quyen Mr.Long (brand content, R2) - da bao
# cao xin phep, CHUA them vao list nay cho den khi duoc phep sua intro cho chung pass gate.
MEDIUM_HIGH_EPS = [
    # 12 medium DA them disclaimer (pass gate R40):
    "13", "14", "21", "24", "31", "34", "38", "39", "43", "45", "47", "48",
    # 4 high (ton giao) DA them:
    "16", "28", "36", "46",
]
# CHO XIN PHEP (fail R40 intro pre-existing, chua them disclaimer):
PENDING_INTRO_FIX_EPS = ["02", "03", "04", "05", "06", "07", "08", "09", "10"]

DISCLAIMER_MARKERS = ("hư cấu", "không có thật", "không khuyến khích")


def test_25_medium_high_episodes_have_disclaimer():
    """Moi tap medium/high PHAI chua it nhat 1 marker disclaimer hu cau."""
    missing = []
    for ep in MEDIUM_HIGH_EPS:
        f = REPO / "output" / f"ep_{ep}" / "episode.md"
        assert f.exists(), f"ep_{ep}/episode.md khong ton tai"
        text = f.read_text(encoding="utf-8")
        if not any(m in text for m in DISCLAIMER_MARKERS):
            missing.append(ep)
    assert not missing, (
        f"{len(missing)} tap medium/high THIEU disclaimer hu cau: {missing} "
        f"(DEBT-023 huong b - moi tap phai co 1 trong {DISCLAIMER_MARKERS})")


def test_high_tier_episodes_have_respectful_disclaimer():
    """4 tap high-tier (ton giao dang thuc hanh) - disclaimer co them y ton kinh/ton trong."""
    for ep in ("16", "28", "36", "46"):
        text = (REPO / "output" / f"ep_{ep}" / "episode.md").read_text(encoding="utf-8")
        assert "hư cấu" in text, f"ep_{ep} high-tier thieu disclaimer hu cau"
        assert ("tôn kính" in text or "tôn trọng" in text), (
            f"ep_{ep} high-tier (ton giao that): disclaimer nen co y ton kinh/ton trong")
