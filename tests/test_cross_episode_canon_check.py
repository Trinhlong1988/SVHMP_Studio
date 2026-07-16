"""
R216 (17/7) — mutation-proof test cho tools/cross_episode_canon_check.py.
Khoa nguyen tac "tap sinh truoc = ground truth": phat hien tap sau mau thuan tap
truoc ve 1 canon-fact, neo tap SOM NHAT lam anchor (KHONG tin so dong).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import cross_episode_canon_check as cec  # noqa: E402


def test_extract_seat_basic_and_classifier():
    assert cec.extract_kp_seat("Khải Phong ngồi ghế thứ ba, tay khoanh.") == "3"
    # bien the "chiec ghe" (loi false-negative cu) PHAI trich duoc
    assert cec.extract_kp_seat("Khải-Phong đang ngồi trên chiếc ghế số bảy của xe.") == "7"
    assert cec.extract_kp_seat("Không ai nhắc tới chỗ ngồi ở đây.") is None


def test_no_divergence_when_all_same():
    fm = {1: ("3", "a"), 2: ("3", "b"), 3: ("3", "c")}
    assert cec.find_divergence(fm) is None


def test_divergence_anchors_on_earliest_not_majority():
    # EP1='7' (som nhat, thieu so) ; EP2..48='3' (so dong) -> anchor PHAI la EP1='7'
    fm = {1: ("7", "a")}
    for ep in range(2, 49):
        fm[ep] = ("3", "b")
    d = cec.find_divergence(fm)
    assert d is not None
    assert d["anchor_ep"] == 1 and d["anchor_val"] == "7", d
    # 47 tap so dong '3' deu bi liet vao "diverging" (SAI so voi anchor)
    assert 2 in d["diverging"] and 48 in d["diverging"] and 1 not in d["diverging"]


def test_real_repo_flags_ep01_seat_divergence():
    """Repo that: EP01 ghe 7 vs EP02+ ghe 3 -> PHAI flag, anchor=EP01='7'."""
    fm = cec.collect_fact()
    if len(fm) < 2:
        return  # chua du du lieu
    d = cec.find_divergence(fm)
    assert d is not None, "phai phat hien phan ky ghe EP01-vs-con-lai"
    assert d["anchor_ep"] == min(fm), "anchor phai la tap som nhat"
    assert d["anchor_val"] == "7", f"EP01 (goc) = ghe 7 la ground truth, duoc: {d['anchor_val']}"


def test_mutation_if_all_conform_no_flag():
    """Mutation: neu MOI tap cung gia tri anchor -> khong con flag (chung minh gate
    that su do phan ky, khong phai luon FAIL)."""
    fm = {1: ("7", "a"), 2: ("7", "b"), 3: ("7", "c")}
    assert cec.find_divergence(fm) is None
