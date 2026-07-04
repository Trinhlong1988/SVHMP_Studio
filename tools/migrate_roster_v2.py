"""SVHMP — Migrate roster -> Character Identity System v2 (Boss 2/7: fix hoan chinh).

GIU NGUYEN identity lock: id, char_name, pillar, regret_*, signature_object/setting, gender, assigned_ep.
ENRICH can bang (deterministic, KHONG random, KHONG suy luan narrative):
- age_range: rebalance dat target (child 12 / youth 28 / middle 33 / elderly 17 / unknown 10).
- life_status: da_mat (unknown-age -> linh_hon).
- voice: region_dialect + hometown + pronoun + particle (>=3 vung, hop le validator).
- death.type: trai deu 9 kieu (khong lap 'oan_khuat').
- pain <- regret_label; haunting_symbol <- signature_object (mapping, khong bia).
Ghi de roster (git giu ban goc). Bump schema_version=2.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml
from gen_100_passenger import compute_novelty_hash

SVHMP = Path(__file__).parent.parent
ROSTER = SVHMP / 'runtime' / 'passenger_roster_100.yaml'

STAGE_TARGET = [('child', 12), ('youth', 28), ('middle', 33), ('elderly', 17), ('unknown', 10)]
AGE_OF = {'child': ['13-17', '13-17'], 'youth': ['18-25', '26-35'],
          'middle': ['36-50', '51-65'], 'elderly': ['66+', '66+'], 'unknown': ['', '']}
REGIONS = ['bac', 'trung', 'nam']
HOME = {'bac': ['Hà Nội', 'Hải Phòng', 'Nam Định', 'Bắc Ninh', 'Thái Bình', 'Hải Dương'],
        'trung': ['Huế', 'Nghệ An', 'Hà Tĩnh', 'Đà Nẵng', 'Quảng Bình'],
        'nam': ['Sài Gòn', 'Biên Hòa', 'Vũng Tàu', 'Hồ Chí Minh']}  # chi town map 'nam' (tranh mismatch tay)
PRON = {'bac': 'tôi', 'trung': 'tui', 'nam': 'con'}
PART = {'bac': 'nhỉ', 'trung': 'rứa', 'nam': 'nghen'}
DEATHS = ['tai_nan', 'benh_tat', 'mat_tich', 'oan_khuat', 'tu_nhien',
          'hieu_lam', 'hy_sinh', 'bi_phan_boi', 'khong_ro']


def main():
    data = yaml.safe_load(ROSTER.read_text(encoding='utf-8'))
    pas = data['passengers']
    n = len(pas)

    # stage pool dung target, spread (khong cum) bang stride nguyen to
    pool = []
    for s, c in STAGE_TARGET:
        pool += [s] * c
    pool = pool[:n] + ['middle'] * max(0, n - len(pool))
    order = sorted(range(n), key=lambda i: (i * 37) % n)
    stage_of = {}
    for k, i in enumerate(order):
        stage_of[i] = pool[k]

    for i, p in enumerate(pas):
        stg = stage_of[i]
        age = AGE_OF[stg][i % 2]
        p['age_range'] = age
        p['life_status'] = 'linh_hon' if stg == 'unknown' else 'da_mat'
        region = REGIONS[i % 3]
        p['voice'] = {
            'region_dialect': region,
            'hometown': HOME[region][i % len(HOME[region])],
            'pronoun_system': PRON[region],
            'particles': [PART[region]],
            'register': 'dan_da',
        }
        p['death'] = {'type': DEATHS[i % len(DEATHS)], 'pain': p.get('regret_label', '')}
        p['haunting_symbol'] = p.get('signature_object', '')
        p['display_name'] = f"{p['char_name']} ({age or 'linh hồn'})"
        p['status'] = 'identity_v2'
        p['novelty_hash'] = compute_novelty_hash({**p, 'relationship_focus': region,
                                                  'time_of_loss': p['death']['type']})

    data['schema_version'] = 2
    data['migration_v2'] = {
        'by': 'tools/migrate_roster_v2.py', 'date': '2026-07-02',
        'enriched': ['age_range(rebalanced)', 'life_status', 'voice', 'death', 'haunting_symbol'],
        'preserved': ['id', 'char_name', 'pillar', 'regret_*', 'signature_object/setting', 'gender', 'assigned_ep'],
    }
    ROSTER.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print(f"MIGRATED {n} passenger -> v2. Preserved identity, enriched age/voice/death/life_status.")


if __name__ == '__main__':
    main()
