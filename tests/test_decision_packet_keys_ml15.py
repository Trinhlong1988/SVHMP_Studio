"""audit ML #15 (10/7) — bp6_decision_check.check_io() chi doi chieu packet_schema TINH khai
trong decision_io.yaml, KHONG bao gio goi decision_engine.build_packet() that -> neu build_packet
them top-level key ngoai PACKET_REQUIRED ∪ {status, status_note} thi khong check nao bat.
Test nay goi build_packet THAT + doi chieu key thuc te (mutation-proof: them key la -> FAIL).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import decision_engine as de
import story_planner as sp
from bp6_decision_check import PACKET_REQUIRED


def test_build_packet_top_level_keys_within_declared_set():
    plan = sp.build_episode_plan_ep01()
    packet = de.build_packet(1, plan=plan)
    allowed = set(PACKET_REQUIRED) | {'status', 'status_note'}
    extra = set(packet.keys()) - allowed
    assert not extra, (
        f"build_packet() them top-level key ngoai danh sach da khai "
        f"(PACKET_REQUIRED ∪ status/status_note): {extra} - field-creep khong duoc khai dong")


def test_build_packet_has_status_fields_beyond_required():
    # xac nhan status/status_note la 2 field build_packet them ngoai PACKET_REQUIRED (baseline that)
    plan = sp.build_episode_plan_ep01()
    packet = de.build_packet(1, plan=plan)
    assert 'status' in packet and 'status_note' in packet
    for f in PACKET_REQUIRED:
        assert f in packet, f"packet thieu field bat buoc PACKET_REQUIRED: {f}"
