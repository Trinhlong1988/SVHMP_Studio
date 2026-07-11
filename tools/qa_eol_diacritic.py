"""R86 QA tool — detect EOL diacritic violations (ngã/nặng/hỏi at sentence end).
Mr.Long HARDLOCK 29/6: cấm sentence kết thúc với dấu ngã / nặng / hỏi.
Reason: BigVGAN không model accurate glottal stop -> âm cụt/hụt hơi/lệch tone.
"""
import re
import sys
import unicodedata
from pathlib import Path

BANNED_COMBINING = {0x0303: "NGA", 0x0309: "HOI", 0x0323: "NANG"}


def check_word_eol(word):
    """Check ALL chars in word for banned diacritic codepoint.
    Vietnamese diacritic on vowel may be mid-word (e.g. 'biệt' = b+i+ệ+t, dấu nặng on ệ).
    Use ord(ch) to get codepoint — NOT unicodedata.combining() which returns CCC class.
    """
    if not word:
        return None
    norm = unicodedata.normalize("NFD", word)
    for ch in norm:
        if ord(ch) in BANNED_COMBINING:
            return BANNED_COMBINING[ord(ch)]
    return None


def scan(md_path):
    text = Path(md_path).read_text(encoding="utf-8")
    # Cut at post-narration metadata sections
    # DEBT-018 R86 fix (11/7, per Mr.Long authorization TASK_DEBT018_R86_FIX_49EP.md):
    # "# CONSTITUTION CHECK" them vao - phat hien khi sua R86 cho 49 tap: EP02/03/05/10
    # dung marker nay (KHONG phai "# SELF-CHECK" nhu EP01) cho section checklist sau
    # CLIFFHANGER, truoc do KHONG duoc cat -> R86 quet nham noi dung checklist ("- ✅
    # ALWAYS...") thanh vi pham gia (da tu grep xac nhan ep_02: 3/44 vi pham la false
    # positive tu day). "# FINAL STATUS" luon dung SAU "# CONSTITUTION CHECK" trong 2
    # tap co ca 2 (ep_02/03) nen khong can them rieng.
    for marker in ("# SELF-CHECK", "# NOTES", "## NOTES", "## SELF-CHECK",
                   "# CONSTITUTION CHECK"):
        idx = text.find(marker)
        if idx >= 0:
            text = text[:idx]
    lines = text.split(chr(10))
    violations = []
    in_codeblock = False
    for lnum, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_codeblock = not in_codeblock
            continue
        if in_codeblock:
            continue
        line = stripped
        if not line or line.startswith(("#", "[", "---")):
            continue
        # Skip dialogue lines starting with — or " (character voice)
        if line.startswith(("—", '"', "'")):
            continue
        sents = re.split(r"(?<=[.!?…])\s+", line)
        for s in sents:
            s = s.strip()
            if not s:
                continue
            m = re.search(r'(\S+?)([.!?…"]*)\s*$', s)
            if not m:
                continue
            last_word = re.sub(r"[^\wÀ-ỹ]", "", m.group(1))
            if not last_word:
                continue
            tone = check_word_eol(last_word)
            if tone:
                violations.append((lnum, tone, last_word, s[:80]))
    return violations


if __name__ == "__main__":
    fp = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[1] / r'output/ep_01/episode.md')
    vio = scan(fp)
    print(f"R86 EOL violations: {len(vio)}")
    for lnum, tone, w, s in vio:
        print(f"  L{lnum} {tone} [{w}] {s}")
    sys.exit(0 if len(vio) == 0 else 1)
