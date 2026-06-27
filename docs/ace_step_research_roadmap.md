# ACE-Step Research Roadmap — HDK Music Library

## ⚠️ CHỐT STRATEGY 2026-06-27 — Mr.Long approved

### KHÔNG train từ đầu
- Tốn dataset rất lớn, GPU lớn, time dài
- KHÔNG đáng cho kênh YouTube

### Fine-tune LoRA — CHƯA phải bước đầu
- H200 mất 2.5h với 23 bài
- RTX 5060 Ti 16GB khó (LoRA training cần ~24GB+ thoải mái)
- Bản quyền dataset = rủi ro lớn (Freesound CC0 vẫn có commercial use grey)

### Bước đầu = HDK Music Bible workflow:
```
1. ACE-Step local generate (CHƯA train, prompt-based)
2. Chọn 50-100 loop chất lượng tốt
3. Xây HDK Music Bible (theme catalog)
4. Dùng ổn định cho 30-50 video đầu
5. Sau đó mới quyết định fine-tune LoRA
6. Fine-tune chỉ đáng khi xác định được "chất nhạc HDK" qua data thực tế
```

### Kết luận thực tế Phase ƯU TIÊN:
- ✅ **Phase 0 LIBRARY BOOTSTRAP** (1 tuần)
- ⏸ Phase 1-4 DEFERRED đến sau 30-50 video

---

## 📋 PIPELINE Mr.Long LOCK 2026-06-27

### Giai đoạn A — Generate 4 base themes (30s each loop)

**Output:**
```
SVHMP_Studio/assets/sfx/hdk_music_library/
├── HDK_Piano_01_Sad_30s.wav       (HOOK + SETUP base)
├── HDK_Piano_02_Tension_30s.wav   (INCIDENT)
├── HDK_Piano_03_Reveal_30s.wav    (REVEAL peak)
├── HDK_Piano_04_Ending_30s.wav    (PAYOFF + CLIFF)
```

**Master prompt template (Mr.Long approved):**
```
Slow emotional solo felt piano, Vietnamese spiritual storytelling atmosphere,
dark cinematic ambient, soft reverb, minimal melody,
no vocals, no drums, no pop rhythm, no bright major chords,
suitable for ghost story narration, 30 seconds seamless loop.
```

**Per-theme variants:**
- Theme 01 Sad: `melancholic, A minor, 60 bpm, slow felt piano, dark ambient pad, gentle reverb`
- Theme 02 Tension: `dissonant chord, sub-bass drone, mysterious, 50 bpm, suspended notes`
- Theme 03 Reveal: `dark cinematic, low strings + piano, climactic, 70 bpm, emotional swell`
- Theme 04 Ending: `lingering felt piano, fading reverb, contemplative, 55 bpm, open question`

### Giai đoạn B — QA filter (LOẠI BỎ)

❌ Reject ngay nếu:
- Quá vui / cheerful
- Quá pop / electronic dance rhythm
- Có vocal / human voice
- Melody quá nổi → lấn giọng kể
- Loop bị gãy / abrupt cut
- Âm thanh vỡ / clipping / distortion

✅ Accept criteria:
- Mood phù hợp horror/ghost story
- Seamless loop transition
- Minimal melody (không lấn voice)
- Dynamic range -25dB to -35dB (mix background safe)
- No major dissonance
- Vietnamese spiritual feeling

### Giai đoạn C — Library expansion (după A + B)

1. Gen 30-50 variants per theme (different seeds)
2. QA → keep top 10-20 per theme
3. Build `library_index.yaml` catalog với metadata
4. Reuse cho EP02-90

### Giai đoạn D — Sau 100-200 loops + 30-50 videos
- Đánh giá "chất nhạc HDK" qua video data
- Nếu pattern rõ → train LoRA với dataset SELF-MADE (tránh bản quyền)
- KHÔNG dùng dataset người khác





## 1. Architecture (per Technical Report arxiv 2506.00045)

**ACE-Step v1.5 = Hybrid Diffusion + Linear Transformer**
- **Backbone**: Diffusion Transformer (DiT)
- **Encoder**: Sana Deep Compression AutoEncoder (DCAE)
- **Alignment**: MERT + m-hubert semantic representation (REPA)
- **Sampler**: Pingpong SDE (better music consistency)
- **Model size**: 3.5B parameters

**Inference characteristics:**
- 4 phút nhạc trong 20s trên A100 (15× faster than LLM baselines)
- RTX 5060 Ti 16GB: inference OK với `--bf16 true` (per memory)
- VRAM peak ~10-14GB inference

## 2. Fine-tune Support — LoRA confirmed working

