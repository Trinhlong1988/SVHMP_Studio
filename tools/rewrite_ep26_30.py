"""SVHMP — Manual rewrite EP26-30."""
import shutil, sys
from pathlib import Path
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

EP_REWRITES = {
    26: {
        '"Bố im. Rồi': '"Bố im lặng. Rồi',
        'Bố tan ra.': 'Người bố tan ra.',
        'Đêm.': 'Trời đã về đêm.',
        'Đêm thứ hai mươi sáu.': 'Đêm thứ hai mươi sáu của hành trình.',
        'Anh vào xe.': 'Người đàn ông vào xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Anh Lâm về quê.': 'Người tên Lâm về quê.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        'Năm tốt nghiệp.': 'Năm em tốt nghiệp xong.',
        '"Đêm hai mươi sáu.': '"Vào đêm hai mươi sáu.',
        'Đêm thứ hai mươi sáu.': 'Đêm thứ hai mươi sáu của hành trình.',
        'Tôi không thi Kiến trúc. Tôi thi Kế toán Học viện Tài chính.':
            'Tôi không thi Kiến trúc. Người con thi Kế toán Học viện Tài chính.',
    },
    27: {
        'Hằng tan ra.': 'Người tên Hằng tan ra.',
        'Đêm thứ hai mươi bảy.': 'Đêm thứ hai mươi bảy của hành trình.',
        'Mưa rơi nhẹ nhàng.': 'Trời mưa rơi nhẹ nhàng.',
        'Cô bước lên xe.': 'Cô gái bước lên xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ nhẹ.',
        'Cô quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        '"Tối em quên gọi.': '"Vào tối em quên gọi.',
        "Anh xin báo em.'\"": "Người đàn ông xin báo em.'\"",
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới đường.',
        'Cô đến.': 'Cô gái đến nơi đó.',
        '"Đêm hai mươi bảy.': '"Vào đêm hai mươi bảy.',
        'Đêm thứ hai mươi bảy.': 'Đêm thứ hai mươi bảy của hành trình.',
        'Em sinh ở Phú Thọ — Vĩnh Lộc. Em sống Mỹ': 'Em sinh ở Phú Thọ — Vĩnh Lộc. Cô gái sống Hoa Kỳ',
        '"Em không viết dài sau. Em quên.': '"Em không viết dài sau. Cô gái quên hẳn.',
        '"Em sốc. Em không khóc trước chồng.': '"Em sốc. Cô gái không khóc trước chồng.',
        '"Em nhớ. Em hứa Hằng giúp khi cần': '"Em nhớ. Cô gái hứa Hằng giúp khi cần',
    },
    28: {
        '"Em đứng lặng. Em': '"Em đứng lặng yên. Em',
        '"Em im. Em': '"Em im lặng. Em',
        'Đêm thứ hai mươi tám.': 'Đêm thứ hai mươi tám của hành trình.',
        'Anh lên xe.': 'Người đàn ông lên xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Năm mươi lăm tuổi.': 'Anh năm mươi lăm tuổi rồi.',
        'Năm mươi ba tuổi.': 'Anh năm mươi ba tuổi rồi.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        'Anh đến.': 'Người đàn ông đến nơi đó.',
        'Anh chỉ tha qua Chúa.': 'Người đàn ông chỉ tha qua Chúa.',
        '"Đêm hai mươi tám.': '"Vào đêm hai mươi tám.',
        'Đêm thứ hai mươi tám.': 'Đêm thứ hai mươi tám của hành trình.',
        '"Em về bến — không thấy Hồng đón. Em đi bộ về nhà.':
            '"Em về bến — không thấy Hồng đón. Người đàn ông đi bộ về nhà.',
        '"Em đứng lặng yên. Em không la — không đánh — không nói.':
            '"Em đứng lặng yên. Người đàn ông không la — không đánh — không nói.',
        '"Em im lặng. Em nghĩ thầm.': '"Em im lặng. Người đàn ông nghĩ thầm.',
        'Em quyết — em đi tang Hồng. Em đến nhà thờ': 'Em quyết — em đi tang Hồng. Người đàn ông đến nhà thờ',
    },
    29: {
        'Nga tan ra.': 'Người tên Nga tan ra.',
        'Đêm thứ hai mươi chín.': 'Đêm thứ hai mươi chín của hành trình.',
        'Gió biển mặn.': 'Cơn gió biển mặn.',
        'Cô lên bậc xe.': 'Cô gái lên bậc xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ.',
        'Cô quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới đường.',
        'Cô đến quầy.': 'Cô gái đến bên quầy.',
        'Năm tốt nghiệp.': 'Năm em tốt nghiệp xong.',
        '"Đêm hai mươi chín.': '"Vào đêm hai mươi chín.',
        'Đêm thứ hai mươi chín.': 'Đêm thứ hai mươi chín của hành trình.',
        '"Em không đi khám. Em ngại.': '"Em không đi khám. Cô gái rất ngại.',
        '"Em đến tang em. Em quỳ bên quan tài Nga.':
            '"Em đến tang em. Cô gái quỳ bên quan tài Nga.',
        '"Em nhớ. Em không thử khám tủy cho Nga': '"Em nhớ. Cô gái không thử khám tủy cho Nga',
    },
    30: {
        'có từng chữ "2017"': 'có dòng chữ in chìm "2017"',
        'mẩu bằng — từng chữ "Khải Phong"': 'mẩu bằng — dòng chữ in chìm "Khải Phong"',
        '"Mẹ tôi im. Tôi': '"Mẹ tôi im lặng. Tôi',
        'Thầy tan ra.': 'Người thầy tan ra.',
        'Đêm thứ ba mươi.': 'Đêm thứ ba mươi của hành trình.',
        'Anh vào xe.': 'Người đàn ông vào xe.',
        'Anh ngồi bên Khải Phong.': 'Người đàn ông ngồi bên Khải Phong.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Năm mươi tám tuổi.': 'Em năm mươi tám tuổi rồi.',
        'Anh mỉm cười nhẹ.': 'Người đàn ông mỉm cười nhẹ.',
        'Anh đến.': 'Người đàn ông đến nơi.',
        '"Đêm ba mươi — milestone.': '"Vào đêm ba mươi — milestone.',
        'Đêm thứ ba mươi.': 'Đêm thứ ba mươi của hành trình.',
        'Mưa đã hết rồi.': 'Trời mưa đã hết hẳn.',
        '"Tôi học. Tôi tốt nghiệp THPT năm hai nghìn không trăm mười bảy':
            '"Tôi học. Người con tốt nghiệp THPT năm hai nghìn không trăm mười bảy',
        '"Tôi đi làm cho văn phòng kế toán nhỏ ở Hà Nội — lương khởi điểm tám triệu.':
            '"Người con đi làm cho văn phòng kế toán nhỏ ở Hà Nội — lương khởi điểm tám triệu.',
        '"Tôi sốc. Tôi không khóc trước vợ thầy': '"Tôi sốc. Người con không khóc trước vợ thầy',
    },
}

def main():
    apply = '--apply' in sys.argv
    total = 0
    for n, rewrites in EP_REWRITES.items():
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        text = p.read_text(encoding='utf-8')
        applied = 0
        for old, new in rewrites.items():
            c = text.count(old)
            if c:
                text = text.replace(old, new)
                applied += c
        if apply and applied:
            shutil.copy2(p, p.with_suffix('.md.bak'))
            p.write_text(text, encoding='utf-8')
        print(f"EP{n:02d}: {applied}")
        total += applied
    print(f"Total: {total}")

if __name__ == '__main__':
    main()
