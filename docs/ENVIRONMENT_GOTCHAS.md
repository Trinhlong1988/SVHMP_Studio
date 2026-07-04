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

## Nguồn cảm hứng
So sánh với Hermes Agent (Nous Research, 4/7): pattern "skill file agent tự viết, mọi lần gọi lại
đọc được" đúng hướng nhưng KHÔNG áp dụng "tự viết không kiểm duyệt" — file này làm thủ công, review
tại audit, đúng tinh thần R209 (cấm Builder tự tuyên PASS) áp dụng luôn cho tri thức meta.