**Repo có sẵn:**
- `TRAIN_INSTRUCTION.md` — full training pipeline
- `trainer.py` — PyTorch Lightning training loop
- `config/zh_rap_lora_config.json` — example r=256
- `config/vpop_lora_config.json` — example r=16 (memory-saving)
- `ZH_RAP_LORA.md` — case study Chinese rap LoRA fine-tune
- `convert2hf_dataset.py` — dataset conversion

**LoRA params:**
- target_modules: linear_q/k/v + to_q/k/v + to_out.0 (attention layers)
- r=16 (small/RTX 5060) OR r=256 (large GPU)
- speaker_embedder layer included

## 3. Dataset Format

Per file **3 components**:
```
data/
├── theme_001.mp3        # audio sample (10-30s ideal)
├── theme_001_prompt.txt # "slow emotional piano, cinematic, melancholic, 60 bpm, A minor, dark ambient"
└── theme_001_lyrics.txt # "[instrumental]" if no vocals
```

**Convert to HuggingFace dataset:**
```bash
python convert2hf_dataset.py --data_dir "./hdk_piano_data" --repeat_count 500 --output_name "hdk_piano_lora_dataset"
```

## 4. VRAM + Time RTX 5060 Ti 16GB Estimate

| Config | VRAM | Time/step | Total 2000 steps |
|--------|------|-----------|------------------|
| r=8 batch=1 bf16 | ~10 GB | 2-3s | 1-2h |
| r=16 batch=1 bf16 | ~12 GB | 3-4s | 2-3h |
| r=32 batch=1 bf16 | ~14 GB | 4-5s | 3-4h |
| r=64 batch=1 bf16 | ~15.5 GB | 5-6s | 4-5h (risk OOM) |

**Khuyến nghị RTX 5060 Ti:** r=16 batch_size=1 bf16 → 2-3h cho 2000 steps. Có thể accumulate_grad_batches=4 simulate batch=4.

## 5. HDK Music Model Roadmap

### Phase 0 — Library bootstrap (1 tuần)
1. Define 5-10 themes EP01-90:
   - Theme 01: Chuyến xe đêm (sad piano + atmospheric)
   - Theme 02: Hồi tưởng (warm nostalgic piano)
   - Theme 03: Reveal cao trào (dark cinematic strings + piano)
   - Theme 04: Payoff lingering (felt piano + reverb)
   - Theme 05: Cliffhanger open (mystery + sub-bass)
   - Theme 06-10: TBD per EP arc
2. ACE-Step prompt-based gen 3-5 variants per theme (no LoRA)
3. Mr.Long QA + save approved variants to library
4. Build `library_index.yaml` metadata catalog

### Phase 1 — Dataset preparation (1 tuần)
1. Download 100+ piano samples (Freesound CC0 / Musopen / YouTube Audio Library)
2. Stem-isolate piano với Demucs (đã có per memory)
3. Trim 10-30s clips
4. Tag với HDK-style prompt (melancholic, slow, dark ambient, Vietnamese spiritual)
5. Convert to HF dataset

### Phase 2 — Train HDK LoRA (3 ngày)
1. Config r=16 bf16 batch=1 grad_accum=4
2. Train 2000 steps ~2-3h
3. Validate quality vs base ACE-Step
4. Iterate prompt + data quality

### Phase 3 — Production deployment
1. Integrate HDK LoRA vào pipeline EP02-90
2. Per-section prompt template (HOOK/SETUP/INCIDENT/REVEAL/PAYOFF/CLIFF)
3. Save generated music vào library + auto-pick reuse
4. Quality gate: human QA + audio QA tool (R80)

### Phase 4 — Brand audio identity
1. HDK intro motif (5-10s signature) train explicit
2. Per-series sub-theme (Chuyến xe đêm vs Trạm cuối âm dương)
3. Music DNA fingerprint check

## 6. Open questions Mr.Long approve trước Phase 1

1. **Dataset source**: Freesound CC0 (legal safe) OR YouTube (commercial risk)?
2. **Music genre commit**: 100% piano-based OR allow strings/synth?
3. **Cultural tone**: Vietnamese folk piano element OR Western cinematic only?
4. **License**: CC-BY for HDK Music Library OR keep proprietary?

## 7. Reuse rules EP02-90

```yaml
section_music_pick:
  HOOK: theme_05_mystery
  SETUP: theme_01_chuyen_xe_dem (low volume -32dB)
  INCIDENT: theme_03_dark_cinematic (gradual)
  REVEAL: theme_03_peak + theme_04_payoff cross-fade
  PAYOFF: theme_04_lingering
  CLIFFHANGER: theme_05_open_question
boundary_pick: silent room tone -60dB (per R66)
```

## Status hiện tại
- ⏳ ACE-Step inference test prompt-based đang chạy
- 📋 Roadmap ship Phase 0-4 chờ Mr.Long approve
- 🛠️ Tools sẵn: ACE-Step + LoRA + Demucs + Anticipation + FluidSynth
