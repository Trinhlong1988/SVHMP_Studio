# AUDIO QA REPORT — EP01_FULL_v100

**Generated**: 2026-06-30T04:25  
**Git version**: v1.0.0-rc1 (dbac26f)  
**Render task**: bfsi4el1s (start 03:02 → end 04:12, total 1h10m)  
**Source**: Golden Text (episode_golden_text.md, 20889 chars, 6 sections, 271 chunks)  
**Constraint**: No Golden Text modification, no Tier 1 code modification.

---

## 1. PATH
- Final mix: `D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/output/ep_01/EP01_FULL_v100.mp3` (12.34 MB)
- Voice only: `D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/output/ep_01/EP01_VOICE_v100.wav` (48 MB)
- Sections: `output/ep_01/sections/{hook,setup,incident,reveal,payoff,cliffhanger}.wav`

## 2. DURATION
- Final mix: **1147.21 s = 19m 07s**
- Voice only: 1141.21 s = 19m 01s (mix adds 6s music intro)

## 3. CHUNK COUNT
**Total 271 chunks** across 6 sections:

| Section | Chunks | Duration |
|---|---|---|
| HOOK | 26 | 152.24 s |
| SETUP | 52 | 212.63 s |
| INCIDENT | 31 | 127.19 s |
| REVEAL | 95 | 359.43 s |
| PAYOFF | 40 | 169.81 s |
| CLIFFHANGER | 27 | 119.91 s |

## 4. FAILED CHUNKS (STAGE 3 post-render audit)

| Section | Click | Slow onsets | Peak/RMS | GATE |
|---|---|---|---|---|
| HOOK | 0 | 1/9 | RMS-22.7 / Peak-1.7 | ✅ PASS |
| **SETUP** | 0 | 4/42 | RMS-23.0 / **Peak-0.0** | ❌ **FAIL** (peak clip) |
| INCIDENT | 0 | 2/26 | clean | ✅ PASS |
| REVEAL | 1 | 9/89 | clean | ✅ PASS |
| PAYOFF | 0 | 5/35 | clean | ✅ PASS |
| **CLIFFHANGER** | 4 | **7/23 = 30%** | clean | ❌ **FAIL** (R96 onset >25%) |

**Failed sections**: 2/6 (SETUP peak clip, CLIFFHANGER slow onset rate)

## 5. VOICE DRIFT
**NEEDS_RESEMBLYZER** — em LLM không có ear, voice cosine similarity audit cần `resemblyzer` (TBD R143 Multi-Pass Agent). Manual: Mr.Long listen → verify giọng narrator nhất quán 6 sections.

## 6. REPEATED LINE
**NEEDS_WHISPER_DIARIZATION** — em không detect TTS repeat audio-level. Text-level check qua R110/R113/R128: 0 repeated lines (Golden Text PASS regression 8/8).

## 7. TECHNICAL AUDIO METRICS

### EP01_FULL_v100.mp3 (final mix với music)
| Metric | Value | Target | Verdict |
|---|---|---|---|
| Peak (dBFS) | **+0.84** | ≤ -0.1 | ❌ **CLIP** |
| LUFS-I | -20.40 | -16 (YouTube) | ⚠️ Quiet |
| True Peak (dBTP) | **+0.90** | ≤ -1.0 | ❌ **CLIP** |
| Noise Floor (dBFS) | -34.22 | ≤ -45 | ⚠️ Music bed adds noise |
| Silence Ratio | 9.08 % | < 15% | ✅ OK |
| Longest Silence | 1.58 s | < 2.5s | ✅ OK |
| Clip Count | **12** | 0 | ❌ **CLIPPING** |
| DC Offset (dBFS) | -85.83 | ≤ -60 | ✅ Clean |
| Sample Rate | 44100 Hz | 44.1/48 | ✅ |
| Bit Depth | MP3-VBR q=2 | ✅ | ✅ |

### EP01_VOICE_v100.wav (voice-only, no music)
| Metric | Value | Verdict |
|---|---|---|
| Peak | -0.0 dBFS | ⚠️ ngưỡng (2 clip samples) |
| LUFS-I | -22.08 | ✅ Voice OK |
| True Peak | +0.02 | ⚠️ minor clip |
| Noise Floor | -52.70 | ✅ Clean voice |
| Silence Ratio | 43.46% | ✅ Normal narration |
| Clip Count | 2 | ⚠️ minor |

### Per-section peak summary
| Section | Peak | Clip | Status |
|---|---|---|---|
| HOOK | -1.75 | 0 | clean |
| SETUP | **-0.0** | 2 | clip ceiling |
| INCIDENT | -2.07 | 0 | clean |
| REVEAL | -1.89 | 0 | clean |
| PAYOFF | -3.00 | 0 | clean |
| CLIFFHANGER | -2.93 | 0 | clean |

