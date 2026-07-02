"""SVHMP R58 — Audit tilde-ending end-of-sentence (TTS BigVGAN bug).

Mr.Long 28/6 phát hiện:
  "đi Mỹ." → TTS đọc thành "đi Mỵ." (ngã → nặng tone drift)
  "khung cũ." → TTS đọc thành "khung cụ."

Rule R58: từ kết thúc câu/clause bằng nguyên âm dấu NGÃ (~) → CẤM TUYỆT ĐỐI.

EOL boundary: . ! ? — " \n [pause:

Detection:
- regex word ending in tilde-vowel right before EOL boundary
- exclude địa danh compound (Mỹ Đức ...) — Mỹ ở mid-compound

Usage: python tools/audit_tilde_eol.py [--ep N] [--fix]
"""
import re
import sys
import argparse
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).resolve().parents[1]

TILDE_VOWELS = 'ãẵẫẽễĩõỗỡũữỹ'

# EOL boundary: . ! ? — " ' \n [pause: also clause boundary : ; ,
# Phase 1 strict: only sentence-end (. ! ? — " new-line [pause)
EOL_PATTERN = re.compile(
    rf'(\w*[{TILDE_VOWELS}])\s*(?=[.!?—"\'\n]|\[pause)',
    re.UNICODE
)

# Words that are common false positives (compound — tilde-vowel inside word)
# Example: "Mỹ" in "Mỹ Đức" — the Mỹ is followed by space + Capital, not EOL
COMPOUND_OK = {
    'Mỹ Đức', 'Mỹ Linh', 'Mỹ Đình', 'Mỹ Thuận', 'Mỹ Hào', 'Mỹ Tho',
}

def strip_meta_blocks(text):
    """Strip ```...``` code blocks + YAML frontmatter."""
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    return text

def audit_episode(text):
    """Return list of (line_num, word, context, severity)."""
    issues = []
    body = strip_meta_blocks(text)
    lines = body.splitlines()

    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
        for m in EOL_PATTERN.finditer(line):
            word = m.group(1)
            # Skip if word is part of known compound (next char is space + caps in same line)
            end_pos = m.end()
            ctx_start = max(0, m.start() - 30)
            ctx_end = min(len(line), m.end() + 20)
            context = line[ctx_start:ctx_end]

            # Compound check: word followed by space + Capital letter (proper noun chain)
            tail = line[m.end():m.end()+15]
            if re.match(r'\s+[A-ZĐÂÊÔƠƯÁÀẢÃẠ]', tail):
                # Likely compound proper noun — but still check if it's a known one
                # If immediately followed by . ! ? — at end of compound word, still flag
                continue

            issues.append({
                'line': i,
                'word': word,
                'context': context.strip(),
                'severity': 'HIGH',
            })

    return issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int, help='Audit only EP N')
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    print("=" * 70)
    print("R58 AUDIT — Tilde-vowel at end-of-sentence (TTS bug)")
    print("=" * 70)

    eps_dir = SVHMP / 'output'
    total_issues = 0
    eps_with_issues = []

    eps_to_audit = []
    if args.ep:
        p = eps_dir / f'ep_{args.ep:02d}' / 'episode.md'
        if p.exists():
            eps_to_audit.append((args.ep, p))
    else:
        for n in range(1, 91):
            p = eps_dir / f'ep_{n:02d}' / 'episode.md'
            if p.exists():
                eps_to_audit.append((n, p))

    all_violations = []

    for n, p in eps_to_audit:
        text = p.read_text(encoding='utf-8')
        issues = audit_episode(text)
        if issues:
            eps_with_issues.append((n, len(issues)))
            total_issues += len(issues)
            for issue in issues:
                issue['ep'] = n
                all_violations.append(issue)
            if not args.summary:
                print(f"\nEP{n:02d}: {len(issues)} violations")
                for issue in issues[:10]:
                    print(f"  L{issue['line']}: '{issue['word']}' | ...{issue['context']}...")
                if len(issues) > 10:
                    print(f"  ... + {len(issues) - 10} more")

    print(f"\n{'='*70}")
    print(f"SUMMARY: {total_issues} HIGH violations in {len(eps_with_issues)} EPs")
    print('='*70)
    for n, cnt in sorted(eps_with_issues, key=lambda x: -x[1])[:15]:
        print(f"  EP{n:02d}: {cnt}")

    out = SVHMP / 'runtime' / 'audit_tilde_eol_report.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        'total_violations': total_issues,
        'eps_with_issues': eps_with_issues,
        'violations': all_violations,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

    return 0 if total_issues == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
