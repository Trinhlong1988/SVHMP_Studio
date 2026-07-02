"""SVHMP R60 — Auto-fix short-syllable EOL (sentence ≤3 words ending banned).

Strategy: PAD bằng 1-2 từ tự nhiên giữ rhythm horror nhưng đủ length TTS prosody.

Mapping:
  "im." → "im lặng."
  "đi." → "đi xa."
  "ra." → "ra ngoài."
  "qua." → "qua đó."
  ...

Conservative: chỉ fix sentence ≤3 words exact pattern.
"""
import re
import sys
import shutil
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(__file__).resolve().parents[1]

PAD_MAP = {
    'im': 'im lặng', 'lặng': 'lặng yên', 'rơi': 'rơi xuống',
    'đi': 'đi xa', 'ra': 'ra ngoài', 'qua': 'qua đó',
    'lui': 'lui ra', 'tan': 'tan ra', 'nhỏ': 'rất nhỏ',
    'to': 'rất to', 'lên': 'lên cao', 'xuống': 'xuống dưới',
    'vào': 'vào trong', 'đó': 'ở đó', 'đây': 'ở đây',
    'khẽ': 'khẽ thôi', 'nhẹ': 'nhẹ nhàng', 'mau': 'mau lên',
    'chậm': 'chậm lại', 'mềm': 'mềm mại', 'cứng': 'cứng đờ',
    'nóng': 'nóng bừng', 'lạnh': 'lạnh buốt', 'vắng': 'vắng tanh',
    'đông': 'đông đúc', 'xa': 'rất xa', 'gần': 'gần lại',
    'cao': 'cao vút', 'thấp': 'thấp xuống', 'sáng': 'sáng lên',
    'tối': 'tối đen', 'hết': 'hết rồi', 'rồi': 'rồi đó',
    'thôi': 'thôi vậy', 'nữa': 'nữa thôi', 'mãi': 'mãi mãi',
    'liền': 'liền sau', 'ngay': 'ngay lúc đó', 'dày': 'dày đặc',
    'mỏng': 'mỏng tang', 'khô': 'khô cong', 'ướt': 'ướt sũng',
}

def fix_episode(text):
    """Find sentences ≤3 words ending in banned word, pad them."""
    changes = []
    new_text = text

    # Pattern: capture sentence (1-3 words) ending with banned + EOL boundary
    # Sentence boundary: . ! ? — \n + capital
    for word, replacement in PAD_MAP.items():
        # Sentence patterns: "Word. " / "Word Word. " / "Word Word Word."
        # Conservative: match standalone sentence with banned word at end + ≤3 words total
        # Use lookahead for boundary + lookbehind for sentence start
        pattern = re.compile(
            rf'(?:(?<=^)|(?<=\.\s)|(?<=\?\s)|(?<=!\s)|(?<=—\s))((?:\w+\s+){{1,2}}){re.escape(word)}(?=[.!?])',
            re.UNICODE | re.MULTILINE
        )
        for m in pattern.finditer(new_text):
            changes.append({
                'word': word,
                'replacement': replacement,
                'context': m.group(0),
            })
        new_text = pattern.sub(rf'\g<1>{replacement}', new_text)

    return new_text, changes

def main():
    apply = '--apply' in sys.argv
    print("=" * 70)
    print(f"R60 AUTO-FIX — Short EOL pad | Mode: {'APPLY' if apply else 'DRY-RUN'}")
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
            print(f"EP{n:02d}: {len(changes)} pads")
            for c in changes[:3]:
                print(f"  '{c['context']}' → pad '{c['word']}' → '{c['replacement']}'")
            if apply:
                shutil.copy2(p, p.with_suffix('.md.bak.R60'))
                p.write_text(new_text, encoding='utf-8')
    print(f"\nTotal: {total} pads")
    if apply:
        print("APPLIED (backups: *.bak.R60)")

if __name__ == '__main__':
    main()
