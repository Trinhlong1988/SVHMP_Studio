# CMD AUDIT — PHỤ LỤC RIÊNG G3 (Dialogue)

> KHÔNG thay thế `CMD_AUDIT_PROTOCOL.md` (7 bước chung — vẫn bắt buộc chạy đủ, không rút gọn).
> File này là checkpoint BỔ SUNG, viết TRƯỚC khi build (trước khi CMD_BUILD nộp báo cáo G3) —
> cùng khuôn mẫu `CMD_AUDIT_G4_G5.md` / `CMD_AUDIT_G6.md`, tránh thiên vị xác nhận (kiểm duyệt
> không tự chế tiêu chí SAU khi thấy kết quả). Nguồn rủi ro: đọc trực tiếp
> `governance/blueprint/blueprint_domains.yaml` (khối `dialogue`, dòng 428-450) +
> `governance/pack2/08_artifact_contract.md` (dòng "G3 dialogue") +
> 4 tool dialogue đã tồn tại (`tools/audit_dialogue_hierarchy.py`,
> `tools/audit_driver_dialogue_context.py`, `tools/auto_fix_dialogue_hierarchy.py`,
> `tools/qa_dialogue_identity.py`, `tools/dialog_voice_validator.py`) + `docs/ENVIRONMENT_GOTCHAS.md`
> G1-G12 + memory lessons + 3 vòng skeptic review độc lập trên `TASK_G3_DIALOGUE.md` (5/7:
> R211-dup-check, bible-immutability-check, BP3-dependency-check — 2 vòng đầu/cuối tìm được lỗi
> thật, đã phản ánh vào G3-11/G3-12/G3-13 dưới đây).

## THỨ TỰ CHẠY (bắt buộc, không đảo)
1. `CMD_AUDIT_PROTOCOL.md` đủ 7 bước (B0-B7) trên worktree sạch từ `origin/main`.
2. Bảng checkpoint domain-specific dưới đây — MỌI dòng phải có verdict, không bỏ sót.
3. Tổng hợp theo QUY TẮC PHÂN ĐỊNH — 1 FAIL ở nhóm build-ahead/R211 (G3-1, G3-2) hoặc bible-immutable
   (G3-8) hoặc governance-gap-chưa-đóng (G3-12) = bác toàn bộ pack, không có "PASS có điều kiện" cho
   các nhóm này.

## QUY TẮC PHÂN ĐỊNH 100-ĐÚNG / 100-SAI (không có mức giữa "có vẻ", "chắc là")
- **100% ĐÚNG**: có lệnh máy chạy thật + exit code + đối chiếu dòng code/dữ liệu cụ thể xác nhận
  đúng claim, VÀ đã thử bắn mutation ngược mà không lọt.
- **100% SAI**: có ≥1 bằng chứng cụ thể (dòng code/exit-code/diff) mâu thuẫn trực tiếp với claim.
  Dù chỉ 1 điểm sai, toàn bộ checkpoint đó bị bác — không cộng điểm trung bình.
- **CHƯA ĐỦ BẰNG CHỨNG**: khi thiếu công cụ đo/quyền truy cập để kết luận — PHẢI ghi rõ thiếu gì,
  KHÔNG được mặc định quy về PASS.
- Nhóm **build-ahead R211** (G3-1, G3-2), nhóm **bible immutable** (G3-8), và nhóm
  **governance-gap-chưa-đóng** (G3-12) KHÔNG có mức "tạm chấp nhận" — đây là các lớp lỗi đã tái diễn
  nhiều lần nhất trong lịch sử dự án này (2 lớp đầu) hoặc mới phát hiện qua skeptic review và có
  cùng cơ chế RFC-gate như G3-1 (lớp thứ 3).

## BẢNG RỦI RO ĐÃ BIẾT ← BÀI HỌC LỊCH SỬ (viết trước khi có kết quả build)

