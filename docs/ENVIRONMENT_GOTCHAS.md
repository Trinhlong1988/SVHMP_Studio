# ENVIRONMENT GOTCHAS — tri thức dùng chung mọi phiên (CMD_BUILD/G2/kiểm duyệt/mới)
> Học từ Hermes Agent (Nous Research) đối chiếu 4/7: agent tự viết skill file mọi lần gọi lại đều
> đọc được — dự án mình có lesson tương đương nhưng SỐNG TRONG MEMORY RIÊNG của từng phiên Claude,
> phiên khác không đọc được. File này đưa bài học VÀO REPO để mọi phiên (dù Claude instance khác
> nhau) đều tránh dẫm lại đúng hố cũ. **Append-only, không tự thực thi, kiểm duyệt soát ở audit kế.**
> Đọc file này khi onboard (cùng lượt với CLAUDE.md/bootstrap); thêm mục mới khi tự dò ra bẫy mới.

## G1 — PowerShell 5.1 mặc định ghi BOM (UTF-8 with BOM)
`Set-Content`/`Out-File -Encoding utf8` ghi kèm BOM (`﻿`). Nếu code Python đọc file bằng
`encoding='utf-8'` thường (không phải `utf-8-sig`), guard quét source (vd tìm `def foo` bằng regex)
có thể BỊ XUYÊN THỦNG bởi BOM — case thật: `test_dup_key_loader_single_impl` (BP5, 3/7) không bắt
được bản copy-paste có BOM. **Fix:** viết file code bằng `[IO.File]::WriteAllText(path, content,
(New-Object Text.UTF8Encoding $false))` (không BOM), hoặc code Python đọc `encoding='utf-8-sig'`.

## G2 — `shlex.split()` mặc định (POSIX mode) nuốt backslash Windows
Path Windows kiểu `C:\x\broken.yaml` truyền qua `shlex.split(argv, posix=True)` (mặc định) bị nuốt
`\` → path nát → checker con FAIL SAI LOẠI LỖI (file-not-found thay vì lỗi thật cần test). Case thật:
`blueprint_suite_check.py` pass-through `--bp{N}` (BP5, 3/7). **Fix:** `shlex.split(s, posix=False)`
khi xử lý path Windows, kèm `.strip('"')` bỏ quote thừa.

## G3 — MinGit trên máy Admin KHÔNG có bash.exe / coreutils
Hook `#!/bin/bash` hoặc script gọi `grep`/`sed`/`awk`/`head`/`cat` từ git hook sẽ "command not found"
— máy này chỉ có MinGit, không phải Git for Windows đầy đủ. **Fix:** hook = `#!/bin/sh` wrapper mỏng
→ ủy quyền Python (`git_hook_pre_commit.py`...); mọi tool CLI viết bằng Python, không viết bash.

## G4 — `git worktree remove` có thể xóa record nhưng KHÔNG xóa được thư mục vật lý
Nếu thư mục đang bị khóa (process khác đang `cd` vào đó / file đang mở), lệnh báo `Permission denied`
nhưng git đã âm thầm gỡ worktree khỏi danh sách quản lý — thư mục vẫn nằm trên đĩa, MẤT liên kết với
branch. Case thật: `SVHMP_wt_g2claim` (4/7). **Không mất commit** (đã push an toàn) nhưng phiên đang
đứng trong thư mục đó có thể thấy lỗi lạ. **Fix:** trước khi remove, hỏi/kiểm phiên khác có đang dùng
worktree đó không; nếu remove fail, tự tạo worktree mới từ `origin/main` thay vì cố gắng cứu cái cũ.

## G5 — `git-lfs` cảnh báo ở mọi lệnh checkout/commit là VÔ HẠI trên máy này
Máy không cài git-lfs nhưng repo config `core.hooksPath` kích hoạt post-checkout/post-commit hook LFS
→ in cảnh báo "git-lfs not found on your path" ở MỌI lệnh git. Đây KHÔNG phải lỗi, không ảnh hưởng
kết quả (exit code vẫn đúng). Đừng hoảng khi thấy nó lặp lại liên tục trong output.

