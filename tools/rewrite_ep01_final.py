"""SVHMP — Final cleanup EP01 R58 + R61 remaining 14 issues.

CẢNH BÁO CONCURRENCY (DEBT-005): công cụ THỦ CÔNG, ghi trực tiếp output/ep_01/episode.md THẬT
(dùng chung mọi phiên) KHÔNG có golden_lock. CHỈ chạy 1 lần bằng tay khi KHÔNG có phiên pytest/
render nào khác đang chạy — nếu chạy song song có thể corrupt EP01. Được whitelist trong
tests/test_no_unlocked_ep01_writer.py (_MANUAL_TOOL_EXCEPTION) vì không phải test tự chạy lặp.
"""
import shutil
from pathlib import Path

EP01 = Path(__file__).resolve().parents[1] / r'output/ep_01/episode.md'

REWRITES = {
    # R58 tilde EOL
    'Vỏ xà cừ. Mặt số La Mã.\n\nKim đồng hồ': 'Vỏ xà cừ. Mặt số La Mã trang nhã.\n\nKim đồng hồ',
    'Vỏ xà cừ lạnh.\n\nMặt số La Mã.\n\nKim dừng bảy giờ mười.': 'Vỏ xà cừ lạnh. Mặt số La Mã in chìm trên nền cừ. Kim dừng bảy giờ mười.',
    'Khải Phong gấp tờ giấy lại như cũ.': 'Khải Phong gấp tờ giấy lại như lúc đầu.',
    'Cô gái nhíu mày khẽ.': 'Cô gái khẽ nhíu mày.',
    'Cô gái nhíu mắt nhìn kỹ.': 'Cô gái nhíu mắt nhìn thật kỹ.',
    # R61 remaining
    'Ông cụ không bật radio. Ông chỉ ngồi ôm nó vào lòng.': 'Ông cụ không bật radio. Ông cụ chỉ ngồi ôm nó vào lòng.',
    '— Cô… nhìn gì vậy?': '— Này cô, cô nhìn gì vậy?',
    '— Cô ấy đi rồi.': '— Cô ấy đã đi từ lâu rồi.',
    'Anh đi ngang ghế ba.': 'Khải Phong đi ngang qua ghế thứ ba.',
    'Trên mặt ghế số bảy.': 'Trên mặt ghế số bảy ấy.',
    'Cô gái cúi người xuống.': 'Cô gái khẽ cúi người xuống.',
    'Cô nhặt lên cao.': 'Cô gái nhặt vật lên trước mặt.',
    'Ngoài cửa kính,': 'Phía ngoài cửa kính,',
}

text = EP01.read_text(encoding='utf-8')
shutil.copy2(EP01, EP01.with_suffix('.md.bak.R61_final'))
applied = 0
skipped = []
for old, new in REWRITES.items():
    if old in text:
        text = text.replace(old, new, 1)
        applied += 1
    else:
        skipped.append(old[:60])
EP01.write_text(text, encoding='utf-8')
print(f"Final cleanup: {applied}/{len(REWRITES)} applied")
for s in skipped:
    print(f"  SKIP: {s}")
