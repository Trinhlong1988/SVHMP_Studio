"""g8_qa_runtime_check.py — G8 GATE 1 CUA (mirror pattern g6_story_planner_check.py).

G8 = RECONCILE domain qa_runtime (KHONG build manager moi). Gate nay canh gac cac INVARIANT
da chot o D1/D2/D4 + DEBT-005 fix khong bi regress. Dung STATIC-check (doc file + regex) —
KHONG import deps nang (underthesea...), KHONG goi subprocess pytest (bai hoc G14 fork-bomb).

Invariant kiem:
  1. D2  — file_index.yaml map tools/qa_skeptic_orchestrator.py -> qa_runtime (manager chinh thuc,
     blueprint:613). Neu ai doi lai generation = regress D2.
  2. D4  — pack5/19_qa_pipeline.md da codify luong #3 (orchestrator VNQA/skeptic). Marker bat buoc.
  3. VNQA — vnqa/pipeline.py chay H1-H10 that (run_all goi h1..h10). Chong nham nhan stale H1-H7.
  4. DEBT-005 — tests/_golden_lock.py ton tai + expose golden_lock (fix race concurrent-pytest).
  5. D5  — qa_verdict_schema.yaml + qa_verdict_adapter.py + preflight JSON (option B thin_wrapper).
  6. D3  — qa_post_render.py::audit_pause() delegate qa_pause_silence.audit_array() (khong
     reimplement) - them 9/7 sau khi CMD_AUDIT phat hien D3 dedup thieu bao ve regression.

Exit 0 = PASS, exit 1 = FAIL.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

REPO = Path(__file__).resolve().parent.parent
__version__ = "1.1.0"


def _read(rel):
    p = REPO / rel
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8", errors="replace")


def check_d2_orchestrator_domain():
    """D2: file_index map qa_skeptic_orchestrator.py -> qa_runtime (KHONG phai generation)."""
    txt = _read("governance/file_index.yaml")
    if txt is None:
        return False, "governance/file_index.yaml khong ton tai"
    # tim block entry cua file va doc dong 'domain:' ke tiep
    m = re.search(r"tools/qa_skeptic_orchestrator\.py:\s*\n\s*domain:\s*(\S+)", txt)
    if not m:
        return False, "khong tim thay entry qa_skeptic_orchestrator.py trong file_index"
    dom = m.group(1)
    if dom != "qa_runtime":
        return False, f"domain = '{dom}' (ky vong 'qa_runtime' — D2 regress)"
    return True, "qa_skeptic_orchestrator -> qa_runtime"


def check_d4_pack5_codified():
    """D4: pack5/19 codify luong #3 (orchestrator VNQA/skeptic + H1-H10)."""
    txt = _read("governance/pack5/19_qa_pipeline.md")
    if txt is None:
        return False, "governance/pack5/19_qa_pipeline.md khong ton tai"
    need = ["qa_skeptic_orchestrator", "adversarial_skeptic", "H1-H10"]
    missing = [k for k in need if k not in txt]
    if missing:
        return False, f"pack5/19 thieu marker luong #3: {missing} (D4 regress)"
    return True, "pack5/19 co luong #3 (orchestrator/skeptic/H1-H10)"


def check_vnqa_h1_h10():
    """VNQA: pipeline.py dinh nghia h1..h10 + run_all goi du (chong nham nhan stale)."""
    txt = _read("tools/vnqa/pipeline.py")
    if txt is None:
        return False, "tools/vnqa/pipeline.py khong ton tai"
    missing_def = [f"h{i}" for i in range(1, 11)
                   if not re.search(rf"def {re.escape(f'h{i}')}_\w+\(self", txt)]
    if missing_def:
        return False, f"thieu dinh nghia method: {missing_def}"
    missing_call = [f"h{i}" for i in range(1, 11)
                    if not re.search(rf"self\.{re.escape(f'h{i}')}_\w+\(", txt)]
    if missing_call:
        return False, f"run_all khong goi: {missing_call}"
    return True, "H1-H10 dinh nghia + goi day du (10/10)"


def check_debt005_golden_lock():
    """DEBT-005: tests/_golden_lock.py ton tai + expose golden_lock."""
    txt = _read("tests/_golden_lock.py")
    if txt is None:
        return False, "tests/_golden_lock.py khong ton tai (DEBT-005 fix mat)"
    if "def golden_lock(" not in txt:
        return False, "tests/_golden_lock.py thieu def golden_lock()"
    return True, "golden_lock cross-process ton tai"


