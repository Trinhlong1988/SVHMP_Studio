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

## G17 — Agent con (spawn qua Agent tool) tự MỞ RỘNG phạm vi qua nhiệm vụ được giao, chạy thêm
pytest/gate song song với phiên khác → tái diễn đúng lớp rủi ro DEBT-005 (race-condition)
Case thật (5/7 tối): 1 agent con được giao nhiệm vụ ĐÓNG PHẠM VI ("điều tra git log bible/00, soạn
draft changelog, KHÔNG sửa file thật") hoàn thành đúng việc — nhưng sau đó nhận thêm tin nhắn trực
tiếp (không qua phiên kiểm duyệt chính) và tự ý: (1) viết vào file khóa sau khi vượt qua 1 lần bị
chặn, (2) tự nhận thêm việc không ai giao — kiểm chứng PING của phiên CMD_BUILD khác, tự chạy lại
`pytest tests/ -q` full-suite + `cmd_pipeline_gate.py` — ĐÚNG LÚC phiên kiểm duyệt chính đang tự
chạy 1 workflow audit độc lập khác (2 worktree, mỗi cái cũng chạy full pytest) → nhiều pytest
full-suite chạy đồng thời trên máy, đúng lớp rủi ro DEBT-005 (xem trên) dù lần này không phát hiện
corruption thật. Agent con KHÔNG tự đọc `TECH_DEBT.md`/gotcha này trước khi hành động vì không được
dặn.
**Bài học (bắt buộc mỗi lần spawn Agent() cho việc điều tra/one-off):** (1) LUÔN ghi rõ điều kiện
DỪNG trong prompt spawn — "sau khi báo cáo xong thì DỪNG, không tự nhận thêm việc, nếu người dùng
nhắn thêm việc thì bảo chuyển qua phiên chính"; (2) nếu thấy dấu hiệu agent con tự xử lý việc ngoài
phạm vi gốc, CHẶN NGAY (gửi tin bảo dừng) thay vì để tiếp tục; (3) với agent có khả năng chạy lệnh
nặng, nhắc thẳng trong prompt: kiểm `Get-Process python` trước khi chạy full-suite, tránh race-
condition đã biết.

## G18 — `.bat`/`.ps1` launcher tiếng Việt: BAT cần LF-free (CRLF), PS1 cần BOM — NGƯỢC NHAU, dễ nhầm với G1

Case thật (9/7, tạo `SVHMP_CMD_BUILD/BUILD_2/AUDIT.bat` trên Desktop gọi
`tools/launch_cmd_session.ps1` với path tiếng Việt có dấu):

1. **`.bat` viết bằng tool ghi LF-only (Unix line ending)** → `cmd.exe` tokenize sai, lỗi
   `'ul' is not recognized`, `'oProfile' is not recognized` (mất vài ký tự đầu token, do thiếu
   CR trước LF làm cmd đọc lệch dòng dưới codepage 65001). **Fix:** `.bat` PHẢI CRLF —
   `[System.IO.File]::WriteAllText(path, ($lines -join "`r`n") + "`r`n", (New-Object
   Text.UTF8Encoding $false))` (no BOM cho .bat).
2. **`.ps1` chứa literal tiếng Việt (path, chuỗi) không BOM** → `powershell.exe` (Windows
   PowerShell 5.1, KHÁC `pwsh` 7) đọc source file bằng codepage hệ thống thay vì UTF-8 khi
   thiếu BOM → mojibake ngay trong biến hardcode (`"DỰ ÁN AI"` in ra `"Dá»° ÃN AI"`), dù
   `Get-Content -Encoding UTF8` đọc *nội dung file khác* (không phải chính .ps1 đang chạy) vẫn
   đúng — 2 việc khác nhau, dễ tưởng đã fix. **Fix:** `.ps1` có literal non-ASCII PHẢI ghi BOM —
   `(New-Object Text.UTF8Encoding $true)`.

**NGƯỢC nhau, dễ nhầm với G1** (G1 nói Python cần `utf-8-sig` vì PowerShell ghi thừa BOM — ở
đây lại là trường hợp **thiếu BOM gây lỗi**, đúng ngược). Quy tắc gộp: `.bat` = CRLF + no-BOM;
`.ps1` có ký tự ngoài ASCII = BOM (LF hay CRLF nội dung không quan trọng với `.ps1`, PowerShell
tolerant cả 2). **Luôn test dry-run thật** (biến env cờ như `SVHMP_LAUNCH_DRYRUN=1` skip lệnh
cuối) qua `cmd /c "echo. | script.bat > out.txt 2>&1"` (pipe `echo.` để không treo ở `pause`)
trước khi giao Mr.Long double-click — 2 lỗi trên hoàn toàn im lặng nếu chỉ đọc code bằng mắt.

## G19 — `git reset <ref>` (kể cả KHÔNG `--hard`) trên shared main working tree có thể "xoá" commit của SESSION KHÁC khỏi `git log`/branch — chỉ còn reflog, dễ tưởng mất thật

Case thật (10/7): 2 phiên CMD làm việc trực tiếp trên CÙNG 1 thư mục làm việc chính (không phải
worktree riêng — R200 chỉ đảm bảo push/pull đồng bộ, KHÔNG đảm bảo cách ly session cùng máy). Phiên
A tạo 1 commit local chưa push (Batch D). Phiên B tạo 2 commit local chưa push khác (G2 NHÓM A/B).
Sau đó 1 trong 2 phiên chạy `git reset origin/main` (đồng bộ theo đúng pattern đã dùng nhiều lần
trong project — worktree cô lập cherry-pick → push → `git reset origin/main` ở thư mục chính) —
nhưng **tại thời điểm đó có 3 commit local (của CẢ 2 phiên) đứng SAU `origin/main`**, nên lệnh reset
đưa branch `main` lùi lại, làm 3 commit này rơi khỏi `git log`/`git status` — chỉ còn thấy qua
`git reflog`.

**Điểm dễ hiểu lầm gây hoảng:** vì đây là reset MẶC ĐỊNH (mixed, không `--hard`), working tree KHÔNG
bị ghi đè — nội dung file của cả 3 commit vẫn còn nguyên 100% trên đĩa (`git status` hiện chúng là
"M"/"??"), chỉ mất liên kết với lịch sử commit. Phiên phát hiện sự cố ban đầu kết luận nhầm "2 commit
BỊ MẤT" — thực ra **không mất 1 byte nào**, chỉ mất commit record. Xác nhận bằng
`git diff <hash_dangling> -- <file>` = rỗng cho mọi file liên quan (kiểm duyệt tự verify 10/7,
`git cat-file -e <hash>` xác nhận dangling commit chưa bị GC).

**Quy trình bắt buộc từ nay (chống tái diễn — R215 áp dụng, đây là process failure):**
1. **TRƯỚC khi chạy `git reset <bất kỳ ref nào>` trên thư mục làm việc chính (KHÔNG áp dụng cho
   worktree cô lập tự tạo/tự xoá)** — PHẢI chạy `git log --oneline <ref>..HEAD` trước. Nếu có commit
   nào hiện ra (bất kể của session nào, kể cả không nhận ra tác giả) → **DỪNG**, không reset ngay.
2. Nếu có commit lạ: (a) nếu nội dung hợp lệ (đọc `git show --stat <hash>` xác nhận không phải rác)
   → cherry-pick vào worktree cô lập + push riêng TRƯỚC, hoặc (b) nếu không chắc, để nguyên KHÔNG
   reset, báo qua `log_ping.py` hỏi trước.
3. Sau khi phát hiện đã lỡ reset: **KHÔNG hoảng, không `git reset --hard` để "dọn sạch"** — dangling
   commit còn nguyên trong reflog tối thiểu vài tuần (chưa GC) — dùng `git cat-file -e <hash>` xác
   nhận còn, `git diff <hash> -- <file>` đối chiếu working tree, commit lại trực tiếp (không cần
   cherry-pick nếu working tree đã khớp sẵn).
4. **Về lâu dài (đề xuất, chưa bắt buộc — cần Mr.Long quyết):** mỗi CMD session dùng 1 `git worktree`
   riêng (không phải thư mục chính dùng chung) cho MỌI thao tác build, không chỉ lúc push — thư mục
   chính chỉ dùng để đọc/kiểm tra, không commit trực tiếp. Giảm hẳn khả năng 2 session giẫm branch ref
   lên nhau. Khác G7 (nói về nhiều worktree CỦA CÙNG 1 clone chia sẻ refs) — G19 là 2 session dùng
   CHUNG 1 working tree (không qua worktree nào cả).

## Nguồn cảm hứng
So sánh với Hermes Agent (Nous Research, 4/7): pattern "skill file agent tự viết, mọi lần gọi lại
đọc được" đúng hướng nhưng KHÔNG áp dụng "tự viết không kiểm duyệt" — file này làm thủ công, review
tại audit, đúng tinh thần R209 (cấm Builder tự tuyên PASS) áp dụng luôn cho tri thức meta.

## Bẫy cp1252 khi `subprocess` đọc output tiếng Việt (CMD_BUILD_2, 9/7)
**Triệu chứng:** `git push` treo/timeout kèm `UnicodeDecodeError: 'charmap' codec can't decode byte
0x81 ... in _readerthread` — crash trong **reader thread nền** của `subprocess`, KHÔNG phải trong
code chính (nên khó truy). Xảy ra ở `tools/ci_gate.py` (pre-push CI gate) khi gọi
`subprocess.run([...], capture_output=True, text=True)` **thiếu `encoding=`**.

**Cơ chế:** `text=True` trên Windows decode stdout con bằng **locale mặc định (cp1252)**, KHÔNG phải
UTF-8. Script con in tiếng Việt → phát byte UTF-8 (vd `0x81` là continuation byte) → cp1252 không
decode được → crash. Byte 0x81 hợp lệ trong UTF-8 nhưng **undefined trong cp1252** ⇒ dấu hiệu nhận
biết chắc chắn "parent decode sai codec, KHÔNG phải child ghi sai".

**Fix (đã áp 9/7, CI gate PASS 591 test, 0 crash):** MỌI `subprocess.run(..., text=True)` đọc output
có thể chứa non-ASCII PHẢI thêm `encoding='utf-8', errors='replace'`. Với subprocess con là Python,
set thêm env `PYTHONUTF8=1` để child emit UTF-8 ổn định. KHÔNG dựa vào `sys.stdout.reconfigure()` —
nó chỉ sửa stdout của CHÍNH process, không đổi cách decode output của process CON.

**Đề xuất quy trình (chống tái diễn):** grep repo tìm `text=True` không kèm `encoding=` trong mọi
tool có thể chạy trên hook/CI = nợ tiềm ẩn cùng lớp — nên quét định kỳ.

## Bẫy R86 fix đẩy word_count vượt trần hard_ceiling (CMD_BUILD, 11/7, DEBT-018)
**Triệu chứng:** Sửa vi phạm R86 (EOL NGA/NANG/HOI) bằng cách thêm 1 từ cuối câu (vd "đó", "rồi",
"ấy") ở nhiều câu trong 1 tập — với tập vốn đã gần trần `hard_ceiling` (2900 từ, ep_25 gốc ~2870+),
tổng số từ thêm vào (20-40 từ cho 1 tập ~30 vi phạm) đủ đẩy `word_count` VƯỢT trần → `post_render_gate.py`
FAIL dù R86 đã sạch 100%. Case thật: ep_25 sau fix 37 vi phạm → 2908 từ > 2900 trần.

**Fix:** Sau khi sửa xong R86 (0 vi phạm) và TRƯỚC khi commit, LUÔN chạy `post_render_gate.py --ep N`
đầy đủ (không chỉ `qa_eol_diacritic.py`) — nếu word_count FAIL, cắt bớt ở 2 chỗ: (1) đổi các fix
2-từ (vd "hiện lên", "lần hai") thành fix 1-từ tương đương an toàn tone (vd "đó"); (2) cắt các cụm
mô tả dư thừa KHÔNG liên quan R86 (vd câu tường thuật có 2 mệnh đề lặp ý — "đã có lâu năm" trùng
"bệnh xưa") — chỉ cắt ở câu tường thuật/mô tả, KHÔNG cắt thoại nhân vật (giữ nguyên giọng nhân vật
theo R195/R197). Verify lại `qa_eol_diacritic.py` (vẫn 0) rồi mới `post_render_gate.py` lại.

**Đề xuất quy trình (chống tái diễn cho 24 tập R86 còn lại DEBT-018):** với các tập đã gần trần
(>2800 từ trước khi sửa, xem qua `wc` nhanh), ưu tiên fix bằng REORDER (không thêm từ) hơn fix bằng
THÊM TỪ ở những câu có thể đảo được — chỉ thêm từ khi reorder không khả thi (câu 1 từ đơn, tên riêng
cuối câu, v.v).
