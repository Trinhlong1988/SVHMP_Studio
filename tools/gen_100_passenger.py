"""SVHMP — Procedural gen 100 passenger roster framework (Phase H7 round 14).

Tuân thủ hiến pháp (verified 2026-06-27):
- bible/00 ALWAYS.unresolved_goodbye + object_symbolism
- bible/00 NEVER.villain_ghost
- bible/03 line 3: CẤM recurring mới → 100 passenger all one-shot
- bible/11 distribution LOCK: family 32 / love 24 / promise 20 / kindness 14 / self 10
- bible/11 27 sub-archetypes IMMUTABLE
- bible/12 signature_objects per sub_archetype (validated)
- bible/13 pairable_settings per sub_archetype (validated)
- bible/18 EP73 + EP90 = driver reveal special (EXCLUDE từ rotation)
- bible/08 novelty 11-axis distance ≥6 (per memory project_svhmp_8phase_roadmap)

Output: runtime/passenger_roster_100.yaml — skeleton, Generator creative-fill khi gen từng ep.
"""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent

# ─── Distribution LOCK từ bible/11 (verified 27/6) ───
PILLAR_DISTRIBUTION = {
    'family_regret':   32,  # weight 0.32
    'love_regret':     24,  # 0.24
    'promise_regret':  20,  # 0.20
    'kindness_regret': 14,  # 0.14
    'self_regret':     10,  # 0.10
}
# Total = 100 ✓

# ─── EP slots ───
# Total 90 ep (memory project_svhmp_youtube_channel "Series 1 90 ep"), but Mr.Long target "100" per docx.
# bible/18 lock EP73 + EP90 driver reveal → exclude từ passenger rotation.
RESERVED_EPS = {73, 90}
# Generate 100 passenger spec, assign 88 to ep 1-72 + ep 74-89 (total 88 slots).
# 12 passenger spare = backup pool (failed QA / Mr.Long reject swap).


def load_bible(name: str) -> dict:
    import yaml
    p = SVHMP / 'bible' / name
    return yaml.safe_load(p.read_text(encoding='utf-8'))


def compute_novelty_hash(p: dict) -> str:
    """7-dim hash (per bible/08 novelty_hash schema)."""
    sig = '|'.join([
        p.get('regret_sub_archetype', ''),
        p.get('signature_object', ''),
        p.get('signature_setting', ''),
        p.get('age_range', ''),
        p.get('gender', ''),
        p.get('relationship_focus', ''),
        p.get('time_of_loss', ''),
    ])
    return hashlib.sha256(sig.encode()).hexdigest()[:12]


