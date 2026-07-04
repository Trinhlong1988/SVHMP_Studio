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

## Nguồn cảm hứng
So sánh với Hermes Agent (Nous Research, 4/7): pattern "skill file agent tự viết, mọi lần gọi lại
đọc được" đúng hướng nhưng KHÔNG áp dụng "tự viết không kiểm duyệt" — file này làm thủ công, review
tại audit, đúng tinh thần R209 (cấm Builder tự tuyên PASS) áp dụng luôn cho tri thức meta.
