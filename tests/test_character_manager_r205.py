"""R205 — CharacterRegistry/Profile (Boss 1/7): quan ly nhan vat theo class,
tai dung roster+bible/23, khong sinh ten. Validate load/query/naming/enrich/completeness."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
sys.stdout.reconfigure(encoding='utf-8')
from character_manager import CharacterRegistry, CharacterProfile, VoiceProfile

PASS, FAIL = [], []
def ck(n, c, d=""): (PASS if c else FAIL).append(n); print(("  ok  " if c else "  X   ") + n + ("" if c else f"  [{d}]"))

reg = CharacterRegistry()
pas = reg.all('passenger')
rec = reg.all('recurring')

ck("load 139 passenger (100 goc + 39 backfill ep11-50, merge per Mr.Long 5/7)", len(pas) == 139, len(pas))
ck("load 2 recurring (Bac tai + Nam)", len(rec) == 2, len(rec))
ck("id duy nhat", len({c.id for c in reg.all()}) == len(reg.all()))
ck("naming bible/23 = 0 loi (tai dung, khong sinh)", len(reg.validate_names()) == 0)

d = reg.distribution()
# CAP NHAT 5/7 + DEBT-021 (11/7): 32/24/20/14/10 la balance-target CHI cho 100 passenger GOC
# (gen_100_passenger.py, distribution_target trong roster yaml - GIU NGUYEN, bible/11 lock). So THAT
# tren 139 (39 backfill text-mining): family=41/love=31/promise=29/kindness=23/self=15. PAS_0151
# (Ha Nhi) DA gan pillar family_regret theo bang chung (DEBT-021, Mr.Long 11/7) -> family 40->41,
# 0 RFC_PENDING o pillar (regret_sub_archetype VAN RFC_PENDING, cho RFC bible/11). Enforcer dong bo
# distribution_actual <-> roster: tests/test_roster_distribution_sync.py.
ck("pillar tong THAT sau DEBT-021 (family=41/love=31/promise=29/kindness=23/self=15, 0 RFC_PENDING pillar)",
   d['by_pillar'].get('family_regret') == 41 and d['by_pillar'].get('self_regret') == 15
   and d['by_pillar'].get('RFC_PENDING', 0) == 0, d['by_pillar'])
ck("gender tong THAT sau merge (khong con 50/50 dung vi 39 backfill khong can bang theo generator)",
   d['by_gender'] == {'nu': 69, 'nam': 70}, d['by_gender'])
ck("region_dialect DA set >=3 vung (sau migrate v2)", d['by_region_dialect'].get('?', 0) == 0 and len([k for k in d['by_region_dialect'] if k != '?']) >= 3)

cr = reg.completeness_report()
ck("enriched v2: completeness > 0, khong con skeleton", cr['avg_completeness'] > 0.0 and cr['skeleton_only'] < 100)

# get / filter
c0 = pas[0]
ck("get theo id", reg.get(c0.id) is c0)
ck("filter theo gender", all(x.gender == 'nu' for x in reg.filter(gender='nu')))

# enrich: bo sung truong mo rong (voice/quehuong) -> completeness tang
reg.enrich(c0.id, life_status='da_mat',
           physical={'hair': {'length': 'dai', 'color': 'den'}, 'face': {'dimple': True}},
           voice={'region_dialect': 'nam_saigon', 'hometown': 'Ben Tre', 'pronoun_system': 'tui'})
ck("enrich life_status", reg.get(c0.id).life_status == 'da_mat')
ck("enrich voice (quehuong+giong)", reg.get(c0.id).voice.hometown == 'Ben Tre' and reg.get(c0.id).voice.region_dialect == 'nam_saigon')
ck("completeness tang sau enrich", reg.get(c0.id).completeness() > 0.0)
try:
    reg.enrich(c0.id, khong_co_truong=1); _ke = False
except KeyError:
    _ke = True
ck("enrich field sai -> KeyError", _ke)

# schema co du nhom truong Boss yeu cau
names = {f.name for f in __import__('dataclasses').fields(CharacterProfile)}
need = {'dob', 'life_status', 'physical', 'attire', 'personality', 'voice', 'background', 'death', 'relationships'}
ck("schema du nhom truong 'tat ca ve 1 con nguoi'", need <= names, need - names)
vneed = {'region_dialect', 'hometown', 'residence', 'pronoun_system', 'particles', 'register'}
vnames = {f.name for f in __import__('dataclasses').fields(VoiceProfile)}
ck("VoiceProfile du truong dialogue (que->giong)", vneed <= vnames, vneed - vnames)

print(f"\n=== SUMMARY: {len(PASS)} PASS / {len(FAIL)} FAIL ===")
for n in FAIL: print("  FAIL:", n)
sys.exit(1 if FAIL else 0)
