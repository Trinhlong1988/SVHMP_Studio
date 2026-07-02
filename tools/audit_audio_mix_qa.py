"""Audio Mix QA — 15 checks load bible/05 v1.1 R_AUDIO_01-10 + bible/00 R59.

Usage:
  python tools/audit_audio_mix_qa.py --ep 1 --wav output/ep_01/EP01_R43_MIX.wav

Output: output/ep_NN/audio_mix_qa_verdict.json + console summary.
Exit code: 0 if PASS, 1 if any HIGH FAIL (R59 gate).

Empirical-only — no inference (per R_AUDIO_10).
"""
import sys, json, argparse
from pathlib import Path
import numpy as np
import soundfile as sf
import yaml

BASE = Path(__file__).resolve().parents[1]
BIBLE_05 = BASE / 'bible' / '05_audio_bible.yaml'

def lufs_approx(audio, sr):
    mono = np.mean(audio, axis=0) if audio.ndim == 2 else audio
    block_n = int(0.4 * sr)
    blocks = []
    for i in range(0, len(mono) - block_n, block_n // 4):
        ms = np.mean(mono[i:i+block_n] ** 2)
        if ms > 0: blocks.append(ms)
    if not blocks: return -100.0
    blocks = np.array(blocks)
    loudness = -0.691 + 10 * np.log10(blocks + 1e-12)
    mean_un = -0.691 + 10 * np.log10(np.mean(blocks))
    final = blocks[loudness > mean_un - 10]
    if len(final) == 0: final = blocks
    return -0.691 + 10 * np.log10(np.mean(final))

def rms_db_curve(audio, sr, start_s, end_s, win_s=0.5):
    start_n = int(start_s * sr)
    end_n = min(int(end_s * sr), audio.shape[1])
    mono = np.mean(audio[:, start_n:end_n], axis=0)
    win_n = int(win_s * sr)
    if win_n <= 0 or len(mono) < win_n: return np.array([])
    rms = []
    for i in range(0, len(mono) - win_n, win_n // 2):
        ms = np.mean(mono[i:i+win_n] ** 2)
        rms.append(20 * np.log10(np.sqrt(ms) + 1e-12))
    return np.array(rms)

def check_C1_viewer_empathy(plan):
    issues = []
    moments = plan.get('moments', []) if plan else []
    for m in moments:
        emo = m.get('emotion_label', '')
        cat = (m.get('music_category', '') or '').lower()
        for f1, f2 in [('death_announce','upbeat'),('death_announce','bright_piano'),
                       ('haunting','cheerful'),('memory_of_dead','tension_drone'),
                       ('regret_quiet','loud_percussion')]:
            if f1 in emo and f2 in cat:
                issues.append({'sev':'HIGH','check':'C1','msg':f'Forbidden pair: {emo}+{cat}'})
    return issues

def check_C2_moment_map(p):
    issues = []
    if not p or not p.exists():
        issues.append({'sev':'HIGH','check':'C2','msg':'moment_map.yaml MISSING (R_AUDIO_02)'})
        return issues
    try:
        m = yaml.safe_load(p.read_text(encoding='utf-8'))
        moms = m.get('moments', [])
        if len(moms) < 15:
            issues.append({'sev':'HIGH','check':'C2','msg':f'moments={len(moms)} < 15 min'})
        req = ['line_range','emotion_label','music_pick','dB_level','transition_type']
        for i, mo in enumerate(moms):
            miss = [r for r in req if r not in mo]
            if miss: issues.append({'sev':'MEDIUM','check':'C2','msg':f'moment[{i}] missing: {miss}'})
    except Exception as e:
        issues.append({'sev':'HIGH','check':'C2','msg':f'parse FAIL: {e}'})
    return issues

def check_C3_ambient_bed(audio, sr):
    issues = []
    win_n = int(1.0 * sr)
    mono = np.mean(audio, axis=0)
    run = max_s = 0
    for i in range(0, len(mono) - win_n, win_n):
        rms = np.sqrt(np.mean(mono[i:i+win_n] ** 2))
        if 20*np.log10(rms+1e-12) < -45:
            run += 1; max_s = max(max_s, run)
        else: run = 0
    if max_s > 3:
        issues.append({'sev':'HIGH','check':'C3','msg':f'Silence run {max_s}s > 3s — ambient bed thiếu'})
    return issues

def check_C4_setting_sfx(plan, ep_num):
    issues = []
    if not plan: return issues
    FORB = ['fire','fireplace','campfire','chandelier','desert','cactus','ocean','waves',
            'beach','surf','forest_birds','jungle','baby','infant','explosion','gunfire',
            'military','cathedral']
    sfx = plan.get('episodes', {}).get(f'EP{ep_num:02d}', {}).get('sfx', {})
    for sec, lst in sfx.items():
        for s in lst:
            title = (s.get('title') or '').lower()
            file = (s.get('file') or '').lower()
            for kw in FORB:
                if kw in title or kw in file:
                    issues.append({'sev':'HIGH','check':'C4',
                        'msg':f'SFX [{sec}] "{s.get("title","?")[:50]}" forbidden "{kw}"'})
    return issues

def check_C5_death_announce(moments):
    issues = []
    for m in moments:
        if 'death_announce' in m.get('emotion_label',''):
            cat = (m.get('music_category','') or '').upper()
            if 'HDK_SAD' not in cat and 'MUTE' not in cat and 'AMBIENT_ONLY' not in cat:
                issues.append({'sev':'HIGH','check':'C5','msg':f'death_announce dùng {cat}'})
            if not (m.get('special_treatment','') or '').lower().startswith('mute'):
                issues.append({'sev':'MEDIUM','check':'C5','msg':'death_announce thiếu mute_window'})
    return issues

def check_C6_death_echo(moments):
    issues = []
    for m in moments:
        if 'death_echo' in m.get('emotion_label',''):
            cat = (m.get('music_category','') or '').upper()
            if 'HDK_SAD' not in cat and 'HDK_MYSTERY' not in cat:
                issues.append({'sev':'HIGH','check':'C6','msg':f'death_echo dùng {cat}'})
    return issues

def check_C7_impact_mute(moments):
    issues = []
    for m in moments:
        if m.get('impact_moment') or 'impact' in m.get('emotion_label','').lower():
            if not m.get('mute_window'):
                issues.append({'sev':'HIGH','check':'C7',
                    'msg':f'Impact "{m.get("line_range")}" thiếu mute_window'})
    return issues

def check_C8_memory_haunting(moments):
    issues = []
    for m in moments:
        emo = m.get('emotion_label','')
        cat = (m.get('music_category','') or '').upper()
        if 'memory_of_dead' in emo and 'HDK_REVEAL' not in cat:
            issues.append({'sev':'HIGH','check':'C8','msg':f'memory_of_dead dùng {cat}'})
        if 'haunting' in emo and 'HDK_MYSTERY' not in cat and 'HDK_TENSION' not in cat:
            issues.append({'sev':'HIGH','check':'C8','msg':f'haunting dùng {cat}'})
    return issues

def check_C9_section_db(audio, sr, sections, spec):
    issues = []
    for name, ts, te in sections:
        if name not in spec: continue
        curve = rms_db_curve(audio, sr, ts, te)
        if len(curve) == 0: continue
        s = spec[name]
        avg = curve.mean()
        if 'spec_dB_level' in s:
            t = s['spec_dB_level']
            if abs(avg - t) > 4:
                issues.append({'sev':'MEDIUM','check':'C9',
                    'msg':f'{name} avg {avg:.1f} vs {t} (off {abs(avg-t):.1f})'})
        if 'spec_no_drop' in s:
            n = len(curve)
            drop = curve[:n//4].mean() - curve[-n//4:].mean()
            if drop > 3:
                issues.append({'sev':'HIGH','check':'C9','msg':f'{name} drops {drop:.1f} dB'})
    return issues

def check_C10_hook_swell_align(audio, sr, first_word_ms):
    issues = []
    if first_word_ms is None:
        issues.append({'sev':'MEDIUM','check':'C10','msg':'first_word_center_ms not provided'})
        return issues
    curve = rms_db_curve(audio, sr, 0, 30)
    if len(curve) == 0: return issues
    peak_ms = curve.argmax() * 250
    diff = abs(peak_ms - first_word_ms)
    if diff > 200:
        issues.append({'sev':'HIGH','check':'C10',
            'msg':f'HOOK peak @ {peak_ms}ms, expected {first_word_ms}ms (off {diff}ms)'})
    return issues

def check_C11_lufs(audio, sr):
    issues = []
    lufs = lufs_approx(audio, sr)
    if not (-17 <= lufs <= -15):
        sev = 'HIGH' if abs(lufs+16) > 2 else 'MEDIUM'
        issues.append({'sev':sev,'check':'C11','msg':f'LUFS {lufs:.2f} outside [-17,-15]'})
    return issues

def check_C12_peak_bell(audio, sr, bell_count):
    issues = []
    peak = 20*np.log10(np.max(np.abs(audio))+1e-12)
    if peak > -1:
        issues.append({'sev':'HIGH','check':'C12','msg':f'Peak {peak:.2f} dBFS > -1'})
    if bell_count is not None and bell_count > 1:
        issues.append({'sev':'HIGH','check':'C12','msg':f'Bell {bell_count} > 1'})
    return issues

def check_C13_click_pop(audio, sr):
    issues = []
    mono = np.mean(audio, axis=0) if audio.ndim == 2 else audio
    diff = np.abs(np.diff(mono))
    idx = np.where(diff > 0.3)[0]
    if len(idx) > 0:
        issues.append({'sev':'HIGH','check':'C13',
            'msg':f'{len(idx)} click/pop. First @ {idx[0]/sr:.2f}s'})
    return issues

def check_C14_dc(audio, sr):
    issues = []
    mono = np.mean(audio, axis=0) if audio.ndim == 2 else audio
    win_n = int(0.1 * sr)
    bad = sum(1 for i in range(0, len(mono)-win_n, win_n)
              if abs(np.mean(mono[i:i+win_n])) > 0.001)
    if bad > 0:
        issues.append({'sev':'MEDIUM','check':'C14','msg':f'{bad} windows DC > 0.001'})
    return issues

def check_C15_spectral(audio, sr):
    issues = []
    mono = np.mean(audio, axis=0) if audio.ndim == 2 else audio
    mid = len(mono)//2
    seg = mono[max(0,mid-int(2.5*sr)) : mid+int(2.5*sr)]
    if len(seg) < sr: return issues
    fft = np.abs(np.fft.rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1/sr)
    fft_db = 20*np.log10(fft/fft.max()+1e-12)
    mask = freqs > 22000
    if mask.any() and fft_db[mask].max() > -40:
        issues.append({'sev':'MEDIUM','check':'C15',
            'msg':f'High-freq spike {fft_db[mask].max():.1f} dB above 22 kHz'})
    return issues

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', type=int, required=True)
    ap.add_argument('--wav', type=Path, required=True)
    ap.add_argument('--moment-map', type=Path, default=None)
    ap.add_argument('--plan', type=Path, default=BASE/'output'/'ep_audio_plan.yaml')
    ap.add_argument('--first-word-center-ms', type=float, default=None)
    ap.add_argument('--bell-count', type=int, default=None)
    ap.add_argument('--output', type=Path, default=None)
    args = ap.parse_args()

    if not args.wav.exists():
        print(f'WAV not found: {args.wav}'); sys.exit(2)

    print(f'[AUDIT] EP{args.ep:02d} - {args.wav.name}')
    audio, sr = sf.read(str(args.wav), always_2d=True); audio = audio.T
    duration = audio.shape[1] / sr
    print(f'  sr={sr}, ch={audio.shape[0]}, duration={duration:.1f}s')

    plan = None
    if args.plan.exists():
        plan = yaml.safe_load(args.plan.read_text(encoding='utf-8'))

    moments = []
    mm_path = args.moment_map or (BASE/'output'/f'ep_{args.ep:02d}'/'moment_map.yaml')
    if mm_path.exists():
        try:
            moments = yaml.safe_load(mm_path.read_text(encoding='utf-8')).get('moments', [])
        except Exception: pass

    sections_tts = [
        ('HOOK',0.0,82.1),('SETUP',82.1,298.8),('INCIDENT',298.8,502.5),
        ('REVEAL',502.5,755.2),('PAYOFF',755.2,948.6),
        ('CLIFFHANGER',948.6,max(948.6, duration-7.0)),
    ]
    INTRO = 7.0
    sections_file = [(n, (ts if n=='HOOK' else ts+INTRO), te+INTRO) for n,ts,te in sections_tts]

    spec = yaml.safe_load(BIBLE_05.read_text(encoding='utf-8'))\
        .get('audio_mix_rules', {}).get('R_AUDIO_06_music_section_personality', {}).get('sections', {})

    print('\n[RUNNING 15 CHECKS]')
    all_issues = []
    checks = [
        ('C1',  lambda: check_C1_viewer_empathy({'moments': moments})),
        ('C2',  lambda: check_C2_moment_map(mm_path)),
        ('C3',  lambda: check_C3_ambient_bed(audio, sr)),
        ('C4',  lambda: check_C4_setting_sfx(plan, args.ep)),
        ('C5',  lambda: check_C5_death_announce(moments)),
        ('C6',  lambda: check_C6_death_echo(moments)),
        ('C7',  lambda: check_C7_impact_mute(moments)),
        ('C8',  lambda: check_C8_memory_haunting(moments)),
        ('C9',  lambda: check_C9_section_db(audio, sr, sections_file, spec)),
        ('C10', lambda: check_C10_hook_swell_align(audio, sr, args.first_word_center_ms)),
        ('C11', lambda: check_C11_lufs(audio, sr)),
        ('C12', lambda: check_C12_peak_bell(audio, sr, args.bell_count)),
        ('C13', lambda: check_C13_click_pop(audio, sr)),
        ('C14', lambda: check_C14_dc(audio, sr)),
        ('C15', lambda: check_C15_spectral(audio, sr)),
    ]
    pc = 0
    for cid, fn in checks:
        try: issues = fn()
        except Exception as e: issues = [{'sev':'ERROR','check':cid,'msg':f'threw: {e}'}]
        if not issues:
            print(f'  {cid}: PASS'); pc += 1
        else:
            high = sum(1 for i in issues if i['sev']=='HIGH')
            print(f'  {cid}: {"FAIL" if high else "WARN"} ({len(issues)}, {high} HIGH)')
            for i in issues[:3]: print(f'      [{i["sev"]}] {i["msg"][:120]}')
            all_issues.extend(issues)

    high = sum(1 for i in all_issues if i['sev']=='HIGH')
    med = sum(1 for i in all_issues if i['sev']=='MEDIUM')
    verdict = 'PASS' if high == 0 else 'FAIL'
    print(f'\n[VERDICT] {verdict} - {pc}/15 PASS, {high} HIGH, {med} MEDIUM')

    out = args.output or (BASE/'output'/f'ep_{args.ep:02d}'/'audio_mix_qa_verdict.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        'ep': args.ep, 'wav': str(args.wav), 'duration_s': duration,
        'verdict': verdict, 'pass_count': pc, 'high': high, 'medium': med,
        'issues': all_issues,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'  Verdict JSON: {out}')
    sys.exit(0 if verdict == 'PASS' else 1)

if __name__ == '__main__':
    main()
