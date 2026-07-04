"""PACK CLAIM — chong 2 builder cung build 1 pack (Mr.Long ky 4/7, sau 2 va cham 3-4/7:
BP6 ban A/B + G2 flip C5). MASTER luat 11: claim TRUOC khi build, release SAU khi push.

Usage:
  python tools/build_claim.py claim   <pack_id> <session>   # exit 0 = duoc build; 1 = pack co chu
  python tools/build_claim.py release <pack_id> <session>   # tra pack sau khi push verified
  python tools/build_claim.py status  [pack_id]             # xem claim (exit 0)

Session = ten phien (vd CMD_BUILD, G2_EXECUTOR, KIEM_DUYET). Re-claim cung session = idempotent.
--file <path> chi danh cho test (khong dung o che do that).
"""
import datetime
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DEFAULT_FILE = REPO / 'runtime' / 'build_claim.yaml'


def _load(path):
    data = yaml.safe_load(Path(path).read_text(encoding='utf-8')) if Path(path).exists() else None
    data = data or {}
    data.setdefault('claims', {})
    return data


def _save(path, data):
    Path(path).write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=True),
                          encoding='utf-8')


def main(argv):
    args = list(argv)
    claim_file = DEFAULT_FILE
    if '--file' in args:
        i = args.index('--file')
        claim_file = Path(args[i + 1])
        del args[i:i + 2]
    if not args or args[0] not in ('claim', 'release', 'status'):
        print(__doc__)
        return 2
    cmd = args[0]
    data = _load(claim_file)

    if cmd == 'status':
        target = args[1] if len(args) > 1 else None
        for pack, c in sorted(data['claims'].items()):
            if target and pack != target:
                continue
            print(f"  {pack}: {c.get('status')} by {c.get('session')} at {c.get('claimed_at')}")
        if not data['claims']:
            print('  (chua co claim nao)')
        return 0

    if len(args) < 3:
        print('ERROR: can <pack_id> <session>')
        return 2
    pack, session = args[1], args[2]
    cur = data['claims'].get(pack)

    if cmd == 'claim':
        if cur and cur.get('status') == 'active' and cur.get('session') != session:
            print(f"[CLAIM-FAIL] {pack} DANG CLAIMED by {cur['session']} "
                  f"(tu {cur.get('claimed_at')}) — KHONG build. "
                  f"Phien do release xong moi duoc claim (MASTER luat 11).")
            return 1
        data['claims'][pack] = {'session': session, 'status': 'active',
                                'claimed_at': datetime.datetime.now().isoformat(timespec='seconds')}
        _save(claim_file, data)
        print(f"[CLAIM-OK] {pack} -> {session}. Nho log_ping CLAIM + release sau khi push.")
        return 0

    # release
    if not cur or cur.get('status') != 'active':
        print(f"[RELEASE-OK] {pack} khong co claim active (idempotent).")
        return 0
    if cur.get('session') != session:
        print(f"[RELEASE-FAIL] {pack} active by {cur['session']} — chi chinh chu duoc release.")
        return 1
    cur['status'] = 'released'
    cur['released_at'] = datetime.datetime.now().isoformat(timespec='seconds')
    _save(claim_file, data)
    print(f"[RELEASE-OK] {pack} released by {session}.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
