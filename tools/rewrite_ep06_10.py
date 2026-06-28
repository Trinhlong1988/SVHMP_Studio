"""SVHMP L — Manual rewrite EP06-10 all R58/R60/R61/R62 violations."""
import shutil
import sys
from pathlib import Path

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

EP_REWRITES = {
    6: {
        # R60
        'Rất rất nhỏ.': 'Rất rất nhỏ nhẹ.',
        '"Cháu lặng.': '"Cháu im lặng một thoáng.',
        # R61
        'Đêm nay ba lần liền.': 'Vào đêm nay đếm được ba lần liền.',
        'Năm nay tám mươi mốt.': 'Cụ năm nay tám mươi mốt tuổi.',
        'Năm cháu nội ngoại."': 'Cụ có năm cháu nội ngoại."',
        'Đêm hai tám."': 'Vào đêm hai tám tháng Chạp."',
        'Lúc cụ mười tám tuổi.': 'Vào lúc cụ mười tám tuổi.',
        'Gió đêm khép vào.': 'Cơn gió đêm khép vào cửa.',
        'Trên ghế thứ tư trống.': 'Trên mặt ghế thứ tư trống.',
        'Đêm thứ sáu.': 'Đêm thứ sáu của hành trình.',
        'Đêm vẫn dài.': 'Đêm hôm nay vẫn còn dài.',
        # R62 anaphora 'Cụ về thăm. Cụ ôm em Nhi'
        'Cụ về thăm. Cụ ôm em Nhi lần đầu. Cụ khóc.': 'Cụ về thăm. Bà cụ ôm em Nhi lần đầu. Người bà cụ khẽ khóc.',
        'Cụ biết — cháu chưa bao giờ hỏi mẹ ruột. Cụ cũng không nhắc nữa.': 'Cụ biết — cháu chưa bao giờ hỏi mẹ ruột. Bà cụ cũng không nhắc nữa.',
    },
    7: {
        # R58: "từng chữ" → "nét bút" before quote, "nét chữ" before period
        'phong bao có viết hai từng chữ "Tặng mẹ"': 'phong bao có viết hai nét bút "Tặng mẹ"',
        'mặt phong bao có từng chữ "Tặng mẹ".': 'mặt phong bao có nét bút "Tặng mẹ".',
        'Có hai nét chữ.': 'Có hai dòng chữ in chìm.',
        'Mặt sau — hai từng chữ "Tặng mẹ" viết tay.': 'Mặt sau — hai nét bút "Tặng mẹ" viết tay.',
        # R60
        '"...quê nhà..." rồi tan.': '"...quê nhà..." rồi tan ra.',
        'Một hồi. Rồi tan ra.': 'Một hồi. Rồi tan ra ngoài gió.',
        # R61
        'Đêm ba mươi tháng Chạp.': 'Vào đêm ba mươi tháng Chạp.',
        'Đêm thứ bảy.': 'Đêm thứ bảy của hành trình.',
        'Năm nay hai mốt.': 'Em năm nay hai mốt tuổi.',
        'Anh đem theo.': 'Khải Phong đem theo bên mình.',
        'Anh đi tiếp.': 'Khải Phong bước đi tiếp.',
        'Đêm vẫn dài.\n\nMưa phùn vẫn lất phất.': 'Đêm hôm nay vẫn còn dài.\n\nTrời mưa phùn vẫn lất phất.',
        'Đêm vẫn lăn bánh.': 'Chuyến xe đêm vẫn lăn bánh.',
        # R62
        'Em gái đứng đón. Em không khóc nữa.': 'Em gái đứng đón. Cô em không khóc nữa.',
    },
    8: {
        # R58
        'ba cuộc lỡ.': 'ba cuộc gọi nhỡ.',
        # R60
        '"Bà ngồi đó..."': '"Bà ngồi ở đó..."',
        # R61
        'Đêm ba mươi tháng Chạp.': 'Vào đêm ba mươi tháng Chạp.',
        'Mưa lất phất.': 'Trời mưa lất phất.',
        'Đêm thứ tám.': 'Đêm thứ tám của hành trình.',
        'Năm lần liền sau.': 'Năm lần liền sau đó.',
        'Đêm thứ tám, năm lần.': 'Đêm thứ tám có năm lần như thế.',
        'Cô em đứng cổng đón.': 'Người cô em đứng cổng đón.',
        '"Bà nằm trong quan tài.': '"Người bà nằm trong quan tài.',
        'Bà chọn ông.': 'Bà cụ chọn ông.',
        'Bà bỏ nhà, theo ông.': 'Bà cụ bỏ nhà, theo ông.',
        'Bà nuôi hai thế hệ.': 'Bà cụ nuôi hai thế hệ.',
        'Cô em nấu hộ.': 'Người cô em nấu hộ.',
        'Bà ngồi cạnh nhìn.': 'Bà cụ ngồi cạnh nhìn.',
        'Anh sẽ không nhớ bà.': 'Em sẽ không nhớ bà nữa.',
        'Bà vẫn riêng của em."': 'Người bà vẫn riêng của em."',
        'Anh đi tiếp.': 'Khải Phong bước đi tiếp.',
        'Đêm vẫn dài.': 'Đêm hôm nay vẫn còn dài.',
        'Bà giữ trong túi áo.': 'Bà cụ giữ trong túi áo.',
        # R62
        'Em đang đi nhậu với bạn lớp. Em không bắt.': 'Em đang đi nhậu với bạn lớp. Cháu không bắt máy.',
        'Em sẽ ngồi cạnh ban thờ bà. Em sẽ gọi điện cho bà': 'Em sẽ ngồi cạnh ban thờ bà. Cháu sẽ gọi điện cho bà',
        'Em đi học bình thường. Em đi làm thêm.': 'Em đi học bình thường. Cháu đi làm thêm.',
    },
    9: {
        # R60
        '"Em quên rồi. Em': '"Em đã quên rồi. Em',
        # R61
        'Đêm thứ chín.': 'Đêm thứ chín của hành trình.',
        'Cô bước lên xe.': 'Cô gái bước lên xe.',
        'Cô áp băng lên ngực.': 'Cô gái áp băng lên ngực.',
        'Đêm thứ chín, sáu lần.': 'Đêm thứ chín có sáu lần như thế.',
        'Cô gái quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        'Năm nay ba mốt.': 'Em năm nay ba mốt tuổi.',
        "Bà chưa gặp chắt.'\"": "Bà cụ chưa gặp chắt.'\"",
        '"Bà bảo:': '"Người bà bảo:',
        "Bà còn khoẻ, không sao.'\"": "Bà cụ còn khoẻ, không sao.'\"",
        'Bà đã đi đêm trước."': 'Bà cụ đã đi đêm trước."',
        'Cô gái khẽ gật đầu.': 'Cô gái khẽ gật đầu một cái.',
        'Cô hỏi:': 'Cô gái hỏi:',
        'Cô lên đến hiên.': 'Cô gái lên đến hiên.',
        'Cô đặt băng lên máy.': 'Cô gái đặt băng lên máy.',
        'Cô bấm nút Play.': 'Cô gái bấm nút Play.',
        'Cô vẫn ngồi đó.': 'Cô gái vẫn ngồi đó.',
        'Đêm vẫn dài.\n\nSương núi vẫn dày.': 'Đêm hôm nay vẫn còn dài.\n\nLớp sương núi vẫn dày.',
        'Bà có vết sẹo đó.': 'Bà cụ có vết sẹo đó.',
        # R62
        'Em sẽ đem băng đến nhà sàn cũ của bà. Em sẽ ngồi trên hiên nhà': 'Em sẽ đem băng đến nhà sàn cũ của bà. Cháu sẽ ngồi trên hiên nhà',
        "Em không kể đủ. Em chỉ bảo: 'Em về quê thắp hương bà.": "Em không kể đủ. Cháu chỉ bảo: 'Em về quê thắp hương bà.",
    },
    10: {
        # R60
        '...quê nhà..." nữa.': '...quê nhà..." nữa rồi.',
        # R61
        'Đêm ba mươi tháng Chạp.\n\nSương đặc.': 'Vào đêm ba mươi tháng Chạp.\n\nLớp sương đặc đến nỗi không nhìn thấy gì.',
        'Đêm thứ mười.': 'Đêm thứ mười của hành trình.',
        'Đêm thứ mười, bảy lần.': 'Đêm thứ mười có bảy lần như thế.',
        '"Anh tên Việt.': '"Em tên Việt.',
        'Lúc anh mười sáu tuổi."': 'Vào lúc em mười sáu tuổi."',
        'Anh ở với bà.': 'Em ở với bà nội.',
        'Bà nằm phòng cấp cứu.': 'Bà nội nằm phòng cấp cứu.',
        'Cô anh đang ngồi ngoài.': 'Người cô đang ngồi ngoài.',
        '"Anh vào phòng.': '"Em vào trong phòng.',
        'Bà nằm trên giường.': 'Bà nội nằm trên giường.',
        'Anh ngồi xuống ghế.': 'Em ngồi xuống ghế.',
        'Bà nhìn anh.': 'Bà nội nhìn em.',
        'Anh ghé tai sát.': 'Em ghé tai sát lại.',
        "Bà thì thầm: 'Khăn tay...": "Bà nội thì thầm: 'Khăn tay...",
        '"Cô anh dìu anh ra.': '"Người cô dìu em ra ngoài.',
        '"Anh nhớ, bác."': '"Em nhớ, bác."',
        'Anh đứng đám tang cô.': 'Em đứng đám tang cô.',
        '"Anh muốn kể.': '"Em muốn kể.',
    },
}

def main():
    apply = '--apply' in sys.argv
    print(f"EP06-10 manual rewrite | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    total = 0
    for n, rewrites in EP_REWRITES.items():
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        text = p.read_text(encoding='utf-8')
        applied = 0
        skipped = []
        for old, new in rewrites.items():
            if old in text:
                text = text.replace(old, new, 1)
                applied += 1
            else:
                skipped.append(old[:60])
        print(f"\nEP{n:02d}: {applied}/{len(rewrites)} applied")
        for s in skipped:
            print(f"  SKIP: {s}")
        if apply and applied:
            shutil.copy2(p, p.with_suffix('.md.bak.L_manual'))
            p.write_text(text, encoding='utf-8')
        total += applied
    print(f"\nTotal: {total}")
    if apply:
        print("APPLIED")

if __name__ == '__main__':
    main()
