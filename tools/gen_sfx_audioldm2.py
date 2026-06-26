"""
SVHMP SFX generation via AudioLDM2 local (port 7866) — Round 16

Per bible/17 source_priority tier_3: AudioLDM2 PRIMARY cho naturalistic SFX.
Per bible/05 audio_bible: 11 priority_1 + 4 priority_2 assets cho Ep01.

Usage:
  python tools/gen_sfx_audioldm2.py --asset rain_light
  python tools/gen_sfx_audioldm2.py --batch ep01_priority_1
  python tools/gen_sfx_audioldm2.py --all --dry-run

Strategy: Sau khi gen, post-process qua bible/17 step_5 pipeline (loudnorm + resample + channel fix).
"""
import os, sys, io, json, argparse, time, subprocess
from pathlib import Path
from gradio_client import Client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

ROOT = Path(__file__).parent.parent
SFX_RAW_DIR = ROOT / "assets" / "sfx" / "_raw"
AUDIOLDM2_URL = "http://127.0.0.1:7866/"
LOG_FILE = ROOT / "tools" / "sfx_audioldm2_log.yaml"

# ============================================================
# PROMPT TEMPLATES (text-to-audio for AudioLDM2)
# AudioLDM2 best with concrete, descriptive prompts
# ============================================================

SFX_PROMPTS = {
    "rain_light": {
        "prompt": "soft gentle rain falling on a wooden roof, continuous ambient, cozy bedroom atmosphere, very subtle, no thunder, no wind, hi-fi recording",
        "negative_prompt": "thunder, lightning, wind, heavy rain, storm, music, voices",
        "duration_s": 10,  # AudioLDM2 max 10s per gen; em concat loop sau
        "guidance_scale": 3.5,
        "n_candidates": 3,
        "target_loops": 3,  # gen 3 lần → concat → 30s
        "category": "ambience",
        "target_lufs": -22,
        "channels": "stereo",
        "sample_rate": 44100,
    },
    "bus_engine": {
        "prompt": "old diesel minibus engine idling at low rpm, smooth steady hum, mechanical vibration low frequency, interior cabin perspective",
        "negative_prompt": "revving, acceleration, horn, music, voices, beeping",
        "duration_s": 10,
        "guidance_scale": 3.5,
        "n_candidates": 3,
        "target_loops": 6,  # 60s total
        "category": "ambience",
        "target_lufs": -30,
        "channels": "mono",
        "sample_rate": 44100,
    },
    "wet_road": {
        "prompt": "car tires rolling on wet asphalt road, continuous swooshing water sound, smooth ambient, rainy day driving perspective",
        "negative_prompt": "splashing, big puddle, brakes, horn, music",
        "duration_s": 10,
        "guidance_scale": 3.5,
        "n_candidates": 3,
        "target_loops": 5,  # 45s
        "category": "ambience",
        "target_lufs": -26,
        "channels": "stereo",
        "sample_rate": 44100,
    },
    "bell_resonance": {
        "prompt": "single small brass bell chime, soft warm ring, gentle resonance with 1.5 second decay, no echo, intimate close microphone, no other sounds",
        "negative_prompt": "harsh, metallic clang, church bell, multiple bells, chimes, music, percussion",
        "duration_s": 2,  # short
        "guidance_scale": 4.0,
        "n_candidates": 5,  # cần pick best — Mr.Long sign-off
        "target_loops": 1,
        "category": "discrete",
        "target_lufs": -16,
        "channels": "mono",
        "sample_rate": 48000,
    },
    "yellow_lamp_hum": {
        "prompt": "old streetlamp electrical buzz, soft warm low frequency hum, vintage incandescent humming, distant ambient",
        "negative_prompt": "fluorescent flicker, high pitched whine, sparking, music",
        "duration_s": 4,
        "guidance_scale": 3.5,
        "n_candidates": 3,
        "target_loops": 1,
        "category": "discrete",
        "target_lufs": -30,
        "channels": "mono",
        "sample_rate": 44100,
    },
    "fog_split": {
        "prompt": "soft gentle wind whoosh, brief mist passing by, subtle ambient swish, very low intensity",
        "negative_prompt": "strong wind, storm, howling, voices",
        "duration_s": 2,
        "guidance_scale": 3.5,
        "n_candidates": 3,
        "target_loops": 1,
        "category": "discrete",
        "target_lufs": -28,
        "channels": "stereo",
        "sample_rate": 44100,
    },
    "door_open_bus": {
        "prompt": "vintage minibus folding door opening with soft pneumatic hiss, gentle mechanical sound, single brief action",
        "negative_prompt": "loud slam, electric beep, music, voices",
        "duration_s": 2,
        "guidance_scale": 4.0,
        "n_candidates": 3,
        "target_loops": 1,
        "category": "exit",
        "target_lufs": -22,
        "channels": "mono",
        "sample_rate": 44100,
    },
    "door_close_bus": {
        "prompt": "vintage minibus folding door closing with gentle pneumatic hiss and soft click, single brief action",
        "negative_prompt": "loud slam, electric beep, music, voices",
        "duration_s": 2,
        "guidance_scale": 4.0,
        "n_candidates": 3,
        "target_loops": 1,
        "category": "exit",
        "target_lufs": -22,
        "channels": "mono",
        "sample_rate": 44100,
    },
    "footsteps_fading": {
        "prompt": "footsteps walking away on wet pavement, slow steady pace, gradually fading into distance, single person, leather shoes",
        "negative_prompt": "running, multiple people, voices, music, splashing",
        "duration_s": 5,
        "guidance_scale": 3.5,
        "n_candidates": 3,
        "target_loops": 1,
        "category": "exit",
        "target_lufs": -26,
        "channels": "stereo",
        "sample_rate": 44100,
    },
    "piano_low_C": {
        "prompt": "single low piano note C2 sustained, soft warm gentle reverb tail, intimate close mic, single sustained tone, melancholy mood, no melody",
        "negative_prompt": "melody, chord progression, fast notes, drums, percussion, high pitched, bright",
        "duration_s": 2,
        "guidance_scale": 4.0,
        "n_candidates": 5,
        "target_loops": 1,
        "category": "music",
        "target_lufs": -22,
        "channels": "stereo",
        "sample_rate": 44100,
    },
}

