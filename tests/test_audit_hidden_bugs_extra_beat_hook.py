"""Test extra_beat_HOOK awareness trong tools/audit_hidden_bugs.py (DEBT-032 v2, 2026-07-12).

Boi canh (governance/proposals/bible03_driver_memory_arc_proposal.yaml APPROVED_A +
bible/21_series_arc_design.yaml#extra_beat_HOOK + bible/00_constitution.yaml#R42):
9 tap (EP12/15/20/25/30/35/40/45/50) co bac tai noi THEM 1 "cau thu ba" hop le o vi
tri HOOK (section 1, truoc khi don khach) — KHAC voi beat_3 CLIFFHANGER baseline (da
duoc R42/R55 cong nhan tu 27/6 cho CA 40/40 tap co tag). Truoc fix nay,
tools/audit_hidden_bugs.py check [3] gop CHUNG moi quote "thua" cua bac tai vao 1
nguong ">1 = bug" — khong phan biet vi tri HOOK (hop le) voi CLIFFHANGER/REVEAL
(baseline). Fix them 2 ham thuan (split_driver_extra_quotes / driver_extra_overuse_flag)
tach quote theo vi tri van ban, CHI nang nguong cho 9 tap da field-hoa, giu NGUYEN
hanh vi cu cho 41 tap con lai (regression-safe).

LUU Y (bao cao trung thuc, R_SUPREME PASS declaration must qualify): tren du lieu
THAT (output/ep_12/15/25/35/45), fix nay KHONG lam giam so EP bi flag trong
tools/audit_hidden_bugs.py (van 37 EP nhu truoc) — vi 1 loi rieng, DA CO TU TRUOC
(regex DRIVER_QUOTE_PATTERN dung `[^"]*?` sau tu khoa "lieic guong"/"noi" ma KHONG
co quote ngay sau no tren cung dong/doan van co the "nhay" toi quote GAN NHAT phia
sau trong toan van ban, kể ca khi do la loi thoai HANH KHACH chu khong phai bac tai
— vd EP15/25/35/45 deu bat nham 1 quote "Toi..." cua hanh khach). Loi nay la NGUYEN
NHAN RIENG, KHONG lien quan extra_beat_HOOK, da duoc ghi vao governance/TECH_DEBT.md
(DEBT-036) — KHONG sua trong task nay vi sua se doi ket qua ca 41 tap khac, vuot
pham vi proposal da duyet (R211 — can R7 proposal rieng). Vi vay test o day dung
FIXTURE TONG HOP (khong doc output/ep_*/episode.md that) de chung minh CO CHE
extra_beat_HOOK hoat dong dung doc lap voi loi regex kia — dung "mutation-proof":
lat co (ep_num co/khong trong EXTRA_BEAT_HOOK_EPS) tren CUNG 1 van ban va xac nhan
should_flag lat theo.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import audit_hidden_bugs as ahb  # noqa: E402
from milestones import EXTRA_BEAT_HOOK_EPS, LEGACY_AUDIT_EXEMPT_EPS  # noqa: E402


def _make_episode_body(hook_quotes, rest_quotes):
    """Fixture toi gian: 1 doan HOOK (co N quote bac tai truoc marker SETUP) + 1 doan
    sau SETUP (co M quote bac tai khac, mo phong CLIFFHANGER/REVEAL). Dung dung tu khoa
    + dinh dang ma DRIVER_QUOTE_PATTERN/HOOK_SECTION_END_PATTERN that su nhan dien
    (khop nguyen van "Bác tài ... cất lời/tiếp/liếc gương ... "quote""), KHONG bia
    pattern moi.
    """
    hook_lines = "\n\n".join(f'Bác tài tiếp:\n\n"{q}"' for q in hook_quotes)
    rest_lines = "\n\n".join(f'Bác tài liếc gương. "{q}"' for q in rest_quotes)
    return (
        "# HOOK [section 1]\n\n"
        "Khải Phong ngồi ghế thứ ba.\n\n"
        f"{hook_lines}\n\n"
        "Xe lăn bánh.\n\n"
        "# SETUP [section 2]\n\n"
        "Người đàn ông bước lên xe.\n\n"
        "# CLIFFHANGER [section 6]\n\n"
        f"{rest_lines}\n"
    )


# ---------------------------------------------------------------------------
# split_driver_extra_quotes — vi tri quote duoc phan loai dung HOOK vs rest
# ---------------------------------------------------------------------------

def test_split_hook_and_rest_quotes_by_position():
    body = _make_episode_body(
        hook_quotes=["Đêm nay sẽ có cậu trai khác."],
        rest_quotes=["Vào đêm mười lăm. Đừng vội."],
    )
    hook, rest = ahb.split_driver_extra_quotes(body)
    assert hook == ["Đêm nay sẽ có cậu trai khác."]
    assert rest == ["Vào đêm mười lăm. Đừng vội."]


def test_split_excludes_standard_lines_from_both_groups():
    body = _make_episode_body(
        hook_quotes=["Con đã nhớ ra chưa?", "1 câu thật sự extra."],
        rest_quotes=["Chưa tới lúc."],
    )
    hook, rest = ahb.split_driver_extra_quotes(body)
    assert hook == ["1 câu thật sự extra."]
    assert rest == []


# ---------------------------------------------------------------------------
# driver_extra_overuse_flag — MUTATION-PROOF: lat membership EXTRA_BEAT_HOOK_EPS
# tren CUNG 1 van ban, xac nhan ket qua flag lat theo dung thiet ke.
# ---------------------------------------------------------------------------

def test_hook_list_ep_with_2_hook_quotes_plus_1_baseline_not_flagged():
    """Dung mau thiet ke that (bible/21#extra_beat_HOOK): 2 doan quote HOOK (kieu
    'cất lời' + 'tiếp' — 1 beat chia 2 cau) + 1 quote CLIFFHANGER baseline. Truoc fix,
    tong 3 extra > 1 se bi flag SAI (day chinh la false-positive proposal da chi ra).
    Sau fix, EP nam trong EXTRA_BEAT_HOOK_EPS (vd EP15) KHONG bi flag vi rest chi co 1.
    """
    body = _make_episode_body(
        hook_quotes=[
            "Đêm mười một — con đã thấy cậu trai đem vòng cổ.",
            "Đêm nay sẽ có cậu trai khác — đem cho chính mình.",
        ],
        rest_quotes=["Vào đêm mười lăm. Đừng vội."],
    )
    ep_num = 15
    assert ep_num in EXTRA_BEAT_HOOK_EPS
    should_flag, count, _ = ahb.driver_extra_overuse_flag(ep_num, body)
    assert count == 3
    assert should_flag is False


def test_same_text_ep_not_in_hook_list_still_flagged():
    """MUTATION: cung 1 van ban y het test tren, CHI doi ep_num sang 1 tap KHONG nam
    trong EXTRA_BEAT_HOOK_EPS (vi du 16, khong milestone/legacy-exempt) — phai VAN bi
    flag dung nhu hanh vi code GOC truoc 2026-07-12 (khong am tham noi long cho EP
    ngoai danh sach da duyet).
    """
    body = _make_episode_body(
        hook_quotes=[
            "Đêm mười một — con đã thấy cậu trai đem vòng cổ.",
            "Đêm nay sẽ có cậu trai khác — đem cho chính mình.",
        ],
        rest_quotes=["Vào đêm mười lăm. Đừng vội."],
    )
    ep_num = 16
    assert ep_num not in EXTRA_BEAT_HOOK_EPS
    assert ep_num not in LEGACY_AUDIT_EXEMPT_EPS
    should_flag, count, _ = ahb.driver_extra_overuse_flag(ep_num, body)
    assert count == 3
    assert should_flag is True


def test_hook_list_ep_still_flagged_if_rest_has_2_extras():
    """Khong duoc am tham mien tru CA TAP — chi vung HOOK duoc noi long. Neu phan
    NGOAI HOOK (CLIFFHANGER/REVEAL) co >1 extra, EP trong EXTRA_BEAT_HOOK_EPS van
    phai bi flag (R55 cap goc CHUA doi cho vung nay).
    """
    body = _make_episode_body(
        hook_quotes=["Đêm nay sẽ có cậu trai khác."],
        rest_quotes=["Extra rest 1.", "Extra rest 2."],
    )
    ep_num = 25
    assert ep_num in EXTRA_BEAT_HOOK_EPS
    should_flag, count, _ = ahb.driver_extra_overuse_flag(ep_num, body)
    assert count == 3
    assert should_flag is True


def test_hook_list_ep_with_only_baseline_extra_not_flagged():
    """Truong hop khong co quote HOOK nao ca (vd EP12 thuc te — co che 'dem them'
    khong luon di kem quote duoc regex bat), chi co 1 baseline CLIFFHANGER — van
    KHONG flag (dung y het hanh vi cu, vi 1 <= 1)."""
    body = _make_episode_body(hook_quotes=[], rest_quotes=["Vào đêm mười hai. Đừng vội."])
    ep_num = 12
    assert ep_num in EXTRA_BEAT_HOOK_EPS
    should_flag, count, _ = ahb.driver_extra_overuse_flag(ep_num, body)
    assert count == 1
    assert should_flag is False


# ---------------------------------------------------------------------------
# Regression: EP NGOAI danh sach EXTRA_BEAT_HOOK_EPS phai cho ket qua Y HET
# ham/regex GOC (findall + threshold >1), chung minh KHONG doi hanh vi cho 41 tap
# con lai. Dung du lieu that (output/) cho vai tap dai dien de bat ky regression
# thuc te nao (khong chi fixture tong hop).
# ---------------------------------------------------------------------------

_LEGACY_PATTERN = re.compile(
    r'Bác tài[^\n.]*?(?:cất lời|nói|đáp|bảo|hỏi|tiếp|liếc gương)[^"]*?"([^"]+)"'
)
_STANDARD = {'Con đã nhớ ra chưa?', 'Chưa tới lúc.'}


def _legacy_should_flag(body):
    quotes = _LEGACY_PATTERN.findall(body)
    extras = [q for q in quotes if q.strip() not in _STANDARD]
    return len(extras) > 1, len(extras)


def test_real_episodes_outside_hook_list_match_legacy_behavior_exactly():
    svhmp_root = Path(__file__).resolve().parent.parent
    eps_dir = svhmp_root / "output"
    checked = 0
    for ep_num in [2, 7, 11, 13, 14]:  # tagged DEBT-030 EPs, KHONG trong EXTRA_BEAT_HOOK_EPS
        assert ep_num not in EXTRA_BEAT_HOOK_EPS
        if ep_num in LEGACY_AUDIT_EXEMPT_EPS:
            continue
        f = eps_dir / f"ep_{ep_num:02d}" / "episode.md"
        if not f.exists():
            continue
        body = ahb.strip_meta(f.read_text(encoding="utf-8"))
        legacy_flag, legacy_count = _legacy_should_flag(body)
        new_flag, new_count, _ = ahb.driver_extra_overuse_flag(ep_num, body)
        assert new_flag == legacy_flag, f"EP{ep_num}: flag lệch legacy"
        assert new_count == legacy_count, f"EP{ep_num}: count lệch legacy"
        checked += 1
    assert checked >= 3, "cần ít nhất 3 EP thật để test regression có ý nghĩa"
