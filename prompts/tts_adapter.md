# CMD TTS ADAPTER — v1.0

```
spec_version  : SVHMP-TTSA-1.0
parent_pipeline: SVHMP-RC3.4 (Generator) → THIS → SVHMP-TTS-1.1 (M1-M8)
role          : module middleware giữa Generator output (văn học) và CMD TTS input (đọc-tối-ưu)
status        : DRAFT 2026-06-20
locked_by     : Mr.Long sign-off pending
deps          : episode.md (RC3.4 schema) — read only
out_dir       : SVHMP_Studio/output/ep_XX/tts_adapted/
```

---

## 1. LÝ DO TỒN TẠI

CMD TTS ADAPTER giải quyết 1 sự thật về production AI narration:

> **Script văn học ≠ script TTS-ready.** Cùng 1 câu chuyện, viết để đọc bằng mắt và viết để AI đọc thành tiếng là 2 ngôn ngữ khác nhau.

### Vấn đề khi đưa bản văn học thẳng vào TTS

| Triệu chứng | Root cause |
|---|---|
| **TTS đọc lặp 2 câu liền** | Câu cực ngắn liên tiếp (<4 từ) → engine mất context → autoregressive loop |
| **Nghe rời rạc** | Per-sentence prosody reset, không có flow câu chuyện |
| **Như đọc thông thường, không phải kể truyện** | Câu ngắn → không có dramatic pacing → flat prosody |
| **Ngắt nghỉ sai** | Dấu chấm sau câu 3-4 từ ≠ dấu chấm sau câu 15-20 từ về mặt cảm xúc, nhưng TTS treat giống nhau |
| **Tone không đổi** | Câu ngắn không cho TTS "đủ chỗ" để variation pitch |

### Cải thiện kỳ vọng

> **60-80% độ tự nhiên của giọng đọc AI tăng chỉ qua adapter, KHÔNG đổi engine TTS.**

ADAPTER không thay thế CMD TTS (v1.1 M1-M8 vẫn handle cadence/emotion/silence/ducking/LUFS). ADAPTER là pre-processor đảm bảo INPUT cho CMD TTS đạt chất lượng.

---

## 2. PIPELINE POSITION

```
┌─────────────────────────┐
│ CMD Generator RC3.4     │
│ Output: episode.md      │ ← script văn học, beat structure, ~1812 từ
│        (literary)       │   72% câu ≤12 từ (đúng rule mắt đọc, sai rule TTS)
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ CMD TTS ADAPTER v1.0    │ ← NEW (this spec)
│ Input:  episode.md      │
│ Output: episode.tts.yaml│ ← bản đọc-tối-ưu, scene-split, có pause/emph markup
│         scene_01..05.txt│   80% câu 8-25 từ, ≤3 câu cực ngắn liên tiếp
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ CMD TTS v1.1 M1-M8      │
│ Output: ep_XX.wav       │ ← gen TTS + silence + ducking + LUFS + brand_audio
│         (44100/mono)    │
└─────────────────────────┘
```

---

## 3. INPUT/OUTPUT CONTRACT

### INPUT
- **File:** `SVHMP_Studio/output/ep_XX/episode.md`
- **Schema:** SVHMP-RC3.4 (8 section + YAML metadata)
- **State expected:**
  - `prompt_version` matches `SVHMP-10.x` range
  - `narration_metrics.regret_lines` ≥ 4
  - 8 section headers (HOOK / SETUP / INCIDENT / REVEAL / PAYOFF / CLIFFHANGER + 2 optional)
  - Beat tags `[beat_N: EMOTION]`
  - Dialog em-dash `—`

### OUTPUT (atomic write)
- `episode.tts.yaml` — master manifest (scene index + emotion profile + global config)
- `scene_01_<slug>.txt` ... `scene_05_<slug>.txt` — 5 file đọc-tối-ưu (đã rewrite + tag)
- `tts_adapter_report.yaml` — QA report (rule violations, before/after metrics)

### Naming
Slug = từ khoá scene (vd `xe_dem`, `quang_nho_ha`, `tai_nan`, `xuong_xe`, `twist_ha`)

