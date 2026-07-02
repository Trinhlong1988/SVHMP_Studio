> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: SVHMP_Studio/assets/hdk_channel/_AUDIT_TENTATIVE_LOG.md.

# 08 — Fog Loop Motion (Wan 2.1 local / ComfyUI)

**Output:** `assets/hdk_channel/shared\motion\fog_loop_4s.mp4` (1920×1080, 24fps, 4 giây, seamless loop)
**Tool:** ComfyUI + Wan 2.1 workflow (cài theo SETUP_CHECKLIST.md)
**Alternative fallback:** AnimateDiff + SDXL nếu Wan 2.1 chưa setup được

## Prompt
```
slow drifting fog moving horizontally left to right, low-lying ground fog, volumetric atmospheric, pure black background, neutral grey-white fog color no cast, cinematic atmospheric loop, smooth continuous motion, no characters no objects, hyperrealistic fog simulation
```

## Negative
```
fast motion, explosion, color cast, character, object, text, watermark, low quality, flicker, jitter, abrupt cut
```

## Loop seamless requirement
- 4 giây total = 96 frames @ 24fps
- Frame 96 phải khớp gần-byte với frame 1 → loop infinite không thấy cut
- Method: render 5 giây → cắt 4 giây giữa → crossfade frame đầu-cuối 0.5s nếu cần

## A/B test với Kling (decision gate)
- [ ] Render Wan 2.1 sample 4s
- [ ] Đăng ký Kling free trial → render cùng prompt
- [ ] A/B: Mr.Long judge loop seamless quality
- [ ] Nếu Wan thua xa → mua Kling 1 tháng $37 render 4 motion asset xong unsubscribe
- [ ] Nếu Wan đủ → ship Wan, save $37

## QA checklist
- [ ] 1920×1080
- [ ] 24fps đúng
- [ ] 4.0 giây = 96 frames
- [ ] Frame 1 vs 96 khớp (loop test trong FFmpeg `-stream_loop`)
- [ ] Pure black background, neutral fog color
- [ ] KHÔNG flicker giữa các frame (Wan đôi khi lỗi)
