> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: SVHMP_Studio/assets/hdk_channel/_AUDIT_TENTATIVE_LOG.md.

# 09 — Lantern Flame Loop Motion (Wan 2.1 local)

**Output:** `assets/hdk_channel/shared\motion\lantern_flame_loop.mp4` (1024×1024, 24fps, 3 giây seamless loop)
**Tool:** ComfyUI + Wan 2.1

## Concept
Overlay lên `lantern_still.png` (asset 06). Chỉ render NGỌN LỬA trong glass chimney, để static lantern phía dưới.

## Prompt
```
single small oil lantern flame flickering inside glass chimney, warm amber gold flame, gentle natural flicker motion, slow breathing rhythm, pure black background, no lantern body just isolated flame, hyperrealistic fire simulation, intimate close-up, slight wisp of smoke rising from flame tip
```

## Negative
```
explosion, big fire, multiple flames, color cast green or blue, lantern body visible, character, object, text, watermark, fast violent flicker, abrupt cut, low quality
```

## Loop seamless
- 3 giây = 72 frames @ 24fps
- Flame rhythm 1 chu kỳ thở ~ 1.5s → 2 chu kỳ trong 3s → loop tự nhiên

## Composite usage
- Trong Resolve: place lantern_still.png layer dưới, lantern_flame_loop.mp4 screen blend mode trên, position khớp glass chimney
- INTRO segment 2 (0.8-1.6s): flame fade in

## QA checklist
- [ ] 1024×1024 (square fit glass chimney)
- [ ] Pure black background cho screen blend
- [ ] Flame center frame
- [ ] 72 frames, loop seamless
- [ ] Flicker tự nhiên (KHÔNG strobe/violent)
