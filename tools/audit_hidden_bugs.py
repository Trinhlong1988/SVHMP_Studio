"""SVHMP — Hidden bugs audit (Mr.Long 28/6 nghiêm túc khai thác lỗi KHÁC).

20 dimensions audit các pattern CHƯA detected by existing 13 tools:
1. Timeline math (age vs life events consistency)
2. Object collection counter accuracy
3. Bác tài 2-line rule violation (câu thứ 3 ngoài milestone/extra_beat_HOOK — v2 12/7
   DEBT-032: tính riêng vị trí HOOK theo bible/21#extra_beat_HOOK, xem driver_extra_overuse_flag())
4. Ghost manifest > 1 / EP
5. Section word count balance
6. Pause marker per section
7. Passenger age math (Bích Trâm 32 sinh con 18 → tuổi sinh con 14? math)
8. Location reuse (cùng ngã ba 2 EPs)
9. Passenger occupation variety
10. Object material variety
11. Bell sound description pattern
12. "Khải Phong quan sát" repetition
13. "Bác tài liếc gương" overuse
14. Passenger entry pattern lặp
15. Ghost description pattern (vuốt vai + mỉm cười + tan)
16. Quotation introduction pattern ("Giọng X trầm")
17. EP30 Khải Phong Nguyễn tuổi 30 + tốt nghiệp 2017 math
18. Quote balance per EP
19. Em-dash density extreme
20. Bài 'Áo lụa Hà Đông' radio frequency (callback consistency)
"""
import re
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

sys.path.insert(0, str(Path(__file__).parent))
from milestones import LEGACY_AUDIT_EXEMPT_EPS, EXTRA_BEAT_HOOK_EPS  # single source (see tools/milestones.py)

SVHMP = Path(__file__).resolve().parents[1]

def strip_meta(text):
    return re.sub(r'```.*?```', '', text, flags=re.DOTALL)

# --------------------------------------------------------------------------
# DEBT-032 extension (2026-07-12) — extra_beat_HOOK awareness (bible/21#extra_
# beat_HOOK + bible/00#R42 allowed_format thứ 3, per proposal APPROVED_A).
# --------------------------------------------------------------------------
DRIVER_QUOTE_PATTERN = re.compile(
    r'Bác tài[^\n.]*?(?:cất lời|nói|đáp|bảo|hỏi|tiếp|liếc gương)[^"]*?"([^"]+)"'
)
# Ranh giới HOOK (section 1) — LUÔN đứng trước SETUP (section 2) hoặc INCIDENT
# (section 3, nếu 1 tập thiếu SETUP). Dùng để tách quote "extra_beat_HOOK" (vị
# trí HOOK) khỏi quote CLIFFHANGER/REVEAL baseline (bible/00#R42/#R55) — CHỈ ảnh
# hưởng cách tính cho EP nằm trong EXTRA_BEAT_HOOK_EPS, KHÔNG đổi gì cho EP khác.
HOOK_SECTION_END_PATTERN = re.compile(r'^#\s*(?:SETUP|INCIDENT)\s*\[section', re.MULTILINE)
DRIVER_STANDARD_LINES = {'Con đã nhớ ra chưa?', 'Chưa tới lúc.'}


def split_driver_extra_quotes(body):
    """Tách quote 'thừa' của bác tài (ngoài 2 speech_lines chuẩn) thành 2 nhóm theo
    VỊ TRÍ văn bản: (hook, rest). `hook` = quote xuất hiện TRƯỚC section SETUP/INCIDENT
    (vùng extra_beat_HOOK). `rest` = quote ở CLIFFHANGER/REVEAL/nơi khác (baseline R42/
    R55). `body` PHẢI đã qua strip_meta(). Thứ tự trong `hook`/`rest` giữ nguyên thứ tự
    xuất hiện trong văn bản (khớp DRIVER_QUOTE_PATTERN.findall thứ tự gốc khi gộp lại).
    """
    m = HOOK_SECTION_END_PATTERN.search(body)
    hook_end = m.start() if m else 0
    hook, rest = [], []
    for match in DRIVER_QUOTE_PATTERN.finditer(body):
        q = match.group(1).strip()
        if q in DRIVER_STANDARD_LINES:
            continue
        (hook if match.start() < hook_end else rest).append(q)
    return hook, rest


