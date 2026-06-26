> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: _AUDIT_TENTATIVE_LOG.md.
# DaVinci Resolve Free — Download Guide (Mr.Long thao tác)

**Lý do em không tự cài được:**
Blackmagic Design **bắt buộc** submit form (name + email + country) trước khi cho URL download Resolve installer. Form chạy JavaScript validate + redirect tracking — không có direct download URL stable để em bypass. Đây là policy Blackmagic, không phải limitation tool.

**Thời gian cần:** ~3 phút submit form + ~30 phút tải (3.5GB) + ~10 phút install.

---

## Step 1 — Whitelist DNS (nếu Pi-hole/AdGuard đang block)

Trước khi vào web Blackmagic, anh check DNS có block không:
```powershell
Resolve-DnsName www.blackmagicdesign.com -Type A
```
- Nếu IP trả về **127.0.0.1** hoặc **0.0.0.0** → bị block, anh whitelist domain `blackmagicdesign.com` (wildcard) trên Pi-hole/router
- Nếu IP công cộng (vd 23.x.x.x, 104.x.x.x) → OK, đi tiếp

---

## Step 2 — Vào trang download

URL chính thức:
```
https://www.blackmagicdesign.com/products/davinciresolve
```

Trên trang:
1. Cuộn xuống đến section "Download" (gần cuối trang)
2. Có 2 cột: **DaVinci Resolve 19** (FREE) và **DaVinci Resolve Studio 19** (PAID)
3. Click nút **"Download"** cột **TRÁI** (Resolve FREE, KHÔNG phải Studio)
4. Popup hiện: chọn OS = **"Windows"** → click download icon

---

## Step 3 — Form submit (BẮT BUỘC)

Popup form xuất hiện với fields:

| Field | Anh điền |
|---|---|
| First Name | Long (hoặc tên bất kỳ) |
| Last Name | Nguyen (hoặc họ bất kỳ) |
| Email | ecoglobalcpn@gmail.com (hoặc email phụ) |
| Phone Number | (có thể để trống hoặc nhập 0xxx) |
| Country | Vietnam |
| State / City | Hanoi (hoặc tỉnh anh) |
| Product Use | "I am a hobbyist / personal use" (option đầu) |

→ Click **"Register & Download"**.

**Lưu ý:** Blackmagic KHÔNG verify email. Anh có thể dùng email tạm hoặc email phụ. Không có spam follow-up.

---

## Step 4 — Tải file

Sau khi submit form, browser tự download:
- File: `DaVinci_Resolve_19.x.x_Windows.zip` (~3.5 GB)
- Folder mặc định: `C:\Users\Administrator\Downloads\`
- Tốc độ: 5-15 phút tùy mạng

---

## Step 5 — Giải nén + cài

```powershell
# Giải nén
$zip = Get-ChildItem "$env:USERPROFILE\Downloads\DaVinci_Resolve*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Expand-Archive -Path $zip.FullName -DestinationPath "$env:USERPROFILE\Downloads\Resolve_installer\" -Force

# Tìm installer .exe
Get-ChildItem "$env:USERPROFILE\Downloads\Resolve_installer\" -Filter "*.exe"

# Chạy installer (admin elevation sẽ popup)
Start-Process -FilePath "$env:USERPROFILE\Downloads\Resolve_installer\DaVinci_Resolve_*.exe" -Verb RunAs
```

Trong installer wizard:
1. Accept EULA
2. **Default install path** `C:\Program Files\Blackmagic Design\DaVinci Resolve\` — giữ nguyên
3. **Component selection** — tick tất cả (Resolve + Fairlight Studio Util + Decklink driver)
4. Click Install → đợi 5-8 phút
5. Reboot recommended (Resolve hook GPU driver)

---

## Step 6 — First launch config

Mở **DaVinci Resolve** từ Start Menu:

1. **Welcome popup** — Click "Continue" (skip tutorial)
2. **Quick Setup**:
   - Skip hoặc chọn defaults
3. **Project Manager** hiện → click "New Project" → tên: `HDK_Intro_Test`
4. **Project Settings** (gear icon góc dưới phải):
   - Master Settings:
     - Timeline resolution: **3840 x 2160 Ultra HD**
     - Timeline frame rate: **24 fps** (LOCK — không đổi sau)
     - Playback frame rate: 24 fps
     - Video bit depth: 10-bit
     - Video format: H.264 (NVENC) cho delivery
   - Image Scaling: Lanczos (sharp scaling cho still images)
5. **DaVinci Resolve > Preferences** menu top:
   - **System > Memory and GPU**:
     - GPU processing mode: **CUDA**
     - GPU selection: tick RTX 5060 Ti
   - **System > General**:
     - External scripting using: **Local**
   - Apply, restart Resolve.

---

## Step 7 — Verify Python scripting (em dùng cho automation)

Sau khi Resolve cài + restart, mở PowerShell:

```powershell
$env:RESOLVE_SCRIPT_API = "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
$env:RESOLVE_SCRIPT_LIB = "C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
$env:PYTHONPATH = "$env:PYTHONPATH;$env:RESOLVE_SCRIPT_API\Modules"

python -c "import DaVinciResolveScript as dvr; r = dvr.scriptapp('Resolve'); print(r.GetProductName(), r.GetVersionString())"
```

**Expected output:**
```
DaVinci Resolve 19.x.x
```

Nếu error `import DaVinciResolveScript` fail → check Resolve đang chạy (Python API chỉ work khi Resolve mở).

---

## Step 8 — Báo em xong

Khi tới đây, anh nhắn em "Resolve cài xong" → em verify bằng:
```powershell
Test-Path "C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
```

→ Em sẽ begin build Resolve project intro master 4.5s theo storyboard LOCK.

---

## Troubleshooting

| Lỗi | Fix |
|---|---|
| Form submit fail | Check anh tick "I agree to receive email" (mandatory) |
| Download chậm | Blackmagic CDN US/EU, anh thử lại sau hoặc dùng VPN |
| Installer "Need .NET Framework" | Download Microsoft .NET 4.8 Runtime, cài trước Resolve |
| "Error: Decklink driver fail" | Bỏ tick Decklink component khi install (anh không dùng card capture) |
| Resolve mở → crash launch | Update NVIDIA driver Studio Driver mới nhất (KHÔNG Game Ready), reboot |
| Python `DaVinciResolveScript` không import | Resolve phải đang mở, env vars set đúng path |

---

## Note Studio vs Free

| Feature | Free | Studio $295 |
|---|---|---|
| Resolution | UHD 4K | 8K+ |
| GPU | 1 GPU | Multi-GPU |
| ProRes encode | ❌ | ✓ |
| Neural noise reduction | ❌ | ✓ |
| Fairlight FairlightFX | ❌ | ✓ |
| Fusion built-in nodes | ✓ (đủ cho intro 4.5s) | ✓ |
| Python scripting API | ✓ | ✓ |

→ **Free đủ 100% cho intro 4.5s + main scene ep**. Studio chỉ cần nếu sau này anh ship 8K hoặc cần neural noise reduction.
