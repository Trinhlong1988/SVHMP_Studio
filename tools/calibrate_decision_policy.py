"""calibrate_decision_policy.py — G6a D1: do THAT tren golden EP01, KHONG bia so (R195).

Doc output/ep_01/episode_golden_text.md (golden LOCKED, bible/31), tinh 12 knob cua
bp6/decision_contract.yaml bang DUNG method da ghi san trong tung knob.calibration_source.method.
Moi so deu tra duoc ve dong/cau cu the trong golden text (evidence field).

Chay: python tools/calibrate_decision_policy.py  -> in ra du lieu tinh duoc (khong tu ghi bible/42,
tranh double-write; bible/42 duoc ghi tay 1 lan doi chieu ket qua script nay, D2 validator kiem lai).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GOLDEN = REPO / "output" / "ep_01" / "episode_golden_text.md"

SECTION_RE = re.compile(
    r"^## (\d+)\. (\w+).*?—\s*(\d+):(\d+)\s*—\s*(\d+):(\d+).*$", re.MULTILINE
)
PAUSE_RE = re.compile(r"\[pause:(\d+)ms\]")


def load_text():
    return GOLDEN.read_text(encoding="utf-8")


def parse_sections(text):
    """Tra ve list dict {name, start_line, end_line, t_start_s, t_end_s, body}."""
    lines = text.splitlines()
    headers = []
    for i, line in enumerate(lines):
        m = re.match(r"^## (\d+)\. (\w+).*?—\s*(\d+):(\d+)\s*—\s*(\d+):(\d+)", line)
        if m:
            idx, name, m1, s1, m2, s2 = m.groups()
            t_start = int(m1) * 60 + int(s1)
            t_end = int(m2) * 60 + int(s2)
            headers.append({"idx": int(idx), "name": name, "line": i,
                             "t_start_s": t_start, "t_end_s": t_end})
    sections = []
    for k, h in enumerate(headers):
        start = h["line"] + 1
        end = headers[k + 1]["line"] if k + 1 < len(headers) else len(lines)
        body_lines = lines[start:end]
        # bo dong '---' phan cach va dong trong
        body = "\n".join(l for l in body_lines if l.strip() != "---")
        sections.append({**h, "body": body})
    return sections


def _is_dialogue_paragraph(p):
    """Doan van la THOAI 100% neu bat dau bang em-dash '— ' (quy uoc file nay dung xuyen suot)."""
    return p.strip().startswith("—")


def _split_embedded_dialogue(p):
    """Doan van CO CA narration + thoai nhung (vd 'X noi: — abc' hoac 'X noi ... "abc"').
    Tra ve (narration_words, dialogue_words) tach tai diem '— ' dau tien SAU vi tri 0,
    hoac tai dau ngoac kep dau tien neu co."""
    # tim '— ' khong o dau dong (embedded)
    m = re.search(r"—\s", p)
    if m and m.start() > 0:
        narration = p[: m.start()]
        dialogue = p[m.start():]
        return len(narration.split()), len(dialogue.split())
    # tim doan trong ngoac kep "..."
    m2 = re.search(r'"([^"]+)"', p)
    if m2:
        before = p[: m2.start()]
        quoted = m2.group(1)
        after = p[m2.end():]
        return len((before + " " + after).split()), len(quoted.split())
    return len(p.split()), 0


def compute_word_split(body):
    """Duyet tung doan van (paragraph, ngan cach boi dong trong), phan loai
    narration/dialogue, cong don so tu (Vietnamese token = split by whitespace)."""
    total_narration = 0
    total_dialogue = 0
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    for p in paragraphs:
        p_clean = PAUSE_RE.sub("", p).strip()
        if not p_clean:
            continue
        if p_clean.startswith("```") or p_clean.startswith("|"):
            continue  # metadata block / markdown table, khong tinh vao word count truyen
        if _is_dialogue_paragraph(p_clean):
            total_dialogue += len(p_clean.split())
        else:
            n, d = _split_embedded_dialogue(p_clean)
            total_narration += n
            total_dialogue += d
    return total_narration, total_dialogue


def compute_pause_count(body):
    return len(PAUSE_RE.findall(body))


# nguong bucket pacing du tren avg_sentence_words: TU-DINH-NGHIA nhung bam sat metadata
# THAT da co san trong chinh golden text (dong 573: 'avg_sentence_words: ~7.5 (target 7-9)')
# + bible/01 bimodal rule (cau cut 3-7 tu doi voi cau dai 60+ tu) - KHONG phai chuan ngoai bia.
PACING_THRESHOLDS = [(6.0, "nhanh"), (9.0, "vua"), (12.0, "cham")]  # >=12 -> rat_cham


def bucket_pacing(avg_sentence_words):
    for threshold, label in PACING_THRESHOLDS:
        if avg_sentence_words < threshold:
            return label
    return "rat_cham"


def compute_avg_sentence_words(body):
    """Dem so tu/cau tren toan bo doan van (narration + thoai), tach cau bang dau
    cham/hoi/than — dung lam tin hieu nhip THAT (KHONG dung wpm tu timestamp header,
    vi header time khong dang tin - xem finding trong main())."""
    clean = PAUSE_RE.sub("", body)
    clean = re.sub(r"\n\s*\n", " ", clean)
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean) if s.strip()]
    if not sentences:
        return 0.0
    total_words = sum(len(s.split()) for s in sentences)
    return total_words / len(sentences)


# Whitelist cam xuc THAT dung trong du an (bible/00 emotion_rotation + emotion_tags dau
# episode_golden_text.md dong 64) - chan false-positive tu chu thuong khac trong cell bang
# (vd 'round 2 chot' bi bat nham neu khong co whitelist).
KNOWN_EMOTIONS = {"surprised", "calm", "afraid", "sad", "melancholic", "longing",
                  "regret", "lover", "unspoken_love"}


def parse_emotion_curve_table(text):
    """Doc bang '## EMOTION CURVE v7' (markdown table) -> {SECTION_NAME: {emo: value, ...}}.
    Format dong: '| HOOK | surprised 0.40 + calm 0.30 | giu |'
    Chi lay cot 'emo focus' (cot thu 2), tach cap 'ten_cam_xuc so' bang regex, LOC qua
    KNOWN_EMOTIONS de tranh bat nham tu thuong khac trong cell (vd 'round 2')."""
    m = re.search(r"## EMOTION CURVE v7.*?\n(.*?)\n\n", text, re.DOTALL)
    if not m:
        return {}
    table_block = m.group(1)
    result = {}
    for line in table_block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 2:
            continue
        section_name = cols[0].strip("* ")
        if section_name in ("Section", "---") or set(section_name) <= {"-"}:
            continue
        emo_col = cols[1]
        emo_col = emo_col.replace("**", "")
        pairs = re.findall(r"([a-z_]+)\s*\.?\s*([\d.]+)", emo_col)
        emo_map = {}
        for name, val in pairs:
            if name not in KNOWN_EMOTIONS:
                continue
            try:
                emo_map[name] = float(val if val.startswith("0") or "." in val else "0." + val)
            except ValueError:
                continue
        if emo_map:
            result[section_name] = emo_map
    return result


# ============================================================
# FACT-REVEAL COUNT (reveal_curve / information_budget) — dem TAY co trich dan,
# khong doan mo ho (moi so deu tra duoc ve 1 cau THAT trong golden).
# Dinh nghia 'fact': 1 thong tin CU THE, MOI, lan dau xuat hien lien quan cot truyen/nhan
# vat chinh (KHONG tinh mo ta khong-gian/khong-khi thuan tuy).
# ============================================================
REVEAL_FACT_EVIDENCE = {
    "HOOK": [],  # chi thiet lap boi canh + do vat, chua nha fact cot truyen nao
    "SETUP": [
        "dong ho khong thay pin 8 nam van rung khe (bat thuong sieu nhien dau tien) - dong 154/160",
    ],
    "INCIDENT": [
        "ten nguoi ban: Ha-Vy - dong 254",
        "quan he: thuong tu nam lop muoi mot - dong 256",
        "Ha-Vy di du hoc My, tang dong ho luc tien san bay - dong 258/260",
        "Ha-Vy da mat 8 nam truoc trong 1 tai nan - dong 244",
    ],
    "REVEAL": [
        "thoi diem chinh xac Ha-Vy mat (may bay ha canh, tai nan xe tai) - dong 354/356/358",
        "gio mat trung khop gio kim dong ho dung (bay gio muoi) - dong 372/376",
        "bong phan chieu Ha-Vy trong kinh xe (xac nhan yeu to sieu nhien) - dong 408/412/414",
    ],
    "PAYOFF": [],  # tien biet, khong nha fact cot truyen moi
    "CLIFFHANGER": [
        "1 co gai moi nhat dong ho, vong lap tiep tuc - dong 502/504",
        "tai xe noi cau moi 'Chua toi luc dau chau a' (khac cau cu, bao hieu vong lap) - dong 528",
    ],
}


def compute_reveal_curve():
    return {name: len(v) for name, v in REVEAL_FACT_EVIDENCE.items()}


def main():
    text = load_text()
    sections = parse_sections(text)
    emo_table = parse_emotion_curve_table(text)

    print("=== CALIBRATE decision_policy tu golden EP01 (R195 - khong bia so) ===")
    total_narr, total_dial = 0, 0
    per_scene = []
    for s in sections:
        narr, dial = compute_word_split(s["body"])
        pauses = compute_pause_count(s["body"])
        dur_min = (s["t_end_s"] - s["t_start_s"]) / 60.0
        words = narr + dial
        wpm = words / dur_min if dur_min > 0 else 0
        avg_sent = compute_avg_sentence_words(s["body"])
        pacing = bucket_pacing(avg_sent)
        total_narr += narr
        total_dial += dial
        per_scene.append({
            "name": s["name"], "narration_words": narr, "dialogue_words": dial,
            "pause_count": pauses, "duration_min": round(dur_min, 3),
            "wpm": round(wpm, 1), "avg_sentence_words": round(avg_sent, 2),
            "pacing": pacing,
        })
        print(f"  [{s['name']:12}] narration={narr:4} dialogue={dial:4} "
              f"pause={pauses:2} dur={dur_min:.2f}min wpm={wpm:.1f} "
              f"avg_sent={avg_sent:.2f} pacing={pacing}")

    print("\n[FINDING] wpm tinh tu section-header timestamp KHONG dang tin (HOOK ra "
          "~789 wpm, mau thuan voi target 142 wpm da ghi dong 68-71 golden text) — "
          "header time la uoc luong cu, khong phai do that. -> pacing calibrate bang "
          "avg_sentence_words (metric doc lap voi timestamp), KHONG dung wpm.")

    total_words = total_narr + total_dial
    dialogue_ratio = total_dial / total_words if total_words else 0
    narration_ratio = 1 - dialogue_ratio
    scene_budget = len(sections)
    silence_budget = max(p["pause_count"] for p in per_scene) if per_scene else 0
    reveal_curve = compute_reveal_curve()
    information_budget = max(reveal_curve.values()) if reveal_curve else 0

    print(f"\ndialogue_ratio  = {dialogue_ratio:.4f}  (dialogue={total_dial}/total={total_words})")
    print(f"narration_ratio = {narration_ratio:.4f}  (1 - dialogue_ratio)")
    print(f"scene_budget    = {scene_budget}  (dem so section HOOK..CLIFFHANGER)")
    print(f"silence_budget  = {silence_budget}  (max pause-marker/scene: "
          f"{[(p['name'], p['pause_count']) for p in per_scene]})")
    print(f"reveal_curve    = {reveal_curve}")
    print(f"information_budget = {information_budget}  (max cua reveal_curve)")
    print(f"\nemotion_curve table (tu golden EMOTION CURVE v7):")
    for name, emo in emo_table.items():
        print(f"  {name}: {emo}")

    return {
        "dialogue_ratio": dialogue_ratio, "narration_ratio": narration_ratio,
        "scene_budget": scene_budget, "silence_budget": silence_budget,
        "reveal_curve": reveal_curve, "information_budget": information_budget,
        "per_scene": per_scene, "emotion_curve_table": emo_table,
    }


if __name__ == "__main__":
    main()
    sys.exit(0)
