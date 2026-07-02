"""SVHMP — Vary bell + passenger entry templates (R53 enforcement).

Bell variants (max 15/50 same):
- "Chuông xe ngân. Một tiếng. Tan."          (current default)
- "Tiếng chuông ngân nhẹ. Một hồi. Lặng."
- "Chuông xe rung khẽ. Vang một nhịp. Tan."
- "Một tiếng chuông. Ngắn. Tan trong sương."
- "Chuông xe vọng. Nhịp đơn. Im."

Entry variants:
- "bước lên xe. Đi qua hàng ghế đầu"  (current default)
- "lên xe. Đi xuống lối giữa"
- "lên bậc xe. Đi đến hàng ghế giữa"
- "vào xe. Đi qua mấy hàng ghế trước"

Rotate per EP (EP11-50, skip EP01-10 golden).

Usage: python tools/vary_bell_entry.py [--dry-run]
"""
import re
import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).resolve().parents[1]

BELL_VARIANTS = [
    "Chuông xe ngân. Một tiếng. Tan.",
    "Tiếng chuông ngân nhẹ. Một hồi. Lặng.",
    "Chuông xe rung khẽ. Vang một nhịp. Tan.",
    "Một tiếng chuông. Ngắn. Tan trong sương.",
    "Chuông xe vọng. Nhịp đơn. Im.",
]

ENTRY_VARIANTS = [
    "bước lên xe. Đi qua hàng ghế đầu",
    "lên xe. Đi xuống lối giữa",
    "lên bậc xe. Đi đến hàng ghế giữa",
    "vào xe. Đi qua mấy hàng ghế trước",
]

def vary_ep(ep_num, dry_run=False):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists():
        return 0
    text = p.read_text(encoding='utf-8')

    # Bell rotation (skip EP01-10)
    bell_old = "Chuông xe ngân. Một tiếng. Tan."
    if bell_old in text and ep_num >= 11:
        bell_idx = (ep_num - 11) % len(BELL_VARIANTS)
        bell_new = BELL_VARIANTS[bell_idx]
        if bell_new != bell_old:
            text = text.replace(bell_old, bell_new, 1)

    # Entry rotation
    entry_old = "bước lên xe. Đi qua hàng ghế đầu"
    if entry_old in text and ep_num >= 11:
        entry_idx = (ep_num - 11) % len(ENTRY_VARIANTS)
        entry_new = ENTRY_VARIANTS[entry_idx]
        if entry_new != entry_old:
            text = text.replace(entry_old, entry_new, 1)

    if text != p.read_text(encoding='utf-8'):
        if not dry_run:
            p.write_text(text, encoding='utf-8')
        print(f"  EP{ep_num:02d}: varied (bell variant {bell_idx if bell_old in p.read_text(encoding='utf-8') else 'kept'}, entry {entry_idx if entry_old in p.read_text(encoding='utf-8') else 'kept'})")
        return 1
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    total = 0
    for n in range(11, 51):
        total += vary_ep(n, args.dry_run)
    print(f"\nTotal EPs varied: {total}/40")

if __name__ == '__main__':
    main()
