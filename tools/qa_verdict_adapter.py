"""qa_verdict_adapter.py — G8 D5 (option B thin_wrapper, Mr.Long final_decision_9_7).

Đọc 3 format verdict QA THẬT đang chạy (orchestrator / VNQA / preflight) → trả 1 common_envelope
canonical theo governance/blueprint/schemas/qa_verdict_schema.yaml. Canonical enum 4 trạng thái:
[PASS, PASS_WITH_WARNING, REGEN, REVIEW_REQUIRED].

Phương án B: KHÔNG sửa output gốc của 3 tool — chỉ đọc + map ở lớp adapter mỏng này. exit_2 của
preflight = usage-error (R9) → TOOLING_ERROR, KHÔNG phải verdict tập (raise, không map bừa vào enum).

KHÔNG phụ thuộc domain generator (blueprint qa_runtime.forbidden_dependencies=[generator]).

Usage (CLI):
  python tools/qa_verdict_adapter.py --ep 1                 # ưu tiên orchestrator > vnqa > preflight
  python tools/qa_verdict_adapter.py --ep 1 --source vnqa   # ép đọc đúng 1 tầng
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNTIME_DIR = REPO / "runtime"

# Canonical enum — khớp governance/blueprint/schemas/qa_verdict_schema.yaml
CANONICAL = ("PASS", "PASS_WITH_WARNING", "REGEN", "REVIEW_REQUIRED")

# Bảng ánh xạ native → canonical (schema.mapping). Không mất thông tin: issues[] giữ trong envelope.
MAP_ORCHESTRATOR = {"PASS": "PASS", "PASS_WITH_WARNING": "PASS_WITH_WARNING",
                    "REGEN": "REGEN", "REVIEW_REQUIRED": "REVIEW_REQUIRED"}
MAP_VNQA = {"PASS": "PASS", "WARN": "PASS_WITH_WARNING", "FAIL": "REGEN"}
MAP_PREFLIGHT = {"PASS": "PASS", "FAIL": "REGEN"}

_FILE_TMPL = {
    "orchestrator": "final_verdict_ep_{}.json",
    "vnqa": "vnqa_ep_{}.json",
    "preflight": "preflight_ep_{}.json",
}
# Thứ tự thẩm quyền: orchestrator (tổng hợp cao nhất) > vnqa > preflight.
_PRIORITY = ("orchestrator", "vnqa", "preflight")


class VerdictError(ValueError):
    """Verdict native không hợp lệ / không map được về canonical."""


class ToolingError(RuntimeError):
    """Tín hiệu KHÔNG phải verdict tập (vd preflight exit_2 = usage-error)."""


def _envelope(verdict, source, ep_number, issues, severity_counts, reasoning, ts, raw):
    if verdict not in CANONICAL:
        raise VerdictError(f"verdict '{verdict}' không thuộc canonical {CANONICAL}")
    return {
        "verdict": verdict,
        "source": source,
        "ep_number": ep_number,
        "issues": list(issues or []),
        "severity_counts": dict(severity_counts or {"critical": 0, "warning": 0, "minor": 0}),
        "reasoning": reasoning or "",
        "ts": ts or "",
        "raw": raw,
    }


def adapt_orchestrator(d: dict) -> dict:
    nv = d.get("final_verdict")
    if nv not in MAP_ORCHESTRATOR:
        raise VerdictError(f"orchestrator final_verdict='{nv}' không hợp lệ")
    return _envelope(MAP_ORCHESTRATOR[nv], "orchestrator", d.get("ep_number"),
                     issues=[], severity_counts=d.get("vnqa_issues_count") or {},
                     reasoning=d.get("final_reasoning"), ts=d.get("ts"), raw=d)


def adapt_vnqa(d: dict) -> dict:
    nv = d.get("verdict")
    if nv not in MAP_VNQA:
        raise VerdictError(f"vnqa verdict='{nv}' không hợp lệ")
    return _envelope(MAP_VNQA[nv], "vnqa", d.get("ep_number"),
                     issues=d.get("issues") or [],
                     severity_counts=d.get("issues_count_by_severity") or {},
                     reasoning=None, ts=d.get("ts"), raw=d)


def adapt_preflight(d: dict) -> dict:
    if d.get("exit_code") == 2:
        raise ToolingError("preflight exit_2 = TOOLING_ERROR (usage-error) — không phải verdict tập")
    nv = d.get("verdict")
    if nv not in MAP_PREFLIGHT:
        raise VerdictError(f"preflight verdict='{nv}' không hợp lệ")
    # preflight issues là list chuỗi thô → chuẩn hoá về item envelope (severity warning: chặn render nhưng không phá cấu trúc).
    issues = [{"check": "preflight", "severity": "warning", "evidence": s} for s in (d.get("issues") or [])]
    return _envelope(MAP_PREFLIGHT[nv], "preflight", d.get("ep_number"),
                     issues=issues,
                     severity_counts={"critical": 0, "warning": len(issues), "minor": 0},
                     reasoning=None, ts=d.get("ts"), raw=d)


_ADAPTERS = {"orchestrator": adapt_orchestrator, "vnqa": adapt_vnqa, "preflight": adapt_preflight}


def adapt(source: str, native: dict) -> dict:
    """Map 1 dict verdict native (đã biết source) → common_envelope canonical."""
    if source not in _ADAPTERS:
        raise VerdictError(f"source '{source}' không hỗ trợ (chỉ {list(_ADAPTERS)})")
    return _ADAPTERS[source](native)


def load_and_adapt(source: str, ep_number: int, runtime_dir=RUNTIME_DIR) -> dict:
    p = Path(runtime_dir) / _FILE_TMPL[source].format(ep_number)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return adapt(source, json.loads(p.read_text(encoding="utf-8")))


def canonical_for_ep(ep_number: int, runtime_dir=RUNTIME_DIR) -> dict:
    """Trả envelope từ tầng thẩm quyền cao nhất có sẵn (orchestrator > vnqa > preflight)."""
    for source in _PRIORITY:
        try:
            return load_and_adapt(source, ep_number, runtime_dir)
        except FileNotFoundError:
            continue
    raise FileNotFoundError(f"không có verdict native nào cho ep {ep_number} trong {runtime_dir}")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--ep", type=int, required=True)
    ap.add_argument("--source", choices=list(_PRIORITY), default=None)
    ap.add_argument("--runtime", default=str(RUNTIME_DIR))
    args = ap.parse_args()
    try:
        if args.source:
            env = load_and_adapt(args.source, args.ep, args.runtime)
        else:
            env = canonical_for_ep(args.ep, args.runtime)
    except (FileNotFoundError, VerdictError, ToolingError) as e:
        print(f"[qa_verdict_adapter] {type(e).__name__}: {e}")
        return 2
    print(json.dumps(env, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
