# BP7 REPORT — Narrative Architecture (candidate, chờ audit 7 bước + Mr.Long ký)

## Số đo (REALITY ANCHOR — luật 9: validator PASS trên dữ liệu THẬT)

| Số đo | Giá trị | Nguồn máy |
|---|---|---|
| Cấp cấu trúc khai | **6/6** (Scene/Act/Episode/Season/Series/Ending) | `bp7_narrative_check.py` máy đếm |
| Cultural item khai | **7/7** (culture 3 + belief 2 + ritual 2, khớp bp2/domain_specs.yaml) | máy đếm |
| Curve application khai | **5/5** (emotion/fear/suspense/reveal/pacing → bp6 knob) | máy đếm |
| Checker trên data thật | **exit 0, 0 violation** (sau khi bible/00 R142/R143 dup-key được fix `c735e36`) | `tools/bp7_narrative_check.py` |
| Mutation test | **17/17 pass** | `tests/test_bp7_narrative.py` |
| Episode component order | Khớp CHÍNH XÁC `bible/01_narrative_structure.yaml#bimodal_sentence_length_per_section.pattern_per_section` | check độc lập bible/00 |

## Sự cố phát hiện trong lúc build (đã route đúng kênh)

Khi build `check_story_structure` (Ending level trỏ `bible/00_constitution.yaml#ENDING_RULES`), checker (loader strict single-impl, đúng chuẩn dự án) phát hiện **bible/00 có 2 DUP-KEY thật** (`rule_R142_kill_switch` dòng 2007/2034, `rule_R143_multi_pass_agent` dòng 2012/2040 — nội dung khác nhau, `yaml.safe_load` mặc định nuốt bản đầu im lặng). Đã báo kiểm duyệt/Mr.Long ngay, KHÔNG tự sửa (bible writer = mr_long only). Kiểm duyệt xác minh + mở rộng tìm thêm R143 + fix `check_rule_id_free.py` (bug bỏ sót định dạng `rule_R{N}_`) + Mr.Long quyết nội dung → fix `c735e36` "per Mr.Long authorization". Sau rebase, checker PASS sạch.

## Deliverables

1. `governance/blueprint/bp7/story_structure.yaml` — 6 cấp Scene→Act→Episode→Season→Series→Ending. Episode: 6 component bắt buộc (HOOK/SETUP/INCIDENT/REVEAL/PAYOFF/CLIFFHANGER) TRỎ `bible/01` (không chép). Ending TRỎ `bible/00#ENDING_RULES`. Act/Scene: chưa có field-hoá riêng trong BP2 (chỉ `[season_plan, episode_plan, scene]` entities) — giữ `planned`, KHÔNG bịa component/rule cho Act.
2. `governance/blueprint/bp7/cultural_spec.yaml` — 7 item culture/belief/ritual. Đã đọc TOÀN BỘ `bible/02_lore_db.yaml` (bằng chứng trong file): 0 nội dung phong tục/tín ngưỡng/nghi thức trong lore hiện tại → cả 7 item giữ `planned`, mirror đúng bp2/domain_specs.yaml (không nhân đôi khai báo).
3. `governance/blueprint/bp7/pacing_format.yaml` — 5 curve_application (emotion/fear/suspense/reveal/pacing) trỏ đúng knob_id `bp6/decision_contract.yaml` (đã lock v1.0). KHÔNG chứa số — numeric-leak scan toàn file NGAY TỪ ĐẦU (tái sử dụng `_numeric_leaks` từ `bp6_decision_check.py`, không viết lại — rút kinh nghiệm audit BP6 4/7: lỗ hổng scan-thiếu từng lọt 1 lần, BP7 không lặp lại).
4. `governance/blueprint/bp7/00_narrative.md` — 11-element theo mẫu BP4/BP6.
5. `tools/bp7_narrative_check.py` — DUP-KEY loader single-impl + version khớp 3 file; component-order-vs-bible01; facet-ma cultural; numeric-leak + curve-ma pacing; planned 5-metadata; SoT exists path+key resolve thật.
6. `tests/test_bp7_narrative.py` — 17 test: đủ 3 đòn TASK báo trước (xoá REVEAL → FAIL, cultural facet-ma → FAIL, pacing hardcode → FAIL) + thứ tự sai bible/01, curve-ma, DUP-KEY, planned-thiếu-metadata, sot-phantom.

## Ghi chú cho auditor

- Act không có component/rule riêng — KHÔNG phải thiếu sót, là do BP2 entity list đã đóng chưa có "act" (RFC mới nếu cần field-hoá).
- Registry: `bp7_narrative: candidate` (1 dòng, không dup-key — auditor REPLACE in-place khi lock theo ROOT-FIX 8af9682).
- Builder không kết luận PASS/FREEZE — chỉ READY FOR AUDIT.
