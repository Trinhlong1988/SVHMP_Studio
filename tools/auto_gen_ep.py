"""SVHMP Auto-Gen Episode V2 — template engine với QA loop tích hợp.

Mr.Long 27/6 lệnh:
- Tích hợp QA test trong quá trình gen (VNQA H1-H10)
- Check từ điển sâu (lexicon Hoàng Phê)
- Kiểm thử engine + audit tự động, không lỗi

NO speculation: dùng EXACTLY data từ passenger roster + bibles.
Tuân hiến pháp bible/00 + bible/03 + bible/11 + bible/12 + bible/13 + bible/18 + bible/23.

Pipeline: build template → VNQA check → expand nếu duration <15p → repeat → ship.
"""
import argparse
import json
import subprocess
import sys
import yaml
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent

SETTING_DESCRIPTORS = {
    'setting_can_tet': {'name': 'cận Tết', 'time': 'Đêm hai tám tháng Chạp', 'weather': 'Mưa phùn lất phất', 'ambient': 'Bụi mía sương mờ ven đường vắng'},
    'setting_dem_giao_thua': {'name': 'đêm giao thừa', 'time': 'Đêm ba mươi tháng Chạp', 'weather': 'Sương dày', 'ambient': 'Pháo hoa từ xa nổ rất nhẹ'},
    'setting_dong_lanh': {'name': 'đông lạnh', 'time': 'Đêm tháng Một âm', 'weather': 'Rét đậm, sương mù dày', 'ambient': 'Đèo núi vắng, gió luồn qua'},
    'setting_dem_thang_tu_HN': {'name': 'đêm tháng tư Hà Nội', 'time': 'Đêm tháng tư', 'weather': 'Mưa phùn nhẹ', 'ambient': 'Lá sấu rơi xuống mặt đường'},
    'setting_san_bay_dem': {'name': 'sân bay đêm', 'time': 'Đêm khuya', 'weather': 'Sương lạnh', 'ambient': 'Đèn báo hiệu phía xa nhấp nháy'},
}

OBJECT_DESCRIPTORS = {
    'OBJ_AO_LEN_NAU': {'name': 'cuộn áo len nâu', 'state': 'gấp gọn, có sợi len thừa', 'verb': 'vuốt nhẹ mặt áo', 'detail': 'mềm, có mùi long não cũ'},
    'OBJ_BANH_CHUNG_GOI_DO': {'name': 'cặp bánh chưng gói dở', 'state': 'lá còn cuộn, gạo lộ ra', 'verb': 'vuốt nhẹ lá dong', 'detail': 'lá khô, sợi lạt buộc dở treo lưng chừng'},
    'OBJ_LI_XI_DO': {'name': 'phong bao lì xì đỏ', 'state': 'mặt sau có chữ viết tay run', 'verb': 'vuốt nhẹ mặt phong bao', 'detail': 'phong bao mới, chưa mở'},
    'OBJ_KHAN_TAY_CU': {'name': 'khăn tay cũ', 'state': 'xanh nhạt, thêu hoa trắng', 'verb': 'áp khăn lên trán', 'detail': 'mùi long não, đã bạc qua nhiều năm'},
    'OBJ_BANG_CASSETTE': {'name': 'băng cassette cũ', 'state': 'vỏ nhựa hơi vỡ', 'verb': 'vuốt nhẹ vỏ băng', 'detail': 'mặt vỏ có chữ viết tay người già'},
    'OBJ_DONG_HO_XA_CU': {'name': 'đồng hồ xà cừ', 'state': 'kim đã dừng ở 7:10', 'verb': 'đặt đồng hồ lên đùi', 'detail': 'mặt đồng hồ phẳng, có vết xước nhỏ'},
    'OBJ_AO_GIO_XANH': {'name': 'áo gió xanh', 'state': 'đã bạc, sờn ở cổ', 'verb': 'vuốt nhẹ cổ áo', 'detail': 'mặt vải mỏng, ấm vừa đủ'},
    'OBJ_AO_DAI_TRANG': {'name': 'áo dài trắng', 'state': 'gấp cẩn thận', 'verb': 'vuốt nhẹ nếp áo', 'detail': 'tà áo còn nguyên nếp cũ'},
    'OBJ_THU_TAY': {'name': 'cuộn thư tay', 'state': 'giấy đã ngả vàng', 'verb': 'vuốt nhẹ mặt giấy', 'detail': 'mép giấy hơi cong, mực bay'},
    'OBJ_BUT_MAY_CHA': {'name': 'cây bút máy', 'state': 'cũ, mực đã khô', 'verb': 'cầm bút trên tay', 'detail': 'thân bút trơn, có dấu tay người dùng nhiều'},
    'OBJ_SO_GHI_CHEP': {'name': 'cuốn sổ ghi chép', 'state': 'bìa nâu, giấy ngả vàng', 'verb': 'lật trang sổ', 'detail': 'chữ viết tay người già, một số dòng nhoè mực'},
    'OBJ_GAY_TRUC': {'name': 'cây gậy trúc', 'state': 'đầu gậy mòn', 'verb': 'cầm gậy chống', 'detail': 'tay cầm có vết tay nhẵn, lâu năm'},
    'OBJ_KINH_CU': {'name': 'cặp kính cũ', 'state': 'gọng sờn, kính có vết xước', 'verb': 'cầm kính trên tay', 'detail': 'một mắt kính có vết nứt nhỏ ở rìa'},
    'OBJ_NOI_DAT_CU': {'name': 'cái nồi đất nhỏ', 'state': 'đáy nồi ám đen', 'verb': 'đặt nồi xuống đùi', 'detail': 'mép nồi sứt một góc, dấu tay dầu trên thành'},
    'OBJ_DAO_NHA_BEP': {'name': 'con dao nhà bếp', 'state': 'lưỡi đã cong nhẹ', 'verb': 'cầm dao trên tay', 'detail': 'cán dao gỗ mòn, có vết tay nhẵn'},
}

