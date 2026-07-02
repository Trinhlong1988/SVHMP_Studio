# HDK Channel — Asset & Pipeline Workspace

**Path:** `SVHMP_Studio/assets/hdk_channel/`
**Channel:** Hắc Dạ Ký (@hacdaky)
**Tagline:** "Chuyện kể từ cõi vô hình"
**Lock date:** 2026-06-26

---

## ✅ APPROVED Mr.Long 2026-06-26 — T1-T8 LOCKED

Toàn bộ 60+ items thuộc cluster T1-T8 (motion values bible/19, audio LUFS V9, layer stack V8, 13 SDXL/Wan/Inkscape prompts, storyboard frame breakdown, bible/04 channel_brand_assets, naming convention, cost projection) đã được **Mr.Long approve** ngày 2026-06-26.

**Audit trail historical:** [`_AUDIT_TENTATIVE_LOG.md`](_AUDIT_TENTATIVE_LOG.md) (giữ làm record, KHÔNG xóa)

**Rule cứng cho TƯƠNG LAI:** Memory `feedback_cam_suy_luan.md` — mọi content MỚI viết sau 26/6 vẫn phải mark TENTATIVE nếu suy luận, KHÔNG tự adopt.

**Render asset:** UNBLOCKED. Có thể start sau khi cài tool xong (Inkscape + Resolve + ComfyUI Wan 2.1).

---

## Architecture (hợp nhất 26/6 — Mr.Long chốt Option 1)

Workspace nằm trong hiến pháp SVHMP_Studio, KHÔNG tách riêng. Reference đầy đủ:

| Spec | File | Status |
|---|---|---|
| Hiến pháp series | [`../../bible/00_constitution.yaml`](../../bible/00_constitution.yaml) | FROZEN |
| Ep body pipeline | [`../../prompts/video.md`](../../prompts/video.md) (V1-V6) | LOCKED v1.0 |
| **Channel intro pipeline** | [`../../prompts/video_intro.md`](../../prompts/video_intro.md) (V7-V9) | **TENTATIVE T2/T3** |
| Asset registry | [`../../bible/04_asset_bible.yaml`](../../bible/04_asset_bible.yaml) (v1.1 extend channel_brand_assets) | **TENTATIVE T6** |
| Audio brand | [`../../bible/10_brand_audio.yaml`](../../bible/10_brand_audio.yaml) | LOCKED v1.0 |
| **Motion rules** | [`../../bible/19_motion_bible.yaml`](../../bible/19_motion_bible.yaml) | **TENTATIVE T1** |
| Intro constitution gốc | Docx Mr.Long 2026-06-25 23:56 (memory `project_svhmp_youtube_channel.md`) | LOCKED 4 segment + hard cut |

---

## Folder structure

```
assets/hdk_channel/
├── README.md                          (this file)
├── _AUDIT_TENTATIVE_LOG.md            (master log mọi chỗ Claude suy luận)
├── SETUP_CHECKLIST.md                 (install Inkscape + Resolve + ComfyUI Wan 2.1)
├── RESOLVE_DOWNLOAD_GUIDE.md          (Mr.Long submit form Blackmagic step-by-step)
├── brand/
│   ├── logo/                          (hdk_logo.svg + png export)
│   ├── typography/                    (2 tagline SVG)
│   └── intro_master/                  (HDK_INTRO_4500ms_LOCKED_v01.mov sau render)
├── shared/
│   ├── still/                         (5 SDXL still: moon, railway, storyteller, lantern, smoke)
│   ├── motion/                        (4 Wan 2.1 loop: fog, flame, smoke_fx, dust)
│   └── utility/                       (2 custom: glow_plate, transition_mask)
├── chuyenxe/
│   └── ep01/                          (per-ep assets, không share)
├── _prompts/                          (13 prompt files: 01_brand_logo ... 13_utility_transition_mask)
├── _storyboard/
│   └── intro_master_4500ms.md         (storyboard 4 segment + hard cut)
├── _pipeline_scripts/                 (Python DaVinciResolveScript, FFmpeg concat scripts — TBD)
└── _render_out/                       (per-segment .mov masters trước concat)
```

---

## Tool stack (Mr.Long chốt phương án $0 26/6)

| Layer | Tool | Cost ban đầu | Status setup |
|---|---|---|---|
| Logo + Typography | Inkscape (free) | $0 | ⏸ chưa cài (DNS block inkscape.org — Mr.Long whitelist) |
| 5 still | SDXL local ComfyUI | $0 | ✓ ComfyUI đã có |
| 4 motion | Wan 2.1 local ComfyUI | $0 | ⏸ chưa setup workflow |
| Motion engine | DaVinci Resolve Free | $0 | ⏸ Mr.Long submit form |
| Composite | FFmpeg | $0 | ✓ đã có `C:\Users\Administrator\ffmpeg\bin\` |
| Backup | Mega 50GB free + HDD local | $0 | ⏸ chưa setup |

**Worst case 24mo upgrade scenario:** xem `_AUDIT_TENTATIVE_LOG.md` T8 (TENTATIVE projection).

---

## Workflow per ep (sau khi render xong intro master)

```
ep_NN.script (Mr.Long)
    ↓
ep_NN/narration.wav (SVHMP TTS pipeline IndexTTS2+RVC NNG — đã có)
    ↓
Video Director ep body (prompts/video.md V1-V6) → ep_NN_body.mp4
    ↓
FFmpeg concat: HDK_INTRO_4500ms_LOCKED_v01.mov + ep_NN_body.mp4 → ep_NN_final.mp4
    ↓
SHA256 verify intro first 4500ms byte-identical
    ↓
Upload @hacdaky
```

---

## Next steps (theo thứ tự)

1. **Mr.Long whitelist DNS** trên router 192.168.1.1: `inkscape.org` + `media.inkscape.org` + `blackmagicdesign.com`
2. **Mr.Long approve / reject** từng cluster TENTATIVE trong `_AUDIT_TENTATIVE_LOG.md`:
   - T1 motion values (bible/19)
   - T2 audio LUFS (video_intro.md V9)
   - T3 layer stack order (video_intro.md V8)
   - T4 13 prompts content
   - T5 storyboard frame breakdown
   - T6 bible/04 extension
   - T7 naming convention
   - T8 cost projection
3. **Em chạy 20-vòng audit script** (verify FACTS: path/math/file/schema/link)
4. **Cài tool theo `SETUP_CHECKLIST.md`** sau khi DNS pass
5. **Render asset theo 13 prompts** (chỉ sau khi T4 approve)
6. **Build Resolve project + render intro master** (chỉ sau khi T1/T2/T3/T5 approve)
7. **SHA256 lock intro_master + update bible/04 channel_brand_assets**
8. **Test concat ep01** end-to-end

---

## Status check command

```powershell
Get-ChildItem "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\assets\hdk_channel" -Recurse -File `
  | Select-Object @{N='Path';E={$_.FullName.Replace('D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\assets\hdk_channel\','')}}, @{N='KB';E={[math]::Round($_.Length/1KB,1)}} `
  | Sort-Object Path | Format-Table -AutoSize
```