| # | Rủi ro cụ thể | Bài học lịch sử áp dụng | Cách kiểm — tiêu chí 100đ/100s |
|---|---|---|---|
| G3-1 | `tools/dialogue_manager.py` (D-manager của domain `dialogue`) bị build ra trong khi `blueprint_domains.yaml` dòng 435-441 khai rõ `status: planned` với `blocking_dependency: "quyet dinh tach/giu chung voi character_manager (Change Request Gate R211)"` — build-ahead khi quyết định tách/giữ-chung CHƯA có | REALITY ANCHOR (luật 9 MASTER) + lesson G6-1 (build-ahead vi phạm blocking_dependency đã khai sẵn trong bảng domain) | `git log` tìm PING/commit có trích dẫn rõ Mr.Long đã quyết "tách" hay "giữ chung với character_manager" TRƯỚC ngày commit tạo `tools/dialogue_manager.py`. Có file mới nhưng KHÔNG tìm thấy quyết định tường minh (chỉ có "làm G3 đi" chung chung) = **100% SAI, build-ahead** |
| G3-2 | Generator/validator dialect viết engine audit-pronoun riêng thay vì tái dùng 4 tool đã tồn tại thật trên disk: `tools/audit_dialogue_hierarchy.py` (R48 hierarchy pronoun), `tools/audit_driver_dialogue_context.py` (R174 driver context), `tools/qa_dialogue_identity.py` (R191 speaker identity), `tools/auto_fix_dialogue_hierarchy.py` — R211 cấm nhân đôi | R211 + lesson-claim-equals-work ("built"≠"wired", phải grep điểm gọi thật) | Đọc diff code G3 mới — logic phát hiện pronoun-ambiguity / driver-context / speaker-identity PHẢI **import hoặc gọi** 1 trong 4 file trên (không phải chỉ nhắc tên trong docstring/comment). Có hàm mới làm lại đúng việc `detect_pronoun_issues_in_quote()`/`audit_text()`/`mfcc_embedding()` đã làm = 100% SAI |
| G3-3 | Dialect/giọng vùng miền dùng 1 bảng enum vùng-miền THỨ BA, trong khi 2 nguồn đã tồn tại **đã lệch nhau sẵn** (phát hiện thật, không giả định): `tools/dialog_voice_validator.py::REGIONS` có **5 vùng** `{bac, trung, nam, tay, do_thi}` với `HOMETOWN_REGION` (key lowercase, có cả xã Tây Nam Bộ) — còn `tools/migrate_roster_v2.py::HOME`/`REGIONS` (tool `roster_validator.py` import làm "single-source" cho C2 quê↔giọng R210) chỉ có **3 vùng** `{bac, trung, nam}`, key viết hoa, KHÔNG có 'tay' riêng | R211 (single-source) + lesson-audio-first-character-schema (giọng gắn quê, không suy luận/bịa enum) | Grep giá trị `region_dialect` dùng trong code/schema mới của G3 — nếu vùng `'tay'` hoặc `'do_thi'` xuất hiện: xác nhận roster hiện dùng nguồn nào (`migrate_roster_v2.HOME` 3-vùng hay `dialog_voice_validator.REGIONS` 5-vùng); G3 KHÔNG được tự chọn ngầm 1 trong 2 mà không ghi rõ + xin Mr.Long chốt 1 SSOT duy nhất — chọn ngầm hoặc thêm bảng thứ 3 = 100% SAI. **(2 nguồn lệch nhau là fact đã đọc trong code, việc chọn cái nào SSOT cần Boss xác nhận)** |
| G3-4 | `audit_rule` của domain `dialogue` (blueprint_domains.yaml dòng 450) khai "CAM sinh dialog khi focal char thieu Tier1 (R210)" nhưng generator thật KHÔNG check Tier1-completeness trước khi sinh câu thoại (named nhưng không enforced) | lesson-enforcer-claim-vs-behavior (named≠enforced, ca pack4) | Mutation: tạo 1 nhân vật thiếu field Tier1 mandatory (`bible/37_character_schema.yaml`) → gọi generator G3 sinh dialogue cho nhân vật đó → PHẢI thấy generator raise/refuse (không sinh). Sinh ra dialogue bình thường dù thiếu Tier1 = 100% SAI |
| G3-5 | Cùng dòng `audit_rule`: "thoai qua dialog_voice_validator" — generator CLAIM đã validate nhưng code thật không gọi `dialog_voice_validator.validate()`/`validate_line()`/`validate_profile()` ở đúng điểm sinh câu thoại | lesson-claim-equals-work (built≠wired, phải grep điểm thực thi) | `grep -rn "dialog_voice_validator" tools/dialogue_manager.py <generator mới>` — phải thấy **import + call** thật (không phải chỉ 1 dòng comment nhắc tên). Mutation ngược: cho 1 câu thoại rò rỉ marker vùng khác (vd nhân vật `region_dialect=nam` nói "nhé"/"nhỉ" — marker độc quyền `bac` theo `EXCLUSIVE` dict) → generator PHẢI reject/flag `DIALECT_LEAK`. Sinh trót lọt = 100% SAI |
| G3-6 | Golden set dialogue (`08_artifact_contract.md` dòng "G3 dialogue: generator · validator dialect · golden set · test confusion") dựng bằng dữ liệu tự bịa thay vì bằng chứng thật — `bible/31_golden_samples.yaml` hiện CHỈ có 1 dòng liên quan dialogue ("Bác_tài: găng tay trắng + 2 lock dialogues", dòng 37), quá mỏng để làm golden set cho generator mới | lesson-audio-first-character-schema (confusion-matrix đo từ dữ liệu thật 500/500, không suy luận) + lesson-enterprise-audit (auditor đọc, resolve evidence thật không grep-đoán) | Mở TỪNG evidence path golden set G3 trích dẫn — path/key PHẢI resolve ra giá trị thật tồn tại (không phải chỉ field có tên). Nếu golden set mới tự chế ra ngoài `bible/31` mà không có transcript/audio thật đối chiếu (vd trích từ `output/ep_*/episode.md` đã render thật) = 100% SAI phần đó |
| G3-7 | Test confusion (yêu cầu deliverable) chạy trên input tự sinh/giả lập thay vì dữ liệu thật đã tồn tại — 4 tool audit dialogue hiện có (`audit_dialogue_hierarchy.py`, `audit_driver_dialogue_context.py`) quét thẳng `output/ep_*/episode.md` — nếu G3 mới sinh dialogue ở path/format khác (schema mới, không phải `episode.md`) thì các tool "tái dùng" này sẽ luôn thấy **0 file → PASS RỖNG**, che giấu vi phạm thật | lesson-dont-downplay-rigor (cấm "xong" chỉ vì máy PASS rỗng) | Chạy `python tools/audit_dialogue_hierarchy.py --summary` và `python tools/audit_driver_dialogue_context.py --all` NGAY SAU khi generator G3 sinh nội dung mới — đếm số EP/file thực sự được quét (`Total ... EPs affected`). Số quét = 0 trong khi generator đã sinh dialogue thật ở nơi khác = 100% SAI (tool tồn tại, chạy exit 0, nhưng không kiểm được gì) |
| G3-8 | `bible/22_anti_slop_vi.yaml` / `bible/06_lexical_style.yaml` / `bible/15_voice_bible.yaml` (source_of_truth domain dialogue, `writer: mr_long`, `lock_type: bible`) bị sửa trực tiếp để "cho khớp" output generator thay vì qua `governance/proposals/` | lesson-lock-ceremony-and-regen (bible immutable, cần "per Mr.Long authorization" tường minh trong commit) | `git log --follow` 3 file trên kể từ lúc G3 bắt đầu build — mọi commit sửa PHẢI có cụm "per Mr.Long authorization" trong message. Thiếu = 100% SAI dù nội dung sửa đúng kỹ thuật |
| G3-9 | Generator/manager dialogue vô tình import/gọi tool thuộc `production`/`publisher` (vd script render/publish) — vi phạm `forbidden_dependencies: [production, publisher]` khai rõ trong blueprint_domains.yaml dòng 449 | R211 + dependency_rules (bp3) | `grep -rn "import\|render\|publish" <file G3 mới>` — không được thấy import trực tiếp module thuộc domain `production`/`publisher`. Có = 100% SAI ngay, không cần xét tiếp checkpoint khác |
| G3-10 | Generator sinh biến thể diễn đạt khác (đồng nghĩa nhưng đổi từ) cho 2 câu LOCK Q1/Q2 (`bible/02_lore_db.yaml:18-20`, enforcer `tools/audit_driver_dialogue_context.py` R174) — enforcer chỉ match **literal substring** (`Q1_VARIANTS`/`Q2_VARIANTS` hardcode "Con đã nhớ ra chưa"/"Chưa tới lúc", không synonym-aware) → biến thể lọt qua mà enforcer không phát hiện được (false-negative có sẵn trong chính enforcer, generator mới dễ vô tình khai thác) | lesson-enterprise-audit (đọc code enforcer thật, không tin tên rule) | Cho generator G3 chạy trên 1 case passenger có trigger Q2 nhưng đổi câu LOCK thành từ đồng nghĩa (vd "Giờ chưa tới đâu") → `audit_driver_dialogue_context.py` PHẢI KHÔNG bắt được gì (vì literal-match) — xác nhận đây là lỗ hổng CÓ SẴN của enforcer, không phải lỗi G3; G3 KHÔNG được lấy "audit_driver_dialogue_context.py exit 0" làm bằng chứng "2 câu LOCK giữ nguyên" nếu diff thật cho thấy câu đã bị đổi từ |
| Cross-G2/G3 | G3 (dialogue) và G2 (character audit vá gap) cùng sửa `bible/37_character_schema.yaml` (schema DÙNG CHUNG — dialogue.schema = bible/37 theo dòng 442) trong cùng cửa sổ thời gian mà không claim/thông báo nhau | PACK CLAIM luật 11 + gotcha G6 (claim chỉ chặn trùng-pack, KHÔNG chặn 2 pack khác nhau cùng sửa 1 file chung) | `git log --all --oneline -- bible/37_character_schema.yaml` từ lúc 2 claim (G2, G3) đang mở — 2 commit từ 2 session khác nhau sửa CÙNG vùng dòng gần nhau → cần Boss trọng tài, KHÔNG tự ý merge cả 2 |
| Cross-G3/G6 | Generator G3 tự quyết định tỉ lệ thoại/trần thuật (dialogue/narration ratio) ngay trong lúc sinh, trong khi `non_responsibility` của domain dialogue khai rõ "KHONG quyet ratio thoai/narration (decision_engine)" — đây là trách nhiệm G6 (Story Planner: "Dialogue/Narration Ratio" theo `master_roadmap.md` mục G6) | R211 (ranh giới domain, không lấn trách nhiệm domain khác) | Đọc code G3 — không được có logic tự tính/áp đặt tỉ lệ số-lượng-thoại theo scene; mọi ratio PHẢI nhận làm **input** từ decision_engine (packet có `status: planned`/giá trị thật do G6 cấp), KHÔNG tự suy ra ngầm bên trong dialogue_manager |
| G3-11 | Bảng "NỀN ĐÃ CÓ"/D0 baseline của `TASK_G3_DIALOGUE.md` (hoặc báo cáo build) liệt `ci_gate.py` chỉ có 4 stage, hoặc claim `architecture_registry.yaml` "0 hit" cho từ khoá `dialogue` — cả 2 claim này SAI theo đối chiếu trực tiếp file thật: `ci_gate.py` có **11 entry** trong `CHECKS` (`registry, blueprint, R199_tail, R203_conf, R205_char, R206_voice, R207_canon, R208_age, project_config, G2_roster, g5_supernatural, G4_world`), và `architecture_registry.yaml` đã có `dependency_map` edge "Character -> Dialogue"/"Dialogue -> TTS" cùng `tests/test_dialogue_appropriateness_1000_r208.py` (R208, confusion-test age-slang 1000 case, 0 FN/FP) đăng ký dưới domain `character` | lesson-claim-equals-work (nhãn phải khớp diff/hiện trạng thật) + phát hiện skeptic-1 (R211-dup-check, 2026-07-05) | Đối chiếu D0 baseline log với `tools/ci_gate.py` dòng 19-32 (đếm đúng số entry `CHECKS`, phải ra 11 trước khi G3 wire thêm, 12 sau khi wire) và `grep -i dialogue governance/architecture_registry.yaml` (phải ra ≥2 vùng khớp: `dependency_map` + đường dẫn R208). Baseline/report thiếu hoặc liệt sai số liệu này = 100% SAI phần đó, không tin các số liệu D0 khác của cùng báo cáo cho tới khi sửa |
| G3-12 | D3 (pass-through 2 câu LOCK bác tài, đọc `bible/02_lore_db.yaml` — SoT domain `world`) hoặc D5-Nguồn-B (trích `bible/31_golden_samples.yaml` — SoT domain `audio`) được tính vào DoD/report là số liệu CHÍNH THỨC trong khi `bp3/dependency_detail.yaml` chưa có `dep__dialogue__world`/`dep__dialogue__audio`, và `dialogue` không có mặt trong `world.reader` (dòng 108) / `audio.reader` (dòng 685) của `blueprint_domains.yaml` | phát hiện skeptic-3 (BP3-dependency-check, 2026-07-05) + R211/kỷ luật khai phụ thuộc trước khi dùng (cùng lớp rủi ro với G3-1: dùng "ngầm" trước khi có quyết định tường minh) | Đọc `governance/proposals/g3_bp3_dependency_gap_proposal.yaml` (D1B) — `mr_long_decision != PENDING` là điều kiện BẮT BUỘC trước khi report/D8 tính D3-driver-passthrough hoặc D5-Nguồn-B là số liệu chính thức (dry-run cấu trúc thì được, ghi rõ). Report tính các số này mà proposal còn `PENDING` = 100% SAI, coi là dùng dữ liệu domain khác chưa cấp phép — cùng mức nghiêm trọng như G3-1, không có "tạm chấp nhận" |
| G3-13 | D5/D6 dựng confusion-test hoặc block registry mới đo age-slang mà KHÔNG cross-reference `tests/test_dialogue_appropriateness_1000_r208.py` đã có sẵn (đo cùng lát cắt bằng cùng `dialog_voice_validator.validate()` + `MODERN_SLANG`) — nguy cơ 2 test độc lập không biết nhau, phình test vô ích hoặc lệch kết luận khi 1 cái sửa mà cái kia không update | R211 (đối chiếu "đã có" trước khi tính "gap"/tạo mới) + phát hiện skeptic-1 | Đọc `governance/architecture_registry.yaml` (block `dialogue:` mới, D6) và `reports/G3_DIALOGUE_REPORT.md` — PHẢI có dòng nhắc rõ R208 và giải thích ranh giới (R208 = test hành vi validator age-slang-only, D5 = test hành vi generator đa lát cắt). Thiếu dòng này khi đã tạo test/block mới đo age-slang = 100% SAI (thiếu đối chiếu bắt buộc) |

