"""SVHMP — Cleanup duplicated phrases left from vary_templates.py rewrite.

Fix patterns like:
- 'ven sông đường ven sông' → 'ven sông'
- 'hàng cây bên đường.Đèn pha quét lên' → 'hàng cây bên đường. Đèn pha quét lên' + dedupe
- 'qua đoạn đường ven đường ven' → 'qua đoạn đường ven'
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).resolve().parents[1]

def cleanup(text):
    changes = 0
    # Pattern 1: duplicate "ven X đường ven X" → "ven X"
    new_text, n = re.subn(r'ven\s+\w+\s+đường ven\s+', 'ven ', text)
    if n: changes += n; text = new_text

    # Pattern 1b: "đoạn ven sông đường ven sông X" → "đoạn ven sông X"
    new_text, n = re.subn(r'đoạn ven\s+(\w+)\s+đường ven\s+(\w+)', r'đoạn ven \2', text)
    if n: changes += n; text = new_text

    # Pattern 2: "qua đoạn đường ven đường ven" → "qua đoạn đường ven"
    new_text, n = re.subn(r'đường ven\s+(?:đường\s+)?ven\s+', 'đường ven ', text)
    if n: changes += n; text = new_text

    # Pattern 3: missing space "bên đường.Đèn pha" → "bên đường. Đèn pha"
    new_text, n = re.subn(r'\.([A-ZĐ])', r'. \1', text)
    if n: changes += n; text = new_text

    # Pattern 4: "Đèn pha [X]. Đèn pha [Y]" consecutive same opener — keep first only
    new_text, n = re.subn(
        r'(Đèn pha [^.]+\.)\s*Đèn pha [^.]+\.',
        r'\1',
        text
    )
    if n: changes += n; text = new_text

    # Pattern 5: "ven [place] đường ven" wrap → "ven [place]"
    new_text, n = re.subn(r'ven\s+(\w+)\s+đường\s+ven', r'ven \1', text)
    if n: changes += n; text = new_text

    return text, changes

def main():
    total = 0
    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists(): continue
        original = p.read_text(encoding='utf-8')
        new_text, changes = cleanup(original)
        if changes > 0:
            p.write_text(new_text, encoding='utf-8')
            print(f"  EP{n:02d}: {changes} cleanup")
            total += changes
    print(f"\nTotal cleanup: {total}")

if __name__ == '__main__':
    main()
