"""Post-rotation verification — R88 mandatory.

Checks:
1. Double preposition / clause (trong trong, vào lên, của của, etc.)
2. Hoàng Phê context (death-context words on alive characters)
3. R67/R76 tail re-scan (post-rotation may break tail)
4. Vietnamese grammar (incomplete clauses)

Exit 1 if violation. Block render.
"""
import json, re, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

LEX_PATH = Path(__file__).parent.parent / 'data' / 'vnsl_lexicon.json'
try:
    LEX = json.load(open(LEX_PATH, encoding='utf-8'))
    DEATH_CTX = set(LEX.get('_forbidden_patterns', {}).get('death_context_only', []))
except:
    DEATH_CTX = {'thở hắt ra', 'hấp hối', 'tắt thở', 'ngấp ngoái', 'đột tử', 'lìa đời', 'trút hơi thở cuối', 'qua đời', 'khuất núi'}

# Double preposition / particle patterns
DOUBLE_PATTERNS = [
    r'\btrong\s+trong\b',
    r'\btrong\s+vào\b',
    r'\bvào\s+vào\b',
    r'\bvào\s+lên\b',
    r'\bvào\s+trong\b',
    r'\blên\s+lên\b',
    r'\blên\s+trên\b',
    # r'\btừ\s+từ\b',  # reduplication legitimate (= slowly)
    r'\bvới\s+với\b',
    r'\bvà\s+và\b',
    r'\bcủa\s+của\b',
    r'\bcho\s+cho\b',
    r'\bở\s+ở\b',
    r'\bnhưng\s+nhưng\b',
    r'\bcùng\s+cùng\b',
    r'\bbỗng\s+bỗng\b',
    r'\bchợt\s+chợt\b',
    r'\bđột\s+đột\b',
    r'\bvừa\s+vừa\b',
]

# R67/R76 tail wordlists
STOP_TAIL = {'suốt','khuất','biết','đứt','tắt','thắt','ngắt','cắt','kịch','khắc','tách','đập','thắp','tắp','được'}
OPEN_VOWEL_TAIL = {'nữa','mãi','ngày','tay','dài','ai','mai','đời','ơi','trời','vời','khơi','đâu','sau','lâu','đau','xa','ra','qua','thưa','mưa','vừa','rồi','chơi','trôi','tựa','lúa','đầy','cô','cảm','khảm','lìm','tâm','nay','cuối','người'}

def audit(spec_path):
    d = json.load(open(spec_path, encoding='utf-8'))
    chunks = d.get('sentences', d.get('chunks', []))
    issues = []

    for i, c in enumerate(chunks):
        text = c.get('text', '') if isinstance(c, dict) else c

        # 1. Double prepositions
        for pat in DOUBLE_PATTERNS:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                issues.append(('R88.dup_prep', i, f'"{m.group()}" in chunk'))

        # 2. Death-context (assume Khải Phong/Hà/Cô/Anh alive)
        for word in DEATH_CTX:
            if word in text.lower():
                # Skip if explicit death-context (Hà died context)
                if any(ctx in text.lower() for ctx in ['hà mất', 'hà ra đi', 'hà đã mất', 'qua đời']):
                    continue
                issues.append(('R87.death_ctx', i, f'"{word}" — death-context word'))

        # 3. R67/R76 tail
        sents = [s.strip() for s in re.split(r'[.!?…]', text) if s.strip()]
        if sents:
            last_sent = sents[-1].strip().strip('"').strip(',').strip("'")
            words = last_sent.split()
            if words:
                lw = words[-1].lower().strip('.,!?…"\'')
                if lw in STOP_TAIL:
                    issues.append(('R67.tail', i, f'stop-consonant tail "{lw}"'))
                if lw in OPEN_VOWEL_TAIL:
                    issues.append(('R76.tail', i, f'open-vowel tail "{lw}"'))

        # 4. Grammar: incomplete clause patterns
        # Tail comma without continuation (only if last char is ',')
        if text.rstrip().endswith(','):
            issues.append(('R88.tail_comma', i, 'tail ends with comma (incomplete)'))

    return issues

def main():
    if len(sys.argv) < 2:
        # Audit all sections
        _wd = os.environ.get('SVHMP_WORKDIR', os.path.expanduser(r'~/Desktop/SVHMP_v10_workdir'))
        if not os.path.isdir(_wd):
            sys.exit(f"[SKIP] Legacy workdir khong ton tai: {_wd} — set env SVHMP_WORKDIR de chay, hoac truyen spec path lam tham so.")
        os.chdir(_wd)
        paths = sorted([p for p in glob.glob('spec_ep01_section_*.json') if '_v' not in p and 'backup' not in p and 'old' not in p])
    else:
        paths = sys.argv[1:]

    total_violations = 0
    for p in paths:
        issues = audit(p)
        sec = os.path.basename(p).replace('spec_ep01_section_', '').replace('.json', '')
        if issues:
            print(f"\n=== {sec} ===")
            for rule, ch, msg in issues:
                print(f"  [{rule}] ch{ch}: {msg}")
            total_violations += len(issues)
        else:
            print(f"\n=== {sec} === CLEAN")

    print(f"\n{'='*50}\nTOTAL VIOLATIONS: {total_violations}")
    if total_violations > 0:
        print("BLOCK render. Fix all violations first.")
        sys.exit(1)
    print("PASS — safe to render")

if __name__ == '__main__':
    main()