## KHÔNG CHỜ G3 XONG HẲN MỚI SOÁT TỪNG CHECKPOINT
G3-1/G3-2/G3-3 (build-ahead + trùng lặp + enum lệch) có thể soát NGAY khi thấy file mới xuất hiện
trong diff, không cần đợi build báo `READY_FOR_AUDIT` toàn bộ — phát hiện sớm tránh builder đi tiếp
trên nền sai (giống tinh thần "không chờ đủ 2 pack" của `CMD_AUDIT_G4_G5.md`). Tương tự, G3-11 (số
liệu baseline sai) và G3-12 (dùng dữ liệu world/audio khi D1B còn PENDING) nên soát ngay khi D0/D1B
nộp, không đợi D8 report cuối mới phát hiện.

## SAU KHI CÓ VERDICT
Theo đúng format `CMD_AUDIT_PROTOCOL.md` (bảng Claim|Kiểm bằng gì|Kết quả + PASS/FAIL/PASS-với-
điều-kiện). G3-1 hoặc G3-8 FAIL → route lại CMD_BUILD kèm nguyên văn dòng 435-441 (blocking_dependency)
hoặc dòng 431-434 (source_of_truth bible) đã trích trong bảng trên — không để lặp lại vòng "tự tra
cứu lại domain declaration" tốn thời gian. G3-12 FAIL → route lại kèm nguyên văn `world.reader`/
`audio.reader` (dòng 108/685) và yêu cầu D1B ký trước khi build tiếp phần phụ thuộc đó. G3-11 FAIL
→ yêu cầu build lại D0 với số liệu đối chiếu trực tiếp file thật, không sửa nhẹ rồi báo lại cùng số cũ.