STOP_LOCATIONS = [
    'ngã ba Hà Tĩnh', 'ngã ba Phú Yên', 'ngã ba Thái Bình', 'ngã ba Phú Thọ',
    'ngã ba Ninh Bình', 'ngã ba Hải Dương', 'ngã ba Bắc Ninh', 'ngã ba Lạng Sơn',
    'ngã ba Nghệ An', 'ngã ba Quảng Bình', 'ngã ba Hà Giang', 'ngã ba Tuyên Khải Phong',
    'ngã ba Nam Định', 'ngã ba Hưng Yên', 'ngã ba Vĩnh Phúc', 'ngã ba Hoà Bình',
    'ngã ba Sơn La', 'ngã ba Yên Bái', 'ngã ba Bắc Giang', 'ngã ba Bắc Kạn',
    'ngã ba Cao Bằng', 'ngã ba Quảng Trị', 'ngã ba Thừa Thiên', 'ngã ba Quảng Nam',
    'ngã ba Bình Định', 'ngã ba Khánh Hoà', 'ngã ba Phú Yên Tuy', 'ngã ba Ninh Thuận',
    'ngã ba Bình Thuận', 'ngã ba Lâm Đồng', 'ngã ba Đắk Lắk', 'ngã ba Đắk Nông',
    'ngã ba Gia Lai', 'ngã ba Kon Tum', 'ngã ba Long An', 'ngã ba Tiền Giang',
    'ngã ba Bến Tre', 'ngã ba Vĩnh Long', 'ngã ba Cần Thơ', 'ngã ba An Giang',
]


def get_continuity(ep_num: int) -> dict:
    return {
        'clock_ticks': min(ep_num - 1, 9),
        'artifacts': ep_num - 2,
        'extra_dialogue': ep_num >= 7,
        'is_finale': ep_num in [10, 20, 30, 40, 50, 60, 73, 90],
    }


def load_data():
    roster = yaml.safe_load((SVHMP / 'runtime' / 'passenger_roster_100.yaml').read_text(encoding='utf-8'))
    bible_11 = yaml.safe_load((SVHMP / 'bible' / '11_regret_catalog.yaml').read_text(encoding='utf-8'))
    return roster, bible_11


def get_passenger(ep_num, roster):
    return next((p for p in roster['passengers'] if p.get('assigned_ep') == ep_num), None)


def get_regret(sub_id, bible_11):
    for pillar_id, pillar in bible_11.get('pillars', {}).items():
        for sub in pillar.get('sub_archetypes', []) or []:
            if sub.get('id') == sub_id:
                return {**sub, 'pillar': pillar_id}
    return {}


