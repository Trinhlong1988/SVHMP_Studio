"""SVHMP — Manual rewrite EP01 R61 violations (48 instances).

Per-context rewrite giữ narrative meaning + horror staccato rhythm.
Each entry: short-start sentence → expanded version (≥6 words OR prefix added).
"""
import shutil
from pathlib import Path

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')
EP01 = SVHMP / 'output' / 'ep_01' / 'episode.md'

# Map: exact line text → rewrite
REWRITES = {
    'Sương dày dần.': 'Sương ngoài cửa kính dày dần.',
    'Anh nhìn xuống dưới. Kim vẫn dừng bảy giờ mười.': 'Khải Phong cúi xuống nhìn. Kim vẫn dừng bảy giờ mười.',
    'Anh cũng không mở.': 'Khải Phong cũng không hề mở ngăn.',
    'Anh mới kéo ngăn ra. Anh nhìn nó. Rồi anh đóng lại.': 'Khải Phong mới kéo ngăn kéo ra. Khải Phong nhìn nó một thoáng. Rồi anh đóng lại nhẹ nhàng.',
    'Mưa rơi đều.': 'Tiếng mưa rơi đều bên ngoài.',
    'Ông cụ không bật. Ông chỉ ôm.': 'Ông cụ không bật radio. Ông chỉ ngồi ôm nó vào lòng.',
    'Anh không mở. Anh chỉ giữ lại.': 'Người đàn ông không mở giấy ra. Anh ấy chỉ giữ tờ giấy gấp tư trong tay.',
    'Anh thấy mình bé lại.': 'Khải Phong thấy mình như bé lại.',
    'Cô tóc cột thấp. Áo khoác len màu xám.': 'Cô gái tóc cột thấp sau gáy. Áo khoác len màu xám nhạt.',
    'Cô không hỏi gì.': 'Cô gái không hỏi thêm câu nào.',
    'Cô chỉ nhìn chiếc đồng hồ.': 'Cô gái chỉ lặng nhìn chiếc đồng hồ.',
    'Cô gái cười nhẹ.': 'Cô gái mỉm cười nhẹ nhàng.',
    'Cô gái gật chậm.': 'Cô gái gật đầu chậm rãi.',
    'Cô gái không hỏi nữa.': 'Cô gái không hỏi thêm nữa.',
    'Cô chỉ ngồi yên. Tay cô đan vào nhau trên đùi.': 'Cô gái chỉ ngồi yên lặng. Hai tay cô đan vào nhau đặt trên đùi.',
    'Ông cụ tắt radio.': 'Ông cụ chậm rãi tắt radio.',
    'Cô gái ghế tám đợi.': 'Cô gái ngồi ghế tám đợi anh kể tiếp.',
    'Cô nhìn Khải Phong.': 'Cô y tá nhìn về phía Khải Phong.',
    'Cô khẽ lắc đầu.': 'Cô y tá khẽ lắc đầu một cái.',
    'Cô chỉ đợi.': 'Cô gái chỉ ngồi đợi anh nói tiếp.',
    'Anh quay về cửa kính.': 'Khải Phong quay đầu nhìn về cửa kính.',
    'Anh đọc một lần.': 'Khải Phong đọc nó một lần.',
    'Anh gấp lại.': 'Khải Phong gấp tờ giấy lại như cũ.',
    'Anh đặt tay lên ngực.': 'Khải Phong đặt một bàn tay lên ngực.',
    'Anh chậm lại.': 'Khải Phong thở chậm lại.',
    'Ông cúi đầu một lần.': 'Ông cụ cúi đầu một lần thật chậm.',
    'Anh nhìn cô.': 'Khải Phong nhìn về phía cô gái ghế tám.',
    'Anh gật.': 'Khải Phong khẽ gật đầu.',
    'Cô gái cụp mắt.': 'Cô gái khẽ cụp mắt xuống.',
    'Anh đi ngang ghế ba. Ông cụ ngẩng.': 'Khải Phong đi ngang qua ghế ba. Ông cụ ngẩng đầu lên nhìn.',
    'Anh đi ngang ghế chín. Cô y tá nhìn theo.': 'Khải Phong đi ngang qua ghế chín. Cô y tá đưa mắt nhìn theo.',
    'Anh đứng dậy.': 'Khải Phong từ từ đứng dậy.',
    'Trong xe, im lặng.': 'Trong cabin xe, không gian chìm vào im lặng.',
    'Cô gái ngẩng lên.': 'Cô gái mới ghế bảy ngẩng đầu lên.',
    'Trên ghế số bảy.': 'Trên mặt ghế số bảy.',
    'Cô nhíu mày.': 'Cô gái nhíu mày khẽ.',
    'Cô cúi xuống dưới.': 'Cô gái cúi người xuống.',
    'Cô nhặt lên cao.': 'Cô gái nhặt vật ấy lên.',
    'Cô tóc xõa.': 'Cô gái tóc xõa ngang vai.',
    'Cô nhìn xuống dưới.': 'Cô gái nhìn xuống ghế cạnh mình.',
    'Cô nhíu mắt nhìn.': 'Cô gái nhíu mắt nhìn kỹ.',
    'Cô nhỏ nhẹ nhàng.': 'Cô gái nói khẽ nhỏ nhẹ.',
    'Cô khẽ rùng mình.': 'Cô gái khẽ rùng mình một thoáng.',
}

def main():
    text = EP01.read_text(encoding='utf-8')
    shutil.copy2(EP01, EP01.with_suffix('.md.bak.R61_manual'))
    applied = 0
    skipped = []
    for old, new in REWRITES.items():
        if old in text:
            text = text.replace(old, new, 1)
            applied += 1
        else:
            skipped.append(old)
    EP01.write_text(text, encoding='utf-8')
    print(f"EP01 R61 manual rewrite: {applied} applied / {len(skipped)} skipped (not found)")
    for s in skipped:
        print(f"  SKIP: {s[:50]}")

if __name__ == '__main__':
    main()