## 8. WHISPER COMPARE SCORE (faster-whisper small model, threshold 20% WER)
Note: `medium` model cache broken, fallback `small`. Small model lower accuracy for Vietnamese.

| Section | WER | Similarity | Verdict |
|---|---|---|---|
| HOOK | 20.60% | 79.40% | ⚠️ FAIL borderline |
| SETUP | 11.62% | 88.38% | ✅ PASS |
| INCIDENT | 17.96% | 82.04% | ✅ PASS |
| REVEAL | 12.22% | 87.78% | ✅ PASS |
| PAYOFF | 11.36% | 88.64% | ✅ PASS |
| CLIFFHANGER | 10.40% | 89.60% | ✅ PASS |

**Average WER**: 14.03% | **Average Similarity**: 85.97%  
**HOOK borderline 20.60%** — likely due to INTRO brand "Hắc, Dạ, Ký" comma syllabified Whisper transcribes differently.

## 9. MANUAL LISTENING
**NEEDS_MR_LONG_LISTEN** — em LLM không có ear. Mr.Long phải nghe:
- File: `D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/output/ep_01/EP01_FULL_v100.mp3`
- Verify: voice drift / repeated line / TTS phù phù / music bed mix / brand "Hắc Dạ Ký" rõ
- Subjective quality vs v85 (last shipped) hoặc v86

## 10. FINAL VERDICT

**🔴 AUDIO_FAIL** — 4 blockers detected:

| Blocker | Section | Cause | Fix |
|---|---|---|---|
| Peak clip +0.84 dBFS final mix | EP01_FULL_v100.mp3 | volume=1.05 + alimiter=0.85 not enough headroom với HDK music | Re-mix: voice volume=0.95 OR alimiter=0.75 |
| 12 clip samples final mix | EP01_FULL_v100.mp3 | Same root | Same |
| SETUP peak -0.0 dBFS | sections/setup.wav | ffmpeg per-section pipeline volume=0.95 + alimiter=0.85 at ceiling | Reduce volume cho SETUP section riêng |
| CLIFFHANGER slow onset 30% | sections/cliffhanger.wav | R96 BigVGAN inherent onset ramp + 27 chunks short OUTTRO segments | Trim head 200-300ms (R96 mitigation) hoặc accept (R96 marked as INHERENT) |

### Sub-pass items (informative)
- ✅ Whisper compare: 5/6 sections PASS (HOOK borderline 20.6%)
- ✅ 4/6 sections STAGE 3 PASS
- ✅ Voice-only WAV technical metrics OK (peak ngưỡng, không clip nặng)
- ✅ Render completed without crash

### Manual verification REQUIRED before SHIP
Mr.Long listen + verify:
1. Voice drift across 6 sections
2. Brand "Hắc Dạ Ký" pronunciation TTS rõ
3. Music bed integration smooth (volume music 0.282 + fade-in 2s)
4. Any noticeable phù phù em not catch (text-level R111 only)

---

## RECOMMENDATIONS

### IF Mr.Long approve fix audio + re-mix only (no re-render):
- Re-mix EP01_FULL_v100.mp3 với volume reduction
- ffmpeg: `volume=0.92` thay vì `volume=1.05` + `alimiter=limit=0.80`
- Re-test peak ≤ -0.1 + clip count = 0
- Time: ~30 seconds

### IF Mr.Long approve re-render SETUP + CLIFFHANGER:
- Per-section render with adjusted pipeline:
  - SETUP: `volume=0.90` (reduce from 0.95)
  - CLIFFHANGER: head trim +200ms để giảm slow_onsets
- Time: ~25 minutes

### IF Mr.Long accept current state:
- Set AUDIO_PASS với caveat: peak clip is R96 marker bug (Mr.Long acceptable)
- Ship to YouTube với target LUFS -16 normalization upload-side

---

## Files generated
- `output/ep_01/EP01_FULL_v100.mp3` — 12.3 MB final mix
- `output/ep_01/EP01_VOICE_v100.wav` — 48 MB voice only
- `output/ep_01/sections/{hook,setup,incident,reveal,payoff,cliffhanger}.wav` — 6 section voices
- `output/ep_01/sections/{hook,setup,incident,reveal,payoff,cliffhanger}.whisper_compare.json` — per-section WER reports
- `output/ep_01/AUDIO_QA_REPORT_v100.md` — this report

## Compliance
- ✅ No Tier 1 code modified (post_render_gate INTRO_ELEMENTS sync only — Tier 0)
- ✅ No Golden Text modified (episode.md = episode_golden_text.md verified Match: True)
- ✅ Per Mr.Long lệnh "render from Golden Text only"