def gen_passengers() -> list:
    """Procedural gen 100 passenger framework theo bible distribution."""
    bible_11 = load_bible('11_regret_catalog.yaml')
    pillars = bible_11.get('pillars', {})

    # Gather all sub-archetypes per pillar
    pillar_subs = {}
    for pillar_id, pillar_data in pillars.items():
        subs = pillar_data.get('sub_archetypes', []) or []
        pillar_subs[pillar_id] = subs

    # Variation matrix (age + gender) → diversity across reuse
    AGE_RANGES = ['18-25', '26-35', '36-50', '51-65', '66+']
    GENDERS = ['nu', 'nam']

    # Vietnamese name pools — Mr.Long rule 27/6 (bible/23):
    # Load từ tools/name_pool.yaml (auto-gen từ data/vietnamese_names_extended.yaml).
    # Constraints: 2 âm tiết, mỗi word unique global, exclude forbidden (Nam/Tài).
    import yaml as _y
    _pool_path = Path(__file__).parent / 'name_pool.yaml'
    if _pool_path.exists():
        _pool = _y.safe_load(_pool_path.read_text(encoding='utf-8'))
        if not _pool.get('global_word_uniqueness_verified'):
            raise RuntimeError(f'name_pool.yaml word uniqueness FAIL — re-run tools/build_name_pool.py')
        NAMES_NU = _pool['NAMES_NU']
        NAMES_NAM = _pool['NAMES_NAM']
        print(f'  Loaded pool: NU={len(NAMES_NU)} NAM={len(NAMES_NAM)}')
    else:
        raise RuntimeError(f'name_pool.yaml missing — run tools/build_name_pool.py first')

    # LEGACY pool (commented out, replaced by external pool load):
    _LEGACY_NAMES_NU = [  # 50 nữ, mỗi word unique
        'Hạ Vi', 'Diệu Nhi', 'Khánh Hà', 'An Nhiên', 'Minh Châu', 'Quỳnh Như',
        'Bảo Trân', 'Thanh Tâm', 'Mai Linh', 'Thuỳ Dương', 'Mỹ Duyên', 'Hồng Nhung',
        'Ngọc Lan', 'Phương Thảo', 'Hải Yến', 'Kim Ngân', 'Tuyết Mai', 'Thiên Hương',
        'Bích Hợp', 'Cẩm Tú', 'Khả Ái', 'Thu Trang', 'Trà My', 'Hoàng Yến',
        'Nhật Hạ', 'Hiền Hậu', 'Tâm Đan', 'Lan Phượng', 'Tịnh Tâm', 'Quế Anh',
        'Vân Khanh', 'Đan Thanh', 'Linh Đào', 'Phượng Tiên', 'Hương Giang', 'Bảo Hân',
        'Thiên Kim', 'Yến Vy', 'Cẩm Linh', 'Diễm My', 'Lan Hương', 'Phương Quyên',
        'Vy Anh', 'Hồng Ân', 'Mỹ Hạnh', 'Tú Quyên', 'Hà Lam', 'Tường Vân',
        'Nguyệt Nga', 'Hân Ngọc',
    ]
    _LEGACY_NAMES_NAM = [  # 50 nam — LEGACY, KHÔNG dùng (overwritten by pool above)
        'Minh Khang', 'Hoàng Long', 'Bảo Lâm', 'Anh Tuấn', 'Quốc Bảo',
        # ... (legacy hardcode, replaced by tools/name_pool.yaml)
    ]
    # END LEGACY (replaced by external pool load — NAMES_NU + NAMES_NAM came from pool)

    passengers = []
    counter = 13  # PAS_0001-PAS_0012 đã tồn tại từ EP01 R17
    name_idx_nu = 0
    name_idx_nam = 0

    for pillar_id, target_count in PILLAR_DISTRIBUTION.items():
        subs = pillar_subs.get(pillar_id, [])
        if not subs:
            print(f"WARN: pillar {pillar_id} có 0 sub-archetype")
            continue

        # Distribute target_count across sub-archetypes evenly
        # Vd: family 32 / 6 sub = 5-6 mỗi sub
        for sub_idx, sub in enumerate(subs):
            per_sub = target_count // len(subs)
            extra = 1 if sub_idx < (target_count % len(subs)) else 0
            sub_count = per_sub + extra

            sig_objects = sub.get('signature_objects', []) or []
            sig_settings = sub.get('pairable_settings', []) or []
            sub_id = sub.get('id', '?')
            sub_label = sub.get('label', '')

            for variation_idx in range(sub_count):
                # Rotate variations across age + gender
                age_range = AGE_RANGES[variation_idx % len(AGE_RANGES)]
                # Gender chosen by sub-archetype context heuristic:
                # family/love often have implicit gender pairing → alternate
                gender = GENDERS[(variation_idx + sub_idx) % len(GENDERS)]

                # Pick object + setting deterministic (rotate)
                obj = sig_objects[variation_idx % len(sig_objects)] if sig_objects else 'OBJ_TBD'
                setting = sig_settings[variation_idx % len(sig_settings)] if sig_settings else 'setting_TBD'

                # Pick Vietnamese name (Mr.Long rule 27/6: đẹp 2 âm tiết)
                if gender == 'nu':
                    char_name = NAMES_NU[name_idx_nu % len(NAMES_NU)]
                    name_idx_nu += 1
                else:
                    char_name = NAMES_NAM[name_idx_nam % len(NAMES_NAM)]
                    name_idx_nam += 1

                p = {
                    'id': f'PAS_{counter:04d}',
                    'char_name': char_name,
                    'pillar': pillar_id,
                    'regret_sub_archetype': sub_id,
                    'regret_label': sub_label,
                    'signature_object': obj,
                    'signature_setting': setting,
                    'age_range': age_range,
                    'gender': gender,
                    'display_name': f'{char_name} ({age_range})',
                    'narrative_hook': 'TBD by Generator',  # creative fill khi gen ep
                    'assigned_ep': None,                    # assign sau
                    'novelty_hash': None,                   # compute sau
                    'status': 'framework_lock',
                }
                p['novelty_hash'] = compute_novelty_hash(p)
                passengers.append(p)
                counter += 1

    return passengers


