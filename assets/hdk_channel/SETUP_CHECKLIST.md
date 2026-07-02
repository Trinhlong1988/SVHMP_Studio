> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: _AUDIT_TENTATIVE_LOG.md.
# HDK MOTION ENGINE — Setup Checklist

**Target:** ship phương án $0 ban đầu (Inkscape + ComfyUI Wan 2.1 + Resolve Free + FFmpeg)
**Hardware:** RTX 5060 Ti SM_120, đã có FFmpeg ở `C:\Users\Administrator\ffmpeg\bin\`

---

## 1. Inkscape (logo + typography + utility masks)

### Download
- Trang chính: https://inkscape.org/release/
- Bản Windows 64-bit installer (.msi hoặc .exe)
- Version mới nhất ổn định: Inkscape 1.3.x (tự verify trên trang)

### Install
- [ ] Tải installer
- [ ] Cài mặc định `C:\Program Files\Inkscape\`
- [ ] Mở Inkscape → Edit → Preferences → System: verify
- [ ] Kiểm tra font có dấu:
  - File → New → Text tool → gõ "ơ ờ ạ ế ư ầ" 
  - Đổi font sang Cormorant Garamond (nếu chưa có → tải Google Fonts cài Windows trước)
  - Zoom 800% kiểm dấu rõ ràng

### Font cần cài Windows trước
- [ ] Cormorant Garamond: https://fonts.google.com/specimen/Cormorant+Garamond
  - Tải zip → mở → chọn TẤT CẢ file .ttf → right-click → Install for all users

### Verify
```powershell
Test-Path "C:\Program Files\Inkscape\bin\inkscape.exe"
& "C:\Program Files\Inkscape\bin\inkscape.exe" --version
```

---

## 2. DaVinci Resolve FREE (motion engine)

### Download
- Trang chính: https://www.blackmagicdesign.com/products/davinciresolve
- Click "Download" → chọn **DaVinci Resolve** (FREE, KHÔNG phải Studio)
- Yêu cầu điền form: tên + email + quốc gia (không bắt buộc thật, chỉ để Blackmagic tracking)
- Bản Windows ~3.5GB

### Install
- [ ] Tải installer
- [ ] Chạy installer, accept license
- [ ] Cài mặc định `C:\Program Files\Blackmagic Design\DaVinci Resolve\`
- [ ] Reboot khuyến nghị (Resolve hook GPU driver)

### First launch config
- [ ] Mở Resolve → New Project "HDK_Intro_Test"
- [ ] Project Settings (gear icon):
  - Timeline resolution: 3840×2160 UHD
  - Timeline frame rate: 24 fps (LOCK — không đổi sau)
  - Pixel aspect ratio: Square
  - Video format: ProRes 422 HQ (master) — nếu Free không có ProRes → DNxHR HQ
- [ ] Preferences → System → Memory and GPU:
  - GPU processing mode: CUDA (cho NVIDIA 5060 Ti)
  - GPU selection: tick 5060 Ti

### Python scripting enable
- [ ] Preferences → System → General: tick "External scripting using" → Local
- [ ] Restart Resolve
- [ ] Verify scripting:
```powershell
$env:RESOLVE_SCRIPT_API = "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
$env:RESOLVE_SCRIPT_LIB = "C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
$env:PYTHONPATH += ";$env:RESOLVE_SCRIPT_API\Modules"
python -c "import DaVinciResolveScript as dvr; resolve = dvr.scriptapp('Resolve'); print(resolve.GetProductName(), resolve.GetVersionString())"
```
Phải in: `DaVinci Resolve 19.x.x` (hoặc version mới hơn).

### Verify
```powershell
Test-Path "C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
```

---

## 3. ComfyUI + Wan 2.1 (motion asset)

### ComfyUI (đã có sẵn)
- [x] `C:\Users\Administrator\ComfyUI` đã cài
- [ ] Verify chạy được:
```powershell
cd C:\Users\Administrator\ComfyUI
.\python_embeded\python.exe -s main.py --listen 127.0.0.1 --port 8188
```
- [ ] Mở browser http://127.0.0.1:8188 → ComfyUI UI hiện

### Wan 2.1 workflow
Wan 2.1 là model video-gen mới của Alibaba (2025-2026), chạy được trên RTX 5060 Ti SM_120.

#### Tải model
- Kho official: https://huggingface.co/Wan-AI
- Variant em recommend cho 5060 Ti 16GB:
  - **Wan2.1-T2V-1.3B** (text-to-video 1.3B params, fit 5060 Ti, quality OK loop ngắn)
  - hoặc **Wan2.1-T2V-14B** quantized GGUF nếu cần quality cao hơn (slower)
- Tải về `C:\Users\Administrator\ComfyUI\models\diffusion_models\`

#### Custom node Wan 2.1
- [ ] Cài ComfyUI-Manager nếu chưa có (https://github.com/ltdrdata/ComfyUI-Manager)
- [ ] Trong ComfyUI-Manager → search "Wan" → install node Wan 2.1 (kijai/ComfyUI-WanVideoWrapper hoặc tương đương)
- [ ] Restart ComfyUI
- [ ] Tải sample workflow .json từ kho Wan node → drag vào ComfyUI canvas

#### Test render 1 sample
- [ ] Load workflow fog loop
- [ ] Prompt từ `_prompts/08_motion_fog_loop.md`
- [ ] Render 4 giây @ 24fps = 96 frames, 1920×1080
- [ ] Output `assets/hdk_channel/_render_out\test_fog_v1.mp4`
- [ ] Verify: file mở được, loop test trong VLC

#### Fallback nếu Wan 2.1 không setup được
- **AnimateDiff** (có sẵn community model cho ComfyUI từ 2023, stable)
- Custom node: ComfyUI-AnimateDiff-Evolved
- Model: AnimateDiff-Lightning hoặc V3
- Workflow tương tự, prompt giữ nguyên

### A/B test với Kling (decision gate)
- [ ] Đăng ký Kling free trial: https://klingai.com/
- [ ] Render cùng prompt fog_loop_4s
- [ ] Side-by-side trong VLC hoặc Resolve
- [ ] Mr.Long judge: nếu Wan 2.1 thua xa → mua Kling Pro $37 1 tháng → render 4 motion asset → unsubscribe

---

## 4. FFmpeg (đã có)

### Verify
```powershell
& "C:\Users\Administrator\ffmpeg\bin\ffmpeg.exe" -version
```

### Add to PATH permanent (khuyến nghị)
- [ ] System Properties → Environment Variables → Path → Add `C:\Users\Administrator\ffmpeg\bin`
- [ ] Restart terminal → `ffmpeg -version` chạy bất kỳ đâu

### NVENC verify (hardware encode)
```powershell
ffmpeg -encoders 2>&1 | Select-String "nvenc"
```
Phải thấy: `h264_nvenc`, `hevc_nvenc`.

### Loop seamless test command
```powershell
# Test fog_loop_4s.mp4 loop 3 lần liên tục, xem có cut nháy không
ffmpeg -stream_loop 3 -i fog_loop_4s.mp4 -c copy fog_loop_x3_test.mp4
# Mở fog_loop_x3_test.mp4 trong VLC → quan sát boundary loop
```

---

## 5. Cloud backup (Mega 50GB free)

### Setup
- [ ] Trang: https://mega.io/
- [ ] Đăng ký tài khoản free 50GB (anh có thể dùng email phụ)
- [ ] Tải MEGAsync desktop app
- [ ] Cài → login → tạo folder `MEGA\HDK_Master`
- [ ] Cấu hình sync `assets/hdk_channel/brand\` ↔ `MEGA\HDK_Master\hdk_brand\`
  - Chỉ sync hdk_brand (master locked) — KHÔNG sync `_render_out\` (large temp files)

### Alternative
- Google Drive 15GB free (đã có với Gmail account)
- OneDrive 5GB free
- HDD external manual weekly

---

## 6. Install order (recommend)

1. **Inkscape** (5 phút) — tạo logo + typography trước, cần cho intro
2. **ComfyUI Wan 2.1** (1-2 giờ tải model + setup custom node) — render motion asset
3. **DaVinci Resolve Free** (30 phút tải + cài + first launch config) — motion engine
4. **Mega backup** (10 phút) — không gấp, sau khi có master asset
5. **FFmpeg PATH** (2 phút) — đã có, chỉ add PATH

---

## 7. Verify all installed

```powershell
# Run after all installs
$checks = @{
  "FFmpeg" = "C:\Users\Administrator\ffmpeg\bin\ffmpeg.exe"
  "Inkscape" = "C:\Program Files\Inkscape\bin\inkscape.exe"
  "DaVinci Resolve" = "C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
  "ComfyUI" = "C:\Users\Administrator\ComfyUI\main.py"
}
foreach ($k in $checks.Keys) {
  if (Test-Path $checks[$k]) { Write-Output "OK  : $k" } 
  else { Write-Output "MISS: $k -> $($checks[$k])" }
}
```

Khi tất cả OK → em begin render asset.

---

## 8. Cost recap

| Item | Cost | Note |
|---|---|---|
| Inkscape | $0 | open source |
| Resolve Free | $0 | upgrade Studio $295 nếu cần |
| ComfyUI + Wan 2.1 | $0 | local |
| FFmpeg | $0 | đã có |
| Mega backup | $0 | 50GB free |
| Kling A/B test | $0 | free trial |
| **Phase 1 TOTAL** | **$0** | |
| Worst-case 24mo nếu hit limit | **$402** | Affinity $70 + Kling $37 + Resolve Studio $295 |
