"""REALITY ANCHOR — fix/unsafe-golden-ep01-write.

Proves the two things that were BROKEN before this branch's fix (see
tools/text_batch_fix.py::verify_post_fix and
tests/cases/test_audio_gate_regression.py::case_5_substitute_violates_r111):

  (a) verify_post_fix() writes throwaway probe text directly into the REAL
      output/ep_01/episode.md, then runs several subprocess.run(...) calls,
      THEN restores from backup at the very end. Pre-fix there was no
      try/finally around that block: if any subprocess call raised (timeout,
      OSError, ...) the function exited with episode.md permanently left as
      the probe text — the golden EP01, corrupted. This test monkeypatches
      subprocess.run to raise mid-call and asserts episode.md is still
      restored to its original content afterwards.

  (b) case_5_substitute_violates_r111()'s cleanup tried to "resync"
      output/ep_01/episode_tts_ready.md by rerunning
      tools/tts_adapter_pre_render.py --ep 1 --apply against the real ep_01
      dir. That naive re-derivation does not byte-match the committed golden
      file (observed diff: 90+/118- lines every run), so running the audio
      gate regression suite left permanent uncommitted drift in
      output/ep_01/ even though the test itself PASSED. This test runs that
      suite via subprocess (same bridge pattern as tests/test_ci_suite.py)
      and asserts the git diff of output/ep_01/ is unchanged afterwards.

Both checks FAIL on the pre-fix code and PASS after the fix (verified by hand
during development via `git stash` — see the fix commit message for the
recorded before/after evidence).
"""
import subprocess
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent
EPISODE = BASE / "output/ep_01/episode.md"

sys.path.insert(0, str(BASE / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/
from _golden_lock import golden_lock  # FIX DEBT-005: serialize truy cap output/ep_01 THAT cross-process


def _git_diff_stat_ep01():
    r = subprocess.run(
        ["git", "diff", "--stat", "--", "output/ep_01/"],
        capture_output=True, text=True, cwd=str(BASE),
    )
    return r.stdout.strip()


def test_verify_post_fix_restores_episode_on_exception(monkeypatch):
    """(a) An exception raised mid-verify_post_fix (e.g. a subprocess
    timeout) must NOT leave output/ep_01/episode.md overwritten with the
    probe text — it must be restored to its pre-call content."""
    import text_batch_fix as tbf

    def _boom(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="fake-subprocess", timeout=1)

    monkeypatch.setattr(tbf.subprocess, "run", _boom)

    with golden_lock():  # FIX DEBT-005: doc/verify episode.md THAT trong khoa cross-process
        original = EPISODE.read_text(encoding="utf-8")
        probe_text = original + "\n<!-- REALITY_ANCHOR_PROBE_TEXT -->\n"

        with pytest.raises(subprocess.TimeoutExpired):
            tbf.verify_post_fix(probe_text, ["R86"])

        current = EPISODE.read_text(encoding="utf-8")
        if current != original:
            # Safety net: don't leave the golden file dirty even if this
            # assertion is about to fail because of a real regression.
            EPISODE.write_text(original, encoding="utf-8")
        assert current == original, (
            "verify_post_fix must restore output/ep_01/episode.md from backup "
            "even when a subprocess call inside it raises. Pre-fix, an "
            "exception between the write and the restore left episode.md "
            "permanently overwritten with the probe text — exactly the bug "
            "this branch fixes."
        )


def test_audio_gate_regression_leaves_no_diff_in_output_ep01():
    """(b) Running the audio-gate regression suite must be a no-op on the
    real output/ep_01/ directory. Pre-fix this left a 90+/118- line diff on
    episode_tts_ready.md every run, even though the test itself PASSED."""
    # FIX DEBT-005: khoa cross-process bao quanh cua so observe (before -> subprocess -> after)
    # => khong tien trinh nao khac ghi output/ep_01 giua chung lam flip oracle git-diff.
    with golden_lock():
        before = _git_diff_stat_ep01()

        # test_audio_gate_regression.py is script-style (case_N() + main() under
        # `if __name__ == "__main__":`, no `def test_` functions) — same bridge
        # pattern tests/test_ci_suite.py uses: run it directly as a script and
        # assert exit 0, NOT via `python -m pytest` (which would collect 0 items).
        r = subprocess.run(
            [sys.executable, str(BASE / "tests/cases/test_audio_gate_regression.py")],
            capture_output=True, text=True, cwd=str(BASE), timeout=180,
        )
        assert r.returncode == 0, (
            f"tests/cases/test_audio_gate_regression.py failed:\n"
            f"{r.stdout[-2000:]}\n{r.stderr[-1000:]}"
        )

        after = _git_diff_stat_ep01()
        assert after == before, (
        "Running tests/cases/test_audio_gate_regression.py changed the git "
        "diff of output/ep_01/ — it must be a no-op on the real golden "
        "EP01. Pre-fix, process_ep()'s naive re-derivation of "
        "episode_tts_ready.md did not byte-match the committed golden file, "
        "leaving permanent uncommitted drift (this is the exact bug this "
        f"branch fixes).\nbefore:\n{before}\nafter:\n{after}"
    )
