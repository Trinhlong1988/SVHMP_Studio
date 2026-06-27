# ACE-Step Technical Report (Mr.Long requested 27/6)

## 1. Checkpoint
**Name:** `ACE-Step/ACE-Step-v1-3.5B`
**Source:** Hugging Face Hub
**Local cache:** `C:\Users\Administrator\.cache\ace-step\checkpoints\models--ACE-Step--ACE-Step-v1-3.5B\`
**Snapshot:** `82cd0d7b6322bd28cd4e830fe675ddb6180ce36c`
**Size:** ~7GB
**Auto-download:** Yes (first run if `checkpoint_dir=None`)

## 2. Model Architecture
```json
{
  "_class_name": "ACEStepTransformer2DModel",
  "_diffusers_version": "0.32.2",
  "attention_head_dim": 128,
  "in_channels": 8,
  "inner_dim": 2560,
  "lyric_encoder_vocab_size": 6693,
  "lyric_hidden_size": 1024,
  "max_height": 16,
  "max_position": 32768,
  "max_width": 32768,
  "mlp_ratio": 2.5,
  "num_attention_heads": 20,
  "num_layers": 24,
  "out_channels": 8,
  "patch_size": [16, 1],
  "rope_theta": 1000000.0,
  "speaker_embedding_dim": 512,
  "ssl_encoder_depths": [8, 8],
  "ssl_latent_dims": [1024, 768],
  "ssl_names": ["mert", "m-hubert"],
  "text_embedding_dim": 768
}
```

**Components:**
- ACEStepTransformer2DModel (24 layers, 20 heads, 2560 inner dim)
- DCAE (Deep Compression AutoEncoder) — `music_dcae_f8c8`
- Lyric encoder (vocab 6693)
- MERT + m-hubert SSL encoders (REPA alignment)

## 3. Inference Script

**Python file:** `C:\tmp\acestep_piano_v7_promptv3.py`

```python
import sys
sys.path.insert(0, r'C:\Users\Administrator\ace-step')
from acestep.pipeline_ace_step import ACEStepPipeline

pipeline = ACEStepPipeline(
    checkpoint_dir=None,        # auto-download
    dtype='bfloat16',           # RTX 5060 Ti optimized
    persistent_storage_path=None,
    torch_compile=False,        # avoid compile lag
)

pipeline(
    audio_duration=30.0,
    prompt=PROMPT_V3,           # see below
    lyrics='',                  # empty for instrumental
    infer_step=70,
    guidance_scale=15.0,
    scheduler_type='euler',
    cfg_type='apg',
    omega_scale=10.0,
    manual_seeds='999',
    guidance_interval=0.5,
    guidance_interval_decay=0.0,
    min_guidance_scale=3.0,
    use_erg_tag=True,
    use_erg_lyric=False,
    use_erg_diffusion=True,
    oss_steps='',
    guidance_scale_text=0.0,
    guidance_scale_lyric=0.0,
    save_path=OUT,
)
```

## 4. Launch Command

**Inference CLI:**
```bash
cd C:\Users\Administrator\ace-step
venv\Scripts\python.exe C:\tmp\acestep_piano_v7_promptv3.py
```

**Webui mode (alternative):**
```bash
cd C:\Users\Administrator\ace-step
acestep --port 7865 --bf16 true
```

## 5. VRAM Usage Observed (RTX 5060 Ti 16GB)
- Allocated: **7.44 GB**
- Reserved: **7.85 GB**
- Gen time 30s clip: ~3-5s diffusion + 1-2s preprocess + 1s decode = ~10s total

## 6. Generation History (5 versions tested)

| Version | Prompt approach | Verdict Mr.Long |
|---------|-----------------|-----------------|
| v1 | Sentence-style "slow emotional solo felt piano..." | "ù ù như tiếng chuông" |
| v2 | Hybrid sentence+tags "solo felt piano, clear notes..." | "không rõ piano" |
| v3 | TAG format "solo piano, ambient piano, neoclassical..." | "nghe hay chưa rõ piano" |
| v4 | HDK_MUSIC_MASTER 60+ tags | "vẫn ù ù vọng" |
| v5 | Mr.Long Prompt V2 (no ambient, dry piano) | "vẫn vọng quá ở 1 nốt" |
| v6 | + rhythm + chord progression emphasis | "vẫn nốt ù ù" |
| v7 (in progress) | Mr.Long Prompt V3 (clear emotional melody) | TBD |

## 7. Settings Tested
| Param | Values tried | Notes |
|-------|--------------|-------|
| `infer_step` | 27 / 40 / 60 / 70 | 60-70 standard from examples |
| `guidance_scale` | 10 / 15 | 15 standard |
| `cfg_type` | apg | default |
| `scheduler_type` | euler | default |
| `omega_scale` | 10.0 | default |
| `seed` | 42 / 123 / 456 / 789 / 999 | varied for diversity |
| `lyrics` | "" (empty) | per example for instrumental |

## 8. Sample WAV Files

1. `D:\SVHMP_Studio\assets\sfx\hdk_music_library\piano_acestep_v5_promptv2.wav` (Mr.Long Prompt V2)
2. `D:\SVHMP_Studio\assets\sfx\hdk_music_library\piano_acestep_v6_rhythm.wav` (rhythm focus)
3. `D:\SVHMP_Studio\assets\sfx\hdk_music_library\piano_acestep_v7_promptv3.wav` (Mr.Long Prompt V3 — pending)
4. `D:\SVHMP_Studio\assets\sfx\generated\piano_acestep_v4_hdk.wav` (HDK Master)

## 9. Persistent Issue
- Model consistently produces "ù ù vọng" (rumble + reverb tail)
- Negative tags ineffective for full suppression
- Possibly model trained on song-with-vocal dataset, instrumental piano in distribution tail
- Recommend report to ACE-Step community / Discord
