"""g6_story_planner_check.py — G6 GATE 1 CUA (mirror pattern g4_world_check.py/g3_dialogue_check.py).

Hien tai CHI wire phan G6a (Decision Engine) — G6b (story_planner.py) CHUA build (blocked
boi G4 D1/D2, xem TASK_G6_STORY_PLANNER.md). Khi G6b xong se them stage vao SUITE nay
(khong tao gate rieng, tranh nhan doi R211).

LUU Y (bai hoc G14 — ci_gate pytest fork-bomb): gate nay KHONG goi subprocess pytest.
Chi goi truc tiep 2 script kiem tra (decision_policy_check.py tu no da import contract+
policy, khong dung pytest) -> khong co duong dua de quy nao.

Exit 0 = G6a PASS, exit 1 = FAIL.
"""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable

__version__ = "1.0.0"

SUITE = [
    ("G6a_D2_policy_check", "tools/decision_policy_check.py"),
    ("G6a_D3_packet_selfcheck", "tools/decision_engine.py"),
]


def run_suite():
    rows = []
    for key, rel in SUITE:
        r = subprocess.run([PY, str(REPO / rel)], capture_output=True, text=True, encoding="utf-8")
        rows.append({"key": key, "script": rel, "rc": r.returncode,
                    "tail": ((r.stdout or "") + (r.stderr or ""))[-500:]})
    return rows


def main():
    print(f"=== G6 STORY PLANNER CHECK v{__version__} (D6 — G6a portion, G6b chua build) ===")
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
    print(f"=== PASS — {len(rows)}/{len(rows)} tang G6a xanh (G6b: xem TASK_G6, blocked boi G4) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
