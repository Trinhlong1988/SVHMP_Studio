"""
SVHMP SFX Acquisition Pipeline (bible/17_sfx_acquisition_pipeline.yaml)
Round 16 ship 19/6 — Mr.Long "đưa vào quy trình chặt chẽ"

8-step workflow per asset:
  1. requirement_spec     (per asset target duration / LUFS / channels)
  2. source_priority      (tier 1 CC0 → tier 2 CC-BY → tier 3 AI gen → tier 4 paid)
  3. search + preview     (collect 3-5 candidates)
  4. download             (retry 3 + politeness rate limit)
  5. processing           (ffmpeg: trim / loudnorm / resample / channel)
  6. checksum lock        (sha256 → CHECKSUMS.sha256)
  7. register             (bible/05 entry update)
  8. QA verification      (TTS M7 audit)

Usage:
  python tools/sfx_acquire.py --asset bell_resonance
  python tools/sfx_acquire.py --batch ep01_priority_1
  python tools/sfx_acquire.py --full
  python tools/sfx_acquire.py --gen-with-ace-step --asset piano_low_C
"""
import os, sys, io, json, argparse, hashlib, subprocess, time, shutil
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

ROOT = Path(__file__).parent.parent  # SVHMP_Studio/
SFX_DIR = ROOT / "assets" / "sfx"
RAW_DIR = SFX_DIR / "_raw"
LOG_FILE = ROOT / "tools" / "sfx_acquire_log.yaml"
SEARCH_LOG = ROOT / "tools" / "sfx_search_log.yaml"
CHECKSUMS_FILE = SFX_DIR / "CHECKSUMS.sha256"
ATTRIBUTIONS_FILE = SFX_DIR / "ATTRIBUTIONS.md"
FFMPEG = os.path.expanduser(r'~/ffmpeg/bin/ffmpeg.exe')
ACE_STEP_PORT = 7865

# ============================================================
# ASSET REGISTRY — per bible/17 ep01_required_assets
# ============================================================

