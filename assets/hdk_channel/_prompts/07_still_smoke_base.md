> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: SVHMP_Studio/assets/hdk_channel/_AUDIT_TENTATIVE_LOG.md.

# 07 — Smoke Base (SDXL local)

**Output:** `assets/hdk_channel/shared\still\smoke_base.png` (3840×2160)
**Tool:** ComfyUI SDXL local

## Prompt (positive)
```
thick volumetric smoke and fog filling frame, rolling slow curls of grey-white smoke against pitch black background, soft volumetric light passing through smoke from upper-left at low angle, smoke density medium so background partially visible, no objects no figures just smoke, cinematic atmospheric, fine grain film, high dynamic range, hyperrealistic smoke simulation, no color cast just neutral grey, pure black background where smoke is thinner
```

## Negative
```
fire, flame, explosion, character, people, object, building, text, watermark, color cast blue, color cast red, color cast green, neon, anime, cartoon, low quality, blurry, jpeg artifacts, oversaturated, color blocking
```

## Reuse
- Layer composite cho mọi scene cần atmospheric
- Multiply/screen blend mode trong Resolve Fusion
- 1000+ ep reuse → màu neutral cực kỳ quan trọng

## QA checklist
- [ ] 3840×2160
- [ ] Pure black background (#000000) ở chỗ smoke thinner
- [ ] Smoke trung tính (KHÔNG cast blue/red/green) → composite linh hoạt
- [ ] Density vừa: thấy được background nhưng thấy được smoke
- [ ] KHÔNG có flame/object trong smoke
