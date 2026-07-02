"""SVHMP — TTS adapter pre-render preprocessing (3 handlers).

Handlers:
1. [REVEAL_PAUSE_1000ms] marker → insert [pause:1000ms] before reveal sentence (Ngạn signature)
2. Em-dash (—) trong narrative → comma + [pause:250ms] (R70 BigVGAN gap)
3. Dialogue quote "..." → mark for separate render segment (R72)

Input: output/ep_N/episode.md
Output: output/ep_N/episode_tts_ready.md (preprocessed for TTS pipeline)
"""
import re
import sys
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(__file__).resolve().parents[1]

def handle_reveal_pause(text):
    """Convert [REVEAL_PAUSE_Nms] marker → insert pause BEFORE next sentence."""
    # Pattern: [REVEAL_PAUSE_1000ms] followed by sentence
    return re.sub(r'\[REVEAL_PAUSE_(\d+)ms\]\s*', r'[pause:\1ms] ', text)

def handle_em_dash_narrative(text, pause_ms=250):
    """Convert em-dash in narrative (NOT dialogue speaker dash) → comma + pause."""
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        # Skip dialogue speaker dash (line starts with — like "— Tôi đã đi.")
        if line.lstrip().startswith('—'):
            new_lines.append(line)
            continue
        # Skip metadata / heading / pause lines
        if line.strip().startswith(('#', '[pause', '|', '---', '```')):
            new_lines.append(line)
            continue
        # Replace em-dash in middle: " — " → ", [pause:Nms] "
        new_line = re.sub(r'\s—\s', f', [pause:{pause_ms}ms] ', line)
        new_lines.append(new_line)
    return '\n'.join(new_lines)

def handle_dialogue_quotes(text):
    """Mark dialogue quotes for separate render segments.
    Wrap "..." dialogue with [DIALOGUE_SEG_START][DIALOGUE_SEG_END] markers.
    Render pipeline picks these for separate WAV + bridge 180ms + pitch shift.
    """
    # Pattern: "text" between 5-300 chars
    return re.sub(
        r'"([^"]{5,300})"',
        r'[DIALOGUE_SEG_START]"\1"[DIALOGUE_SEG_END]',
        text
    )

def process_ep(ep_num, dry_run=True):
    src = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    dst = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode_tts_ready.md'
    if not src.exists():
        return None
    text = src.read_text(encoding='utf-8')

    # Apply 3 handlers
    text = handle_reveal_pause(text)
    text = handle_em_dash_narrative(text, pause_ms=250)
    text = handle_dialogue_quotes(text)

    stats = {
        'reveal_pauses': text.count('[pause:1000ms]'),
        'em_dash_pauses': text.count('[pause:250ms]'),
        'dialogue_segments': text.count('[DIALOGUE_SEG_START]'),
    }

    if not dry_run:
        dst.write_text(text, encoding='utf-8')
    return stats

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()

    print("=" * 70)
    print(f"TTS ADAPTER PRE-RENDER | Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print("=" * 70)

    eps = [args.ep] if args.ep else range(1, 51)
    totals = {'reveal_pauses': 0, 'em_dash_pauses': 0, 'dialogue_segments': 0}

    for n in eps:
        stats = process_ep(n, dry_run=not args.apply)
        if stats is None:
            continue
        for k, v in stats.items():
            totals[k] += v
        if args.ep or stats['reveal_pauses'] > 0 or stats['dialogue_segments'] > 0:
            print(f"EP{n:02d}: reveal={stats['reveal_pauses']} em-dash={stats['em_dash_pauses']} dialogue={stats['dialogue_segments']}")

    print(f"\n=== TOTALS (50 EPs) ===")
    print(f"  Reveal pauses inserted: {totals['reveal_pauses']}")
    print(f"  Em-dash pauses inserted: {totals['em_dash_pauses']}")
    print(f"  Dialogue segments marked: {totals['dialogue_segments']}")
    if args.apply:
        print(f"\n  Output: output/ep_*/episode_tts_ready.md")

if __name__ == '__main__':
    main()
