> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: SVHMP_Studio/assets/hdk_channel/_AUDIT_TENTATIVE_LOG.md.

# 11 — Dust Particle Motion (Wan 2.1 local)

**Output:** `assets/hdk_channel/shared\motion\dust_particle.mp4` (1920×1080, 24fps, 4 giây seamless loop)
**Tool:** ComfyUI + Wan 2.1

## Prompt
```
fine dust particles floating slowly in air catching warm side light from camera right, particles drifting in gentle natural air current, pure black background, slight depth of field with some particles in focus others soft, atmospheric volumetric, cinematic close-mid distance, hyperrealistic dust simulation, calm breathing motion, no objects no figures
```

## Negative
```
heavy snow, rain, large debris, fast motion, color cast, character, object, text, watermark, low quality, abrupt cut
```

## Loop seamless
- 4 giây = 96 frames @ 24fps
- Particles không có "landmark" rõ → loop dễ hơn smoke/fog

## Composite usage
- ALL segments của intro: add subtle particle layer overlay (opacity 30-50%, screen blend)
- Add cảm giác chiều sâu cho moon, railway, storyteller stills

## QA checklist
- [ ] 1920×1080, 24fps, 96 frames
- [ ] Warm light side direction (right) → match lantern direction
- [ ] Pure black background
- [ ] Particles vừa, KHÔNG dày như tuyết
- [ ] Loop seamless
