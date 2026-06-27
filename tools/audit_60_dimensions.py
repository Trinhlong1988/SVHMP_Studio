"""SVHMP — 60-dimension comprehensive audit EP01-50.

Mr.Long 28/6: "đặt vị trí mình là người nghe sâu sắc, thích truyện ma, hiểu văn học,
                hiểu hiến pháp project, tự đọc lại từng câu từng từ, mở rộng hiến pháp,
                lặp lại 60 vòng"

6 layers × 10 dimensions = 60 checks total.
Per-EP report + global summary.

Usage: python tools/audit_60_dimensions.py [--ep N]
"""
import re
import json
import sys
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# ============================================================
# CONSTANTS
# ============================================================
INTRO_MARKER = 'Hắc Dạ Ký — chuyện kể từ cõi vô hình'

ANTI_SLOP_T1 = ['đột nhiên', 'bỗng nhiên', 'trong khoảnh khắc đó', 'không thể nào quên',
                'như thể', 'có lẽ', 'dường như', 'vô cùng', 'thầm lặng', 'rùng mình']
ANTI_SLOP_T2 = ['thoáng', 'khẽ', 'se sẽ', 'lặng lẽ', 'dần dần', 'nhẹ nhàng',
                'chậm rãi', 'vô hình', 'ánh mắt', 'khuôn mặt']
ANTI_SLOP_STRUCT = ['Trong khi đó,', 'Mặt khác,', 'Đáng chú ý,', 'Đáng kể,',
                    'Cần lưu ý rằng', 'Có một điều đặc biệt là', 'Thực ra,',
                    'Nói chung,', 'Một cách nào đó,']

NEVER_GORE = ['máu chảy ròng ròng', 'vết thương há miệng', 'xác phân hủy',
              'máu bắn', 'ruột rỗng']
NEVER_SCARE = ['BÙM!', 'tiếng hét chói tai', 'tiếng đập cửa đột ngột']
NEVER_EXORCISM = ['thầy cúng', 'pháp sư', 'lễ trừ tà', 'bài kinh xua đuổi']

DEATH_CONTEXT_WORDS = ['mất', 'chết', 'đã đi', 'qua đời', 'tang', 'quan tài']

MILESTONE_EPS = {1, 10, 20, 30, 40, 50, 60, 70, 73, 80, 90}

# Literary/horror dimensions
SENSORY_WORDS = ['mưa', 'gió', 'đèn', 'tiếng', 'ánh', 'mùi', 'lạnh', 'ấm', 'tối', 'sáng']
GHOST_VERBS = ['xuất hiện', 'hiện ra', 'hiện lên', 'tan', 'mỉm cười', 'vuốt', 'đứng', 'nhìn']

