"""SVHMP Auto-Gen Episode V3.1 — Base Pattern A 2400w + swap REVEAL theo pattern.

Mr.Long 27/6 lệnh: 5-6 templates đa dạng + đạt 15p mỗi tập.

V3.1 simpler approach: dùng V2 Pattern A làm base (proven 15p),
chỉ THAY REVEAL section theo 6 pattern variations.

→ All EPs đạt 15p + diversity tại điểm "đắt giá" nhất (REVEAL = peak emotion).
"""
import argparse
import json
import re
import subprocess
import sys
import yaml
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from auto_gen_ep import (
    SETTING_DESCRIPTORS, OBJECT_DESCRIPTORS, STOP_LOCATIONS,
    get_continuity, load_data, get_passenger, get_regret, pronoun_for,
    build_episode as build_base_v2,
    run_vnqa,
)

PATTERNS = ['A', 'B', 'C', 'D', 'E', 'F']

PATTERN_NAMES = {
    'A': 'Linear flashback',
    'B': 'Reverse POV',
    'C': 'Letter framing',
    'D': 'Object-first',
    'E': 'Multi-POV',
    'F': 'Monologue im lặng',
}


def get_pattern(ep_num: int) -> str:
    return PATTERNS[(ep_num - 11) % 6]


def reveal_variant_block(ep_num, name, pron, pron_cap, obj):
    """Variant insert block (V3.2): 3 micro-variations per ep dựa ep_num.
    Inserted vào REVEAL section để tăng diversity within same pattern.
    """
    variant = (ep_num - 11) // 6 % 3  # 0, 1, 2 — 3 variants
    if variant == 0:
        return f"""[pause:600ms]

Trong gia đình {pron}, người ấy là thế hệ giữ ký ức. Cha mẹ {pron} từ lâu đã không còn. {pron_cap} là người cuối cùng còn nhớ tên nhà bà cố — vùng quê cũ — món ăn {pron} hay được dỗ ăn từ tấm bé. Khi người ấy đi, một mảng quá khứ của {pron} đi theo.

{pron_cap} nhận ra điều đó muộn. Mỗi năm thêm tuổi, {pron} lại nhớ ra một chi tiết người ấy từng kể — và tự buồn vì ngày đó {pron} không lắng nghe đủ. Nay người ấy không còn để hỏi.

"""
    elif variant == 1:
        return f"""[pause:600ms]

Có một đêm {pron} nằm cạnh giường người ấy lúc người ấy đã yếu. Người ấy không nói nhiều — chỉ nắm tay {pron}. Hai bàn tay đan. Lâu. Không ai nói gì. {pron_cap} nhớ — đó là lần đầu tiên {pron} và người ấy nắm tay yên lặng như thế.

Cả đời người ấy chăm sóc {pron}. Một đêm cuối, lần đầu {pron} chăm người ấy. Một đêm. Sáng sau người ấy đi.

{pron_cap} hối hận vì đã không nắm tay người ấy nhiều lần hơn từ trước đó. Hai bàn tay chỉ chạm thẳng nhau trong đêm cuối — chứ không qua nhiều năm.

"""
    else:
        return f"""[pause:600ms]

{pron_cap} có một album ảnh người ấy giữ — album cũ, ảnh đen trắng. {pron_cap} đem theo lên thành phố, đặt trên giá sách. Mỗi cuối năm {pron} lấy xuống xem một lần. Mỗi lần xem, {pron} nhớ thêm chi tiết: ảnh này chụp đâu, người ấy mặc gì, hôm đó là ngày gì.

Album dày năm trang. Sau mười năm, {pron} đã thuộc từng ảnh. Nhưng có một ảnh — ảnh duy nhất chỉ riêng người ấy không có {pron} cùng — {pron} không nhớ chụp khi nào. Người ấy đứng trước một quán nhỏ. Mỉm cười. Có ai đó đứng phía sau — chỉ thấy bóng.

{pron_cap} đoán đó là cha mẹ người ấy. Hoặc một người yêu cũ. {pron_cap} không có ai để hỏi. Người ấy đã đi.

"""


