# G8-D3 — Phân tích dedupe `qa_post_render` (BẰNG CHỨNG trước khi sửa)

**Session:** CMD_BUILD_2 (G8 qa_runtime) · **Ngày:** 2026-07-09
**Quyết định nền:** Mr.Long 9/7 (commit `717342a`) — dùng `noisy<=1` làm chuẩn hợp nhất (R96 v3.3, `bible/00` dòng 1671); `qa_pause_silence.py` (đang `noisy==0`) là bản lỗi thời cần cập nhật; **vẫn bắt buộc A/B golden set trước khi merge**.

> **KẾT LUẬN NGẮN:** Trong 3 cặp task doc gọi là "trùng", **chỉ 1 cặp trùng thật** (pause). 2 cặp còn lại (boundary, onset) là **rule khác nhau, đo đại lượng khác nhau** — "dedupe" chúng = xoá check đang chạy + đổi hành vi gate, KHÔNG phải khử trùng. Ngoài ra **cả 4 file thuộc domain `audio_qa` owner CMD_AUDIO**, không phải qa_runtime của CMD_BUILD_2 → R211 chặn tôi tự sửa. → **DỪNG, xin Mr.Long xác nhận phạm vi đã hiệu chỉnh + phối hợp CMD_AUDIO.**

## 1. Cặp PAUSE — trùng THẬT (dedupe hợp lệ)

| | `qa_post_render.py::audit_pause` (dòng 13-45) | `qa_pause_silence.py::audit` (dòng 16-77) |
|---|---|---|
| Thuật toán | 20ms window → energy_db → silence<-55 → pause≥1200ms → margin 100ms → peak check | **Y HỆT** |
| Input | `(audio, sr)` tiền nạp | `wav_path` (tự đọc file) |
| Hạng | clean(<-70) / noisy(≥-55); dải giữa không đếm | clean(<-70) / **ok(-70..-55)** / noisy(≥-55) + chi tiết từng pause (richer) |
| Ngưỡng pass | `noisy <= 1` (R96 v3.3 — ĐÚNG bible hiện hành) | `noisy == 0` (lỗi thời) |
| Caller | **live**: `audio_pre_ship_gate.py`, `audio_qa_report.py`, `episode_state.py`, `qa_watch.py` | **0 caller .py** (standalone) |

**Dedupe khả thi:** tách core `audit_array(audio, sr)` ngưỡng `noisy<=1` trong `qa_pause_silence` (bản richer, giữ), cho `qa_post_render.audit_pause` gọi lại. A/B trên 87 wav golden `output/ep_*` đo số case đổi verdict. Đây đúng phạm vi Mr.Long duyệt.

## 2. Cặp BOUNDARY — KHÔNG trùng (rule khác)

| `qa_post_render.py::audit_boundary` (dòng 65-69) | `qa_boundary_artifact.py` (R188, Mr.Long 5★) |
|---|---|
| `np.diff(audio) > 0.8` → đếm click; pass `<10` | Phổ ±200ms quanh boundary: sibilance 4-8kHz ("xì"), drone 40-150Hz ("ù"), subharmonic F0 std/mean ("ẹ") |
| Time-domain thuần, không librosa, không cần timestamp | Cần `librosa` + boundary từ `concat_silence.json` |
| Bắt: click/pop nối chunk | Bắt: R188 artifact phổ tại seam |

→ Hai detector **bổ sung**, không thay thế. Thay `audit_boundary` bằng `qa_boundary_artifact` = **bỏ check click + thêm phụ thuộc librosa vào live gate** = đổi hành vi, giảm phủ time-domain.

## 3. Cặp ONSET — KHÔNG trùng (rule khác)

| `qa_post_render.py::audit_head_onset` (dòng 72-106, R88) | `qa_onset_artifact.py` (R190b) |
|---|---|
| Energy đạt -28dB trong 120ms sau pause; pass ratio slow_onset `<=0.25` | F0 jump ratio >1.5 + spectral peak spike >2.0 tại onset 100ms |
| Đo: tốc độ lên tiếng (ramp) | Đo: nhảy cao độ / gai biên độ |

→ Khác đại lượng hoàn toàn. Không phải dup.

## 4. Chặn quyền sửa (R211)

`governance/manifests/audio_qa_manifest.yaml`: cả `qa_post_render.py`, `qa_pause_silence.py`, `qa_boundary_artifact.py`, `qa_onset_artifact.py` thuộc **domain `audio_qa`, owner `CMD_AUDIO`, tier 3**. CMD_BUILD_2 domain = qa_runtime. Sửa file cross-domain phải qua owner (R211 file↔domain↔quyền sửa).

## 5. Khuyến nghị

1. **PAUSE:** dedupe + ngưỡng `noisy<=1` — ĐÚNG như Mr.Long duyệt. Sẵn sàng thực thi + chạy A/B 87 wav ngay khi (a) Mr.Long xác nhận và (b) phối hợp/uỷ quyền CMD_AUDIO (domain owner).
2. **BOUNDARY + ONSET:** **KHÔNG dedupe** — giữ cả 2 lớp (crude time-domain trong live gate + spectral R188/R190b). Nếu muốn tăng phủ: đề xuất WIRE thêm R188/R190b như gate phụ (task riêng của CMD_AUDIO), không thay thế.
3. Task doc D3 gọi cả 3 là "trùng" là **lỗi tiền đề** (chỉ pause trùng) — ghi nhận theo R_SUPREME test_process_failure: cập nhật mô tả D3 trong TASK_G8 để lần sau không ai dedupe nhầm 2 rule khác nhau.

**Chờ:** Mr.Long xác nhận phạm vi (chỉ pause) + cơ chế phối hợp CMD_AUDIO trước khi tôi chạm code audio_qa.
