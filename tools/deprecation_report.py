"""SVHMP — Deprecation Report (Boss 2/7): moi file co trang thai ro keep/deprecated/forbidden.
Doc governance/file_index.yaml -> governance/deprecation_report.md.
Policy: keep=active dung | deprecated=one-off/backup/v1 -> archive | forbidden=CAM sua.
"""
import sys
from pathlib import Path
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml

SVHMP = Path(__file__).parent.parent
FORBIDDEN = ["thư mục ZIP `*-6d16ecda` (stale copy — R200 CẤM sửa)"]


def main():
    idx = yaml.safe_load((SVHMP / 'governance' / 'file_index.yaml').read_text(encoding='utf-8'))
    by = defaultdict(list)
    for f, i in idx['files'].items():
        by[i['status']].append(f)

    lines = ["# DEPRECATION REPORT (G1 — Boss 2/7)", "",
             "**Policy:** `keep`=active đang dùng · `deprecated`=one-off/backup/v1 → archive, KHÔNG xoá vội · `forbidden`=CẤM sửa.", "",
             f"## KEEP (active): {len(by['active'])}",
             f"## DEPRECATED (archive candidate): {len(by['deprecated'])}", ""]
    for f in sorted(by['deprecated']):
        lines.append(f"- `{f}`")
    lines += ["", f"## FORBIDDEN: {len(FORBIDDEN)}"]
    for f in FORBIDDEN:
        lines.append(f"- {f}")
    (SVHMP / 'governance' / 'deprecation_report.md').write_text("\n".join(lines) + "\n", encoding='utf-8')

    print(f"=== DEPRECATION REPORT ===")
    print(f"  keep(active)={len(by['active'])}  deprecated={len(by['deprecated'])}  forbidden={len(FORBIDDEN)}")
    print("  → governance/deprecation_report.md")


if __name__ == '__main__':
    main()
