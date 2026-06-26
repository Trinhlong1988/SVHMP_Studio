"""
CMD TTS ADAPTER v1.0 — implementation per SVHMP-TTSA-1.0 spec
Spec: prompts/tts_adapter.md

Entry:
    python tts_adapter.py --input output/ep_01/episode.md --output_dir output/ep_01/tts_adapted/

Rules R-1 → R-12, Missions M-1 → M-8, QA checklist 12 items.
Rule-based + bounded substitution (no external LLM) for R-12 idempotent.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
import io
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable

import yaml

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

ADAPTER_VERSION = "SVHMP-TTSA-1.0"
TZ_VN = timezone(timedelta(hours=7))

# ===================================================================
# Normalize dictionary (M-6 / R-7)
# ===================================================================

NORMALIZE_DIGIT_WORDS = {
    "0": "không", "1": "một", "2": "hai", "3": "ba", "4": "bốn",
    "5": "năm", "6": "sáu", "7": "bảy", "8": "tám", "9": "chín",
    "10": "mười", "11": "mười một", "12": "mười hai", "13": "mười ba",
    "14": "mười bốn", "15": "mười lăm", "16": "mười sáu", "17": "mười bảy",
    "18": "mười tám", "19": "mười chín", "20": "hai mươi", "30": "ba mươi",
    "40": "bốn mươi", "50": "năm mươi", "60": "sáu mươi", "70": "bảy mươi",
    "80": "tám mươi", "90": "chín mươi", "100": "một trăm",
}

NORMALIZE_PHRASE_MAP = {
    # time HH:MM
    r"\b(\d{1,2}):(\d{2})\b": "_time_",
    # km
    r"\b(\d+)\s*km\b": "_km_",
    r"\b(\d+)\s*m\b": "_meter_",
    # airport codes
    r"\bJFK\b": "J F K",
    r"\bMr\.\s*": "Anh ",
    # single uppercase letter standalone (cổng B, lớp A) — keep word boundary
    r"\bcổng\s+([A-Z])\b": "_gate_",
    r"\blớp\s+([A-Z])\b": "_class_",
    # ép-side number suffix
    r"\bep\s*0?(\d+)\b": "_ep_",
}

LETTER_TO_VN = {
    "A": "A", "B": "Bê", "C": "Xê", "D": "Đê", "E": "E", "F": "Ép",
    "G": "Gờ", "H": "Hát", "I": "I", "J": "Giây", "K": "Ka", "L": "Lờ",
    "M": "Em", "N": "En", "O": "O", "P": "Pê", "Q": "Quy", "R": "Rờ",
    "S": "Ét", "T": "Tê", "U": "U", "V": "Vê", "W": "Vê đúp",
    "X": "Ích", "Y": "I-cờ-rét", "Z": "Dét",
}


def number_to_vn(num: int) -> str:
    """Convert int 0..999 to Vietnamese reading."""
    if num in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
        return NORMALIZE_DIGIT_WORDS[str(num)]
    if 11 <= num <= 19:
        return "mười " + NORMALIZE_DIGIT_WORDS[str(num - 10)] if num != 15 else "mười lăm"
    if 20 <= num <= 99:
        tens, ones = divmod(num, 10)
        out = NORMALIZE_DIGIT_WORDS[str(tens * 10)] if tens * 10 in (20, 30, 40, 50, 60, 70, 80, 90) else f"{NORMALIZE_DIGIT_WORDS[str(tens)]} mươi"
        if ones == 0:
            return out
        if ones == 1:
            return f"{out} mốt"
        if ones == 5:
            return f"{out} lăm"
        return f"{out} {NORMALIZE_DIGIT_WORDS[str(ones)]}"
    if 100 <= num <= 999:
        hundreds, rest = divmod(num, 100)
        out = f"{NORMALIZE_DIGIT_WORDS[str(hundreds)]} trăm"
        if rest == 0:
            return out
        if rest < 10:
            return f"{out} lẻ {NORMALIZE_DIGIT_WORDS[str(rest)]}"
        return f"{out} {number_to_vn(rest)}"
    return str(num)


def normalize_text(text: str, sub_log: list) -> str:
    """M-6 Apply R-7 Latin/digit normalization."""
    out = text

    # Time HH:MM
    def time_repl(m):
        h, mm = int(m.group(1)), int(m.group(2))
        sub_log.append({"from": m.group(0), "to": f"{number_to_vn(h)} giờ {number_to_vn(mm)}", "rule": "time"})
        return f"{number_to_vn(h)} giờ {number_to_vn(mm)}"
    out = re.sub(r"\b(\d{1,2}):(\d{2})\b", time_repl, out)

    # N km → "N cây số" (natural Vietnamese; IndexTTS2 đọc tự nhiên hơn "ki-lô-mét")
    def km_repl(m):
        n = int(m.group(1))
        sub_log.append({"from": m.group(0), "to": f"{number_to_vn(n)} cây số", "rule": "km"})
        return f"{number_to_vn(n)} cây số"
    out = re.sub(r"\b(\d+)\s*km\b", km_repl, out)

    # JFK
    if "JFK" in out:
        sub_log.append({"from": "JFK", "to": "J F K", "rule": "airport"})
        out = out.replace("JFK", "J F K")

    # "La Mã" → "La-mã" (TTS đọc rõ "Mã" hơn khi có hyphen)
    if "La Mã" in out:
        count = out.count("La Mã")
        sub_log.append({"from": "La Mã", "to": "La-mã", "rule": "roman_numeral", "count": count})
        out = out.replace("La Mã", "La-mã")

    # Anti-repetition: "ngăn kéo" → "ngăn bàn" (avoid "kéo" repetition → TTS hallucinate)
    if "ngăn kéo" in out:
        count = out.count("ngăn kéo")
        sub_log.append({"from": "ngăn kéo", "to": "ngăn bàn", "rule": "anti_repeat_drawer", "count": count})
        out = out.replace("ngăn kéo", "ngăn bàn")

    # Phát âm clarity: "Mười một hành khách khác" → "Mười một hành khách"
    if "Mười một hành khách khác" in out:
        count = out.count("Mười một hành khách khác")
        sub_log.append({"from": "Mười một hành khách khác", "to": "Mười một hành khách",
                       "rule": "clarity_phrasing", "count": count})
        out = out.replace("Mười một hành khách khác", "Mười một hành khách")

    # Phát âm clarity: "không nghĩ đến cây cầu" → "không còn nhớ về cây cầu"
    if "không nghĩ đến cây cầu" in out:
        count = out.count("không nghĩ đến cây cầu")
        sub_log.append({"from": "không nghĩ đến cây cầu", "to": "không còn nhớ về cây cầu",
                       "rule": "clarity_phrasing", "count": count})
        out = out.replace("không nghĩ đến cây cầu", "không còn nhớ về cây cầu")

    # Anti-merge: "Quang không quay." (3 từ) merge với câu kế → "không quay trên ghế" confuse
    # Add object → "Quang không quay đầu lại." (5 từ, semantic rõ + still mergeable)
    if "Quang không quay." in out:
        count = out.count("Quang không quay.")
        sub_log.append({"from": "Quang không quay.", "to": "Quang không quay đầu lại.",
                       "rule": "anti_merge_clarity", "count": count})
        out = out.replace("Quang không quay.", "Quang không quay đầu lại.")

    # Anti-repetition: "bé lại" + "Bé như" echo → TTS hallucinate "bé lại bé"
    # Rewrite câu 2 to drop "Bé" duplicate
    if "Bé như cậu sinh viên năm hai" in out:
        count = out.count("Bé như cậu sinh viên năm hai")
        sub_log.append({"from": "Bé như cậu sinh viên năm hai", "to": "Như thời sinh viên năm hai",
                       "rule": "anti_repeat_be", "count": count})
        out = out.replace("Bé như cậu sinh viên năm hai", "Như thời sinh viên năm hai")

    # cổng <X> / lớp <X>
    def letter_word_repl(prefix):
        def _r(m):
            ch = m.group(1)
            vn = LETTER_TO_VN.get(ch, ch)
            sub_log.append({"from": m.group(0), "to": f"{prefix} {vn}", "rule": "letter_standalone"})
            return f"{prefix} {vn}"
        return _r
    out = re.sub(r"\bcổng\s+([A-Z])\b", letter_word_repl("cổng"), out)
    out = re.sub(r"\blớp\s+([A-Z])\b", letter_word_repl("lớp"), out)

    # Remaining digit clusters → spell out
    def digit_repl(m):
        d = m.group(0)
        try:
            vn = number_to_vn(int(d))
            sub_log.append({"from": d, "to": vn, "rule": "digit"})
            return vn
        except (ValueError, KeyError):
            return d
    out = re.sub(r"\b\d+\b", digit_repl, out)

    return out


# ===================================================================
# Parse episode.md
# ===================================================================

SECTION_HEADER_RE = re.compile(r"^##\s+(\d+)\.\s+([A-Z]+)", re.MULTILINE)
STAGE_DIRECTION_RE = re.compile(r"^\s*\[[^\]]+\]\s*$", re.MULTILINE)
YAML_FENCE_RE = re.compile(r"^```[^\n]*\n.*?\n```", re.MULTILINE | re.DOTALL)


@dataclass
class EpisodeMeta:
    ep_number: int
    prompt_version: str
    word_count_estimate: int
    estimated_duration_min: float
    raw_yaml: dict


@dataclass
class Section:
    section_num: int
    name: str           # HOOK / SETUP / INCIDENT / REVEAL / PAYOFF / CLIFFHANGER
    beat: str           # beat tag from header
    raw_text: str       # narration body, no header


def parse_episode_md(md_text: str) -> tuple[EpisodeMeta, list[Section]]:
    """Parse episode.md → meta + list of sections."""
    # Strip SELF-CHECK onwards
    if "# SELF-CHECK" in md_text:
        md_text = md_text.split("# SELF-CHECK")[0]

    # Extract first YAML fence as metadata
    meta_raw = {}
    fence_match = re.search(r"```\n(.*?)\n```", md_text, re.DOTALL)
    if fence_match:
        try:
            meta_raw = yaml.safe_load(fence_match.group(1)) or {}
        except Exception:
            # fallback: parse line: value
            for line in fence_match.group(1).splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta_raw[k.strip()] = v.strip()
        # remove fence from body
        md_text = md_text.replace(fence_match.group(0), "", 1)

    # Strip all remaining code fences
    md_text = YAML_FENCE_RE.sub("", md_text)

    # Strip stage directions [...]
    md_text = STAGE_DIRECTION_RE.sub("", md_text)

    # Strip dividers ---
    md_text = re.sub(r"^---\s*$", "", md_text, flags=re.MULTILINE)

    ep_number = int(str(meta_raw.get("ep_number", 1)).strip())
    prompt_version = str(meta_raw.get("prompt_version", "unknown")).strip()
    word_count_estimate = int(re.findall(r"\d+", str(meta_raw.get("word_count", "1800")))[0])
    dur_str = str(meta_raw.get("estimated_duration", "13"))
    dur_match = re.search(r"([\d.]+)", dur_str)
    estimated_duration_min = float(dur_match.group(1)) if dur_match else 13.0

    meta = EpisodeMeta(
        ep_number=ep_number,
        prompt_version=prompt_version,
        word_count_estimate=word_count_estimate,
        estimated_duration_min=estimated_duration_min,
        raw_yaml=meta_raw,
    )

    # Split by section headers (simple form — beat tags vary like "beat_3→beat_4")
    sections: list[Section] = []
    matches = list(re.finditer(r"^##\s+(\d+)\.\s+([A-Z_]+)", md_text, re.MULTILINE))

    for i, m in enumerate(matches):
        sec_num = int(m.group(1))
        name = m.group(2).strip()
        beat = f"beat_{sec_num}"
        # skip to end of header LINE so trailing metadata doesn't leak into text
        line_end = md_text.find("\n", m.end())
        start = line_end + 1 if line_end >= 0 else m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        raw = md_text[start:end].strip()
        sections.append(Section(section_num=sec_num, name=name, beat=beat, raw_text=raw))
    return meta, sections


# ===================================================================
# Scene mapping (R-10)
# ===================================================================

# Generator RC3.4 sections → 5 scene mapping
SCENE_MAP = [
    {"id": "scene_01", "slug": "xe_dem", "sections": ["HOOK", "SETUP"], "beat": "HOOK_SETUP",
     "profile": {"spk_prompt": "nng_sample", "emo_prompt": "nng_v3_calm",
                 "pitch_semi": -1.0, "tempo": 0.95, "default_pause": 600}},
    {"id": "scene_02", "slug": "incident", "sections": ["INCIDENT"], "beat": "INCIDENT",
     "profile": {"spk_prompt": "nng_sample", "emo_prompt": "nng_v3_calm",
                 "pitch_semi": -1.0, "tempo": 0.95, "default_pause": 600}},
    {"id": "scene_03", "slug": "reveal", "sections": ["REVEAL"], "beat": "REVEAL",
     "profile": {"spk_prompt": "nng_sample", "emo_prompt": "nng_v3_regret",
                 "pitch_semi": -1.5, "tempo": 0.88, "default_pause": 800}},
    {"id": "scene_04", "slug": "payoff", "sections": ["PAYOFF"], "beat": "PAYOFF",
     "profile": {"spk_prompt": "nng_sample", "emo_prompt": "nng_v3_melancholy",
                 "pitch_semi": -1.5, "tempo": 0.90, "default_pause": 800}},
    {"id": "scene_05", "slug": "cliffhanger", "sections": ["CLIFFHANGER"], "beat": "CLIFFHANGER",
     "profile": {"spk_prompt": "nng_sample", "emo_prompt": "nng_v3_mystery",
                 "pitch_semi": -2.0, "tempo": 0.85, "default_pause": 1000}},
]


# ===================================================================
# Sentence split + classification
# ===================================================================

@dataclass
class Sent:
    text: str
    is_dialog: bool = False        # starts with em-dash —
    is_question: bool = False
    is_punch: bool = False         # ≤4 từ (excluding dialog)
    is_regret: bool = False
    is_whisper_hint: bool = False
    is_reveal_hint: bool = False
    is_anaphora: bool = False      # part of anaphora pair (e.g. "Hà Nội đêm..." x2)
    word_count: int = 0
    para_idx: int = 0              # index of source paragraph

    def __post_init__(self):
        self.word_count = len(re.findall(r"\S+", self.text))


REGRET_PATTERNS = [
    r"không nói\b",
    r"Tôi thương.*không nói",
    r"Tôi định nói",
    r"Câu tôi định nói",
    r"Tôi gật.*sẽ nói khi",
    r"Tôi nhớ ra rồi",
    r"Tôi không nói được",
    r"Tám năm.*không mở ngăn",
    r"^—\s*Tôi sợ\.?$",
    r"Tôi sợ mở ngăn",
    r"Tôi sợ nhận ra",
    r"Trớ trêu thay",
    r"đồng hồ chỉ nhớ giờ",
    r"câu chưa kịp nói",
    r"Là lúc.*mất",
    r"đúng giờ.*mất",
]
_regret_re = re.compile("|".join(REGRET_PATTERNS))

WHISPER_HINT_PATTERNS = [r"\bkhẽ\b", r"\bthì thầm\b", r"\bnhư sợ\b", r"\bnhỏ nhẹ\b"]
_whisper_re = re.compile("|".join(WHISPER_HINT_PATTERNS), re.IGNORECASE)

REVEAL_HINT_PATTERNS = [r"\bLà lúc\b", r"\bTôi nhớ ra\b", r"\bMãi về sau.*mới biết\b", r"\bThì ra\b"]
_reveal_re = re.compile("|".join(REVEAL_HINT_PATTERNS))


def regroup_paragraphs(text: str) -> str:
    """Pre-process: Generator RC3.4 dùng blank line tách CÂU.
    Gộp các single-sentence paragraph ngắn liên tiếp thành paragraph thực
    để M-1 consolidation + R-3/R-4 detect đúng.

    Boundary (KHÔNG gộp qua): dialog em-dash, câu ≥15 từ, câu kết thúc bằng `?`,
    hoặc đã có nhiều câu trong paragraph.
    """
    raw_paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    out: list[str] = []
    buffer: list[str] = []

    def flush():
        if buffer:
            out.append(" ".join(buffer))
            buffer.clear()

    for p in raw_paras:
        sent_count = len(re.split(r"(?<=[.?!…])\s+", p))
        is_dialog = p.startswith("—")
        word_count = len(re.findall(r"\S+", p))
        is_short_single = (sent_count == 1) and (word_count < 15) and (not is_dialog)
        if is_short_single:
            buffer.append(p)
            # cap buffer size at 4 to avoid runaway paragraph
            if len(buffer) >= 4:
                flush()
        else:
            flush()
            out.append(p)
    flush()
    return "\n\n".join(out)


def split_sentences(text: str) -> list[Sent]:
    """Split text → list of Sent (paragraph-aware). Apply regroup first."""
    text = regroup_paragraphs(text)
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    sents: list[Sent] = []
    for pi, p in enumerate(paras):
        p_collapsed = re.sub(r"\s+", " ", p).strip()
        # split by sentence terminators while keeping them
        parts = re.split(r"(?<=[.?!…])\s+", p_collapsed)
        for s in parts:
            s = s.strip()
            if not s:
                continue
            is_dialog = s.startswith("—")
            is_question = s.endswith("?")
            wc = len(re.findall(r"\S+", s))
            is_punch = wc <= 4 and not is_dialog
            sent = Sent(
                text=s,
                is_dialog=is_dialog,
                is_question=is_question,
                is_punch=is_punch,
                is_regret=bool(_regret_re.search(s)),
                is_whisper_hint=bool(_whisper_re.search(s)),
                is_reveal_hint=bool(_reveal_re.search(s)),
                para_idx=pi,
            )
            sents.append(sent)
    return sents


# ===================================================================
# M-1 Sentence consolidation + M-5 Anti-repetition (rule-based)
# ===================================================================

def _detect_anaphora_prefix(a: str, b: str, min_words: int = 2) -> bool:
    """Detect anaphora: 2 sentences sharing N+ initial words (e.g. 'Hà Nội đêm…' x2)."""
    wa = a.lstrip("—").strip().split()
    wb = b.lstrip("—").strip().split()
    n = min(min_words + 1, len(wa), len(wb))
    if n < min_words:
        return False
    return wa[:min_words] == wb[:min_words]


_ECHO_STOPWORDS = {"và", "rồi", "nhưng", "mà", "hay", "thì", "là", "có", "không",
                    "anh", "tôi", "em", "cô", "ông", "bà", "người", "này", "đó",
                    "ở", "trên", "dưới", "trong", "ngoài", "với", "cho", "của",
                    "một", "hai", "ba"}


def _detect_echo(prev_text: str, curr_text: str) -> bool:
    """Echo pattern: curr_text BẮT ĐẦU bằng content word đã xuất hiện ở prev_text.
    Vd 'Anh thấy mình bé lại.' + 'Bé như cậu sinh viên năm hai.' → echo 'bé'.
    """
    def words(s):
        return [w.lower().strip(".,;:!?…—\"'") for w in s.split()]
    prev_set = set(words(prev_text)) - _ECHO_STOPWORDS
    curr = words(curr_text)
    if not curr:
        return False
    first = curr[0]
    if first in _ECHO_STOPWORDS or len(first) < 2:
        return False
    return first in prev_set


def consolidate_paragraph(sents: list[Sent], rewrite_log: list) -> list[Sent]:
    """M-1 v1.0.5: 2-phase pipeline.
    Phase 1: scan all adjacent pairs → mark anaphora/echo (preserve).
    Phase 2: compound merge skip marked pairs.
    """
    # PHASE 1: mark anaphora/echo pairs (cross-paragraph OK, must be adjacent sentence).
    for i in range(len(sents) - 1):
        # cho phép cross-paragraph nếu paragraph kế tiếp (diff ≤ 1)
        if abs(sents[i].para_idx - sents[i + 1].para_idx) > 1:
            continue
        if sents[i].is_dialog or sents[i + 1].is_dialog:
            continue
        if sents[i].is_regret or sents[i + 1].is_regret:
            continue
        if sents[i + 1].word_count > 11:
            continue
        is_anaphora = _detect_anaphora_prefix(sents[i].text, sents[i + 1].text, min_words=2)
        is_echo = _detect_echo(sents[i].text, sents[i + 1].text)
        if is_anaphora or is_echo:
            sents[i].is_anaphora = True
            sents[i + 1].is_anaphora = True
            pattern = "anaphora" if is_anaphora else "echo"
            rewrite_log.append({"rule": f"M-1-{pattern}-preserve",
                               "before": f"{sents[i].text} | {sents[i+1].text}",
                               "after": "(kept as 2 sentences w/ melancholy emph)"})

    # PHASE 2: compound merge skipping anaphora-marked pairs
    out: list[Sent] = []
    i = 0
    while i < len(sents):
        s = sents[i]
        if s.is_dialog or s.is_regret or s.word_count >= 12 or s.is_anaphora:
            out.append(s)
            i += 1
            continue

        # collect run of short non-dialog non-regret non-anaphora sents in same paragraph
        # MAX run = 2 (paired only). 3-4 câu khác mood/topic merge → flat prosody.
        # Exception: R-4 same-subject 3-câu vẫn merge bên dưới (detected separately).
        run = [s]
        j = i + 1
        while (j < len(sents) and
               sents[j].para_idx == s.para_idx and
               not sents[j].is_dialog and
               not sents[j].is_regret and
               not sents[j].is_anaphora and
               sents[j].word_count < 12 and
               len(run) < 2):
            run.append(sents[j])
            j += 1

        # R-4 same-subject 3-câu lookahead (Hà cười. Hà vẫy tay. Hà mất hút.)
        same_subj_extra = (
            len(run) == 2 and
            j < len(sents) and
            sents[j].para_idx == s.para_idx and
            not sents[j].is_dialog and
            not sents[j].is_regret and
            not sents[j].is_anaphora and
            sents[j].word_count < 12 and
            _same_subject_pattern(s.text, sents[j].text)
        )
        if same_subj_extra:
            run.append(sents[j])
            j += 1

        # R-4 same-subject 3-sentence detection (Hà cười. Hà vẫy tay. Hà mất hút.)
        if (len(run) >= 3 and
            _same_subject_pattern(run[0].text, run[1].text) and
            _same_subject_pattern(run[0].text, run[2].text)):
            merged = _merge_same_subject(run[:3], rewrite_log)
            out.append(Sent(text=merged, para_idx=s.para_idx))
            i = i + 3
            continue

        if len(run) >= 2:
            merged = _merge_to_compound(run, rewrite_log)
            out.append(Sent(text=merged, para_idx=s.para_idx))
            i = j
            continue

        out.append(s)
        i += 1
    return out


def _strip_terminal(text: str) -> str:
    """Strip trailing . ! but preserve ? … : quotes (semantic markers)."""
    t = text.rstrip()
    if t.endswith(('"', "'", ":", "…", "?")):
        return t
    return t.rstrip(".!").rstrip()


def _merge_to_compound(run: list[Sent], log: list) -> str:
    """Merge 2-4 short sentences into 1 compound sentence with em-dash + clauses.

    Pattern:
      [first sentence] — [rest 1], [rest 2], [rest 3].

    Preserve question mark (?) if last sentence is question — KHÔNG override với "."
    """
    first = _strip_terminal(run[0].text).strip()
    rests = [_strip_terminal(s.text).strip() for s in run[1:]]
    last_chunk = rests[-1] if rests else first
    # Decide suffix: respect last sentence's ending
    if last_chunk.endswith(('"', "'", ":", "…", "?")):
        suffix = ""
    else:
        suffix = "."

    if len(run) == 2:
        merged = f"{first} — {rests[0]}{suffix}"
    else:
        has_internal_comma = any("," in t for t in rests) or "," in first
        sep = " — " if has_internal_comma else ", "
        merged = f"{first} — " + sep.join(rests) + suffix
    before = " ".join(s.text for s in run)
    log.append({"rule": "M-1-compound", "before": before, "after": merged})
    return merged


def _same_subject_pattern(a: str, b: str) -> bool:
    """Detect 'Subject + Verb' pattern with same subject."""
    wa = a.lstrip("—").strip().split()
    wb = b.lstrip("—").strip().split()
    if len(wa) < 2 or len(wb) < 2:
        return False
    return wa[0] == wb[0]


def _merge_short_run(run: list[Sent], log: list) -> tuple[str, str]:
    """R-3: gộp 3-4 câu ngắn thành 1-2 câu."""
    texts = [s.text.rstrip(".!?…") for s in run]
    before = " ".join(s.text for s in run)
    if len(run) <= 3:
        # join all with ", ", capitalize first
        merged = texts[0] + ", " + ", ".join(t[0].lower() + t[1:] if t else t for t in texts[1:]) + "."
        log.append({"rule": "R-3", "before": before, "after": merged})
        return merged, ""
    # 4+: split 2+rest
    first = texts[0] + ", " + (texts[1][0].lower() + texts[1][1:] if texts[1] else "") + "."
    rest_texts = texts[2:]
    second = rest_texts[0] + ", " + ", ".join(t[0].lower() + t[1:] if t else t for t in rest_texts[1:]) + "."
    merged_combo = first + " | " + second
    log.append({"rule": "R-3", "before": before, "after": merged_combo})
    return first, second


def _merge_same_subject(run: list[Sent], log: list) -> str:
    """R-4: 'Hà cười. Hà vẫy tay. Hà mất hút.' → 'Hà cười, rồi khẽ vẫy tay, trước khi mất hút.'"""
    subject = run[0].text.lstrip("—").strip().split()[0]
    rests = []
    for s in run:
        words = s.text.lstrip("—").strip().rstrip(".!?…").split()
        rests.append(" ".join(words[1:]))
    if len(rests) == 2:
        merged = f"{subject} {rests[0]}, rồi {rests[1]}."
    else:
        joiners = ["", ", rồi khẽ ", ", trước khi "]
        merged = f"{subject} {rests[0]}" + joiners[1] + rests[1] + joiners[2] + rests[2] + "."
    before = " ".join(s.text for s in run)
    log.append({"rule": "R-4", "before": before, "after": merged})
    return merged


# ===================================================================
# M-4 Emphasis tagging
# ===================================================================

def assign_emph(sents: list[Sent], scene_id: str) -> list[tuple[Sent, str | None]]:
    """Return list of (sent, emph_label_or_None)."""
    tagged: list[tuple[Sent, str | None]] = []
    in_flashback = False
    for s in sents:
        emph = None
        # flashback detection: paragraph starts with "Trong đầu anh" or similar
        if re.search(r"^Trong đầu\b", s.text) or re.search(r"^Trong tâm trí\b", s.text):
            in_flashback = True
        # exit flashback on dialog or scene transition cue
        if in_flashback and (s.is_dialog or re.search(r"^Quang (mở mắt|ngừng|nhắm)", s.text)):
            in_flashback = False

        if in_flashback:
            emph = "flashback"
        elif s.is_regret and scene_id in ("scene_03", "scene_04"):
            emph = "regret_climax"
        elif s.is_reveal_hint:
            emph = "reveal"
        elif s.is_anaphora:
            emph = "melancholy"
        elif s.is_whisper_hint:
            emph = "whisper"
        elif s.is_punch and scene_id == "scene_03":
            emph = "punch"
        elif s.is_question:
            emph = "question"
        tagged.append((s, emph))
    return tagged


# ===================================================================
# M-2 Pause insertion
# ===================================================================

PAUSE_MS = {
    "micro": 300,
    "short": 600,
    "medium": 1300,    # 1300 triggers '...' in parse_scene (paragraph boundary dramatic)
    "regret_before": 1500,
    "regret_after": 2000,
    "ending": 3000,
    "punch_after": 1200,
}


def decide_pause(curr: Sent, nxt: Sent | None, is_para_end: bool, is_scene_end: bool,
                 default_pause_ms: int) -> int:
    """Pick pause ms after curr based on context."""
    if is_scene_end:
        return PAUSE_MS["ending"]
    if nxt is None:
        return PAUSE_MS["medium"]
    # Anaphora / echo pair:
    # - Short anchor (≤3 từ "Tám năm.") → 800ms em-dash (continuous, dramatic short)
    # - Longer anchor ("Hà Nội đêm tháng tư.") → 1400ms ellipsis (dramatic break to avoid TTS repetition)
    if curr.is_anaphora and nxt.is_anaphora:
        return 800 if curr.word_count <= 3 else 1400
    # regret transitions
    if nxt.is_regret:
        return PAUSE_MS["regret_before"]
    if curr.is_regret:
        return PAUSE_MS["regret_after"]
    if curr.is_punch:
        return PAUSE_MS["punch_after"]
    if is_para_end:
        # Paragraph boundary → 800ms em-dash (continuous flow, không quá dài)
        return max(800, default_pause_ms)
    return PAUSE_MS["micro"]


# ===================================================================
# Brand intro (R-11)
# ===================================================================

BRAND_INTRO_TEXT = """[emph:whisper] Kính chào quý thính giả. [pause:1000ms]

