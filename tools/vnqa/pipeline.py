"""
SVHMP Vietnamese QA Pipeline — Phase H (H1-H8) round 14
Lock date: 2026-06-26 (Mr.Long approve full Phase H ship)

Replace manual bible/22_anti_slop_vi.yaml với library-based QA chính xác.
Compress 8 steps thành single orchestrator + sub-checks.

Stack ($0 cost, offline-capable):
- H1: Underthesea (Apache-2.0) — tokenize + POS + sentiment
- H2: Vietnamese dictionary lookup (Wiktionary cached / small seed)
- H3: PhoBERT collocation similarity (skeleton — install model on demand)
- H4: Idiom detector (seed list từ thành ngữ corpus)
- H5: Formality classifier (heuristic baseline → fine-tune later)
- H6: PhoNLP dependency parsing (skeleton)
- H7: N-gram anomaly detector (PhoMT corpus baseline)
- H8: Orchestrator combine + emit qa_vietnamese_report.json

Apply rule cứng:
- KHÔNG bịa frequency threshold — defaults sensible + Mr.Long tune
- Mark TENTATIVE chỗ chưa fine-tune (PhoBERT, PhoMT corpus chưa download)
- VRAM safe: all CPU inference khi possible (PhoBERT-base ~500MB CPU OK)

Usage:
    python tools/vietnamese_qa_pipeline.py --episode output/ep_02/episode.md --output runtime/vietnamese_qa_ep_2.json

Output schema:
{
  "ep_number": int,
  "stats": {tokens, sentences, adverbs_count, adverbs_ratio, ...},
  "issues": [
    {"check": "H1_pos_rhythm", "severity": "warning", "evidence": "...", "suggestion": "..."}
  ],
  "verdict": "PASS | WARN | FAIL"
}
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import List, Dict

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent.parent  # tools/vnqa/pipeline.py → SVHMP_Studio (B30 fix Phase H2)

# Lazy import — heavy libraries
_underthesea = None
def _get_underthesea():
    global _underthesea
    if _underthesea is None:
        import underthesea
        _underthesea = underthesea
    return _underthesea


# ─── PHASE H2 WIRE: load resources yaml + vnsl_lexicon (round 14 Phase H2) ───
import yaml as _yaml

_RESOURCES_DIR = Path(__file__).parent / 'resources'
_DATA_DIR = SVHMP / 'data'

def _load_yaml(name):
    p = _RESOURCES_DIR / name
    if p.exists():
        try:
            return _yaml.safe_load(p.read_text(encoding='utf-8')) or {}
        except Exception:
            return {}
    return {}

def _load_lexicon():
    p = _DATA_DIR / 'vnsl_lexicon.json'
    if p.exists():
        try:
            import json as _j
            return _j.loads(p.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}

_RES_AI = _load_yaml('ai_tell_words.yaml')
_RES_IDIOM = _load_yaml('idioms_seed.yaml')
_RES_FORMAL = _load_yaml('formality_markers.yaml')
_LEXICON = _load_lexicon()

# Tier 1 AI words from yaml (fallback hardcode if yaml empty)
TIER_1_AI_WORDS = set()
for entry in (_RES_AI.get('tier_1_kill_on_sight', {}) or {}).get('words', []) or []:
    if isinstance(entry, dict) and 'word' in entry:
        TIER_1_AI_WORDS.add(entry['word'])
if not TIER_1_AI_WORDS:
    TIER_1_AI_WORDS = {
        'đột nhiên', 'bỗng nhiên', 'trong khoảnh khắc đó', 'không thể nào quên',
        'như thể', 'có lẽ', 'dường như', 'vô cùng', 'thầm lặng', 'rùng mình',
    }

# H1 token_repeat WHITELIST — proper noun + central object SVHMP horror
# Mr.Long 26/6 B29: "anh"/"đồng hồ"/"ghế"/"tay" repeat 30-72x = expected, KHÔNG flag
TOKEN_REPEAT_WHITELIST = {
    # Vietnamese pronouns (always high freq in narrative)
    'anh', 'chị', 'em', 'cô', 'chú', 'bác', 'ông', 'bà', 'cháu', 'mình', 'tôi', 'nó', 'họ',
    'con', 'mẹ', 'cha', 'bố', 'cậu', 'mợ', 'dì', 'thầy',  # B37 EP02 fix: family pronoun common
    # Character names (SVHMP recurring — auto-extend qua canon_registry future)
    'quang', 'nam', 'hà', 'khánh', 'tài',
    # Central objects + body parts (high freq expected horror narrative)
    'đồng', 'hồ', 'đồng hồ', 'ghế', 'tay', 'mắt', 'đầu', 'cổ', 'chân', 'mặt',
    'xe', 'kim', 'cửa', 'kính', 'đường', 'đèn',
    # B37 EP02 fix: passenger generic noun + common narrative verb
    'gái', 'trai', 'người', 'nhìn', 'biết', 'nói', 'hai', 'một', 'bóng',
    # Vietnamese numerals (high freq in narrative time/count)
    'ba', 'bốn', 'năm', 'mười', 'mươi', 'trăm',
    # Common adverbs/particles (B37 EP02 extension)
    'lại', 'cũng', 'chỉ', 'rồi', 'đã', 'đang', 'sẽ', 'thì', 'mà', 'nhưng',
    # B38 EP03 extension: motion + demonstrative + auxiliary
    'lên', 'vẫn', 'cái', 'này', 'đó', 'kia', 'còn', 'có', 'được', 'với',
    'không', 'thấy', 'đi', 'về', 'ra', 'vào', 'sau', 'trước',
    # B39 EP02 extension: central narrative object/action (story-specific high freq)
    'cuộn', 'đan', 'kim', 'len', 'bánh', 'chưng', 'gói', 'lá', 'dong',
}
TIER_2_CLUSTER = {
    'thoáng', 'khẽ', 'se sẽ', 'lặng lẽ', 'dần dần',
    'nhẹ nhàng', 'chậm rãi', 'vô hình', 'ánh mắt', 'khuôn mặt',
}
TIER_3_FILLER = [
    'Trong khi đó,', 'Mặt khác,', 'Đáng chú ý,', 'Đáng kể,', 'Cần lưu ý rằng',
    'Có một điều đặc biệt là', 'Thực ra,', 'Nói chung,', 'Một cách nào đó,',
]

# H4 seed idiom list (Vietnamese thành ngữ — natural use OK, cliché overuse flagged)
IDIOM_SEED = {
    'đầu xuôi đuôi lọt', 'xanh vỏ đỏ lòng', 'có công mài sắt có ngày nên kim',
    'lửa thử vàng gian nan thử sức', 'gừng càng già càng cay',
    'thấy người ta ăn khoai cũng vác mai đi đào', 'gần đất xa trời',
    'tre già măng mọc', 'một con sâu làm rầu nồi canh', 'ăn quả nhớ kẻ trồng cây',
}

# H5 formality heuristic — journalistic markers ≠ horror narrative
JOURNALISTIC_MARKERS = {
    'theo nguồn tin', 'theo báo cáo', 'được biết', 'theo đó', 'đại diện',
    'phát biểu', 'tuyên bố', 'thông báo', 'báo cáo cho biết', 'nguồn tin cho hay',
    'sự việc', 'sự kiện này', 'theo thống kê',
}

# H7 N-gram anomaly threshold (sensible defaults — Mr.Long tune sau)
NGRAM_REPETITION_MAX_PER_SENTENCE = 2  # cùng bi-gram >2x trong 1 câu = AI
SENTENCE_LEN_MAX_WORDS = 150            # Mr.Long 26/6: SVHMP literary intent, max 145 từ accepted. (TENTATIVE: Phase H2 wire genre yaml load)


class VietnameseQAChecker:
    def __init__(self, episode_text: str, ep_number: int = 0):
        self.text = episode_text
        self.ep = ep_number
        self.issues: List[Dict] = []
        self.stats: Dict = {}

    def _flag(self, check: str, severity: str, evidence: str, suggestion: str = ''):
        self.issues.append({
            'check': check,
            'severity': severity,
            'evidence': evidence[:200],
            'suggestion': suggestion,
        })

    def h1_underthesea_pos_rhythm(self):
        """POS-based AI rhythm detection: 3+ adverbs cluster, repeat tokens."""
        ut = _get_underthesea()
        tokens = ut.word_tokenize(self.text)
        pos_tags = ut.pos_tag(self.text)

        self.stats['tokens_count'] = len(tokens)
        self.stats['sentences_approx'] = self.text.count('.') + self.text.count('!') + self.text.count('?')

        # Adverb count (POS = 'R')
        adverbs = [w for w, t in pos_tags if t == 'R']
        adv_ratio = len(adverbs) / max(len(tokens), 1)
        self.stats['adverbs_count'] = len(adverbs)
        self.stats['adverbs_ratio'] = round(adv_ratio, 3)

        if adv_ratio > 0.15:  # >15% adverbs = AI flat rhythm
            self._flag('H1_pos_adverb_ratio_high', 'warning',
                       f'Adverb ratio {adv_ratio:.1%} > 15% (cụm trạng từ dày)',
                       'Giảm trạng từ filler, dùng động từ mạnh thay')

        # Repeat token detection (excluding stopwords + punct)
        STOPWORDS = {'và', 'là', 'có', 'không', 'của', 'một', 'như', 'cho', 'này', 'đó', 'với'}
        PUNCT = {',', '.', '!', '?', ':', ';', '...', '-', '"', '\''}
        token_lower = [t.lower() for t in tokens if t.lower() not in STOPWORDS and t not in PUNCT]
        token_freq = Counter(token_lower)
        for word, count in token_freq.most_common(10):
            if count >= 3 and len(word) > 2:
                if word in TOKEN_REPEAT_WHITELIST:
                    continue  # B29 fix: proper noun + central object expected high freq
                self._flag('H1_token_repeat', 'warning',
                           f'"{word}" lặp {count}x trong ep',
                           'Đa dạng từ vựng, dùng synonym')

        # Tier-1 AI word frequency
        text_lower = self.text.lower()
        for ai_word in TIER_1_AI_WORDS:
            count = text_lower.count(ai_word)
            if count > 3:  # threshold per bible/22
                self._flag('H1_tier1_overuse', 'warning',
                           f'"{ai_word}" xuất hiện {count}x (max 3 per ep)',
                           f'Thay alternatives đa dạng')

    def h2_vietnamese_dict_existence(self):
        """Wiktionary-based existence check. Skeleton — cached small seed."""
        # TENTATIVE: full Wiktionary scrape defer. Em check obvious neologisms.
        # Detect compound words AI bịa kiểu "linh hồn mưa buồn"
        ut = _get_underthesea()
        tokens = ut.word_tokenize(self.text)

        # Underthesea token có dấu '_' = compound word detected by tokenizer
        compounds = [t for t in tokens if '_' in t or ' ' in t]
        # Em không có Wiktionary full → just count + report unusual
        unusual = [c for c in compounds if len(c) > 12 and ' ' in c]
        if unusual:
            self._flag('H2_dict_unusual_compound', 'minor',
                       f'Cụm từ dài bất thường: {unusual[:3]}',
                       'TENTATIVE — Mr.Long verify trong từ điển VN')

    def h3_phobert_collocation_skeleton(self):
        """PhoBERT collocation similarity. SKELETON — model download on demand."""
        # TENTATIVE: PhoBERT-base v1 model ~500MB. Em không tự download bulk.
        # Pattern: check obvious unnatural noun+noun (vd "ánh mắt mưa")
        UNNATURAL_PATTERNS = [
            (r'ánh mắt \w+', ['mưa', 'gió', 'mây', 'sương']),  # ánh mắt không go với weather
        ]
        for pattern_re, anti_words in UNNATURAL_PATTERNS:
            matches = re.findall(pattern_re, self.text.lower())
            for m in matches:
                noun2 = m.split()[-1]
                if noun2 in anti_words:
                    self._flag('H3_collocation_unnatural', 'warning',
                               f'"{m}" — collocation không tự nhiên',
                               'TENTATIVE — install PhoBERT để verify đầy đủ')

    def h4_idiom_detection(self):
        """Detect idiom usage + flag overuse."""
        text_lower = self.text.lower()
        for idiom in IDIOM_SEED:
            count = text_lower.count(idiom)
            if count >= 2:  # idiom 1x natural, 2+ = cliché overuse
                self._flag('H4_idiom_overuse', 'minor',
                           f'Thành ngữ "{idiom}" dùng {count}x',
                           'Idiom dùng 1 lần OK, lạm dụng = cliché')

    def h5_formality_journalistic(self):
        """Heuristic formality detector — journalistic markers ≠ horror."""
        text_lower = self.text.lower()
        markers_hit = []
        for marker in JOURNALISTIC_MARKERS:
            if marker in text_lower:
                markers_hit.append(marker)
        if markers_hit:
            self._flag('H5_formality_journalistic', 'warning',
                       f'Journalistic tone markers: {markers_hit[:3]}',
                       'Horror narrative không dùng tone báo chí')

    def h6_phonlp_dependency_skeleton(self):
        """PhoNLP dependency parsing. SKELETON — install + load model on demand."""
        # TENTATIVE: PhoNLP requires download model + Java? Defer install.
        # Em check sentence length anomaly (run-on sentences = AI structure flat)
        sentences = re.split(r'[.!?]', self.text)
        for sent in sentences:
            words = sent.split()
            if len(words) > SENTENCE_LEN_MAX_WORDS:
                self._flag('H6_sentence_runon', 'warning',
                           f'Câu {len(words)} từ (max {SENTENCE_LEN_MAX_WORDS})',
                           'Cắt thành 2-3 câu ngắn để rhythm narrative')

    def h7_ngram_anomaly(self):
        """N-gram repetition detection per-sentence."""
        sentences = re.split(r'[.!?]', self.text)
        for sent in sentences:
            words = [w for w in sent.lower().split() if len(w) > 2]
            if len(words) < 4:
                continue
            # Bi-grams
            bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
            bigram_freq = Counter(bigrams)
            for bg, count in bigram_freq.most_common(3):
                if count > NGRAM_REPETITION_MAX_PER_SENTENCE:
                    self._flag('H7_ngram_repetition', 'warning',
                               f'Bi-gram "{bg}" lặp {count}x trong 1 câu',
                               'Reword câu để tránh repetition')

    def h8_collocation_lexicon(self):
        """Phase H3 round 14 — wire data/vnsl_lexicon.json _forbidden_patterns.

        Scan 4 categories: verb_misuse / phonetic_risk / logic_violations / temporal_overload.
        Each pattern là regex literal (vd 'khẽ thốt' | 'X mất.*X gọi').
        """
        if not _LEXICON:
            return  # B30 path fix safety — không noise nếu lexicon empty
        fb = _LEXICON.get('_forbidden_patterns', {}) or {}
        text_lower = self.text.lower()
        severity_map = {
            'verb_misuse': 'warning',          # R73 mâu thuẫn động từ — sửa
            'logic_violations': 'critical',     # chết rồi sao gọi — must fix
            'temporal_overload': 'warning',     # 3x đêm chunk
            'phonetic_risk': 'minor',           # /aːj/ BigVGAN — preference
        }
        for cat, items in fb.items():
            if cat == 'stop_consonant_tail':
                continue  # H9 handle riêng
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict) or 'pattern' not in item:
                    continue
                pat = item['pattern']
                try:
                    matches = re.findall(pat, text_lower, flags=re.IGNORECASE)
                except re.error:
                    continue
                if matches:
                    self._flag(f'H8_collocation_{cat}',
                               severity_map.get(cat, 'warning'),
                               f'Pattern "{pat}" match {len(matches)}x — {item.get("reason", "")}',
                               item.get('fix', ''))

    def h9_stop_consonant_tail(self):
        """Phase H3 round 14 — BigVGAN tail consonant risk word check."""
        if not _LEXICON:
            return
        fb = _LEXICON.get('_forbidden_patterns', {}) or {}
        items = fb.get('stop_consonant_tail', []) or []
        text_lower = self.text.lower()
        for item in items:
            if not isinstance(item, dict) or 'word' not in item:
                continue
            word = item['word']
            # Word boundary để tránh false positive (vd "suốt" trong "tuốt")
            count = len(re.findall(rf'\b{re.escape(word)}\b', text_lower))
            if count > 0:
                fix_ex = item.get('fix_examples', [])
                self._flag('H9_stop_consonant_tail', 'minor',
                           f'Word "{word}" xuất hiện {count}x (BigVGAN tail risk)',
                           '; '.join(fix_ex[:2]) if fix_ex else '')

    def h10_duration_range(self):
        """Phase H11 NEW (Mr.Long 27/6): word_count → estimated_runtime check.
        Range: 15-18 phút preferred (Ngọc Ngạn 155 wpm), 15-20 phút acceptable.
        < 15p = WARN (quá ngắn, mất retention), > 20p = WARN (quá dài, listener mệt).
        EP01 = GRANDFATHERED EXCEPTION (golden ref establish phase 21.2p, Mr.Long 27/6 lock)."""
        word_count = len(self.text.split())
        narration_wpm = 155
        minutes = word_count / narration_wpm
        self.stats['word_count'] = word_count
        self.stats['estimated_minutes'] = round(minutes, 1)
        if self.ep == 1:
            return  # EP01 golden ref ngoại lệ — KHÔNG flag duration
        if minutes < 15:
            self._flag('H10_duration_too_short', 'warning',
                       f'{minutes:.1f} phút (target 15-18p, max 20p)',
                       f'Expand thêm {int((15 - minutes) * narration_wpm)} từ để đạt 15p')
        elif minutes > 20:
            self._flag('H10_duration_too_long', 'warning',
                       f'{minutes:.1f} phút (max 20p)',
                       f'Cắt {int((minutes - 20) * narration_wpm)} từ để dưới 20p')
        elif minutes > 18:
            self._flag('H10_duration_above_preferred', 'minor',
                       f'{minutes:.1f} phút (preferred 15-18p, max 20p)',
                       'OK acceptable nhưng listener có thể mệt')

    def run_all(self) -> dict:
        """Run all H1-H10 checks. Return structured report."""
        try:
            self.h1_underthesea_pos_rhythm()
            self.h2_vietnamese_dict_existence()
            self.h3_phobert_collocation_skeleton()
            self.h4_idiom_detection()
            self.h5_formality_journalistic()
            self.h6_phonlp_dependency_skeleton()
            self.h7_ngram_anomaly()
            self.h8_collocation_lexicon()         # Phase H3 wire
            self.h9_stop_consonant_tail()          # Phase H3 wire
            self.h10_duration_range()              # Phase H11 NEW (Mr.Long 27/6)
        except Exception as e:
            self._flag('PIPELINE_ERROR', 'critical', str(e),
                       'Phase H pipeline fail — check log')

        # Verdict aggregate
        critical = sum(1 for i in self.issues if i['severity'] == 'critical')
        warning = sum(1 for i in self.issues if i['severity'] == 'warning')
        minor = sum(1 for i in self.issues if i['severity'] == 'minor')

        if critical:
            verdict = 'FAIL'
        elif warning >= 5:
            verdict = 'WARN'
        elif warning >= 1 or minor >= 3:
            verdict = 'WARN'
        else:
            verdict = 'PASS'

        return {
            'ep_number': self.ep,
            'phase_h_version': 'H1-H7 v1.0',
            'stats': self.stats,
            'issues': self.issues,
            'issues_count_by_severity': {
                'critical': critical, 'warning': warning, 'minor': minor,
            },
            'verdict': verdict,
            'next_action': {
                'PASS': 'Pipeline proceed to TTS',
                'WARN': 'Generator review issues, optional regen',
                'FAIL': 'REGEN required scope=language_only',
            }.get(verdict),
        }


def cli():
    parser = argparse.ArgumentParser(description='SVHMP Vietnamese QA Pipeline (Phase H round 14)')
    parser.add_argument('--episode', type=str, required=True, help='Path to episode.md')
    parser.add_argument('--output', type=str, required=True, help='Path to write JSON report')
    parser.add_argument('--ep', type=int, default=0, help='Episode number')
    args = parser.parse_args()

    with open(args.episode, encoding='utf-8') as f:
        text = f.read()

    checker = VietnameseQAChecker(text, ep_number=args.ep)
    report = checker.run_all()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✓ Vietnamese QA report: {args.output}")
    print(f"  Verdict: {report['verdict']}")
    print(f"  Issues: {report['issues_count_by_severity']}")
    print(f"  Stats: tokens={report['stats'].get('tokens_count')} adverb_ratio={report['stats'].get('adverbs_ratio')}")


if __name__ == '__main__':
    cli()
