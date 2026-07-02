# ACE-Step v1.5 — Deep Research (HDK Music Library)

## 🏗️ Architecture (verified config.json)

### DiT (acestep-v15-turbo) — Transformer
```yaml
architectures: AceStepConditionGenerationModel
model_type: acestep
model_version: turbo
is_turbo: true                    # 8-step inference cap
hidden_size: 2048
num_hidden_layers: 24             # DiT depth
num_attention_heads: 16
num_key_value_heads: 8            # GQA (grouped query attention)
head_dim: 128
intermediate_size: 6144
max_position_embeddings: 32768
layer_types: [sliding_attention, full_attention] * 12  # alternating
sliding_window: 128
rope_theta: 1000000               # long context support
rms_norm_eps: 1e-06
dtype: bfloat16

# Audio-specific
audio_acoustic_hidden_dim: 64
fsq_dim: 2048                     # Finite Scalar Quantization
fsq_input_levels: [8, 8, 8, 5, 5, 5]  # 6-level FSQ codebook
patch_size: 2

# Encoders (sub-modules)
num_lyric_encoder_hidden_layers: 8
num_timbre_encoder_hidden_layers: 4
timbre_hidden_dim: 64
timbre_fix_frame: 750
text_hidden_dim: 1024
num_audio_decoder_hidden_layers: 24

# Flow matching
timestep_mu: -0.4
timestep_sigma: 1.0
```

### LM Models (Chain-of-Thought planner)
```
acestep-5Hz-lm-0.6B   (Qwen3-0.6B base)  — Medium understanding
acestep-5Hz-lm-1.7B   (Qwen3-1.7B base)  — Medium understanding/composition  ← em đang dùng
acestep-5Hz-lm-4B     (Qwen3-4B base)    — Strong composition + melody copy
```

LM functions: query rewrite + CoT metas + audio understanding + composition capability

### Text Encoder
- **Qwen3-Embedding-0.6B** (replaces UMT5 from v1)
- text_hidden_dim: 1024
- 50+ languages support

### VAE
- Separate `vae/` directory
- diffusion_pytorch_model.safetensors
- Encodes 48kHz audio → latent → DiT

## 🎯 DiT Model Zoo (4 variants)

| Variant | CFG | Steps | Quality | Diversity | Fine-tune | HF |
|---------|-----|-------|---------|-----------|-----------|-----|
| `acestep-v15-base` | ✅ | 50 | Medium | High | Easy | Pretrained only |
| `acestep-v15-sft` | ✅ | 50 | High | Medium | Easy | Pretrained + SFT |
| **`acestep-v15-turbo`** | ❌ | **8** | **Very High** | Medium | Medium | **CURRENT** (Pretrained + SFT + Distill) |
| `acestep-v15-turbo-rl` | ❌ | 8 | Very High | Medium | Medium | Pretrained + SFT + RL (to release) |

**Em đang dùng turbo** — Very High quality, 8 steps only (no CFG support).

## 🎵 Supported Tasks (7 types)

| Task | turbo | Description |
|------|-------|-------------|
| **text2music** | ✅ | Generate from caption + lyrics |
| **cover** | ✅ | Style cover with reference audio |
| **repaint** | ✅ | Repaint section of existing audio |
| **extract** | ❌ (base only) | Extract stems |
| **lego** | ❌ (base only) | Stitch sections |
| **complete** | ❌ (base only) | Complete partial audio |
| **vocal_to_bgm** | ✅ | Convert vocal to instrumental backing |

## ⚡ Performance (RTX 5060 Ti 16GB measured)

| Operation | Time |
|-----------|------|
| Model load (first) | ~30s |
| Encoder time | 0.08s |
| **Diffusion (8 steps)** | **1.19s** |
| Per-step | 0.15s |
| VAE decode (tiled) | 0.5s |
| **Total gen 30s audio** | **~1.3s** |

VRAM: ~7GB peak (Qwen3 LM + DiT + VAE + text encoder)

## 🎛️ Generation Parameters (handler.generate_music)