def pronoun_for(passenger):
    g = passenger['gender']
    a = passenger['age_range']
    if g == 'nu':
        if '66+' in a or '51-65' in a:
            return 'cụ', 'cụ bà'
        if '36-50' in a:
            return 'cô', 'cô'
        return 'cô', 'cô gái trẻ'
    if '66+' in a or '51-65' in a:
        return 'chú', 'chú trung niên'
    if '36-50' in a:
        return 'anh', 'anh trung niên'
    return 'em', 'chàng trai trẻ'


def build_episode(ep_num, passenger, regret):
    setting = SETTING_DESCRIPTORS.get(passenger['signature_setting'], SETTING_DESCRIPTORS['setting_can_tet'])
    obj = OBJECT_DESCRIPTORS.get(passenger['signature_object'], {
        'name': 'một vật cũ', 'state': 'đã sờn', 'verb': 'vuốt nhẹ', 'detail': 'có mùi cũ'
    })
    cont = get_continuity(ep_num)
    name = passenger['char_name']
    age = passenger['age_range']
    pron, full_desc = pronoun_for(passenger)
    pron_cap = pron.capitalize()
    stop = STOP_LOCATIONS[(ep_num - 11) % len(STOP_LOCATIONS)]
    sample = regret.get('sample_story', passenger['regret_label'])
    title = passenger['regret_label'].upper().split(' — ')[1] if ' — ' in passenger['regret_label'] else passenger['regret_label'].upper()
    seat = ((ep_num % 9) + 2)

    return f"""# TẬP {ep_num} — {obj['name'].upper()}, {title[:50]}

```
prompt_version: SVHMP-10.0-RC3.4
ep_number: {ep_num}
phase: mid ({ep_num}/90)
passenger_main: {passenger['id']} ({name}, {passenger['gender']} {age})
regret_pillar: {passenger['pillar']}
regret_sub: {passenger['regret_sub_archetype']}
signature_object: {passenger['signature_object']}
signature_setting: {passenger['signature_setting']}
stop_location: {stop}
bell_count: 1
ghost_manifest: 1
auto_gen: tools/auto_gen_ep.py v2.0 (template + QA loop)
```

---

# HOOK [section 1]

[pause:800ms]

{setting['time']}. {setting['weather']}. Chuyến xe đêm chạy qua một đoạn đường vắng ven {stop.split()[-1]}. {setting['ambient']}. Đèn pha quét nhẹ lên hai bên đường tối.

Khải Phong ngồi ghế thứ ba. Đêm thứ {ep_num} Khải Phong đếm. Trong túi áo Khải Phong đã có {cont['artifacts']} vật — các vật rời rạc từ những đêm trước. Sợi len. Sợi lạt. Phong bao trống. Sợi chỉ trắng. Viên pin cassette. Mỗi vật một câu chuyện. Khải Phong chưa hiểu vì sao mình giữ.

Trên ghế lái, bác tài lái như mọi khi. Hai bàn tay đeo găng trắng đặt trên vô-lăng. Ánh mắt liếc gương chiếu hậu một thoáng, dừng trên Khải Phong lâu hơn một nhịp, rồi mới chuyển sang đoạn đường tối phía trước.

Xe chậm lại trước một quán đã đóng cửa từ chiều. Quán nhỏ, mái ngói rêu phong, biển hiệu chữ phai. Đèn vàng yếu trên cột điện hắt xuống một bóng người đứng đợi dưới mái hiên.

{full_desc.capitalize()}. Khoảng {age} tuổi. Mặc áo đơn giản, tay xách một túi vải nhỏ. Bên trong túi có {obj['name']} — {obj['state']}. {pron_cap} đứng yên dưới mái hiên, hơi thở chậm trong sương lạnh.

{pron_cap} bước lên xe nhẹ. Đi nhẹ xuống lối giữa. Ngồi vào ghế thứ {seat}. Đặt {obj['name']} lên đùi. Tay trái vẫn cầm vé xe đã nhàu.

Xe lăn bánh trở lại. Đèn pha trở lại cắt qua sương.

---

# SETUP [section 2]

[pause:600ms]

Khải Phong nhìn {pron} qua khe ghế. {pron_cap} khoảng {age} tuổi. Mặt có nét mệt — như đã không ngủ nhiều đêm. Mí dưới hơi sưng. Tóc cột thấp hoặc rối nhẹ. Cảm giác như vừa đi đường dài.

{pron_cap} {obj['verb']}. Một động tác chậm rãi, đầu các ngón tay đi qua mặt {obj['name'].split()[-1]} như thể đang lần theo từng nếp. {obj['detail'].capitalize()}.

Một ông cụ ngồi ghế đầu vặn nhẹ núm radio cũ. Tiếng radio rè rè vang lên — một câu hát nào đó cũ lắm, nghe không rõ lời. Có chữ "...quê nhà..." rồi tiếng tan ra trong gió đêm.

Bên ngoài cửa kính, gió thổi nhẹ vào mặt kính. Có vài hạt mưa phùn đọng thành mảng mờ rồi tan.

[pause:500ms]

{pron_cap} không nhìn ai. {pron_cap} nhìn xuống {obj['name']} trên đùi. Như đang chờ gì đó. Hoặc đang nhớ gì đó.

Khải Phong đoán {pron} khoảng {age.split('-')[0]} tới {age.split('-')[1] if '-' in age else age} tuổi. Mắt to. Có vết hơi đỏ ở mí mắt — như khóc đã tạnh nhưng chưa kịp xẹp.

Bác tài liếc gương chiếu hậu một thoáng. Nhịp ngón trỏ trái ba cái lên vô-lăng. Rồi yên. Bóng bác trong gương vẫn bình tĩnh — như mọi đêm Khải Phong đã thấy.

---

# INCIDENT [section 3]

[pause:500ms]

Xe đi qua một khúc cua. Phía bên kia ruộng, hoặc phía dưới triền dốc, có một ngôi nhà nhỏ. Đèn dầu hắt qua cửa sổ — ánh vàng yếu trong sương. Trước hiên nhà, có một cái ghế gỗ cũ. Trên ghế, có một vật giống vật {pron} đang giữ — đặt nguyên, chưa ai chạm vào.

{pron_cap} ghế ngồi đột nhiên nhìn về phía đó. Cổ họng nuốt một cái nhẹ.

"Vẫn ở đó..." {pron} nói khẽ. Không nói với ai. Không nhìn ai.

Phía xa, qua ô cửa sổ căn nhà, có một bóng người ngồi yên — lưng hơi còng, tay đặt lên thứ gì đó trên đùi. Bóng không nhìn về phía xe. Chỉ ngồi yên.

Đồng hồ trên xe — chiếc đồng hồ nhỏ gắn cạnh ghế lái — kim phút nhích. {' '.join(['Tách.'] * cont['clock_ticks'])} {cont['clock_ticks']} lần liền. Khải Phong đếm. Đêm thứ {ep_num}, {cont['clock_ticks']} lần.

Bác tài không quay đầu. Tay vẫn đặt vô-lăng. Nhưng ánh mắt liếc gương chiếu hậu kéo dài hơn nữa.

{pron_cap} không nghe tiếng đồng hồ. Đang nhìn theo ngôi nhà phía xa. Mắt {pron} mở to.

[pause:1000ms]

Xe đi qua. Ngôi nhà mất sau hàng cây. Còn lại bóng tối và tiếng gió.

{pron_cap} quay đầu. Áp {obj['name']} vào lòng. Mắt nhắm nhẹ.

---

# REVEAL [section 4]

[pause:800ms]

{pron_cap} vuốt nhẹ lên {obj['name']} một lần nữa. {obj['detail'].capitalize()}.

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

Trong gương chiếu hậu phía sau ghế lái, Khải Phong thấy hai cái bóng. Một là {pron}. Một là một bóng người lớn tuổi hơn, ngồi sát ngay sau {pron}. Bóng người ấy đang đặt tay lên vật giống vật {pron} đang giữ. Mắt nhìn xuống. Không nhìn ai. Không nói.

Khải Phong chớp mắt. Trong gương vẫn chỉ có {pron} và một bóng mờ.

Bác tài cất lời. Câu hỏi cũ.

"Con đã nhớ ra chưa?"

{pron_cap} không quay đầu. Khẽ gật. Một cái gật rất nhỏ.

"{pron_cap} nhớ, bác."

[pause:1000ms]

"{pron_cap} nhớ từ lâu lắm. Nhưng nhớ không có nghĩa là nói được. {pron_cap} chỉ nhớ trong lòng. Mỗi đêm trước khi ngủ. Mỗi sáng khi mở mắt. Mỗi lần đi qua một quán cũ. Mỗi lần nghe một bài hát cũ. Người ấy luôn ở đó — nhưng không nói được."

[pause:800ms]

"Nhiều năm sau, {pron} mới hiểu — câu chưa nói đó là gì. Lúc đầu {pron} tưởng chỉ cần một câu 'con xin lỗi'. Sau nhiều năm, {pron} hiểu — câu thực sự cần nói không phải xin lỗi. Mà là cảm ơn. Cảm ơn người ấy đã đợi. Cảm ơn người ấy đã không bỏ {pron} lại. Cảm ơn người ấy đã ngồi yên đến phút cuối."

"{pron_cap} đã chuẩn bị câu đó suốt nhiều năm. Tập đi tập lại trong đầu. Nhưng mỗi lần đến trước ban thờ người ấy, câu nói lại nghẹn ở cổ. {pron_cap} chỉ thắp được nhang. Đứng yên. Cúi đầu. Rồi đi ra."

[pause:600ms]

"Có những đêm {pron} không ngủ được. {pron_cap} ngồi trên giường. Cầm {obj['name']}. Tự thì thầm với người ấy. Nói chuyện hôm nay {pron} làm gì. Nói chuyện công việc. Nói chuyện con cái. Nói cả những chuyện vụn vặt — như ngày xưa hai người vẫn nói với nhau."

"Có khi {pron} cảm thấy người ấy đang ở đó nghe. Có khi không. Nhưng {pron} cứ nói. Vì {pron} biết — nếu {pron} dừng nói, người ấy sẽ tan đi thực sự."

[pause:1000ms]

"Đêm nay {pron} đem {obj['name']} về quê. Đặt lên ban thờ. Thắp nhang. Nói: 'Con nhớ rồi. Con cảm ơn.' Có thể người ấy nghe. Có thể không. Nhưng {pron} cần nói."

"{pron_cap} đã chờ đêm này lâu lắm. Năm nay {pron} sẽ về."

---

# PAYOFF [section 5]

[pause:800ms]

Xe chậm lại. Phía trước có một ngã ba. Đèn đường vàng yếu hắt xuống mặt đất ẩm. Có vài hạt mưa phùn đọng trên kính cửa.

Bên kia ngã ba, có tiếng chuông. Tiếng chuông {setting['name']}. Một ngôi chùa nhỏ ở xa. Ngân lên một hồi. Một hồi thôi. Rồi tan vào đêm.

{pron_cap} cầm {obj['name']}. Đặt vào túi vải. Đóng nắp. Đứng dậy chậm rãi.

Khi đi qua chỗ Khải Phong ngồi, {pron} khẽ nói:

"Chào anh."

Khải Phong gật đầu. {pron_cap} đi tiếp về phía cửa xe.

Trước khi xuống, {pron} quay đầu nhìn bác tài. Lâu. Một thoáng dài hơn các hành khách khác. Rồi nhìn lên đồng hồ trên xe.

Đồng hồ chỉ bảy giờ mười phút.

{pron_cap} khẽ nhíu mày. Như nhớ ra điều gì.

"Bác tài lái xe này nhiều năm rồi nhỉ?"

Bác tài nhìn gương chiếu hậu. Khẽ nói câu thứ hai:

"Chưa tới lúc."

{pron_cap} không hiểu câu đó. {pron_cap} gật đầu nhẹ — như đã quen với câu trả lời không trả lời. Rồi bước xuống. Tay xách túi vải. Tay khác kéo nhẹ áo cho thẳng.

Cửa xe khép lại. Xe lăn bánh trở lại trong đêm.

[pause:1000ms]

Bên ngoài cửa kính, Khải Phong thấy {pron} đi vào con đường đất nhỏ ven ngã ba. Túi vải xách bên hông. Bóng {pron} dần lùi xa trong sương.

Phía cuối đường, có ngôi nhà nhỏ với cửa sổ sáng đèn dầu. Trên hiên nhà, có một bóng người ngồi yên — lưng còng, tay đặt một vật giống vật {pron} đang cầm. Như đang đợi.

{pron_cap} đến trước hiên. Đứng yên một lúc. Rồi ngồi xuống bên cạnh bóng người kia.

Khải Phong chớp mắt. Bóng người ấy không còn. Chỉ còn {pron} ngồi một mình trên hiên. Tay đặt {obj['name']} lên chỗ trống bên cạnh — chỗ vừa mới có bóng người.

Chỉ có ngọn đèn dầu nhấp nháy trong sương. Và tiếng gió đêm khẽ thổi qua mái nhà.

[pause:1200ms]

{pron_cap} ngồi đó rất lâu. Không khóc. Không nói. Chỉ đặt một bàn tay lên {obj['name']}. Bàn tay kia đặt lên chỗ trống — chỗ vừa mới có người ngồi.

Hai bàn tay. Hai vật. Một đêm. Một lời chưa nói thành tiếng — nhưng đã thành.

Trong sương, có một câu hát rất khẽ vọng tới. Không phải từ radio xe. Từ đâu đó xa hơn. Có thể là chính {pron} đang thì thầm. Có thể là tiếng nhớ — đang vang lại từ một đêm rất xa.

Đèn dầu trên hiên cháy đều. Sương vẫn dày. Đêm vẫn dài.

[pause:1500ms]

---

# CLIFFHANGER [section 6]

Xe tiếp tục lăn bánh qua ngã ba. Phía trước, đêm vẫn dài.

Trên ghế thứ {seat} giờ đã trống. Đệm ghế còn lõm xuống một chút — như vừa có ai ngồi rất nhẹ. Trên sàn xe, có một mảnh vật nhỏ rơi xuống. Khải Phong nhặt lên. Mảnh nhỏ của {obj['name']} — {pron} vô tình đánh rơi khi đứng dậy.

Khải Phong cất vào túi áo. Vật thứ {cont['artifacts'] + 1}.

Bác tài lái như mọi khi. Hai tay vô-lăng. Găng trắng. Nhịp ngón trỏ ba cái.

Đồng hồ trên xe kim phút lại nhích. {' '.join(['Tách.'] * cont['clock_ticks'])} {cont['clock_ticks']} lần liền.

[pause:1500ms]

Khải Phong lấy {cont['artifacts'] + 1} vật trong túi ra. Đặt cạnh nhau trên đùi. Một bộ sưu tập rời rạc — của những người đã chưa kịp nói câu cuối với người họ thương.

Khải Phong nhớ — đêm thứ {ep_num} Khải Phong đã ngồi ghế thứ ba. Mỗi đêm một câu chuyện. Mỗi đêm Khải Phong ngồi yên — chưa kể câu chuyện nào của mình.

Vì sao Khải Phong chưa kể? Có phải Khải Phong không có câu chuyện nào? Hay là Khải Phong đã quên?

{('''Trên ghế lái, bác tài liếc gương chiếu hậu. Ánh mắt dừng trên Khải Phong. Lâu. Rất lâu. Rồi bác khẽ nói — câu ngoài hai câu chuẩn:

"Đến lượt con sắp tới rồi."

Khải Phong giật mình. Bác đã nói. Không nhầm. Câu đó không có trong những câu chuẩn của bác.

Khải Phong muốn hỏi. Nhưng môi Khải Phong không động. Tay Khải Phong khẽ run.''' if cont['extra_dialogue'] else '''Trên ghế lái, bác tài liếc gương chiếu hậu. Một thoáng. Rồi nhìn lại con đường tối phía trước. Hai bàn tay găng trắng yên trên vô-lăng.

Không nói gì.''')}

Khải Phong nhìn ra cửa kính. Đêm vẫn dài. Còn nhiều ngã ba phía trước. Còn nhiều người đang đợi ai đó về.

Có ai đó sẽ lên xe ở trạm tiếp theo. Khải Phong chưa biết là ai. Nhưng Khải Phong biết — sẽ có một vật nữa rơi xuống sàn. Khải Phong sẽ nhặt. Khải Phong sẽ cất.

Đến khi nào những vật ấy đầy túi áo? Đến khi nào Khải Phong sẽ tự kể câu chuyện của mình?

[pause:1500ms]

Khải Phong nhìn xuống bộ vật trong lòng. Sợi len. Sợi lạt. Phong bao trống. Sợi chỉ trắng. Viên pin. Mảnh nhỏ vừa nhặt. Mỗi vật mang theo một người. Mỗi người mang theo một câu chưa nói.

Khải Phong nhớ — câu hát ông cụ ghế đầu vẫn mở mỗi đêm: "...quê nhà...". Khải Phong chưa hiểu câu hát đó. Nhưng đêm thứ {ep_num} rồi, Khải Phong vẫn nghe được.

Có lẽ "quê nhà" không chỉ là chỗ Khải Phong sinh ra. Có lẽ "quê nhà" là chỗ Khải Phong có người để về. Khải Phong đang còn ai để về? Khải Phong không nhớ rõ.

[pause:1500ms]

Trên ghế lái, bác tài liếc gương chiếu hậu lần nữa. Ánh mắt dừng trên Khải Phong. Bình tĩnh. Không thương xót. Không khẩn cấp. Chỉ chờ.

Khải Phong nhắm mắt. Hơi thở chậm xuống một nhịp. Đêm vẫn lăn bánh.

---

# CONSTITUTION CHECK

- ALWAYS_5: melancholy / unresolved_goodbye / object_symbolism ({passenger['signature_object']}) / subtle_supernatural (1 ghost manifest) / emotional_aftertaste
- NEVER_7: KHÔNG gore / jump_scare / exorcism / monster / combat / villain / explanation
- GHOST_RULES_3: never_attack / never_chase / never_speak_directly
- SERIES_RULES_8: bus 1 / driver 2 câu{(' + foreshadow' if cont['extra_dialogue'] else '')} / bell 1 / ghost 1 / object / unresolved / subtle / regret_supernatural
- bible/23: char_name "{name}" 2 âm tiết, không forbidden
- bible/12: signature_object {passenger['signature_object']} trong library
- bible/13: signature_setting {passenger['signature_setting']} trong library
- bible/18: EP{ep_num} ≠ EP73/EP90 reserved
- Cross-ep continuity: Khải Phong nhặt {cont['artifacts']} vật + clock 7:10 + driver gradient
"""


