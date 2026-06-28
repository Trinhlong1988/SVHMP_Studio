"""SVHMP R61 — Auto-fix short-syllable START (Đêm./Hôm./Ngày. etc).

Strategy: PREPEND filler word ("Vào ", "Trong ") để TTS không cụt prosody mở đầu.

Conservative: chỉ fix sentences ≤5 words starting with banned + short next.
"""
import re
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

PREFIX_MAP = {
    'Đêm': 'Vào đêm',
    'Hôm': 'Vào hôm',
    'Ngày': 'Vào ngày',
    'Năm': 'Vào năm',
    'Sáng': 'Vào sáng',
    'Chiều': 'Vào chiều',
    'Tối': 'Vào tối',
    'Mưa': 'Trận mưa',
    'Gió': 'Cơn gió',
    'Sương': 'Lớp sương',
    'Lúc': 'Vào lúc',
    'Khi': 'Vào khi',
}

def fix_episode(text):
    changes = []
    new_text = text
    lines = new_text.split('\n')
    for i, line in enumerate(lines):
        if not line.strip() or line.startswith('#') or line.startswith('[') or line.startswith('---') or line.startswith('|'):
            continue
        # Split into sentences by . ! ?
        sentences = re.split(r'(?<=[.!?])\s+', line)
        new_sents = []
        modified = False
        for s in sentences:
            s_strip = s.strip()
            if not s_strip:
                new_sents.append(s)
                continue
            words = s_strip.split()
            if len(words) > 5:
                new_sents.append(s)
                continue
            # Get first word skip quotes
            m = re.match(r'^([""\'—\s]*)(\w+)\b', s_strip)
            if m and m.group(2) in PREFIX_MAP:
                first = m.group(2)
                # Check next word is short
                rest = s_strip[m.end():].strip()
                next_word = rest.split()[0] if rest else ''
                if next_word and len(next_word) <= 4:
                    # Replace "Đêm" → "Vào đêm" + lowercase the original
                    replacement = PREFIX_MAP[first]
                    new_s = s_strip[:m.start(2)] + replacement + ' ' + first.lower() + s_strip[m.end():]
                    # Simpler: replace first word with prefix + lowercase
                    new_s = replacement + s_strip[m.end():]
                    changes.append({
                        'word': first,
                        'replacement': replacement,
                        'context': s_strip[:50],
                    })
                    new_sents.append(new_s)
                    modified = True
                    continue
            new_sents.append(s)
        if modified:
            lines[i] = ' '.join(new_sents)
    new_text = '\n'.join(lines)
    return new_text, changes

def main():
    apply = '--apply' in sys.argv
    print("=" * 70)
    print(f"R61 AUTO-FIX — Short START prefix | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    print("=" * 70)

    total = 0
    for n in range(1, 91):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        new_text, changes = fix_episode(text)
        if changes:
            total += len(changes)
            print(f"EP{n:02d}: {len(changes)} prefix")
            for c in changes[:3]:
                print(f"  '{c['word']}...' → '{c['replacement']}...' | {c['context']}")
            if apply:
                shutil.copy2(p, p.with_suffix('.md.bak.R61'))
                p.write_text(new_text, encoding='utf-8')
    print(f"\nTotal: {total} prefix")
    if apply:
        print("APPLIED (backups: *.bak.R61)")

if __name__ == '__main__':
    main()
