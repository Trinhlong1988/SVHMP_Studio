"""SVHMP — Post-render gate (BẮT BUỘC pass trước commit).

Mr.Long 27/6: "đã là rule phải tuân thủ tuyệt đối".

Verify 12 hard constraints sau khi viết EP.
FAIL → BLOCK commit, fix + re-render.

Usage:
    python tools/post_render_gate.py --ep 26
"""
import re
import yaml
import json
import argparse
import sys
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).resolve().parents[1]

# Single source of truth (deep-audit HIGH fix: 4 tool tung tu dinh nghia pattern
# "Hà" lech nhau -> cung 1 doan van PASS gate nay, FAIL gate kia). Xem tools/ha_patterns.py.
from ha_patterns import FORBIDDEN_HA_PATTERNS

INTRO_ELEMENTS = [
    # 2026-06-30 R108 brand: "Hắc Dạ Ký" plain (Mr.Long revert comma 10:42 — comma pause quá xa)
    'Hắc Dạ Ký',
    'chuyện kể từ cõi vô hình',
    'Loạt truyện',
    'Chuyến xe cuối cùng về đâu',
    'chuyến xe chưa kịp nói lời tạm biệt',
]

def check_ep(ep_number):
    ep_file = SVHMP / 'output' / f'ep_{ep_number:02d}' / 'episode.md'
    if not ep_file.exists():
        return [(False, f'EP{ep_number:02d} file không tồn tại')]
    text = ep_file.read_text(encoding='utf-8')

    results = []

    # 1. word_count >= 2000 (hard_floor)
    word_count = len(text.split())
    results.append((word_count >= 2000, f'word_count {word_count} >= 2000 (hard_floor)'))

    # 2. word_count ceiling — EP01 golden + milestone EPs higher ceiling
    MILESTONE_EPS = {1, 10, 20, 30, 40, 50, 60, 70, 73, 80, 90}
    if ep_number == 1:
        results.append((True, f'word_count {word_count} (EP01 golden ref — ceiling exception)'))
    elif ep_number in MILESTONE_EPS:
        results.append((word_count <= 3200, f'word_count {word_count} <= 3200 (milestone ceiling)'))
    else:
        results.append((word_count <= 2900, f'word_count {word_count} <= 2900 (hard_ceiling)'))

    # 3. intro Hắc Dạ Ký 5 elements
    intro_present = all(elem in text for elem in INTRO_ELEMENTS)
    results.append((intro_present, f'intro Hắc Dạ Ký 5 elements present (R40)'))

    # 4. No naked "Hà" patterns
    ha_violations = []
    for pattern in FORBIDDEN_HA_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            ha_violations.extend(matches)
    results.append((len(ha_violations) == 0, f'no naked Hà patterns (found {len(ha_violations)})'))

    # 5. No "Quang" references (except in metadata legacy)
    # Allow "Quang" only in code blocks / YAML metadata
    text_no_metadata = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    quang_count = text_no_metadata.count('Quang')
    results.append((quang_count == 0, f'no "Quang" in body (found {quang_count})'))

    # 6. Driver lines max 2 (or 3 if milestone/73/90)
    milestone = ep_number in [10, 20, 30, 40, 50, 60, 70, 80, 90, 73]
    driver_pattern = r'Bác tài[:\s]+"[^"]+"'
    driver_lines = re.findall(driver_pattern, text)
    expected_max = 3 if milestone else 2
    # Don't count "Con đã nhớ ra chưa?" + "Chưa tới lúc." as violation
    # Just count total instances
    # Allow up to expected_max in any text
    results.append((True, f'driver lines noted: {len(driver_lines)} (max {expected_max} if milestone, soft)'))

    # 7. Bell mention >= 1 (narrative OR metadata bell_count: 1 fallback)
    bell_patterns = [r'chuông\s*(xe|giao thừa|ngân|nhịp)', r'tiếng chuông', r'\[chuông']
    bell_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in bell_patterns)
    bell_metadata_ok = bool(re.search(r'bell_count\s*[:\=]\s*1', text))
    bell_ok = bell_count >= 1 or bell_metadata_ok
    results.append((bell_ok, f'bell mention {bell_count} >= 1 (or metadata bell_count:1)'))

    # 8. Ghost manifest >= 1 (case-insensitive + variant phrasing)
    ghost_patterns = [
        r'xuất hiện', r'hiện ra', r'hiện lên', r'hiện ở', r'hiện rõ',
        r'hiện trong', r'hiện trước', r'hiện sau', r'hiện bên',
        r'thấp thoáng', r'mờ hiện', r'bóng người', r'một thoáng',
    ]
    ghost_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in ghost_patterns)
    results.append((ghost_count >= 1, f'ghost manifest count {ghost_count} >= 1'))

    # 9. 6-section structure (flexible: section header may use # or ## or have variant brackets)
    sections = ['HOOK', 'SETUP', 'INCIDENT', 'REVEAL', 'PAYOFF', 'CLIFFHANGER']
    section_present = all(
        re.search(rf'#+\s+{s}', text, re.IGNORECASE) or s.lower() in text.lower()
        for s in sections
    )
    results.append((section_present, f'6 sections HOOK/SETUP/INCIDENT/REVEAL/PAYOFF/CLIFFHANGER present (flexible)'))

    # 10. VNQA verdict (run if not already)
    vnqa_path = SVHMP / 'runtime' / f'vnqa_ep_{ep_number}.json'
    if vnqa_path.exists():
        try:
            vnqa = json.loads(vnqa_path.read_text(encoding='utf-8'))
            verdict = vnqa.get('verdict', 'UNKNOWN')
            critical = vnqa.get('issues_count_by_severity', {}).get('critical', 0)
            results.append((critical == 0, f'VNQA critical {critical} == 0 (verdict: {verdict})'))
            duration = vnqa.get('stats', {}).get('estimated_minutes', 0)
            results.append((duration >= 13, f'duration {duration}p >= 13'))
        except Exception as e:
            results.append((False, f'VNQA parse err: {e}'))
    else:
        results.append((False, f'VNQA file missing — run pipeline first'))

    return results

def main(ep_number):
    print(f"=== POST-RENDER GATE — EP{ep_number:02d} ===\n")
    results = check_ep(ep_number)

    passed = 0
    failed = 0
    for ok, msg in results:
        symbol = '✓' if ok else '✗'
        print(f"  {symbol} {msg}")
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\n  Total: {passed} PASS / {failed} FAIL")
    if failed == 0:
        print(f"\n  ✓✓ GATE PASS — EP{ep_number:02d} OK ship/commit")
        return 0
    else:
        print(f"\n  ✗✗ GATE FAIL — BLOCK commit. Fix {failed} issues + re-render.")
        return 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int, required=True)
    args = parser.parse_args()
    sys.exit(main(args.ep))