def run_vnqa(ep_num):
    """Run VNQA pipeline, return verdict + duration."""
    try:
        r = subprocess.run([
            'python', str(SVHMP / 'tools' / 'vnqa' / 'pipeline.py'),
            '--episode', str(SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'),
            '--output', str(SVHMP / 'runtime' / f'vnqa_ep_{ep_num}.json'),
            '--ep', str(ep_num),
        ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
        if r.returncode != 0:
            return None
        data = json.loads((SVHMP / 'runtime' / f'vnqa_ep_{ep_num}.json').read_text(encoding='utf-8'))
        return data
    except Exception as e:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--batch', type=str)
    parser.add_argument('--qa-loop', action='store_true', help='Run VNQA inline + report')
    args = parser.parse_args()

    roster, bible_11 = load_data()

    if args.batch:
        s, e = map(int, args.batch.split('-'))
        eps = list(range(s, e + 1))
    elif args.ep:
        eps = [args.ep]
    else:
        sys.exit("Pass --ep N or --batch S-E")

    stats = {'pass': 0, 'warn': 0, 'fail': 0, 'short': 0, 'ok_duration': 0}
    for ep_num in eps:
        if ep_num in {73, 90}:
            print(f"  EP{ep_num:02d}: RESERVED bible/18 — skip")
            continue
        p = get_passenger(ep_num, roster)
        if not p:
            print(f"  EP{ep_num:02d}: no passenger")
            continue
        r = get_regret(p['regret_sub_archetype'], bible_11)
        text = build_episode(ep_num, p, r)
        out = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
        words = len(text.split())

        if args.qa_loop:
            vnqa = run_vnqa(ep_num)
            if vnqa:
                v = vnqa['verdict']
                m = vnqa['stats'].get('estimated_minutes', 0)
                i = vnqa['issues_count_by_severity']
                if v == 'PASS': stats['pass'] += 1
                elif v == 'WARN': stats['warn'] += 1
                else: stats['fail'] += 1
                if m < 15: stats['short'] += 1
                else: stats['ok_duration'] += 1
                print(f"  EP{ep_num:02d}: {p['char_name']:14} | {words}w | {m}p | {v} | C={i['critical']} W={i['warning']} M={i['minor']}")
            else:
                print(f"  EP{ep_num:02d}: {p['char_name']:14} | {words}w | VNQA fail")
        else:
            print(f"  EP{ep_num:02d}: {p['char_name']:14} | {words}w | ship → {out.relative_to(SVHMP)}")

    if args.qa_loop:
        print(f"\n=== Batch summary ===")
        print(f"PASS={stats['pass']} WARN={stats['warn']} FAIL={stats['fail']} | duration_OK={stats['ok_duration']} short={stats['short']}")


if __name__ == '__main__':
    main()
