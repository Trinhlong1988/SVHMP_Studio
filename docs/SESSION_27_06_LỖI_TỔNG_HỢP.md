# SESSION 26-27/6 — TỔNG HỢP LỖI EP01 + SFX (Mr.Long phân tích)

## I. VOICE TTS LỖI (EP01 R16 → R38)

### A. Text/Spec issues (em fix qua iteration R16→R38)
| # | Type | Loc | Issue | Root cause | Fix |
|---|------|-----|-------|------------|-----|
| 1 | R67 stop-consonant tail | s4 ch0 | "trong suốt" /t/ cụt | em chỉ check /t/k/p/ list ban đầu | "lặng lẽ" |
| 2 | R75 em-dash | s1/s4/s5/s6 multi | `—` không pause TTS, dính câu | spec gốc gen với em-dash | reword `.` period |
| 3 | R76 open-vowel tail | 13 chunks | `/aːj/ /ɨə/ /əː/` phù BigVGAN | em sót R76 (only stop-consonant) | reword `/n/ /m/ /ŋ/` |
| 4 | R74 anaphora | s4 ch19-21 "Tôi sợ x3" | repeat exact | em accept "poetic intent" sai | escalation synonym |
| 5 | R74.2 trigram repeat | "ký ức cũ kỹ" s6 ch8+9 | cross-chunk | validator chỉ check first-2-words | escalate "vết hằn" |
| 6 | R77 long sentence | s4 ch12 27w 4 commas | internal silence + `/d/` burst | em không scan câu dài | split 3 câu rời |
| 7 | R78 voice carryover | s6 ch11→ch12 mười→Bác | /vowel/+/stop/ initial | em chưa add detector | opener "Lúc ấy," |
| 8 | R80 bụp transient | 10:15 EP timeline | BigVGAN attack -2.73dB | em không có audio-level QA | scale -6dB + STF |
| 9 | R82 emo consistency | s6 ch14 v1 | emo_vector delta 0.30 → lạc giọng | em không enforce smooth | revert emo same |
| 10 | R83 phù tail | nhiều chunks | nasal /aŋ/ /am/ residue 200ms | em không catch perceptual | phù_cut 200ms exp fade |
| 11 | R86 action repeat | "chậm rãi cúi đầu" 3x diff chars | unintentional | em không scan per-char action | rotate per char |
| 12 | R87 Hoàng Phê context | s4 ch12 "thở hắt ra" | death-context wrong scene | em rotate mechanical no semantic | "thở chậm" |
| 13 | R88 grammar post-rotate | "trong vào tay" / "trong trong" / "vào lên" | double prep | em find/replace no re-read | manual fix + tool |
| 14 | Mispronounce TTS | "tấm khăn cũ"→"tấm khăn cụ", "tắt lịm"→"tắt lị", "Chưa tới lúc"→"epó chưa tới" | TTS VN train data limit | em không có Whisper diff | reword Việt thuần |
| 15 | Voice drift single-chunk | s5 ch9 R29 | seed re-init voice profile | em splice single không match | full section render (R81) |

### B. Audio Pipeline issues
| # | Type | Issue | Cause | Fix |
|---|------|-------|-------|-----|
| 1 | Aggressive bell-fade | "mất chữ" R19 | em apply 300ms exp on transient | revert peak cap global only |
| 2 | Pure silence boundary | "giật rời rạc" | -180 dB vs section -65 dB contrast | room tone -60 dB |
| 3 | Long pause | s4 ch36 2000ms, s2/s3/s5 ch >1500ms | spec gen quá dài | cap ≤ 1500ms |
| 4 | Onset burst | "nổ bụp bụp" mở chunk | silence→voice + /b/p/k/ initial | onset fade-in 50ms |

### C. Workflow issues
| # | Em sai | Lý do | Cam kết |
|---|--------|-------|---------|
| 1 | Không load full hiến pháp | R89 chưa enforce | tools/pre_render_audit auto-call R88 |
| 2 | Rotate text mechanical | Em không re-read | post_rotate_verify.py mandatory |
| 3 | Audio QA chỉ catch peak/bụp | em LLM text-only | TODO build Whisper diff |
| 4 | Ship partial | Mr.Long catch sau ship | R79 strict gate enforce |

---

## II. SFX LỖI (R39-R40 + ACE-Step v1-v4)