BATCHES = {
    "ep01_priority_1": [
        "rain_light", "bus_engine", "bell_resonance",
        "door_open_bus", "door_close_bus", "footsteps_fading",
    ],
    "ep01_priority_2": [
        "yellow_lamp_hum", "fog_split", "wet_road", "piano_low_C",
    ],
}


def log_event(event):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"- {json.dumps(event, ensure_ascii=False)}\n")


def gen_audioldm2(asset_id, spec, client):
    """Call AudioLDM2 webui via gradio_client để gen audio."""
    print(f"\n========== {asset_id} ==========")
    print(f"  prompt: {spec['prompt'][:80]}...")
    print(f"  negative: {spec['negative_prompt'][:60]}...")
    print(f"  duration: {spec['duration_s']}s × {spec['n_candidates']} candidates")

    out_dir = SFX_RAW_DIR / spec["category"]
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = []
    for i in range(spec["n_candidates"]):
        t0 = time.time()
        # AudioLDM2 Gradio API — endpoint signature depends on webui version
        # Common params: text, neg, duration, guidance_scale, n_samples, seed
        try:
            result = client.predict(
                spec["prompt"],
                spec["negative_prompt"],
                spec["duration_s"],
                spec["guidance_scale"],
                1,  # n_samples per call (em loop n_candidates lần)
                42 + i,  # seed variant
                api_name="/predict",  # may differ; em probe after start
            )
            elapsed = time.time() - t0
            raw_path = result if isinstance(result, str) else result.get('path', str(result))
            cand_path = out_dir / f"{asset_id}_cand{i:02d}.wav"
            import shutil
            shutil.copy2(raw_path, cand_path)
            candidates.append(str(cand_path))
            print(f"  [#{i+1}/{spec['n_candidates']}] {elapsed:.1f}s → {cand_path.name}")
        except Exception as e:
            print(f"  [#{i+1}] FAIL: {e}")

    log_event({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "asset_id": asset_id,
        "n_candidates": len(candidates),
        "candidates": candidates,
    })
    return candidates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset", help="Single asset ID")
    ap.add_argument("--batch", choices=list(BATCHES.keys()))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.asset:
        targets = [args.asset]
    elif args.batch:
        targets = BATCHES[args.batch]
    elif args.all:
        targets = list(SFX_PROMPTS.keys())
    else:
        ap.print_help()
        sys.exit(1)

    print(f"[AudioLDM2 SFX Gen] Targets: {len(targets)}")

    if args.dry_run:
        for aid in targets:
            spec = SFX_PROMPTS[aid]
            print(f"\n  {aid}:")
            print(f"    prompt: {spec['prompt']}")
            print(f"    negative: {spec['negative_prompt']}")
            print(f"    {spec['duration_s']}s × {spec['n_candidates']} cands, {spec['category']}")
        return

    # Connect to AudioLDM2 webui
    print(f"\nConnecting to AudioLDM2 webui at {AUDIOLDM2_URL}...")
    client = Client(AUDIOLDM2_URL, verbose=False)

    for aid in targets:
        if aid not in SFX_PROMPTS:
            print(f"[ERROR] {aid} unknown")
            continue
        gen_audioldm2(aid, SFX_PROMPTS[aid], client)


if __name__ == "__main__":
    main()
