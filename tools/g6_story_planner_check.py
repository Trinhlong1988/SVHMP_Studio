"""g6_story_planner_check.py — G6 GATE 1 CUA (mirror pattern g4_world_check.py/g3_dialogue_check.py).

G6a (Decision Engine) + G6b (Story Planner) CUNG chay trong 1 gate nay (khong tao gate
rieng cho G6b, tranh nhan doi R211 — dung theo comment cu da ghi truoc khi G6b build xong).

LUU Y (bai hoc G14 — ci_gate pytest fork-bomb): gate nay KHONG goi subprocess pytest.
Chi goi truc tiep cac script kiem tra (tu import contract/policy/roster, khong dung
pytest) -> khong co duong dua de quy nao.

Exit 0 = G6a+G6b PASS, exit 1 = FAIL.
"""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable

__version__ = "1.1.0"

SUITE = [
    ("G6a_D2_policy_check", "tools/decision_policy_check.py"),
    ("G6a_D3_packet_selfcheck", "tools/decision_engine.py"),
    ("G6b_D5_story_planner_selfcheck", "tools/story_planner.py"),
    ("G6b_D6a_schema_check", "tools/story_plan_schema_check.py"),
]


def run_suite():
    rows = []
    for key, rel in SUITE:
        r = subprocess.run([PY, str(REPO / rel)], capture_output=True, text=True, encoding="utf-8")
        rows.append({"key": key, "script": rel, "rc": r.returncode,
                    "tail": ((r.stdout or "") + (r.stderr or ""))[-500:]})
    return rows


def main():
    print(f"=== G6 STORY PLANNER CHECK v{__version__} (D6 — G6a + G6b) ===")
    rows = run_suite()
    fails = [row for row in rows if row["rc"] != 0]
    for row in rows:
        mark = "PASS" if row["rc"] == 0 else "FAIL"
        print(f"  [{mark}] {row['key']:<24} {row['script']} (exit {row['rc']})")
        if row["rc"] != 0:
            print(row["tail"])
    if fails:
        print(f"=== FAIL — {len(fails)}/{len(rows)} tang do: "
              f"{', '.join(row['key'] for row in fails)} ===")
        return 1
    print(f"=== PASS — {len(rows)}/{len(rows)} tang G6a+G6b xanh ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
