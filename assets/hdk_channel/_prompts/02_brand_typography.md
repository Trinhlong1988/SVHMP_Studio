> ✅ **APPROVED Mr.Long 2026-06-26** — content trong file này đã Mr.Long approve toàn bộ cluster T1-T8. Audit trail historical: SVHMP_Studio/assets/hdk_channel/_AUDIT_TENTATIVE_LOG.md.

# 02 — Typography 2 Tagline (Inkscape brief)

**Output:**
- `assets/hdk_channel/brand\typography\hdk_tagline_channel.svg` — "Chuyện kể từ cõi vô hình"
- `assets/hdk_channel/brand\typography\hdk_tagline_chuyenxe.svg` — "Ai cũng có một chuyến xe chưa nói lời tạm biệt"

**Tool:** Inkscape (free)
**Size:** 3840×800 SVG vector

## Tagline 1 — channel (intro lock)
- Text: **"Chuyện kể từ cõi vô hình"**
- Font: **Cormorant Garamond Italic** (gợi tự sự, mềm)
- Size: 180pt height
- Color: #C9B789 (mờ vàng đèn dầu)
- Letter spacing: +40 (rộng, hơi điện ảnh)
- Alignment: center
- Drop shadow: 4px blur #000000 50% (tăng tương phản trên fog)

## Tagline 2 — series chuyenxe (per-ep card hoặc end card)
- Text: **"Ai cũng có một chuyến xe chưa nói lời tạm biệt"**
- Font: **Cormorant Garamond Italic**
- Size: 120pt height (dài hơn nên giảm)
- Color: #C9B789
- 2 dòng max nếu width thiếu: "Ai cũng có một chuyến xe" / "chưa nói lời tạm biệt"

## Việt dấu kiểm tra
Đặc biệt kiểm 6 ký tự dấu thường lỗi:
- ơ (cõi)
- ờ (lời)
- ạ (tạm)
- ế (kể)
- ư (chưa)
- ầ (chầu — nếu có)

→ Sau khi typeset, **convert path** rồi zoom 800% kiểm từng dấu không bị mất/lệch.

## Export
- SVG (master)
- PNG 3840×800 alpha transparent
- PNG 7680×1600 (4K headroom)

## Checklist
- [ ] Inkscape canvas 3840×800 transparent
- [ ] Typeset tagline 1, kiểm 6 dấu zoom 800%
- [ ] Drop shadow filter
- [ ] Convert text to path
- [ ] Export SVG + PNG 3840 + PNG 7680
- [ ] Lặp lại tagline 2
- [ ] Verify đọc rõ trên dark background trong intro
