"""SVHMP — Audit STORY MODE: hồi tưởng ám ảnh vs kể lể chronological (R56+R57).

Mr.Long 28/6 CORE FEEDBACK: "là truyện đạt hồi tưởng, logic ám ảnh tâm linh
                              KHÔNG miên man kể lể"

Detection:
1. "Năm em/tôi X tuổi" count per EP (>3 = chronological recap)
2. Resume facts: "lương X triệu" / "công ty Y" / "vị trí Z" (>2 = show resume)
3. Year-by-year breakdown ratio in REVEAL
4. Generation depth (bố mẹ + ông bà + cô chú + anh chị em) — > 2 generations = sprawl
5. Sensory anchor presence (vật/âm/mùi specific) — must have ≥1 vivid sensory per vignette
6. Vignette count (target 3-5)
7. Death scene detail (acceptable 1-2 sentences, NOT extended)
8. Tonight purpose clear (vì sao đêm nay)

Usage: python tools/audit_story_mode.py [--ep N]
"""
import re
import sys
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

def strip_meta(text):
    return re.sub(r'```.*?```', '', text, flags=re.DOTALL)

def extract_reveal(text):
    m = re.search(r'#+\s*REVEAL.*?(?=#+\s*(PAYOFF|CLIFFHANGER)|$)', text, re.IGNORECASE | re.DOTALL)
    return m.group() if m else ''

def audit_story_mode(text):
    """Return list of (check, value, severity)."""
    reveal = extract_reveal(strip_meta(text))
    if not reveal:
        return [('no_reveal', 0, 'HIGH')]

    results = []

    # 1. Chronological year mentions ("Năm em/tôi X tuổi")
    year_age = re.findall(r'[Nn]ăm (?:em|tôi)\s+(?:[\w\s]{1,20})?\s*tuổi', reveal)
    results.append(('R57.1 year-age mentions', len(year_age), 'HIGH' if len(year_age) > 5 else 'MEDIUM' if len(year_age) > 3 else 'OK'))

    # 2. Resume facts (lương/công ty/vị trí)
    resume_patterns = [
        r'lương[^.]*triệu',
        r'(?:phó|trưởng|giám đốc) phòng',
        r'công ty (?:cổ phần|trách nhiệm|TNHH|tư nhân|nhà nước|xây dựng|may|cảng|hóa chất|du lịch|công nghệ)',
        r'mức lương',
        r'(?:tốt nghiệp|đậu) (?:Đại học|đại học|cao đẳng) \w+',
    ]
    resume_count = sum(len(re.findall(p, reveal)) for p in resume_patterns)
    results.append(('R57.2 resume facts (lương/công ty/vị trí)', resume_count, 'HIGH' if resume_count > 3 else 'MEDIUM' if resume_count > 2 else 'OK'))

    # 3. Generation depth (count distinct family member words)
    fam_words = ['bố', 'mẹ', 'ông', 'bà', 'cô', 'chú', 'bác', 'cậu', 'dì', 'anh', 'chị', 'em']
    unique_fam = sum(1 for w in fam_words if reveal.lower().count(' '+w+' ') > 2)  # mentioned 3+ times
    results.append(('R57.3 family depth (>3 mentions/word)', unique_fam, 'MEDIUM' if unique_fam > 4 else 'OK'))

    # 4. Sensory anchor presence
    sensory_words = ['tay run', 'tay lạnh', 'tay ấm', 'mùi', 'tiếng', 'ánh', 'bóng', 'gió', 'mưa', 'sương']
    sensory_count = sum(reveal.lower().count(w) for w in sensory_words)
    results.append(('R57.4 sensory anchors', sensory_count, 'OK' if sensory_count >= 3 else 'MEDIUM'))

    # 5. Vignette count (count separate "scene" blocks via [pause:Xms])
    pauses = re.findall(r'\[pause:\d+ms\]', reveal)
    results.append(('R57.5 pause blocks (vignettes)', len(pauses), 'OK' if 3 <= len(pauses) <= 8 else 'LOW'))

    # 6. Linear time chain detection ("Năm X — Năm Y — Năm Z" consecutive)
    sentences = re.split(r'[.!?]\s+', reveal)
    year_chain = 0
    cur_chain = 0
    for s in sentences:
        if re.match(r'^[Nn]ăm', s.strip()):
            cur_chain += 1
            year_chain = max(year_chain, cur_chain)
        else:
            cur_chain = 0
    results.append(('R57.6 consecutive year-start sentences', year_chain, 'HIGH' if year_chain >= 4 else 'MEDIUM' if year_chain >= 3 else 'OK'))

    # 7. Tonight purpose clear ("đêm nay" mention in last 200 words)
    last_part = reveal[-500:]
    tonight_clear = 'đêm nay' in last_part.lower() or 'tối nay' in last_part.lower()
    results.append(('R57.7 tonight purpose stated', 1 if tonight_clear else 0, 'OK' if tonight_clear else 'MEDIUM'))

    # 8. Death scene length — should be 1-2 sentences, not extended
    death_match = re.search(r'(?:mất|chết|đi)[^.]*\.', reveal, re.IGNORECASE)
    results.append(('R57.8 death scene present', 1 if death_match else 0, 'OK' if death_match else 'MEDIUM'))

    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    print("="*70)
    print("STORY MODE AUDIT R56+R57 — hồi tưởng vs kể lể")
    print("="*70)

    eps = {}
    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if p.exists():
            eps[n] = p.read_text(encoding='utf-8')

    if args.ep:
        eps = {args.ep: eps[args.ep]} if args.ep in eps else {}

    all_high_count = 0
    chronological_eps = []
    resume_eps = []

    for n in sorted(eps.keys()):
        results = audit_story_mode(eps[n])
        high = sum(1 for _, _, s in results if s == 'HIGH')
        med = sum(1 for _, _, s in results if s == 'MEDIUM')
        all_high_count += high

        if high > 0:
            year_age = next((v for c, v, _ in results if 'year-age' in c), 0)
            resume = next((v for c, v, _ in results if 'resume facts' in c), 0)
            year_chain = next((v for c, v, _ in results if 'year-start' in c), 0)

            if year_age > 5 or year_chain >= 4:
                chronological_eps.append((n, year_age, year_chain))
            if resume > 3:
                resume_eps.append((n, resume))

            if not args.summary:
                print(f"\n  EP{n:02d}: HIGH={high} MED={med}")
                for c, v, s in results:
                    if s in ('HIGH', 'MEDIUM'):
                        sym = '🔴' if s == 'HIGH' else '🟡'
                        print(f"    {sym} {c}: {v}")

    print(f"\n{'='*70}\nSUMMARY\n{'='*70}")
    print(f"Total HIGH issues: {all_high_count}")
    print(f"Chronological recap EPs: {len(chronological_eps)}")
    for n, ya, yc in chronological_eps[:10]:
        print(f"  EP{n:02d}: {ya} year-age + {yc} consecutive year-start")
    print(f"Resume mode EPs: {len(resume_eps)}")
    for n, r in resume_eps[:10]:
        print(f"  EP{n:02d}: {r} resume facts")

    import json
    out = SVHMP / 'runtime' / 'audit_story_mode_report.json'
    out.write_text(json.dumps({
        'total_high': all_high_count,
        'chronological_eps': chronological_eps,
        'resume_eps': resume_eps,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
