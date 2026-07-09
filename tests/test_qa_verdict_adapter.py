"""Behavior test — qa_verdict_adapter (G8 D5, option B thin_wrapper).

Kiểm HÀNH VI THẬT (không text-grep): map từng native → canonical, exit_2 raise, priority
orchestrator>vnqa>preflight, round-trip file thật, và adapter KHỚP schema field-hóa (chống drift).
"""
import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import qa_verdict_adapter as A  # noqa: E402

SCHEMA = REPO / "governance/blueprint/schemas/qa_verdict_schema.yaml"


# ---------- map từng tầng ----------

def test_vnqa_map_warn_to_pass_with_warning():
    env = A.adapt_vnqa({"verdict": "WARN", "ep_number": 3,
                        "issues": ["x"], "issues_count_by_severity": {"critical": 0, "warning": 1, "minor": 0}})
    assert env["verdict"] == "PASS_WITH_WARNING"
    assert env["source"] == "vnqa"
    assert env["issues"] == ["x"]
    assert env["raw"]["verdict"] == "WARN"  # giữ payload gốc, không mất dữ liệu


def test_vnqa_map_fail_and_pass():
    assert A.adapt_vnqa({"verdict": "FAIL", "ep_number": 1})["verdict"] == "REGEN"
    assert A.adapt_vnqa({"verdict": "PASS", "ep_number": 1})["verdict"] == "PASS"


def test_orchestrator_identity_including_review_required():
    for nv in ("PASS", "PASS_WITH_WARNING", "REGEN", "REVIEW_REQUIRED"):
        env = A.adapt_orchestrator({"final_verdict": nv, "ep_number": 2, "final_reasoning": "r"})
        assert env["verdict"] == nv
        assert env["source"] == "orchestrator"
        assert env["reasoning"] == "r"


def test_preflight_map_and_issue_normalization():
    env = A.adapt_preflight({"verdict": "FAIL", "exit_code": 1, "ep_number": 1,
                             "issues": ["R1 ch3: SHORT", "R5 LAST"]})
    assert env["verdict"] == "REGEN"
    assert len(env["issues"]) == 2
    assert env["issues"][0] == {"check": "preflight", "severity": "warning", "evidence": "R1 ch3: SHORT"}
    assert env["severity_counts"]["warning"] == 2


def test_preflight_exit2_is_tooling_error_not_verdict():
    """exit_2 = usage-error (R9) → ToolingError, KHÔNG map bừa vào REVIEW_REQUIRED."""
    with pytest.raises(A.ToolingError):
        A.adapt_preflight({"verdict": "PASS", "exit_code": 2, "ep_number": 0})


def test_invalid_native_verdict_raises():
    with pytest.raises(A.VerdictError):
        A.adapt_vnqa({"verdict": "MAYBE", "ep_number": 1})
    with pytest.raises(A.VerdictError):
        A.adapt("unknown_source", {})


# ---------- load file thật + priority ----------

def _write(dirp, name, obj):
    (dirp / name).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def test_load_and_adapt_roundtrip_preflight(tmp_path):
    _write(tmp_path, "preflight_ep_1.json",
           {"tool": "preflight", "ep_number": 1, "verdict": "PASS", "exit_code": 0, "issues": [], "chunks": 40})
    env = A.load_and_adapt("preflight", 1, runtime_dir=tmp_path)
    assert env["verdict"] == "PASS" and env["source"] == "preflight"


def test_canonical_priority_orchestrator_beats_vnqa_preflight(tmp_path):
    _write(tmp_path, "preflight_ep_5.json", {"verdict": "FAIL", "exit_code": 1, "ep_number": 5})
    _write(tmp_path, "vnqa_ep_5.json", {"verdict": "WARN", "ep_number": 5})
    _write(tmp_path, "final_verdict_ep_5.json", {"final_verdict": "PASS", "ep_number": 5})
    env = A.canonical_for_ep(5, runtime_dir=tmp_path)
    assert env["source"] == "orchestrator" and env["verdict"] == "PASS"


def test_canonical_falls_back_when_higher_absent(tmp_path):
    _write(tmp_path, "vnqa_ep_7.json", {"verdict": "FAIL", "ep_number": 7})
    env = A.canonical_for_ep(7, runtime_dir=tmp_path)
    assert env["source"] == "vnqa" and env["verdict"] == "REGEN"


def test_canonical_missing_all_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        A.canonical_for_ep(99, runtime_dir=tmp_path)


# ---------- adapter KHỚP schema field-hóa (chống drift) ----------

def test_adapter_matches_schema_field_hoa():
    """CANONICAL enum + 3 bảng mapping trong adapter PHẢI khớp schema đã field-hóa."""
    doc = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
    sch = doc["schema"]
    assert tuple(sch["canonical_verdict"]["values"].keys()) == A.CANONICAL
    mp = sch["mapping"]
    assert mp["from_orchestrator"] == A.MAP_ORCHESTRATOR
    assert mp["from_vnqa"] == A.MAP_VNQA
    assert mp["from_preflight"] == A.MAP_PREFLIGHT
    # exit_2 tách riêng khỏi verdict enum
    assert mp["from_preflight_non_verdict"] == {"exit_2": "TOOLING_ERROR"}


def test_schema_meta_option_b_and_owner():
    doc = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
    assert doc["meta"]["owner_domain"] == "qa_runtime"
    assert doc["meta"]["adapter"] == "tools/qa_verdict_adapter.py"
    assert "APPROVED_B" in doc["meta"]["approval"]
