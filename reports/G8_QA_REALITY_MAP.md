# G8 — QA RUNTIME REALITY MAP (D1)

> **REALITY ANCHOR** cho pack `g8_qa_runtime` (claim CMD_BUILD_2, 2026-07-09). Ghi lại hiện trạng
> lớp QA runtime TRƯỚC khi sửa bất cứ gì (D2→D7). Mọi kết luận **verify bằng đọc code thật** (file:line),
> KHÔNG chép mù `prompts/TASK_G8_QA_RUNTIME.md` — task doc tự cảnh báo có thể sai vài chỗ, và verify
> độc lập đã tìm ra **4 sai lệch thật** (mục cuối). D1 read-only: KHÔNG sửa file nào.

**Nguồn verify:** đọc trực tiếp `tools/*.py` + `governance/file_index.yaml` + `governance/blueprint/blueprint_domains.yaml` + `governance/architecture_registry.yaml` (9/7). Line-number theo trạng thái repo 9/7 — có thể dịch nhẹ khi file đổi, ý nghĩa giữ nguyên.

---

## 1. SÁU LUỒNG QA CHẠY SONG SONG (entry point → gọi thật cái gì)

| # | Entry point | Gọi thật (file:line) | Codify trong pack5? |
|---|---|---|---|
| 1 | `svhmp_preflight_qa.py` (FULL_TEXT_GATE) | `qa_eol_diacritic.py` qua subprocess — `svhmp_preflight_qa.py:170-174` (gate `--skip-r86` :162; exit≠0 → append issue :176-177) | ✅ Có (doc19) |
| 2 | `render_with_character_gate.py` → `svhmp_v13_render.py` | wrapper KHÔNG tự gọi; `render_with_character_gate.py:70-72` gọi `svhmp_v13_render.py`; chính render gọi `qa_eol_diacritic.py` ở R90 STAGE1 — `svhmp_v13_render.py:311-312` (FAIL → `sys.exit(2)` :320) | ✅ Có (doc19) |
| 3 | `qa_skeptic_orchestrator.py` (**manager chính thức** của qa_runtime theo blueprint) | `vnqa/auto_fix.py` (:75-76, Phase H4) → `vnqa/pipeline.py` (:108-109) → `adversarial_skeptic.py` (:146-147). Thứ tự: AUTO_FIX→VNQA→đọc qa_output→Skeptic→final verdict (:174-201) | ❌ **KHÔNG — lỗ hổng codify nghiêm trọng nhất (D4)** |
| 4 | `qa_watch.py` + `qa_watch_supervisor.py` (daemon) | STAGE1 `qa_eol_diacritic.py` (`qa_watch.py:80-81`); STAGE3 `qa_post_render.py` (:96-97, chạy 6 section :177-178). Supervisor chỉ watchdog relaunch (`qa_watch_supervisor.py:35,128-143`, circuit-breaker 12 restart/h). **STAGE3 KHÔNG gọi** `qa_pause_silence`/`qa_boundary_artifact`/`qa_onset_artifact` — logic bị TỰ VIẾT LẠI trong `qa_post_render.py` (xem §2) | 🟡 Có nhắc daemon (doc22), không nói STAGE3 tự viết lại |
| 5 | `audio_pre_ship_gate.py` | `audio_qa_metrics.py` (:59) + `qa_concat_silence.py` R94b (:74-76) + `qa_post_render.py` 6 section (:87,92 — **lặp lại #4**) | ❌ Không nhắc trong doc19 |
| 6 | Batch legacy: `deep_200_rounds.py`, `verify_50_rounds.py`, `sequential_full_auto.py` **(+ file thứ 4 `deep_200_rounds_all_rules.py` task doc bỏ sót)** | gọi các `audit_*` qua subprocess `--summary` (chi tiết §4-legacy) | ❌ Vô hình với governance (D6) |

---

## 2. TRÙNG LẶP LOGIC ĐÃ XÁC NHẬN (đọc 2 bản, so dòng)

### 2a. Cặp PAUSE — `qa_post_render.audit_pause()` vs `qa_pause_silence.audit()` = bản sao 1-1, KHÁC 1 chỗ verdict
| Tham số | `qa_post_render.audit_pause()` | `qa_pause_silence.audit()` |
|---|---|---|
| window 20ms | `win_n=int(0.020*sr)` :15 | `:23` |
| min_pause_ms=1200 | `:13` default | `:16` |
| silence_thr −55dB | hardcode `energy_db < -55` :22 | `silence_thr_db=-55` :16 |
| pass_thr_db=−70 | `:13` | `:16` |
| margin 100ms | `:13,33` | `:48-49` |
| **verdict tolerance** | **`pass: noisy <= 1`** (R96, `:44-45`) | **`pass: noisy == 0`** (strict, `:76`) |

→ Thuật toán y hệt, chỉ lệch tiêu chí verdict. **D3 KHÔNG hợp nhất mù** — phải hỏi Mr.Long tolerance nào là ý định thật (R96 `noisy<=1` hay strict `==0`).

### 2b. Cặp BOUNDARY/ONSET — `qa_post_render` là bản THÔ, bản chính thức tinh vi hơn
- `qa_post_render.audit_boundary()` (`:65-69`): chỉ `np.diff(audio) > 0.8` đếm click, pass nếu `< 10`. **Không spectral.**
- `qa_post_render.audit_head_onset()` (`:72-106`): thuần energy-RMS 20ms, ramp −28dB/120ms. **Không spectral/F0.**
- `qa_boundary_artifact.py` (**R188 chính thức**, `"rule":"R188" :217`): STFT band-energy (:58-70), sibilance 4-8kHz, drone 40-150Hz, sub-harmonic F0 qua `librosa.yin` (:124-146).
- `qa_onset_artifact.py` (**R190b chính thức**, `:125`): F0-jump `librosa.yin` (:49-60), spectral peak ratio (:70-74).

→ **D3 giữ bản NGHIÊM NGẶT hơn (spectral) khi hợp nhất, KHÔNG hạ chuẩn về bản thô** (bài học #10/#12).

### 2c. `audit_60_dimensions` vs `audit_100_check` — comment tự thú trùng
`ha_patterns.py:3-10` tự ghi: `:7` "audit_60_dimensions.py : 4 pattern giong audit_100_check.py"; `:6` "audit_100_check.py : 4 pattern (thieu 5 so voi gate)". Single-source dày nhất = `post_render_gate.py` (9 pattern, `:5,12-13`), **KHÔNG phải** `qa_post_render.py`.

---

## 3. DOMAIN GÁN SAI (đọc field domain thật — CHỈ sửa manifest ở D2, KHÔNG sửa code)

| File | file_index.yaml | blueprint_domains.yaml | architecture_registry.yaml | Kết luận D2 |
|---|---|---|---|---|
| `qa_skeptic_orchestrator.py` | `domain: generation` (:791-794) | manager của `qa_runtime` (:613, block :607) | không mâu thuẫn ngược | **SỬA generation→qa_runtime** ✅ (2 field chính thức mâu thuẫn thật) |
| `audit_dialogue_hierarchy.py` / `audit_driver_dialogue_context.py` | `domain: text_qa` (:359-366) | dialogue chỉ import/gọi qua wrapper | `:289-295` "VAN thuoc so huu character/text_qa, KHONG chuyen ownership, can Mr.Long duyet" | **GIỮ text_qa** ⚠️ (KHÔNG đổi sang dialogue — xem sai lệch #1) |
| `qa_dialogue_identity.py` | `text_qa` (:743-746) | `validator` của `tts` (:644, block :630) | — | 2 field chính thức mâu thuẫn (text_qa/tts) + 1 tín hiệu ngữ cảnh audio (pack5/21, KHÔNG phải field domain) — báo cáo đúng bản chất, chờ Mr.Long chọn chủ sở hữu |
| `story_consistency_validator.py` | `domain: unclassified` (:915-918) | `validator` của `character` (:385) **VÀ** `event` (:476) | validators của `character` (:264); ownership `CMD_CHARACTER` (:59) | **KHÔNG gán world** ⚠️ (xem sai lệch #2 — mọi field chính thức nói character+event) |

---

## 4. BỐN SAI LỆCH THẬT so với task doc (verify độc lập tìm ra — G8 phải dừng đúng chỗ)

1. **[SAI — task doc tự mâu thuẫn]** D2 dòng 68-69 bảo đổi `audit_dialogue_hierarchy`/`audit_driver_dialogue_context` **"về G3 dialogue"** — mâu thuẫn chính dòng 42 của nó ("giữ text_qa") + governance thật (`file_index:360/364=text_qa`; `architecture_registry:293-294 "KHONG chuyen ownership"`). → **D2 phải GIỮ text_qa**, chỉ ghi chú "G3 tiêu thụ qua wrapper, không sở hữu".
2. **[SAI/đáng ngờ]** `story_consistency_validator.py` **KHÔNG có field domain "world"**. Field chính thức: character (`blueprint:385`, `arch_registry:264`) + event (`blueprint:476`); `file_index` hiện = `unclassified`. Caller `g4_world_check.py:11,31` chỉ gọi nó như **self-test**, không phải sở hữu. → Nếu D2 đổi `unclassified→world` sẽ vi phạm cảnh báo M1 ("sửa file_index domain mà không đối chiếu blueprint→FAIL"). **Cần Mr.Long/kiểm duyệt xác nhận chủ sở hữu là character (hay event) trước khi gán.**
3. **[KHÔNG chính xác — nhỏ, luồng 6]** `audit_vn_style` KHÔNG được gọi bởi 4 file batch (không thuộc lớp batch legacy này). `audit_pronoun_pov` chỉ có trong `deep_200_rounds_all_rules.py:39` — file thứ 4 task doc bỏ sót tên.
4. **[Sắc thái — luồng 2]** `render_with_character_gate.py` gọi `qa_eol_diacritic.py` **gián tiếp** qua `svhmp_v13_render.py:311-312`, không phải trực tiếp.

**Bổ sung quan trọng cho D4 (không phải sai lệch, là cảnh báo):** VNQA thật chạy **H1-H10** (`vnqa/pipeline.py:372-381`, `run_all` gọi h1..h10; method h1@166 … h10@344). NHƯNG **mọi nhãn tự-khai đều đếm thiếu**: orchestrator log "H1-H7" (`:114`), docstring pipeline "H1-H8" (`:2`), `phase_h_version` trả "H1-H7 v1.0" (`:402`), blueprint "VNQA H1-H9" (`:608`). → **D4 codify pack5/19 PHẢI dùng H1-H10 (code thật), KHÔNG chép nhãn cũ.**

---

## 5. KHỚP task doc (không sai) — để không mất công verify lại
Luồng 1/3/4/5 ✅ · cặp pause `noisy<=1` vs `==0` ✅ · boundary/onset thô vs spectral ✅ · `ha_patterns` "4 pattern giống nhau" ✅ · `qa_skeptic_orchestrator` generation-vs-qa_runtime ✅ · `qa_dialogue_identity` text_qa-vs-tts + audio-context ✅.

---

## 6. TÁC ĐỘNG LÊN D2→D7 (ghi trước, chống vừa sửa vừa quên)
- **D2** chỉ sửa AN TOÀN: `qa_skeptic_orchestrator generation→qa_runtime`. **GIỮ text_qa** cho audit_dialogue_*. **KHÔNG gán world** cho story_consistency_validator (chờ xác nhận chủ sở hữu character/event). → registry 0/0/0 sau sửa.
- **D3** chờ Mr.Long (tolerance R96) + A/B verdict golden trước/sau; hợp nhất giữ bản spectral.
- **D4** codify luồng #3 (VNQA H1-H10 + skeptic) vào pack5/19 — dùng nhãn H1-H10 code thật.
- **D6** batch legacy = 4 file (không phải 3): `deep_200_rounds`, `verify_50_rounds`, `sequential_full_auto`, `deep_200_rounds_all_rules`. Kiểm git log lần cuối dùng trước khi khai tử/đăng ký.
- **D7** gate 1 cửa mirror `g6_story_planner_check.py`, `_PYTEST_GUARD` như `ci_gate.py`.
