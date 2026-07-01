"""SVHMP — Manual rewrite EP46-50 (EP50 milestone CLIMAX)."""
import shutil, sys
from pathlib import Path
SVHMP = Path(__file__).resolve().parents[1]

EP_REWRITES = {
    46: {
        'Bin tan ra.': 'Người tên Bin tan đi.',
        'Đêm.': 'Trời đã về đêm.',
        'Đêm thứ bốn mươi sáu.': 'Đêm thứ bốn mươi sáu của hành trình.',
        'Mưa rải nhẹ nhàng.': 'Trời mưa rải nhẹ nhàng.',
        'Bà vào xe.': 'Bà cụ khẽ vào xe.',
        'Bà ngồi yên.': 'Bà cụ ngồi yên một lát.',
        'Bà nói rất nhỏ.': 'Bà cụ nói rất nhỏ nhẹ.',
        'Bà quay đầu lại.': 'Bà cụ khẽ quay đầu lại.',
        'Bà Hảo gật.': 'Bà cụ Hảo khẽ gật đầu.',
        'Bà Hảo ôm túi cát.': 'Bà cụ Hảo ôm túi cát.',
        'Bà bước xuống dưới.': 'Bà cụ bước xuống dưới đường.',
        'Bà đến bục thờ.': 'Bà cụ đến bên bục thờ.',
        'Bà Hảo ngẩng đầu.': 'Bà cụ Hảo ngẩng đầu lên.',
        '"Đêm bốn mươi sáu.': '"Vào đêm bốn mươi sáu.',
        'Anh chỉ ngại.': 'Em chỉ rất ngại.',
        '"Em đến bãi biển. Em đã được kéo lên': '"Em đến bãi biển. Cô bé đã được kéo lên',
        '"Em quỳ bên thân em — em không khóc trước người. Em vuốt tóc em một lúc.':
            '"Em quỳ bên thân em — em không khóc trước người. Bà cụ vuốt tóc em một lúc.',
        '"Em sống một mình ở quê. Em không có cháu khác.':
            '"Em sống một mình ở quê. Bà cụ không có cháu khác.',
        '"Em nhớ. Em hứa Bin đem em ra biển tháng sáu':
            '"Em nhớ. Bà cụ hứa Bin đem em ra biển tháng sáu',
    },
    47: {
        'Khoa tan ra.': 'Người tên Khoa tan đi.',
        'Đêm thứ bốn mươi bảy.': 'Đêm thứ bốn mươi bảy của hành trình.',
        'Cô bước lên xe.': 'Cô gái bước lên xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ.',
        'Cô quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        '"Đêm em đi ngủ.': '"Vào đêm em đi ngủ.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới đường.',
        'Cô đến.': 'Cô gái đến nơi đó.',
        '"Đêm bốn mươi bảy.': '"Vào đêm bốn mươi bảy.',
        'Anh ăn xong.': 'Em ăn xong rồi.',
        'Anh đem nhẫn Hạ Vy.': 'Khải Phong đem nhẫn Hạ Vy.',
        'Anh chụp ảnh.': 'Em chụp ảnh kỉ niệm.',
        'Anh đem về Việt Nam.': 'Khải Phong đem về Việt Nam.',
        '"Em sờ — em không thở. Em lạnh — đã đi mấy giờ.':
            '"Em sờ — em không thở. Cô gái lạnh — đã đi mấy giờ.',
        '"Em nhớ. Em hứa đi Hàn Quốc trăng mật với em':
            '"Em nhớ. Cô gái hứa đi Hàn Quốc trăng mật với em',
        'Em không đùa. Em tin em sẽ làm thật.':
            'Em không đùa. Cô gái tin em sẽ làm thật.',
        'Anh không đặt vé Hàn Quốc — anh chỉ hứa miệng. Anh không có vé giấy treo':
            'Anh không đặt vé Hàn Quốc — anh chỉ hứa miệng. Người đàn ông không có vé giấy treo',
        'Anh sẽ đi Hàn Quốc một mình. Anh đem nhẫn Hạ Vy.':
            'Anh sẽ đi Hàn Quốc một mình. Người đàn ông đem nhẫn Hạ Vy.',
        'Anh vẫn đi làm văn phòng kiến trúc Khâm Thiên. Anh không đi nước ngoài.':
            'Anh vẫn đi làm văn phòng kiến trúc Khâm Thiên. Người đàn ông không đi nước ngoài.',
        'Anh vẫn ngủ một mình phố Nguyễn Trãi. Anh không nhớ ngày đó.':
            'Anh vẫn ngủ một mình phố Nguyễn Trãi. Người đàn ông không nhớ ngày đó.',
    },
    48: {
        'Phong tan ra.': 'Người tên Phong tan đi.',
        'Đêm thứ bốn mươi tám.': 'Đêm thứ bốn mươi tám của hành trình.',
        'Anh lên xe.': 'Người đàn ông lên xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        '"Đêm bốn mươi tám.': '"Vào đêm bốn mươi tám.',
        '"Em ra trường năm em hai mươi mốt. Em đi dạy âm nhạc':
            '"Em ra trường năm em hai mươi mốt. Cô gái đi dạy âm nhạc',
        '"Em không nhắc lời hứa đàn. Em không hỏi.':
            '"Em không nhắc lời hứa đàn. Cô gái không hỏi.',
        '"Em mất ba năm sau chẩn đoán. Em đến tang em ở Sài Gòn.':
            '"Em mất ba năm sau chẩn đoán. Cô gái đến tang em ở Sài Gòn.',
        'Em hứa em đàn mười lăm năm — em quên — em đến muộn ba năm sau em phát hiện':
            'Em hứa em đàn mười lăm năm — em quên — cô gái đến muộn ba năm sau em phát hiện',
        'Anh sẽ đặt vé bay sau dự cưới anh xong — anh sẽ bay từ Sài Gòn về Hà Nội':
            'Anh sẽ đặt vé bay sau dự cưới anh xong — người đàn ông sẽ bay từ Sài Gòn về Hà Nội',
        'Anh đã quyết — anh sẽ đi Hàn Quốc một mình sau dự cưới Hạ Nhi. Anh sẽ đặt':
            'Anh đã quyết — anh sẽ đi Hàn Quốc một mình sau dự cưới Hạ Nhi. Người đàn ông sẽ đặt',
    },
    49: {
        'Vân tan ra.': 'Người tên Vân tan đi.',
        'Đêm thứ bốn mươi chín.': 'Đêm thứ bốn mươi chín của hành trình.',
        'Mưa rơi nhẹ nhàng.': 'Trời mưa rơi nhẹ nhàng.',
        'Cô lên bậc xe.': 'Cô gái lên bậc xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ.',
        'Cô quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới đường.',
        'Cô đến.': 'Cô gái đến nơi đó.',
        'Anh đã giữ lời hứa.': 'Em đã giữ lời hứa rồi.',
        '"Đêm bốn mươi chín.': '"Vào đêm bốn mươi chín.',
        'Anh sống lặng yên.': 'Em sống lặng yên một mình.',
        'Anh cất cẩn thận.': 'Em cất giữ cẩn thận.',
        '"Em hai mươi bảy tuổi lúc đó. Em đi làm về tối — mưa rất to.':
            '"Em hai mươi bảy tuổi lúc đó. Cô gái đi làm về tối — mưa rất to.',
        "\"Em dừng xe. Em hỏi: 'Em ơi em có sao không?":
            "\"Em dừng xe. Cô gái hỏi: 'Em ơi em có sao không?",
        '"Em đem em về phòng trọ em ở Sóc Trăng. Em pha nước nóng':
            '"Em đem em về phòng trọ em ở Sóc Trăng. Cô gái pha nước nóng',
        '"Em qua thăm em hai tháng — mỗi tuần một lần. Em đem cơm':
            '"Em qua thăm em hai tháng — mỗi tuần một lần. Cô gái đem cơm',
        '"Em đến nhà tang — em quỳ bên quan tài em. Em không có gia đình đến tang.':
            '"Em đến nhà tang — em quỳ bên quan tài em. Cô gái không có gia đình đến tang.',
        '"Em nhớ. Em đỡ em hai tháng — em bỏ em ba tuần':
            '"Em nhớ. Cô gái đỡ em hai tháng — em bỏ em ba tuần',
        'Anh chỉ đi làm — về phòng — ngủ. Anh không đỡ ai':
            'Anh chỉ đi làm — về phòng — ngủ. Người đàn ông không đỡ ai',
    },
    50: {
        '"Anh sẽ đi. Anh': '"Em sẽ đi. Em',
        'Khải Phong gật. "Anh sẽ đi. Anh': 'Khải Phong gật. "Em sẽ đi. Em',
        'Đêm thứ năm mươi.': 'Đêm thứ năm mươi của hành trình.',
        'Anh gái Hạ Vy.': 'Người chị gái Hạ Vy.',
        '"Anh Khải Phong.': '"Người tên Khải Phong.',
        'Anh nói tiếp:': 'Người đàn ông nói tiếp:',
        '"Chị..."': '"Chị Hạ Nhi ơi..."',
        '"Anh sẽ đi.': '"Em sẽ đi.',
        'Anh đến — đủ."': 'Người đàn ông đến — đủ rồi."',
        '"Anh cầm.': '"Em cầm lấy.',
        'Chị em đẹp.': 'Chị em đẹp lắm.',
        'Anh mỉm cười.': 'Em mỉm cười nhẹ.',
        'Anh vẫy tay một lần.': 'Em vẫy tay một lần.',
        'Năm mươi vật.': 'Có năm mươi vật.',
        'Năm mươi đêm.': 'Có năm mươi đêm.',
        'Năm mươi câu chuyện.': 'Có năm mươi câu chuyện.',
        'Đêm năm mươi đặc biệt:': 'Vào đêm năm mươi đặc biệt:',
        'Mưa đã hết rồi.': 'Trời mưa đã hết hẳn.',
        'Em hai mươi tư tuổi. Em ở Sài Gòn.': 'Em hai mươi tư tuổi. Cô gái ở Sài Gòn.',
        '"Anh sẽ đi. Anh xin lỗi em không trả lời.': '"Em sẽ đi. Người đàn ông xin lỗi em không trả lời.',
        '"Anh sẽ đi. Anh sẽ ngồi cùng bàn bố em.': '"Em sẽ đi. Người đàn ông sẽ ngồi cùng bàn bố em.',
        'Anh nhìn Khải Phong qua cửa sổ. Anh mỉm cười.': 'Anh nhìn Khải Phong qua cửa sổ. Người tài xế mỉm cười.',
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
