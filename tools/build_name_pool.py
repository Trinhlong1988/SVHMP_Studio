"""Build Vietnamese name pool từ data/vietnamese_names_extended.yaml.

Constraint (bible/23 + Mr.Long 27/6):
- Mỗi WORD (syllable) DUY NHẤT 1 lần across all 100 names
- Exclude forbidden ("Nam", "Tài" — recurring CHAR collision)
- 2 âm tiết per name (đẹp, văn học)

Output: tools/name_pool.yaml (load by gen_100_passenger.py)
"""
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
DB_PATH = SVHMP / 'data' / 'vietnamese_names_extended.yaml'
OUT = Path(__file__).parent / 'name_pool.yaml'


def extract_syllables(db: dict, gender: str) -> list:
    """Extract distinct syllables từ db, dedup theo syl."""
    key = f'{gender}_syllables'
    cats = db.get(key, {})
    all_syls = []
    for cat_name, syls in cats.items():
        for entry in syls:
            all_syls.append(entry['syl'])
    return list(dict.fromkeys(all_syls))  # preserve order, dedup


def pair_pool(syl_bank: list, count: int, exclude_words: set) -> tuple:
    """Pair adjacent syllables ensuring no word reused. Return (pool, used_words)."""
    avail = [s for s in syl_bank if s not in exclude_words]
    pool = []
    used = set(exclude_words)
    i = 0
    while i < len(avail) - 1 and len(pool) < count:
        s1 = avail[i]
        s2 = avail[i + 1]
        if s1 in used or s2 in used or s1 == s2:
            i += 1
            continue
        pool.append(f'{s1} {s2}')
        used.update([s1, s2])
        i += 2  # skip used syllables
    return pool, used


def main():
    import yaml
    if not DB_PATH.exists():
        print(f'ERROR: database missing {DB_PATH}')
        sys.exit(1)

    db = yaml.safe_load(DB_PATH.read_text(encoding='utf-8'))

    # Forbidden từ db
    forbidden = {item['syl'] for item in db.get('forbidden_words', [])}
    print(f'Forbidden: {forbidden}')

    # Extract syllables
    fem_syls = extract_syllables(db, 'feminine')
    mas_syls = extract_syllables(db, 'masculine')
    print(f'FEM bank size: {len(fem_syls)}')
    print(f'MAS bank size: {len(mas_syls)}')

    # B35 fix: Build MAS pool FIRST (smaller bank → consume first), then NU.
    # Reason: FEM bank lớn 100+, MAS bank 60-100 → MAS first avoid overlap conflict.
    nam_pool, used_nam = pair_pool(mas_syls, 50, forbidden)
    print(f'NAM pool: {len(nam_pool)} names')

    # Build NU pool — exclude MAS đã dùng + forbidden
    nu_pool, used_nu = pair_pool(fem_syls, 50, used_nam | forbidden)
    print(f'NU pool: {len(nu_pool)} names')

    # Verify global uniqueness
    all_words = []
    for name in nu_pool + nam_pool:
        all_words.extend(name.split())
    dup = {k: v for k, v in Counter(all_words).items() if v > 1}
    print(f'Global word duplicates: {len(dup)}')
    if dup:
        print(f'  {dup}')

    # Verify forbidden không có trong pool
    forbidden_violations = []
    for name in nu_pool + nam_pool:
        for word in name.split():
            if word in forbidden:
                forbidden_violations.append((name, word))
    print(f'Forbidden violations: {len(forbidden_violations)}')

    # Output
    out_data = {
        'schema_version': 2,
        'rule_source': 'bible/23_passenger_naming.yaml',
        'database_source': 'data/vietnamese_names_extended.yaml',
        'lock_date': '2026-06-27',
        'count_nu': len(nu_pool),
        'count_nam': len(nam_pool),
        'total_unique_names': len(nu_pool) + len(nam_pool),
        'global_word_uniqueness_verified': len(dup) == 0,
        'forbidden_collision_verified': len(forbidden_violations) == 0,
        'NAMES_NU': nu_pool,
        'NAMES_NAM': nam_pool,
    }
    OUT.write_text(yaml.safe_dump(out_data, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print(f'\n→ Output: {OUT}')
    print(f'NU sample: {nu_pool[:5]}')
    print(f'NAM sample: {nam_pool[:5]}')


if __name__ == '__main__':
    main()