def reveal_pattern_A(name, age, pron, pron_cap, obj, sample, ep_num=11):
    """Pattern A: Linear flashback — passenger kể chuyện chronological."""
    variant_block = reveal_variant_block(ep_num, name, pron, pron_cap, obj)
    return f"""[pause:800ms]

{pron_cap} {obj['verb']} một lần nữa. {obj['detail'].capitalize()}.

"{pron_cap} tên {name}. Năm nay {age} tuổi."

Giọng {pron} nhỏ. Khô. Như đọc cho chính {obj['name']} nghe.

"{sample}"

[pause:600ms]

"Nhiều năm qua, {pron} mang theo {obj['name']} này. Trong túi xách. Trong cặp. Trong ba lô đi công tác. Mỗi đêm trước khi ngủ, {pron} lấy ra. Đặt cạnh đầu giường. Để cảm thấy hơi của người ấy chưa hoàn toàn tan."

"Vợ/chồng/con {pron} có lúc hỏi: 'Sao cứ giữ vật cũ này?' {pron_cap} không trả lời được. Vì nếu kể, người ấy sẽ thành câu chuyện. {pron_cap} không muốn người ấy thành câu chuyện. Người ấy là của riêng {pron} thôi."

[pause:800ms]

"Hôm người ấy đi, {pron} không có mặt. {pron_cap} ở xa. Đường tắc. Xe muộn. Đến nơi thì đã muộn — chỉ muộn hai giờ, hoặc nửa ngày, hoặc một ngày. Nhưng vẫn muộn."

"Người ấy nằm đó. Tay đặt trên ngực. Mặt bình thản. Không có gì đáng sợ. Chỉ là không còn thở."

"{pron_cap} ngồi cạnh. Cầm tay người ấy. Bàn tay đã lạnh. Da đã trắng. {pron_cap} muốn nói: 'Con xin lỗi. Con về muộn.' Nhưng người ấy không nghe. {pron_cap} chỉ ngồi đó. Không khóc. Không nói. Đến lúc ai đó dìu {pron} đứng dậy."

[pause:1500ms]

Bác tài nhìn gương chiếu hậu một thoáng. Im lặng. Không nói câu nào.

Trong gương chiếu hậu phía sau ghế lái, Quang thấy hai cái bóng. Một là {pron}. Một là một bóng người lớn tuổi hơn, ngồi sát ngay sau {pron}. Bóng người ấy đang đặt tay lên vật giống vật {pron} đang giữ. Mắt nhìn xuống. Không nhìn ai. Không nói.

Quang chớp mắt. Trong gương vẫn chỉ có {pron} và một bóng mờ.

Bác tài cất lời. Câu hỏi cũ.

"Con đã nhớ ra chưa?"

{pron_cap} không quay đầu. Khẽ gật. Một cái gật rất nhỏ.

"{pron_cap} nhớ, bác."

[pause:1000ms]

"{pron_cap} nhớ từ lâu lắm. Nhưng nhớ không có nghĩa là nói được. {pron_cap} chỉ nhớ trong lòng. Mỗi đêm trước khi ngủ. Mỗi sáng khi mở mắt. Mỗi lần đi qua một quán cũ. Mỗi lần nghe một bài hát cũ. Người ấy luôn ở đó — nhưng không nói được."

[pause:800ms]

"Đêm nay {pron} đem {obj['name']} về quê. Đặt lên ban thờ. Thắp nhang. Nói: 'Con nhớ rồi. Con xin lỗi.' Có thể người ấy nghe. Có thể không. Nhưng {pron} cần nói.\""""


def reveal_pattern_B(name, age, pron, pron_cap, obj, sample, ep_num=11):
    """Pattern B: Reverse POV — passenger giờ ở vị trí MẸ đợi (gen reversal)."""
    return f"""[pause:800ms]

"{pron_cap} tên {name}. {age}. Năm nay {pron} ngồi đây — chỗ mẹ chồng {pron} ngày xưa ngồi."

Giọng {pron} chậm, không buồn.

"Mẹ chồng {pron} ngày {pron} mười tám tuổi đã dạy {pron} cách giữ {obj['name']} này. Mẹ chồng bảo: 'Sau này con sẽ đợi. Hôm nay con học cách đợi.' {pron_cap} không tin."

"{pron_cap} nghĩ — đời mình sẽ khác. Mình sẽ không phải đợi. Con cháu sẽ về."

[pause:600ms]

"Năm nào {pron} cũng gọi điện cho con cả. Con cả: 'Mẹ ơi năm nay con bận công ty.' Con thứ: 'Mẹ ơi vợ con đi du lịch.' Con út: chưa từng về từ Mỹ. Cháu lớn ở Singapore. Cháu thứ ở Sài Gòn. Cháu út chưa biết đi."

"Mỗi câu trả lời, {pron} đều bình thản. Không trách. Vì {pron} cũng đã từng làm vậy. Năm {pron} ba mươi tuổi, con nhỏ, công việc bận. {pron_cap} cũng nhắn mẹ chồng: 'Mẹ ơi năm nay con không về kịp.'"

[pause:1000ms]

"{pron_cap} đã ở vị trí cả hai. Ngày xưa người không về. Bây giờ người đợi. Có cảm giác hai vị trí đều cô đơn — nhưng cô đơn theo cách khác."

"Khi mình là người đi xa, cô đơn là không có mẹ. Khi mình là người đợi, cô đơn là không có con. Cuối cùng cả hai đều cô đơn — vì ở trên đời này, ai cũng đến lượt phải đợi một ai đó không về."

[pause:1500ms]

Bác tài nhìn gương chiếu hậu. Im lặng.

Trong gương, Quang thấy hai cái bóng. {pron_cap} và một bóng phụ nữ rất già — tóc bạc gần hết, ngồi cạnh {pron}. Bóng phụ nữ ấy đang đặt tay lên vai {pron}. Một cái chạm nhẹ. Như khen ngợi.

Quang chớp mắt. Bóng phụ nữ tan.

Bác tài cất lời.

"Con đã nhớ ra chưa?"

{pron_cap} gật.

"{pron_cap} nhớ, bác. {pron_cap} đã hiểu — mẹ chồng {pron} ngày xưa không trách {pron} không về. Mẹ chồng chỉ đợi. Lúc đó {pron} không hiểu. Giờ {pron} hiểu."

[pause:1200ms]

"Đêm nay {pron} đem {obj['name']} về đặt lên ban thờ mẹ chồng. Cảm ơn mẹ chồng đã dạy {pron} cách đợi không trách. Cảm ơn mẹ chồng đã không bỏ {pron} lại lúc {pron} bỏ mẹ chồng lại."

"{pron_cap} đã viết một câu thư từ chiều — để đặt cùng {obj['name']}. Trong thư {pron} viết: 'Mẹ ơi con đã ngồi đúng chỗ mẹ rồi. Con xin lỗi vì ngày xưa con không hiểu. Giờ con hiểu.'"

"Đến lượt {pron} truyền lại — cho con dâu, cho cháu dâu, cho ai sau này còn chịu nghe. Cách đợi không trách."

{reveal_variant_block(ep_num, name, pron, pron_cap, obj)}"""