---

## 4. RULES CỨNG (R-1 → R-12)

### R-1: Độ dài câu
- **Câu đọc bình thường:** 8-25 từ
- **Câu punch line cố ý** (<4 từ): cho phép NHƯNG bắt buộc theo sau `[pause:NNNNms]` (700-2500ms tuỳ context)
- **Câu >25 từ:** chia thành 2 câu hoặc dùng dấu chấm phẩy + clause

### R-2: Đoạn (paragraph)
- **2-4 câu/paragraph**
- Paragraph 1 câu chỉ cho phép nếu là **scene transition** hoặc **punch standalone**
- Paragraph >4 câu: chia 2 paragraph

### R-3: Câu cực ngắn liên tiếp
- **KHÔNG cho phép >3 câu liên tiếp <6 từ** (trigger TTS lặp/loop)
- Vi phạm → gộp 2 câu lại bằng từ nối / trạng từ

### R-4: Câu cấu trúc giống nhau
- 2 câu cùng cấu trúc `Subject + Verb + (.)` trong khoảng <30 từ → rewrite 1 câu
- Ví dụ vi phạm: "Hà cười. Hà vẫy tay. Hà chạy đi."
- Rewrite: "Hà cười, rồi khẽ vẫy tay trước khi chạy vào cánh cửa kính."

### R-5: Pause markup
- Markup dạng `[pause:NNNNms]` ở cuối câu cần dramatic pause
- 6 mức chuẩn:
  - `pause:300ms` — micro (clause break trong cùng paragraph)
  - `pause:600ms` — short (kết câu narrator tĩnh)
  - `pause:1000ms` — medium (kết paragraph)
  - `pause:1500ms` — regret_before (trước câu regret peak)
  - `pause:2000ms` — regret_after (sau câu regret peak)
  - `pause:3000ms` — ending (kết scene)
- KHÔNG dùng silence concat cứng sau gen — markup ngay trong text để TTS handle

### R-6: Emphasis tagging
Markup `[emph:LABEL]` trước câu cần đọc đặc biệt. 6 label:
- `emph:punch` — câu ngắn dramatic, đọc NHANH + ngắt mạnh
- `emph:whisper` — câu narrator MEN whisper, đọc CHẬM + volume thấp
- `emph:regret_climax` — câu regret peak, đọc CHẬM HẲN + pitch trầm
- `emph:question` — câu hỏi, pitch tăng cuối
- `emph:flashback` — đoạn hồi tưởng, đọc đều đều mơ hồ
- `emph:reveal` — câu reveal sự thật, đọc rõ ràng + nhấn

### R-7: Latin/digit normalization
- Số → chữ Việt: `2 km` → `hai ki-lô-mét` / `7:10` → `bảy giờ mười` / `8 năm` → `tám năm`
- Ký tự Latin đơn → phiên âm: `B` → `Bê`, `JFK` → `J F K` (space-separated), `Mr.` → `Anh`
- Bảng dictionary `tts_adapter/normalize_dict.yaml` (extensible)

### R-8: Anti-repetition heuristic
- Phát hiện cấu trúc dễ gây TTS loop:
  - 3+ câu cùng subject liên tiếp (`Tôi sợ. Tôi sợ X. Tôi sợ Y.`) → gộp hoặc rewrite
  - Câu láy lại từ cuối câu trước (`...đồng hồ. Đồng hồ kia...`) → thêm clause trung gian
  - 4+ dấu `—` (dialog em-dash) liên tiếp KHÔNG có narrator → insert 1 narrator line
- Mỗi violation log vào `tts_adapter_report.yaml`

### R-9: Dialog (em-dash)
- Dialog em-dash giữ nguyên `—`
- Dialog ngắn (`— Dạ.`) ALLOW vì là speech realistic, KHÔNG count vào rule R-3
- Sau dialog ngắn cần thêm narrator line (1-2 câu) trước dialog kế tiếp nếu có em-dash chain >2

