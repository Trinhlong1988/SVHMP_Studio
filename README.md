# SVHMP Studio — Production Pipeline

```
Status:   PIPELINE READY (Phase 1 — text generation + QA)
Path:     D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\
Series:   CHUYẾN XE CUỐI CÙNG VỀ ĐÂU — 90 tập × 3 season, pivot ep 73
Cadence:  1 ep/day target → 90 ep ≈ 3 tháng production
Created:  2026-06-19 (theo kiến trúc Mr.Long docx round 7)
```

## Kiến trúc 10-file flat

```
SVHMP_Studio/
├── 01_series_bible.yaml          ← high-level config (immutable per series)
├── 02_lore_bible.yaml             ← luật bất biến + 21 facts mythology
├── 03_character_bible.yaml        ← bác tài + Nam (chỉ 2 recurring)
├── 04_state.yaml                  ← dynamic state — UPDATE sau MỖI ep
├── 05_episode_input.yaml          ← per-ep config — overwrite mỗi ep
├── 06_generator_prompt.md         ← SVHMP-10.0-RC3.2 (Story Generator)
├── 07_qa_prompt.md                ← SVHMP_CMD_QA_MASTER_LOCK_v1.0 (FROZEN)
├── 08_tts_prompt.md               ← TTS Director (STUB — chờ voice clone)
├── 09_video_prompt.md             ← Video Director (STUB — chờ LoRA train)
├── 10_youtube_prompt.md           ← Publisher (STUB — chờ MP4 thật)
├── output/
│   └── ep_{N}/
│       ├── input.yaml             ← snapshot of 05_episode_input.yaml at time
│       ├── episode.md             ← Generator output (1700-2000 từ)
│       ├── qa_output.yaml         ← QA Lock decision (PASS/REGEN/REVIEW)
│       ├── narration.wav          ← TTS output (after 08)
│       ├── video.mp4              ← Video output (after 09)
│       ├── final.mp4              ← Mux narration + video
│       ├── youtube_metadata.yaml  ← Publisher prep (after 10)
│       └── state_diff.yaml        ← changes applied to 04_state.yaml
└── README.md
```

## Pipeline per ep

```
1. EDIT  05_episode_input.yaml      (set ep_number, AUTO fields → user override nếu cần)
2. LOAD  01 + 02 + 03 + 04 + 05     (input to Generator)
3. RUN   06 (Generator: SVHMP-RC3.2) → output/ep_{N}/episode.md
4. RUN   07 (QA Lock v1.0)          → output/ep_{N}/qa_output.yaml
5. CHECK qa_output.decision:
        PASS              → goto 6
        REGEN             → loop 3 với regen_scope
        REVIEW_REQUIRED   → human manual review
6. RUN   08 (TTS)                   → output/ep_{N}/narration.wav
7. HUMAN TTS review                 → tweak emotion presets nếu cần
8. RUN   09 (Video)                 → output/ep_{N}/video.mp4
9. MUX   narration + video          → output/ep_{N}/final.mp4
10. RUN  10 (YouTube prep)          → output/ep_{N}/youtube_metadata.yaml
11. UPLOAD                          → YouTube channel
12. T+48h: scrape analytics         → output/ep_{N}/analytics_48h.yaml
13. UPDATE 04_state.yaml            (apply state_diff)
14. AGGREGATE batch 10 ep           → analytics_feedback.auto_tuning fire if drift
15. NEXT ep                         → step 1
```

## Phase tracking

### Phase 1 — Text Generation + QA (CURRENT)
- ✅ 01-07 hoàn tất
- ✅ Ep 01 sample đã ship (Desktop\ep_01_sample.md)
- ⏳ TODO: chạy QA Lock trên Ep 01 → verify hallucination → tweak
- ⏳ TODO: ship Ep 02-10 → batch QA → freeze RC3.2 → SVHMP-10.1-FINAL

### Phase 2 — TTS Production
- ⏳ Voice clone bác tài (30s sample)
- ⏳ ElevenLabs setup
- ⏳ IndexTTS2 fallback
- ⏳ Loudness normalization pipeline

### Phase 3 — Video Production
- ⏳ Train LoRA `lora_bus_night_rain_v01` (1048 ref pool)
- ⏳ Gen master assets → checksum sha256
- ⏳ ComfyUI workflow batch

### Phase 4 — Publish + Analytics Loop
- ⏳ YouTube channel + API
- ⏳ Thumbnail/end_screen template
- ⏳ Auto-caption + comment scraper
- ⏳ analytics_feedback loop → auto_tuning RC3.2.XXX

### Phase 5 — Python Studio Automation
- ⏳ Prompt Compiler (đọc 01-07, compose runtime → tiết kiệm token vs paste 103KB)
- ⏳ Multi-Agent split (Generator / QA / Parser / Scorer / TTS / Video / Publisher độc lập)
- ⏳ State Database (PostgreSQL hoặc SQLite cho 04_state.yaml)
- ⏳ Telemetry Dashboard (cost/retry/finish_rate/ROI)
- ⏳ Scheduler (1 ep/day auto)

## Pattern source

Kiến trúc 10-file flat theo Mr.Long docx round 7 (2026-06-19 00:38):
- Passenger có ID `PAS_XXXX` + display_name → 100 ep không quên/đổi tên
- Arc có `ARC_XXXX` + status (OPEN/PAYOFF/CLOSED) + importance (HIGH/MED/LOW)
- Lore + Character + State + Asset tách file riêng → AI load deterministic

Tương tự pipeline SVTK MMORPG: Load State → Process → Validate → Commit.

## Compatibility

| Component | Version | Status |
|---|---|---|
| Generator | SVHMP-10.0-RC3.2 | PC (sẽ → 10.1-FINAL sau 30 ep) |
| QA Lock | v1.0 | FROZEN |
| TTS prompt | 0.1 stub | STUB |
| Video prompt | 0.1 stub | STUB |
| YouTube prompt | 0.1 stub | STUB |

## Run pipeline

Hiện tại còn manual (Phase 5 chưa có Python).

Cách run thủ công:
1. Mở `05_episode_input.yaml` → set ep_number + override AUTO fields nếu cần.
2. Paste `01 + 02 + 03 + 04 + 05 + 06` vào Claude/GPT → nhận episode.md.
3. Paste `episode.md + 07` vào Claude/GPT (session khác) → nhận qa_output.yaml.
4. Review decision → loop hoặc proceed.

Phase 5 Python Studio sẽ thay step 2-4 thành 1 lệnh `python pipeline.py --ep 2`.
