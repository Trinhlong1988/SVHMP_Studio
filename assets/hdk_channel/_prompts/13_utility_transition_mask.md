> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: SVHMP_Studio/assets/hdk_channel/_AUDIT_TENTATIVE_LOG.md.

# 13 — Transition Mask Blackout (Inkscape)

**Output:** `assets/hdk_channel/shared\utility\transition_mask_blackout.png` (3840×2160, RGBA alpha)
**Tool:** Inkscape

## Concept
Mask transition để CẮT cuối intro (segment 5: 4.0-4.5s) và bắt đầu narration ep. Hard cut to black qua mask gradient.

## Inkscape spec
- Canvas 3840×2160 (intro resolution)
- Rectangle fill linear gradient:
  - Top: #000000 alpha 0% (transparent)
  - Bottom: #000000 alpha 100% (opaque black)
- HOẶC iris-out: center transparent → edges black, radial
- 2 variant lưu cả 2:
  - `transition_mask_blackout_linear.png` (top-down fade)
  - `transition_mask_blackout_iris.png` (center iris)

## Use case
- INTRO segment 5: animate alpha 0→100 qua 0.5s → fade to black
- Generic: bất kỳ ep nào cần fade in/out

## Alternative dùng FFmpeg trực tiếp
Nếu chỉ cần hard fade đơn giản, FFmpeg fade filter đủ:
```
ffmpeg -i input.mp4 -vf "fade=out:st=4.0:d=0.5:color=black" output.mp4
```
→ Mask file chỉ cần khi muốn iris/shape transition phức tạp.

## QA checklist
- [ ] 3840×2160
- [ ] Alpha gradient smooth, no banding
- [ ] 2 variant: linear + iris
- [ ] Test composite trên intro → fade out clean