```python
captions: str                # main prompt (< 512 chars)
lyrics: str                  # "[Instrumental]" for no vocals (< 4096 chars)
bpm: int                     # 30-300 (or None for auto)
key_scale: str               # "A minor", "C Major" (or "" for auto)
time_signature: str          # "2", "3", "4", "6" (or "" for auto)
vocal_language: str          # "en", "zh", "ja", "unknown" (50+ codes)
inference_steps: int         # 8 for turbo, 32-100 for base
guidance_scale: float        # CFG strength (base only, turbo ignored)
seed: int                    # -1 for random
audio_duration: float        # 10-600s (or -1 for auto)
task_type: str               # "text2music", "cover", "repaint", etc.

# Advanced DiT
use_adg: bool                # Adaptive Dual Guidance (base only)
cfg_interval_start/end: float  # 0.0-1.0 CFG window
shift: float                 # timestep shift factor (default 1.0)
infer_method: str            # "ode" default

# 5Hz LM CoT (Chain-of-Thought)
thinking: bool               # Enable LM reasoning
lm_temperature: float        # 0.0-2.0
lm_cfg_scale: float          # CFG for LM
lm_top_k/top_p: int/float    # Sampling
lm_negative_prompt: str      # LM control
use_cot_metas: bool          # LM generates music metadata
use_cot_caption: bool        # LM rewrites caption
use_cot_language: bool       # LM detects vocal language
```

## 🔥 Key Differentiators v1.5 vs v1

| Feature | v1 (ACE-Step-v1-3.5B) | v1.5 (Ace-Step1.5) |
|---------|----------------------|-------------------|
| **Architecture** | Diffusion + linear transformer | LM (planning) + DiT (synthesis) hybrid |
| **Speed** | 15× faster than LLM baselines | <2s/song on A100, **1.3s on 5060 Ti** |
| **VRAM** | ~7-8 GB | <4 GB claimed (7GB measured ours) |
| **Training data** | Mixed (potential copyright) | **Licensed + royalty-free + MIDI-to-audio** ✅ commercial-ready |
| **Text encoder** | UMT5 | **Qwen3-Embedding-0.6B** (better multilingual) |
| **CoT planning** | ❌ | ✅ 5Hz LM Chain-of-Thought |
| **Languages** | 19 | **50+** |
| **Inference steps** | 27-100 | **8 (turbo)** |
| **Pipeline** | `ACEStepPipeline` | `AceStepHandler` |
| **Repo** | acestep package | `ace-step-v15-space` (HF Space code) |

## 🚀 Advanced Features

### 1. Chain-of-Thought reasoning (Qwen3 LM)
- LM auto-generates: metadata, captions, lyrics, audio codes
- Reduces user effort: just give topic → LM expands
- `use_cot_metas=True` → LM picks BPM, key, instruments

### 2. Multi-task editing
- **cover**: Generate cover with same melody but new instrumentation
- **repaint**: Re-generate specific section (start_time, end_time)
- **vocal_to_bgm**: Strip vocals + create instrumental

### 3. Reference audio conditioning
- Pass `reference_audio` for style transfer
- `audio_cover_strength` (0.0-1.0) controls influence

### 4. Audio codes (advanced)
- `audio_codes` string for code-level control
- Useful for precise music structure

### 5. LoRA support (from v1 carried over)
- `load_lora(lora_path)` / `unload_lora()`
- Compatible LoRA dataset format (3 files: mp3 + prompt.txt + lyrics.txt)

## 🎼 Best Practices for HDK Piano

### Prompt format (verified working tags)
```python
captions = "solo felt piano, dry recording, clear emotional piano melody, slow lyrical phrases, recognizable rhythm, simple repeating motif, intimate piano, late night storytelling, melancholic, A minor, 56 BPM, instrumental"
lyrics = "[Instrumental]"
```

### Key params for piano-only
- `bpm=56` explicit
- `key_scale="A minor"` explicit
- `time_signature="4"` explicit
- `vocal_language="en"` (placeholder when instrumental)
- `task_type="text2music"`
- `inference_steps=8` (turbo cap)
- `audio_duration=30.0` (loop unit)
- Multiple seeds for variants

