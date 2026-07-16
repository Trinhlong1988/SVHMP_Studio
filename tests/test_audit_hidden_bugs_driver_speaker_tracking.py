"""DEBT-036 — SPEAKER-TRACKING driver-quote attribution (Variant B, Mr.Long APPROVED 16/7).

Boi canh (governance/TECH_DEBT.md DEBT-036 + proposal debt036_proposal_withB.yaml):
tools/audit_hidden_bugs.py check[3] TRUOC 16/7 dung DRIVER_QUOTE_PATTERN
(`Bác tài[^\\n.]*?(?:...liếc gương)[^"]*?"([^"]+)"`) — phan `[^"]*?"` bang qua
newline/dau cham/section marker de "nhay" toi dau `"` GAN NHAT phia sau. Khi cau kich
hoat KHONG kem quote ngay sau (vd `Bác tài liếc gương. Không nói.`), regex nhay toi
quote HANH KHACH nhieu doan sau -> tinh nham la 1 "extra" cua bac tai (50/50 EP dinh).

Fix (DEBT-036): thay bang driver_quotes() speaker-tracking (adjacency) — moi quote
`"..."` gan cho speaker qua attribution GAN NHAT phia truoc (cung doan = inline, hoac
doan lien truoc). Do 3 chieu 50 EP (measure_debt036_variantB.py): 0 passenger-FP,
0 false-negative (cuu 5 loi foreshadow bac tai that EP11/12/21/30/50 ma Variant A
regex sot), flag check[3] = [12,14,16,17,18,35].

MUTATION-PROOF (R215.1): 9 case BEHAVIORAL (dung text that -> goi ham -> assert danh
sach quote) + 1 mutation anchor chung minh neu ai revert ve DRIVER_QUOTE_PATTERN cu
(bat nham) thi test se FAIL (test_mutation_...). Khong pass-rong: moi assert doi 1
quote CU THE co/khong trong tap driver quote.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import audit_hidden_bugs as ahb  # noqa: E402


def _driver_quote_texts(body):
    """Danh sach text quote gan cho BAC TAI (speaker-tracking)."""
    return [q for _pos, q in ahb.driver_quotes(body)]


def _public_extra_quotes(body):
    """Quote 'thua' qua API cong khai split_driver_extra_quotes() (hook + rest)."""
    hook, rest = ahb.split_driver_extra_quotes(body)
    return hook + rest


# ===========================================================================
# NHOM 1 — FALSE-POSITIVE PHAI BO: quote hanh khach sau cum bac tai KHONG-kem-quote
# (regex CU nhay toi va gan nham -> speaker-tracking phai BO)
# ===========================================================================

def test_fp_liec_guong_khong_noi_then_passenger_narration():
    """ep_15/24-style: `Bác tài liếc gương. Không nói.` roi vai doan sau la loi
    HANH KHACH -> KHONG duoc gan bac tai."""
    body = (
        'Bác tài liếc gương. Không nói.\n\n'
        'Anh ghế sáu vuốt vải.\n\n'
        '"Tôi nhớ mẹ..."'
    )
    dq = _driver_quote_texts(body)
    assert "Tôi nhớ mẹ..." not in dq
    assert dq == []  # khong co quote bac tai nao trong doan nay


def test_fp_de_bai_tren_vo_not_driver():
    """ep_24 that: `Đề bài: "Tả cô giáo em yêu nhất."` la text tren vo (narration
    'Bà cụ lật vở'), KHONG phai loi ai — nhat la khong phai bac tai."""
    body = (
        'Bác tài liếc gương. Không nói.\n\n'
        'Bà cụ lật vở. Đề bài: "Tả cô giáo em yêu nhất."'
    )
    dq = _driver_quote_texts(body)
    assert "Tả cô giáo em yêu nhất." not in dq
    assert "Tả cô giáo em yêu nhất." not in _public_extra_quotes(body)


def test_fp_passenger_quote_at_paragraph_start_not_driver():
    """ep_17 that: quote hanh khach dung dau doan, doan lien truoc KHONG phai cum
    dan bac tai -> KHONG gan bac tai."""
    body = (
        'Em ghế sáu nhìn về bến.\n\n'
        '"Toàn..."\n\n'
        'Người đàn ông nói rất nhỏ.'
    )
    dq = _driver_quote_texts(body)
    assert "Toàn..." not in dq
    assert dq == []


# ===========================================================================
# NHOM 2 — DRIVER PHAI GIU: loi bac tai that phai duoc bat (chong false-negative)
# Gom 2 case Variant A regex TUNG SOT (inline co mo ta xen + appositive doan lien truoc)
# ===========================================================================

def test_driver_inline_clean_cliffhanger():
    """ep_15 cliffhanger inline sach: `Bác tài liếc gương. "Vào đêm..."`."""
    body = 'Bác tài liếc gương. "Vào đêm mười lăm. Cứ giữ vật này."'
    dq = _driver_quote_texts(body)
    assert "Vào đêm mười lăm. Cứ giữ vật này." in dq


def test_driver_inline_with_interposed_description_variant_a_missed():
    """ep_21 — Variant A regex SOT (mo ta 'lần này dừng trên người khách lâu.' xen
    giua verb va quote lam `[^"\\w]*?` cua A truot). Speaker-tracking PHAI cuu."""
    body = (
        'Bác tài liếc gương — lần này dừng trên người khách lâu. '
        '"Vào đêm hai mươi mốt. Con nhớ phố Khâm Thiên."'
    )
    dq = _driver_quote_texts(body)
    assert "Vào đêm hai mươi mốt. Con nhớ phố Khâm Thiên." in dq


def test_driver_appositive_previous_paragraph_variant_a_missed():
    """ep_11 — Variant A regex SOT (quote o doan RIENG sau doan-dan appositive).
    Speaker-tracking (nhanh doan-lien-truoc) PHAI cuu."""
    body = (
        'Bác tài liếc gương — lần này dừng trên người đàn ông lâu hơn thường lệ nhiều.\n\n'
        '"Vào đêm mười một. Con bắt đầu nhớ một tên."'
    )
    dq = _driver_quote_texts(body)
    assert "Vào đêm mười một. Con bắt đầu nhớ một tên." in dq


def test_driver_colon_flashback_inline():
    """ep_35 flashback inline dau hai cham: `Bác tài đêm đầu chỉ nói: "..."`."""
    body = 'Bác tài đêm đầu chỉ nói: "Con đi cùng chuyến xe này. Đêm sau con sẽ hiểu."'
    dq = _driver_quote_texts(body)
    assert "Con đi cùng chuyến xe này. Đêm sau con sẽ hiểu." in dq


def test_driver_hook_tiep_previous_paragraph():
    """ep_50-style HOOK: `Bác tài tiếp:` (doan dan) + quote o doan lien sau."""
    body = 'Bác tài tiếp:\n\n"Đêm nay sẽ có cậu trai khác. Cứ giữ lại."'
    dq = _driver_quote_texts(body)
    assert "Đêm nay sẽ có cậu trai khác. Cứ giữ lại." in dq


# ===========================================================================
# NHOM 3 — NEGATION GUARD: `không nói` PHU DINH veto -> KHONG sinh quote bac tai
# ===========================================================================

def test_negation_no_quote_when_driver_khong_noi():
    """Proposal fixture: `Bác tài liếc gương. Không nói nữa...` — khong co quote nao
    gan bac tai (khong co quote adjacency; 'không nói' veto)."""
    body = (
        'Bác tài liếc gương. Không nói nữa — câu thứ ba đã nói.\n\n'
        'Khải Phong đặt mảnh lên đùi.'
    )
    dq = _driver_quote_texts(body)
    assert dq == []


def test_negation_veto_blocks_following_quote():
    """MUTATION-PROOF cho NEG veto: cung mau nhung CO quote hanh khach o doan sau.
    Neu bo veto `không nói`, nhanh doan-lien-truoc se thay 'Bác tài ... liếc gương'
    + quy nham quote cho bac tai. Veto PHAI chan."""
    body = (
        'Bác tài liếc gương. Không nói.\n\n'
        '"Con sợ lắm..."'
    )
    dq = _driver_quote_texts(body)
    assert "Con sợ lắm..." not in dq
    assert dq == []


# ===========================================================================
# MUTATION ANCHOR (R215.1 / task item 5) — chung minh revert ve regex CU = FP
# ===========================================================================

def test_mutation_legacy_regex_would_misattribute_but_speaker_tracking_does_not():
    """EP24 kinh dien: `Bác tài liếc gương. Không nói.` roi text-tren-vo hanh khach.
    - LEGACY DRIVER_QUOTE_PATTERN (con dinh nghia lam tham chieu) BAT NHAM quote nay
      -> chung minh co che CU that su buggy (khong phai gia dinh).
    - driver_quotes() speaker-tracking KHONG gan.
    - API cong khai split_driver_extra_quotes() KHONG surface no.
    Neu ai revert split_driver_extra_quotes() ve DRIVER_QUOTE_PATTERN.finditer(),
    assert cuoi se FAIL -> mutation-proof."""
    body = (
        'Bác tài liếc gương. Không nói.\n\n'
        'Bà cụ khẽ lật cuốn vở.\n\n'
        '"Tả cô giáo em yêu nhất."'
    )
    legacy = [m.group(1) for m in ahb.DRIVER_QUOTE_PATTERN.finditer(body)]
    assert "Tả cô giáo em yêu nhất." in legacy, (
        "regex CU phai bat nham (chung minh bug that) — neu khong, mutation anchor vo nghia"
    )
    dq = _driver_quote_texts(body)
    assert "Tả cô giáo em yêu nhất." not in dq
    hook, rest = ahb.split_driver_extra_quotes(body)
    assert "Tả cô giáo em yêu nhất." not in (hook + rest), (
        "split_driver_extra_quotes() PHAI dung speaker-tracking — revert ve regex cu se FAIL o day"
    )


def test_split_public_api_matches_driver_quotes_source():
    """Chong pass-rong o tang API: split_driver_extra_quotes() phai lay tu
    driver_quotes() — mot loi foreshadow that (inline sach) PHAI xuat hien trong
    extras (khong bi loc, khong phai standard line)."""
    body = 'Bác tài liếc gương. "Vào đêm mười lăm. Cứ giữ vật này."'
    extras = _public_extra_quotes(body)
    assert "Vào đêm mười lăm. Cứ giữ vật này." in extras