Có những câu chuyện chỉ kể được lúc đêm khuya — khi đèn đã tắt, khi mưa còn rơi ngoài cửa kính, khi lòng người chưa kịp ngủ. [pause:1500ms]

Đêm nay, qua giọng đọc của tác giả Khánh An, xin gửi tới quý vị một loạt truyện ma. [pause:1000ms] Những câu chuyện về điều người ta giấu kín, về những lời chưa kịp nói. [pause:1500ms]

[emph:whisper] Xin mời quý thính giả... cùng tôi lắng nghe. [pause:2500ms]
"""


def make_episode_title_block(ep_number: int, episode_title: str) -> str:
    """Title block với emphasis + ellipsis pause to give weight to episode name."""
    return (
        f"[emph:reveal] Tập {number_to_vn(ep_number)}. [pause:1500ms] "
        f"{episode_title}. [pause:2500ms]\n"
    )


# ===================================================================
# Scene rendering
# ===================================================================

@dataclass
class RenderedScene:
    id: str
    slug: str
    file_name: str
    text: str
    word_count: int
    pause_markup_count: int
    emph_markup_count: int
    estimated_duration_sec: float
    profile: dict


def render_scene(scene_spec: dict, sections: list[Section],
                 rewrite_log: list, sub_log: list,
                 violations: list) -> RenderedScene:
    # Concat raw_text of all matching sections
    joined = "\n\n".join(sec.raw_text for sec in sections if sec.name in scene_spec["sections"])
    # Normalize first (M-6) so word counts reflect spoken text
    joined = normalize_text(joined, sub_log)

    # Sentence split + para-aware
    sents = split_sentences(joined)

    # M-1 + M-5
    sents = consolidate_paragraph(sents, rewrite_log)

    # Re-detect flags after merge (some merged sents lose regret detection)
    for s in sents:
        s.is_regret = bool(_regret_re.search(s.text))
        s.is_whisper_hint = bool(_whisper_re.search(s.text))
        s.is_reveal_hint = bool(_reveal_re.search(s.text))
        s.is_dialog = s.text.startswith("—")
        s.is_question = s.text.endswith("?")
        s.word_count = len(re.findall(r"\S+", s.text))
        s.is_punch = s.word_count <= 4 and not s.is_dialog

    # M-4 emph tagging
    tagged = assign_emph(sents, scene_spec["id"])

    # R-3 violation count
    short_run = 0
    rule3_violations = 0
    for s in sents:
        if s.word_count < 6 and not s.is_dialog:
            short_run += 1
            if short_run > 3:
                rule3_violations += 1
        else:
            short_run = 0
    if rule3_violations > 0:
        violations.append({
            "rule": "R-3", "scene": scene_spec["id"],
            "detail": f"{rule3_violations} run(s) of >3 short sentences after rewrite"
        })

    # Render with pauses; paragraph-scope emph (EC-3): same label in same paragraph emits tag once
    default_pause = scene_spec["profile"]["default_pause"]
    rendered_lines: list[str] = []
    pause_count = 0
    emph_count = 0
    n = len(tagged)
    prev_para_idx = -1
    prev_para_emph: str | None = None
    for i, (s, emph) in enumerate(tagged):
        para_end = (i + 1 == n) or (tagged[i + 1][0].para_idx != s.para_idx)
        scene_end = (i + 1 == n)
        nxt = tagged[i + 1][0] if i + 1 < n else None
        pause = decide_pause(s, nxt, para_end, scene_end, default_pause)

        # paragraph-scope emph: emit tag only on first sentence of paragraph,
        # OR when emph changes mid-paragraph (vd dialog interrupt flashback)
        emit_emph = False
        if emph:
            new_para = s.para_idx != prev_para_idx
            changed = emph != prev_para_emph
            if new_para or changed:
                emit_emph = True
            prev_para_emph = emph
        else:
            prev_para_emph = None
        prev_para_idx = s.para_idx

        prefix = f"[emph:{emph}] " if emit_emph else ""
        if emit_emph:
            emph_count += 1
        line = f"{prefix}{s.text} [pause:{pause}ms]"
        pause_count += 1
        rendered_lines.append(line)
        if para_end and not scene_end:
            rendered_lines.append("")  # paragraph break

    text = "\n".join(rendered_lines).rstrip() + "\n"
    word_count = sum(s.word_count for s, _ in tagged)
    # estimated duration: 140 wpm + pause sum / 1000
    pause_total_sec = sum(decide_pause(s, (tagged[i + 1][0] if i + 1 < n else None),
                                        (i + 1 == n or tagged[i + 1][0].para_idx != s.para_idx),
                                        i + 1 == n, default_pause) / 1000
                          for i, (s, _) in enumerate(tagged))
    est_dur = (word_count / 140 * 60) + pause_total_sec

    return RenderedScene(
        id=scene_spec["id"],
        slug=scene_spec["slug"],
        file_name=f"{scene_spec['id']}_{scene_spec['slug']}.txt",
        text=text,
        word_count=word_count,
        pause_markup_count=pause_count,
        emph_markup_count=emph_count,
        estimated_duration_sec=est_dur,
        profile=scene_spec["profile"],
    )


# ===================================================================
# QA checklist
# ===================================================================

def qa_check(scene_files: list[Path], yaml_path: Path, scenes: list[RenderedScene],
             total_estimated_min: float) -> tuple[bool, list[str]]:
    issues: list[str] = []

    # 1. 5 scene files exist
    if len(scene_files) != 5:
        issues.append(f"QA-1: expected 5 scene files, got {len(scene_files)}")
    # 2. each scene has ≥1 pause markup
    for f in scene_files:
        t = f.read_text(encoding="utf-8")
        if "[pause:" not in t:
            issues.append(f"QA-2: {f.name} missing pause markup")
    # 3. no 3+ blank lines
    for f in scene_files:
        t = f.read_text(encoding="utf-8")
        if re.search(r"\n\n\n+", t):
            issues.append(f"QA-3: {f.name} has 3+ consecutive blank lines")
    # 4. no metadata residue
    forbidden = ["## ", "---", "# SELF-CHECK", "[chuông", "[beat_", "```"]
    for f in scene_files:
        t = f.read_text(encoding="utf-8")
        for fb in forbidden:
            if fb in t:
                issues.append(f"QA-4: {f.name} contains forbidden '{fb}'")
                break
    # 5. no single-letter standalone (allowed: J F K in airport context)
    allow_letters_re = re.compile(r"J F K")
    for f in scene_files:
        t = f.read_text(encoding="utf-8")
        t_clean = allow_letters_re.sub("", t)
        bad = re.findall(r"\b[A-Z]\b", t_clean)
        if bad:
            issues.append(f"QA-5: {f.name} has stray uppercase letters: {bad[:5]}")
    # 6. no digit
    for f in scene_files:
        t = f.read_text(encoding="utf-8")
        # exclude inside pause/emph markup
        t_clean = re.sub(r"\[pause:\d+ms\]", "", t)
        digits = re.findall(r"\d", t_clean)
        if digits:
            issues.append(f"QA-6: {f.name} has stray digits: {digits[:5]}")
    # 10. yaml valid
    try:
        yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except Exception as e:
        issues.append(f"QA-10: invalid yaml: {e}")
    # 12. duration window 11.0 - 16.0 min (compound sentences read faster than short runs)
    if not (11.0 <= total_estimated_min <= 16.0):
        issues.append(f"QA-12: total duration {total_estimated_min:.1f}min out of 11.0-16.0 window")

    return len(issues) == 0, issues


# ===================================================================
# Main
# ===================================================================

def _vn_title_case(s: str) -> str:
    """Vietnamese title-case: first char upper, rest lower; keep proper nouns capitalized.
    Naive: first letter of string upper, rest lower. Caller handles proper nouns separately."""
    s = s.strip()
    if not s:
        return s
    return s[0].upper() + s[1:].lower()


def derive_title(meta: EpisodeMeta, raw_md: str) -> str:
    m = re.search(r"^#\s+TẬP\s+\d+\s*[—-]\s*(.+)$", raw_md, re.MULTILINE)
    if m:
        return _vn_title_case(m.group(1).strip().rstrip("."))
    return "Tập mới"


def run(input_md: Path, output_dir: Path, season: int = 1) -> int:
    raw_md = input_md.read_text(encoding="utf-8")
    meta, sections = parse_episode_md(raw_md)
    title = derive_title(meta, raw_md)
    print(f"[Adapter] ep_{meta.ep_number:02d} | sections={len(sections)} | title={title}", flush=True)

    output_dir.mkdir(parents=True, exist_ok=True)

    rewrite_log: list[dict] = []
    sub_log: list[dict] = []
    violations: list[dict] = []
    rendered: list[RenderedScene] = []

    for scene_spec in SCENE_MAP:
        rs = render_scene(scene_spec, sections, rewrite_log, sub_log, violations)
        rendered.append(rs)

    # Brand intro for ep_1 season 1 — prepend to scene_01
    brand_intro_dur = 0.0
    if meta.ep_number == 1 and season == 1:
        intro_block = BRAND_INTRO_TEXT.rstrip() + "\n\n" + make_episode_title_block(meta.ep_number, title).rstrip() + "\n\n"
        rendered[0].text = intro_block + rendered[0].text.lstrip()
        rendered[0].word_count += len(re.findall(r"\S+", intro_block))
        rendered[0].pause_markup_count += intro_block.count("[pause:")
        rendered[0].emph_markup_count += intro_block.count("[emph:")
        brand_intro_dur = 28.0
        rendered[0].estimated_duration_sec += brand_intro_dur

    # Write scene files
    scene_paths: list[Path] = []
    for rs in rendered:
        path = output_dir / rs.file_name
        path.write_text(rs.text, encoding="utf-8")
        scene_paths.append(path)
        print(f"[Adapter]   {rs.file_name}: {rs.word_count}w, {rs.pause_markup_count}p, "
              f"{rs.emph_markup_count}e, ~{rs.estimated_duration_sec:.0f}s", flush=True)

    total_word = sum(rs.word_count for rs in rendered)
    total_sec = sum(rs.estimated_duration_sec for rs in rendered)

    # episode.tts.yaml
    now_str = datetime.now(TZ_VN).strftime("%Y-%m-%dT%H:%M:%S+07")
    src_sha = hashlib.sha256(raw_md.encode("utf-8")).hexdigest()[:16]
    tts_yaml = {
        "schema_version": ADAPTER_VERSION,
        "ep_number": meta.ep_number,
        "adapter_run_at": now_str,
        "source_episode_md_sha256": src_sha,
        "brand_intro": meta.ep_number == 1 and season == 1,
        "scenes": [
            {
                "id": rs.id, "slug": rs.slug, "file": rs.file_name, "beat": SCENE_MAP[i]["beat"],
                "profile": rs.profile,
                "word_count": rs.word_count,
                "estimated_duration_sec": round(rs.estimated_duration_sec, 1),
                "pause_markup_count": rs.pause_markup_count,
                "emph_markup_count": rs.emph_markup_count,
            } for i, rs in enumerate(rendered)
        ],
        "global": {
            "brand_intro_duration_sec": brand_intro_dur,
            "total_word_count": total_word,
            "total_estimated_duration_sec": round(total_sec, 1),
        },
        "qa": {
            "pass": None,  # filled below
            "rule_violations": len(violations),
            "rewrites_applied": len(rewrite_log),
            "normalize_substitutions": len(sub_log),
            "warnings": [],
        },
    }

    # QA check
    yaml_path = output_dir / "episode.tts.yaml"
    yaml_path.write_text(yaml.dump(tts_yaml, allow_unicode=True, sort_keys=False), encoding="utf-8")

    total_min = total_sec / 60
    qa_pass, qa_issues = qa_check(scene_paths, yaml_path, rendered, total_min)
    tts_yaml["qa"]["pass"] = qa_pass
    tts_yaml["qa"]["warnings"] = qa_issues
    yaml_path.write_text(yaml.dump(tts_yaml, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # report
    report = {
        "adapter_run_at": now_str,
        "adapter_version": ADAPTER_VERSION,
        "ep_number": meta.ep_number,
        "violations": violations,
        "rewrites": rewrite_log,
        "normalize_subs": sub_log,
        "metrics": {
            "total_word_count": total_word,
            "total_estimated_duration_sec": round(total_sec, 1),
            "total_estimated_duration_min": round(total_min, 2),
            "scenes": len(rendered),
        },
        "qa_pass": qa_pass,
        "qa_issues": qa_issues,
    }
    report_path = output_dir / "tts_adapter_report.yaml"
    report_path.write_text(yaml.dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")

    print(f"[Adapter] total={total_word}w / ~{total_min:.1f}min | "
          f"rewrites={len(rewrite_log)} | normalize={len(sub_log)} | "
          f"violations={len(violations)} | qa={'PASS' if qa_pass else 'FAIL'}", flush=True)
    if not qa_pass:
        for x in qa_issues:
            print(f"  [QA] {x}", flush=True)

    return 0 if qa_pass else 1


def main():
    ap = argparse.ArgumentParser(description="SVHMP CMD TTS ADAPTER v1.0")
    ap.add_argument("--input", required=True, help="path to episode.md")
    ap.add_argument("--output_dir", required=True, help="dir to write 5 scene files + tts.yaml + report.yaml")
    ap.add_argument("--season", type=int, default=1)
    args = ap.parse_args()
    sys.exit(run(Path(args.input), Path(args.output_dir), season=args.season))


if __name__ == "__main__":
    main()