def reveal_pattern_C(name, age, pron, pron_cap, obj, sample, ep_num=11):
    """Pattern C: Letter framing — passenger đọc lá thư người đã mất."""
    return f"""[pause:800ms]

{pron_cap} mở một xấp giấy nhỏ — buộc bằng dải băng đỏ — lấy ra từ {obj['name']}. Giấy đã ố vàng. Chữ viết tay người già, nét run.

"{pron_cap} tên {name}. {age}. {pron_cap} đem theo xấp thư của mẹ/bà/cha {pron}. Mẹ/bà/cha viết cho {pron} qua nhiều năm — nhưng nhiều thư {pron} chưa kịp đọc khi còn sống."

[pause:600ms]

{pron_cap} đọc lá thư đầu tiên — giọng nhỏ, đủ Quang nghe được.

"'{name} ơi, hôm nay là sinh nhật mười tám tuổi của con. Mẹ không gửi tiền được — tháng này mẹ đang khám bệnh. Mẹ xin lỗi.'"

"'Mẹ chỉ có lá thư này. Mẹ muốn nói với con vài điều — phòng khi mẹ không còn cơ hội.'"

"'Mẹ tự hào về con. Con đã đi xa, học hành tốt. Mẹ vui. Nhưng mẹ cũng nhớ con lắm.'"

[pause:800ms]

"'Mẹ muốn nói với con: dù sau này mẹ không còn, con đừng buồn nhiều. Mẹ luôn ở bên con. Trong mỗi bữa cơm con ăn. Trong mỗi đêm con ngủ. Mẹ ở đó.'"

"'Nếu có một ngày con quên mẹ — mẹ không trách. Đời con dài, con phải sống tiếp. Nhưng nếu có lúc nào đó con nhớ — mẹ cũng đang nhớ con.'"

"'Mẹ ký: Mẹ của con.'"

[pause:1500ms]

{pron_cap} gấp thư. Áp lên ngực. Nhắm mắt.

"Lá thư này đến tay {pron} sau khi mẹ đi rồi một tuần. Bưu điện chậm. Hoặc {pron} chậm về."

"{pron_cap} đã đọc lá thư này nhiều lần qua các năm. Mỗi năm đọc lại, hiểu thêm một chút. Năm đầu — {pron} khóc nhiều. Năm hai ba — {pron} im. Năm năm — {pron} cảm ơn. Năm mười — {pron} hiểu mẹ đã chuẩn bị câu này lâu lắm trước khi viết."

[pause:1000ms]

"Trong xấp này còn nhiều thư nữa — thư mẹ viết qua các năm. Có thư mẹ viết vào ngày {pron} thi đại học. Thư mẹ viết ngày {pron} đi làm xa. Thư mẹ viết ngày {pron} cưới. Mỗi thư là một câu mẹ chưa kịp nói trực tiếp."

"Năm nay {pron} đem cả xấp về quê đặt lên mộ mẹ. Trả lời từng thư bằng cách đặt thư bên cạnh mẹ. Là cách {pron} nói: 'Con đã đọc rồi mẹ. Con cảm ơn.'"

[pause:1500ms]

Bác tài cất lời.

"Con đã nhớ ra chưa?"

{pron_cap} gật. Không nói thêm.

[pause:800ms]

"{pron_cap} cũng đã viết một lá thư hồi đáp mẹ — viết tay, dài năm trang. {pron_cap} viết đêm qua, ngủ chỉ ba tiếng. Trong thư {pron} kể hết: kể về cuộc đời {pron} sau khi mẹ đi. Kể về vợ/chồng {pron}, về con {pron}, về việc {pron} làm. Kể cả những điều {pron} chưa bao giờ kể với ai."

"Lá thư này {pron} sẽ đốt trên mộ mẹ — để mẹ đọc."

"{pron_cap} biết — đốt thư không gửi được đến mẹ. Nhưng {pron} cần đốt. Đốt là cách {pron} giải phóng câu chuyện đã giữ trong lòng quá lâu.\""""


