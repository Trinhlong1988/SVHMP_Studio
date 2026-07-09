# G8-D3 — TURNKEY PACKAGE cho CMD_AUDIO: dedup PAUSE + A/B evidence

**Chuẩn bị bởi:** CMD_BUILD_2 (per Mr.Long approve 9/7, ping `20:10`) · **Ngày:** 2026-07-09
**Trạng thái:** ĐỀ XUẤT (văn bản) — CMD_BUILD_2 **KHÔNG** thực thi code trong domain `audio_qa`.
CMD_AUDIO (owner) chạy khi rảnh; mọi thứ đã sẵn sàng turnkey.

> **PHẠM VI (QUYẾT ĐỊNH CUỐI Mr.Long, TASK_G8 D3):** CHỈ dedup **PAUSE** (`audit_pause` ↔
> `qa_pause_silence`). **KHÔNG đụng** `audit_boundary`↔`qa_boundary_artifact` (R188 phổ) và
> `audit_head_onset`↔`qa_onset_artifact` (R190b F0) — đã xác minh là **rule khác, không trùng**
> (xem `reports/G8_D3_DEDUPE_ANALYSIS.md`). Ngưỡng hợp nhất = **`noisy<=1`** (R96 v3.3, bible/00:1671).

---

## 1. BẰNG CHỨNG A/B (bắt buộc trước merge — đã chạy sẵn)

Script: `tools/qa_pause_ab_probe.py` (subprocess gọi `qa_pause_silence.py`, KHÔNG sửa/không import
file audio_qa). Chạy lại: `python tools/qa_pause_ab_probe.py --json runtime/d3_pause_ab.json`.

Kết quả trên **87 wav golden** (`output/**/*.wav`), 0 lỗi:

| Ngưỡng | PASS | Ý nghĩa |
|---|---|---|
| CŨ `noisy==0` (qa_pause_silence hiện tại) | 38/87 | bản lỗi thời, quá nghiêm |
| MỚI `noisy<=1` (đã duyệt = audit_pause) | 61/87 | R96 v3.3 |

- **23 wav ĐỔI verdict** (FAIL→PASS) — **tất cả đều `noisy==1`** (đúng 1 noisy pause): rare BigVGAN
  artifact mà R96 v3.3 chấp nhận. Không phải bug — là ý định thật của việc nới ngưỡng.
- **0 wav PASS→FAIL**: `noisy<=1` lỏng hơn `noisy==0` nên đổi verdict **1 chiều** (chỉ nới). An toàn:
  dedup không làm nội dung đã PASS trước đó bị FAIL.
- Danh sách 23 wav flip: xem stdout probe (chủ yếu EP01 VOICE v84-v200 + sections incident/payoff).

> Sau khi CMD_AUDIO dedup xong (qa_pause_silence chuyển `noisy<=1`), chạy lại probe: cột old==new,
> 0 flip — xác nhận 2 impl đã hội tụ cùng verdict.

## 2. PATCH PLAN (đề xuất — CMD_AUDIO thực thi trong domain audio_qa)

### 2a. `tools/qa_pause_silence.py` — tách core + đổi ngưỡng
- Tách phần detect từ mảng ra hàm mới `audit_array(audio, sr, min_pause_ms=1200, silence_thr_db=-55, pass_thr_db=-70)`:
  giữ NGUYÊN logic 20ms-window + margin 100ms + 3 hạng CLEAN/OK/NOISY hiện có.
- `audit(wav_path, ...)` thành wrapper mỏng: `audio, sr = sf.read(wav_path)` (+ mono) → gọi `audit_array`.
- **Đổi 1 dòng ngưỡng:** `"pass": noisy == 0` → `"pass": noisy <= 1` (R96 v3.3). Thêm comment trỏ
  bible/00:1671 + `qa_post_render.audit_pause` (nguồn ngưỡng chuẩn).
- GIỮ NGUYÊN output keys (`pauses_detected/clean/ok/noisy/results/pass`) — là bản richer, làm canonical.

### 2b. `tools/qa_post_render.py` — `audit_pause` GỌI LẠI core (diệt trùng)
- `import qa_pause_silence` (cùng thư mục tools/).
- `audit_pause(audio, sr, ...)` → `r = qa_pause_silence.audit_array(audio, sr, ...)` rồi map keys
  về đúng cấu trúc downstream đang dùng: `{"total": r["pauses_detected"], "clean": r["clean"],
  "noisy": r["noisy"], "pass": r["pass"]}`. XÓA phần reimplement thô (dòng 15-45 hiện tại).
- Downstream `main()` (`p["total"]/p["clean"]/p["noisy"]/p["pass"]`) không đổi.

### 2c. KHÔNG đụng
- `audit_boundary` / `audit_head_onset` (qa_post_render) — giữ nguyên (rule khác R188/R190b).
- `qa_boundary_artifact.py` / `qa_onset_artifact.py` — không sửa.
- `svhmp_v13_render.py` (LOCKED) — tuyệt đối không đụng.

## 3. INVARIANT SAU DEDUP (CMD_AUDIO verify)
1. `python tools/qa_pause_ab_probe.py` → old==new mọi wav, **0 flip** (2 impl hội tụ noisy<=1).
2. Chỉ còn **1** nơi implement thuật toán pause (qa_pause_silence.audit_array); qa_post_render.audit_pause
   chỉ delegate (grep xác nhận không còn vòng lặp energy_db thứ 2).
3. Ngưỡng `noisy<=1` ở đúng 1 chỗ (audit_array). Không còn `noisy == 0` trong qa_pause_silence.
4. Chạy test audio hiện có + `qa_watch.py`/`audio_pre_ship_gate.py` smoke: verdict EP01 không tệ đi
   (23 wav noisy==1 giờ PASS đúng như A/B dự báo).
5. `architecture_registry_check.py` 0/0/0.

## 4. HANDOFF
- File MỚI thuộc CMD_BUILD_2 (domain qa_runtime), KHÔNG phải audio_qa: `tools/qa_pause_ab_probe.py`
  (A/B harness) + báo cáo này. CMD_AUDIO **không cần sửa** 2 file này.
- 2 file cần patch (2a/2b) thuộc **CMD_AUDIO** — chỉ CMD_AUDIO thực thi (R211 domain ownership).
- Sau merge: cập nhật `governance/pack5/19_qa_pipeline.md` (nếu cần) ghi qa_post_render.audit_pause
  nay delegate; đóng D3 trong TASK_G8 + ping.
