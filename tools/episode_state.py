"""R149 — Episode State Machine (Principle 2: State Machine).

States:
  draft → outline_approved → scene_planned → writing → logic_passed
       → language_passed → rendered → audio_qa_passed → production_ready → published

KHÔNG được bỏ qua bước. Transition validation enforced.

Usage:
  python tools/episode_state.py --ep 1 status
  python tools/episode_state.py --ep 1 transition --to logic_passed
  python tools/episode_state.py --ep 1 validate  # check current state requirements
"""
import sys
import argparse
import yaml
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]

STATES = [
    "draft",
    "outline_approved",
    "scene_planned",
    "writing",
    "logic_passed",
    "language_passed",
    "rendered",
    "audio_qa_passed",
    "production_ready",
    "published",
]

# Each transition requires verification of previous state
STATE_REQUIREMENTS = {
    "outline_approved": "Outline có 6 sections + hook + climax + payoff",
    "scene_planned": "bible/29_scene_contracts.yaml ready cho EP",
    "writing": "scene_planned + brief + timeline complete",
    "logic_passed": "qa_continuity + qa_fact_check + qa_ssot_diff PASS",
    "language_passed": "qa_eol_diacritic + qa_honorific + qa_repeat_action + qa_anti_generic + qa_phonetic_safe PASS",
    "rendered": "All 6 sections WAV exist + chunk_timestamps generated",
    "audio_qa_passed": "qa_post_render PASS all sections + Whisper compare (TBD)",
    "production_ready": "publish_score GATE PASS",
    "published": "Manual: Mr.Long ship",
}


def state_file(ep):
    return BASE / "output" / f"ep_{ep:02d}" / "_state.yaml"


def load_state(ep):
    sf = state_file(ep)
    if not sf.exists():
        return {"state": "draft", "history": []}
    return yaml.safe_load(sf.read_text(encoding="utf-8")) or {"state": "draft", "history": []}


def save_state(ep, data):
    sf = state_file(ep)
    sf.parent.mkdir(parents=True, exist_ok=True)
    sf.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ep", type=int, required=True)
    ap.add_argument("action", choices=["status", "transition", "validate", "reset"])
    ap.add_argument("--to", help="Target state for transition")
    args = ap.parse_args()

    data = load_state(args.ep)
    current = data["state"]

    if args.action == "status":
        idx = STATES.index(current) if current in STATES else -1
        print(f"=== EP{args.ep:02d} STATE: {current} (step {idx+1}/{len(STATES)}) ===")
        print("\nProgress:")
        for i, s in enumerate(STATES):
            marker = "✅" if i < idx else ("🔄" if i == idx else "⬜")
            print(f"  {marker} {s}")
        print("\nHistory:")
        for h in data.get("history", [])[-10:]:
            print(f"  {h['ts']} → {h['to']}")

    elif args.action == "transition":
        if not args.to:
            print("ERROR: --to required")
            sys.exit(1)
        if args.to not in STATES:
            print(f"ERROR: '{args.to}' not in valid states {STATES}")
            sys.exit(1)
        cur_idx = STATES.index(current)
        target_idx = STATES.index(args.to)
        if target_idx <= cur_idx:
            print(f"ERROR: Cannot transition backward from {current} to {args.to}")
            sys.exit(1)
        if target_idx != cur_idx + 1:
            print(f"⚠️ WARNING: Skipping intermediate states ({STATES[cur_idx+1:target_idx]})")
            print(f"   Use --force to override (not implemented — re-implement when safe)")
            sys.exit(1)
        req = STATE_REQUIREMENTS.get(args.to, "")
        print(f"Transitioning: {current} → {args.to}")
        print(f"Requirement: {req}")
        data["state"] = args.to
        data.setdefault("history", []).append({"ts": datetime.now().isoformat(), "from": current, "to": args.to})
        save_state(args.ep, data)
        print(f"✓ State updated. File: {state_file(args.ep)}")

    elif args.action == "validate":
        req = STATE_REQUIREMENTS.get(current, "(no requirement)")
        print(f"=== EP{args.ep:02d} VALIDATE current state '{current}' ===")
        print(f"Requirement: {req}")
        print(f"\nNote: Manual run required tools to verify.")

    elif args.action == "reset":
        data = {"state": "draft", "history": [{"ts": datetime.now().isoformat(), "action": "reset"}]}
        save_state(args.ep, data)
        print(f"✓ EP{args.ep:02d} reset to draft")


if __name__ == "__main__":
    main()
