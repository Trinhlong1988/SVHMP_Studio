"""SVHMP — Ngạn opening hook template audit (bible/01).

Opening 4-8 từ đầu PHẢI = [BỐI CẢNH THỜI GIAN/ĐỊA DANH] hoặc [NHÂN CHỨNG FRAME]
CẤM in medias res.
"""
import re, sys, json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(__file__).resolve().parents[1]

# Accepted opening patterns
BỐI_CẢNH_STARTS = [
    r'^Năm \d{4}',                  # "Năm 2005"
    r'^Tháng \w+ năm',              # "Tháng tư năm ấy"
    r'^Tháng \w+ [A-ZĐ]\w+',        # "Tháng tư Hà Nội"
    r'^\w+ \d{4}',                  # "Hà Nội 2018"
    r'^[A-ZĐ]\w+ \w+\. \w+',        # "Hà Nội đêm tháng tư"
    r'^Vào (đêm|hôm|sáng|chiều|tối|năm) \w+',  # "Vào đêm thứ mười"
    r'^Hôm đó',                     # "Hôm đó, từ bảy giờ tối"
    r'^Đêm \w+ tháng',              # "Đêm hai tám tháng Chạp"
]

NHÂN_CHỨNG_STARTS = [
    r'^Câu chuyện',
    r'^Tôi nghe',
    r'^Có một câu chuyện',
    r'^Tôi có người quen',
]

IN_MEDIAS_RES_BAD = [
    r'^Tôi giật mình',
    r'^Bỗng nhiên',
    r'^Đột nhiên',
    r'^Chợt',
    r'^Một tiếng',  # "Một tiếng động vang lên" type
]

def find_opening_sentence(text):
    """Find first narrative sentence (after metadata/intro/HOOK header)."""
    body = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Skip intro block "Hắc Dạ Ký..." "Tác giả:..." "Series:..." "Tập N..."
    body = re.sub(r'^.*?## 1\. HOOK[^\n]*\n', '', body, count=1, flags=re.DOTALL)
    body = re.sub(r'^\[pause:[^\]]+\]\s*', '', body)
    body = body.strip()
    # First sentence
    m = re.match(r'^([^.!?\n]+[.!?])', body)
    return m.group(1).strip() if m else None

def main():
    print("=" * 70)
    print("NGẠN OPENING HOOK TEMPLATE — bible/01 audit")
    print("=" * 70)

    results = {'good': [], 'in_medias_res': [], 'unclear': []}
    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists(): continue
        text = p.read_text(encoding='utf-8')
        opening = find_opening_sentence(text)
        if not opening:
            results['unclear'].append((n, 'NO_OPENING'))
            continue

        is_good = (
            any(re.match(p, opening) for p in BỐI_CẢNH_STARTS) or
            any(re.match(p, opening) for p in NHÂN_CHỨNG_STARTS)
        )
        is_bad = any(re.match(p, opening) for p in IN_MEDIAS_RES_BAD)

        if is_bad:
            results['in_medias_res'].append((n, opening[:60]))
        elif is_good:
            results['good'].append((n, opening[:60]))
        else:
            results['unclear'].append((n, opening[:60]))

    print(f"\n✅ GOOD opening Ngạn-style: {len(results['good'])}/50")
    print(f"❌ IN MEDIAS RES (bad): {len(results['in_medias_res'])}")
    for n, s in results['in_medias_res'][:5]:
        print(f"  EP{n:02d}: {s}")
    print(f"⚠️ UNCLEAR (needs review): {len(results['unclear'])}")
    for n, s in results['unclear'][:10]:
        print(f"  EP{n:02d}: {s}")

    out = SVHMP / 'runtime' / 'audit_ngan_opening.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
