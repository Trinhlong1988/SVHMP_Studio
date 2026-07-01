"""SVHMP — Manual rewrite EP36-40 (EP40 milestone)."""
import shutil, sys
from pathlib import Path
SVHMP = Path(__file__).resolve().parents[1]

EP_REWRITES = {
    36: {
        'Khóc rất to. Bố': 'Khóc rất to lớn. Bố',
        'Đêm.': 'Trời đã về đêm.',
        'Đêm thứ ba mươi sáu.': 'Đêm thứ ba mươi sáu của hành trình.',
        'Anh lên xe.': 'Người đàn ông lên xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Anh đến.': 'Người đàn ông đến nơi đó.',
        '"Đêm ba mươi sáu.': '"Vào đêm ba mươi sáu.',
        'Đêm thứ ba mươi sáu.': 'Đêm thứ ba mươi sáu của hành trình.',
        'Tôi cầm. Tôi không nói gì.': 'Tôi cầm lấy. Người đàn ông không nói gì.',
    },
    37: {
        'xen kẽ.': 'xen kẽ nhau.',
        'Đêm thứ ba mươi bảy.': 'Đêm thứ ba mươi bảy của hành trình.',
        'Mưa đã ngớt.': 'Trời mưa đã ngớt.',
        'Cô lên bậc xe.': 'Cô gái lên bậc xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ.',
        'Cô quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới đường.',
        'Cô đến.': 'Cô gái đến nơi đó.',
        '"Đêm ba mươi bảy.': '"Vào đêm ba mươi bảy.',
        'Đêm thứ ba mươi bảy.': 'Đêm thứ ba mươi bảy của hành trình.',
        '"Em dọn dần — sáu tháng. Em đem quần áo em về Bình Định gửi mẹ em.':
            '"Em dọn dần — sáu tháng. Cô gái đem quần áo em về Bình Định gửi mẹ em.',
        '"Em cũng quyết — em sẽ chuyển nhà. Em bán phòng trọ': '"Em cũng quyết — em sẽ chuyển nhà. Cô gái bán phòng trọ',
        '"Em không tái hôn ngay. Em ba lăm hai': '"Em không tái hôn ngay. Cô gái ba lăm hai',
        '"Em nhớ. Em đi xe máy phố Huế một mình tối thứ ba': '"Em nhớ. Cô gái đi xe máy phố Huế một mình tối thứ ba',
    },
    38: {
        'Đêm thứ ba mươi tám.': 'Đêm thứ ba mươi tám của hành trình.',
        'Mưa rải nhẹ nhàng.': 'Trời mưa rải nhẹ nhàng.',
        'Anh vào xe.': 'Người đàn ông vào xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        'Anh đến.\n\nAnh đặt tiền cước.': 'Người đàn ông đến nơi đó.\n\nNgười đàn ông đặt tiền cước.',
        '"Đêm ba mươi tám.': '"Vào đêm ba mươi tám.',
        'Đêm thứ ba mươi tám.': 'Đêm thứ ba mươi tám của hành trình.',
        '"Tôi nghĩ về hộp quà em hai tháng. Tôi quyết': '"Tôi nghĩ về hộp quà em hai tháng. Người đàn ông quyết',
        '"Tôi sống tiếp. Tôi học cấp ba xong': '"Tôi sống tiếp. Người đàn ông học cấp ba xong',
        '"Tôi nhớ. Tôi hứa tặng Lan hộp quà sinh nhật mười tám': '"Tôi nhớ. Người đàn ông hứa tặng Lan hộp quà sinh nhật mười tám',
    },
    39: {
        'Đêm thứ ba mươi chín.': 'Đêm thứ ba mươi chín của hành trình.',
        'Bà bước lên xe.': 'Bà cụ bước lên xe.',
        'Bà ngồi yên.': 'Bà cụ ngồi yên.',
        'Bà nói rất nhỏ.': 'Bà cụ nói rất nhỏ.',
        'Bà quay đầu lại.': 'Bà cụ quay đầu lại.',
        'Năm mươi lăm tuổi.': 'Em năm mươi lăm tuổi rồi.',
        '"Năm tám — em bận.': '"Vào năm tám — em bận.',
        'Bà bước xuống dưới.': 'Bà cụ bước xuống dưới.',
        'Bà đến.': 'Bà cụ đến nơi đó.',
        '"Đêm ba mươi chín.': '"Vào đêm ba mươi chín.',
        'Đêm thứ ba mươi chín.': 'Đêm thứ ba mươi chín của hành trình.',
        '"Em sốc. Em đã không đem cơm ba tuần liên tiếp.':
            '"Em sốc. Cô gái đã không đem cơm ba tuần liên tiếp.',
        '"Em đến đám tang. Em quỳ bên quan tài bà.': '"Em đến đám tang. Cô gái quỳ bên quan tài bà.',
        '"Em nhớ. Em hứa đem cơm cho bà Trinh — em bỏ ba tuần': '"Em nhớ. Cô gái hứa đem cơm cho bà Trinh — em bỏ ba tuần',
        'Anh Hải là đồng nghiệp Hạ Vy. Anh quen Hạ Vy qua công việc.':
            'Anh Hải là đồng nghiệp Hạ Vy. Người tên Hải quen Hạ Vy qua công việc.',
    },
    40: {
        'Đêm thứ bốn mươi.': 'Đêm thứ bốn mươi của hành trình.',
        'Anh lên xe.': 'Người đàn ông lên xe.',
        'Anh ngồi bên Khải Phong.': 'Người đàn ông ngồi bên Khải Phong.',
        'Anh quay sang Khải Phong.': 'Người đàn ông quay sang Khải Phong.',
        'Anh có nhớ em không?"': 'Người đàn ông có nhớ em không?"',
        'Anh cảm ơn em.': 'Người đàn ông cảm ơn em.',
        '"Đêm bốn mươi — milestone.': '"Vào đêm bốn mươi — milestone.',
        'Đêm thứ bốn mươi.': 'Đêm thứ bốn mươi của hành trình.',
        'Anh gái Hạ Nhi đến.': 'Người anh gái Hạ Nhi đến.',
        '"Em hét — em không kịp can. Em chạy xe máy đến': '"Em hét — em không kịp can. Cô gái chạy xe máy đến',
        '"Em đưa chị vào bệnh viện Bạch Mai. Em đi cùng xe cấp cứu': '"Em đưa chị vào bệnh viện Bạch Mai. Cô gái đi cùng xe cấp cứu',
        'Anh cảm ơn em. Anh không hỏi tên em.': 'Người đàn ông cảm ơn em. Anh không hỏi tên em.',
        '"Em ngồi ngoài cùng anh — em không nói gì. Em không có quyền':
            '"Em ngồi ngoài cùng anh — em không nói gì. Cô gái không có quyền',
        '"Em làm tiếp Mộc Hà sáu năm sau. Em lên kiến trúc sư chính.':
            '"Em làm tiếp Mộc Hà sáu năm sau. Cô gái lên kiến trúc sư chính.',
        '"Em tìm văn phòng anh. Em đến — không gặp anh hôm đầu.':
            '"Em tìm văn phòng anh. Cô gái đến — không gặp anh hôm đầu.',
        '"Em nhớ. Em đã gặp anh đêm Bạch Mai.': '"Em nhớ. Cô gái đã gặp anh đêm Bạch Mai.',
        'Em đã hồi phục — em không cần giữ cuộn nữa. Em gặp anh đêm nay':
            'Em đã hồi phục — em không cần giữ cuộn nữa. Cô gái gặp anh đêm nay',
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
