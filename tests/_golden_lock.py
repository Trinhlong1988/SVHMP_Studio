"""Cross-process lock cho cac test cham vao output/ep_01/ THAT dung chung.

FIX TRIET DE DEBT-005 (residual): DEBT-005 da co lap tools/text_batch_fix.py::
verify_post_fix() sang tempfile, NHUNG con SOT 2 test writer thi that giam nhau khi
nhieu phien `pytest` chay dong thoi tren cung repo (C:\\Users\\Admin\\SVHMP_git):
  - tests/cases/test_publish_score.py::main()  -> ghi probe vao episode.md THAT + rebuild
    episode_tts_ready.md THAT (try/finally restore) — an toan 1 tien trinh, corrupt cross-process.
  - tests/cases/test_forbidden_phrases.py::main() — y het pattern.
Va 1 observer nhay cam: tests/test_golden_ep01_write_safety_reality_anchor.py::
test_audio_gate_regression_leaves_no_diff_in_output_ep01 dung `git diff --stat output/ep_01/`
lam oracle — bat ky tien trinh nao ghi ep_01 trong cua so do => flip assertion.

Lock nay serialize dung cac diem do (mutual exclusion cross-process). DEBT-005 dong 81
da de xuat huong nay ("filelock/msvcrt.locking khoa file that trong luc probe chay").

An toan CI: BEST-EFFORT — het timeout thi proceed kem canh bao (KHONG deadlock gate moi phien);
stale-lock (tien trinh giu bi crash) tu doc lai theo mtime; reentrant trong CUNG 1 tien trinh.
Lock file dat o tempdir may (KHONG trong repo — tranh lam ban `git status`/`git diff` cua chinh
test observer), ten khoa theo hash duong dan repo -> chi cac tien trinh dung CHUNG output/ep_01
vat ly moi tranh chap.
"""
import hashlib
import os
import tempfile
import time
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent
_LOCK_PATH = (Path(tempfile.gettempdir()) /
              f"svhmp_golden_ep01_{hashlib.md5(str(_BASE).encode()).hexdigest()[:8]}.lock")
_STALE_SEC = 120.0        # lock cu hon nguong nay = tien trinh giu da crash -> doat lai
_ACQUIRE_TIMEOUT = 180.0  # het thi proceed best-effort (khong deadlock CI)
_POLL_SEC = 0.05
_depth = 0                # reentrancy guard trong CUNG 1 tien trinh


class _GoldenLock:
    def __enter__(self):
        global _depth
        if _depth > 0:            # da giu trong tien trinh nay -> reentrant no-op
            _depth += 1
            return self
        deadline = time.monotonic() + _ACQUIRE_TIMEOUT
        while True:
            try:
                fd = os.open(str(_LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(fd, f"{os.getpid()} {time.time()}".encode())
                finally:
                    os.close(fd)
                _depth = 1
                return self
            except FileExistsError:
                try:
                    age = time.time() - _LOCK_PATH.stat().st_mtime
                except OSError:
                    continue          # bien mat giua chung -> thu lai ngay
                if age > _STALE_SEC:
                    try:
                        _LOCK_PATH.unlink()
                    except OSError:
                        pass
                    continue
                if time.monotonic() > deadline:
                    print(f"[golden_lock] WARN: acquire timeout {_ACQUIRE_TIMEOUT}s "
                          f"-> proceed best-effort (khong deadlock CI)")
                    _depth = 1
                    return self
                time.sleep(_POLL_SEC)

    def __exit__(self, *exc):
        global _depth
        if _depth > 1:
            _depth -= 1
            return False
        _depth = 0
        try:
            _LOCK_PATH.unlink()
        except OSError:
            pass
        return False


def golden_lock():
    """Context manager: `with golden_lock(): ...` bao quanh doan cham output/ep_01 THAT."""
    return _GoldenLock()
