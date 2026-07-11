# DEBT-018 / R197 FULL_TEXT_GATE — Báo cáo Giai đoạn 1 (LOG-ONLY)

> Thực thi 11/7/2026, CMD_BUILD, per Mr.Long authorization (PING_CMD_LEAD_29_06.md 00:57).
> Giai đoạn 1 CHỈ ghi log, KHÔNG chặn render. Báo cáo này KHÔNG kèm quyết định — chờ
> Mr.Long xem xong quyết Giai đoạn 2 (chặn thật) theo đúng yêu cầu DEBT-018.

## 1. Tóm tắt (executive summary)

- **50/50 tập hiện có SẼ bị CHẶN render nếu bật Giai đoạn 2 (chặn thật) ngay bây giờ.**
- **49/50 tập có vi phạm R86 EOL diacritic THẬT** (đọc trực tiếp `episode.md`, tin cậy
  cao) — chỉ **EP01 (golden/locked) sạch R86** (0 vi phạm).
- **Ngay cả EP01 (golden/locked, tham chiếu chính thức) cũng KHÔNG sạch 100%** theo bộ
  rule đầy đủ của `svhmp_preflight_qa.py` — 22 issue khác R86 (R1 short-fragment ×13,
  R5 thiếu ending phrase ×1, R10 scene-switch-no-transition ×5, R17 lặp phrase ×1) khi
  chạy trên **spec.json THẬT** (sản phẩm pipeline TTS thật, không phải dữ liệu giả lập).
- **1 bug kỹ thuật được phát hiện + sửa trong lúc wire:** `svhmp_preflight_qa.py`
  resolve sai đường dẫn `episode.md` khi nhận spec.json sản xuất thật (1 cấp thư mục,
  vd `output/ep_01/spec.json`) — khiến R86 broad **âm thầm bị SKIP** (chính là 1/2
  "bypass" DEBT-018 đã ghi nhận trước đó: "missing-md skip"). Đã fix + test mutation-proof
  (xem mục 4).

## 2. Phương pháp + giới hạn dữ liệu (ĐỌC KỸ trước khi diễn giải số liệu)

Chỉ **EP01** có `spec.json` THẬT (sản phẩm thật của pipeline TTS, `svhmp_v13_render.py
--spec output/ep_01/spec.json`). **49/50 tập còn lại (EP02-EP50) CHƯA từng qua render
TTS** nên KHÔNG có `spec.json`. Để vẫn xem trước (preview) được, script batch
(`scratchpad/debt018_batch_preflight.py`, one-time diagnostic — không phải gate
thường trực) tự dựng `spec.json` XẤP XỈ từ `episode.md` (tách câu bằng dấu `.!?…`,
bỏ header/annotation/code block — mirror cách `qa_eol_diacritic.py` đọc file).

**Độ tin cậy khác nhau theo loại rule:**

| Rule | Nguồn dữ liệu | Độ tin cậy |
|---|---|---|
| **R86 EOL diacritic** (qua `qa_eol_diacritic.py`) | Đọc TRỰC TIẾP `episode.md` (không qua spec.json tự dựng) | **Cao** — không phụ thuộc cách tách câu |
| R1 (short fragment), R5 (ending phrase), R10 (scene switch), R17 (lặp phrase), character gate | Đọc qua `sentences[].text` của spec.json (thật cho EP01, tự dựng xấp xỉ cho EP02-50) | **Cao cho EP01** (spec thật) — **THẤP cho EP02-50** (nhiễu do tách câu thô: dấu ngoặc kép đứng riêng bị đếm thành "câu 1 từ", bullet checklist ("- ✅ ALWAYS") lẫn vào bị đếm nhầm thành câu văn) |

→ **Số liệu R86 (mục 3) là bằng chứng đáng tin cậy nhất trong báo cáo này.** Số liệu R1/
R5/R10/R17 cho EP02-50 (mục 5) chỉ mang tính **xu hướng/tham khảo**, KHÔNG dùng làm căn
cứ quyết định — muốn số liệu chính xác cho các rule này cần spec.json THẬT (tức phải
render TTS thật trước, ngoài phạm vi Giai đoạn 1 LOG-ONLY).

## 3. R86 EOL diacritic — số liệu tin cậy (49/50 tập có vi phạm)

| Tập | R86 violations | Tập | R86 | Tập | R86 | Tập | R86 | Tập | R86 |
|---|---|---|---|---|---|---|---|---|---|
| ep_01 | **0** (golden) | ep_11 | 35 | ep_21 | 45 | ep_31 | 34 | ep_41 | 40 |
| ep_02 | 44 | ep_12 | 36 | ep_22 | 35 | ep_32 | 25 | ep_42 | 38 |
| ep_03 | 47 | ep_13 | 31 | ep_23 | 34 | ep_33 | 33 | ep_43 | 31 |
| ep_04 | 42 | ep_14 | 31 | ep_24 | 36 | ep_34 | 29 | ep_44 | 31 |
| ep_05 | 47 | ep_15 | 28 | ep_25 | 38 | ep_35 | 41 | ep_45 | 33 |
| ep_06 | 52 | ep_16 | 38 | ep_26 | 32 | ep_36 | 39 | ep_46 | 37 |
| ep_07 | 53 | ep_17 | 39 | ep_27 | 43 | ep_37 | 44 | ep_47 | 37 |
| ep_08 | 43 | ep_18 | 39 | ep_28 | 29 | ep_38 | 38 | ep_48 | 28 |
| ep_09 | 36 | ep_19 | 45 | ep_29 | 41 | ep_39 | 29 | ep_49 | 38 |
| ep_10 | 37 | ep_20 | 42 | ep_30 | 43 | ep_40 | 39 | ep_50 | 48 |

