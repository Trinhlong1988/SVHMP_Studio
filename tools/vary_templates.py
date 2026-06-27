"""SVHMP — Vary HOOK opener templates across EPs (R49 enforcement).

Rotate 10 varied opener templates across EP11-50 (skip EP01-10 golden).

Usage: python tools/vary_templates.py [--dry-run]
"""
import re
import sys
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# 10 varied opener templates (atmospheric variety)
OPENERS = [
    # Variant 0 — original (keep some)
    "Đêm tháng tư. Mưa nhẹ. Chuyến xe đêm chạy qua đoạn đường ven sông {river}, {city}. Đèn pha quét lên hàng {tree}.",
    # Variant 1
    "Tháng tư. Đêm vừa khuya. Xe đêm rẽ vào đoạn ven sông {river}, {city}. Đèn pha cắt qua màn sương — chiếu lên hàng {tree} bên đường.",
    # Variant 2
    "Mưa đã rơi từ chiều. Đêm tháng tư — không tan hết. Chuyến xe đêm đi qua đoạn {river}, {city} — đèn pha hắt lên hàng {tree} ướt sương.",
    # Variant 3
    "Cuối tháng tư. Trời ẩm. Xe đêm chạy chậm qua đường ven {river}, {city}. Hàng {tree} ven đường — lá còn rơi vài giọt mưa cuối ngày.",
    # Variant 4
    "Đêm. Đường vắng. Xe đêm trôi qua đoạn {river}, {city}. Đèn pha quét đi quét lại trên hàng {tree} — không có ai khác trên đường.",
    # Variant 5
    "Hà Nội cuối tháng tư. Đêm. Chuyến xe đi qua đoạn ven {river}, {city}. Đèn pha rọi lên hàng {tree} — ánh đèn vàng cô đơn.",
    # Variant 6
    "Sau cơn mưa chiều. Đêm xuống nhanh. Xe đêm rẽ vào đoạn {river}, {city}. Hàng {tree} ven đường còn đẫm — đèn pha quét lên thân cây ướt.",
    # Variant 7
    "Đêm thứ {night_text} — Khải Phong ngồi ghế thứ ba. Mưa tháng tư rỉ rả ngoài kính xe. Xe đi qua đoạn {river}, {city} — hàng {tree} im bóng.",
    # Variant 8
    "Đèn xe rọi vào sương. Đêm tháng tư miền {region}. Chuyến xe đi qua đoạn {river}, {city} — hàng {tree} ven đường thấp thoáng trong sương.",
    # Variant 9
    "Phố vắng. Đêm thưa. Xe đêm đi qua đoạn {river}, {city} — đèn pha hắt lên hàng {tree} cao quá đầu — bóng đổ dài trên mặt đường ướt.",
]

def get_template_idx(ep_num):
    """Rotate templates so consecutive EPs don't repeat."""
    return (ep_num - 11) % len(OPENERS)

def find_opener_pattern(text):
    """Find the formulaic opener block in HOOK section.
    Flexible regex: Đêm tháng tư + [Mưa variants] + Chuyến xe đêm + ven [place] + Đèn pha."""
    # Master flexible pattern — catch most variants
    # Đêm tháng tư. [Mưa anything.] [Optional Mặt đường anything.] Chuyến xe đêm (chạy|đi|rẽ) [anything] (?:ven |nội thành |vành đai |về |từ |qua )[anything until period]. [Đèn pha anything.]
    flex = re.compile(
        r'Đêm tháng tư\. '
        r'(?:[A-ZĐ][^.]*\. ){0,3}'  # 0-3 lead sentences (Mưa.../Mặt đường...)
        r'Chuyến xe đêm (?:chạy|đi|rẽ|trôi)[^.]*\. '
        r'(?:[A-ZĐ][^.]*\. ){0,2}',  # 0-2 follow sentences (Đèn pha.../sensory)
        re.DOTALL
    )
    m = flex.search(text)
    if m:
        return m
    return None

def extract_place_from_match(matched_text):
    """Extract location info from matched opener for template fill."""
    # Try to find "ven [place]" or "qua đoạn [place]" or just any city name
    m = re.search(r'(?:ven|qua đoạn|qua|đến|về)\s+([^,.\n]{3,40})(?:,|\.)\s*([^.\n]{3,30})?', matched_text)
    river = "sông"
    city = "Hà Nội"
    if m:
        if m.group(1):
            river = m.group(1).strip()[:30]
        if m.group(2):
            city = m.group(2).strip()[:30]
    # tree from "Đèn pha quét lên hàng X" if present
    tree_m = re.search(r'Đèn pha[^.]*?(?:lên|trên)\s+(?:hàng |rừng |bụi )?([^,.\n—]{3,30})', matched_text)
    tree = tree_m.group(1).strip()[:25] if tree_m else "cây"
    return river, city, tree

def rewrite_ep(ep_num, dry_run=False):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists():
        return 0
    text = p.read_text(encoding='utf-8')

    m = find_opener_pattern(text)
    if not m:
        if not dry_run:
            print(f"  EP{ep_num:02d}: no formulaic opener found")
        return 0

    # Extract from flexible match
    matched = m.group()
    river, city, tree = extract_place_from_match(matched)

    # Get template
    tpl_idx = get_template_idx(ep_num)
    template = OPENERS[tpl_idx]

    # Region inference
    region = "Bắc"
    if any(c in city for c in ['Sài Gòn', 'Bình', 'Đồng', 'Cần Thơ', 'Bến Tre', 'Sóc Trăng', 'Quảng Ninh', 'Quảng Bình']):
        region = "Trung-Nam"
    elif 'Lào' in city or 'Hà' in city:
        region = "Bắc"

    night_text = str(ep_num) + " trên chuyến xe"

    # Build new opener
    new_opener = template.format(
        river=river.strip(),
        city=city.strip(),
        tree=tree.strip(),
        region=region,
        night_text=night_text,
    )

    new_text = text[:m.start()] + new_opener + text[m.end():]

    if not dry_run:
        p.write_text(new_text, encoding='utf-8')
    print(f"  EP{ep_num:02d}: variant {tpl_idx} applied")
    return 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    # Skip EP01-10 (golden + initial)
    changed = 0
    for n in range(11, 51):
        changed += rewrite_ep(n, args.dry_run)
    print(f"\nTotal EPs varied: {changed}/40")
    return 0

if __name__ == '__main__':
    sys.exit(main())
