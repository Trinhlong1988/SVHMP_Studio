"""SVHMP — PROMOTION GUARD (PACK1 hard-gate HANH VI, khong chi khoa chu).

Finding kiem duyet: 05_builder_hard_gate.md chi CAM bang chu ("Builder khong duoc
doi promotion_status->locked / tao tag") — KHONG co tool chan hanh vi. Guard nay
chan THUC SU o pre-push:

  Neu diff sap push (a) doi mot key YAML (promotion_status / packN_*) sang 'locked',
  HOAC (b) push tag khop 'pack*-v*'  ->  BLOCK (exit 1)
  TRU KHI commit message trong range chua "per Mr.Long authorization".

Chi Mr.Long (LEAD) moi lock/tag; Builder tu lam = chan tai push, khong chi loi chu.

Dung:
  # pre-push hook: doc ref-list tren stdin (git format: <lref> <lsha> <rref> <rsha>)
  git ... | python tools/promotion_guard.py
  # kiem 1 range cu the (dung cho test / thu cong):
  python tools/promotion_guard.py --base <sha> --head <sha>

Exit: 0 = cho phep ; 1 = BLOCK (lock/tag khong authorization).
"""
import re
import subprocess
import sys
import argparse

AUTH_PHRASE = 'per mr.long authorization'          # so khop lowercase
LOCK_RE = re.compile(r'(promotion_status|pack\w*)\s*:\s*locked\b', re.IGNORECASE)
TAG_RE = re.compile(r'pack[\w-]*-v\d', re.IGNORECASE)   # pack2-governance-v1.0, pack1-constitution-v1.0


def added_yaml_sets_locked(diff_text):
    """True neu co dong THEM ('+') trong file .yaml dat key -> 'locked'."""
    cur_file = None
    for line in (diff_text or '').splitlines():
        if line.startswith('+++ '):
            cur_file = line[4:].strip()
            if cur_file.startswith('b/'):
                cur_file = cur_file[2:]
            continue
        if line.startswith('--- '):
            continue
        if line.startswith('+') and not line.startswith('+++'):
            if cur_file and cur_file.lower().endswith(('.yaml', '.yml')):
                if LOCK_RE.search(line[1:]):
                    return True
    return False


def tag_from_ref(ref):
    """Tra ve ten tag pham quy neu ref la refs/tags/pack*-v*, else None."""
    if ref and ref.startswith('refs/tags/'):
        name = ref[len('refs/tags/'):]
        if TAG_RE.search(name):
            return name
    return None


def is_authorized(messages):
    return AUTH_PHRASE in (messages or '').lower()


# Tripwire chong WIPE (su co 2/7: origin mat 1037 file trong 1 push): push xoa
# qua nguong nay ma khong uy quyen -> BLOCK. Refactor lon hop le thi xin uy quyen.
MASS_DELETE_LIMIT = 50


def count_deleted_files(diff_text):
    """Dem file bi XOA trong unified diff ('+++ /dev/null' moi file xoa 1 lan)."""
    return sum(1 for ln in (diff_text or '').splitlines() if ln.strip() == '+++ /dev/null')


def decide(lock_change, tag_change, authorized, mass_delete=0):
    """Logic thuan — de test NEGATIVE truc tiep, khong can git."""
    violations = []
    if lock_change:
        violations.append("doi promotion_status/pack -> 'locked'")
    if tag_change:
        violations.append("tao/push release tag pack*-v*")
    if mass_delete > MASS_DELETE_LIMIT:
        violations.append(f"XOA {mass_delete} file (> {MASS_DELETE_LIMIT} — chong wipe 2/7)")
    if violations and not authorized:
        return 1, ('BLOCK: ' + ' + '.join(violations) +
                   " — thieu \"per Mr.Long authorization\" trong commit message. "
                   "Chi LEAD (Mr.Long) moi duoc lock/tag/mass-delete (05_builder_hard_gate).")
    return 0, 'OK: khong co lock/tag/mass-delete chua uy quyen.'


