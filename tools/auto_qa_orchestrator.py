"""SVHMP — AUTO QA ORCHESTRATOR (Mr.Long 28/6 lệnh tự động ping-input).

Loop tự động:
1. Scan all audits EP02-50
2. Apply auto-fix
3. Re-scan verify
4. Repeat đến convergence (no new fixes OR max 10 iterations)
5. Final report

Scope: EP02-50 only (EP01 do CMD khác)
"""
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
import sys
import json
import time
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

TRIGGER_WORDS = {'Khải-Phong', 'Khải', 'Cô', 'Anh', 'Bà', 'Ông', 'Em', 'Tôi', 'Bác'}

def count_chains_ep(ep_num):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists(): return 0
    text = re.sub(r'#[^\n]*\n', '', p.read_text(encoding='utf-8'))
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chains = 0
    chain = []
    for s in sentences:
        first = s.strip().split()[0] if s.strip() else ''
        if first in TRIGGER_WORDS:
            chain.append(first)
        else:
            if len(chain) >= 3: chains += 1
            chain = []
    if len(chain) >= 3: chains += 1
    return chains

def count_chains_all():
    return sum(count_chains_ep(n) for n in range(2, 51))

def run_vary_fix():
    """Apply vary subject fix EP02-50."""
    cmd = [sys.executable, str(SVHMP / 'tools' / 'fix_anaphora_vary_subject.py'), '--apply']
    result = subprocess.run(cmd, cwd=SVHMP, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120, creationflags=CREATE_NO_WINDOW)
    return result.stdout

def main():
    print("=" * 70)
    print("AUTO QA ORCHESTRATOR — EP02-50 anaphora convergence loop")
    print("Mr.Long lệnh tự động ping-input — 'bất kể từ gì >2 liền tiếp'")
    print("=" * 70)

    MAX_ITER = 10
    prev_total = -1

    for iteration in range(1, MAX_ITER + 1):
        total_chains = count_chains_all()
        print(f"\n--- Iteration {iteration} ---")
        print(f"Chains ≥3 ANY trigger: {total_chains}")

        if total_chains == 0:
            print("✅ CONVERGED — 0 chains remaining")
            break
        if total_chains == prev_total:
            print(f"⏸️ No reduction this iter — stopping (vary script limit)")
            break

        prev_total = total_chains
        print(f"Running vary fix...")
        run_vary_fix()
        time.sleep(0.5)

    # Final report per-EP
    final = {}
    for n in range(2, 51):
        c = count_chains_ep(n)
        if c > 0:
            final[n] = c

    print(f"\n=== FINAL REPORT ===")
    print(f"EPs với chains remaining: {len(final)}")
    print(f"Total chains: {sum(final.values())}")
    print(f"Top 10:")
    for n, c in sorted(final.items(), key=lambda x: -x[1])[:10]:
        print(f"  EP{n:02d}: {c}")

    out = SVHMP / 'runtime' / 'auto_qa_orchestrator_report.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        'iterations': iteration,
        'final_total_chains': sum(final.values()),
        'eps_with_chains': final,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
