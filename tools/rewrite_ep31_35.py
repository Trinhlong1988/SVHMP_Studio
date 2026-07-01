"""SVHMP — Manual rewrite EP31-35."""
import shutil, sys
from pathlib import Path
SVHMP = Path(__file__).resolve().parents[1]

EP_REWRITES = {
    31: {
        'gỗ mòn nét chữ.': 'gỗ mòn nét bút.',
        'em chăm chưa kỹ': 'em chăm chưa kỹ càng',
        'Mẹ tan ra.': 'Người mẹ tan ra.',
        'Mưa rất to. Đêm': 'Mưa rất to lớn. Đêm',
        'Sương lất phất.': 'Trời sương lất phất.',
        'Đêm thứ ba mươi mốt.': 'Đêm thứ ba mươi mốt của hành trình.',
        'Bà bước lên xe.': 'Bà cụ bước lên xe.',
        'Bà ngồi yên.': 'Bà cụ ngồi yên.',
        'Bà nói rất nhỏ.': 'Bà cụ nói rất nhỏ.',
        'Bà quay đầu lại.': 'Bà cụ quay đầu lại.',
        'Năm mươi lăm tuổi.': 'Bà năm mươi lăm tuổi rồi.',
        'Bà bước xuống dưới.': 'Bà cụ bước xuống dưới đường.',
        'Bà đến.': 'Bà cụ đến nơi đó.',
        'Năm vật cúc trong túi.': 'Có năm vật cúc trong túi.',
        'Đêm.': 'Trời đã về đêm.',
        'Ngày bao nhiêu?': 'Ngày bao nhiêu rồi nhỉ?',
        'Ngày mười hai.': 'Ngày mười hai tháng tư.',
        '"Đêm ba mươi mốt.': '"Vào đêm ba mươi mốt.',
        'Đêm thứ ba mươi mốt.': 'Đêm thứ ba mươi mốt của hành trình.',
        '"Em nhớ. Em không kịp nói lời yêu mẹ rõ trước khi mẹ đi.':
            '"Em nhớ. Cô gái không kịp nói lời yêu mẹ rõ trước khi mẹ đi.',
    },
    32: {
        'Nhung tan ra.': 'Người tên Nhung tan ra.',
        'Đêm vừa khuya.': 'Trời đêm vừa khuya.',
        'Đêm thứ ba mươi hai.': 'Đêm thứ ba mươi hai của hành trình.',
        'Anh lên xe.': 'Người đàn ông lên xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        'Anh đến mộ Nhung.': 'Người đàn ông đến mộ Nhung.',
        '"Đêm ba mươi hai.': '"Vào đêm ba mươi hai.',
        'Đêm thứ ba mươi hai.': 'Đêm thứ ba mươi hai của hành trình.',
        '"Em quyết em sẽ đan tặng tôi một chiếc chăn mới — chăn cưới mười năm. Em':
            '"Em quyết em sẽ đan tặng tôi một chiếc chăn mới — chăn cưới mười năm. Vợ tôi',
        '"Tôi dậy bảy giờ. Tôi ra phòng khách.': '"Tôi dậy bảy giờ. Người đàn ông ra phòng khách.',
    },
    33: {
        'cây phượng vĩ —': 'cây phượng vĩ đỏ —',
        'có từng chữ "Cát Linh-Hà Đông"': 'có nét bút "Cát Linh-Hà Đông"',
        'Quỳnh tan ra.': 'Người tên Quỳnh tan ra.',
        'Mưa đã rơi từ chiều.': 'Trời mưa đã rơi từ chiều.',
        'Đêm thứ ba mươi ba.': 'Đêm thứ ba mươi ba của hành trình.',
        'Cô lên bậc xe.': 'Cô gái lên bậc xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô đặt vé lên đùi.': 'Cô gái đặt vé lên đùi.',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ.',
        'Cô ghế chín quay đầu.': 'Cô gái ghế chín quay đầu.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới đường.',
        'Cô đến.': 'Cô gái đến nơi đó.',
        '"Đêm ba mươi ba.': '"Vào đêm ba mươi ba.',
        'Đêm thứ ba mươi ba.': 'Đêm thứ ba mươi ba của hành trình.',
        'Em bận. Em không ra ngoài.': 'Em bận. Cô gái không ra ngoài.',
        "\"Em sốc. Em đáp ngay: 'Quỳnh ơi em đến Hà Nội": "\"Em sốc. Cô gái đáp ngay: 'Quỳnh ơi em đến Hà Nội",
        '"Em đem vé về Thái Bình — em đến tang em. Em định đặt vé vào quan tài em.':
            '"Em đem vé về Thái Bình — em đến tang em. Cô gái định đặt vé vào quan tài em.',
        '"Em nhớ. Em hứa em đi tàu điện ba năm': '"Em nhớ. Cô gái hứa em đi tàu điện ba năm',
        '"Em định — sang năm em sẽ đem một bạn khác đi tàu điện. Em quen một cô bạ':
            '"Em định — sang năm em sẽ đem một bạn khác đi tàu điện. Cô gái quen một cô bạ',
    },
    34: {
        'Bác tan ra.': 'Người bác tan ra.',
        'Đêm thứ ba mươi tư.': 'Đêm thứ ba mươi tư của hành trình.',
        'Anh vào xe.': 'Người đàn ông vào xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Năm mươi tuổi.': 'Em năm mươi tuổi rồi.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        'Anh đến.': 'Người đàn ông đến nơi đó.',
        'Ngày đầu tiên.': 'Vào ngày đầu tiên.',
        '"Đêm ba mươi tư.': '"Vào đêm ba mươi tư.',
        'Đêm thứ ba mươi tư.': 'Đêm thứ ba mươi tư của hành trình.',
    },
    35: {
        'Đêm.': 'Trời đã về đêm.',
        'Đêm thứ ba mươi lăm.': 'Đêm thứ ba mươi lăm của hành trình.',
        'Anh bước lên xe.': 'Người đàn ông bước lên xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        'Anh đến.': 'Người đàn ông đến nơi đó.',
        '"Đêm ba mươi lăm.': '"Vào đêm ba mươi lăm.',
        'Đêm thứ ba mươi lăm.': 'Đêm thứ ba mươi lăm của hành trình.',
        '"Tôi rải hồ sơ năm công ty — không công ty nào nhận. Tôi không có gia đìn':
            '"Tôi rải hồ sơ năm công ty — không công ty nào nhận. Người đàn ông không có gia đìn',
        '"Tôi về phòng trọ — đêm — ngồi trước gương treo tường — nhìn mình. Tôi th':
            '"Tôi về phòng trọ — đêm — ngồi trước gương treo tường — nhìn mình. Người đàn ông th',
        "\"Tôi nghĩ: 'Tôi hai sáu. Tôi còn nhiều năm.":
            "\"Tôi nghĩ: 'Tôi hai sáu. Người đàn ông còn nhiều năm.",
        '"Tôi đặt mảnh gương xuống. Tôi không cứa.': '"Tôi đặt mảnh gương xuống. Người đàn ông không cứa.',
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
