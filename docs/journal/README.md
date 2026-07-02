# docs/journal — Nhật ký quy trình (không phải sản phẩm)

Thư mục này chứa các **log điều phối / ping / lesson / notice** phát sinh trong quá trình
làm việc. Chúng KHÔNG được code nào tham chiếu (đã verify bằng grep) → gom vào đây cho
thư mục gốc gọn gàng.

Chuyển vào 2026-07-01 khi dọn repo.

## Lưu ý
Các file log "load-bearing" (được tool đọc/ghi) vẫn nằm ở **thư mục gốc**, KHÔNG chuyển:
- `PING_CMD_LEAD_29_06.md` — `tools/log_ping.py` ghi vào, nhiều audit đọc
- `RENAME_LOG.md` — `tools/log_rename.py` ghi vào
- `PROMPT_CMD_LEAD.txt`, `PROMPT_CMD_THUC_THI.txt` — `tools/project_bootstrap.py` đọc
- `COORDINATION_HUB.md` — nhắc trong hướng dẫn bootstrap
