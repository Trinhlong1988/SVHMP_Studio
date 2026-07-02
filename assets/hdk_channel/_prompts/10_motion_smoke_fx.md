> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: SVHMP_Studio/assets/hdk_channel/_AUDIT_TENTATIVE_LOG.md.

# 10 — Smoke FX Motion (Wan 2.1 local)

**Output:** `assets/hdk_channel/shared\motion\smoke_fx.mp4` (1920×1080, 24fps, 5 giây seamless loop)
**Tool:** ComfyUI + Wan 2.1

## Prompt
```
thick volumetric smoke billowing slowly upward, swirling natural turbulence, grey-white neutral color no cast, pure black background, cinematic atmospheric particle simulation, slow rising motion, no objects no figures no fire source, hyperrealistic smoke
```

## Negative
```
fire visible, explosion, fast motion, color cast, character, object, text, watermark, low quality, flicker, abrupt cut
```

## Loop seamless
- 5 giây = 120 frames @ 24fps
- Crossfade method: render 6 giây, cắt 5 giây giữa, blend frame đầu/cuối 0.4s

## Use case khác với fog_loop
- fog_loop_4s: horizontal drift, low-lying, mỏng
- smoke_fx: vertical rising, denser, dùng cho reveal moments / dramatic beats

## QA checklist
- [ ] 1920×1080, 24fps, 120 frames
- [ ] Smoke rising (NOT drifting horizontal)
- [ ] Pure black background
- [ ] Neutral grey color
- [ ] Loop seamless (test ffmpeg stream_loop)
