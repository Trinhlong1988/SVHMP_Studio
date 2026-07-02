"""SVHMP — Manual rewrite EP41-45."""
import shutil, sys
from pathlib import Path
SVHMP = Path(__file__).resolve().parents[1]

EP_REWRITES = {
    41: {
        'Đêm.': 'Trời đã về đêm.',
        'Đêm thứ bốn mươi mốt.': 'Đêm thứ bốn mươi mốt của hành trình.',
        'Cô lên bậc xe.': 'Cô gái lên bậc xe.',
        'Cô gái ngồi yên lặng.': 'Cô gái khẽ ngồi yên lặng.',
        'Cô nói rất nhỏ.': 'Cô gái nói rất nhỏ nhẹ.',
        'Cô quay đầu lại.': 'Cô gái khẽ quay đầu lại.',
        'Cô bước xuống dưới.': 'Cô gái bước xuống dưới đường.',
        'Cô đến.': 'Cô gái đến nơi đó.',
        '"Đêm bốn mươi mốt.': '"Vào đêm bốn mươi mốt.',
    },
    42: {
        'Đêm vừa khuya.': 'Trời đêm vừa khuya.',
        'Đêm thứ bốn mươi hai.': 'Đêm thứ bốn mươi hai của hành trình.',
        'Anh vào xe.': 'Người đàn ông vào xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        'Anh đến.': 'Người đàn ông đến nơi đó.',
        '"Đêm bốn mươi hai.': '"Vào đêm bốn mươi hai.',
        'Đêm bốn mươi hai.': 'Vào đêm bốn mươi hai.',
        'Đêm này dài.': 'Đêm này còn dài lắm.',
    },
    43: {
        'Mưa đã rơi từ chiều.': 'Trời mưa đã rơi từ chiều.',
        'Đêm thứ bốn mươi ba.': 'Đêm thứ bốn mươi ba của hành trình.',
        'Anh bước lên xe.': 'Người đàn ông bước lên xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        'Năm mươi tuổi.': 'Em năm mươi tuổi rồi.',
        'Anh ở xã bên.': 'Anh ấy ở xã bên cạnh.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        '"Đêm bốn mươi ba.': '"Vào đêm bốn mươi ba.',
        'Đêm bốn mươi ba.': 'Vào đêm bốn mươi ba.',
        'Đêm chưa sáng lên.': 'Trời đêm chưa sáng lên.',
    },
    44: {
        'Đêm thứ bốn mươi tư.': 'Đêm thứ bốn mươi tư của hành trình.',
        'Bà lên xe.': 'Bà cụ lên xe.',
        'Bà ngồi yên.': 'Bà cụ ngồi yên một lát.',
        'Bà nói rất nhỏ.': 'Bà cụ nói rất nhỏ nhẹ.',
        'Bà quay đầu lại.': 'Bà cụ khẽ quay đầu lại.',
        'Năm mươi hai tuổi.': 'Em năm mươi hai tuổi rồi.',
        'Bà mất sáng hôm sau.': 'Bà cụ mất sáng hôm sau.',
        'Bà bước xuống dưới.': 'Bà cụ bước xuống dưới đường.',
        'Bà đến.': 'Bà cụ đến nơi đó.',
        'Bà Sáu tan ra.': 'Người bà Sáu tan ra.',
        'Anh đã sai.': 'Em đã sai rồi.',
        'Anh sống Sài Gòn.': 'Em sống Sài Gòn lâu rồi.',
        '"Đêm bốn mươi tư.': '"Vào đêm bốn mươi tư.',
        'Anh nhỏ — anh khóc.': 'Cậu trai nhỏ — anh khóc.',
    },
    45: {
        'Đêm.': 'Trời đã về đêm.',
        'Đêm thứ bốn mươi lăm.': 'Đêm thứ bốn mươi lăm của hành trình.',
        'Anh lên bậc xe.': 'Người đàn ông lên bậc xe.',
        'Anh ngồi yên.': 'Người đàn ông ngồi yên.',
        'Anh nói rất nhỏ.': 'Người đàn ông nói rất nhỏ.',
        'Anh quay đầu lại.': 'Người đàn ông quay đầu lại.',
        '"Đêm nay — em quyết.': '"Vào đêm nay — em quyết.',
        'Anh bước xuống dưới.': 'Người đàn ông bước xuống dưới.',
        'Anh đến.': 'Người đàn ông đến nơi đó.',
        '"Đêm bốn mươi lăm.': '"Vào đêm bốn mươi lăm.',
        'Anh chỉ cần check-in.': 'Em chỉ cần check-in thôi.',
        'Anh đã trả tiền vé.': 'Em đã trả tiền vé rồi.',
        'Anh đã sai.': 'Em đã sai rồi.',
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
