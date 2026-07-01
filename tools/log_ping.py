"""Auto-update PING_CMD_LEAD log every fix/violation/render event.
Mr.Long lệnh 29/6: update PING tự động sau mỗi lần fix hoặc sai mới có sửa.

Usage:
  python tools/log_ping.py VIOLATION "Mr.Long flag: cô cô duplicate L210"
  python tools/log_ping.py FIX "L210 reword cô cô → này cô gái"
  python tools/log_ping.py RENDER "v46 SETUP launched ETA 12min"
  python tools/log_ping.py AUDIT "STAGE 3 FAIL peak 0.0 clip"
  python tools/log_ping.py APPROVE "Mr.Long: chốt đã sạch sẽ"
"""
import sys
import datetime
from pathlib import Path

PING = Path(__file__).resolve().parents[1] / r'PING_CMD_LEAD_29_06.md'

CATEGORIES = {
    "VIOLATION": "Mr.Long flag",
    "FIX": "Em fix",
    "RENDER": "Render",
    "AUDIT": "STAGE audit",
    "APPROVE": "Mr.Long approve",
    "RULE": "Rule new/update",
    "INFO": "Info",
}


def log(category, message):
    if category not in CATEGORIES:
        print(f"ERROR: Unknown category {category}. Use: {list(CATEGORIES.keys())}")
        sys.exit(1)
    ts = datetime.datetime.now().strftime("%H:%M")
    label = CATEGORIES[category]
    entry = f"- `{ts}` **[{category}]** {label}: {message}\n"
    existing = PING.read_text(encoding="utf-8") if PING.exists() else "# PING CMD LEAD\n\n"
    # Find or create "## AUTO LOG" section
    marker = "## AUTO LOG (tự động cập nhật)\n"
    if marker not in existing:
        existing = existing.rstrip() + f"\n\n---\n{marker}\n"
    # Append entry under AUTO LOG section
    idx = existing.find(marker) + len(marker)
    new_content = existing[:idx] + entry + existing[idx:]
    PING.write_text(new_content, encoding="utf-8")
    print(f"[log_ping] {entry.rstrip()}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    log(sys.argv[1], " ".join(sys.argv[2:]))
