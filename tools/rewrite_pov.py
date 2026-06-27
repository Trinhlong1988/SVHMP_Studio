"""SVHMP — Rewrite POV violations: 'em' → 'anh' in narrative for Khải Phong references.

Conservative: only replace 'em' / 'Em' in narrative paragraphs (outside quotes)
that contain 'Khải Phong'. Specific verb collocations.

Usage:
    python tools/rewrite_pov.py --ep 41 --dry-run    # preview
    python tools/rewrite_pov.py --ep 41               # apply
    python tools/rewrite_pov.py --all                 # all 50 EPs
"""
import re
import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# Verb patterns where "em" / "Em" likely refers to Khải Phong (narrator)
KP_VERBS = ['cố', 'không', 'đã', 'sẽ', 'là', 'có', 'nhớ', 'nhìn', 'đi', 'về',
            'ngồi', 'đứng', 'vuốt', 'gật', 'cảm', 'hiểu', 'biết', 'sống', 'làm',
            'còn', 'nhói', 'lệ', 'tim', 'cảm thấy', 'ngẫm', 'quyết',
            'đợi', 'đem', 'gửi', 'cất', 'lấy', 'mở', 'đóng', 'rời',
            'đeo', 'tháo', 'vẫn', 'chỉ', 'tiếp']

def strip_metadata(text):
    """Return (metadata_block, body)."""
    m = re.search(r'```.*?```', text, flags=re.DOTALL)
    if m:
        return text[:m.end()], text[m.end():]
    return '', text

def split_quoted(text):
    """Split text into list of (chunk, is_quoted)."""
    chunks = []
    pos = 0
    for m in re.finditer(r'"[^"]*"', text):
        if m.start() > pos:
            chunks.append((text[pos:m.start()], False))
        chunks.append((m.group(), True))
        pos = m.end()
    if pos < len(text):
        chunks.append((text[pos:], False))
    return chunks

def rewrite_narrative_paragraph(para):
    """Within a narrative paragraph that mentions Khải Phong, rewrite Em/em → Anh/anh
    only for verbs in KP_VERBS list (safe heuristic)."""
    if 'Khải Phong' not in para:
        return para, 0

    changes = 0

    # Pattern 1: "Em <verb>" at sentence start → "Anh <verb>"
    for verb in KP_VERBS:
        # Capitalized "Em verb"
        pattern = rf'\bEm (?={re.escape(verb)}\b)'
        new_para, n = re.subn(pattern, 'Anh ', para)
        if n:
            para = new_para
            changes += n

        # lowercase " em verb"
        pattern = rf'\b em (?={re.escape(verb)}\b)'
        new_para, n = re.subn(pattern, ' anh ', para)
        if n:
            para = new_para
            changes += n

    # Pattern 2: "Em <pronoun>" specific Khải Phong inner monologue
    # "Em chỉ" / "Em không thể" / "Em sắp"
    extra_starts = ['chỉ', 'thấy', 'lại', 'phải', 'thật', 'lần', 'tỉnh', 'sắp', 'mới', 'hôm', 'tuần', 'tháng', 'năm']
    for start in extra_starts:
        # Only inside Khải Phong inner monologue paragraphs (heuristic)
        pattern = rf'\bEm (?={re.escape(start)}\b)'
        new_para, n = re.subn(pattern, 'Anh ', para)
        if n:
            para = new_para
            changes += n
        pattern = rf'\b em (?={re.escape(start)}\b)'
        new_para, n = re.subn(pattern, ' anh ', para)
        if n:
            para = new_para
            changes += n

    return para, changes

def rewrite_text(text):
    """Rewrite entire EP text — narrative only (skip quoted dialogue + metadata)."""
    meta, body = strip_metadata(text)
    chunks = split_quoted(body)
    new_chunks = []
    total_changes = 0
    for chunk, is_quoted in chunks:
        if is_quoted:
            new_chunks.append(chunk)
        else:
            # Split into paragraphs
            paragraphs = chunk.split('\n\n')
            new_paragraphs = []
            for p in paragraphs:
                new_p, n = rewrite_narrative_paragraph(p)
                new_paragraphs.append(new_p)
                total_changes += n
            new_chunks.append('\n\n'.join(new_paragraphs))
    return meta + ''.join(new_chunks), total_changes

def process_ep(ep_num, dry_run=False):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists():
        print(f"  EP{ep_num:02d}: not found")
        return 0
    original = p.read_text(encoding='utf-8')
    new_text, changes = rewrite_text(original)
    if dry_run:
        print(f"  EP{ep_num:02d}: {changes} changes (dry-run)")
    else:
        if changes > 0:
            p.write_text(new_text, encoding='utf-8')
        print(f"  EP{ep_num:02d}: {changes} changes applied")
    return changes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if args.ep:
        process_ep(args.ep, args.dry_run)
    elif args.all:
        total = 0
        for n in range(1, 51):
            c = process_ep(n, args.dry_run)
            total += c
        print(f"\nTOTAL: {total} changes")
    else:
        print("Usage: --ep N [--dry-run] OR --all [--dry-run]")
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
