"""SVHMP S — Manual rewrite EP16-20 all R58/R60/R61/R62 violations."""
import shutil
import sys
from pathlib import Path

SVHMP = Path(__file__).resolve().parents[1]

EP_REWRITES = {
    16: {
        'Mẹ tan ra.': 'Người mẹ ấy tan ra.',
        'Quỳ thêm. Tụng rất nhỏ.': 'Quỳ thêm. Tụng rất khẽ khàng.',
        'Đêm.': 'Trời đã về đêm.',
        'Đêm thứ mười sáu.': 'Đêm thứ mười sáu của hành trình.',
        'Cô lên xe.': 'Cô gái khẽ lên xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ.',
        'Bà cụ khuất.': 'Bóng bà cụ khuất.',
        'Cô gái quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        'Năm giờ sáng lên.': 'Lúc năm giờ sáng lên.',
        '"Anh Hùng hiểu.': '"Người anh Hùng hiểu.',
        'Cô gái khẽ gật đầu.': 'Cô gái khẽ gật đầu một cái.',
        'Cô ôm chậu cúc.': 'Cô gái ôm chậu cúc.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới.',
        'Cô đến.': 'Cô gái đến nơi.',
        '"Đêm mười sáu.': '"Vào đêm mười sáu.',
        'Đêm thứ mười sáu.': 'Đêm thứ mười sáu của hành trình.',
        '"Em cãi mẹ. Em lớn tiếng': '"Em cãi mẹ. Cô con gái lớn tiếng',
        'Em chia tay anh hai tháng sau. Em không vì giận anh': 'Em chia tay anh hai tháng sau. Cô gái không vì giận anh',
    },
    17: {
        # R58 'lỡ' → 'không nghe được'
        'Cuộc gọi lỡ."': 'Cuộc gọi không nhận được."',
        'một cuộc gọi lỡ —': 'một cuộc gọi không nhận được —',
        'Toàn tan ra.': 'Người tên Toàn tan ra.',
        'Đêm thứ mười bảy.': 'Đêm thứ mười bảy của hành trình.',
        'Anh lên bậc xe.': 'Người đàn ông lên bậc xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh đặt USB lên đùi.': 'Người đàn ông đặt USB lên đùi.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Tối qua ở đó.': 'Vào tối qua ở đó.',
        'Anh quỳ.': 'Người đàn ông khẽ quỳ.',
        '"Đêm mười bảy.': '"Vào đêm mười bảy.',
        'Đêm thứ mười bảy.': 'Đêm thứ mười bảy của hành trình.',
        '"Tôi đọc tin. Tôi sốc': '"Tôi đọc tin. Người đàn ông sốc',
        '"Tôi sốc. Tôi không khóc.': '"Tôi sốc. Người đàn ông không khóc.',
        'Tôi không trách anh không xoay kịp tiền. Tôi biết anh bận.': 'Tôi không trách anh không xoay kịp tiền. Người đàn ông biết anh bận.',
    },
    18: {
        # R58 chữ
        'biển "Cà phê Lâm" đã mòn nét chữ.': 'biển "Cà phê Lâm" đã mòn nét bút.',
        'chỉ nhìn nét nét chữ.': 'chỉ nhìn từng nét bút.',
        # R60
        '"Mẹ em im. Pha': '"Mẹ em im lặng. Pha',
        'Khang tan ra.': 'Người tên Khang tan ra.',
        # R61
        'Đêm thứ mười tám.': 'Đêm thứ mười tám của hành trình.',
        'Cô vào xe.': 'Cô gái khẽ vào xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ.',
        'Cô gái quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        'Anh chơi ghi-ta tốt.': 'Anh ấy chơi ghi-ta tốt.',
        "Anh sẽ chia tay em.'\"": "Anh ấy sẽ chia tay em.'\"",
        'Cô gấp thư.': 'Cô gái gấp thư.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới.',
        'Cô lấy thư ra.': 'Cô gái lấy thư ra.',
        '"Đêm mười tám.': '"Vào đêm mười tám.',
        'Đêm thứ mười tám.': 'Đêm thứ mười tám của hành trình.',
        # R62
        '"Em không đọc thư anh trong một tháng. Em sợ': '"Em không đọc thư anh trong một tháng. Cô gái sợ',
        "Anh không trách. Anh chỉ viết: 'Trang ơi": "Anh không trách. Người anh chỉ viết: 'Trang ơi",
        '"Em sốc. Em không tin.': '"Em sốc. Cô gái không tin.',
        '"Em quỳ bên quan tài. Em xin lỗi anh': '"Em quỳ bên quan tài. Cô gái xin lỗi anh',
        '"Em nhớ. Em chia tay anh Khang vì mẹ': '"Em nhớ. Cô gái chia tay anh Khang vì mẹ',
    },
    19: {
        'hàng từng chữ "Nghĩa trang Đông Hộ': 'hàng nét bút "Nghĩa trang Đông Hộ',
        'Mai tan ra.': 'Người tên Mai tan ra.',
        'Đêm thứ mười chín.': 'Đêm thứ mười chín của hành trình.',
        'Cô bước lên xe.': 'Cô gái bước lên xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô vuốt một cánh cúc.': 'Cô gái vuốt một cánh cúc.',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ.',
        'Cô gái quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        'Năm mươi tuổi.': 'Cô năm mươi tuổi.',
        'Cô gái khẽ gật đầu.': 'Cô gái khẽ gật đầu một cái.',
        'Cô đỡ vòng cúc.': 'Cô gái đỡ vòng cúc.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới.',
        'Cô đến.': 'Cô gái đến nơi.',
        '"Đêm mười chín.': '"Vào đêm mười chín.',
        'Đêm thứ mười chín.': 'Đêm thứ mười chín của hành trình.',
        'Đêm này hoàn thành.': 'Đêm này đã hoàn thành.',
        '"Em quỳ bên Mai. Em xin lỗi': '"Em quỳ bên Mai. Cô gái xin lỗi',
        'Em ngại. Em ngại nhìn Mai': 'Em ngại. Cô gái ngại nhìn Mai',
        '"Em sốc. Em không trả lời.': '"Em sốc. Cô gái không trả lời.',
        '"Em nhớ. Em không đến với Mai': '"Em nhớ. Cô gái không đến với Mai',
    },
    20: {
        # R58 ngõ + lỡ
        'Bên ngõ — Hoài xuất hiện': 'Bên hẻm — Hoài xuất hiện',
        'đi xuống ngõ.': 'đi xuống hẻm.',
        'Khải Phong lỡ — chưa nhớ.': 'Khải Phong nhỡ mất — chưa nhớ.',
        'Hoài tan ra.': 'Người tên Hoài tan ra.',
        # R61
        'Đêm thứ hai mươi.': 'Đêm thứ hai mươi của hành trình.',
        'Anh lên xe.': 'Người đàn ông lên xe.',
        'Anh ngồi bên Khải Phong.': 'Người đàn ông ngồi bên Khải Phong.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        "Anh chúc em sống vui.'\"": "Người đàn ông chúc em sống vui.'\"",
        'Đêm thứ hai mươi.': 'Đêm thứ hai mươi của hành trình.',
        'Đêm sau — chưa biết.': 'Đêm sau đó — chưa biết.',
        'Mưa đã ngớt.': 'Trời mưa đã ngớt.',
        # R62
        '"Tôi đọc tin. Tôi không sốc.': '"Tôi đọc tin. Người đàn ông không sốc.',
        '"Tôi cảm thấy — tôi đã quên Hoài vì sự nghiệp. Tôi đã có sự nghiệp.': '"Tôi cảm thấy — tôi đã quên Hoài vì sự nghiệp. Người đàn ông đã có sự nghiệp.',
        '"Tôi nhớ. Tôi quên người yêu vì lương.': '"Tôi nhớ. Người đàn ông quên người yêu vì lương.',
    },
}

def main():
    apply = '--apply' in sys.argv
    print(f"EP16-20 manual rewrite | Mode: {'APPLY' if apply else 'DRY-RUN'}")
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
            shutil.copy2(p, p.with_suffix('.md.bak.S_manual'))
            p.write_text(text, encoding='utf-8')
        total += applied
    print(f"\nTotal: {total}")

if __name__ == '__main__':
    main()
