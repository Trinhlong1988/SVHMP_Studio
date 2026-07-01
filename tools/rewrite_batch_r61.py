"""SVHMP G — Batch rewrite EP02-50 R61 violations.

Generic pattern map từ EP01 golden reference.
Strategy: expand subject + verb compound or prefix với spatial/temporal context.
"""
import shutil
from pathlib import Path

SVHMP = Path(__file__).resolve().parents[1]

# Generic patterns (sentence ≤5 words starting with banned + short next)
PATTERNS = {
    # Anh + short verb
    'Anh gật.': 'Khải Phong khẽ gật đầu.',
    'Anh gật chậm.': 'Khải Phong gật đầu chậm rãi.',
    'Anh đi.': 'Khải Phong bước đi.',
    'Anh ra.': 'Khải Phong bước ra.',
    'Anh đứng dậy.': 'Khải Phong từ từ đứng dậy.',
    'Anh ngồi xuống.': 'Khải Phong ngồi xuống ghế.',
    'Anh quay đầu.': 'Khải Phong quay đầu lại.',
    'Anh cúi đầu.': 'Khải Phong khẽ cúi đầu.',
    'Anh nhắm mắt.': 'Khải Phong nhắm mắt lại.',
    'Anh mở mắt.': 'Khải Phong từ từ mở mắt.',
    'Anh thở dài.': 'Khải Phong thở dài một hơi.',

    # Cô + short verb
    'Cô gật.': 'Cô gái khẽ gật đầu.',
    'Cô gật chậm.': 'Cô gái gật đầu chậm rãi.',
    'Cô khẽ gật.': 'Cô gái khẽ gật đầu.',
    'Cô cúi đầu.': 'Cô gái khẽ cúi đầu.',
    'Cô ngẩng lên.': 'Cô gái ngẩng đầu lên.',
    'Cô quay đầu.': 'Cô gái quay đầu lại.',
    'Cô đứng dậy.': 'Cô gái từ từ đứng dậy.',
    'Cô ngồi yên.': 'Cô gái ngồi yên lặng.',
    'Cô khóc nhẹ.': 'Cô gái khẽ khóc nhẹ.',
    'Cô lắc đầu.': 'Cô gái khẽ lắc đầu.',
    'Cô nhìn anh.': 'Cô gái nhìn về phía anh.',
    'Cô nhìn xa.': 'Cô gái nhìn ra xa.',

    # Ông + Bà + Cụ
    'Ông cúi đầu.': 'Ông cụ khẽ cúi đầu.',
    'Ông gật đầu.': 'Ông cụ khẽ gật đầu.',
    'Bà gật đầu.': 'Bà cụ khẽ gật đầu.',
    'Cụ gật.': 'Cụ già khẽ gật đầu.',

    # Em (passenger first-person)
    'Em hứa.': 'Em đã hứa với chị.',
    'Em nhận.': 'Em nhận lấy nó.',
    'Em đi.': 'Em bước đi.',

    # Time/weather banned starts ≤5 words
    'Đêm đó mưa.': 'Vào đêm đó, mưa rơi không ngớt.',
    'Đêm nay lạnh.': 'Vào đêm nay, trời lạnh hơn mọi khi.',
    'Đêm nay tối.': 'Vào đêm nay, trời tối đen như mực.',
    'Hôm nay nắng.': 'Vào hôm nay, trời nắng nhẹ.',
    'Hôm qua mưa.': 'Vào hôm qua, trời đổ mưa.',
    'Năm ấy lạnh.': 'Vào năm ấy, mùa đông rất lạnh.',
    'Sáng nay sương.': 'Vào sáng nay, sương phủ dày.',
    'Chiều nay mưa.': 'Vào chiều nay, trời đổ mưa rào.',
    'Tối nay khuya.': 'Vào tối nay, khuya hơn thường ngày.',

    # Mưa/Gió/Sương short
    'Mưa rơi đều.': 'Tiếng mưa rơi đều bên ngoài.',
    'Mưa rơi nhẹ.': 'Mưa rơi nhẹ nhàng từ trời.',
    'Gió thổi nhẹ.': 'Cơn gió thổi nhẹ qua cửa kính.',
    'Sương dày dần.': 'Sương ngoài cửa kính dày dần.',
    'Sương đặc thêm.': 'Sương ngoài kính đặc thêm.',

    # Cô + Anh + Ông short patterns generic
    'Cô cười nhẹ.': 'Cô gái mỉm cười nhẹ.',
    'Anh cười nhẹ.': 'Khải Phong khẽ mỉm cười.',
    'Cô khóc.': 'Cô gái khẽ khóc.',
    'Anh khóc.': 'Khải Phong khẽ khóc.',
    'Em khóc.': 'Em đã khóc nức nở.',

    # "Bác" patterns
    'Bác không nói.': 'Bác tài không nói gì.',
    'Bác liếc gương.': 'Bác tài liếc gương chiếu hậu.',
    'Bác gật đầu.': 'Bác tài khẽ gật đầu.',

    # Ngoài cửa kính,
    'Ngoài cửa kính,': 'Bên ngoài cửa kính,',
}

def main():
    apply = '--apply' in __import__('sys').argv
    print(f"Batch rewrite EP02-50 | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    total = 0
    eps_modified = 0
    for n in range(2, 91):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        new_text = text
        count = 0
        for old, new in PATTERNS.items():
            occ = new_text.count(old)
            if occ:
                new_text = new_text.replace(old, new)
                count += occ
        if count:
            total += count
            eps_modified += 1
            if apply:
                shutil.copy2(p, p.with_suffix('.md.bak.batch_R61'))
                p.write_text(new_text, encoding='utf-8')
            print(f"EP{n:02d}: {count} fixes")
    print(f"\nTotal: {total} fixes in {eps_modified} EPs")
    if apply:
        print("APPLIED (backups: *.bak.batch_R61)")

if __name__ == '__main__':
    main()
