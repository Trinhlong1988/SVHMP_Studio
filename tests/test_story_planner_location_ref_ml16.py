"""audit ML #16 (10/7) — story_planner.build_episode_plan_ep01(): location_ref phai doc DONG
tu event_ledger_draft ep_01.primary_event.stop_location.value, KHONG hardcode literal.
Truoc fix: hardcode "Cau Long Bien" (khop ngau nhien voi data that; drift neu ledger doi).
Mutation-proof: doi gia tri stop_location trong event_ledger (mock) -> location_ref PHAI doi theo.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import story_planner as sp


def test_location_ref_matches_event_ledger_default():
    plan = sp.build_episode_plan_ep01()
    locs = {s['location_ref'] for s in plan['scenes_detail']}
    assert locs == {'Cầu Long Biên'}, f"gia tri that hien tai tu event_ledger, got {locs}"


def test_location_ref_reads_dynamically_not_hardcoded(monkeypatch):
    real_load = sp._load

    def fake_load(path):
        data = real_load(path)
        if str(path) == str(sp.EVENT_LEDGER):
            data['events']['ep_01']['primary_event']['stop_location']['value'] = 'DIA DIEM MOCK ML16'
        return data

    monkeypatch.setattr(sp, '_load', fake_load)
    plan = sp.build_episode_plan_ep01()
    locs = {s['location_ref'] for s in plan['scenes_detail']}
    # Neu code hardcode 'Cau Long Bien' -> test nay FAIL (locs != mock). Chung minh doc dong.
    assert locs == {'DIA DIEM MOCK ML16'}, f"location_ref phai doc dong tu event_ledger, got {locs}"
