"""R117 — Fact Database check.
Verify episode text vs bible/27_fact_db.yaml. KHÔNG cho phép drift fact.
"""
import re
import sys
import yaml
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
EPISODE = BASE / "output/ep_01/episode.md"
FACT_DB = BASE / "bible/27_fact_db.yaml"


def cut_metadata(text):
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    for marker in ("# SELF-CHECK", "# NOTES", "## SOUL", "## REVIEW", "## NARRATION", "## EMOTION"):
        idx = text.find(marker)
        if idx >= 0:
            text = text[:idx]
    return text


def check_facts(text, facts):
    """Verify key facts present + no contradiction."""
    violations = []

    # 1. Đồng hồ stopped at 7:10
    if "bảy giờ mười phút" not in text and "7:10" not in text:
        violations.append("FACT: 'bảy giờ mười phút' KHÔNG xuất hiện trong text (đồng hồ stopped time)")

    # 2. 8 năm
    if "tám năm" not in text and "8 năm" not in text:
        violations.append("FACT: 'tám năm' KHÔNG xuất hiện (Khải-Phong giữ đồng hồ 8 năm)")

    # 3. Cầu Long Biên
    if "Cầu Long Biên" not in text:
        violations.append("FACT: 'Cầu Long Biên' KHÔNG xuất hiện (destination)")

    # 4. Sân bay Kennedy
    if "Kennedy" not in text and "kennedy" not in text:
        violations.append("FACT: 'Kennedy' KHÔNG xuất hiện (Hạ-Vy arrival)")

    # 5. Bác tài 2 dialogue
    bac_tai_q = text.count("Con đã nhớ ra chưa?")
    if bac_tai_q < 1:
        violations.append(f"FACT: 'Con đã nhớ ra chưa?' = {bac_tai_q} (Bác tài line missing)")
    chua_toi_luc = "Chưa tới lúc đâu cháu" in text
    if not chua_toi_luc:
        violations.append("FACT: 'Chưa tới lúc đâu cháu' KHÔNG xuất hiện (Bác tài line 2)")

    # 6. Character description sync — Hạ-Vy áo gió xanh nhạt
    if "xanh nhạt" not in text:
        violations.append("FACT: 'xanh nhạt' KHÔNG xuất hiện (Hạ-Vy appearance — L316 + L414 sync required)")

    # 7. Contradict check — Khải-Phong KHÔNG cầm đồng hồ sau khi rơi
    if "tay vẫn ôm chiếc đồng hồ" in text:
        violations.append("CONTRADICT: 'tay vẫn ôm chiếc đồng hồ' sau khi đồng hồ đã rơi (L444)")

    # 8. Forbidden phrases
    forbidden = ["Hắc Vỹ Dạ", "ghế thứ bảy", "ghế thứ ba"]
    for f in forbidden:
        if f in text:
            violations.append(f"FORBIDDEN: '{f}' phải REMOVE")

    # 9. Brand consistency
    brand_count = text.count("Hắc Dạ Ký") + text.count("Hắc, Dạ, Ký")
    if brand_count < 4:
        violations.append(f"BRAND: 'Hắc Dạ Ký' appearances = {brand_count} (cần ≥4 cho INTRO+OUTTRO)")

    return violations


def main():
    text = EPISODE.read_text(encoding="utf-8")
    text_clean = cut_metadata(text)
    facts = yaml.safe_load(FACT_DB.read_text(encoding="utf-8"))

    print("=== R117 FACT DATABASE CHECK ===\n")
    violations = check_facts(text_clean, facts)
    for v in violations:
        print(f"  ⚠️ {v}")

    fail = len(violations) > 0
    print(f"\n== R117 GATE: {'FAIL - FIX REQUIRED' if fail else 'PASS'} ==")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