### A. Synthetic SFX numpy (R39 round 1)
| # | SFX | Mr.Long judge | Lý do |
|---|-----|---------------|-------|
| 1 | rain_steady (pink noise + drops) | "như tiếng đài sôi" | white hiss artifact |
| 2 | sad_piano (sine + harmonics + ADSR) | "như tiếng đàn nhị" | sustained bowed-like, not piano percussive |
| 3 | engine_rumble | OK | sine 80Hz + LFO acceptable |
| 4 | wind_gentle | OK | low-pass noise + LFO acceptable |

**Root cause:** Em build numpy synthetic không có proper instrument samples + physical model. Piano cần hammer attack + string decay (sample-based) hoặc physical modeling (Pianoteq).

### B. ACE-Step v1-v4 piano gen
| Version | Prompt format | Result Mr.Long | Issue |
|---------|---------------|----------------|-------|
| v1 (gen 11:30) | "slow emotional solo felt piano..." (sentence) | "ù ù như tiếng chuông không rõ nốt" | model trained on TAG list, sentence confused |
| v2 (gen 11:38) | "solo felt piano, clear melodic notes..." (mixed) | "không rõ piano" | ambient pad dominant |
| v3 (gen 11:43) | "solo piano, ambient piano, neoclassical..." (proper tags) | "nghe hay chưa rõ piano" | better but vẫn pad influence |
| v4 (gen 11:47, HDK master prompt) | 60+ tags (Mr.Long approved master + 27 negative) | **"vẫn có tiếng ù ù vọng"** | model carry-over vocoder noise floor |

**Root cause ACE-Step ù ù:**
1. **Trained on songs** (vocals + drums + electronics dataset)
2. **Negative tags** không hoàn toàn loại được pad/synth carry-over
3. **Vocoder reconstruction** luôn có noise floor (sample rate + diffusion artifact)
4. **Diffusion model** generative noise inherent (random walk)

### C. Settings ACE-Step thử (RTX 5060 Ti 16GB, 8GB VRAM peak)
- `infer_step`: 27 → 40 → 60 → 70 (more steps = more detail but vẫn ù)
- `guidance_scale`: 15 → 10 → 15 (no clear winner)
- `seed`: 42/123/999 (variant không fix base issue)
- `cfg_type`: apg (default)
- `scheduler_type`: euler (default)

---

## III. STRATEGY MUSIC DNA (Mr.Long ship docx 27/6)

### Pipeline đề xuất:
```
Reference Track → Music Analysis (25-40 attributes) → Music DNA → HDK Music Bible → ACE-Step Prompt V2
```

### 13 attributes em sẽ analyze nếu Mr.Long gửi reference WAV:
1. Tempo (BPM)
2. Key + Mode (A minor / D minor / E minor / etc.)
3. Hòa âm (chord progression Am-F-C-G etc.)
4. Mật độ giai điệu (sparse/minimal/busy/dense)
5. Cấu trúc (A/B/C section)
6. Dynamics (PPP-PP-P-MF-F)
7. Reverb (dry/room/hall/cathedral)
8. Chất liệu piano (felt/grand/upright/vintage)
9. Đường cong cảm xúc theo time (0-30s mood1, 30-60s mood2)
10. Nhạc cụ phụ (strings/pad/sub-bass nếu có)
11. Độ phức tạp giai điệu (linear/contrapuntal/syncopated)
12. Khả năng loop (seamless/with cue)
13. Yếu tố cần tránh (no electronic, no major key, etc.)

### Sample HDK_MUSIC_DNA.md structure:
```yaml
hdk_music_dna:
  tempo: 56 BPM
  key: A minor
  dynamics: PPP-P
  piano_type: Felt
  reverb: Room Medium
  emotion: Lonely
  melody: Minimal
  harmony: Dark
  texture: Ambient
```

---

## IV. CÂU HỎI MR.LONG PHÂN TÍCH

### Voice TTS:
- Em đã catch 30+ issues qua iteration R16→R38. Còn pattern lỗi nào em chưa detect?
- Mr.Long approve workflow R79+R89 strict gate cho EP02-90?

### SFX:
- **A**: Tiếp tục tune ACE-Step (Mr.Long gửi reference track → em analyze Music DNA → Prompt V2)?
- **B**: Switch FluidSynth + Anticipation MIDI piano (real sample-based deterministic, no AI noise)?
- **C**: Mr.Long manual download CC0 piano YouTube/Musopen → em mix?
- **D**: Combine A+B (ACE-Step ambient + FluidSynth piano melody layered)?

### Music DNA roadmap:
- Mr.Long ship reference track WAV/MP3 nào để em analyze 13 attributes?
- Mr.Long approve build `HDK_MUSIC_DNA.md` cho 5 themes (SAD/MYSTERY/TENSION/REVEAL/ENDING)?