def reveal_pattern_D(name, age, pron, pron_cap, obj, sample, ep_num=11):
    """Pattern D: Object-first — 3 variants D_v1 vết / D_v2 mùi / D_v3 âm thanh."""
    variant = (ep_num - 11) // 6 % 3
    if variant == 1:
        return _reveal_D_v2_smell(name, age, pron, pron_cap, obj)
    if variant == 2:
        return _reveal_D_v3_sound(name, age, pron, pron_cap, obj)
    # Default variant 0 = D_v1 (vết theo thời gian)
    return f"""[pause:800ms]

{pron_cap} đặt {obj['name']} lên đùi. Tay đi qua từng chi tiết.

"{pron_cap} tên {name}. {age}. Nhưng đêm nay {pron} không kể chuyện {pron}. {pron_cap} kể chuyện vật này."

"{obj['name'].capitalize()} này là của mẹ. Mẹ mua/đan/giữ không biết bao nhiêu năm rồi. Chỉ biết mẹ luôn dùng. Mỗi ngày. Mỗi tuần. Mỗi mùa Tết. {obj['name'].capitalize()} đã thấy nhiều thứ."

[pause:600ms]

"Vết xước này ở góc — là năm mẹ bốn mươi tuổi. Mẹ vô tình làm. Mẹ cười. Bảo: 'Vết xước cũng đẹp.' Sau đó mỗi lần mẹ dùng, mẹ đều chạm vào vết xước — như chạm vào kỷ niệm."

"Vết nhỏ hơn — là năm {pron} mười lăm tuổi. {pron_cap} vô tình làm khi giúp mẹ. Mẹ giật mình. Nhưng không la {pron}. Mẹ chỉ bảo: 'Bây giờ vật này có hai vết xước. Hai mẹ con đều có dấu trên đó.'"

[pause:800ms]

"Mảng sờn ở mép — là chỗ mẹ vẫn cầm. Bàn tay mẹ qua nhiều năm đã làm mòn chỗ đó. Cứ chạm vào mảng sờn, {pron} cảm thấy hơi tay mẹ — dù mẹ không còn."

"Vết ố nhỏ ở giữa — là ngày sinh nhật bốn mươi của {pron}. Mẹ làm vô tình. Cũng cười. Bảo: 'Mỗi vết là một câu chuyện.'"

[pause:1000ms]

"Vết dài này — là vết nứt mới. Là năm mẹ đi. Mẹ ngã. Vật rơi. Nứt thêm. Khi {pron} thu xếp đồ mẹ, {pron} cầm lên — thấy vết nứt mới. {pron_cap} hiểu — mẹ vừa đi."

"Tay {pron} run khi cầm lên. Nhưng {pron} không khóc được. Chỉ đặt vật vào ngực. Nghe nhịp tim mình qua vật."

[pause:1500ms]

"Đêm nay {pron} đem vật này theo. Mỗi vết trên đó là một câu chuyện của mẹ và {pron}. {pron_cap} không cần kể nhiều bằng lời. Vật kể giúp {pron}."

Bác tài nhìn gương chiếu hậu. Im lặng.

Trong gương, Quang thấy hai cái bóng. {pron_cap} và một bóng phụ nữ trung niên — đang đặt tay lên vật cùng {pron}. Hai bàn tay chồng lên nhau. Hai mẹ con cùng cầm.

Quang chớp mắt. Bóng tan.

Bác tài cất lời.

"Con đã nhớ ra chưa?"

{pron_cap} gật. "{pron_cap} nhớ. Mẹ nói chuyện qua vật. Không cần lời."

[pause:1000ms]

"Đêm nay {pron} đem vật này về quê. Đặt lên ban thờ mẹ. Để tay mẹ cuối cùng cũng cầm vật một lần nữa."

"Sau này khi {pron} đi, {pron} sẽ truyền vật này cho con. Con {pron} không hiểu hết các vết. Nhưng con sẽ giữ. Đến lượt con vô tình làm thêm một vết. Vết của thế hệ con."

"Cứ thế. Vật được truyền. Vết được thêm. Câu chuyện được kể qua các thế hệ — không bằng lời.\""""


