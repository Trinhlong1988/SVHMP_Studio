"""R175 — Apply per-chunk emo override from registry.

Load bible/35_text_fix_registry.yaml#emo_overrides → match chunk by text → override.

Usage:
  python tools/spec_chunk_emo_override.py --apply
  python tools/spec_chunk_emo_override.py --scan
"""
import argparse
import json
import sys
import yaml
from pathlib import Path

BASE = Path(r"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio")
SECTIONS_DIR = BASE / "output/ep_01/sections"
REGISTRY = BASE / "bible/35_text_fix_registry.yaml"


def apply_overrides():
    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    overrides = reg.get("emo_overrides", [])
    print(f"=== R175 EMO OVERRIDE — {len(overrides)} entries ===")
    applied = 0
    for ov in overrides:
        sec = ov["section"].lower()
        match_text = ov["chunk_text_match"]
        emo = ov["emo_vector"]
        vol = ov.get("volume_scale", 1.0)
        spec_file = SECTIONS_DIR / f"spec_{sec}.json"
        if not spec_file.exists():
            print(f"  spec_{sec}.json not found")
            continue
        spec = json.loads(spec_file.read_text(encoding="utf-8"))
        for chunk in spec["sentences"]:
            if match_text in chunk.get("text", ""):
                chunk["emo_vector"] = [emo.get(k, 0.0) for k in
                                       ["happy", "angry", "sad", "afraid", "disgusted",
                                        "melancholic", "surprised", "calm"]]
                chunk["volume_scale"] = vol
                applied += 1
                print(f"  applied {ov['id']} -> {sec}: '{chunk['text'][:60]}...'")
                break
        spec_file.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nApplied {applied}/{len(overrides)}")
    return applied


def scan_dialogue_without_override():
    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    override_texts = [ov["chunk_text_match"] for ov in reg.get("emo_overrides", [])]
    print(f"=== R175 SCAN dialogue without override ===")
    print(f"  Existing overrides: {len(override_texts)}")
    flagged = []
    for spec_file in sorted(SECTIONS_DIR.glob("spec_*.json")):
        sec = spec_file.stem.replace("spec_", "")
        spec = json.loads(spec_file.read_text(encoding="utf-8"))
        for i, chunk in enumerate(spec["sentences"]):
            txt = chunk.get("text", "")
            if txt.strip().startswith("—"):
                has = any(o in txt for o in override_texts)
                if not has:
                    flagged.append((sec, i, txt[:80]))
    for sec, i, txt in flagged:
        print(f"  {sec} chunk[{i}]: {txt}")
    print(f"\n  Total dialogue without override: {len(flagged)}")
    return len(flagged)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--scan", action="store_true")
    args = ap.parse_args()
    if args.apply:
        n = apply_overrides()
        sys.exit(0)
    elif args.scan:
        n = scan_dialogue_without_override()
        sys.exit(0 if n == 0 else 1)
    else:
        print("Usage: --apply OR --scan")
        sys.exit(1)


if __name__ == "__main__":
    main()
