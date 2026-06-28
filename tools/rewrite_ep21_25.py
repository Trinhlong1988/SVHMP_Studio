"""SVHMP V — Manual rewrite EP21-25 all R58/R60/R61/R62 violations."""
import shutil
import sys
from pathlib import Path

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

EP_REWRITES = {
    21: {
        # R58 chữ + rũ
        'gỗ xưa — đã mòn từng chữ —': 'gỗ xưa — đã mòn nét bút —',
        'rồi tay rũ.': 'rồi tay rũ xuống.',
        # R60
        '"Vợ tôi im. Hiể': '"Vợ tôi im lặng. Hiể',
        # R61
        'Đêm vắng tanh.': 'Đêm hôm nay vắng tanh.',
        'Đêm thứ hai mươi mốt.': 'Đêm thứ hai mươi mốt của hành trình.',
        'Anh lên bậc xe.': 'Người đàn ông lên bậc xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Năm mươi tuổi.': 'Em năm mươi tuổi rồi.',
        'Đêm tôi sinh ra.': 'Vào đêm tôi sinh ra.',
        'Anh đến mộ.': 'Người đàn ông đến mộ.',
        '"Đêm hai mươi mốt.': '"Vào đêm hai mươi mốt.',
        'Đêm thứ hai mươi mốt.': 'Đêm thứ hai mươi mốt của hành trình.',
        # R62
        '"Tôi nhớ. Tôi không bao giờ nhìn thấy mặt mẹ': '"Tôi nhớ. Người con không bao giờ nhìn thấy mặt mẹ',
    },
    22: {
        'Thầy tan ra.': 'Người thầy tan ra.',
        'Đêm vừa khuya.': 'Trời đêm vừa khuya.',
        'Đêm thứ hai mươi hai.': 'Đêm thứ hai mươi hai của hành trình.',
        'Cô vào xe.': 'Cô gái khẽ vào xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới đường.',
        'Cô bước vào văn phòng.': 'Cô gái bước vào văn phòng.',
        'Cô đến.': 'Cô gái đến nơi đó rồi.',
        'Đêm mưa.': 'Trời đêm mưa.',
        '"Đêm hai mươi hai.': '"Vào đêm hai mươi hai.',
        'Đêm thứ hai mươi hai.': 'Đêm thứ hai mươi hai của hành trình.',
        # R62
        'Em ở Mai Trung — Bắc Ninh — quê. Em làm giáo viên cấp ba': 'Em ở Mai Trung — Bắc Ninh — quê. Cô gái làm giáo viên cấp ba',
        '"Em sốc. Em xin nghỉ — về Bắc Ninh': '"Em sốc. Cô gái xin nghỉ — về Bắc Ninh',
        '"Em sốc. Em không khóc trước vợ thầy.': '"Em sốc. Cô gái không khóc trước vợ thầy.',
        '"Em đi đám tang thầy hôm sau. Em đứng bên quan tài.': '"Em đi đám tang thầy hôm sau. Cô gái đứng bên quan tài.',
        'Em mang sách thầy tặng — đặt trên ghế thầy giữ lại. Em không bao giờ giữ':
            'Em mang sách thầy tặng — đặt trên ghế thầy giữ lại. Cô gái không bao giờ giữ',
    },
    23: {
        # R58 chữ
        'chỉ còn từng chữ "Hải Cảng"': 'chỉ còn nét bút "Hải Cảng"',
        'chỉ nhìn nét nét chữ.': 'chỉ nhìn từng nét bút.',  # replace_all (2 instances)
        'không có nét chữ.': 'không có nét bút nào.',
        # R61
        'Mưa đã rơi từ chiều.': 'Trời mưa đã rơi từ chiều.',
        'Đêm thứ hai mươi ba.': 'Đêm thứ hai mươi ba của hành trình.',
        'Anh bước lên xe.': 'Người đàn ông bước lên xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh đặt thư lên đùi.': 'Người đàn ông đặt thư lên đùi.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Anh đến.': 'Người đàn ông đến nơi đó.',
        '"Đêm hai mươi ba.': '"Vào đêm hai mươi ba.',
        'Đêm thứ hai mươi ba.': 'Đêm thứ hai mươi ba của hành trình.',
        # R62
        '"Tôi không nói. Tôi hai lăm': '"Tôi không nói. Người đàn ông mới hai lăm',
        '"Tôi gọi món Yến thích — cua hấp bia — bánh đa cua. Tôi đợi Yến ăn xong':
            '"Tôi gọi món Yến thích — cua hấp bia — bánh đa cua. Người đàn ông đợi Yến ăn xong',
        '"Tôi sốc. Tôi không nói gì.': '"Tôi sốc. Người đàn ông không nói gì.',
        'Em đã biết — từ năm thứ ba anh vào công ty — em thấy anh nhìn em mỗi sáng k':
            'Em đã biết — từ năm thứ ba anh vào công ty — cô gái thấy anh nhìn em mỗi sáng k',
        'Tôi không liên lạc. Tôi không gửi quà cưới.': 'Tôi không liên lạc. Người đàn ông không gửi quà cưới.',
        '"Tôi không đến đám tang Yến — tôi không phải gia đình — tôi không có vai tr':
            '"Tôi không đến đám tang Yến — tôi không phải gia đình — người đàn ông không có vai tr',
        'Tôi đem thư về Hải Phòng — về văn phòng công ty Hải Cảng — chính văn phòng':
            'Tôi đem thư về Hải Phòng — về văn phòng công ty Hải Cảng — người đàn ông đem về chính văn phòng',
    },
    24: {
        # R61
        'Đêm thứ hai mươi tư.': 'Đêm thứ hai mươi tư của hành trình.',
        'Bà lên xe.': 'Bà cụ khẽ lên xe.',
        'Bà ngồi yên.': 'Người bà ngồi yên.',
        'Bà lật vở.': 'Bà cụ lật vở.',
        'Bà quay đầu lại.': 'Người bà quay đầu lại.',
        '"Chị Lan không nói gì.': '"Người chị Lan không nói gì.',
        'Chị Lan không nhìn em.': 'Người chị Lan không nhìn em.',
        'Bà đến.': 'Bà cụ đến nơi đó.',
        'Đêm mưa.': 'Trời đêm mưa.',
        '"Đêm hai mươi tư.': '"Vào đêm hai mươi tư.',
        'Đêm thứ hai mươi tư.': 'Đêm thứ hai mươi tư của hành trình.',
        # R62
        '"Em ngồi nhà — biết em nói dối. Em xấu hổ với chính mình':
            '"Em ngồi nhà — biết em nói dối. Cô gái xấu hổ với chính mình',
        '"Em đến đám tang. Em quỳ bên quan tài Mai Anh.':
            '"Em đến đám tang. Cô gái quỳ bên quan tài Mai Anh.',
        '"Em nhớ. Em từ chối đỡ học phí Mai Anh': '"Em nhớ. Cô gái từ chối đỡ học phí Mai Anh',
    },
    25: {
        # R58
        'mẩu giấy vở học sinh với từng chữ "Cô giáo em..."':
            'mẩu giấy vở học sinh với nét bút "Cô giáo em..."',
        # R61
        'Đêm.': 'Trời đã về đêm.',
        'Đêm thứ hai mươi lăm.': 'Đêm thứ hai mươi lăm của hành trình.',
        'Anh lên bậc xe.': 'Người đàn ông lên bậc xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Đêm mưa.': 'Trời đêm mưa.',
        '"Anh là Khải Phong à?': '"Người đàn ông là Khải Phong à?',
        'Anh đến gấp."': 'Người đàn ông đến gấp."',
        '"Đêm hai mươi lăm.': '"Vào đêm hai mươi lăm.',
        'Đêm thứ hai mươi lăm.': 'Đêm thứ hai mươi lăm của hành trình.',
        'Mưa đã hết rồi.': 'Trời mưa đã hết hẳn.',
        # R62
        '"Tôi tự hào. Tôi nghĩ tôi khỏe': '"Tôi tự hào. Người đàn ông nghĩ tôi khỏe',
        '"Tôi sốc. Tôi không khóc trong phòng bác người.': '"Tôi sốc. Người đàn ông không khóc trong phòng bác.',
        'Tôi không leo cầu thang được — leo ba tầng phải nghỉ giữa. Tôi không chạy':
            'Tôi không leo cầu thang được — leo ba tầng phải nghỉ giữa. Người đàn ông không chạy',
        '"Tôi nhớ. Tôi đã không khám định kỳ': '"Tôi nhớ. Người đàn ông đã không khám định kỳ',
    },
}

def main():
    apply = '--apply' in sys.argv
    print(f"EP21-25 manual rewrite | Mode: {'APPLY' if apply else 'DRY-RUN'}")
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
        print(f"\nEP{n:02d}: {applied} / {len(skipped)} skipped")
        for s in skipped:
            print(f"  SKIP: {s}")
        if apply and applied:
            shutil.copy2(p, p.with_suffix('.md.bak.V_manual'))
            p.write_text(text, encoding='utf-8')
        total += applied
    print(f"\nTotal: {total}")

if __name__ == '__main__':
    main()