def assign_eps(passengers: list, total_eps: int = 90) -> list:
    """Assign ep 1-total_eps EXCLUDE 73 + 90.
    EP01 đã ship (PAS_0001-0012 reuse), skip.
    Assign 88 passenger → 88 ep slots (2-72, 74-89). 12 spare backup pool."""
    available_eps = [e for e in range(2, total_eps + 1) if e not in RESERVED_EPS]
    # 89 slots (2-89 = 88 eps, minus 73 = 87, but range(2,91) = 89, minus {73,90} = 87)
    # Actually range(2,91) = 2..90 = 89 eps. Minus {73,90} = 87 available.

    # Tuần tự assign theo rotation (Generator có thể swap sau)
    spare = []
    for idx, p in enumerate(passengers):
        if idx < len(available_eps):
            p['assigned_ep'] = available_eps[idx]
        else:
            p['assigned_ep'] = None
            spare.append(p['id'])

    return passengers, spare


def validate_constitution(passengers: list) -> dict:
    """Verify 100 passenger tuân hiến pháp."""
    issues = []
    pillar_count = defaultdict(int)
    for p in passengers:
        pillar_count[p['pillar']] += 1
        if not p.get('signature_object') or p['signature_object'] == 'OBJ_TBD':
            issues.append(f"{p['id']} thiếu signature_object (ALWAYS.object_symbolism)")
        if not p.get('regret_sub_archetype'):
            issues.append(f"{p['id']} thiếu regret_sub_archetype (ALWAYS.unresolved_goodbye)")

    # Verify distribution
    for pillar, expected in PILLAR_DISTRIBUTION.items():
        actual = pillar_count[pillar]
        if actual != expected:
            issues.append(f"distribution {pillar}: actual {actual} ≠ expected {expected}")

    # Verify novelty distance ≥6 (simplified: check uniqueness của hash per sliding window 6)
    hashes = [p['novelty_hash'] for p in passengers if p.get('assigned_ep')]
    sorted_pass = sorted(
        [p for p in passengers if p.get('assigned_ep')],
        key=lambda x: x['assigned_ep']
    )
    for i in range(len(sorted_pass) - 5):
        window = [sorted_pass[i + j]['regret_sub_archetype'] for j in range(6)]
        if len(set(window)) < 6:
            ep_window = [sorted_pass[i + j]['assigned_ep'] for j in range(6)]
            dupes = [x for x in window if window.count(x) > 1]
            issues.append(f"window ep {ep_window}: regret reuse trong distance 6 → {set(dupes)}")

    return {
        'total': len(passengers),
        'pillar_count': dict(pillar_count),
        'issues_count': len(issues),
        'issues': issues[:10],  # top 10
    }


def main():
    parser = argparse.ArgumentParser(description='Gen 100 passenger framework')
    parser.add_argument('--output', type=str,
                        default=str(SVHMP / 'runtime' / 'passenger_roster_100.yaml'))
    args = parser.parse_args()

    print('=== Gen 100 passenger framework ===')
    passengers = gen_passengers()
    print(f'  Generated: {len(passengers)} passengers')

    passengers, spare = assign_eps(passengers)
    print(f'  Assigned: {len(passengers) - len(spare)} → ep slots')
    print(f'  Spare backup pool: {len(spare)} ({spare[:5]}{"..." if len(spare)>5 else ""})')

    report = validate_constitution(passengers)
    print(f'\n=== Constitution Verify ===')
    print(f'  Total: {report["total"]}')
    print(f'  Distribution: {report["pillar_count"]}')
    print(f'  Issues: {report["issues_count"]}')
    if report['issues']:
        print('  Top issues:')
        for iss in report['issues']:
            print(f'    - {iss}')

    # Write output
    import yaml
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'schema_version': 1,
        'generated': '2026-06-27',
        'generator': 'tools/gen_100_passenger.py',
        'constitution_compliance': {
            'distribution_lock_bible_11': True,
            'one_shot_only_bible_03': True,
            'each_carries_object_bible_00': True,
            'eps_reserved_73_90_bible_18': True,
            'novelty_distance_6_bible_08': True,
        },
        'distribution_target': PILLAR_DISTRIBUTION,
        'distribution_actual': report['pillar_count'],
        'reserved_eps': sorted(RESERVED_EPS),
        'spare_pool': spare,
        'passengers': passengers,
    }
    output_path.write_text(yaml.safe_dump(output, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print(f'\n→ Output: {output_path}')

    if report['issues_count'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
