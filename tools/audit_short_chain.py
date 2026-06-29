"""R66 audit — short sentence chain detection.

Rule: 1 câu ngắn (4-6 từ) phải đi kèm 1 câu dài (≥10 từ).
CẤM > 2 câu ngắn (4-6 từ) consecutive trong cùng paragraph hoặc cross-paragraph block.

Usage:
  python tools/audit_short_chain.py --ep 1
"""
import re, json, argparse
from pathlib import Path

BASE = Path(r'D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio')
SHORT_MIN = 4
SHORT_MAX = 6
MAX_CONSECUTIVE = 2

def word_count(sent):
    s = re.sub(r'\[[^\]]*\]', '', sent).strip()
    s = re.sub(r'[—.!?…,:;"\'\(\)]', ' ', s)
    return len([w for w in s.split() if w])

def audit_episode(ep_num):
    ep_md = BASE / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not ep_md.exists():
        return None
    text = ep_md.read_text(encoding='utf-8')
    # Strip codeblock + NOTES
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    sc = re.search(r'^# (SELF-CHECK|NOTES)', text, re.MULTILINE)
    if sc: text = text[:sc.start()]

    violations = []
    # Collect ALL sentences in order (cross paragraph)
    sentences = []
    line_no = 1
    for line in text.split('\n'):
        if re.match(r'^#+ ', line) or line.strip().startswith('---'):
            line_no += 1; continue
        # Split line into sentences
        for s in re.split(r'(?<=[.!?…])\s+', line):
            s = s.strip()
            if s:
                sentences.append((line_no, s, word_count(s)))
        line_no += 1

    # Walk: count consecutive short (4-6 từ)
    consecutive = []
    for ln, sent, wc in sentences:
        if SHORT_MIN <= wc <= SHORT_MAX:
            consecutive.append((ln, sent, wc))
            if len(consecutive) > MAX_CONSECUTIVE:
                violations.append({
                    'severity': 'HIGH',
                    'count': len(consecutive),
                    'first_line': consecutive[0][0],
                    'last_line': consecutive[-1][0],
                    'sentences': [{'line': c[0], 'wc': c[2], 'text': c[1][:80]} for c in consecutive],
                })
                # Restart counter after flag
                consecutive = consecutive[1:]
        else:
            consecutive = []

    return violations

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', type=int, default=None)
    ap.add_argument('--summary', action='store_true')
    args = ap.parse_args()

    eps = [args.ep] if args.ep else list(range(1, 51))
    all_results = {}
    total_high = 0
    for ep in eps:
        v = audit_episode(ep)
        if v is None: continue
        all_results[ep] = v
        n_high = sum(1 for x in v if x['severity'] == 'HIGH')
        total_high += n_high
        if not args.summary:
            print(f'EP{ep:02d}: {n_high} HIGH violations (>{MAX_CONSECUTIVE} consecutive short sentences)')
            for ix in v[:3]:
                print(f'  L{ix["first_line"]}-L{ix["last_line"]} ({ix["count"]} consecutive):')
                for s in ix['sentences'][:5]:
                    print(f'    L{s["line"]} ({s["wc"]}w): "{s["text"]}"')

    print(f'\n=== TOTAL R66 HIGH violations across {len(all_results)} EPs: {total_high} ===')

    out = BASE / 'runtime' / 'audit_short_chain_report.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Report: {out}')

if __name__ == '__main__':
    main()
