"""
R216 (17/7) — mutation-proof test cho tools/cross_episode_canon_check.py.
Khoa nguyen tac "tap sinh truoc = ground truth": phat hien tap sau mau thuan tap
truoc ve 1 canon-fact, neo tap SOM NHAT lam anchor (KHONG tin so dong).

Muc tieu mutation-proof (R215.5/R215.6 — gate that su enforce, khong phai no-op):
  1. evaluate() phan biet TRACKED (allowlist DEBT-035) vs FAIL (divergence moi).
  2. Chung minh ALLOWLIST LOAD-BEARING: go key khoi allowlist -> divergence that
     (ghe EP01 vs EP02-50) FLIP sang FAIL. Neu allowlist la no-op, test nay fail.
  3. Anchor = tap SOM NHAT, khong phai so dong.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import cross_episode_canon_check as cec  # noqa: E402


# ---------- extractor ----------
def test_extract_seat_basic_and_classifier():
    assert cec.extract_kp_seat("Khải Phong ngồi ghế thứ ba, tay khoanh.") == "3"
    assert cec.extract_kp_seat("Khải-Phong đang ngồi trên chiếc ghế số bảy của xe.") == "7"
    assert cec.extract_kp_seat("Không ai nhắc tới chỗ ngồi ở đây.") is None


def test_extract_havy_death_place_ny_vs_hn_vs_none():
    ny = ("Cô ấy mất tám năm trước. Hạ-Vy được học bổng du học Hoa Kỳ, "
          "xuống sân bay Kennedy ở New York rồi bắt taxi.")
    hn = ("Hạ Vy mất trong tai nạn xe máy đêm ấy, tại ngã tư phố Huế - "
          "Hai Bà Trưng, đưa vào bệnh viện Bạch Mai.")
    assert cec.extract_havy_death_place(ny) == "NY"
    assert cec.extract_havy_death_place(hn) == "HN"
    # nhac Ha Noi nhung KHONG phai noi chet (boi canh xe chay) -> None
    assert cec.extract_havy_death_place("Chuyến xe khởi hành từ Hà Nội lúc nửa đêm.") is None
    # khong nhac cai chet -> None
    assert cec.extract_havy_death_place("Hạ Vy cười, đứng ở cổng trường.") is None


# ---------- find_divergence: anchor = earliest ----------
def test_no_divergence_when_all_same():
    fm = {1: ("3", "a"), 2: ("3", "b"), 3: ("3", "c")}
    assert cec.find_divergence(fm) is None


def test_divergence_anchors_on_earliest_not_majority():
    fm = {1: ("7", "a")}
    for ep in range(2, 49):
        fm[ep] = ("3", "b")
    d = cec.find_divergence(fm)
    assert d is not None
    assert d["anchor_ep"] == 1 and d["anchor_val"] == "7", d
    assert 2 in d["diverging"] and 48 in d["diverging"] and 1 not in d["diverging"]


# ---------- evaluate(): ratchet TRACKED vs FAIL (mutation-proof, pure) ----------
_DIVERG = {"anchor_ep": 1, "anchor_val": "7",
           "values": {"7": [1], "3": [2, 3]}, "diverging": [2, 3]}


def test_evaluate_divergence_in_allowlist_is_tracked_not_fail():
    fail, lines = cec.evaluate([("kp_seat", "ghế", _DIVERG)], allowlist={"kp_seat"})
    assert fail == 0
    assert lines[0][0] == "TRACKED"


def test_evaluate_same_divergence_NOT_in_allowlist_fails():
    # MUTATION: cung divergence do nhung allowlist rong -> PHAI FAIL. Chung minh
    # allowlist la thu giu gate xanh, KHONG phai gate mu luon-pass.
    fail, lines = cec.evaluate([("kp_seat", "ghế", _DIVERG)], allowlist=set())
    assert fail == 1
    assert lines[0][0] == "FAIL"


def test_evaluate_clean_fact_passes():
    fail, lines = cec.evaluate([("kp_seat", "ghế", None)], allowlist=set())
    assert fail == 0
    assert lines[0][0] == "OK"


def test_evaluate_new_divergence_fails_even_when_another_allowlisted():
    results = [("kp_seat", "ghế", _DIVERG),          # allowlisted -> tracked
               ("other_fact", "khác", _DIVERG)]        # KHONG allowlist -> fail
    fail, lines = cec.evaluate(results, allowlist={"kp_seat"})
    assert fail == 1
    statuses = {k: s for s, k, *_ in lines}
    assert statuses["kp_seat"] == "TRACKED" and statuses["other_fact"] == "FAIL"


# ---------- integration tren repo THAT ----------
def test_real_repo_seat_detected_and_tracked():
    """Repo that: EP01 ghe 7 vs EP02+ ghe 3 -> run_all() PHAI thay phan ky ghe
    va xep TRACKED (trong allowlist), fail=0. Chung minh gate CHAY tren du lieu that
    (khong mu), dong thoi ratchet dung."""
    fail, lines = cec.run_all()
    seat = next((ln for ln in lines if ln[1] == "kp_seat"), None)
    assert seat is not None
    if seat[3] is None:
        # da reconcile xong (khong con phan ky) -> chap nhan, khong ep phai co divergence
        return
    assert seat[0] == "TRACKED", f"ghe dang reconcile phai TRACKED, duoc: {seat[0]}"
    assert seat[3]["anchor_ep"] == 1 and seat[3]["anchor_val"] == "7"
    assert fail == 0


def test_real_repo_removing_seat_from_allowlist_flips_to_fail():
    """MUTATION-PROOF quan trong nhat: neu go 'kp_seat' khoi allowlist va van con
    phan ky that -> run_all PHAI fail>=1. Neu test nay pass ma khong fail, nghia la
    hoac da reconcile xong (OK), hoac gate mu. Ta phan biet 2 truong hop."""
    fail_track, lines = cec.run_all()          # voi allowlist that
    seat = next((ln for ln in lines if ln[1] == "kp_seat"), None)
    if seat is None or seat[3] is None:
        return  # da reconcile xong -> khong con gi de mutate
    # con phan ky that -> go allowlist -> PHAI fail
    fail_no_allow, _ = cec.run_all(allowlist=set())
    assert fail_no_allow >= 1, "go allowlist ma van khong fail => gate MU (no-op)"