## THAM CHIẾU
`CMD_AUDIT_PROTOCOL.md` (7 bước gốc) · `CMD_AUDIT_G4_G5.md` + `CMD_AUDIT_G6.md` (mẫu gốc) ·
`prompts/TASK_G3_DIALOGUE.md` (bản đã sửa theo 3 skeptic, PHẢN BIỆN #1-#12, D0-D8 + D1B) ·
`governance/blueprint/blueprint_domains.yaml` (khối `dialogue` dòng 428-450, `world.reader` dòng 108,
`audio.reader` dòng 685) · `governance/blueprint/bp3/dependency_detail.yaml`
(`dep__dialogue__character`, `dep__dialogue__culture` — và gap `dep__dialogue__world`/
`dep__dialogue__audio` chưa khai) · `governance/pack2/08_artifact_contract.md` (dòng "G3 dialogue") ·
`tools/audit_dialogue_hierarchy.py` · `tools/audit_driver_dialogue_context.py` ·
`tools/auto_fix_dialogue_hierarchy.py` · `tools/qa_dialogue_identity.py` ·
`tools/dialog_voice_validator.py` · `tools/migrate_roster_v2.py` · `tools/roster_validator.py` ·
`tools/ci_gate.py` (11 entry `CHECKS` thật) · `governance/architecture_registry.yaml`
(`dependency_map` Character->Dialogue/Dialogue->TTS) · `tests/test_dialogue_appropriateness_1000_r208.py`
(R208, wired trong ci_gate) · `bible/02_lore_db.yaml` (dòng 18-20) · `bible/31_golden_samples.yaml` ·
lesson-enforcer-claim-vs-behavior · lesson-dont-downplay-rigor · lesson-lock-ceremony-and-regen ·
lesson-claim-equals-work · lesson-audio-first-character-schema · lesson-enterprise-audit.
