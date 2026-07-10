"""audit ML #7/#8 (10/7) — dialogue_generator.py:
#7 placeholder '...' gia mao: khi khong dung duoc bien the tu du lieu THAT (pronoun malformed
   + catchphrase/scene_context rong), truoc tra status='OK' line='...'. Nay _candidate_variants
   tra [] (khong placeholder) va generate_line -> REFUSED reason='NO_VARIANT_FROM_REAL_DATA' (R195).
#8 field 'particles' thieu (39/139) bi am tham default [] -> nay vao OPTIONAL_VOICE_FIELDS +
   missing_optional_fields + report.
"""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import dialogue_generator as dg
from dialogue_generator import (generate_line, _candidate_variants, OPTIONAL_VOICE_FIELDS,
                                 DialogueManager)

REPO = Path(__file__).parent.parent


def _dm():
    return DialogueManager()


# ---------- #7: khong con placeholder '...' ----------

def test_candidate_variants_returns_empty_not_placeholder():
    # pronoun_system '/' tach ra token rong + catchphrase/scene rong -> KHONG co bien the that.
    # Mutation-proof: truoc fix ham tra ['...'], nay phai tra [] (khong bia placeholder).
    profile = {'pronoun_system': '/', 'particles': []}
    voice_profile = {'catchphrase': ''}
    out = _candidate_variants(profile, voice_profile, {})
    assert out == [], f"khong duoc tra placeholder, got {out}"
    assert '...' not in out


def test_generate_line_refuses_when_no_variant(monkeypatch):
    # ep candidates rong -> generate_line PHAI tra REFUSED ro rang, KHONG OK+'...'
    dm = _dm()
    real = [c for c in dm.registry.all('passenger') if c.assigned_ep][:1]
    assert real, "can it nhat 1 passenger co assigned_ep"
    monkeypatch.setattr(dg, '_candidate_variants', lambda *a, **k: [])
    r = generate_line(real[0].id, {}, dm)
    assert r['status'] == 'REFUSED'
    assert r['reason'] == 'NO_VARIANT_FROM_REAL_DATA'
    assert r.get('line') in (None, ''), "KHONG duoc emit line placeholder khi refuse"


# ---------- #8: particles vao OPTIONAL_VOICE_FIELDS + report ----------

def test_particles_now_in_optional_voice_fields():
    assert 'particles' in OPTIONAL_VOICE_FIELDS, "audit ML #8: particles phai duoc theo doi"


def test_missing_particles_appears_in_missing_optional(tmp_path):
    dm = _dm()
    base = next((c for c in dm.registry.all('passenger') if c.assigned_ep), None)
    assert base is not None
    bad = copy.deepcopy(base)
    bad.id = 'TEST_ML8_NO_PARTICLES'
    bad.voice.particles = []          # gia lap passenger thieu particles
    dm.registry.chars[bad.id] = bad
    try:
        r = generate_line(bad.id, {'emotion_beat': 'nho nha', 'listener_call': 'Me oi'},
                          dm, missing_report_path=tmp_path / 'missing.md')
        assert 'particles' in r['missing_optional_fields'], (
            "particles thieu phai xuat hien trong missing_optional_fields")
        report = tmp_path / 'missing.md'
        assert report.exists() and bad.id in report.read_text(encoding='utf-8')
    finally:
        del dm.registry.chars[bad.id]