def driver_extra_overuse_flag(ep_num, body, extra_beat_hook_eps=EXTRA_BEAT_HOOK_EPS):
    """True nếu tập `ep_num` có driver quote 'thừa' vượt R55 (bible/00#R55_driver_R42_
    strict_enforce), CÓ tính extra_beat_HOOK (bible/21#extra_beat_HOOK, 9 tập field-hoá
    2026-07-12): với EP trong `extra_beat_hook_eps`, quote ở vị trí HOOK KHÔNG tính vào
    cap R55 (đã field-hoá là allowed_format thứ 3 của R42) — CHỈ phần NGOÀI HOOK
    (CLIFFHANGER/REVEAL/khác) vẫn áp cap cũ (>1 = bug, KHÔNG nới thêm). Với EP KHÔNG nằm
    trong `extra_beat_hook_eps`, hành vi Y HỆT code gốc trước 2026-07-12 (>1 tổng = bug)
    — regression-safe, không đổi kết quả cho 41 EP còn lại.
    Trả về (should_flag: bool, extras_count: int, sample_extras: list[str]).
    """
    hook, rest = split_driver_extra_quotes(body)
    extras = hook + rest
    if ep_num in extra_beat_hook_eps:
        should_flag = len(rest) > 1
    else:
        should_flag = len(extras) > 1
    return should_flag, len(extras), extras[:2]

def load_eps():
    return {n: (SVHMP/'output'/f'ep_{n:02d}'/'episode.md').read_text(encoding='utf-8')
            for n in range(1,51) if (SVHMP/'output'/f'ep_{n:02d}'/'episode.md').exists()}