def _reveal_D_v2_smell(name, age, pron, pron_cap, obj):
    """D variant 2: kể qua MÙI vật theo thời gian."""
    return f"""[pause:800ms]

{pron_cap} đưa {obj['name']} lên gần mũi. Hít một hơi nhẹ. Nhắm mắt.

"{pron_cap} tên {name}. {age}. Đêm nay {pron} kể chuyện qua mùi vật này."

[pause:600ms]

"Mùi đầu tiên — là mùi mẹ. Mẹ {pron} cầm vật này nhiều năm. Hơi tay mẹ thấm vào. Đó là một mùi {pron} không tả được. Pha giữa nước hoa nhài cũ mẹ vẫn xịt mỗi cuối tuần. Pha giữa mùi cơm rang chiều. Pha giữa mùi nắng phơi áo."

"Mùi này {pron} chỉ ngửi được khi ép sát vào mũi. Nhưng mùi đậm hơn — đậm như cả tuổi thơ {pron} nằm chung trong vật này."

[pause:800ms]

"Mùi thứ hai — là mùi nhà cũ ở quê. Vật này từng đặt trên bàn gỗ phòng khách quê. Phòng khách mở cửa sổ ra vườn. Hoa cau buổi sáng. Trầu già. Lá khô mùa thu. Tất cả đã thấm vào sợi vải/giấy/gỗ của vật. Khi {pron} đưa vật lên mũi, {pron} ngửi được cả căn nhà — dù căn nhà đã đổ năm năm trước."

"Mỗi năm mùi này nhạt đi một chút. {pron_cap} sợ — một ngày nào đó vật chỉ còn mùi của thành phố nơi {pron} sống bây giờ. Không còn mùi nhà cũ. Nên {pron} cất vật trong hộp kín. Chỉ mở ra mỗi đêm trước khi ngủ — ngửi một hơi. Đóng lại."

[pause:1000ms]

"Mùi thứ ba — là mùi {pron}. Bàn tay {pron} qua năm tháng đã làm thêm một lớp mùi mới — mỗi lần {pron} cầm. Ba mươi/bốn mươi/năm mươi năm vật ở trong tay {pron}. Mùi {pron} bây giờ là mùi chủ đạo. Nhưng dưới đó vẫn còn mùi mẹ và mùi nhà cũ — như tầng đá nền."

"Có lúc {pron} tự hỏi: khi {pron} mất, ai sẽ ngửi vật này? Con {pron} sẽ ngửi. Sẽ chỉ ngửi được mùi {pron} mới. Mùi mẹ và mùi nhà cũ — sẽ tan."

[pause:1500ms]

Bác tài liếc gương. Trong gương, Quang thấy hai bóng — {pron} và một phụ nữ ngồi sau. Phụ nữ ấy đang đặt mặt vào áo {pron} — như ngửi.

Quang chớp mắt. Bóng tan.

Bác tài cất lời.

"Con đã nhớ ra chưa?"

{pron_cap} gật. "{pron_cap} nhớ. Mùi mẹ vẫn còn — chỉ cần ngửi sát."

[pause:1200ms]

"Đêm nay {pron} đem vật về quê. Mở hộp ra ngay trên ban thờ. Để mẹ ngửi lại mùi nhà cũ — mùi đã tan với {pron} nhưng còn lại trong vật."

"{pron_cap} tin — mùi có thể truyền hai chiều. Mẹ ngửi được mùi {pron} bây giờ. {pron_cap} ngửi được mùi mẹ ngày xưa. Cả hai gặp nhau trong vật."

"Sau khi {pron} đi, con {pron} mở hộp — sẽ ngửi được mùi {pron} và mẹ và bà cố. Ba thế hệ trong một mùi. Đó là cách gia đình không tan dù người đi."""


