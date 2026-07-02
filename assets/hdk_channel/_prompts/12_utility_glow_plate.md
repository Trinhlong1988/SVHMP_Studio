> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: SVHMP_Studio/assets/hdk_channel/_AUDIT_TENTATIVE_LOG.md.

# 12 — Glow Plate Radial (SDXL hoặc Inkscape gradient)

**Output:** `assets/hdk_channel/shared\utility\glow_plate_radial.png` (2048×2048, RGBA alpha)
**Tool:** Inkscape (đơn giản hơn) hoặc SDXL nếu cần organic

## Concept
Plate radial gradient từ trung tâm sáng → biên trong suốt. Composite "screen" blend lên logo / lantern / moon để tăng glow mà KHÔNG cần Fusion plugin.

## Inkscape spec (cách 1 — nhanh)
- Canvas 2048×2048 transparent
- Circle 1800×1800 center
- Radial gradient fill:
  - Center: #FFE8B8 alpha 100% (warm amber)
  - 30%: #C9B789 alpha 60%
  - 100% (edge): transparent
- Export PNG 2048×2048 alpha

## SDXL spec (cách 2 — organic glow)
Prompt:
```
soft warm amber radial glow on pure black background, center bright golden hue fading smoothly to pitch black edges, no object no source visible just pure light, hyperrealistic volumetric light, dust particles barely visible in glow halo
```
→ Sau đó tách alpha channel bằng GIMP/Photoshop chroma key black

## Use case
- INTRO segment 2: glow plate behind lantern khi flame ignites
- INTRO segment 3: glow behind logo reveal
- INTRO segment 4: glow nhẹ behind tagline text

## QA checklist
- [ ] 2048×2048 transparent
- [ ] Alpha gradient smooth (no banding)
- [ ] Warm amber #FFE8B8 → transparent
- [ ] Test screen blend trên black → glow tự nhiên
