"""SVHMP K — Manual rewrite EP02-05 all R58/R60/R61 violations.

Per-context rewrite từng EP riêng để giữ narrative meaning.
"""
import shutil
from pathlib import Path

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# Map: ep_num → {old: new}
EP_REWRITES = {
    2: {
        # R58: chữ EOL — "từng chữ" pattern fix
        'Có từng chữ "...quê nhà..."': 'Có từng nét chữ "...quê nhà..."',
        # R60: short EOL
        'Mắt rất to.': 'Mắt cô gái rất to tròn.',
        'Rất rất nhỏ.': 'Rất rất nhỏ nhẹ.',
        '"Con quỳ xuống.': '"Con đã quỳ xuống.',
        'Đến sáng lên.': 'Đến lúc trời sáng lên.',
        # R61: short START
        'Đêm hai tám tháng Chạp.': 'Vào đêm hai tám tháng Chạp.',
        'Cô nhìn ra cửa kính.': 'Cô gái nhìn ra cửa kính xe.',
        'Cô khẽ thở ra.': 'Cô gái khẽ thở ra một hơi.',
        'Cô gái đang đan tiếp.': 'Cô gái vẫn đang đan tiếp.',
        'Đêm ba mươi.': 'Vào đêm ba mươi tháng Chạp.',
        'Cô gái dừng. Khẽ thở ra một hơi.': 'Cô gái dừng đan. Khẽ thở ra một hơi.',
        'Cô gái đứng dậy.': 'Cô gái từ từ đứng dậy.',
        'Cô gật đầu nhẹ.': 'Cô gái khẽ gật đầu nhẹ.',
    },
    3: {
        # R58
        'Có từng chữ "đường dài".': 'Có từng nét chữ "đường dài".',
        # R60
        '"Mẹ luộc rồi..."': '"Mẹ đã luộc rồi..."',
        'Không tan ra.': 'Không tan ra ngoài.',
        # R61
        'Đêm ba mươi tháng Chạp.': 'Vào đêm ba mươi tháng Chạp.',
        'Trong xe lạnh buốt.': 'Bên trong xe lạnh buốt.',
        'Anh đang qua đèo.': 'Anh ấy đang vượt qua đèo.',
        "Anh sẽ về kịp.'": "Anh ấy sẽ về kịp.'",
        'Anh ta ngừng.': 'Người đàn ông ngừng lại.',
        'Anh ta nói tiếp.': 'Người đàn ông nói tiếp.',
        'Anh ta dừng.': 'Người đàn ông dừng lại.',
        'Anh đi ra cửa xe.': 'Người đàn ông đi ra cửa xe.',
        'Anh gật đầu nhẹ.': 'Người đàn ông khẽ gật đầu.',
        'Đêm vẫn dài.': 'Đêm hôm ấy vẫn còn dài.',
    },
    4: {
        # R58: 8 "từng chữ" instances — fix "từng" → "nét" để hết tilde EOL
        'Mặt trước in từng chữ "An Khang Thịnh Vượng"': 'Mặt trước in dòng chữ "An Khang Thịnh Vượng"',
        'Chỉ có hai từng chữ "Cháu Diệu"': 'Chỉ có hai dòng chữ "Cháu Diệu"',
        'phong bao có từng chữ "Cháu Diệu"': 'phong bao có dòng chữ "Cháu Diệu"',
        'phong bao có hai từng chữ "Cháu Diệu"': 'phong bao có hai dòng chữ "Cháu Diệu"',
        "Tay vuốt nhẹ từng chữ \"Cháu Diệu\"": "Tay vuốt nhẹ dòng chữ \"Cháu Diệu\"",
        "viết được hai từng chữ 'Cháu Diệu'": "viết được hai dòng chữ 'Cháu Diệu'",
        "chỉ có hai từng chữ 'Cháu Diệu'": "chỉ có hai dòng chữ 'Cháu Diệu'",
        "Cầm phong bao có từng chữ \"Cháu Diệu\" lên": "Cầm phong bao có dòng chữ \"Cháu Diệu\" lên",
        # R60
        '"Con chạy ra. Đỡ': '"Con chạy ra ngoài. Đỡ',
        # R61
        'Đêm hai chín tháng Chạp.': 'Vào đêm hai chín tháng Chạp.',
        'Mưa phùn lất phất.': 'Trời mưa phùn lất phất.',
        'Cô bước lên xe.': 'Cô gái bước lên xe.',
        'Cô nhìn xuống cặp da.': 'Cô gái nhìn xuống cặp da.',
        'Cô mở khoá cặp da.': 'Cô gái mở khoá cặp da.',
        'Cô lật xấp phong bao.': 'Cô gái lật xấp phong bao.',
        'Cô chớp mắt.': 'Cô gái khẽ chớp mắt.',
        'Cô gái quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        'Cô đi ra cửa xe.': 'Cô gái đi ra cửa xe.',
        'Cô gật đầu nhẹ.': 'Cô gái khẽ gật đầu nhẹ.',
    },
    5: {
        # R60
        'Rồi tan ra.': 'Rồi tan ra trong gió.',
        # R61
        'Đêm ba mươi tháng Chạp.': 'Vào đêm ba mươi tháng Chạp.',
        'Mưa lất phất.': 'Trời mưa lất phất.',
        'Đêm nay hai lần.': 'Vào đêm nay đến hai lần.',
        'Đêm ba mươi.': 'Vào đêm ba mươi cuối năm.',
        'Năm sau nữa cũng vậy.': 'Một năm sau nữa cũng vậy.',
        'Năm?': 'Năm thứ mấy rồi?',
        'Mưa biển vẫn lất phất.': 'Trời mưa biển vẫn lất phất.',
        'Sương biển khép vào lạnh.': 'Lớp sương biển khép vào lạnh.',
        'Trên ghế thứ tám trống.': 'Trên mặt ghế thứ tám trống.',
        'Đêm vẫn dài.': 'Đêm hôm nay vẫn còn dài.',
        'Đêm vẫn lăn bánh.': 'Chuyến xe đêm vẫn lăn bánh.',
    },
}

def main():
    apply = '--apply' in __import__('sys').argv
    print(f"EP02-05 manual rewrite | Mode: {'APPLY' if apply else 'DRY-RUN'}")
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
                skipped.append(old[:50])
        print(f"\nEP{n:02d}: {applied}/{len(rewrites)} applied")
        for s in skipped:
            print(f"  SKIP: {s}")
        if apply and applied:
            backup = p.with_suffix('.md.bak.K_manual')
            shutil.copy2(p, backup)
            p.write_text(text, encoding='utf-8')
        total += applied
    print(f"\nTotal: {total}")
    if apply:
        print("APPLIED")

if __name__ == '__main__':
    main()
