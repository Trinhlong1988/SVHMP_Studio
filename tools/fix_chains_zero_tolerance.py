"""SVHMP — ZERO TOLERANCE chain breaker.

Mr.Long: "bất kể từ gì không được lặp liền nhau quá 2 lần"
→ Bất cứ chain ≥3 PHẢI break, không exception.

Strategy aggressive++:
1. Find chain ≥3 cùng trigger word
2. ALSO find chain ≥3 mixed trigger words
3. Cho mỗi chain: MERGE 2 câu liền với "," HOẶC vary subject
4. Loop với synonym pool rotating
5. Skip nothing — every chain MUST break

Run until count = 0 OR max 15 iterations.
"""
import re
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(__file__).resolve().parents[1]

TRIGGER_WORDS = ['Khải-Phong', 'Khải', 'Cô', 'Anh', 'Bà', 'Ông', 'Em', 'Tôi', 'Bác', 'Bóng', 'Người']

SYNONYM_POOLS = {
    'Anh': ['Người đàn ông', 'Người khách', 'Người ngồi đó', 'Bóng anh', 'Người ấy'],
    'Cô': ['Người con gái', 'Cô ấy', 'Cô gái ấy', 'Bóng cô', 'Người nữ'],
    'Khải-Phong': ['Anh ấy', 'Người khách ghế bảy', 'Người ngồi ghế bảy'],
    'Khải': ['Anh ấy', 'Người ngồi'],
    'Bà': ['Bà cụ ấy', 'Người bà', 'Bóng bà'],
    'Ông': ['Ông cụ ấy', 'Người ông', 'Bóng ông'],
    'Em': ['Cô ấy', 'Cô em', 'Em ấy', 'Đứa em'],
    'Tôi': ['Người kể', 'Tôi đây'],
    'Bác': ['Bác ấy', 'Người bác'],
    'Bóng': ['Hình bóng', 'Hình ảnh'],
    'Người': ['Bóng người', 'Hình bóng'],
}

counter = [0]

def get_syn(word):
    pool = SYNONYM_POOLS.get(word, [])
    if not pool: return None
    syn = pool[counter[0] % len(pool)]
    counter[0] += 1
    return syn

def process_ep(ep_num, dry_run=True):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists(): return 0
    text = p.read_text(encoding='utf-8')

    paragraphs = text.split('\n\n')
    new_paragraphs = []
    fixes = 0

    for para in paragraphs:
        if not para.strip() or para.startswith(('#', '[', '|', '---', '```')):
            new_paragraphs.append(para)
            continue

        sentences = re.split(r'(?<=[.!?])\s+', para)
        # Identify trigger word at start of each sentence (any TRIGGER word)
        starts = []
        for i, s in enumerate(sentences):
            s_strip = s.strip()
            first = s_strip.split()[0] if s_strip else ''
            # Strip dialogue dash
            if first.startswith('—'):
                first = ''
            starts.append((i, first))

        # Find chains of consecutive starts where first ∈ TRIGGER_WORDS
        chain = []
        chains_to_break = []
        for i, fw in starts:
            if fw in TRIGGER_WORDS:
                chain.append((i, fw))
            else:
                if len(chain) >= 3:
                    chains_to_break.append(list(chain))
                chain = []
        if len(chain) >= 3:
            chains_to_break.append(list(chain))

        # For each chain ≥3, vary pos 1 onwards
        for chain in chains_to_break:
            for pos, (idx, fw) in enumerate(chain):
                if pos >= 1:  # vary pos 1, 2, 3... (keep pos 0)
                    syn = get_syn(fw)
                    if syn:
                        sentences[idx] = re.sub(
                            rf'^{re.escape(fw)}\b',
                            syn,
                            sentences[idx],
                            count=1
                        )
                        fixes += 1

        new_paragraphs.append(' '.join(sentences))

    if fixes > 0 and not dry_run:
        backup = p.with_suffix('.md.bak.zero_tol')
        shutil.copy2(p, backup)
        p.write_text('\n\n'.join(new_paragraphs), encoding='utf-8')

    return fixes

def count_chains_ep(ep_num):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists(): return 0
    text = re.sub(r'#[^\n]*\n', '', p.read_text(encoding='utf-8'))
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    paragraphs = text.split('\n\n')
    chains = 0
    for para in paragraphs:
        if not para.strip(): continue
        sentences = re.split(r'(?<=[.!?])\s+', para)
        chain = 0
        for s in sentences:
            first = s.strip().split()[0] if s.strip() else ''
            if first.startswith('—'): first = ''
            if first in TRIGGER_WORDS:
                chain += 1
                if chain == 3:
                    chains += 1
            else:
                chain = 0
    return chains

def main():
    apply = '--apply' in sys.argv
    print(f"ZERO TOLERANCE BREAKER — EP02-50 | Mode: {'APPLY' if apply else 'DRY-RUN'}")

    for iteration in range(1, 16):
        total_fixes = 0
        for n in range(2, 51):
            fixes = process_ep(n, dry_run=not apply)
            total_fixes += fixes
        total_chains = sum(count_chains_ep(n) for n in range(2, 51))
        print(f"Iter {iteration}: fixes={total_fixes} | chains remaining={total_chains}")
        if total_chains == 0:
            print("✅ CONVERGED — zero chains")
            break
        if total_fixes == 0:
            print(f"⏸️ Hit limit — vary script can't reduce further")
            break

if __name__ == '__main__':
    main()
