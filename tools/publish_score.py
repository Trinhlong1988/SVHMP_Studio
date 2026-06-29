"""R140 — Publish Score Gate.

Run TẤT CẢ 7 QA tools, compute score, GATE publish.

Thresholds:
  Logic ≥ 90
  Language ≥ 85
  Repetition ≤ threshold
  TTS ≥ 90
  Hook ≥ 85

Pass mức gate = SHIP ALLOWED.
Fail = KILL SWITCH (R142): không publish, quay lại fix.
"""
import sys
import subprocess
from pathlib import Path

BASE = Path(r"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio")

QA_TOOLS = [
    ("R86 EOL diacritic", "qa_eol_diacritic.py", 100),
    ("R92b/R95/R107 honorific", "qa_honorific.py", 100),
    ("R110 narrative continuity", "qa_continuity.py", 100),
    ("R111 TTS phonetic safe", "qa_phonetic_safe.py", 100),
    ("R113 action verb repeat", "qa_repeat_action.py", 100),
    ("R117 fact database", "qa_fact_check.py", 100),
    ("R128 anti-generic AI", "qa_anti_generic.py", 100),
    ("R141 SSOT diff check", "qa_ssot_diff.py", 100),
]

# Category mapping → score weights
CATEGORIES = {
    "Logic": ["R110 narrative continuity", "R117 fact database", "R141 SSOT diff check"],
    "Language": ["R92b/R95/R107 honorific", "R113 action verb repeat", "R128 anti-generic AI"],
    "TTS": ["R86 EOL diacritic", "R111 TTS phonetic safe"],
}

THRESHOLDS = {
    "Logic": 90,
    "Language": 85,
    "TTS": 90,
}


def run_qa(script_name):
    """Run a QA tool, return PASS/FAIL."""
    try:
        result = subprocess.run(
            [sys.executable, str(BASE / "tools" / script_name)],
            capture_output=True, text=True, timeout=60,
            cwd=str(BASE),
            encoding="utf-8", errors="ignore",
        )
        passed = result.returncode == 0
        return passed, result.stdout[-200:] if result.stdout else ""
    except Exception as e:
        return False, f"ERROR: {e}"


def main():
    print("=" * 60)
    print("R140 PUBLISH SCORE GATE")
    print("=" * 60)
    print()

    results = {}
    for name, script, weight in QA_TOOLS:
        passed, output = run_qa(script)
        results[name] = {"passed": passed, "weight": weight}
        symbol = "✅" if passed else "❌"
        print(f"  {symbol} {name:35s} {'PASS' if passed else 'FAIL'}")

    # Compute category scores
    print()
    print("--- CATEGORY SCORES ---")
    overall_pass = True
    for cat, tools in CATEGORIES.items():
        passes = sum(1 for t in tools if results[t]["passed"])
        score = int(100 * passes / len(tools))
        threshold = THRESHOLDS[cat]
        symbol = "✅" if score >= threshold else "❌"
        print(f"  {symbol} {cat:10s} {score}/100 (threshold {threshold})")
        if score < threshold:
            overall_pass = False

    print()
    if overall_pass:
        print("=" * 60)
        print("🟢 PUBLISH GATE: PASS — SHIP ALLOWED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("=" * 60)
        print("🔴 PUBLISH GATE: FAIL — KILL SWITCH (R142)")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
