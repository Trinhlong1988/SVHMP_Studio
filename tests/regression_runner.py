"""Regression Test Runner — chạy 100 dataset qua 8 QA tools.

Đo:
- True Positive (negative sample → tool catches violation)
- True Negative (positive sample → tool clean PASS)
- False Positive (positive sample → tool báo nhầm)
- False Negative (negative sample → tool bỏ sót)

KPI threshold (Mr.Long lock):
- False Positive ≤ 10%
- False Negative ≤ 15%
- Detection Rate (Logic) ≥ 90%
"""
import os
import subprocess
import sys
import shutil
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EPISODE = BASE / "output/ep_01/episode.md"
GOLDEN = BASE / "output/ep_01/episode_golden_text.md"
POS_DIR = BASE / "tests/regression/positive"
NEG_DIR = BASE / "tests/regression/negative"

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/
from _golden_lock import golden_lock  # DEBT-005 vong3: serialize mutate output/ep_01 THAT cross-process

QA_TOOLS = [
    ("R86", "qa_eol_diacritic.py"),
    ("R92b", "qa_honorific.py"),
    ("R110", "qa_continuity.py"),
    ("R111", "qa_phonetic_safe.py"),
    ("R113", "qa_repeat_action.py"),
    ("R117", "qa_fact_check.py"),
    ("R128", "qa_anti_generic.py"),
    ("R141", "qa_ssot_diff.py"),
]


def run_qa(script):
    """Run QA tool, return exit code (0=PASS, !=0=FAIL)."""
    try:
        r = subprocess.run(
            [sys.executable, str(BASE / "tools" / script)],
            capture_output=True, cwd=str(BASE), timeout=30,
            text=True, encoding="utf-8", errors="ignore",
        )
        return r.returncode == 0
    except Exception:
        return False


def run_tts_adapter():
    """Rebuild tts_ready (for R86 scan)."""
    try:
        subprocess.run(
            [sys.executable, str(BASE / "tools/tts_adapter_pre_render.py"), "--ep", "1", "--apply"],
            capture_output=True, cwd=str(BASE), timeout=30,
        )
    except Exception:
        pass


def main():
    # DEBT-005 vong3: khoa cross-process bao quanh TOAN BO doan mutate output/ep_01 THAT (backup ->
    # copy fixture -> chay QA -> restore). Backup ten theo PID (khong con co dinh) lam lop phong thu 2.
    with golden_lock():
        _run(EPISODE.with_suffix(f".md.regression_backup.{os.getpid()}"))


def _run(backup):
    shutil.copy(EPISODE, backup)

    results = {tool[0]: {"TP": 0, "TN": 0, "FP": 0, "FN": 0} for tool in QA_TOOLS}

    try:
        start = time.time()

        # ===== POSITIVE samples (expect ALL PASS) =====
        pos_files = sorted(POS_DIR.glob("*.md"))
        print(f"[TESTER] Running 50 positive samples...")
        for i, f in enumerate(pos_files):
            shutil.copy(f, EPISODE)
            run_tts_adapter()
            for rule_id, script in QA_TOOLS:
                passed = run_qa(script)
                if passed:
                    results[rule_id]["TN"] += 1
                else:
                    results[rule_id]["FP"] += 1
            if (i + 1) % 10 == 0:
                print(f"    ... {i+1}/50 done")

        # ===== NEGATIVE samples (expect AT LEAST 1 tool catches) =====
        neg_files = sorted(NEG_DIR.glob("*.md"))
        print(f"[TESTER] Running 50 negative samples...")
        for i, f in enumerate(neg_files):
            shutil.copy(f, EPISODE)
            run_tts_adapter()
            # Determine which rule this negative targets from filename
            target_rule = None
            for rule_id, _ in QA_TOOLS:
                if rule_id in f.stem:
                    target_rule = rule_id
                    break
            # MIX_*** negatives don't target single rule
            for rule_id, script in QA_TOOLS:
                passed = run_qa(script)
                # If this is the target rule: expect FAIL (TP) ; if not target: should still PASS or not counted
                if target_rule == rule_id:
                    if not passed:
                        results[rule_id]["TP"] += 1
                    else:
                        results[rule_id]["FN"] += 1
            if (i + 1) % 10 == 0:
                print(f"    ... {i+1}/50 done")

        elapsed = int(time.time() - start)

    finally:
        shutil.copy(backup, EPISODE)
        backup.unlink()
        run_tts_adapter()

    # Report
    print()
    print("=" * 80)
    print(f"REGRESSION RUNNER REPORT — 100 samples × 8 QA tools — {elapsed}s")
    print("=" * 80)
    print()
    print(f"{'Rule':<8s} {'TP':>4s} {'TN':>4s} {'FP':>4s} {'FN':>4s} {'FP%':>6s} {'FN%':>6s} {'Detect%':>8s} {'Verdict':<10s}")
    print("-" * 80)
    all_pass = True
    for rule_id, _ in QA_TOOLS:
        r = results[rule_id]
        total_pos = r["TN"] + r["FP"]
        total_neg = r["TP"] + r["FN"]
        fp_pct = (r["FP"] / total_pos * 100) if total_pos else 0
        fn_pct = (r["FN"] / total_neg * 100) if total_neg else 0
        detect_pct = (r["TP"] / total_neg * 100) if total_neg else 100  # no negative for this rule
        kpi_pass = fp_pct <= 10 and (total_neg == 0 or fn_pct <= 15)
        verdict = "PASS" if kpi_pass else "FAIL"
        if not kpi_pass:
            all_pass = False
        print(f"{rule_id:<8s} {r['TP']:>4d} {r['TN']:>4d} {r['FP']:>4d} {r['FN']:>4d} {fp_pct:>5.1f}% {fn_pct:>5.1f}% {detect_pct:>7.1f}% {verdict:<10s}")
    print()
    print(f"KPI thresholds (Mr.Long lock): FP ≤ 10%, FN ≤ 15%")
    print(f"Overall: {'✅ ALL PASS' if all_pass else '❌ SOME FAIL'}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
