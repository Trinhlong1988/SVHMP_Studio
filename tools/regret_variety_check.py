"""regret_variety_check.py — DEBT-032 check #2 (regret variety), per Mr.Long authorization
12/7 (TASK_DEBT030_031_CONTENT_FIX.md Buoc 3, giao kem DEBT-031 content fix).

Doi chieu `regret_sub` cua cac tap DA CO trong `runtime/event_ledger_draft.yaml` (da mine san,
KHONG mine lai) voi `bible/11_regret_catalog.yaml#variety_rules`:
  - pillar_distance        : cung pillar khong duoc lap lai cach nhau < N tap (mac dinh 3)
  - family_regret_max_per_10_ep : moi cua so 10 tap lien tiep, family_regret khong qua N lan
  - pillar_per_10_ep_min_distinct : moi cua so 10 tap lien tiep, phai dung >= N pillar khac nhau

Nguyen nhan can enforcer nay: DEBT-032 (TECH_DEBT.md) — grep xac nhan TRUOC task nay, KHONG co
tool QA nao (ke ca svhmp_preflight_qa.py) doi chieu noi dung episode that voi 2 rule bible/11 nay,
khien EP02-10 lot qua QA pipeline dung 9/10 tap cung family_regret (DEBT-031) ma khong ai bat.

R211 (tai dung khung san co, KHONG viet lai):
  - REGRET_SUB_PREFIX_TO_PILLAR + EVENT_LEDGER + BIBLE_11_REGRET: import tu tools/story_planner.py
    (source_of_truth mapping prefix->pillar, da TU CHINH 12/7 cung task nay).
  - Wired vao tools/svhmp_preflight_qa.py (FULL_TEXT_GATE section), mirror pattern
    CHARACTER_COMPLETENESS_GATE da co san trong file do (import + append issues, WARN-by-default
    khong crash render neu module thieu).

CHUA CO ENFORCER rieng cho pillar_distance/family_regret_max/min_distinct O CAC FILE KHAC ngoai
runtime/event_ledger_draft.yaml (vd neu ai viet EP12+ ma khong cap nhat ledger, check nay se
KHONG thay - phu thuoc hoan toan vao ledger da duoc DUYET/mine dung). Day la gioi han da biet,
ghi ro theo R215 (khong claim rong hon that co).
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_TOOLS = str(REPO / "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

import story_planner as sp  # noqa: E402 - tai dung REGRET_SUB_PREFIX_TO_PILLAR/EVENT_LEDGER/BIBLE_11_REGRET

__version__ = "1.0.0"

DEFAULT_WINDOW = 10  # khop bible/11 "..._per_10_ep_..." naming


def _regret_sub_value(primary_event):
    """Trich value string tu primary_event['regret_sub'] (dict {'value':...} hoac None)."""
    rs = (primary_event or {}).get("regret_sub")
    if rs is None:
        return None
    if isinstance(rs, dict):
        return rs.get("value")
    return rs


def load_pillar_sequence(ledger_events=None, max_ep=None):
    """Tra ve list [(ep_int, pillar_str)] SAP XEP theo ep tang dan, CHI cac tap co regret_sub
    != null VA prefix da biet trong story_planner.REGRET_SUB_PREFIX_TO_PILLAR (bo qua ep chua
    field-hoa/pending - KHONG suy doan, R195). `ledger_events` optional override (dict giong
    event_ledger_draft.yaml['events']) - dung cho test injection, mac dinh doc file that.
    `max_ep` optional - chi lay ep <= max_ep (dung khi preflight 1 tap, khong xem tap sau)."""
    if ledger_events is None:
        ledger = sp._load(sp.EVENT_LEDGER)
        ledger_events = ledger.get("events", {})
    pairs = []
    for ep_key, ep_data in ledger_events.items():
        m = ep_key.split("_")
        try:
            ep_num = int(m[-1])
        except (ValueError, IndexError):
            continue
        if max_ep is not None and ep_num > max_ep:
            continue
        regret_sub_value = _regret_sub_value(ep_data.get("primary_event"))
        pillar = sp._regret_pillar_from_regret_sub(regret_sub_value)
        if pillar is not None:
            pairs.append((ep_num, pillar))
    pairs.sort(key=lambda t: t[0])
    return pairs


def load_variety_rules(bible11=None):
    """Doc variety_rules that tu bible/11_regret_catalog.yaml (KHONG hardcode nguong)."""
    data = bible11 if bible11 is not None else sp._load(sp.BIBLE_11_REGRET)
    return data["variety_rules"]


def check_pillar_distance(pairs, min_distance):
    """FAIL neu 2 lan xuat hien LIEN TIEP cua CUNG 1 pillar cach nhau < min_distance tap."""
    errs = []
    last_ep_for_pillar = {}
    for ep_num, pillar in pairs:
        if pillar in last_ep_for_pillar:
            gap = ep_num - last_ep_for_pillar[pillar]
            if gap < min_distance:
                errs.append(
                    f"pillar_distance: {pillar} lap lai ep_{last_ep_for_pillar[pillar]:02d}->"
                    f"ep_{ep_num:02d} (cach {gap}, can >={min_distance})")
        last_ep_for_pillar[pillar] = ep_num
    return errs


def check_family_max_per_window(pairs, max_family, window=DEFAULT_WINDOW):
    """FAIL neu bat ky cua so `window` tap LIEN TIEP (theo ep_num that, khong phai theo index)
    co so lan family_regret > max_family."""
    errs = []
    if not pairs:
        return errs
    eps = [p[0] for p in pairs]
    lo_ep, hi_ep = min(eps), max(eps)
    seen_windows = set()
    for start in range(lo_ep, hi_ep + 1):
        end = start + window - 1
        key = (start, end)
        if key in seen_windows:
            continue
        seen_windows.add(key)
        count = sum(1 for ep_num, pillar in pairs if start <= ep_num <= end and pillar == "family_regret")
        if count > max_family:
            errs.append(
                f"family_regret_max_per_{window}_ep: ep_{start:02d}..ep_{end:02d} co "
                f"{count} lan family_regret (can <={max_family})")
    return errs


def check_min_distinct_per_window(pairs, min_distinct, window=DEFAULT_WINDOW):
    """FAIL neu bat ky cua so `window` tap LIEN TIEP co so pillar KHAC NHAU < min_distinct.
    CHI kiem cac cua so co it nhat `window` tap DA CO du lieu (bo qua batch dau chua du du
    lieu de tranh bao dong gia luc mining con dang do dang)."""
    errs = []
    if not pairs:
        return errs
    eps = [p[0] for p in pairs]
    lo_ep, hi_ep = min(eps), max(eps)
    seen_windows = set()
    for start in range(lo_ep, hi_ep + 1):
        end = start + window - 1
        key = (start, end)
        if key in seen_windows:
            continue
        seen_windows.add(key)
        in_window = [pillar for ep_num, pillar in pairs if start <= ep_num <= end]
        if len(in_window) < window:
            continue  # cua so chua du du lieu (vd cuoi batch da mine) - bo qua, khong bia
        distinct = len(set(in_window))
        if distinct < min_distinct:
            errs.append(
                f"pillar_per_{window}_ep_min_distinct: ep_{start:02d}..ep_{end:02d} chi co "
                f"{distinct} pillar khac nhau (can >={min_distinct})")
    return errs


def check_regret_variety(max_ep=None, ledger_events=None, bible11=None):
    """Composition — chay CA 3 sub-check tren bible/11 variety_rules that. Tra ve list issue
    string (rong = PASS). `max_ep`/`ledger_events`/`bible11` optional override cho test."""
    rules = load_variety_rules(bible11)
    pairs = load_pillar_sequence(ledger_events=ledger_events, max_ep=max_ep)
    errs = []
    errs += check_pillar_distance(pairs, rules["pillar_distance"])
    errs += check_family_max_per_window(pairs, rules["family_regret_max_per_10_ep"])
    errs += check_min_distinct_per_window(pairs, rules["pillar_per_10_ep_min_distinct"])
    return errs


def _run_all_body_ok(src):
    """Static proof (mirror pattern tests/test_supernatural_run_all_composition.py): xac nhan
    check_regret_variety() trong SOURCE that dang goi du 3/3 sub-check. Tra (ok, detail)."""
    import re as _re
    m = _re.search(r"def check_regret_variety\(.*?\n(?=def |\Z)", src, _re.DOTALL)
    if not m:
        return False, "khong tim thay ham check_regret_variety()"
    body = m.group(0)
    required_calls = ["check_pillar_distance(", "check_family_max_per_window(", "check_min_distinct_per_window("]
    missing = [c for c in required_calls if c not in body]
    if missing:
        return False, f"check_regret_variety() thieu goi: {missing}"
    return True, "OK"


if __name__ == "__main__":
    issues = check_regret_variety()
    if issues:
        print(f"REGRET_VARIETY FAIL — {len(issues)} issue(s)")
        for i in issues:
            print(f"  {i}")
        sys.exit(1)
    print("REGRET_VARIETY PASS — 0 issue")
    sys.exit(0)
