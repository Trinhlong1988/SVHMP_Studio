> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: SVHMP_Studio/assets/hdk_channel/_AUDIT_TENTATIVE_LOG.md.

# 01 — HDK Logo (Inkscape brief)

**Output:** `assets/hdk_channel/brand\logo\hdk_logo.svg`
**Tool:** Inkscape (free)
**Size:** 2048×2048 SVG vector (export PNG 4K khi cần)

## Concept
"Hắc Dạ Ký" — tự sự cõi vô hình. Logo đơn giản, dấu ấn cảm xúc, dùng được 1000+ ep mà không lỗi thời.

## Design spec
- **Form:** kết hợp ký tự "H" + "D" + "K" thành 1 mark đơn (negative space giữa 3 chữ)
- **Visual cue:** một vệt khói/sương mảnh quấn dưới chân chữ, gợi ý "cõi vô hình"
- **Style:** monoline serif Việt hóa, nét 8-12px scale 2048
- **Color:** 
  - Logo: #E8DCC4 (warm ivory, gợi đèn dầu)
  - Background trong intro: #0A0606 (đen ám đỏ rất nhẹ)
- **No:** không gradient, không 3D, không texture phức tạp — phải scale từ 64px tới 4K rõ ràng

## Font Việt
- Dùng font đã cài Windows hỗ trợ dấu: **Cormorant Garamond** (Google Font, free, có dấu đầy đủ)
- Convert path sau khi typeset → tránh fallback khi mở máy khác

## Export
- SVG (master)
- PNG 2048×2048 alpha transparent
- PNG 4096×4096 alpha transparent (backup)

## Checklist
- [ ] Mở Inkscape, canvas 2048×2048 transparent
- [ ] Typeset "HĐK" hoặc "HDK" Cormorant Garamond bold
- [ ] Vẽ vệt khói dưới chân
- [ ] Convert text to path (Path > Object to Path)
- [ ] Export SVG + PNG 2K + PNG 4K
- [ ] Verify trên dark background #0A0606 readable