### R-10: Scene boundary
- 5 scene cứng theo beat:
  - `scene_01` = HOOK + SETUP (beat 1-2)
  - `scene_02` = INCIDENT (beat 3)
  - `scene_03` = REVEAL (beat 4 NGHẸN)
  - `scene_04` = PAYOFF (beat transition dư âm)
  - `scene_05` = CLIFFHANGER (beat 5 DƯ ÂM)
- Mỗi scene kết thúc với `[pause:3000ms]` (ending)
- Scene 1 mở đầu với brand intro block (chỉ ep_01 hoặc theo rule brand_audio CMD TTS)

### R-11: Brand intro (chỉ ep_01 mỗi season)
Block intro placed đầu `scene_01_*.txt`:
```
Kính chào quý thính giả.

Có những câu chuyện chỉ kể được lúc đêm khuya — khi đèn đã tắt, khi mưa còn rơi ngoài cửa kính, khi lòng người chưa kịp ngủ.

Đêm nay, qua giọng kể Nguyễn Ngọc Ngạn, xin gửi tới quý vị một loạt truyện ma của tác giả Khánh An. Những câu chuyện về điều người ta giấu kín, về những lời chưa kịp nói.

Mời quý thính giả lắng nghe. [pause:1500ms]

Tập một. Đồng hồ nữ màu xà cừ. [pause:2000ms]
```
Ep_02+ skip intro, vào thẳng HOOK.

### R-12: Idempotent
- Input cùng `episode.md` chạy ADAPTER 2 lần → output byte-identical
- Không stochastic: KHÔNG dùng LLM tự do rewrite. Rule-based + bounded substitution.
- Exception: nếu cần LLM rewrite (R-1 câu >25 từ, R-4 cấu trúc giống), seed cố định + prompt determinism.

---

## 5. 8 NHIỆM VỤ (M-1 → M-8)

### M-1 Sentence consolidation
- Scan paragraph → tìm 2-3 câu ngắn cùng subject hoặc cùng theme miêu tả
- Gộp bằng từ nối (`, rồi`, `, và`, `, kèm theo`, `cũng`, `cùng`)
- Bù preposition / trạng từ nếu cần (`Quang ngẩng lên` → `Quang khẽ ngẩng lên`)

### M-2 Pause insertion
- Apply rule R-5 6 mức pause
- Heuristic: mỗi `\n\n` paragraph break → tối thiểu `[pause:600ms]`
- Sau câu regret (match regret_pattern) → `[pause:1500ms]` trước, `[pause:2000ms]` sau
- Cuối scene → `[pause:3000ms]`

### M-3 Scene split
- Parse heading `## N. SECTION_NAME` từ episode.md
- Map 5 scene per R-10
- Strip section headers, beat tags, YAML metadata, SELF-CHECK / SCORE / STATE block
- Output 5 file scene_XX_<slug>.txt

### M-4 Emphasis tagging
- Auto-detect câu theo pattern → assign R-6 emph label
- Pattern table:
  - Câu ≤4 từ ở beat 4 NGHẸN section → `emph:punch`
  - Câu chứa "khẽ", "thì thầm", "như sợ" → `emph:whisper`
  - Câu chứa regret_pattern + ở REVEAL/PAYOFF → `emph:regret_climax`
  - Câu kết `?` → `emph:question`
  - Câu trong section FLASHBACK / "Trong đầu anh" → `emph:flashback`
  - Câu chứa "Là lúc", "Đúng là", "Tôi nhớ ra" → `emph:reveal`

### M-5 Anti-repetition rewrite
- Apply R-3, R-4, R-8 heuristic
- Rewrite candidate phải preserve SOUL (giữ nguyên thông tin + cảm xúc, chỉ đổi câu pháp)
- Log mọi rewrite vào report với before/after diff

### M-6 Latin/digit normalize
- Apply R-7 với dictionary
- Special handling: `7:10` (time) → `bảy giờ mười`, `2 km` → `hai ki-lô-mét`, `JFK` (airport) → `J F K`, single `B` (letter standalone) → `Bê`

### M-7 Beat → emotion profile assign
Mapping table emotion profile per scene (consumed by CMD TTS):

