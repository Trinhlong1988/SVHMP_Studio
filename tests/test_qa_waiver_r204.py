"""R204 — waiver chong spam (Boss 1/7): QA khong bao lai loi DA PHAT HIEN+DUYET,
NHUNG van surface loi MOI (vd R80.click). Additive, khong doi detector."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
sys.stdout.reconfigure(encoding='utf-8')
from svhmp_audio_qa import _is_waived, _load_waivers

PASS, FAIL = [], []
def ck(n, c): (PASS if c else FAIL).append(n); print(("  ok  " if c else "  X   ") + n)

w = [{"rule": "R77.audio", "type": "internal_silence"}, {"rule": "R80.peak"}]
ck("waive R77 internal_silence (nghi intro)", _is_waived({"rule": "R77.audio", "type": "internal_silence"}, w))
ck("waive R80.peak moi type (master lock)", _is_waived({"rule": "R80.peak", "type": "overall_peak_clipping"}, w))
ck("KHONG waive R80.click (loi MOI phai surface)", not _is_waived({"rule": "R80.click", "type": "click_transient"}, w))
ck("KHONG waive R80 bup (loi MOI)", not _is_waived({"rule": "R80", "type": "bụp_transient"}, w))
ck("KHONG waive R77 khac type", not _is_waived({"rule": "R77.audio", "type": "other"}, w))
ck("waiver rong -> khong bo gi", not _is_waived({"rule": "R80.click", "type": "x"}, []))
ck("load qa_waivers.json >=2 lop", len(_load_waivers(str(Path(__file__).parent.parent / "runtime" / "qa_waivers.json"))) >= 2)

print(f"\n=== SUMMARY: {len(PASS)} PASS / {len(FAIL)} FAIL ===")
sys.exit(1 if FAIL else 0)
