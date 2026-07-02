# Voice References — assets/voice_refs/

**Mr.Long lock 30/6 19:00 — Tier 2.x Phase 1**
**Schema source:** `bible/15_voice_bible.yaml` v2.0
**Manager:** `tools/voice_profile_manager.py` (R181b)

## Purpose

Golden reference WAV + cached speaker embedding cho mỗi character profile.
Speaker embedding extract qua ECAPA-TDNN (wespeaker / pyannote) — 192-dim vector.
Embedding cached `.npy` file để speaker similarity QA (R181c) load nhanh.

## Required files per character (LOCKED — KHÔNG đổi sau Phase 2)

| File | Format | Purpose |
|---|---|---|
| `<CHAR>_golden.wav` | WAV 22050Hz mono PCM_S16LE 8-15s clean speech | Source cho embedding + reference cho clone |
| `<CHAR>_embedding.npy` | numpy float32 shape (192,) | Cached ECAPA-TDNN embedding |
| `<CHAR>_embedding.sha256` | hex string | Integrity verify |

## Profiles required (4 mandatory)

| Voice ID | Source plan | Status |
|---|---|---|
| `NARRATOR` | Reuse `D:/rvc-vn/assets/weights/NNG.pth` source WAV — Hắc Dạ Ký (narrator ẩn danh) | PLACEHOLDER — TBD Phase 2 |
| `KHAI_PHONG` | Reuse `D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/GIỌNG ĐỌC  ANH KHÁNH.wav` baseline | PLACEHOLDER — TBD Phase 2 |
| `DRIVER` | Cần record / source — voice trầm già 55-65 tuổi | PLACEHOLDER — TBD Phase 2 |
| `GIRL_GHE7` | Cần record / source — voice nữ trẻ 20-28 tuổi | PLACEHOLDER — TBD Phase 2 |

## Build procedure (Phase 2 — KHÔNG do Phase 1)

```bash
# Step 1: produce golden WAV (manual edit từ source)
ffmpeg -i source.wav -ar 22050 -ac 1 -c:a pcm_s16le -t 12 KHAI_PHONG_golden.wav

# Step 2: extract embedding via ECAPA-TDNN
python tools/extract_speaker_embedding.py \
  --wav assets/voice_refs/KHAI_PHONG_golden.wav \
  --output assets/voice_refs/KHAI_PHONG_embedding.npy

# Step 3: compute sha256
python tools/extract_speaker_embedding.py --sha256 \
  --npy assets/voice_refs/KHAI_PHONG_embedding.npy \
  > assets/voice_refs/KHAI_PHONG_embedding.sha256

# Step 4: update bible/15 v2.0 with sha256
# Replace PLACEHOLDER_TBD_ON_FIRST_EMBEDDING_EXTRACT with real hash
```

## QA gate (R181c — Phase 2)

After every TTS render, per-chunk:
1. Extract embedding from rendered chunk WAV
2. Compare cosine similarity vs `<CHAR>_embedding.npy`
3. Threshold ≥ 0.85 PASS / < 0.85 BLOCK + auto-retry render

## Invariants (R181b sealed)

- LOCKED fields (voice_id, embedding path, embedding sha256, accent, timbre, gender, age, pitch base, rate base) — KHÔNG modify sau init
- Replace golden ref → MUST bump profile version + regenerate embedding + update sha256

## Status

**Phase 1 (30/6 — present):** Placeholder only. Manager + bible schema + tests built.
**Phase 2 (sau approve):** Build extract_speaker_embedding.py + populate 4 golden WAV + extract embeddings + populate sha256.