| Scene | Beat | spk_prompt | emo_prompt | pitch_semi | tempo | default_pause |
|---|---|---|---|---|---|---|
| scene_01 | establish | nng_sample | nng_v3_calm | -1.0 | 0.95 | 600ms |
| scene_02 | INCIDENT | nng_sample | nng_v3_calm | -1.0 | 0.95 | 600ms |
| scene_03 | REVEAL NGHẸN | nng_sample | nng_v3_regret | -1.5 | 0.88 | 800ms |
| scene_04 | PAYOFF dư âm | nng_sample | nng_v3_melancholy | -1.5 | 0.90 | 800ms |
| scene_05 | CLIFFHANGER | nng_sample | nng_v3_mystery | -2.0 | 0.85 | 1000ms |

(Ref files placeholder: actual paths defined trong `audio_assets.yaml` ở SVHMP_Studio root)

### M-8 Output schema emit
- Write 5 scene files
- Write `episode.tts.yaml`:
```yaml
ep_number: 1
adapter_version: SVHMP-TTSA-1.0
generated_at: 2026-06-20T08:50:00+07
brand_intro: true   # chỉ ep_01 season 1
scenes:
  - id: scene_01
    slug: xe_dem
    file: scene_01_xe_dem.txt
    profile: { spk_prompt: nng_sample, emo_prompt: nng_v3_calm,
               pitch_semi: -1.0, tempo: 0.95, default_pause: 600 }
    word_count: 540
    estimated_duration_sec: 230
  # ... scene_02..05
global:
  brand_intro_duration_sec: 28
  total_word_count: 1812
  total_estimated_duration_sec: 850
qa:
  rule_violations: 0
  rewrites: 7
  normalize_subs: 4
```
- Write `tts_adapter_report.yaml` (rule violations + diff log)

---

## 6. VÍ DỤ REWRITE (canonical)

### Ví dụ 1 — Sentence consolidation
```
GỐC:
Mưa rơi đều. Tiếng máy xe đều. Có ai đó ho khẽ ở phía sau. Quang không quay.

TTS:
Mưa rơi đều, tiếng máy xe cũng đều đều. [pause:300ms]
Phía sau, có ai đó ho khẽ, nhưng Quang không quay đầu lại. [pause:1000ms]
```
- Vi phạm: 4 câu liên tiếp <6 từ (R-3)
- Áp dụng: M-1 gộp 2+2 thành 2 câu / M-2 pause

### Ví dụ 2 — Anti-repetition (R-4 cấu trúc giống)
```
GỐC:
Hà cười. Hà vẫy tay. Hà mất hút sau cánh cửa kính.

TTS:
Hà cười, rồi khẽ vẫy tay, trước khi mất hút sau cánh cửa kính. [pause:1500ms]
```
- Vi phạm: 3 câu cùng cấu trúc `Hà + verb` (R-4)
- Áp dụng: M-5 rewrite 1 câu phức + M-2 pause regret_before

### Ví dụ 3 — Punch line giữ ngắn + markup pause
```
GỐC:
— Tôi nhớ ra rồi.

Tiếng anh khẽ. Như sợ Hà đang ngủ ở phòng bên.

— Bảy giờ mười.

— Là lúc Hà mất.

TTS:
[emph:reveal] — Tôi nhớ ra rồi. [pause:1500ms]

[emph:whisper] Tiếng anh khẽ, như sợ Hà đang ngủ ở phòng bên. [pause:1000ms]

[emph:punch] — Bảy giờ mười. [pause:1200ms]

[emph:regret_climax] — Là lúc Hà mất. [pause:2500ms]
```
- Giữ punch line ngắn (R-1 exception)
- M-2 pause markup explicit
- M-4 emphasis tag mỗi câu
- M-1 gộp "Tiếng anh khẽ. Như sợ..." thành 1 câu

### Ví dụ 4 — Latin/digit normalize
```
GỐC:
"Cầu Long Biên — 2 km."
Hà xuống sân bay JFK. Tôi đứng cổng B.

TTS:
"Cầu Long Biên — hai ki-lô-mét." [pause:1000ms]
Hà xuống sân bay J F K. Tôi đứng cổng Bê. [pause:600ms]
```