ASSETS = {
    # ── PRIORITY 1 — must-have for Ep01 ──
    "rain_light": {
        "category": "ambience",
        "target_duration_ms": 30000,
        "target_lufs": -22,
        "target_peak_db": -3,
        "channels": "stereo",
        "sample_rate_hz": 44100,
        "loop_seamless": True,
        "search_queries": [
            "light rain on roof loop seamless",
            "soft rain ambient bedroom loop",
        ],
        "candidate_pixabay_ids": [],  # to fill from search step
    },
    "bus_engine": {
        "category": "ambience",
        "target_duration_ms": 60000,
        "target_lufs": -30,
        "target_peak_db": -6,
        "channels": "mono",
        "sample_rate_hz": 44100,
        "loop_seamless": True,
        "search_queries": [
            "bus diesel engine idle interior loop",
            "vintage minibus engine hum",
        ],
    },
    "wet_road": {
        "category": "ambience",
        "target_duration_ms": 45000,
        "target_lufs": -26,
        "target_peak_db": -6,
        "channels": "stereo",
        "sample_rate_hz": 44100,
        "loop_seamless": True,
        "search_queries": [
            "tire on wet road continuous loop",
            "car driving rain road",
        ],
    },
    "bell_resonance": {
        "category": "discrete",
        "target_duration_ms": 1500,
        "target_lufs": -16,
        "target_peak_db": -3,
        "channels": "mono",
        "sample_rate_hz": 48000,
        "search_queries": [
            "small brass bell single chime soft warm",
            "tibetan singing bowl gentle resonant",
        ],
    },
    "yellow_lamp_hum": {
        "category": "discrete",
        "target_duration_ms": 3000,
        "target_lufs": -30,
        "target_peak_db": -12,
        "channels": "mono",
        "sample_rate_hz": 44100,
        "search_queries": [
            "old street lamp electrical hum warm",
            "fluorescent buzz low gentle",
        ],
    },
    "fog_split": {
        "category": "discrete",
        "target_duration_ms": 800,
        "target_lufs": -28,
        "target_peak_db": -10,
        "channels": "stereo",
        "sample_rate_hz": 44100,
        "search_queries": [
            "soft wind whoosh subtle short",
            "mist dispersing ambient",
        ],
    },
    "door_open_bus": {
        "category": "exit",
        "target_duration_ms": 1000,
        "target_lufs": -22,
        "target_peak_db": -6,
        "channels": "mono",
        "sample_rate_hz": 44100,
        "search_queries": [
            "bus door open soft hiss vintage",
            "vehicle door slide open gentle",
        ],
    },
    "door_close_bus": {
        "category": "exit",
        "target_duration_ms": 1000,
        "target_lufs": -22,
        "target_peak_db": -6,
        "channels": "mono",
        "sample_rate_hz": 44100,
        "search_queries": [
            "bus door close gentle click vintage",
            "vehicle door slide close soft",
        ],
    },
    "footsteps_fading": {
        "category": "exit",
        "target_duration_ms": 4000,
        "target_lufs": -26,
        "target_peak_db": -10,
        "channels": "stereo",
        "sample_rate_hz": 44100,
        "search_queries": [
            "footsteps on wet pavement walking away",
            "footsteps fading distance stereo pan",
        ],
    },
    # ── BRAND SIGNATURE (bible/10 brand_audio) ──
    "brand_rain_intro_4s": {
        "category": "brand",
        "target_duration_ms": 4000,
        "target_lufs": -20,
        "target_peak_db": -3,
        "channels": "stereo",
        "sample_rate_hz": 44100,
        "build_from": "rain_light",
        "processing": "trim 0-4s + fade_in 800ms",
    },
    "brand_bell_distant": {
        "category": "brand",
        "target_duration_ms": 1800,
        "target_lufs": -16,
        "target_peak_db": -3,
        "channels": "stereo",
        "sample_rate_hz": 44100,
        "build_from": "bell_resonance",
        "processing": "reverb tail 1500ms + stereo widen",
    },
    "brand_bell_single_outro": {
        "category": "brand",
        "target_duration_ms": 1500,
        "target_lufs": -18,
        "target_peak_db": -3,
        "channels": "stereo",
        "sample_rate_hz": 44100,
        "build_from": "bell_resonance",
        "processing": "single chime + 800ms decay",
    },
    "brand_intro_template_6500ms": {
        "category": "brand",
        "target_duration_ms": 6500,
        "target_lufs": -18,
        "target_peak_db": -3,
        "channels": "stereo",
        "sample_rate_hz": 44100,
        "build_from": ["brand_rain_intro_4s", "brand_bell_distant", "bus_engine"],
        "processing": "amix sequence: rain 0-4s + bell at 3.5s overlap + engine fade-in 5s",
    },
    # ── MUSIC BEDS (transition piano) — gen via ACE-Step ──
    "piano_low_C": {
        "category": "music",
        "target_duration_ms": 1200,
        "target_lufs": -22,
        "target_peak_db": -6,
        "channels": "stereo",
        "sample_rate_hz": 44100,
        "ai_generate": True,
        "ace_step_prompt": "single low piano note C2, sustained, gentle reverb tail, no melody, melancholy, intimate",
        "ace_step_negative": "drums, percussion, beat, fast tempo, bright",
    },
}

BATCHES = {
    "ep01_priority_1": [
        "rain_light", "bus_engine", "bell_resonance",
        "door_open_bus", "door_close_bus", "footsteps_fading",
        "brand_rain_intro_4s", "brand_bell_distant", "brand_bell_single_outro",
        "brand_intro_template_6500ms",
    ],
    "ep01_priority_2": [
        "yellow_lamp_hum", "fog_split", "wet_road", "piano_low_C",
    ],
    "ep01_all": None,  # filled below
}
BATCHES["ep01_all"] = BATCHES["ep01_priority_1"] + BATCHES["ep01_priority_2"]


# ============================================================
# UTILITIES
# ============================================================