### Output format
- 48000 Hz sample rate
- Stereo (2-ch tensor [2, 1440000])
- bfloat16 → convert .float().cpu().numpy()
- Returns dict: `{'tensor': tensor, 'sample_rate': 48000}`

## 📚 Mr.Long Workflow Integration

### Phase 0 — HDK Music Library (Mr.Long approved)
```python
HDK_THEMES = {
    'HDK_SAD':     {'key': 'A minor', 'bpm': 56, 'mood': 'melancholic, sad, lonely'},
    'HDK_MYSTERY': {'key': 'D minor', 'bpm': 58, 'mood': 'mysterious, eerie, suspenseful'},
    'HDK_TENSION': {'key': 'C minor', 'bpm': 60, 'mood': 'tense, anxious, foreboding'},
    'HDK_REVEAL':  {'key': 'E minor', 'bpm': 54, 'mood': 'climactic, dramatic, dark'},
    'HDK_ENDING':  {'key': 'G minor', 'bpm': 52, 'mood': 'lingering, contemplative, fading'},
}
SEEDS = [42, 123, 456, 789, 999]
# 5 themes × 5 seeds = 25 clips × 30s = ~30s total gen time!
```

### Phase 1 — Music DNA workflow (Mr.Long ship docx 27/6)
- Mr.Long gửi reference WAV → em analyze 13 attributes
- Build `HDK_MUSIC_DNA.md` catalog
- Generate Prompt V2 → gen variants

## 🔮 Future paths

### A. Use larger LM (acestep-5Hz-lm-4B)
- Better composition + melody understanding
- ETA install: download 4B model (~8GB extra)

### B. Try base/sft variants
- `acestep-v15-base` for more diversity (50 steps + CFG)
- `acestep-v15-sft` for higher quality

### C. LoRA fine-tune for HDK style
- After collecting 100+ approved loops
- Use ACE-Step LoRA training pipeline (TRAIN_INSTRUCTION.md)
- RTX 5060 Ti 16GB: r=16 bf16 batch=1 grad_accum=4

### D. ACE-Step Space self-host
- Full webui via `python app.py`
- Browse generated clips + metadata
- Save to library workflow

## 🛠️ Setup Notes (RTX 5060 Ti Windows specific)

### Working dependency versions
```
torch==2.7.1+cu128
transformers==4.57.0
diffusers (latest)
vector-quantize-pytorch==1.27.15  ← downgrade from 1.29 to avoid meta tensor bug
einops, einx, frozendict, accelerate
soundfile, torchcodec
nano-vllm (local third_parts/)
```

### Required workaround (meta tensor bug)
```python
import torch
torch.set_default_device('cpu')  # init on CPU
import transformers
transformers.modeling_utils._LOW_CPU_MEM_USAGE_DEFAULT = False
# THEN load model
# After load:
torch.set_default_device('cuda')  # switch for inference
```

### Code paths
- HF Space code: `C:\Users\Administrator\ace-step-v15-space\`
- Model cache: `C:\Users\Administrator\.cache\huggingface\hub\models--ACE-Step--Ace-Step1.5\`
- Inference script: `C:\tmp\acestep_v15_full.py`

## 🎯 Recommended next steps

1. **Test 5 HDK themes batch** (25 clips, ~35s total gen time)
2. **Mr.Long QA + select** best 1-2 per theme
3. **Mr.Long ship reference WAV** → em build Music DNA Prompt V2
4. **Build HDK_MUSIC_DNA.md** catalog
5. **Integrate vào EP01 R39** mix layer

## 📊 Comparison vs v1 cuối session

| Aspect | v1 cuối (v4 prompt) | v1.5 turbo (v1 prompt) |
|--------|---------------------|------------------------|
| Quality verdict | "vẫn ù ù vọng" | Pending Mr.Long QA |
| Gen time 30s | ~12s | **1.3s** |
| VRAM peak | 7.85 GB | 7 GB |
| Architecture | Old DiT | LM+DiT hybrid |
| Training data | Mixed | Licensed/royalty-free |
| Commercial use | Risky | ✅ Safe |