### Ví dụ 5 — Scene transition đầu/cuối
```
SCENE 03 cuối (REVEAL ending):
... [emph:regret_climax] — Là lúc Hà mất. [pause:2500ms]

[emph:whisper] Sương ngoài cửa kính tách ra.
Một ngọn đèn vàng hiện lên ở cuối con dốc. [pause:3000ms]

SCENE 04 đầu (PAYOFF):
Quang đứng dậy, chậm rãi, như có ai đỡ vai anh từ phía sau. [pause:600ms]
```

---

## 7. EDGE CASES

### EC-1: Dialog chain ngắn liên tiếp
```
GỐC:
— Dạ.
— Của ai vậy chú?
— Của một người bạn.

TTS (giữ nguyên — R-9 exception cho dialog):
— Dạ. [pause:600ms]
— Của ai vậy chú? [pause:600ms]
— Của một người bạn. [pause:1000ms]
```
Dialog ngắn KHÔNG count R-3, nhưng pause sau cần explicit.

### EC-2: Câu mở đầu paragraph là punch
```
GỐC paragraph:
Quang cứng người.

Anh không trả lời ngay. Anh nhìn chiếc đồng hồ trong tay.

TTS:
[emph:punch] Quang cứng người. [pause:1200ms]

Anh không trả lời ngay, chỉ nhìn xuống chiếc đồng hồ trong tay. [pause:1000ms]
```

### EC-3: Câu hồi tưởng (FLASHBACK)
```
GỐC:
Trong đầu anh, Hà đang đứng ở cổng B.
Hà mặc áo gió xanh nhạt.
Tóc Hà cột cao.
Hà cười. Hà vẫy tay. Hà mất hút sau cánh cửa kính.

TTS:
[emph:flashback]
Trong đầu anh, Hà đang đứng ở cổng Bê, mặc áo gió xanh nhạt, tóc cột cao. [pause:600ms]

Hà cười, rồi khẽ vẫy tay, trước khi mất hút sau cánh cửa kính. [pause:1500ms]
```
Toàn flashback paragraph gắn 1 emph tag đầu, hết flashback xoá tag.

### EC-4: Title / metadata trong section
- YAML block ` ``` ... ``` ` → strip
- `## N. SECTION (...) [beat_N: ...]` → strip
- `---` divider → strip
- `[chuông ngân...]` stage direction → strip (TTS không đọc)
- `# SELF-CHECK` đến hết file → strip

---

## 8. QA CHECKLIST (pre-ship)

ADAPTER ship phải pass 12/12:

- [ ] 1. 5 scene file tồn tại với naming chuẩn
- [ ] 2. Mỗi scene file có ≥1 `[pause:NNNNms]` markup
- [ ] 3. KHÔNG còn raw `\n\n\n+` (max 1 blank line)
- [ ] 4. KHÔNG còn chứa: `## `, `---`, YAML code fence, `# SELF-CHECK`, `[chuông`, `[beat_`
- [ ] 5. KHÔNG còn ký tự Latin đơn lẻ (regex `\b[A-Z]\b` = 0 match, trừ trong dictionary allow-list)
- [ ] 6. KHÔNG còn digit (regex `\d` = 0 match)
- [ ] 7. R-3 violation count ≤ 2 (3+ câu ngắn liên tiếp)
- [ ] 8. R-4 violation count ≤ 1
- [ ] 9. R-8 anti-repetition violation = 0
- [ ] 10. `episode.tts.yaml` valid YAML + match schema
- [ ] 11. Idempotent: chạy 2 lần → diff = 0
- [ ] 12. `total_estimated_duration_sec` trong khoảng 12.5-14.5 phút (target SVHMP)

Vi phạm bất kỳ → ADAPTER refuse ship, log lỗi vào `tts_adapter_report.yaml`.

---

## 9. SCHEMA YAML chi tiết