def _reveal_D_v3_sound(name, age, pron, pron_cap, obj):
    """D variant 3: kể qua ÂM THANH vật phát ra theo thời gian."""
    return f"""[pause:800ms]

{pron_cap} cầm {obj['name']}. Chạm tay nhẹ vào. Lắc khẽ. Có một âm thanh rất nhỏ phát ra — như tiếng khẽ của vải/gỗ/giấy cũ.

"{pron_cap} tên {name}. {age}. Đêm nay {pron} kể chuyện qua âm thanh vật này."

[pause:600ms]

"Âm thanh đầu tiên {pron} nhớ về vật — là tiếng mẹ cầm. Mẹ đi qua phòng, tay cầm vật, làm phát ra tiếng nhỏ. Nhịp đều. Mỗi nhịp tay mẹ đi. {pron_cap} hồi nhỏ nằm trên giường, nghe tiếng đó từ phòng bên — biết mẹ đang làm việc trong bếp."

"Tiếng đó đối với {pron} là tiếng yên tâm. Mẹ còn ở đây. Mẹ đang làm việc. Mẹ chưa ngủ. {pron_cap} ngủ ngon vì có tiếng đó."

[pause:800ms]

"Âm thanh thứ hai — là tiếng vật rơi. Năm {pron} mười tám tuổi, đêm cuối trước khi đi học xa. {pron_cap} đứng dậy giúp mẹ. Tay vô tình va vào. Vật rơi xuống sàn — phát ra một tiếng 'cộc' khô. Không vỡ. Nhưng tiếng đó {pron} nhớ — vì lúc rơi, mẹ chỉ nhìn vật. Không la. Mẹ cúi xuống nhặt. Đặt lại chỗ cũ."

"Mẹ không trách. Mẹ chỉ nói: 'Mai con đi.' Tiếng mẹ nói câu đó cũng gần như tiếng vật rơi — khô, ngắn, không lời."

[pause:1000ms]

"Âm thanh thứ ba — là tiếng im. Đêm mẹ đi. Cả nhà yên tĩnh đến mức {pron} nghe được tiếng đồng hồ treo tường. Vật ở trên bàn — không phát ra tiếng nào. Mẹ không còn cầm. Vật im."

"Đó là lần đầu {pron} nghe vật im như thế. Suốt tuổi thơ {pron}, vật luôn có tiếng — vì mẹ luôn cầm. Đêm mẹ đi, vật im. Mới biết tiếng vật không phải từ vật — mà từ tay mẹ."

[pause:1200ms]

"Sau đó {pron} thử cầm vật cho ra tiếng. Lắc. Đi qua phòng. Nhưng tiếng {pron} cầm không giống tiếng mẹ. Nhịp khác. Mạnh khác. Vật phát ra tiếng — nhưng không phải tiếng yên tâm. Mà là tiếng nhớ."

[pause:1500ms]

Bác tài liếc gương. Trong gương, có hai bóng. {pron_cap} và mẹ — mẹ đang cầm vật, đi qua phòng. Tiếng nhịp đều vọng lại từ gương — chỉ Quang nghe được.

Quang chớp mắt. Bóng tan. Tiếng tan.

Bác tài cất lời.

"Con đã nhớ ra chưa?"

{pron_cap} gật.

"{pron_cap} nhớ. Tiếng mẹ vẫn còn trong vật. Chỉ chờ đúng tay cầm lại."

[pause:1200ms]

"Đêm nay {pron} đem vật về quê. Đặt trên bàn cũ chỗ mẹ vẫn để. Đêm nay {pron} sẽ thử cầm vật theo nhịp mẹ — nhịp {pron} nhớ từ hồi bé. Nếu cầm đúng, có thể tiếng sẽ về."

"Có thể không. Nhưng {pron} thử."

"Đêm nay {pron} cũng dạy con {pron} cách cầm vật. Cho con biết — tiếng vật không phải từ vật. Từ tay. Truyền qua các thế hệ. Mỗi tay một tiếng. Nhưng tất cả đều là tiếng nhớ." """


