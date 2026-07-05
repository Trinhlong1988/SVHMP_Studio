"""SVHMP — Single source of truth cho pattern "Hà" trần trụi (lộ tên gốc, đã rename).

Truoc fix nay, 4 tool doc lap dinh nghia list pattern LECH NHAU:
  - tools/post_render_gate.py       : 9 pattern (day nhat, co "Hà mất"/"Hà chết"/
                                       "Hà tai nạn"/"với Hà"/"cho Hà"/"của Hà")
  - tools/audit_100_check.py        : 4 pattern (thieu 5 pattern so voi gate)
  - tools/audit_60_dimensions.py    : 4 pattern giong audit_100_check.py
  - tools/audit_continuity_cross_ep.py : regex khac han (negative-lookahead bat
                                       MOI "Hà" tran trui, khong loc theo cum tu)
  => cung 1 doan van co the PASS gate nay nhung FAIL gate kia.

FIX: chon FORBIDDEN_HA_PATTERNS cua post_render_gate.py (day nhat, chat nhat) lam
SINGLE SOURCE. 3 tool con lai import truc tiep tu day, khong tu dinh nghia rieng.

Luu y: audit_continuity_cross_ep.py van giu cong thuc threshold rieng cua no
(`naked_ha <= ep_num // 10` — tolerance scale theo tap), CHI dong bo lai PATTERN
list dung chung, khong dong bo cong thuc.
"""

FORBIDDEN_HA_PATTERNS = [
    r'\btên Hà\b',
    r'\bcô Hà\b',
    r'\byêu Hà\b',
    r'\bHà mất\b',
    r'\bHà chết\b',
    r'\bHà tai nạn\b',
    r'\bvới Hà\b',
    r'\bcho Hà\b',
    r'\bcủa Hà\b',
]
