"""Test R117 + R141 — Fact contradiction.

PASS: All facts present + correct
FAIL: Missing key fact (Cầu Long Biên)
EDGE: Synonym match ('tám năm' OK for '8 năm')
"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EPISODE = BASE / "output/ep_01/episode.md"
TOOL = BASE / "tools/qa_fact_check.py"
SSOT_TOOL = BASE / "tools/qa_ssot_diff.py"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # tests/
from _golden_lock import golden_lock  # DEBT-005 vong3: serialize ghi output/ep_01 THAT cross-process


def make_pass():
    return """# TEST PASS
Hắc Dạ Ký kể chuyện đêm.
Hắc Dạ Ký, những câu chuyện tâm linh.
Hắc Dạ Ký — chuyện kể từ cõi vô hình.
Hắc Dạ Ký xin hẹn gặp lại quý vị.
Khải-Phong giữ đồng hồ tám năm.
Đồng hồ dừng bảy giờ mười phút.
Hạ-Vy lớp 11 đi du học Hoa Kỳ tại Kennedy New York.
Cầu Long Biên đêm tháng tư Hà Nội.
— Con đã nhớ ra chưa?
— Chưa tới lúc đâu cháu ạ.
Hạ-Vy mặc áo gió xanh nhạt tóc cột cao.
Cô gái khoác áo gió xanh dương trong sáng.
Không một lần xe dừng.
"""


def make_fail_no_long_bien():
    return make_pass().replace("Cầu Long Biên", "cây cầu nào đó")


def make_edge_synonym():
    """Use '8 năm' instead of 'tám năm'."""
    return make_pass().replace("tám năm", "tám năm trời")


def run_tool(tool):
    result = subprocess.run(
        [sys.executable, str(tool)],
        capture_output=True, text=True, cwd=str(BASE),
        encoding="utf-8", errors="ignore", timeout=30,
    )
    return result.returncode, result.stdout


def run_case(name, text, tool, expect_fail):
    with golden_lock():
        orig = EPISODE.read_text(encoding="utf-8")
        EPISODE.write_text(text, encoding="utf-8")
        try:
            code, out = run_tool(tool)
            if expect_fail:
                assert code != 0 or "FAIL" in out, f"{name} should FAIL: {out[-300:]}"
                print(f"  ✅ {name}: caught")
            else:
                assert code == 0 or "PASS" in out, f"{name} should PASS: {out[-300:]}"
                print(f"  ✅ {name}: passed")
        finally:
            EPISODE.write_text(orig, encoding="utf-8")


if __name__ == "__main__":
    print("=== TEST R117 fact_check ===")
    run_case("PASS all facts", make_pass(), TOOL, expect_fail=False)
    run_case("FAIL missing Cầu Long Biên", make_fail_no_long_bien(), TOOL, expect_fail=True)
    print()
    print("=== TEST R141 SSOT diff ===")
    run_case("PASS all facts (SSOT)", make_pass(), SSOT_TOOL, expect_fail=False)
    run_case("FAIL missing Cầu Long Biên (SSOT)", make_fail_no_long_bien(), SSOT_TOOL, expect_fail=True)
    print("=== ALL 4 PASS ===")