def check_d5_verdict_schema():
    """D5 (option B thin_wrapper): schema field-hoa + adapter + preflight JSON prerequisite.
    - qa_verdict_schema.yaml ton tai, canonical 4-enum, owner qa_runtime.
    - qa_verdict_adapter.py ton tai, du 3 bang map + xu ly exit_2 (ToolingError).
    - svhmp_preflight_qa.py da phat JSON verdict (prerequisite), GIU exit code cu."""
    sch = _read("governance/blueprint/schemas/qa_verdict_schema.yaml")
    if sch is None:
        return False, "qa_verdict_schema.yaml chua field-hoa"
    need_enum = ["PASS", "PASS_WITH_WARNING", "REGEN", "REVIEW_REQUIRED"]
    miss = [e for e in need_enum if e not in sch]
    if miss or "canonical_verdict" not in sch or "owner_domain: qa_runtime" not in sch:
        return False, f"schema thieu canonical/enum/owner: {miss}"
    ad = _read("tools/qa_verdict_adapter.py")
    if ad is None:
        return False, "tools/qa_verdict_adapter.py khong ton tai (option B adapter)"
    for marker in ["MAP_ORCHESTRATOR", "MAP_VNQA", "MAP_PREFLIGHT", "ToolingError"]:
        if marker not in ad:
            return False, f"adapter thieu {marker}"
    pf = _read("tools/svhmp_preflight_qa.py")
    if pf is None or "preflight_ep_" not in pf or "sys.exit(0)" not in pf or "sys.exit(1)" not in pf:
        return False, "preflight chua phat JSON verdict HOAC mat exit code cu (backward-compat)"
    return True, "schema+adapter+preflight-JSON (option B) day du"


def _pause_delegation_body_ok(src):
    """Pure check TREN SOURCE TEXT (khong doc file - de mutation-proof test goi truc tiep
    tren ban da mutate trong bo nho): body ham audit_pause() PHAI goi
    qa_pause_silence.audit_array() (delegation D3, 9/7) va KHONG con vong lap reimplement
    detect (win_n/energy_db) - dung chung boi check_d3_pause_delegation() (gate) va
    tests/test_qa_post_render_pause_delegation.py (mutation-proof), R211 khong nhan doi logic."""
    m = re.search(r"def audit_pause\(.*?\n(?=def |\Z)", src, re.DOTALL)
    if not m:
        return False, "khong tim thay ham audit_pause() trong qa_post_render.py"
    body = m.group(0)
    # \(\s*audio\b bat buoc CO tham so (goi that voi audio/sr) - tranh khop nham voi docstring
    # chi NHAC ten ham "qa_pause_silence.audit_array()" (rong, khong phai loi goi that).
    if not re.search(r"qa_pause_silence\.audit_array\(\s*audio\b", body):
        return False, "audit_pause() khong con goi THAT qa_pause_silence.audit_array(audio,...) - D3 delegation bi go (regression)"
    if "win_n = int(0.020" in body:
        return False, "audit_pause() co dau hieu reimplement lai vong lap detect (win_n/energy_db) - vi pham dedup D3"
    return True, "audit_pause() delegate dung qa_pause_silence.audit_array(), khong reimplement"


def check_d3_pause_delegation():
    """D3 (9/7, CMD_AUDIT phat hien thieu bao ve): qa_post_render.py::audit_pause() PHAI
    delegate qa_pause_silence.audit_array() - khong duoc quay lai reimplement logic."""
    txt = _read("tools/qa_post_render.py")
    if txt is None:
        return False, "tools/qa_post_render.py khong ton tai"
    return _pause_delegation_body_ok(txt)


SUITE = [
    ("D2_orchestrator_domain", check_d2_orchestrator_domain),
    ("D4_pack5_codified", check_d4_pack5_codified),
    ("VNQA_h1_h10", check_vnqa_h1_h10),
    ("DEBT005_golden_lock", check_debt005_golden_lock),
    ("D5_verdict_schema", check_d5_verdict_schema),
    ("D3_pause_delegation", check_d3_pause_delegation),
]


def main():
    print(f"=== G8 QA RUNTIME CHECK v{__version__} (D7 — reconcile invariants) ===")
    fails = []
    for key, fn in SUITE:
        try:
            ok, detail = fn()
        except Exception as e:  # noqa: BLE001 — gate phai bao FAIL ro, khong crash im
            ok, detail = False, f"EXCEPTION: {e}"
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {key:<24} {detail}")
        if not ok:
            fails.append(key)
    if fails:
        print(f"=== FAIL — {len(fails)}/{len(SUITE)} invariant: {', '.join(fails)} ===")
        return 1
    print(f"=== PASS — {len(SUITE)}/{len(SUITE)} invariant G8 xanh ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