## G6 — PACK CLAIM (luật 11 MASTER) chỉ chặn "2 người giành 1 pack", CHƯA chặn "build trước khi pack
trước được KHÓA". Case thật (4/7): CMD_BUILD claim `bp7_narrative` trong khi `bp6_decision` vẫn
`candidate` (chưa có chữ ký Mr.Long) — không phải va chạm (claim hợp lệ, không ai tranh), nhưng lệch
nghi thức "chỉ tự đọc task kế tiếp SAU KHI Mr.Long lock pack N" (BP_PIPELINE_MASTER). **Chưa có
enforcer** — backlog: `build_claim.py claim` nên tự kiểm registry pack liền trước trong chuỗi MASTER
đã `locked` chưa trước khi cho claim pack kế. Hiện tại: builder + kiểm duyệt phải tự ý thức, chưa có
máy chặn.

## G7 — Nhiều `git worktree` của CÙNG 1 clone chia sẻ chung `.git` objects/refs, KHÔNG cách ly
"local-only, chưa push" như tưởng. Case thật (4/7): kiểm duyệt `git rebase origin/main` trên shared
main tree tạo ra commit local `c725729` (G2 cố ý ghi "Commit LOCAL — CHƯA push, chờ Mr.Long duyệt
pool tên + waiver"). Không hề `git push` — nhưng 1 worktree KHÁC được tạo sau đó (cùng clone) thấy
được nhánh `main` cục bộ này qua `git log --all` (không cần qua origin!) và vô tình đẩy nó lên. Hệ quả:
nội dung "chờ duyệt" lọt lên origin/main mà KHÔNG ai chủ đích push nó. **Bài học:** "commit local
chưa push" chỉ thật sự an toàn nếu nó nằm trên **branch riêng đặt tên rõ** (vd `g2/hybrid-draft-nopush`),
KHÔNG phải branch `main` dùng chung — vì bất kỳ worktree nào khác của cùng clone đều nhìn thấy và có
thể vô tình publish nó. Áp dụng: nội dung "chờ Mr.Long duyệt trước khi lên chung" PHẢI commit trên
branch cách ly tên riêng, không rebase/để trên `main` dù chỉ tạm thời.

## G8 — Tool quét trùng-ID bằng regex phải liệt kê ĐỦ mọi quy ước đặt tên đang dùng thật
`check_rule_id_free.py` chỉ coi `^R{N}_xxx:` và `- id: R{N}` là "định nghĩa" — bỏ sót quy ước
`rule_R{N}_xxx:` (76/123 rule bible/00 dùng dạng này) → 2 dup-key THẬT (R142, R143 — cùng literal
key lặp 2 lần, `yaml.safe_load` âm thầm nuốt bản đầu) lọt qua `--all` VÀ qua `--staged` (guard sống
trong pre-commit hook) suốt nhiều tuần, chỉ lộ khi 1 checker khác (BP7, dùng loader nghiêm ngặt hơn)
tình cờ raise lỗi khi load toàn file. **Bài học:** khi viết tool quét-trùng bằng regex (không parse
yaml, vì chính yaml.safe_load là nạn nhân), phải liệt kê ĐỦ mọi biến thể đặt tên đang tồn tại trên
disk (`grep -c "^X_" file` vs `grep -c "^prefix_X_" file` — so cả 2 con số), không chỉ theo docstring
mô tả "4 format" — docstring có thể lạc hậu so với thực tế file đã tăng trưởng.

## G9 — Kiểm duyệt FIX xong + LOCK xong KHÔNG tự động báo cho phiên builder đang bị chặn biết
Case thật (4/7): kiểm duyệt sửa bible/00 (R142/R143) lúc 19:15, lock BP6 lúc 19:28 — nhưng worktree
của CMD_BUILD (`bp7_narrative`) đứng yên nguyên tại commit lúc claim, KHÔNG tự pull/biết gì, tiếp tục
"bị chặn" trong đầu nó dù chặn đã gỡ từ lâu. **Nguyên nhân:** không có kênh nào đẩy tin giữa các
phiên Claude Code (mỗi phiên = terminal riêng, không thấy nhau) — chỉ có `log_ping` (phiên phải TỰ
đọc mới biết) hoặc Mr.Long làm người chuyển lời thủ công. **Bài học:** sau khi fix/lock một defect
đang CHẶN builder khác, kiểm duyệt phải chủ động soạn sẵn đoạn relay ngắn (lệnh cụ thể: fetch+rebase+
lệnh verify) để Mr.Long dán ngay — đừng chỉ ghi log_ping rồi coi như xong việc, vì thời gian chờ
Mr.Long thấy + dán lại = thời gian builder ngồi không oan uổng. Về lâu dài: đây là ca dùng thật cho
ý tưởng "Hermes-style PING→Telegram" (xem Nguồn cảm hứng) — mức ưu tiên nên nâng lên khi có nhiều
pack chạy song song hơn.

## G10 — "Sẽ vớt ý từ nhánh archive" là lời hứa, KHÔNG phải hành động — phải làm ngay lúc archive
Case thật (4/7, LỖI CỦA CHÍNH KIỂM DUYỆT): va chạm BP6 (Bản A vs Bản B) — kiểm duyệt phán "Bản A đi
tiếp, Bản B archive" và NÓI "sẽ diff Bản B vớt ý hay trước khi trình ký" — nhưng KHÔNG thực sự chạy
diff đó. Bản B đã tự phát hiện **bible/31_golden_samples.yaml dòng 113 lỗi cú pháp YAML (crash cứng
mọi parser, không riêng loader strict)** — Mr.Long chính tay ghi PING lúc đó "bible/31 defect cần ký
fix bất kể chọn bản nào" — nhưng vì không ai trích ra khỏi nhánh archive, defect nằm chết ở đó **suốt
nhiều tiếng đồng hồ** cho tới khi CMD_BUILD (làm BP8, cần bible/31 làm SoT golden_output) tình cờ đụng
lại TỪ ĐẦU, tưởng là phát hiện mới. **Bài học:** "tôi sẽ vớt ý từ bản thua" là câu nói dễ, hành động
thật là 1 lệnh `git diff <lock-branch> <archive-branch>` chạy NGAY lúc archive, không phải ý định để
đó. Archive một nhánh mà không diff trước = tự tay chôn mọi phát hiện nó có, dù đúng dù sai. Áp dụng:
mọi lần "archive, không merge" PHẢI kèm bước diff-and-extract LÀM NGAY trong cùng phiên, ghi kết quả
diff vào chính commit message archive (không chỉ nói "tôi sẽ...").

## G11 — File mới tạo trong worktree KHÔNG tự xuất hiện trên shared main tree sau khi push
Case thật (4/7): tạo `prompts/launch_build3.cmd` trong worktree riêng (đúng R200) → commit → push →
**xóa worktree** — nhưng vì file gốc từng bị `Remove-Item` khỏi shared main tree (`SVHMP_git`) lúc
chuyển sang worktree, và sau khi push KHÔNG `git pull` lại shared tree, file vẫn THIẾU trên
`SVHMP_git` dù đã lên `origin/main`. Hệ quả: shortcut Desktop trỏ đường dẫn shared-tree báo lỗi
"is not recognized" — Boss double-click chạy fail ngay lần đầu dùng. **Bài học:** sau MỌI lần push
từ worktree phụ, nếu file đó cần dùng NGAY trên shared tree (script/shortcut target, không chỉ để
builder khác pull sau) — PHẢI `git pull --rebase` trên `SVHMP_git` NGAY LẬP TỨC, không coi push
xong = việc xong. Kiểm chứng bằng `Test-Path` trên đường dẫn THẬT trước khi báo "đã tạo xong", không
tin "đã push" là đủ.

## G12 — `git worktree add`/checkout trả **exit code 2 GIẢ** do hook git-lfs mặc định, dù thao tác
THÀNH CÔNG hoàn toàn — đây là ROOT CAUSE của nhiều sự cố "worktree lỗi" cả phiên (4/7)
Máy Admin không có binary `git-lfs`, nhưng `.githooks/post-checkout` + `post-commit` + `post-merge`
dùng đúng template mặc định của git-lfs: `command -v git-lfs || { ...; exit 2; }` — nghĩa là **MỌI
lần** `checkout`/`worktree add`/`commit`/`merge` đều in cảnh báo + trả **exit 2**, kể cả khi file/
thư mục đã tạo/cập nhật đúng 100%. Case thật gây hậu quả: **CMD_BUILD_3 chạy `git worktree add`, thấy
exit 2, kết luận hợp lý (theo quy ước exit-code chuẩn) là "thất bại", bỏ cuộc worktree, quay về sửa
TRỰC TIẾP trên shared tree** trong lúc G2_EXECUTOR + CMD_BUILD đang push song song → conflict thật ở
`runtime/build_claim.yaml` lúc rebase. Đã **FIX TẬN GỐC** (không chỉ né): áp đúng pattern đã có sẵn
và đúng từ trước ở `.githooks/pre-push` (`if command -v git-lfs; then git lfs <cmd> || exit $?; fi`
— chỉ gọi khi CÓ, không bao giờ ép exit non-zero khi thiếu) cho cả 3 hook còn lại. **Verify bằng lệnh
thật:** trước fix `git worktree add` → exit 2; sau fix → exit 0 sạch (commit `3d8f973`).
**Bài học kép:** (1) đừng chỉ tin exit-code khi có hook lạ chen vào — `git worktree add` xong PHẢI
`Test-Path` thư mục mới, đừng suy ra "fail" chỉ từ exit code; (2) khi thấy 1 hook đã fix đúng
(`pre-push`), **rà tất cả hook cùng họ** (mọi `post-*`/`pre-*` khác) xem có dính cùng bug — đừng chỉ
vá đúng chỗ vừa bị bắt.

## G13 — `git stash` dùng CHUNG toàn bộ clone, KHÔNG cách ly theo từng `git worktree`
Case thật (5/7): 2 agent chạy song song, mỗi agent làm việc trong 1 worktree RIÊNG (đường dẫn khác
nhau, tưởng độc lập hoàn toàn), nhưng cả 2 đều `git stash` tại một thời điểm gần nhau để dọn tạm rồi
`git stash pop` lại. Vì `git stash` lưu vào 1 stack DÙNG CHUNG cho cả clone (nằm trong `.git/` gốc,
không phải trong thư mục worktree), agent A `stash pop` vô tình lấy nhầm stash của agent B (branch/
task khác hẳn), và ngược lại — kết quả: file của agent B (2 file, `governance/TECH_DEBT.md` +
`tools/sfx_acquire.py`) xuất hiện uncommitted trong worktree của agent A, và file của agent A
(`tools/hidden_audit.py`) xuất hiện trong worktree của agent B. May mắn không mất gì (đã đối chiếu
byte-for-byte với bản mỗi bên tự commit, giống hệt, dọn sạch an toàn) nhưng đây là **rủi ro mất dữ
liệu thật** nếu 1 trong 2 bên không kiểm tra kỹ trước khi commit. **Bài học:** KHÔNG dùng `git stash`
trần khi chạy nhiều agent/phiên song song trên cùng 1 clone (dù khác worktree) — nếu cần dọn tạm,
dùng `git stash push -m "<nhãn duy nhất theo task>"` VÀ pop bằng đúng tên/index đã lưu lại
(`git stash list` để tìm đúng, không `pop` mù theo mặc định `stash@{0}`), hoặc tránh stash hoàn toàn
(dùng `git worktree` cho mỗi task — đã làm — nhưng thao tác TRONG mỗi worktree vẫn phải né stash
chung, ưu tiên commit-tạm-rồi-amend thay vì stash khi làm việc song song).

## G14 — Gate mới GỌI LẠI `pytest` qua subprocess trên chính file test CHỨA NÓ → fork-bomb đệ quy
vô hạn nếu thiếu re-entrancy guard (tái diễn đúng lớp lỗi đã biết — xem lesson-ci-gate-pytest-recursion)
Case thật (5/7, lúc build G3 D7): `tools/g3_dialogue_check.py` (gate 1 cửa mới) có 1 stage gọi
`subprocess.run([py, '-m', 'pytest', 'tests/test_g3_dialogue.py'])` để tái dùng test có sẵn làm
smoke-check. Nhưng CHÍNH file `tests/test_g3_dialogue.py` đó lại có 1 test tự gọi lại
`g3_dialogue_check.py` (để test "gate chạy được, ghi report đúng") — tạo vòng lặp: gate → pytest →
test → gate → pytest → test → ... **Hậu quả THẬT đã xảy ra:** sinh ra **hơn 2200 tiến trình
`python.exe`** trước khi bị phát hiện và kill kịp thời (may mắn kill đúng phạm vi, không đụng tiến
trình khác của Boss). Đây là ĐÚNG lớp lỗi `ci_gate.py` từng dính trước đây (R213→auditor→ci_gate→
pytest) — dự án ĐÃ CÓ pattern fix chuẩn (`_PYTEST_GUARD` bằng biến môi trường) nhưng người viết gate
mới không tự động biết để áp lại, phải tự nhớ mirror đúng pattern. **Fix (đã áp dụng, xem
`tools/g3_dialogue_check.py::_PYTEST_GUARD`):** guard 2 lớp bằng 1 biến môi trường dùng chung —
(1) trong hàm gọi subprocess pytest của gate: nếu guard đã set thì SKIP không spawn thêm; (2) trong
chính test hay bị gọi lại: nếu guard đã set thì `pytest.skip()` ngay đầu test, không chạy logic gì
thêm. Đặt guard NGAY TRƯỚC khi spawn subprocess con (`env[GUARD]='1'`), không set global toàn tiến
trình cha. **Bài học (áp dụng bắt buộc cho MỌI gate mới có stage gọi `subprocess.run(pytest ...)`):**
trước khi ship 1 gate mới có stage tái dùng pytest, PHẢI tự hỏi "test được gọi có thể trực tiếp/gián
tiếp gọi lại chính gate này không?" — nếu có, bắt buộc thêm guard theo đúng pattern `ci_gate.py` đã
có, KHÔNG viết gate mới mà bỏ qua bước này. Khi nghi ngờ đang chạy thử 1 gate mới lần đầu, mở sẵn
`Get-Process python | Measure-Object` ở cửa sổ khác để bắt sớm nếu số tiến trình tăng bất thường,
đừng đợi máy đơ mới biết.

## G15 — Kỹ thuật làm sạch tạp âm/cụt hơi cụt chữ TTS đã có sẵn, ĐÃ TUNE — đừng coi là nợ kỹ thuật cần giải lại
Case thật (1/7, phiên fix "chữ cuối mỗi đoạn bị cụt" của ep_01 intro — xem lesson-tail-cut-debug
trong memory riêng, giờ đưa vào đây để MỌI phiên đọc được, không chỉ 1 memory riêng). Kiểm duyệt
5/7 khi audit DEBT-002 (thiếu audio thật `hook.wav`/`cliffhanger.wav`) ban đầu viết nhầm hướng đề
xuất "chờ Boss tìm lại file cũ" — Boss chỉnh lại: kỹ thuật làm sạch đã có sẵn và ĐÃ PROVEN, không
phải giải lại từ đầu.

**Vị trí kỹ thuật (còn sống, xem trực tiếp trước khi dùng — đây là snapshot 1/7):**
`tools/svhmp_v13_render.py`: `qa_clean_tail()` — bộ cắt đuôi voicing-based deterministic (thay
`aggressive_trim_tail` cũ dùng ngưỡng cứng, hay cắt lẹm đuôi mềm của từ), giữ tới last-voiced +
`release_pad_ms` rồi cosine-fade về 0 → hết hiện tượng "lụp bụp xì xì" ở cuối câu. Tham số đã Boss
tune và duyệt: `TAIL_TRIM_DB=-62` (giữ đủ dư âm hơi thở ~-38dB, không giữ tới mức lộ tạp âm nền),
`FADE_TAIL_MS=80`, `fade_head` 80ms cosine (chống pop/"xẹt" đầu đoạn khi ghép chunk).

**Bằng chứng sản phẩm thật:** `assets/voice_samples/EP01_intro_qaclean_v2q_01072026.wav` (chốt
bởi Boss 5/7 — bản render cuối cùng trong chuỗi fix `intro_FULL_v2o→v2p→v2q`, gốc tại
`D:\SVHMP_render\ep_01\`, copy vào repo để không phụ thuộc ổ D — quy ước dọn file cũ mỗi lần
render mới có thể xoá bản gốc).

**Áp dụng khi cần audio thật mới (vd giải DEBT-002):** KHÔNG cần "tìm lại file mất" — chạy lại
đúng pipeline này (`scratchpad/render_one.py` cwd `render_cwd`, xem lesson
svhmp-render-on-this-machine) trên spec còn nguyên (`spec_hook.json`/`spec_cliffhanger.json`) là
đủ, vì phần khó (làm sạch tạp âm/cắt cụt chữ) đã giải xong, không phải giải lại.

## G16 — `tests/cases/test_audio_gate_regression.py` (qua `text_batch_fix.py::verify_post_fix`) ghi
tạm THẲNG vào `output/ep_01/episode.md` THẬT — an toàn 1 tiến trình, KHÔNG an toàn khi 2 phiên chạy
`pytest` đồng thời trên CÙNG thư mục dùng chung → corrupt file golden thật (chi tiết đầy đủ +
hướng fix: xem `governance/TECH_DEBT.md` DEBT-005)
Case thật (5/7 tối): push bị CI gate chặn, điều tra ra `output/ep_01/episode.md` giảm từ ~630 dòng
xuống gần rỗng trong working tree (chưa commit, khôi phục an toàn bằng `git checkout --`). Nguyên
nhân: hàm `verify_post_fix()` cố ý ghi `bad_text` vào file thật để chạy probe QA-rule, có try/finally
khôi phục đúng cho 1 tiến trình, nhưng dùng đường dẫn backup CỐ ĐỊNH (không có PID/lock) — 2 tiến
trình cùng chạy test này cùng lúc (thường xảy ra vì chỉ kiểm duyệt dùng worktree cách ly cho audit,
các phiên CMD_BUILD khác làm việc trực tiếp trên thư mục dùng chung) sẽ giẫm backup của nhau.
**Bài học:** khi CI gate FAIL trên file `output/ep_01/`, LUÔN tự hỏi "có phiên khác đang chạy full
suite cùng lúc không" trước khi coi là lỗi thật trong commit đang push — kiểm `git status`/chạy lại
test độc lập để phân biệt nhiễu-đồng-thời (tự hết, retry được) với lỗi-commit-thật (không tự hết).
Đồng thời: phát hiện thêm 1 regression KHÔNG liên quan (R86 không bắt lỗi "cũ." EOL đúng như test kỳ
vọng) trong lúc điều tra — ghi riêng `DEBT-006`, không lẫn với vấn đề concurrency ở trên.

## Nguồn cảm hứng
So sánh với Hermes Agent (Nous Research, 4/7): pattern "skill file agent tự viết, mọi lần gọi lại
đọc được" đúng hướng nhưng KHÔNG áp dụng "tự viết không kiểm duyệt" — file này làm thủ công, review
tại audit, đúng tinh thần R209 (cấm Builder tự tuyên PASS) áp dụng luôn cho tri thức meta.
