"""R141 — SSOT Diff Check.

Compare episode.md current state vs bible/27_fact_db.yaml (Single Source of Truth).
Flag ANY fact drift detected.

Logic:
  - For each fact in fact_db, scan episode for consistency
  - Names / numbers / locations / dialogue lines must match
  - Color descriptions (Hạ-Vy = áo gió xanh nhạt) must NOT drift
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


def diff_facts(text, facts):
    drifts = []

    # 1. Bác tài 2 dialogue exact lines
    expected_dialogues = facts["characters"]["Bác_tài"]["dialogue_lines"]
    for line in expected_dialogues:
        clean = line.lstrip("— ").rstrip()
        # Allow flexible match
        if clean not in text:
            drifts.append(f"DIALOGUE DRIFT: Bác tài expected '{clean}' KHÔNG có trong episode")

    # 2. Đồng hồ stopped time
    stopped = facts["objects"]["Đồng_hồ_nữ_xà_cừ"]["stopped_at"]
    if "bảy giờ mười phút" not in text:
        drifts.append(f"FACT DRIFT: '{stopped}' (đồng hồ stopped) missing")

    # 3. Khải-Phong holding duration — accept "8 năm" OR "tám năm"
    duration = facts["characters"]["Khải-Phong"]["duration_holding"]
    duration_alt = duration.replace("8", "tám").replace("năm", "năm")
    if duration not in text and duration_alt not in text and "tám năm" not in text:
        drifts.append(f"FACT DRIFT: '{duration}'/'tám năm' (Khải-Phong holds) missing")

    # 4. Hạ-Vy school
    school = facts["characters"]["Hạ-Vy"]["school"]
    if "lớp 11" not in text and "lớp mười một" not in text:
        drifts.append(f"FACT DRIFT: 'lớp 11/mười một' (Hạ-Vy school) missing")

    # 5. Hạ-Vy airport arrival
    arrival = facts["characters"]["Hạ-Vy"]["arrival_airport"]
    if "Kennedy" not in text:
        drifts.append(f"FACT DRIFT: '{arrival}' (Hạ-Vy arrival airport) missing")

    # 6. Character color consistency — Hạ-Vy áo gió xanh nhạt
    hv_appearance = facts["characters"]["Hạ-Vy"]["appearance_as_ghost"]
    if "xanh nhạt" not in text:
        drifts.append(f"COLOR DRIFT: Hạ-Vy expected áo gió xanh nhạt, missing in text")

    # 7. Cô gái CLIFFHANGER distinct color
    new_passenger_color = facts["characters"]["Cô_gái_ghế_bảy_mới_CLIFFHANGER"]["appearance"]
    if "xanh dương trong sáng" not in text and "xanh dương sáng" not in text and "xanh dương tinh khôi" not in text:
        drifts.append(f"COLOR DRIFT: Cô gái CLIFF expected '{new_passenger_color}', missing")

    # 8. Location facts
    if "Cầu Long Biên" not in text:
        drifts.append("LOCATION DRIFT: 'Cầu Long Biên' missing")
    if "Hà Nội" not in text:
        drifts.append("LOCATION DRIFT: 'Hà Nội' missing")

    # 9. Forbidden — Khải-Phong holding sau khi rơi
    if "tay vẫn ôm chiếc đồng hồ" in text:
        drifts.append("CONTRADICT: Khải-Phong 'tay vẫn ôm chiếc đồng hồ' sau khi đồng hồ đã rơi (immutable rule)")

    # 10. Bus state CLIFFHANGER: KHÔNG dừng
    if "Không một lần xe dừng" not in text:
        drifts.append("SCENE PHYSICS: 'Không một lần xe dừng' (CLIFFHANGER explanation) missing")

    # 11. BRAND drift — forbidden "Hắc Vỹ Dạ" / "Hắc, Vỹ, Dạ" (sai brand)
    forbidden_brand = ["Hắc Vỹ Dạ", "Hắc, Vỹ, Dạ"]
    for fb in forbidden_brand:
        if fb in text:
            drifts.append(f"BRAND DRIFT: forbidden '{fb}' present (correct: Hắc Dạ Ký)")

    return drifts


def main():
    text = EPISODE.read_text(encoding="utf-8")
    text_clean = cut_metadata(text)
    facts = yaml.safe_load(FACT_DB.read_text(encoding="utf-8"))

    print("=== R141 SSOT DIFF CHECK (episode vs fact_db) ===\n")
    drifts = diff_facts(text_clean, facts)
    for d in drifts:
        print(f"  ⚠️ {d}")
    if not drifts:
        print("  ✓ NO fact drift detected")

    fail = len(drifts) > 0
    print(f"\n== R141 GATE: {'FAIL - FIX REQUIRED' if fail else 'PASS'} ==")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