def reveal_pattern_E(name, age, pron, pron_cap, obj, sample, ep_num=11):
    """Pattern E: Multi-POV — Quang internal alternating với passenger external."""
    return f"""[pause:800ms]

[POV {pron_cap}, ngoài]: {pron_cap} {obj['verb']}. "{pron_cap} tên {name}. {age}."

[POV Quang, trong]: Quang nhìn {pron} qua khe ghế. Quang nhận ra mặt {pron} có nét quen. Như đã từng thấy ở đâu đó.

[POV {pron_cap}]: "{sample}"

[POV Quang]: Quang nghe câu chuyện. Quang cảm thấy ngực mình hơi đau — như đó cũng là câu chuyện Quang. Hoặc gần giống.

Quang nhớ — đêm nào đó rất xa, Quang cũng có một cuộc điện thoại nhỡ. Một người thân ốm. Quang ở xa. Quang không về kịp.

Quang quên tên người ấy.

[pause:1000ms]

[POV {pron_cap}]: "{pron_cap} mang theo {obj['name']} này nhiều năm. Mỗi đêm đặt cạnh đầu giường. Để không cô đơn."

[POV Quang internal]: Quang lục lọi trí nhớ. Có một thứ Quang vẫn cầm theo. Trong túi áo trong. Một chiếc khăn tay xanh nhạt, hoa thêu trắng. Khăn mùi long não cũ.

Khăn của ai? Quang không nhớ. Nhưng khăn luôn ở đó.

[POV {pron_cap}]: "Vợ/chồng {pron} có lúc hỏi: 'Sao giữ vật cũ này?' {pron_cap} không trả lời được. Vì nếu kể, người ấy thành câu chuyện. {pron_cap} không muốn người ấy thành câu chuyện."

[POV Quang]: Quang cũng vậy. Quang không kể với ai về khăn tay trong túi. Không vợ/chồng. Không bạn. Vì khăn không phải câu chuyện.

[pause:1500ms]

[POV {pron_cap}]: "Hôm người ấy đi, {pron} không có mặt. Đường tắc. Xe muộn. Đến nơi thì đã muộn."

[POV Quang]: Quang nhớ — đêm đó Quang cũng đang ngồi trên một chuyến xe nào đó. Xe khách đêm. Đường tắc. Quang chạy bộ phần cuối — mưa phùn. Đến nhà sáng sớm. Cổng mở. Người trong xóm đông.

Quang không nhớ ai trong quan tài. Quang nhớ chỉ một câu — em gái/em trai/cô em Quang nói: "Anh về rồi."

[POV {pron_cap}]: "{pron_cap} ngồi cạnh người ấy. Cầm tay. Tay đã lạnh. {pron_cap} không khóc. Chỉ ngồi."

[POV Quang]: Quang cũng ngồi. Quang nhớ. Nhưng Quang không nhớ ai. Tay ai. Mặt ai.

Có một mảng đen trong trí nhớ Quang. Đêm đó.

[pause:1500ms]

Bác tài cất lời.

"Con đã nhớ ra chưa?"

[POV {pron_cap}]: gật.

[POV Quang]: cũng định gật. Nhưng môi Quang không động. Vì Quang chưa nhớ ra.

Bác tài liếc gương. Ánh mắt dừng trên Quang. Lâu.

"Sắp nhớ ra rồi," bác khẽ. Không nhìn {pron}. Nhìn Quang.

[pause:1200ms]

[POV {pron_cap}]: "Đêm nay {pron} đem {obj['name']} về quê. Đặt lên ban thờ."

[POV Quang]: Quang nhìn xuống tay mình. Tay trống. Nhưng trong túi áo trong — khăn tay vẫn ở đó. Mùi long não. Như mẹ/bà.

Quang chạm vào khăn qua áo. Tay run.

"Còn vài đêm nữa," bác tài nói thêm. "Rồi con sẽ kể.\""""


def reveal_pattern_F(name, age, pron, pron_cap, obj, sample, ep_num=11):
    """Pattern F: Monologue extended — passenger im lặng, tự sự internal sâu."""
    return f"""[pause:800ms]

"{pron_cap} tên {name}. {age}."

Giọng {pron} đều, gần như thì thầm.

"Đêm nay {pron} không kể nhiều. Câu chuyện {pron} ngắn lắm. Một câu thôi."

[pause:1000ms]

"Mẹ/bà/cha {pron} đợi {pron}. {pron_cap} không về kịp."

[pause:1500ms]

"{pron_cap} đã có hai/ba mươi năm để nói câu xin lỗi. Hai/ba mươi năm đó {pron} không nói được. Vì nói với ai? Mẹ/bà/cha đã đi."

"{pron_cap} thử nói với chính mình. Trong gương. Trong đêm khuya. Trong những lúc ngồi trên ghế gỗ ngoài hiên — chỗ mẹ/bà/cha ngày xưa ngồi."

[pause:800ms]

"Câu 'Con xin lỗi mẹ/bà/cha' — {pron} đã nói nghìn lần. Mỗi lần một chút thấm. Nhưng vẫn chưa đủ. Vì có một sự khác biệt — nói với người đã đi không giống nói với người còn sống."

"Với người sống, câu xin lỗi là yêu cầu được tha thứ. Với người đi, câu xin lỗi chỉ là tự an ủi. Hai câu giống nhau nhưng không giống nhau."

[pause:1200ms]

(Trong đầu {pron}, có một dòng chữ thầm — Quang đoán được qua nét mặt.)

{pron_cap} đang nói câu thứ nghìn mốt. Lần này không phải "Con xin lỗi". Mà là: "Mẹ/bà/cha ơi, con không xin lỗi nữa. Con cảm ơn. Cảm ơn đã đợi con tới phút cuối. Cảm ơn đã không bỏ con dù con bỏ mẹ/bà/cha."

[pause:1500ms]

Bên ngoài, gió thổi. Mưa phùn vẫn lất phất. Quang nhìn {pron} qua khe ghế. {pron_cap} không động đậy. Chỉ ngồi với {obj['name']} trên đùi.

Trên áo {pron} có một mảng ẩm — không phải mưa. Là nước mắt {pron} đã rơi từ lúc nào không biết. {pron_cap} không lau. Để mặc.

[pause:1500ms]

Bác tài cất lời.

"Con đã nhớ ra chưa?"

{pron_cap} ngẩng đầu. Một thoáng. Rồi gật rất nhẹ.

Không nói lại. Vẫn im lặng.

Nhưng Quang biết — câu trả lời là "Có". Là "Có từ lâu. Chỉ chưa nói được với ai. Vì không cần nói."

[pause:1200ms]

(Trong đầu {pron} có một câu cuối Quang đoán được:)

"Đêm nay {pron} đem {obj['name']} về quê. Đặt lên ban thờ. Không thắp nhang. Không nói gì. Chỉ ngồi. Đợi. Đợi đến sáng. Như mẹ/bà/cha ngày xưa đợi {pron}. Đến sáng, {pron} sẽ về Hà Nội. Tiếp tục sống. Mang theo {obj['name']} đến lượt {pron} đi."

"Cách thương yêu cuối cùng là im lặng. Im lặng cùng người mình thương. Im lặng cho người mình thương ngủ yên.\""""


