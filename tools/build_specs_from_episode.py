"""
build_specs_from_episode.py — R194 Phase 2.5 SSOT skeleton.
Generate spec_*.json from inline annotated episode.md.

Annotation format (proposed):
  [emo:NORMAL]      → set current emotion state
  [pause:Xms]       → explicit pause after current line
  [dialogue:CHAR]   → mark line as dialogue from CHAR
  [volume:0.X]      → volume scale
  [section:NAME]    → start new section (mapped to spec_NAME.json)

Without annotations, defaults: emo=NORMAL, pause=1500ms (R94b), dialogue=false.

Phase 2.5 (this skeleton) supports:
  - Parse annotations
  - Group by section
  - Emit spec_<section>.json with sentences + emo_vector + pause + is_dialogue

NOT YET supported (future):
  - Voice profile lookup from bible/15
  - Auto-emotion classifier
  - Multi-character speaker labeling beyond explicit [dialogue:CHAR]
"""
from __future__ import annotations
import argparse, json, re, sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent

SECTION_RE = re.compile(r"\[section:([A-Z_]+)\]")
EMO_RE = re.compile(r"\[emo:([A-Z_]+)\]")
PAUSE_RE = re.compile(r"\[pause:(\d+)ms\]")
DIALOGUE_RE = re.compile(r"\[dialogue:([A-Z_]+)\]")
VOLUME_RE = re.compile(r"\[volume:([0-9.]+)\]")

DEFAULT_EMO_VECTOR = [0.0, 0.0, 0.1, 0.1, 0.0, 0.2, 0.0, 0.6]


@dataclass
class Chunk:
    text: str
    emo_vector: list[float] = field(default_factory=lambda: list(DEFAULT_EMO_VECTOR))
    pause_after_ms: int = 1500
    is_dialogue: bool = False
    dialogue_char: str | None = None
    volume_scale: float | None = None


def load_voice_bible() -> dict:
    if yaml is None:
        return {}
    p = REPO_ROOT / "bible" / "15_voice_bible.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def emo_vector_for_state(state: str, voice_bible: dict) -> list[float]:
    states = voice_bible.get("states", {})
    if state in states:
        v = states[state].get("default_emotion_vector")
        if v and len(v) == 8:
            return list(v)
    return list(DEFAULT_EMO_VECTOR)


def parse_episode(md_path: Path, voice_bible: dict) -> dict[str, list[Chunk]]:
    text = md_path.read_text(encoding="utf-8")
    sections: dict[str, list[Chunk]] = {}
    current_section = "DEFAULT"
    current_emo = "NORMAL"
    current_pause = 1500

    sections.setdefault(current_section, [])

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith(">") or line.startswith("```"):
            continue
        if line.startswith("---") or line.startswith("|"):
            continue

        m_sec = SECTION_RE.search(line)
        if m_sec:
            current_section = m_sec.group(1)
            sections.setdefault(current_section, [])
            line = SECTION_RE.sub("", line).strip()
            if not line:
                continue

        m_emo = EMO_RE.search(line)
        if m_emo:
            current_emo = m_emo.group(1)
            line = EMO_RE.sub("", line).strip()

        m_pause_explicit = PAUSE_RE.search(line)
        next_pause = current_pause
        if m_pause_explicit:
            next_pause = int(m_pause_explicit.group(1))
            line_clean = PAUSE_RE.sub("", line).strip()
            if line_clean:
                line = line_clean
            else:
                continue

        m_dial = DIALOGUE_RE.search(line)
        dial_char = m_dial.group(1) if m_dial else None
        if m_dial:
            line = DIALOGUE_RE.sub("", line).strip()

        m_vol = VOLUME_RE.search(line)
        vol = float(m_vol.group(1)) if m_vol else None
        if m_vol:
            line = VOLUME_RE.sub("", line).strip()

        if not line:
            continue

        chunk = Chunk(
            text=line,
            emo_vector=emo_vector_for_state(current_emo, voice_bible),
            pause_after_ms=next_pause,
            is_dialogue=bool(dial_char) or line.startswith("—"),
            dialogue_char=dial_char,
            volume_scale=vol,
        )
        sections[current_section].append(chunk)

    return sections


def emit_spec_files(sections: dict[str, list[Chunk]], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for section_name, chunks in sections.items():
        if not chunks:
            continue
        spec = {
            "sentences": [
                {
                    "text": c.text,
                    "emo_vector": c.emo_vector,
                    "pause_after_ms": c.pause_after_ms,
                    "is_dialogue": c.is_dialogue,
                    **({"dialogue_char": c.dialogue_char} if c.dialogue_char else {}),
                    **({"volume_scale": c.volume_scale} if c.volume_scale is not None else {}),
                }
                for c in chunks
            ],
            "ssot_generated": True,
            "ssot_source_md": "episode.md",
            "rule_ref": "R194 ssot_generate_not_sync",
        }
        out_path = output_dir / f"spec_{section_name.lower()}.json"
        out_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        written[section_name] = out_path
    return written


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", type=int, required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args()

    ep_dir = REPO_ROOT / "output" / f"ep_{args.episode:02d}"
    md_path = ep_dir / "episode.md"
    output_dir = Path(args.output_dir) if args.output_dir else (ep_dir / "sections_ssot")

    if not md_path.exists():
        print(f"[R194] FAIL — missing {md_path}")
        return 2

    voice_bible = load_voice_bible()
    sections = parse_episode(md_path, voice_bible)

    print(f"[R194] parsed {sum(len(v) for v in sections.values())} chunks across {len(sections)} sections")
    for name, chunks in sections.items():
        n_dialogue = sum(1 for c in chunks if c.is_dialogue)
        print(f"  section {name}: chunks={len(chunks)}  dialogue={n_dialogue}")

    if args.dry_run:
        print("[R194] DRY-RUN only — no files written")
        return 0

    written = emit_spec_files(sections, output_dir)
    print(f"[R194] wrote {len(written)} spec files to {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