### episode.tts.yaml
```yaml
schema_version: SVHMP-TTSA-1.0
ep_number: <int>
adapter_run_at: <ISO8601>
source_episode_md_sha256: <hex>
brand_intro: <bool>   # true chỉ ep đầu season

scenes:
  - id: <"scene_01" | ... | "scene_05">
    slug: <string>   # vd "xe_dem"
    file: <string>   # tên file relative
    beat: <"HOOK_SETUP" | "INCIDENT" | "REVEAL" | "PAYOFF" | "CLIFFHANGER">
    profile:
      spk_prompt: <string>   # key trong audio_assets.yaml
      emo_prompt: <string>
      pitch_semi: <float>
      tempo: <float>
      default_pause: <int>   # ms
    word_count: <int>
    estimated_duration_sec: <float>
    pause_markup_count: <int>
    emph_markup_count: <int>

global:
  brand_intro_duration_sec: <float>   # 0 nếu không có
  total_word_count: <int>
  total_estimated_duration_sec: <float>

qa:
  pass: <bool>
  rule_violations: <int>
  rewrites_applied: <int>
  normalize_substitutions: <int>
  warnings: [<string>, ...]
```

### tts_adapter_report.yaml
```yaml
adapter_run_at: <ISO8601>
ep_number: <int>
rules_checked: [R-1, R-2, ..., R-12]
violations:
  - rule: R-3
    location: scene_01_xe_dem.txt:line_42
    detail: "4 câu liên tiếp <6 từ"
    action: auto_rewrite
    before: "Mưa rơi đều. Tiếng máy xe đều. Có ai đó ho khẽ ở phía sau. Quang không quay."
    after: "Mưa rơi đều, tiếng máy xe cũng đều đều. Phía sau, có ai đó ho khẽ, nhưng Quang không quay đầu lại."
rewrites:
  - rule: R-4
    location: scene_03_tai_nan.txt:line_5
    before: "Hà cười. Hà vẫy tay. Hà mất hút."
    after: "Hà cười, rồi khẽ vẫy tay, trước khi mất hút."
normalize_subs:
  - { from: "2 km", to: "hai ki-lô-mét", count: 1 }
  - { from: "JFK", to: "J F K", count: 1 }
  - { from: "cổng B", to: "cổng Bê", count: 2 }
metrics:
  before_total_sentences: 256
  after_total_sentences: 178
  before_pct_under_4_words: 22%
  after_pct_under_4_words: 8%
  before_pct_8_to_25_words: 41%
  after_pct_8_to_25_words: 79%
qa_pass: true
```

---

## 10. IMPLEMENTATION HINTS

- Language: **Python 3.11** (consistent với pipeline NNG)
- Entry: `tts_adapter.py --input episode.md --output_dir ./tts_adapted/`
- Dependencies: `pyyaml`, `regex` (Vietnamese diacritics), KHÔNG dùng LLM ngoài cho R-12 idempotent
- Normalize dictionary: tách file `tts_adapter_normalize_dict.yaml`
- Audio assets ref: tách file `SVHMP_Studio/audio_assets.yaml`
- Logging: structured (stdout JSON line) — CI/CD friendly
- CI gate: pre-commit hook chạy adapter trên test fixture, diff với golden output

---

## 11. NEXT STEPS

1. Mr.Long review spec → sign-off rules R-1 → R-12 (đặc biệt threshold 8-25 từ, 6 mức pause)
2. Em viết `tts_adapter.py` impl (~600-800 LOC ước tính)
3. Test fixture: 3 ep mẫu (ep_01 RC3.4 + 2 ep tạo thêm với pattern khó)
4. Áp adapter lên ep_01 hiện tại → regen 5 scene .txt → re-run CMD TTS → A/B với version cũ
5. Nếu pass → freeze SVHMP-TTSA-1.0 → integrate vào CI gate Generator → ADAPTER → TTS

---

## 12. STATUS

```yaml
spec: SVHMP-TTSA-1.0
status: DRAFT (pending Mr.Long sign-off)
written_by: claude-code-cmd-tts-adapter-bot
written_at: 2026-06-20T08:50:00+07
size_kb: ~21
```
