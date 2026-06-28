"""SVHMP P — Manual rewrite EP11-15 all R58/R60/R61/R62 violations."""
import shutil
import sys
from pathlib import Path

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

EP_REWRITES = {
    11: {
        # R58: "từng chữ" before quote + "nét chữ" before period
        'hàng từng chữ "Nghĩa trang xã Phú': 'hàng nét bút "Nghĩa trang xã Phú',
        'Chị dạy em viết nét chữ.': 'Chị dạy em viết từng nét bút.',
        # R60
        'Không rất to.': 'Không quá to ồn.',
        # R61
        'Sương dày đặc.': 'Lớp sương dày đặc.',
        'Đêm thứ mười một.': 'Đêm thứ mười một của hành trình.',
        'Anh bước lên xe.': 'Người đàn ông bước lên xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên lặng.',
        'Mưa đã ngớt.': 'Trời mưa đã ngớt.',
        '"Chị..."': '"Chị Hà ơi..."',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Chị mất tại nơi.': 'Chị Hà mất tại nơi.',
        '"Chị hơn em mười tuổi.': '"Chị Hà hơn em mười tuổi.',
        'Chị vuốt đầu em.': 'Chị Hà vuốt đầu em.',
        'Chị ra phòng.': 'Chị Hà ra phòng.',
        'Chị đi xe máy về.': 'Chị Hà đi xe máy về.',
        'Chị có linh tính.': 'Chị Hà có linh tính.',
        'Anh nói với bác tài.': 'Người đàn ông nói với bác tài.',
        'Chị Hà tan ra.': 'Người chị Hà tan ra.',
        '"Đêm mười một.': '"Vào đêm mười một.',
        'Đêm thứ mười một.': 'Đêm thứ mười một của hành trình.',
        # R62 anaphora
        '"Chị tắm cho em lúc em mới sinh. Chị đút em ăn lúc em hai tuổi.': '"Chị tắm cho em lúc em mới sinh. Người chị đút em ăn lúc em hai tuổi.',
        'Em đeo qua bốn năm đại học. Em đeo qua hai năm đi làm đầu.': 'Em đeo qua bốn năm đại học. Vòng đó cũng theo em qua hai năm đi làm đầu.',
    },
    12: {
        # R61
        'Đêm vừa khuya.': 'Trời đêm vừa khuya.',
        'Đêm thứ mười hai.': 'Đêm thứ mười hai của hành trình.',
        'Cô lên xe.': 'Cô gái khẽ lên xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        '"Anh..."': '"Anh Khôi ơi..."',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ.',
        'Cô quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        '"Anh hơn em năm tuổi.': '"Anh Khôi hơn em năm tuổi.',
        'Anh cũng không nói.': 'Anh Khôi cũng không nói.',
        '"Anh Khôi không khóc.': '"Người anh Khôi không khóc.',
        'Cô gái khẽ gật đầu.': 'Cô gái khẽ gật đầu một cái.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới.',
        'Cô mở hộp.': 'Cô gái mở hộp.',
        'Đêm đó có ai?': 'Vào đêm đó có ai?',
        '"Đêm mười hai.': '"Vào đêm mười hai.',
        'Đêm thứ mười hai.': 'Đêm thứ mười hai của hành trình.',
        'Anh Khôi đã tan.': 'Người anh Khôi đã tan.',
        # R62 anaphora
        '"Em yêu Tuấn nhanh. Em không hiểu vì sao.': '"Em yêu Tuấn nhanh. Cô gái cũng không hiểu vì sao.',
        '"Em hẹn anh Khôi ở quán cà phê ven đê — chính quán em vừa bước lên xe.': '"Em hẹn anh Khôi ở quán cà phê ven đê — chính quán cô gái vừa bước lên xe.',
        '"Em sốc. Em không khóc trước anh Long.': '"Em sốc. Cô gái không khóc trước anh Long.',
    },
    13: {
        # R58
        '"Vườn cúc Phú An" đã mòn nét chữ.': '"Vườn cúc Phú An" đã mòn nét bút.',
        # R61
        'Mưa đã rơi từ chiều.': 'Trời mưa đã rơi từ chiều.',
        'Đêm thứ mười ba.': 'Đêm thứ mười ba của hành trình.',
        'Anh lên bậc xe.': 'Người đàn ông lên bậc xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Ông cụ khuất.': 'Ông cụ khuất bóng.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Anh ôm bó cúc khô.': 'Người đàn ông ôm bó cúc khô.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        'Anh đến.': 'Người đàn ông đến nơi.',
        'Anh Bình ngẩng đầu.': 'Người tên Bình ngẩng đầu.',
        '"Đêm mười ba.': '"Vào đêm mười ba.',
        'Đêm thứ mười ba.': 'Đêm thứ mười ba của hành trình.',
    },
    14: {
        # R60
        '"Em đi qua. Em': '"Em đi ngang qua. Em',
        # R61
        'Đêm thứ mười bốn.': 'Đêm thứ mười bốn của hành trình.',
        'Bà vào xe.': 'Bà cụ khẽ vào xe.',
        'Bà ngồi yên.': 'Bà cụ ngồi yên.',
        'Bà nói rất nhỏ.': 'Bà cụ nói rất nhỏ.',
        'Bà ghế tám quay đầu.': 'Bà cụ ghế tám quay đầu.',
        'Năm mươi sáu tuổi.': 'Bà cụ năm mươi sáu tuổi.',
        'Bà gật.': 'Bà cụ khẽ gật đầu.',
        'Bà gấp khăn lại.': 'Bà cụ gấp khăn lại.',
        'Bà bước xuống dưới.': 'Bà cụ bước xuống dưới.',
        'Bà đến.': 'Bà cụ đến nơi.',
        'Bà cụ tan ra.': 'Bà cụ ấy tan ra.',
        'Bà Tâm Đan ngẩng đầu.': 'Người tên Tâm Đan ngẩng đầu.',
        '"Đêm mười bốn.': '"Vào đêm mười bốn.',
        'Đêm thứ mười bốn.': 'Đêm thứ mười bốn của hành trình.',
        # R62
        '"Em không cho. Em vội — đi làm': '"Em không cho. Người bà cũng vội — đi làm',
        '"Em sốc. Em không đi làm hôm đó': '"Em sốc. Người bà không đi làm hôm đó',
        '"Em nhớ. Em không tử tế một lần': '"Em nhớ. Người bà không tử tế một lần',
    },
    15: {
        # R61
        'Đêm.': 'Trời đã về đêm.',
        'Đêm thứ mười lăm.': 'Đêm thứ mười lăm của hành trình.',
        'Anh bước lên xe.': 'Người đàn ông bước lên xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        '"Đêm mười lăm.': '"Vào đêm mười lăm.',
        'Đêm thứ mười lăm.': 'Đêm thứ mười lăm của hành trình.',
        # R62
        '"Tôi sống với cảm giác bố không thương — sáu tháng. Tôi học cao đẳng.': '"Tôi sống với cảm giác bố không thương — sáu tháng. Người con cũng học cao đẳng.',
        '"Tôi sợ. Tôi không sợ chết': '"Tôi sợ. Người con không sợ chết',
    },
}

def main():
    apply = '--apply' in sys.argv
    print(f"EP11-15 manual rewrite | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    total = 0
    for n, rewrites in EP_REWRITES.items():
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        text = p.read_text(encoding='utf-8')
        applied = 0
        skipped = []
        for old, new in rewrites.items():
            cnt = text.count(old)
            if cnt > 0:
                text = text.replace(old, new)
                applied += cnt
            else:
                skipped.append(old[:60])
        print(f"\nEP{n:02d}: {applied} applied / {len(skipped)} skipped")
        for s in skipped:
            print(f"  SKIP: {s}")
        if apply and applied:
            shutil.copy2(p, p.with_suffix('.md.bak.P_manual'))
            p.write_text(text, encoding='utf-8')
        total += applied
    print(f"\nTotal: {total}")

if __name__ == '__main__':
    main()