def log_event(event):
    """Append event to log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"- {json.dumps(event, ensure_ascii=False)}\n")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def ffmpeg_run(args, label="ffmpeg"):
    """Run ffmpeg with stderr capture."""
    cmd = [FFMPEG, "-y"] + args
    print(f"  [{label}] {' '.join(cmd[:6])}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [{label}] FAIL: {res.stderr[:500]}")
    return res

def get_audio_info(path):
    """Use ffmpeg to probe duration + sample rate."""
    res = subprocess.run(
        [FFMPEG, "-i", str(path), "-hide_banner"],
        capture_output=True, text=True
    )
    info = {}
    for line in res.stderr.split('\n'):
        if 'Duration:' in line:
            t = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = t.split(':')
            info['duration_s'] = int(h)*3600 + int(m)*60 + float(s)
        if 'Audio:' in line:
            parts = line.split(',')
            for p in parts:
                if 'Hz' in p:
                    info['sample_rate'] = int(p.strip().split(' ')[0])
                if 'mono' in p:
                    info['channels'] = 1
                if 'stereo' in p:
                    info['channels'] = 2
    return info


# ============================================================
# STEP 3-4 — SEARCH + DOWNLOAD (semi-automated — em log candidates for Mr.Long review)
# ============================================================

def search_pixabay(query):
    """Pixabay sound effects search — return list of candidate URLs.

    NOTE: Pixabay API requires API key. Em log search URL cho Mr.Long manual
    OR use direct download URLs nếu Mr.Long ship candidate list.
    """
    return f"https://pixabay.com/sound-effects/search/{query.replace(' ', '%20')}/"

def search_freesound(query):
    """Freesound CC0 filter search URL — manual preview."""
    return f"https://freesound.org/search/?q={query.replace(' ', '%20')}&f=license:%22Creative+Commons+0%22"

def emit_search_candidates(asset_id, spec):
    """Step 3: log search URLs cho Mr.Long manual review."""
    candidates = []
    for q in spec.get("search_queries", []):
        candidates.append({
            "query": q,
            "pixabay": search_pixabay(q),
            "freesound_cc0": search_freesound(q),
        })
    return candidates


# ============================================================
# STEP 5 — PROCESSING PIPELINE
# ============================================================

def process_asset(asset_id, raw_path, spec):
    """Apply ffmpeg deterministic processing to raw file → final."""
    out_dir = SFX_DIR / spec["category"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{asset_id}.wav"

    print(f"[Process] {asset_id} ← {raw_path}")
    info = get_audio_info(raw_path)
    print(f"  raw: {info.get('duration_s', '?')}s @ {info.get('sample_rate', '?')}Hz {info.get('channels', '?')}ch")

    # Build ffmpeg filter chain
    filters = []

    # 5b trim if target_duration > 0
    target_dur = spec["target_duration_ms"] / 1000.0
    if "loop_seamless" in spec and spec["loop_seamless"]:
        # for loops: trim to target duration with crossfade safe
        pass  # use -t below

    # 5c loudnorm (2-pass via measured)
    pass1 = ffmpeg_run([
        "-i", str(raw_path),
        "-af", f"loudnorm=I={spec['target_lufs']}:TP={spec['target_peak_db']}:LRA=7:print_format=json",
        "-f", "null", "-"
    ], label="loudnorm-measure")
    import re as _re
    m = _re.search(r'\{[^{}]*"input_i"[^{}]*\}', pass1.stderr, _re.DOTALL)
    if m:
        measured = json.loads(m.group(0))
        ln_filter = (f"loudnorm=I={spec['target_lufs']}:TP={spec['target_peak_db']}:LRA=7:"
                    f"measured_I={measured['input_i']}:"
                    f"measured_LRA={measured['input_lra']}:"
                    f"measured_TP={measured['input_tp']}:"
                    f"measured_thresh={measured['input_thresh']}:"
                    f"offset={measured.get('target_offset', 0)}:linear=true")
    else:
        ln_filter = f"loudnorm=I={spec['target_lufs']}:TP={spec['target_peak_db']}:LRA=7"
    filters.append(ln_filter)

    # 5d resample
    filters.append(f"aresample={spec['sample_rate_hz']}")

    # 5e channel
    ac_flag = "1" if spec["channels"] == "mono" else "2"

    # final ffmpeg
    cmd_args = [
        "-i", str(raw_path),
        "-t", f"{target_dur}",
        "-af", ",".join(filters),
        "-ar", str(spec["sample_rate_hz"]),
        "-ac", ac_flag,
        "-acodec", "pcm_s24le" if spec["category"] in ("discrete", "brand") else "pcm_s16le",
        str(out_path),
    ]
    res = ffmpeg_run(cmd_args, label="process-final")
    if res.returncode != 0:
        return None

    # Verify
    final_info = get_audio_info(out_path)
    print(f"  final: {final_info.get('duration_s', '?')}s @ {final_info.get('sample_rate', '?')}Hz {final_info.get('channels', '?')}ch")
    print(f"  path: {out_path}")
    return out_path


# ============================================================
# STEP 6-7 — CHECKSUM + REGISTER
# ============================================================

def checksum_and_register(asset_id, final_path, spec, source_info):
    """Compute sha256 + update CHECKSUMS.sha256 + log register."""
    csum = sha256_file(final_path)
    rel_path = final_path.relative_to(ROOT).as_posix()

    # Append CHECKSUMS.sha256
    line = f"{csum}  {rel_path}\n"
    existing = ""
    if CHECKSUMS_FILE.exists():
        existing = CHECKSUMS_FILE.read_text(encoding='utf-8')
    # Replace if asset_id line exists, else append
    new_lines = [l for l in existing.split('\n') if rel_path not in l and l.strip()]
    new_lines.append(f"{csum}  {rel_path}")
    CHECKSUMS_FILE.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')

    log_event({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "action": "register",
        "asset_id": asset_id,
        "path": rel_path,
        "checksum": csum,
        "source": source_info,
    })
    print(f"  ✓ checksum lock: sha256:{csum[:16]}...")
    print(f"  ✓ registered: {CHECKSUMS_FILE.name}")
    return csum


# ============================================================
# STEP 3 ALTERNATIVE — AI GENERATION via ACE-Step
# ============================================================

def generate_via_ace_step(asset_id, spec):
    """Route to ACE-Step local port 7865 for AI generation."""
    print(f"[AI-gen] {asset_id} via ACE-Step port {ACE_STEP_PORT}")
    print(f"  prompt: {spec.get('ace_step_prompt', '')}")
    print(f"  TODO: implement gradio_client call to ACE-Step API")
    # placeholder — Mr.Long sẽ manual gen via ACE-Step webui hoặc em implement sau
    return None


# ============================================================
# MAIN
# ============================================================

def acquire_asset(asset_id, dry_run=False, force=False):
    """Full pipeline cho 1 asset."""
    if asset_id not in ASSETS:
        print(f"[ERROR] Asset '{asset_id}' không có trong registry.")
        return False
    spec = ASSETS[asset_id]
    print(f"\n========== {asset_id} ==========")
    print(f"  category: {spec['category']}")
    print(f"  target: {spec['target_duration_ms']}ms @ {spec['target_lufs']} LUFS, {spec['channels']}, {spec['sample_rate_hz']}Hz")

    # Check already registered
    if not force and CHECKSUMS_FILE.exists():
        existing = CHECKSUMS_FILE.read_text(encoding='utf-8')
        if f"{spec['category']}/{asset_id}.wav" in existing:
            print(f"  ⊘ already registered — skip (use --force to redo)")
            return True

    # Step 3 — emit search candidates for Mr.Long manual or AI gen
    if spec.get("ai_generate"):
        print(f"  → AI generation path")
        raw_path = generate_via_ace_step(asset_id, spec)
        if not raw_path:
            print(f"  [INFO] ACE-Step gen pending — Mr.Long manual via webui port {ACE_STEP_PORT}")
            return False
    elif spec.get("build_from"):
        print(f"  → Build from existing: {spec['build_from']}")
        # build_from assets — handled separately
        print(f"  [TODO] build_from compositing — em sẽ implement sau khi raw assets ready")
        return False
    else:
        candidates = emit_search_candidates(asset_id, spec)
        print(f"  → Search candidates ({len(candidates)} queries):")
        for c in candidates:
            print(f"    Query: {c['query']}")
            print(f"      Pixabay: {c['pixabay']}")
            print(f"      Freesound CC0: {c['freesound_cc0']}")
        print(f"\n  [ACTION] Mr.Long preview + paste URL chosen vào: tools/sfx_chosen_urls.yaml")
        print(f"  Format: {asset_id}: {{url: '...', license: 'CC0', source: 'pixabay'}}")
        return False  # await Mr.Long curation

    if dry_run:
        return True

    # Step 5 — process
    # final_path = process_asset(asset_id, raw_path, spec)
    # Step 6-7 — checksum + register
    # checksum_and_register(asset_id, final_path, spec, source_info)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset", help="Single asset ID")
    ap.add_argument("--batch", choices=list(BATCHES.keys()), help="Run batch")
    ap.add_argument("--full", action="store_true", help="Run all assets")
    ap.add_argument("--dry-run", action="store_true", help="Search only")
    ap.add_argument("--force", action="store_true", help="Redo even if registered")
    args = ap.parse_args()

    targets = []
    if args.asset:
        targets = [args.asset]
    elif args.batch:
        targets = BATCHES[args.batch]
    elif args.full:
        targets = list(ASSETS.keys())
    else:
        ap.print_help()
        sys.exit(1)

    print(f"[SFX Acquire Pipeline] Round 16 — bible/17 v1.0")
    print(f"Targets: {len(targets)} asset(s)")
    results = {"ok": 0, "pending": 0, "fail": 0}
    for aid in targets:
        try:
            ok = acquire_asset(aid, dry_run=args.dry_run, force=args.force)
            if ok:
                results["ok"] += 1
            else:
                results["pending"] += 1
        except Exception as e:
            print(f"[ERROR] {aid}: {e}")
            results["fail"] += 1

    print(f"\n========== SUMMARY ==========")
    print(f"  ok: {results['ok']}  pending: {results['pending']}  fail: {results['fail']}")
    print(f"  manifest: {CHECKSUMS_FILE}")
    print(f"  log: {LOG_FILE}")


if __name__ == "__main__":
    main()
