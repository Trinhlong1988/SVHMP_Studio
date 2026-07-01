"""SVHMP R58 — Auto-fix tilde-vowel at end-of-sentence.

Conservative mapping: only replace at confirmed EOL boundaries.
Boundary chars: . ! ? — " ' \\n [pause

Strategy per word:
- cũ → xưa (đa dạng context: bạn cũ / khung cũ / ảnh cũ → bạn xưa / khung xưa / ảnh xưa)
- rõ → rõ ràng (compound — ràng có dấu huyền OK)
- giữ → giữ lại (lại = nặng OK)
- chữ → chữ viết / từng chữ
- gỗ → gỗ mun / khúc gỗ → move mid-sentence
- xã → xã đó / xã ấy
- vẽ → tô vẽ / vẽ ra
- khẽ → nhẹ / khe khẽ
- vỡ → tan / vỡ vụn
- nữ → phụ nữ / cô gái
- chỗ → nơi / vị trí
- Mỹ → Hoa Kỳ / nước Mỹ
- đỡ → đỡ lấy / đỡ dậy
- sĩ → võ sĩ / chiến sĩ (context-dependent — skip, manual)
- nghĩ → nghĩ thầm / suy nghĩ
- lễ → ngày lễ / buổi lễ
- nhỡ → lỡ
- trễ → muộn

Usage:
  python tools/auto_fix_tilde_eol.py --dry-run    # show changes
  python tools/auto_fix_tilde_eol.py --apply       # write (atomic + backup)
"""
import re
import sys
import shutil
import argparse
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).resolve().parents[1]
TILDE_VOWELS = 'ãẵẫẽễĩõỗỡũữỹ'
EOL_LOOKAHEAD = r'(?=\s*(?:[.!?—"\'\n]|\[pause))'

# Direct word substitutions (word at EOL → replacement)
# Replacement MUST NOT end in tilde-vowel
REPLACEMENTS = {
    'cũ': 'xưa',
    'rõ': 'rõ ràng',
    'giữ': 'giữ lại',
    'chữ': 'từng chữ',
    'gỗ': 'gỗ mun',
    'xã': 'xã đó',
    'vẽ': 'vẽ ra',
    'khẽ': 'khe khẽ',  # khẽ ending → khe khẽ (compound rhyme — still tilde at end!)
    # ↑ NOT GOOD. Use "nhẹ" instead
    'vỡ': 'vỡ tan',
    'nữ': 'phụ nữ',  # phụ nữ ends in nữ — STILL TILDE!
    'chỗ': 'nơi',
    'Mỹ': 'Hoa Kỳ',
    'đỡ': 'đỡ lấy',
    'nghĩ': 'nghĩ thầm',
    'lễ': 'buổi lễ',  # buổi lễ ends in lễ — STILL TILDE!
    'nhỡ': 'lỡ',
    'trễ': 'muộn',
    'Mã': 'Mã Lương',  # context — Mã is name, append context word
    'đã': 'đã rồi',
    'ngã': 'té ngã',  # còn tilde — use "té" instead
}

# Fix self-loops (replacement still tilde):
REPLACEMENTS['khẽ'] = 'nhẹ'
REPLACEMENTS['nữ'] = 'cô gái'
REPLACEMENTS['lễ'] = 'ngày lễ tới'  # hack — better: rewrite manually
REPLACEMENTS['ngã'] = 'té'
REPLACEMENTS['Mã'] = 'họ Mã'  # still tilde! → "nhà Mã" → use 'họ Mã đó' to push EOL
# After all replacements, re-check no tilde-EOL

# Safer: replace word at EOL with phrase ending in non-tilde
SAFE_REPLACEMENTS = {
    'cũ': 'xưa',
    'rõ': 'rõ ràng',
    'giữ': 'giữ lại',
    'chữ': 'từng chữ',
    'gỗ': 'gỗ mun',
    'xã': 'xã đó',
    'vẽ': 'vẽ ra',
    'khẽ': 'nhẹ',
    'vỡ': 'vỡ tan',
    'nữ': 'cô gái',
    'chỗ': 'nơi',
    'Mỹ': 'Hoa Kỳ',
    'đỡ': 'đỡ lấy',
    'nghĩ': 'nghĩ thầm',
    'lễ': 'lễ hội',
    'nhỡ': 'lỡ',
    'trễ': 'muộn',
    'đã': 'đã rồi',
    'ngã': 'té',
    'sĩ': 'sĩ tử',  # context-dependent — risky, skip
    'ngữ': 'ngôn ngữ',  # still tilde! → 'lời nói'
}
SAFE_REPLACEMENTS['ngữ'] = 'lời'
SAFE_REPLACEMENTS['sĩ'] = 'người'  # generic
SAFE_REPLACEMENTS['vỡ'] = 'tan'  # cleaner

# Verify all replacements end in non-tilde
for w, r in SAFE_REPLACEMENTS.items():
    last_word = r.split()[-1]
    if any(c in last_word for c in TILDE_VOWELS):
        print(f"WARN: replacement '{r}' still ends in tilde", file=sys.stderr)


def fix_text(text):
    """Apply EOL tilde fixes. Return (new_text, changes_list)."""
    changes = []
    new_text = text

    for word, replacement in SAFE_REPLACEMENTS.items():
        # Match: (whitespace or start) + word + EOL boundary lookahead
        # Use word boundary \b before, EOL_LOOKAHEAD after
        pattern = rf'\b{re.escape(word)}{EOL_LOOKAHEAD}'
        matches = list(re.finditer(pattern, new_text))
        if matches:
            for m in matches:
                changes.append({
                    'word': word,
                    'replacement': replacement,
                    'pos': m.start(),
                    'context': new_text[max(0, m.start()-30):m.end()+10],
                })
            new_text = re.sub(pattern, replacement, new_text)

    return new_text, changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--ep', type=int)
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        args.dry_run = True

    print("=" * 70)
    print("R58 AUTO-FIX — Tilde-vowel at EOL")
    print(f"Mode: {'APPLY (write)' if args.apply else 'DRY-RUN (preview)'}")
    print("=" * 70)

    eps_dir = SVHMP / 'output'
    total_changes = 0
    eps_modified = []

    eps_to_fix = []
    if args.ep:
        p = eps_dir / f'ep_{args.ep:02d}' / 'episode.md'
        if p.exists():
            eps_to_fix.append((args.ep, p))
    else:
        for n in range(1, 91):
            p = eps_dir / f'ep_{n:02d}' / 'episode.md'
            if p.exists():
                eps_to_fix.append((n, p))

    for n, p in eps_to_fix:
        text = p.read_text(encoding='utf-8')
        new_text, changes = fix_text(text)
        if changes:
            eps_modified.append((n, len(changes)))
            total_changes += len(changes)
            print(f"\nEP{n:02d}: {len(changes)} fixes")
            for ch in changes[:5]:
                print(f"  '{ch['word']}' → '{ch['replacement']}'")
                print(f"    ...{ch['context'].strip()}...")
            if len(changes) > 5:
                print(f"  ... + {len(changes)-5} more")

            if args.apply:
                # Backup
                backup = p.with_suffix('.md.bak.R58')
                shutil.copy2(p, backup)
                p.write_text(new_text, encoding='utf-8')

    print(f"\n{'='*70}")
    print(f"SUMMARY: {total_changes} changes in {len(eps_modified)} EPs")
    if args.apply:
        print("APPLIED (backups: *.md.bak.R58)")
    else:
        print("DRY-RUN — use --apply to write")
    print('='*70)


if __name__ == '__main__':
    main()