REVEAL_BUILDERS = {
    'A': reveal_pattern_A,
    'B': reveal_pattern_B,
    'C': reveal_pattern_C,
    'D': reveal_pattern_D,
    'E': reveal_pattern_E,
    'F': reveal_pattern_F,
}


def build_episode_v3(ep_num, passenger, regret, pattern):
    """Build EP với base V2 (proven 15p) + swap REVEAL theo pattern."""
    # Get V2 full template first
    base_text = build_base_v2(ep_num, passenger, regret)

    # Replace REVEAL section
    pron, _ = pronoun_for(passenger)
    pron_cap = pron.capitalize()
    name = passenger['char_name']
    age = passenger['age_range']
    obj = OBJECT_DESCRIPTORS.get(passenger['signature_object'], {
        'name': 'vật', 'state': 'cũ', 'verb': 'vuốt nhẹ', 'detail': 'cũ'
    })
    sample = regret.get('sample_story', passenger['regret_label'])

    new_reveal = REVEAL_BUILDERS[pattern](name, age, pron, pron_cap, obj, sample, ep_num)
    # V3.2: append variant block để fix same-pattern HIGH lặp
    variant_block = reveal_variant_block(ep_num, name, pron, pron_cap, obj)
    new_reveal_full = new_reveal + "\n\n" + variant_block

    # Find REVEAL section + replace
    pattern_re = re.compile(r'# REVEAL.*?(?=# PAYOFF)', re.S)
    new_section = f"# REVEAL [section 4 — Pattern {pattern}: {PATTERN_NAMES[pattern]}]\n\n{new_reveal_full}\n\n---\n\n"
    result = pattern_re.sub(new_section, base_text)

    # Add pattern marker to header
    result = result.replace('auto_gen: tools/auto_gen_ep.py v2.0',
                            f'auto_gen: tools/auto_gen_ep_v3.py v3.1 — pattern {pattern} ({PATTERN_NAMES[pattern]})')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--batch', type=str)
    parser.add_argument('--qa-loop', action='store_true')
    args = parser.parse_args()

    roster, bible_11 = load_data()

    if args.batch:
        s, e = map(int, args.batch.split('-'))
        eps = list(range(s, e + 1))
    elif args.ep:
        eps = [args.ep]
    else:
        sys.exit("Pass --ep N or --batch S-E")

    stats = {'pass': 0, 'warn': 0, 'fail': 0, 'short': 0, 'ok_duration': 0, 'patterns': {}}

    for ep_num in eps:
        if ep_num in {73, 90}:
            print(f"  EP{ep_num:02d}: RESERVED")
            continue
        p = get_passenger(ep_num, roster)
        if not p:
            print(f"  EP{ep_num:02d}: no passenger")
            continue
        r = get_regret(p['regret_sub_archetype'], bible_11)
        pattern = get_pattern(ep_num)
        text = build_episode_v3(ep_num, p, r, pattern)
        out = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
        words = len(text.split())
        stats['patterns'][pattern] = stats['patterns'].get(pattern, 0) + 1

        if args.qa_loop:
            vnqa = run_vnqa(ep_num)
            if vnqa:
                v, m, i = vnqa['verdict'], vnqa['stats'].get('estimated_minutes', 0), vnqa['issues_count_by_severity']
                if v == 'PASS': stats['pass'] += 1
                elif v == 'WARN': stats['warn'] += 1
                else: stats['fail'] += 1
                if m < 15: stats['short'] += 1
                else: stats['ok_duration'] += 1
                print(f"  EP{ep_num:02d} [{pattern}] {p['char_name']:14} | {words}w | {m}p | {v}")
            else:
                print(f"  EP{ep_num:02d} [{pattern}] {p['char_name']:14} | {words}w | VNQA fail")
        else:
            print(f"  EP{ep_num:02d} [{pattern}] {p['char_name']:14} | {words}w → {out.relative_to(SVHMP)}")

    if args.qa_loop:
        print(f"\n=== Batch summary V3.1 ===")
        print(f"PASS={stats['pass']} WARN={stats['warn']} FAIL={stats['fail']} | duration_OK={stats['ok_duration']} short={stats['short']}")
        print(f"Pattern distribution: {stats['patterns']}")


if __name__ == '__main__':
    main()
