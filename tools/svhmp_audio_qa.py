"""SVHMP audio QA — R80 transient peak + R76 open-vowel tail + cross-section boundary.

Chạy POST-RENDER mandatory TRƯỚC concat. Block ship nếu HIGH issues.
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
import soundfile as sf

def scan_bup_transients(audio, sr, threshold_prev_db=-50, threshold_cur_db=-3, threshold_delta_db=40):
    """R80: detect bụp = silence→loud burst (true audible transient)."""
    abs_a = np.abs(audio)
    ws = int(0.05 * sr)
    issues = []
    for i in range(ws, len(audio) - ws, ws):
        prev_peak = abs_a[i-ws:i].max()
        cur_peak = abs_a[i:i+ws].max()
        prev_db = 20*np.log10(prev_peak + 1e-9)
        cur_db = 20*np.log10(cur_peak + 1e-9)
        delta = cur_db - prev_db
        if prev_db < threshold_prev_db and cur_db > threshold_cur_db and delta > threshold_delta_db:
            issues.append({
                'rule': 'R80', 'sev': 'HIGH', 'type': 'bụp_transient',
                't': round(i/sr, 2), 'prev_db': round(prev_db, 1),
                'cur_db': round(cur_db, 1), 'delta_db': round(delta, 1)
            })
    return issues

def scan_overall_peak(audio, sr, max_peak_db=-3):
    """Hard limit: no sample > -3 dBFS (loudnorm push clipping)."""
    peak = np.abs(audio).max()
    db = 20*np.log10(peak + 1e-9)
    if db > max_peak_db:
        idx = np.argmax(np.abs(audio))
        return [{'rule': 'R80.peak', 'sev': 'HIGH', 'type': 'overall_peak_clipping',
                 't': round(idx/sr, 2), 'peak_db': round(db, 1)}]
    return []

def scan_tail_residue(audio, sr, max_tail_db=-15):
    """R76 audio-level: tail 200ms peak > -15 dB = open-vowel sustain risk phù."""
    tail = audio[-int(0.2*sr):]
    if len(tail) == 0: return []
    tp = 20*np.log10(np.abs(tail).max() + 1e-9)
    if tp > max_tail_db:
        return [{'rule': 'R76.audio', 'sev': 'MED', 'type': 'tail_open_vowel_sustain',
                 'tail_db': round(tp, 1)}]
    return []

def scan_internal_silence(audio, sr, max_silence_ms=200, silence_threshold_db=-40):
    """R77: internal silence > 200ms within chunk (comma split internal pause)."""
    abs_a = np.abs(audio)
    thr = 10**(silence_threshold_db/20)
    silent = abs_a < thr
    issues = []
    in_run = False; start_idx = 0
    for i, s in enumerate(silent):
        if s and not in_run:
            in_run = True; start_idx = i
        elif not s and in_run:
            dur_ms = (i - start_idx) * 1000 / sr
            if dur_ms > max_silence_ms:
                # exclude very-start and very-end
                t_start = start_idx / sr
                t_end = i / sr
                if t_start > 0.3 and t_end < (len(audio)/sr - 0.3):
                    issues.append({
                        'rule': 'R77.audio', 'sev': 'MED', 'type': 'internal_silence',
                        't_start': round(t_start, 2), 't_end': round(t_end, 2),
                        'dur_ms': round(dur_ms, 0)
                    })
            in_run = False
    return issues

def qa_section(path):
    a, sr = sf.read(path)
    if a.ndim > 1: a = a.mean(axis=1)
    issues = []
    issues.extend(scan_bup_transients(a, sr))
    issues.extend(scan_overall_peak(a, sr))
    issues.extend(scan_tail_residue(a, sr))
    issues.extend(scan_internal_silence(a, sr))
    return issues, {'duration': len(a)/sr, 'sr': sr,
                    'peak_db': round(20*np.log10(np.abs(a).max()+1e-9), 2),
                    'rms_db': round(20*np.log10(np.sqrt(np.mean(a**2))+1e-9), 2)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--json-out', default=None)
    ap.add_argument('--strict', action='store_true', help='exit 1 if any HIGH issue')
    args = ap.parse_args()

    total = {'files': [], 'high_count': 0, 'med_count': 0}
    for f in args.files:
        issues, stats = qa_section(f)
        high = sum(1 for i in issues if i['sev'] == 'HIGH')
        med = sum(1 for i in issues if i['sev'] == 'MED')
        total['high_count'] += high
        total['med_count'] += med
        print(f"\n=== {Path(f).name} ===")
        print(f"  dur={stats['duration']:.2f}s sr={stats['sr']} peak={stats['peak_db']}dB rms={stats['rms_db']}dB")
        print(f"  Issues: HIGH={high} MED={med}")
        for i in issues[:10]:
            print(f"  [{i['sev']}][{i['rule']}] {i['type']}: {dict((k,v) for k,v in i.items() if k not in ('rule','sev','type'))}")
        if len(issues) > 10:
            print(f"  ... and {len(issues)-10} more")
        total['files'].append({'name': Path(f).name, 'high': high, 'med': med, 'stats': stats, 'issues': issues})

    print(f"\n{'='*60}\nTOTAL: HIGH={total['high_count']} MED={total['med_count']}")
    if args.json_out:
        json.dump(total, open(args.json_out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f"JSON saved → {args.json_out}")
    if args.strict and total['high_count'] > 0:
        print("STRICT MODE: HIGH issues found → exit 1")
        sys.exit(1)

if __name__ == '__main__':
    main()