def _git(args, cwd=None):
    # encoding='utf-8', errors='replace': git output (vd `log --format=%B` cua
    # range push qua _range_messages) co the chua byte non-cp1252 — commit message
    # tieng Viet co dau / blob nhi phan. Mac dinh text=True tren Windows dung cp1252
    # -> reader-thread subprocess crash UnicodeDecodeError (byte 0x90...). Parity voi
    # tools/ci_gate.py (da dung pattern nay). Ref: cp1252 pre-push trace 16/7 (DEBT-hook).
    r = subprocess.run(['git'] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', cwd=cwd)
    return r.stdout


def _range_diff(base, head, cwd=None):
    return _git(['diff', f'{base}..{head}'], cwd=cwd)


def _range_messages(base, head, cwd=None):
    return _git(['log', '--format=%B', f'{base}..{head}'], cwd=cwd)


def check_range(base, head, cwd=None, pushed_ref=None):
    diff = _range_diff(base, head, cwd=cwd)
    msgs = _range_messages(base, head, cwd=cwd)
    lock = added_yaml_sets_locked(diff)
    tag = tag_from_ref(pushed_ref) is not None
    return decide(lock, tag, is_authorized(msgs), mass_delete=count_deleted_files(diff))


def _from_prepush_stdin(stdin_text, cwd=None):
    """Moi dong: <local_ref> <local_sha> <remote_ref> <remote_sha>.
    Tong hop: bat ky ref nao vi pham -> BLOCK (tru khi authorized trong range do)."""
    ZERO = '0' * 40
    processed = 0
    # BOM-strip phong thu: pipe Windows/PowerShell co the chen U+FEFF dau stream
    # -> 'refs/tags/x' thanh U+FEFF+'refs/tags/x' khong match, guard bi mu (audit 2/7).
    stdin_text = (stdin_text or '').lstrip('﻿')
    for raw in stdin_text.splitlines():
        parts = raw.lstrip('﻿').split()
        if len(parts) < 4:
            continue
        processed += 1
        local_ref, local_sha, _remote_ref, remote_sha = parts[0], parts[1], parts[2], parts[3]
        if local_sha == ZERO:            # xoa ref -> bo qua
            continue
        # tag push
        tag = tag_from_ref(local_ref) is not None
        # range diff + messages
        if remote_sha == ZERO:           # ref moi -> lay toan bo commit cua local (gioi han)
            diff = _git(['diff', local_sha], cwd=cwd) if False else _git(['show', '--format=', local_sha], cwd=cwd)
            msgs = _git(['log', '--format=%B', '-1', local_sha], cwd=cwd)
        else:
            diff = _range_diff(remote_sha, local_sha, cwd=cwd)
            msgs = _range_messages(remote_sha, local_sha, cwd=cwd)
        lock = added_yaml_sets_locked(diff)
        code, reason = decide(lock, tag, is_authorized(msgs),
                              mass_delete=count_deleted_files(diff))
        if code != 0:
            return code, f'[{local_ref}] {reason}'
    if not processed:
        return 0, 'OK: stdin rong (khong co ref hop le de kiem).'
    return 0, f'OK: {processed} ref kiem — khong co lock/tag chua uy quyen.'


def main(argv=None):
    ap = argparse.ArgumentParser(description='SVHMP promotion guard (pre-push behavior gate)')
    ap.add_argument('--base', help='sha base cua range (dung voi --head)')
    ap.add_argument('--head', help='sha head cua range')
    ap.add_argument('--pushed-ref', help='ref dang push (vd refs/tags/pack1-constitution-v1.0)')
    args = ap.parse_args(argv)

    if args.base and args.head:
        code, reason = check_range(args.base, args.head, pushed_ref=args.pushed_ref)
    else:
        code, reason = _from_prepush_stdin(sys.stdin.read())

    print(f'[promotion_guard] {reason}')
    return code


if __name__ == '__main__':
    sys.exit(main())
