"""SVHMP — Audit pronoun POV consistency cross 50 EPs.

R47: Narrator 3rd person — Khải Phong = 'anh' (NOT 'em' ngoài dialogue).

Logic:
- Split text into segments: quoted (between "...") vs narrative
- In narrative segments containing "Khải Phong", count "Em" / "em" occurrences
- These are likely POV violations (em refers to Khải Phong in narrative)

Usage: python tools/audit_pronoun_pov.py
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

def strip_metadata(text):
    return re.sub(r'```.*?```', '', text, flags=re.DOTALL)

def split_quoted_unquoted(text):
    """Split text into (narrative, dialogue) chunks.
    Returns list of (chunk, is_dialogue)."""
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

def count_pov_violations(text):
    """Count 'Em' / 'em' in narrative paragraphs containing 'Khải Phong'.
    These are likely POV violations (Khải Phong should be 'anh' in narrative)."""
    text = strip_metadata(text)
    chunks = split_quoted_unquoted(text)

    violations = 0
    violation_samples = []

    for chunk, is_dialogue in chunks:
        if is_dialogue:
            continue
        # Split chunk into paragraphs
        paragraphs = chunk.split('\n\n')
        for para in paragraphs:
            if 'Khải Phong' in para:
                # Count "Em" at sentence start (capital E) AND " em " (lowercase em with spaces)
                em_starts = len(re.findall(r'(?:^|\.\s+|\?\s+|!\s+|—\s*)Em\b', para))
                em_inline = len(re.findall(r'\bem\s+(?:cố|không|đã|sẽ|là|có|nhớ|nhìn|đi|về|ngồi|đứng|vuốt|gật|cảm|hiểu|biết|sống|làm)', para))
                if em_starts + em_inline > 0:
                    violations += em_starts + em_inline
                    if len(violation_samples) < 3:
                        # Find first occurrence sample
                        m = re.search(r'(?:^|\.\s+)(Em [^.!?]{20,80})', para)
                        if m:
                            violation_samples.append(m.group(1)[:80])
    return violations, violation_samples

def main():
    print("=" * 70)
    print("PRONOUN POV AUDIT — Khải Phong narrative 'Em' violations")
    print("=" * 70)
    print()
    total = 0
    per_ep = {}
    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        violations, samples = count_pov_violations(text)
        per_ep[n] = violations
        total += violations
        symbol = '🔴' if violations > 5 else '🟡' if violations > 0 else '✓'
        print(f"  EP{n:02d}: {symbol} {violations} violations")
        if samples and n <= 5:
            for s in samples[:2]:
                print(f"      SAMPLE: '{s}...'")
    print()
    print(f"TOTAL POV VIOLATIONS: {total}")
    print(f"EPs with violations: {sum(1 for v in per_ep.values() if v > 0)}/{len(per_ep)}")
    print(f"Avg violations/EP: {total/len(per_ep):.1f}")

    # Save report
    import json
    out = SVHMP / 'runtime' / 'audit_pronoun_pov_report.json'
    out.write_text(json.dumps({'per_ep': per_ep, 'total': total}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report: {out}")
    return 0 if total == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
