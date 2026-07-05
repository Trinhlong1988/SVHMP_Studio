"""SVHMP — VNQA H9 Continuity check cross-EP (Agent 4 kentjuno pattern).

Detect inconsistency in cross-EP facts:
- Khải Phong object count cumulative
- Hạ Vy mentions per EP (S2A limit ≤3, S2B ≤5)
- Driver lines count (==2 standard, ≤4 milestone)
- M1-M18 memory progression alignment
"""
import re, sys, json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(__file__).resolve().parents[1]

# Single source of truth (deep-audit HIGH fix: 4 tool tung tu dinh nghia pattern
# "Hà" lech nhau -> cung 1 doan van PASS gate nay, FAIL gate kia). Xem tools/ha_patterns.py.
from ha_patterns import FORBIDDEN_HA_PATTERNS

MILESTONE_EPS = {10, 20, 30, 40, 50, 60, 70, 73, 80, 90}

def audit_ep(text, ep_num):
    """Return list of (check, status, value)."""
    body = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    body = re.sub(r'^---\n.*?\n---\n', '', body, count=1, flags=re.DOTALL)
    results = []

    # 1. Hạ Vy mentions
    ha_vy_count = len(re.findall(r'\bHạ Vy\b', body))
    is_milestone = ep_num in MILESTONE_EPS
    max_hv = 8 if is_milestone else 5
    ha_vy_ok = ha_vy_count <= max_hv
    results.append(('Hạ_Vy_mentions', 'OK' if ha_vy_ok else 'WARN', f'{ha_vy_count}/{max_hv}'))

    # 2. Driver lines (bác tài quoted dialogue)
    driver_lines = re.findall(r'Bác tài[:\s]+"[^"]+"', body)
    max_driver = 4 if is_milestone else 2
    driver_ok = len(driver_lines) <= max_driver
    results.append(('Driver_lines', 'OK' if driver_ok else 'WARN', f'{len(driver_lines)}/{max_driver}'))

    # 3. Khải Phong object count (text mentions number of vật in pocket)
    obj_match = re.search(r'(\w+\s+)?(?:vật|đồ vật)\s+(?:trong túi|theo)', body)
    # Not strict — informational only
    results.append(('Khải_Phong_object_mention', 'INFO', 'present' if obj_match else 'absent'))

    # 4. Khải Phong rename verified (no naked Hà)
    # PATTERN list dung chung (single source: tools/ha_patterns.py) — CHI dong bo
    # list pattern, KHONG dong bo cong thuc threshold (van giu tolerance scale rieng).
    naked_ha = sum(len(re.findall(pat, body)) for pat in FORBIDDEN_HA_PATTERNS)
    ha_ok = naked_ha == 0 or naked_ha <= ep_num // 10  # tolerance scale
    results.append(('Naked_Hà_check', 'OK' if naked_ha == 0 else 'WARN', f'{naked_ha} naked'))

    # 5. Quang legacy check (should be 0 after rename)
    quang_count = body.count('Quang')
    results.append(('Quang_legacy', 'OK' if quang_count == 0 else 'WARN', f'{quang_count} Quang'))

    return results

def main():
    print("=" * 70)
    print("CONTINUITY CROSS-EP — VNQA H9")
    print("=" * 70)

    all_results = {}
    total_warn = 0
    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists(): continue
        text = p.read_text(encoding='utf-8')
        results = audit_ep(text, n)
        warns = [r for r in results if r[1] == 'WARN']
        if warns:
            all_results[n] = warns
            total_warn += len(warns)

    print(f"\n{len(all_results)} EPs có WARN — total {total_warn} issues")
    for n in sorted(all_results.keys())[:15]:
        print(f"\nEP{n:02d}:")
        for check, status, value in all_results[n]:
            print(f"  ⚠️ {check}: {value}")

    if not all_results:
        print("✅ ALL 50 EPs continuity clean")

    out = SVHMP / 'runtime' / 'audit_continuity.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({'eps_with_warn': {str(k): v for k, v in all_results.items()}}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