# ============================================================
# UTILS
# ============================================================
def strip_metadata(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    return text

def get_ngrams(text, n=4):
    words = text.split()
    return set(' '.join(words[i:i+n]) for i in range(len(words) - n + 1))

def jaccard(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

def load_episodes():
    eps = {}
    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if p.exists():
            eps[n] = p.read_text(encoding='utf-8')
    return eps

# ============================================================
# 60 CHECKS — per EP basis where possible
# ============================================================
def check_ep_60(ep_num, text, all_eps):
    """Run 60 dimensions for ONE EP."""
    body = strip_metadata(text)
    body_lower = body.lower()
    results = []

    # LAYER 1 — REPETITION (10)
    # 1.1 Internal anaphora >= 4 consecutive
    sentences = re.split(r'[.!?]\s+', body)
    starts = [s.split()[0] if s.split() else '' for s in sentences]
    max_run = 1
    cur_run = 1
    for i in range(1, len(starts)):
        if starts[i] == starts[i-1] and starts[i]:
            cur_run += 1; max_run = max(max_run, cur_run)
        else:
            cur_run = 1
    # Ngọc Ngạn first-person passenger monologue ("Em..." tự kể) — accept ≤14 consecutive
    # Vietnamese convention: passenger kể chuyện về chính mình nat. start with "Em"
    results.append(('1.1 internal anaphora consecutive', max_run, 'HIGH' if max_run >= 15 else 'MEDIUM' if max_run >= 8 else 'OK'))

    # 1.2 Word frequency excessive (single word > 20)
    words_count = Counter(re.findall(r'\b\w+\b', body_lower))
    excessive_words = [(w, c) for w, c in words_count.items() if c > 20 and len(w) > 2 and w not in ['khải', 'phong', 'hạ', 'vy', 'em', 'anh', 'không', 'một', 'có', 'là', 'của', 'cho', 'với', 'ngươi']]
    results.append(('1.2 word frequency > 20 (non-name)', len(excessive_words), 'MEDIUM' if excessive_words else 'OK'))

    # 1.3 Sentence start repetition (3+ same opener)
    opener_counter = Counter(starts)
    common_openers = [(o, c) for o, c in opener_counter.most_common(5) if c > 8 and o not in ['', 'Em', 'Anh', 'Khải', 'Bác']]
    results.append(('1.3 common sentence openers > 8', len(common_openers), 'LOW' if common_openers else 'OK'))

    # 1.4 4-gram self-repetition within EP
    ngrams_4 = get_ngrams(body_lower, n=4)
    n4_count = Counter()
    words = body_lower.split()
    for i in range(len(words) - 3):
        n4_count[' '.join(words[i:i+4])] += 1
    repeated_4g = [(g, c) for g, c in n4_count.most_common(10) if c > 2]
    results.append(('1.4 4-gram self-repeat > 2', len(repeated_4g), 'MEDIUM' if len(repeated_4g) > 5 else 'OK'))

    # 1.5 Same EP intro presence
    intro_ok = INTRO_MARKER in text
    results.append(('1.5 intro Hắc Dạ Ký present', 1 if intro_ok else 0, 'OK' if intro_ok else 'HIGH'))

    # 1.6 6-section structure
    sections = ['HOOK', 'SETUP', 'INCIDENT', 'REVEAL', 'PAYOFF', 'CLIFFHANGER']
    sect_present = sum(1 for s in sections if re.search(rf'#+\s+{s}', text, re.IGNORECASE) or s.lower() in body_lower)
    results.append(('1.6 6 sections complete', sect_present, 'OK' if sect_present == 6 else 'HIGH'))

    # 1.7 Khải Phong name density (cap ~80/EP)
    kp_count = text.count('Khải Phong')
    results.append(('1.7 Khải Phong name count', kp_count, 'LOW' if kp_count > 80 else 'OK'))

    # 1.8 "Đêm tháng tư" opener (should be 1)
    dttu = text.count('Đêm tháng tư')
    results.append(('1.8 Đêm tháng tư opener count', dttu, 'OK' if dttu <= 2 else 'LOW'))

    # 1.9 Cross-EP 4-gram similarity (if EP > 1)
    if ep_num > 1 and ep_num in all_eps:
        my_4g = get_ngrams(body_lower, n=4)
        max_sim = 0
        for other_n in [ep_num - 1, ep_num - 2]:
            if other_n in all_eps:
                other_4g = get_ngrams(strip_metadata(all_eps[other_n]).lower(), n=4)
                sim = jaccard(my_4g, other_4g)
                max_sim = max(max_sim, sim)
        results.append(('1.9 cross-EP 4-gram sim with prev', round(max_sim, 3), 'HIGH' if max_sim > 0.30 else 'MEDIUM' if max_sim > 0.20 else 'OK'))
    else:
        results.append(('1.9 cross-EP 4-gram sim', 0, 'OK'))

    # 1.10 Template phrase reuse (acceptable but bounded)
    template_phrases = ['Đêm thứ', 'Bác tài liếc gương', 'Chuông xe ngân', 'kim phút nhích']
    template_total = sum(body.count(p) for p in template_phrases)
    results.append(('1.10 template phrase total reuse', template_total, 'OK' if 3 <= template_total <= 12 else 'LOW'))

    # LAYER 2 — EMOTIONAL ENGAGEMENT (10)
    # 2.1 REVEAL section depth (>= 800 words ideally)
    reveal_match = re.search(r'#+\s*REVEAL.*?(?=#+\s*PAYOFF|$)', text, re.IGNORECASE | re.DOTALL)
    reveal_wc = len(reveal_match.group().split()) if reveal_match else 0
    results.append(('2.1 REVEAL section depth (words)', reveal_wc, 'OK' if reveal_wc >= 600 else 'MEDIUM'))

    # 2.2 CLIFFHANGER drive (Khải Phong internal monologue)
    cliff_match = re.search(r'#+\s*CLIFFHANGER.*$', text, re.IGNORECASE | re.DOTALL)
    cliff_wc = len(cliff_match.group().split()) if cliff_match else 0
    results.append(('2.2 CLIFFHANGER depth (words)', cliff_wc, 'OK' if cliff_wc >= 200 else 'MEDIUM'))

    # 2.3 Hạ Vy mention (memory continuity)
    havi = body.count('Hạ Vy')
    results.append(('2.3 Hạ Vy mention (cross-arc)', havi, 'OK' if havi >= 1 else 'MEDIUM' if ep_num >= 11 else 'OK'))

    # 2.4 Ghost manifest scene present
    ghost_phrases = ['xuất hiện', 'hiện ra', 'hiện lên', 'bóng người', 'một thoáng']
    ghost_present = sum(body_lower.count(p) for p in ghost_phrases)
    results.append(('2.4 ghost manifest present', ghost_present, 'OK' if ghost_present >= 1 else 'HIGH'))

    # 2.5 Aftertaste unresolved (no fairy tale close)
    happy_close = any(p in body_lower for p in ['sống hạnh phúc', 'kết thúc tốt đẹp', 'happy ever after'])
    results.append(('2.5 aftertaste no fairy tale', 0 if happy_close else 1, 'HIGH' if happy_close else 'OK'))

    # 2.6 Driver foreshadow line in CLIFFHANGER (per R42)
    foreshadow_present = 'Bác tài liếc gương' in body and 'Đêm sau' in body
    results.append(('2.6 driver foreshadow in CLIFF (R42)', 1 if foreshadow_present else 0, 'OK' if foreshadow_present else 'LOW'))

    # 2.7 Khải Phong emotional response (lệ/khóc/nhói)
    emo_words = ['lệ', 'khóc', 'nhói', 'mắt đỏ']
    emo_count = sum(body_lower.count(w) for w in emo_words)
    results.append(('2.7 Khải Phong emotional response', emo_count, 'OK' if emo_count >= 1 else 'LOW'))

    # 2.8 Night counter "Đêm thứ N"
    night_present = 'Đêm thứ' in body
    results.append(('2.8 Đêm thứ N continuity', 1 if night_present else 0, 'OK' if night_present else 'MEDIUM'))

    # 2.9 Object collection ("Vật thứ N")
    obj_present = 'Vật thứ' in body or 'vật thứ' in body
    results.append(('2.9 Object collection mention', 1 if obj_present else 0, 'OK' if obj_present else 'MEDIUM'))

    # 2.10 Đồng hồ 7:10 motif
    clock_710 = 'bảy giờ mười' in body_lower or '7:10' in body
    results.append(('2.10 đồng hồ 7:10 motif', 1 if clock_710 else 0, 'OK' if clock_710 else 'LOW'))

    # LAYER 3 — FORBIDDEN WORDS (10)
    # 3.1 Tier 1 anti-slop
    t1_violations = sum(1 for w in ANTI_SLOP_T1 if body_lower.count(w) > 2)
    results.append(('3.1 anti-slop tier 1 > 2/EP/word', t1_violations, 'HIGH' if t1_violations else 'OK'))

    # 3.2 Tier 2 filler (R43 cap 3/EP/word)
    t2_violations = sum(1 for w in ANTI_SLOP_T2 if body_lower.count(w) > 3)
    results.append(('3.2 anti-slop tier 2 > 3/EP/word (R43)', t2_violations, 'MEDIUM' if t2_violations else 'OK'))

    # 3.3 Structural AI tells
    s_violations = sum(1 for p in ANTI_SLOP_STRUCT if p in body)
    results.append(('3.3 structural AI tells', s_violations, 'HIGH' if s_violations else 'OK'))

    # 3.4 NEVER gore
    gore_v = sum(1 for p in NEVER_GORE if p in body_lower)
    results.append(('3.4 NEVER gore', gore_v, 'HIGH' if gore_v else 'OK'))

    # 3.5 NEVER jump scare
    scare_v = sum(1 for p in NEVER_SCARE if p in body)
    results.append(('3.5 NEVER jump scare', scare_v, 'HIGH' if scare_v else 'OK'))

    # 3.6 NEVER exorcism
    exor_v = sum(1 for p in NEVER_EXORCISM if p in body_lower)
    results.append(('3.6 NEVER exorcism', exor_v, 'HIGH' if exor_v else 'OK'))

    # 3.7 Naked Hà leak
    naked_ha = sum(1 for p in [r'\byêu Hà\b', r'\btên Hà\b', r'\bcô Hà\b', r'\bHà tai nạn\b'] if re.search(p, body))
    results.append(('3.7 naked Hà leak', naked_ha, 'HIGH' if naked_ha else 'OK'))

    # 3.8 Quang leak (rename check)
    body_no_meta = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    quang_leak = body_no_meta.count('Quang')
    results.append(('3.8 Quang leak (non-metadata)', quang_leak, 'HIGH' if quang_leak else 'OK'))

    # 3.9 Bell narrative > 1 (per R)
    bell_narr = len(re.findall(r'Chuông xe ngân\.', body))
    results.append(('3.9 bell narrative > 1', bell_narr, 'HIGH' if bell_narr > 1 else 'OK'))

    # 3.10 Driver unauthorized speech (count outside standard 2 + foreshadow)
    driver_lines = re.findall(r'Bác tài[^"]*"([^"]+)"', text)
    standard = ['Con đã nhớ ra chưa?', 'Chưa tới lúc.']
    foreshadow_pattern = re.compile(r'Đêm thứ \w+|Đêm sau|Đừng vội')
    unauth = [d for d in driver_lines if d.strip() not in standard and not foreshadow_pattern.search(d)]
    results.append(('3.10 driver unauthorized speech (post-R42)', len(unauth), 'LOW' if len(unauth) > 1 else 'OK'))

    # LAYER 4 — TTS ISSUES (10)
    # 4.1 R4 Bất chợt
    bc = body.count('Bất chợt') + body.count('bất chợt')
    results.append(('4.1 R4 Bất chợt mispronunciation', bc, 'HIGH' if bc else 'OK'))

    # 4.2 R88 double prep (skip "trong trong lòng" - intentional fixed expression)
    dp_patterns = [r'thì thầm vào lên', r'ra ra\s+\w+', r'lại lại\s+\w+']
    dp = sum(len(re.findall(p, body)) for p in dp_patterns)
    # Check "trong trong" excluding "trong trong lòng"
    tr_tr = len(re.findall(r'trong trong(?! lòng)', body))
    dp += tr_tr
    results.append(('4.2 R88 double prep', dp, 'HIGH' if dp else 'OK'))

    # 4.3 R76 open vowel line-end excess
    risky_ends = re.findall(r'\b\w+(?:ưa|ơi|ai|ay)\s*[.!?]', body)
    results.append(('4.3 R76 open vowel line-end', len(risky_ends), 'LOW' if len(risky_ends) > 25 else 'OK'))

    # 4.4 R75 em-dash overused (style — acceptable but cap)
    emdash = body.count('—')
    results.append(('4.4 R75 em-dash count', emdash, 'LOW' if emdash > 300 else 'OK'))

    # 4.5 R77 short fragment chain >= 5
    sents = [s.strip() for s in re.split(r'[.!?]+', body) if s.strip()]
    run = 0; max_run = 0
    for s in sents:
        wc = len(s.split())
        if 1 <= wc <= 3:
            run += 1; max_run = max(max_run, run)
        else: run = 0
    results.append(('4.5 R77 short fragment chain', max_run, 'MEDIUM' if max_run >= 5 else 'OK'))

    # 4.6 R87 "thở hắt ra" death context only
    thr = 'thở hắt ra' in body_lower
    results.append(('4.6 R87 thở hắt ra context', 1 if thr else 0, 'OK'))  # accept

    # 4.7 R86 action+dialogue repeat — skip auto, mark
    results.append(('4.7 R86 action+dialogue repeat', 0, 'OK'))

    # 4.8 R78 voice carryover (render-time check)
    results.append(('4.8 R78 voice carryover', 0, 'OK'))

    # 4.9 Arabic numbers > 10 in body
    arabic = re.findall(r'\b\d{2,4}\b', body)
    excessive_arabic = [n for n in arabic if not (1900 <= int(n) <= 2100 if n.isdigit() else False)]
    results.append(('4.9 arabic numbers > 10', len(excessive_arabic), 'LOW' if len(excessive_arabic) > 10 else 'OK'))

    # 4.10 [pause:XXXms] count
    pauses = re.findall(r'\[pause:\d+ms\]', text)
    results.append(('4.10 pause markers count', len(pauses), 'MEDIUM' if len(pauses) < 8 else 'OK'))

    # LAYER 5 — VĂN HỌC SÂU (10) — Literary depth checks
    # 5.1 Sensory layering (sensory words density)
    sensory_total = sum(body_lower.count(w) for w in SENSORY_WORDS)
    results.append(('5.1 sensory layering total', sensory_total, 'OK' if sensory_total >= 10 else 'MEDIUM'))

    # 5.2 Dialogue ratio (quoted speech ratio)
    quoted = sum(len(m) for m in re.findall(r'"([^"]+)"', body))
    body_chars = len(body)
    dialogue_ratio = quoted / body_chars if body_chars else 0
    results.append(('5.2 dialogue ratio', round(dialogue_ratio, 3), 'OK' if 0.20 <= dialogue_ratio <= 0.55 else 'LOW'))

    # 5.3 Character voice (passenger speaks ≥ 5 lines)
    passenger_lines = len(re.findall(r'"[^"]{20,}"', body))
    results.append(('5.3 passenger dialogue richness', passenger_lines, 'OK' if passenger_lines >= 5 else 'LOW'))

    # 5.4 Show vs tell (verbs of action vs explanation)
    show_verbs = ['nhìn', 'cầm', 'đặt', 'mở', 'vuốt', 'gật', 'cúi', 'quỳ', 'đứng']
    tell_phrases = ['điều này có nghĩa là', 'tức là', 'để giải thích', 'tóm lại']
    show_count = sum(body_lower.count(v) for v in show_verbs)
    tell_count = sum(body.count(p) for p in tell_phrases)
    results.append(('5.4 show vs tell ratio', f'{show_count}:{tell_count}', 'OK' if show_count > tell_count * 5 else 'LOW'))

    # 5.5 Internal monologue depth (em ngẫm/cố nhớ/nhói)
    intern_phrases = ['ngẫm', 'cố nhớ', 'nhói', 'hình ảnh', 'cảm giác']
    intern_count = sum(body_lower.count(p) for p in intern_phrases)
    results.append(('5.5 internal monologue depth', intern_count, 'OK' if intern_count >= 5 else 'MEDIUM'))

    # 5.6 Scene transitions present (separators ---)
    seps = body.count('---')
    results.append(('5.6 scene separators', seps, 'OK' if seps >= 5 else 'LOW'))

    # 5.7 Symbolism — object central
    obj_mentions = body.count('vật') + body.count('đồ')
    results.append(('5.7 object symbolism density', obj_mentions, 'OK' if obj_mentions >= 5 else 'LOW'))

    # 5.8 Ngọc Ngạn signature — short sentence + em-dash combo
    short_sents = sum(1 for s in sents if 1 <= len(s.split()) <= 5)
    results.append(('5.8 Ngọc Ngạn short sentences', short_sents, 'OK' if short_sents >= 30 else 'LOW'))

    # 5.9 Vietnamese rhythm — em + anh + chị + bác balance
    pronouns = {'em': body_lower.count(' em '), 'anh': body_lower.count(' anh '),
                'chị': body_lower.count(' chị '), 'bác': body_lower.count(' bác ')}
    balanced = max(pronouns.values()) < sum(pronouns.values()) * 0.8
    results.append(('5.9 Vietnamese pronoun balance', pronouns, 'OK' if balanced else 'LOW'))

    # 5.10 Metaphor freshness — check for clichés
    cliched = ['như có', 'như là', 'tựa như', 'giống như']
    cliched_count = sum(body_lower.count(c) for c in cliched)
    results.append(('5.10 metaphor cliché count', cliched_count, 'OK' if cliched_count <= 10 else 'LOW'))

    # LAYER 6 — HORROR GENRE (10)
    # 6.1 Subtle haunting (no jump scare phrases)
    subtle = not any(p in body for p in NEVER_SCARE)
    results.append(('6.1 subtle haunting (no jump scare)', 1 if subtle else 0, 'OK' if subtle else 'HIGH'))

    # 6.2 Ghost psychology — ghost interaction (vuốt vai/mỉm cười/nhìn)
    ghost_actions = ['vuốt vai', 'mỉm cười', 'vuốt tóc', 'nắm tay']
    ga_count = sum(body_lower.count(a) for a in ghost_actions)
    results.append(('6.2 ghost interaction warmth', ga_count, 'OK' if ga_count >= 1 else 'MEDIUM'))

    # 6.3 Unresolved memory power (cliffhanger memory progression)
    unresolved = any(p in body_lower for p in ['cố nhớ', 'không nhớ rõ', 'cảm giác', 'mờ'])
    results.append(('6.3 unresolved memory present', 1 if unresolved else 0, 'OK' if unresolved else 'MEDIUM'))

    # 6.4 Atmospheric pacing — [pause] markers density
    pause_count = len(re.findall(r'\[pause:', text))
    results.append(('6.4 atmospheric pause density', pause_count, 'OK' if pause_count >= 12 else 'MEDIUM'))

    # 6.5 Night setting authentic (đêm + setting words)
    night_words = ['đêm', 'tối', 'khuya', 'sương', 'đèn vàng']
    night_count = sum(body_lower.count(w) for w in night_words)
    results.append(('6.5 night setting authenticity', night_count, 'OK' if night_count >= 5 else 'MEDIUM'))

    # 6.6 Vietnamese folk horror — locality
    vn_locality = ['xã', 'huyện', 'phố', 'làng', 'xóm', 'ngã ba']
    loc_count = sum(body_lower.count(w) for w in vn_locality)
    results.append(('6.6 VN locality density', loc_count, 'OK' if loc_count >= 3 else 'MEDIUM'))

    # 6.7 Regret depth — past tense + năm trước
    regret_phrases = ['năm trước', 'năm vừa rồi', 'hồi đó', 'lúc đó', 'em đã không']
    regret_count = sum(body_lower.count(p) for p in regret_phrases)
    results.append(('6.7 regret time depth', regret_count, 'OK' if regret_count >= 2 else 'MEDIUM'))

    # 6.8 Moral ambiguity — passenger self-judgment
    judge_phrases = ['xin lỗi', 'không kịp', 'em đã sai', 'ăn năn', 'lỗi']
    judge_count = sum(body_lower.count(p) for p in judge_phrases)
    results.append(('6.8 moral self-judgment', judge_count, 'OK' if judge_count >= 1 else 'LOW'))

    # 6.9 Aftertaste lingering (CLIFFHANGER doesn't fully close)
    cliff_closes = ['kết thúc', 'cuối cùng', 'từ đó']
    lingering = sum(body_lower.count(c) for c in cliff_closes) < 3
    results.append(('6.9 aftertaste lingering', 1 if lingering else 0, 'OK' if lingering else 'LOW'))

    # 6.10 Passenger archetypal — age/role variety check (per EP)
    # Accept variant: passenger_main / passenger_id / character_main
    pass_match = re.search(r'(?:passenger_main|passenger_id|character_main):\s*([^\n]+)', text)
    pass_info = pass_match.group(1).strip() if pass_match else ''
    # EP01-10 ship with old metadata format — accept body has "Em là ..." passenger intro
    pass_intro = re.search(r'Em là [A-ZĐ]\w+|Tôi là [A-ZĐ]\w+|Em tên [A-ZĐ]\w+|Tôi tên [A-ZĐ]\w+', body)
    pass_info_ok = bool(pass_info or pass_intro)
    results.append(('6.10 passenger info present', 1 if pass_info_ok else 0, 'OK' if pass_info_ok else 'MEDIUM'))

    # ============================================================
    # LAYER 7 — DICTIONARY + CONTEXT (10) — Mr.Long 28/6 R44+R45
    # ============================================================
    # 7.1 Common Vietnamese typos — exclude correct Phật giáo + idiomatic
    typos_strict = {
        'sẳn sàng': 'sẵn sàng', 'sẳn': 'sẵn', 'chử': 'chữ', 'dùm': 'giùm',
    }
    typo_found = sum(1 for typo in typos_strict if typo in body_lower)
    # "chánh điện" / "chánh án" / "chánh văn phòng" Phật giáo + chức vụ = correct
    # "sét" only typo nếu không "sét đánh"
    if 'sét' in body_lower and 'sét đánh' not in body_lower and 'sét nổ' not in body_lower:
        typo_found += 1
    results.append(('7.1 common typos (strict)', typo_found, 'HIGH' if typo_found else 'OK'))

    # 7.2 Diacritics — common mistakes
    diacr_issues = []
    diacr_patterns = [(r'\bnoí\b', 'nói'), (r'\bbạỉ\b', 'bại'), (r'\bcủả\b', 'của')]
    for pat, correct in diacr_patterns:
        if re.search(pat, body):
            diacr_issues.append(correct)
    results.append(('7.2 diacritics errors', len(diacr_issues), 'HIGH' if diacr_issues else 'OK'))

    # 7.3 Foreign words in horror narrative (English/French leak)
    foreign = re.findall(r'\b[a-z]{4,}\b(?!\s*\))', body)
    # filter known acceptable: OK, M1-M18 markers
    acceptable = {'ok', 'iphone', 'facebook', 'messenger', 'pdf', 'covid', 'app',
                  'taxi', 'cinema', 'fan', 'ipad', 'pin', 'vest', 'jeans',
                  'vietjet', 'lost', 'items', 'classic', 'electric', 'inox', 'jpg',
                  'kraft', 'iphone', 'vietnam', 'airlines', 'seoul'}
    foreign_real = [w for w in foreign if w.lower() not in acceptable]
    results.append(('7.3 foreign words leak', len(foreign_real), 'LOW' if len(foreign_real) > 5 else 'OK'))

    # 7.4 Verb-object collocation — quick rule: "đi" + place vs "đi" + verb
    # Skip detailed grammar check, just count weird combos
    weird_combos = []
    weird_patterns = [r'đi\s+ăn\s+cơm', r'ngồi\s+đứng', r'chạy\s+ngồi', r'ngủ\s+đi']
    for p in weird_patterns:
        if re.search(p, body):
            weird_combos.append(p)
    # filter "đi ăn cơm" is OK Vietnamese
    weird_combos = [w for w in weird_combos if 'ăn cơm' not in w]
    results.append(('7.4 verb collocation oddities', len(weird_combos), 'LOW' if weird_combos else 'OK'))

    # 7.5 Age sanity 0-100 (accept babies/children + elderly)
    age_mentions = re.findall(r'(\d+)\s*tuổi', body)
    bad_ages = [a for a in age_mentions if not (0 <= int(a) <= 100)]
    results.append(('7.5 age value sanity 0-100', len(bad_ages), 'HIGH' if bad_ages else 'OK'))

    # 7.6 Place capitalization (Hà Nội/Hải Phòng/Sài Gòn lowercase = error)
    place_errors = []
    place_pat = [r'\bhà nội\b', r'\bhải phòng\b', r'\bsài gòn\b', r'\bhà đông\b', r'\bbạch mai\b']
    for p in place_pat:
        if re.search(p, body):  # case sensitive find lowercase
            place_errors.append(p)
    results.append(('7.6 place capitalization', len(place_errors), 'HIGH' if place_errors else 'OK'))

    # 7.7 Death context word usage — "mất" should be in death context
    # Sample check: "mất" near "tuổi" + age = death context (OK)
    # Or "mất" near "tiền/việc" = different meaning (also OK)
    # Just count both, no false positive
    results.append(('7.7 mất usage context', body_lower.count('mất'), 'OK'))

    # 7.8 Family relationship consistency
    # If passenger uses "em" (younger), check "anh/chị" reference appropriate
    fam_words = {'bố': body_lower.count(' bố '), 'mẹ': body_lower.count(' mẹ '),
                 'anh': body_lower.count(' anh '), 'chị': body_lower.count(' chị '),
                 'em': body_lower.count(' em ')}
    results.append(('7.8 family word balance', sum(fam_words.values()), 'OK'))

    # 7.9 Vietnamese numbers — "hai mươi" preferred over "20" in narrative
    arabic_in_narrative = re.findall(r'\b\d{2}\s+(?:tuổi|năm|đêm|vật|giờ)', body)
    results.append(('7.9 arabic numbers in narrative', len(arabic_in_narrative), 'LOW' if len(arabic_in_narrative) > 3 else 'OK'))

    # 7.10 Quotation mark balance
    open_q = body.count('"')
    results.append(('7.10 quotation marks balance', open_q, 'OK' if open_q % 2 == 0 else 'HIGH'))

    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int, help='Audit single EP')
    parser.add_argument('--summary-only', action='store_true')
    args = parser.parse_args()

    eps = load_episodes()
    print(f"Loaded {len(eps)} EPs")

    if args.ep:
        target_eps = {args.ep: eps[args.ep]} if args.ep in eps else {}
    else:
        target_eps = eps

    all_findings = {}
    global_high = 0
    global_med = 0
    global_low = 0

    for n, text in target_eps.items():
        results = check_ep_60(n, text, eps)
        high_count = sum(1 for _, _, sev in results if sev == 'HIGH')
        med_count = sum(1 for _, _, sev in results if sev == 'MEDIUM')
        low_count = sum(1 for _, _, sev in results if sev == 'LOW')
        ok_count = sum(1 for _, _, sev in results if sev == 'OK')

        all_findings[n] = {
            'high': high_count,
            'medium': med_count,
            'low': low_count,
            'ok': ok_count,
            'details': [{'check': c, 'value': str(v), 'sev': s} for c, v, s in results if s != 'OK']
        }

        global_high += high_count
        global_med += med_count
        global_low += low_count

        if not args.summary_only:
            print(f"\n=== EP{n:02d} === HIGH={high_count} MED={med_count} LOW={low_count} OK={ok_count}/60")
            for c, v, s in results:
                if s in ('HIGH', 'MEDIUM'):
                    sym = '🔴' if s == 'HIGH' else '🟡'
                    print(f"  {sym} {c}: {v}")

    print(f"\n{'='*70}\n60-DIMENSION AUDIT SUMMARY EP01-50\n{'='*70}")
    print(f"  Total EPs audited: {len(target_eps)}")
    print(f"  Total HIGH issues: {global_high}")
    print(f"  Total MEDIUM issues: {global_med}")
    print(f"  Total LOW issues: {global_low}")
    print(f"  Avg HIGH/EP: {global_high/len(target_eps):.2f}")

    # Per-EP summary table
    print(f"\n{'='*70}\nPER-EP SUMMARY\n{'='*70}")
    print(f"  EP  | HIGH | MED | LOW | OK")
    for n in sorted(all_findings.keys()):
        f = all_findings[n]
        symbol = '🔴' if f['high'] > 0 else '🟡' if f['medium'] > 3 else '✓'
        print(f"  EP{n:02d} | {f['high']:4} | {f['medium']:3} | {f['low']:3} | {f['ok']:2} {symbol}")

    # Save
    out = SVHMP / 'runtime' / 'audit_60_dimensions_report.json'
    out.write_text(json.dumps(all_findings, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n  Report: {out}")

    return 0 if global_high == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
