# -*- coding: utf-8 -*-
"""Mutation-proof test cho tools/canon_consistency_check.py (DEBT-035, R215).

BEHAVIORAL — không grep-thuần: mỗi test gọi thẳng find_canon_violations() và
kiểm tra HÀNH VI (số finding đổi theo mutation), không chỉ token tồn tại.

Bug gốc (đã lọt EP01): mô tả cái chết Hạ Vy bằng khung New York/Kennedy/taxi/cao tốc.
Canon (bible/21): Hạ Vy mất 12/4/2018, Hà Nội, tai nạn XE MÁY.
"""
import sys
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
if str(SVHMP) not in sys.path:
    sys.path.insert(0, str(SVHMP))

from tools.canon_consistency_check import find_canon_violations, scan_file  # noqa: E402

# --- Fixture "bản EP01 GỐC" (lỗi): Hạ Vy chết ở New York / taxi ---
FIXTURE_BUG = (
    "— Cô ấy là bạn lớp tôi hồi cấp ba. Tên cô ấy là Hạ-Vy.\n"
    "— Máy bay hạ cánh êm xuôi, cô ấy xuống sân bay Kennedy ở New York rồi bắt "
    "taxi về nhà người dì.\n"
    "— Taxi gặp xe tải. Trên đường cao tốc.\n"
    "— cô ấy đã mất ngay tại nơi đó rồi.\n"
    "— Kim dừng đúng giờ Hạ-Vy mất.\n"
)

# --- Fixture "bản đã SỬA" (sạch): Hà Nội / xe máy ---
FIXTURE_CLEAN = (
    "— Cô ấy là bạn lớp tôi hồi cấp ba. Tên cô ấy là Hạ-Vy.\n"
    "— Đêm qua trên đường về nhà, tới một ngã tư, cô ấy đi xe máy giữa cơn mưa.\n"
    "— Một chiếc xe tải vượt đến, đâm ngang qua.\n"
    "— cô ấy đã mất ngay tại nơi đó rồi.\n"
    "— Kim dừng đúng giờ Hạ-Vy mất.\n"
)

# --- Fixture HÀNH KHÁCH KHÁC đi nước ngoài (KHÔNG phải Hạ Vy) — chống false-positive ---
FIXTURE_OTHER_PASSENGER = (
    "Người khách bốn lăm tuổi. Em đỗ học bổng du học Hoa Kỳ năm hai mươi mốt.\n"
    "Em sang Hoa Kỳ, sống Texas hai mươi bốn năm. Bạn thân em là Hằng đã mất vì bệnh.\n"
)

# --- Fixture EP25-style: Hạ Vy chết ở Hà Nội, có 'taxi' đi bệnh viện (canon ĐÚNG) ---
FIXTURE_HANOI_TAXI = (
    "Anh ấy chạy ra đường — bắt taxi — đến bệnh viện Bạch Mai. Tới nơi — Hạ Vy "
    "đang trong phòng mổ.\n"
    "Hạ Vy mất ba tiếng sau, tai nạn xe máy ngã tư Hai Bà Trưng — Trần Hưng Đạo.\n"
)


def test_a_bug_fixture_flags():
    """(a) Hạ Vy + New York + taxi + mất  ->  PHẢI FLAG."""
    v = find_canon_violations(FIXTURE_BUG)
    assert len(v) >= 1, "bản GỐC lỗi phải bị FLAG"
    tokens = {f["token"] for f in v}
    assert "New York" in tokens and "Kennedy" in tokens
    # corroborating taxi/cao tốc phải được đính kèm
    assert any(f["corroborating"] for f in v)


def test_b_clean_fixture_passes():
    """(b) bản đã sửa Hà Nội/xe máy  ->  0 flag."""
    assert find_canon_violations(FIXTURE_CLEAN) == []


def test_c_other_passenger_no_flag():
    """(c) hành khách khác du học Hoa Kỳ (không phải Hạ Vy)  ->  0 flag."""
    assert find_canon_violations(FIXTURE_OTHER_PASSENGER) == []


def test_c2_hanoi_taxi_no_false_positive():
    """(c-bis) Hạ Vy chết Hà Nội, có 'taxi' đi BV (EP25)  ->  0 flag (chống FP)."""
    assert find_canon_violations(FIXTURE_HANOI_TAXI) == []


def test_d_reality_anchor_ep01_fixed():
    """(d) EP01 đã sửa trên disk  ->  0 flag (reality anchor, không cite quá khứ)."""
    for fname in ("episode.md", "episode_golden_text.md", "episode_tts_ready.md"):
        p = SVHMP / "output" / "ep_01" / fname
        if p.exists():
            assert scan_file(p) == [], f"EP01 {fname} vẫn còn canon contradiction"


# ---------------- MUTATION-PROOF: gỡ từng điều kiện -> finding phải biến mất ----------------
def test_mutation_remove_foreign_place_flips_pass():
    """Gỡ token nước-ngoài (New York/Kennedy) khỏi bản lỗi -> 0 flag (token load-bearing)."""
    mutated = FIXTURE_BUG.replace("Kennedy ở New York", "một ngã tư ở Hà Nội")
    assert find_canon_violations(mutated) == [], (
        "nếu vẫn FLAG sau khi gỡ token nước-ngoài => check không thực sự dựa token")


def test_mutation_remove_havy_flips_pass():
    """Gỡ mọi mention Hạ Vy -> 0 flag (điều kiện Hạ-Vy load-bearing)."""
    mutated = FIXTURE_BUG.replace("Hạ-Vy", "Cô ấy")
    assert find_canon_violations(mutated) == [], (
        "nếu vẫn FLAG sau khi gỡ Hạ Vy => check không scope theo Hạ Vy (sẽ FP hành khách khác)")


def test_mutation_remove_death_flips_pass():
    """Gỡ mọi từ-chết -> 0 flag (điều kiện ngữ-cảnh-chết load-bearing)."""
    mutated = (FIXTURE_BUG
               .replace("đã mất ngay tại nơi đó", "đã về tới nơi bình an")
               .replace("giờ Hạ-Vy mất", "giờ Hạ-Vy hẹn"))
    assert find_canon_violations(mutated) == [], (
        "nếu vẫn FLAG sau khi gỡ ngữ cảnh chết => check bắt token trần, sẽ FP")
