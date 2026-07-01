"""SVHMP — R66 auto-fix chain ≥3 câu 4-6 từ (Mr.Long 28/6 S6).

Strategy: trong mỗi chain ≥3 câu 4-6 từ, merge câu 1+2 bằng " — " (em-dash):
  "Đèn trần xe vàng. / Sáng vừa đủ thấy mặt người. / Mười một..."
  → "Đèn trần xe vàng — sáng vừa đủ thấy mặt người. / Mười một..."

Lý do dùng em-dash:
- Bảo toàn nghĩa, không thay từ
- TTS pause natural ~250ms (R75 dấu — không hard pause)
- Giảm chain từ 3 → 2 câu → audit qua

Edge cases:
- Skip nếu câu 1 hoặc 2 bắt đầu bằng "—" (đã là dialogue/list)
- Skip nếu câu 1 hoặc 2 chứa "[pause" (đã có TTS adapter)
- Skip nếu câu 1 kết thúc bằng "?" hoặc "!" (giữ tone)
"""
import re
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(__file__).resolve().parents[1]


def can_merge(s1, s2):
    """Decide if 2 sentences safe to merge with em-dash."""
    if not s1 or not s2: return False
    if s1.startswith('—') or s2.startswith('—'): return False
    if '[pause' in s1 or '[pause' in s2: return False
    if s1.rstrip()[-1:] in ('?', '!'): return False
    # Skip nếu s2 mở đầu chữ hoa proper noun (tên người) — tránh phá flow
    # → OK em-dash vẫn xuống chữ thường ổn
    return True


def merge_pair(s1, s2):
    """Merge s1 + s2 → 's1_no_period — s2_lowered_first_char'"""
    # Strip trailing .
    s1_body = re.sub(r'\.\s*$', '', s1.rstrip())
    # Lower first char s2 nếu không phải proper noun (heuristic: 2+ chars all caps = proper, else lower)
    s2_strip = s2.lstrip()
    if s2_strip and s2_strip[0].isupper() and not (len(s2_strip) > 1 and s2_strip[1].isupper()):
        # Common case: capitalized first letter — lower it
        s2_new = s2_strip[0].lower() + s2_strip[1:]
    else:
        s2_new = s2_strip
    return f'{s1_body} — {s2_new}'


def fix_text(text):
    """Process whole EP text, merge pair câu 1+2 mỗi chain ≥3."""
    paras = text.split('\n\n')
    new_paras = []
    total_fixes = 0

    for para in paras:
        first_line = para.lstrip().split('\n', 1)[0]
        if not para.strip() or first_line.startswith(('#', '[', '|', '---', '```', '>')):
            new_paras.append(para)
            continue
        # Skip numbered list / bullet (1. 2. * - )
        if re.match(r'^\s*(?:\d+\.\s|\*\s|-\s)', first_line):
            new_paras.append(para)
            continue
        # Skip nếu para có bold marker ** (notes/meta)
        if '**' in para[:50]:
            new_paras.append(para)
            continue

        sentences = re.split(r'(?<=[.!?])\s+', para)
        if len(sentences) < 3:
            new_paras.append(para)
            continue

        # Find chains, merge first 2 in each
        result = []
        i = 0
        while i < len(sentences):
            s = sentences[i]
            wc = len(s.split())
            if 4 <= wc <= 6 and i + 2 < len(sentences):
                # Check next 2
                s2 = sentences[i + 1]
                s3 = sentences[i + 2]
                wc2 = len(s2.split())
                wc3 = len(s3.split())
                if 4 <= wc2 <= 6 and 4 <= wc3 <= 6 and can_merge(s, s2):
                    merged = merge_pair(s, s2)
                    result.append(merged)
                    total_fixes += 1
                    i += 2  # consumed 1+2
                    continue
            result.append(s)
            i += 1

        new_paras.append(' '.join(result))

    return '\n\n'.join(new_paras), total_fixes


def main():
    apply = '--apply' in sys.argv
    ep_arg = None
    for a in sys.argv[1:]:
        if a.startswith('--ep='):
            ep_arg = int(a.split('=')[1])

    print(f"R66 CHAIN MERGE | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    total = 0
    eps = [ep_arg] if ep_arg else range(1, 51)

    for n in eps:
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists(): continue
        text = p.read_text(encoding='utf-8')
        new_text, fixes = fix_text(text)
        if fixes > 0:
            total += fixes
            print(f"EP{n:02d}: {fixes} chain merge(s)")
            if apply and new_text != text:
                shutil.copy2(p, p.with_suffix('.md.bak.r66'))
                p.write_text(new_text, encoding='utf-8')

    print(f"\nTotal: {total} R66 chain merges across {'1 EP' if ep_arg else '50 EPs'}")


if __name__ == '__main__':
    main()