**Trung bình EP02-50: ~38 vi phạm R86/tập** (min 25 ep_32, max 53 ep_07). EP01 là **duy
nhất** sạch — phù hợp giả thuyết EP01 (golden/locked) đã qua tay soát riêng trước khi
khoá, còn EP02-50 chưa qua đợt soát R86 tương tự.

## 4. Bug đã phát hiện + sửa: `md_path` resolution trong `svhmp_preflight_qa.py`

**Trước fix:** `spec_path.parents[1] / 'episode.md'` giả định spec.json luôn lồng 2 cấp
dưới thư mục tập (đúng cho spec cũ dạng `output/ep_01/sections/spec_hook.json`, `parents[1]`
= `output/ep_01`) — nhưng spec.json SẢN XUẤT THẬT của `svhmp_v13_render.py`
(`output/ep_01/spec.json`) chỉ lồng 1 cấp, `parents[1]` = `output` (SAI) → `episode.md`
không resolve được → nhánh `WARN: episode.md not found, skip R86 broad` được chọn ÂM THẦM.

**Đã tự verify bằng chạy thật:** `python tools/svhmp_preflight_qa.py output/ep_01/spec.json`
trước fix in ra `[FULL_TEXT_GATE] WARN: episode.md not found at output\episode.md, skip
R86 broad`; sau fix in ra `[FULL_TEXT_GATE] R86 broad EOL check via qa_eol_diacritic.py`
đúng như kỳ vọng.

**Fix:** thử nhiều vị trí ứng viên theo thứ tự ưu tiên (`spec_path.parent`, rồi
`spec_path.parents[1]` nếu có, cuối cùng fallback `REPO/output/ep_NN/episode.md` — luôn
đúng bất kể spec.json đặt ở đâu). Không phá hành vi cũ (spec lồng 2 cấp vẫn resolve đúng
như trước — có test regression riêng).

## 5. Wiring vào `svhmp_v13_render.py` (LOG-ONLY, không chặn)

Thêm block `[R197-LOG-ONLY]` ngay sau R90 STAGE 1 (gate THẬT, vẫn giữ nguyên hành vi chặn
cũ, không đổi) — gọi `svhmp_preflight_qa.py args.spec` qua subprocess, in kết quả ra log,
**KHÔNG** `sys.exit` bất kể exit code. Mirror đúng pattern R90 STAGE 1 đã có sẵn trong
CHÍNH file này (subprocess QA call in-line) — KHÔNG tái phạm lỗi cũ (commit 8dbcecc chèn
CHARACTER_GATE logic trực tiếp vào file LOCKED, đã bị `test_gate_wired_g2.py` chặn lại;
đoạn LOG-ONLY này không đụng đến character-gate/flag mới nào, đã tự chạy lại guard đó
xác nhận PASS).

## 6. Danh sách issue mẫu (EP01, spec.json THẬT)

```
R17 ch9: LẶP PHRASE "một chuyến xe" 2x trong chunk
R1 ch33/111/112/122/123/127/137/145/153/154/190/213/227/265: SHORT fragment (1-3 từ)
R5 ch266 LAST: thiếu ending phrase
R10 ch170→171, 223→224, 237→238, 238→239, 239→240: SCENE SWITCH không transition
```

## 7. Việc CHƯA làm (đúng phạm vi Giai đoạn 1, chờ Mr.Long)

- **KHÔNG** bật chặn thật (Giai đoạn 2) — `--skip-r86` vẫn còn, R197 vẫn chỉ LOG-ONLY.
- **KHÔNG** tự quyết hướng xử 49 tập cũ (waiver hay regen) — theo đúng DEBT-018 yêu cầu.
- **KHÔNG** sửa (1a)/(1b)/(1c) audio docstring (`svhmp_audio_qa.py`/R199 guard/"LOCKED
  v1.3" claim) — theo DEBT-018 "sau khi giai đoạn 2 xong, tránh sửa 2 lần nếu giai đoạn 1
  đổi hướng".
- **KHÔNG** wire các script phụ trợ khác (`render_chunk.py`, `render_section.py` — công cụ
  dev-workflow per-chunk/per-section, KHÔNG phải entrypoint chính thức theo
  `governance/blueprint/bp8/render_chain.yaml` stage `tts` — chỉ khai `tools/
  svhmp_v13_render.py`). Nếu Mr.Long muốn phủ cả 2 script này ở Giai đoạn 2, cần quyết
  định riêng (ngoài phạm vi entrypoint chính DEBT-018 đã nêu).

## 8. Bằng chứng chạy thật

- `scratchpad/debt018_batch_preflight.py` — script batch (one-time, không đăng ký gate).
- `scratchpad/debt018_batch_preflight_results.json` — raw kết quả 50 tập.
- `tests/test_preflight_repo_path.py` — 2 test mới (real production spec resolve đúng +
  regression spec cũ vẫn đúng).
- `tests/test_debt018_r197_log_only.py` — 6 test mới (static + mutation-proof cho block
  LOG-ONLY: không sys.exit, gọi đúng preflight+args.spec, không tái phạm CHARACTER_GATE).
- `python -m pytest tests/ -q` — full suite xanh sau khi sửa (xem log_ping).