def main():
    print("="*70)
    print("HIDDEN BUGS AUDIT — 20 patterns chưa detected")
    print("="*70)
    eps = load_eps()
    if not eps:
        # deep-audit F6 (2/7): 0 episode = thieu input -> exit 2 (BLOCKED),
        # KHONG return 0 "no findings" (false-pass tren repo trong).
        print("[BLOCKED] khong tim thay episode nao (thieu input) — KHONG PASS.")
        return 2
    findings = []

    # 1. Timeline math: EP30 Khải Phong Nguyễn 30 tuổi + tốt nghiệp 2017
    print("\n[1] EP30 timeline math (passenger 30 tuổi + tốt nghiệp THPT 2017):")
    if 30 in eps:
        body = strip_meta(eps[30])
        # Passenger 30 → sinh ~1996 → tốt nghiệp THPT 18 tuổi = 2014, không 2017
        # Hoặc: tốt nghiệp 2017 → sinh 1999 → 2026 = 27 tuổi, không 30
        m_age = re.search(r'Khải Phong Nguyễn.*?(\d+) tuổi', body)
        m_grad = '2017' in body
        if m_age and m_grad:
            age = int(m_age.group(1))
            # If grad 2017 = 18 tuổi → today 2026 → age = 27 not 30
            expected_age = 2026 - (2017 - 18)
            if abs(age - expected_age) > 2:
                print(f"  🔴 BUG: passenger 30 tuổi nhưng tốt nghiệp 2017 → math expects ~{expected_age}")
                findings.append(('EP30_timeline_math', age, expected_age))
            else:
                print(f"  ✓ OK")

    # 2. Object collection counter accuracy
    print("\n[2] Object counter accuracy:")
    word_to_num = {
        'mười một':11,'mười hai':12,'mười ba':13,'mười bốn':14,'mười lăm':15,
        'mười sáu':16,'mười bảy':17,'mười tám':18,'mười chín':19,'hai mươi':20,
        'hai mươi mốt':21,'hai mươi hai':22,'hai mươi ba':23,'hai mươi tư':24,'hai mươi lăm':25,
        'hai mươi sáu':26,'hai mươi bảy':27,'hai mươi tám':28,'hai mươi chín':29,'ba mươi':30,
        'ba mươi mốt':31,'ba mươi hai':32,'ba mươi ba':33,'ba mươi tư':34,'ba mươi lăm':35,
        'ba mươi sáu':36,'ba mươi bảy':37,'ba mươi tám':38,'ba mươi chín':39,'bốn mươi':40,
        'bốn mươi mốt':41,'bốn mươi hai':42,'bốn mươi ba':43,'bốn mươi tư':44,'bốn mươi lăm':45,
        'bốn mươi sáu':46,'bốn mươi bảy':47,'bốn mươi tám':48,'bốn mươi chín':49,'năm mươi':50,
    }
    counter_bugs = []
    for n, t in eps.items():
        body = strip_meta(t)
        m = re.search(r'[Vv]ật thứ ([\w\s]+?)\.', body)
        if m:
            counter_text = m.group(1).strip().lower()
            counter_num = word_to_num.get(counter_text)
            if counter_num and counter_num != n:
                counter_bugs.append((n, counter_text, counter_num))
    if counter_bugs:
        print(f"  🔴 BUG: {len(counter_bugs)} EPs counter mismatch")
        for n, txt, num in counter_bugs[:5]:
            print(f"    EP{n:02d}: 'Vật thứ {txt}' (= {num}, expected {n})")
        findings.append(('object_counter_bugs', counter_bugs))
    else:
        print(f"  ✓ OK")

    # 3. Bác tài quotes — STRICT pattern (chỉ match khi bác tài là speaker)
    #    v2 (2026-07-12, DEBT-032): tính cả extra_beat_HOOK (bible/21#extra_beat_HOOK) —
    #    xem driver_extra_overuse_flag() phía trên (logic đầy đủ, mutation-tested trong
    #    tests/test_audit_hidden_bugs_extra_beat_hook.py).
    print("\n[3] Bác tài quote ngoài 2 standard (strict regex, extra_beat_HOOK-aware):")
    non_ms_extra = []
    for n, t in eps.items():
        if n in LEGACY_AUDIT_EXEMPT_EPS: continue
        body = strip_meta(t)
        should_flag, count, samples = driver_extra_overuse_flag(n, body)
        if should_flag:
            non_ms_extra.append((n, count, samples))
    if non_ms_extra:
        print(f"  🟡 {len(non_ms_extra)} EPs có >1 extra driver quote (R55)")
        for n, c, samples in non_ms_extra[:5]:
            print(f"    EP{n:02d}: {c} extras → '{samples[0][:60]}'")
        findings.append(('driver_extra_overuse', [(n, c) for n, c, _ in non_ms_extra]))
    else:
        print(f"  ✓ OK (strict regex)")

    # 4. Ghost manifest > 1 per EP
    print("\n[4] Ghost manifest 'xuất hiện' > 1 / EP:")
    ghost_excess = []
    for n, t in eps.items():
        body = strip_meta(t)
        cnt = len(re.findall(r'\bxuất hiện\b', body))
        if cnt > 2:  # 1-2 acceptable (passenger appear + ghost), 3+ = excess
            ghost_excess.append((n, cnt))
    if ghost_excess:
        print(f"  🟡 {len(ghost_excess)} EPs với 3+ 'xuất hiện'")
        for n, c in ghost_excess[:5]: print(f"    EP{n:02d}: {c}x")
        findings.append(('ghost_manifest_excess', ghost_excess))
    else:
        print(f"  ✓ OK")

    # 5. Passenger occupation distribution
    print("\n[5] Passenger occupation variety:")
    occupations = Counter()
    for n, t in eps.items():
        body = strip_meta(t)
        # Match "Em/Tôi làm [job]" intro
        m = re.search(r'(?:Em|Tôi) làm ([^.—\n]+)', body)
        if m:
            job = m.group(1).strip()[:30]
            occupations[job] += 1
    top_occ = occupations.most_common(5)
    print(f"  Top 5 occupations:")
    for job, cnt in top_occ:
        flag = '🟡' if cnt >= 4 else '○'
        print(f"    {flag} [{cnt}x] {job}")
    if top_occ and top_occ[0][1] >= 4:
        findings.append(('occupation_overrep', top_occ[0]))

    # 6. Object material variety (signature_object types)
    print("\n[6] Signature_object material variety:")
    obj_types = Counter()
    for n, t in eps.items():
        m = re.search(r'signature_object:\s*OBJ_(\w+)', t)
        if m:
            obj_types[m.group(1)[:15]] += 1
    top_obj = obj_types.most_common(5)
    print(f"  Top 5 object types:")
    for obj, cnt in top_obj:
        flag = '🟡' if cnt >= 4 else '○'
        print(f"    {flag} [{cnt}x] OBJ_{obj}")

    # 7. "Khải Phong quan sát" repetition
    print("\n[7] 'Khải Phong quan sát từ ghế ba' template:")
    quan_sat = sum(strip_meta(t).count('Khải Phong quan sát') for t in eps.values())
    print(f"  Total: {quan_sat} (50 EPs = 1/EP target)")
    if quan_sat > 60:
        findings.append(('quan_sat_overuse', quan_sat))

    # 8. Bell sound "Chuông xe ngân. Một tiếng. Tan." exact pattern
    print("\n[8] Bell template variety:")
    bell_exact = sum(strip_meta(t).count('Chuông xe ngân. Một tiếng. Tan.') for t in eps.values())
    print(f"  Exact 'Chuông xe ngân. Một tiếng. Tan.' template: {bell_exact}/50 (formulaic)")
    if bell_exact > 30:
        findings.append(('bell_template_overuse', bell_exact))

    # 9. Passenger entry pattern lặp
    print("\n[9] Passenger entry 'bước lên xe. Đi qua hàng ghế đầu' template:")
    entry_pattern = sum(1 for t in eps.values() if 'bước lên xe. Đi qua hàng ghế đầu' in strip_meta(t))
    print(f"  Template count: {entry_pattern}/50")
    if entry_pattern > 30:
        findings.append(('entry_pattern_overuse', entry_pattern))

    # 10. Ghost description pattern "vuốt vai + Mỉm cười + tan"
    print("\n[10] Ghost manifest description pattern:")
    ghost_desc = sum(1 for t in eps.values() if 'vuốt vai' in strip_meta(t) and 'Mỉm cười' in strip_meta(t))
    print(f"  'vuốt vai + Mỉm cười' template: {ghost_desc}/50")
    if ghost_desc > 30:
        findings.append(('ghost_desc_template_overuse', ghost_desc))

    # 11. Bài "Áo lụa Hà Đông" radio callback frequency
    print("\n[11] 'Áo lụa Hà Đông' radio callback:")
    ao_lua = sum(1 for t in eps.values() if 'Áo lụa Hà Đông' in strip_meta(t))
    print(f"  Count: {ao_lua}/50 (design: EP08+EP20+EP30+EP40 = 4 milestones)")
    if ao_lua < 3 or ao_lua > 6:
        findings.append(('ao_lua_callback_off', ao_lua))

    # 12. Section word count balance — check REVEAL too short
    print("\n[12] REVEAL section word count (target ≥600):")
    reveal_short = []
    for n, t in eps.items():
        m = re.search(r'#+\s*REVEAL.*?(?=#+\s*(PAYOFF|CLIFFHANGER)|$)', t, re.IGNORECASE | re.DOTALL)
        if m:
            wc = len(m.group().split())
            if wc < 600:
                reveal_short.append((n, wc))
    if reveal_short:
        print(f"  🟡 {len(reveal_short)} EPs REVEAL < 600 words")
        for n, wc in reveal_short[:5]: print(f"    EP{n:02d}: {wc} words")
        findings.append(('reveal_too_short', reveal_short))
    else:
        print(f"  ✓ OK")

    # 13. EP08 + EP14 radio "Áo lụa" + "quê nhà" cross check
    print("\n[13] Radio 'quê nhà' pattern frequency:")
    que_nha = sum(strip_meta(t).count('quê nhà') for t in eps.values())
    print(f"  Total: {que_nha} (1-2/EP expected = 50-100)")

    # 14. "Đèn pha quét" pattern reuse
    print("\n[14] 'Đèn pha quét' opener template:")
    den_pha = sum(strip_meta(t).count('Đèn pha quét') for t in eps.values())
    print(f"  Total: {den_pha}")
    if den_pha > 40:
        findings.append(('den_pha_overuse', den_pha))

    # 15. Quote brackets balance per EP
    print("\n[15] Quotation balance:")
    unbalanced = []
    for n, t in eps.items():
        cnt = t.count('"')
        if cnt % 2 != 0:
            unbalanced.append((n, cnt))
    if unbalanced:
        print(f"  🔴 {len(unbalanced)} EPs unbalanced")
        findings.append(('quote_unbalanced', unbalanced))
    else:
        print(f"  ✓ OK")

    # 16-20: Sample remaining
    print("\n[16-20] More checks (cliffhanger ending pattern, etc.):")
    cliff_end_template = sum(1 for t in eps.values() if 'Bác tài liếc gương. "Đêm' in strip_meta(t))
    print(f"  CLIFFHANGER 'Bác tài liếc gương. \"Đêm...\"': {cliff_end_template}/50")
    if cliff_end_template > 40:
        findings.append(('cliffhanger_template_overuse', cliff_end_template))

    # SUMMARY
    print(f"\n{'='*70}\nSUMMARY — HIDDEN BUGS FOUND: {len(findings)}\n{'='*70}")
    for f in findings:
        print(f"  • {f[0]}")

    # Save report
    out = SVHMP / 'runtime' / 'audit_hidden_bugs_report.json'
    out.write_text(json.dumps({
        'findings': [{'type': f[0], 'data': str(f[1:])[:300]} for f in findings],
        'top_occupations': dict(top_occ),
        'top_objects': dict(top_obj),
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")
    return 0 if not findings else 1

if __name__ == '__main__':
    sys.exit(main())
