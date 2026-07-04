"""BP8 PRODUCTION CHECK v1.0.0 — gate máy cho BP8 Production Architecture.

Check:
  1  DUP-KEY loader single-impl (import blueprint_constitution_check) + version
     khớp checker/3 file bp8 (render_chain/golden_output/distribution_spec).
  2  render_chain: mỗi stage.bp4_hop PHẢI khớp CHÍNH XÁC domain/status/path (hoặc
     planned_path) của hop tương ứng trong bp4/runtime_flow.yaml (LOCKED) — lệch
     (drift) = FAIL · stage tool.status=exists path PHẢI tồn tại thật (TOOL-MA) ·
     gate.enforcement_mode=automated PHẢI có grep_evidence + wired_evidence.path
     tồn tại thật (named ≠ enforced) · planned đủ 5 metadata.
  3  golden_output: KHÔNG số (int/float) bất kỳ đâu trong toàn file (scan TOÀN
     FILE ngay từ đầu, tái sử dụng `_numeric_leaks` — KHÔNG lặp lỗ hổng BP6 4/7) ·
     mọi criterion.detector.status=exists path PHẢI tồn tại thật.
  4  distribution_spec: video/publisher status/path PHẢI khớp CHÍNH XÁC bp4 hop
     8/9 · analytics.status=exists path PHẢI tồn tại thật.

Exit 0 = PASS, exit 1 = FAIL.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402
from bp6_decision_check import _numeric_leaks  # noqa: E402 (tai su dung — khong viet lai)

__version__ = '1.0.0'

BP8 = REPO / 'governance' / 'blueprint' / 'bp8'
D_RENDER = BP8 / 'render_chain.yaml'
D_GOLDEN = BP8 / 'golden_output.yaml'
D_DIST = BP8 / 'distribution_spec.yaml'
D_BP4_FLOW = REPO / 'governance' / 'blueprint' / 'bp4' / 'runtime_flow.yaml'

PLANNED_META = ['planned_path', 'owner', 'reason_not_exists_yet',
                'target_milestone', 'blocking_dependency']


def _load(path, errs, label):
    try:
        return load_yaml_no_dup(Path(path).read_text(encoding='utf-8'))
    except DupKeyError as e:
        errs.append(f'{label}: DUP-KEY — {e}')
    except Exception as e:
        errs.append(f'{label}: khong doc duoc: {e}')
    return None


def _bp4_hops_by_num(bp4_flow):
    return {h['hop']: h for h in (bp4_flow or {}).get('flow') or []}


def _check_planned(label, ref, errs):
    for m in PLANNED_META:
        if not ref.get(m):
            errs.append(f'{label}: PLANNED HONESTY — thieu metadata {m}')


def _check_tool_ref(label, ref, errs, root=REPO):
    """So sanh 1 'tool'/'via' ref (status/path hoac planned_path) — tra ve gi de doi chieu BP4."""
    st = ref.get('status')
    if st == 'exists':
        p = ref.get('path')
        if not p or not (Path(root) / p).exists():
            errs.append(f'{label}: TOOL-MA — status exists nhung path KHONG ton tai (phantom): {p}')
    elif st == 'planned':
        _check_planned(label, ref, errs)
    else:
        errs.append(f'{label}: status {st!r} khong thuoc exists|planned')


def check_render_chain(render, bp4_flow, root=REPO):
    """Check 2. Tra ve list loi."""
    errs = []
    hops = _bp4_hops_by_num(bp4_flow)
    for stage in (render or {}).get('stages') or []:
        sid = stage.get('stage_id', '?')
        hn = stage.get('bp4_hop')
        hop = hops.get(hn)
        if hop is None:
            errs.append(f'{sid}: bp4_hop {hn} KHONG ton tai trong bp4/runtime_flow.yaml')
            continue
        # DRIFT: domain phai khop stage_id, input/output/status/path phai khop BP4 THAT
        if hop.get('domain') != sid:
            errs.append(f'{sid}: DRIFT-BP4 domain BP4={hop.get("domain")!r} != stage_id={sid!r}')
        if hop.get('input') != stage.get('input'):
            errs.append(f'{sid}: DRIFT-BP4 input lech BP4 hop {hn}')
        if hop.get('output') != stage.get('output'):
            errs.append(f'{sid}: DRIFT-BP4 output lech BP4 hop {hn}')
        bp4_via = hop.get('via') or {}
        tool = stage.get('tool') or {}
        if bp4_via.get('status') != tool.get('status'):
            errs.append(f'{sid}: DRIFT-BP4 tool.status ({tool.get("status")}) != BP4 via.status ({bp4_via.get("status")})')
        bp4_path = bp4_via.get('path') or bp4_via.get('planned_path')
        tool_path = tool.get('path') or tool.get('planned_path')
        if bp4_path != tool_path:
            errs.append(f'{sid}: DRIFT-BP4 tool path ({tool_path}) != BP4 via path ({bp4_path})')

        _check_tool_ref(f'{sid}.tool', tool, errs, root)

        for g in stage.get('gate') or []:
            gid = g.get('gate_id', '?')
            mode = g.get('enforcement_mode')
            if mode not in ('automated', 'manual'):
                errs.append(f'{sid}.{gid}: enforcement_mode {mode!r} khong thuoc automated|manual')
            we = g.get('wired_evidence') or {}
            wp = we.get('path')
            if wp and not (Path(root) / wp).exists():
                errs.append(f'{sid}.{gid}: GATE-MA — wired_evidence.path KHONG ton tai: {wp}')
            if mode == 'automated' and not we.get('grep_evidence') and not we.get('grep_lines'):
                errs.append(f'{sid}.{gid}: NAMED-KHONG-ENFORCED — enforcement_mode=automated nhung thieu grep_evidence/grep_lines (khong chung minh wired that)')
    return errs


def check_golden_output(golden):
    """Check 3. Tra ve list loi."""
    errs = []
    for leak in _numeric_leaks(golden, 'golden_output', allowed_keys=set()):
        errs.append(f'R195-HARDCODE: so hardcode trong golden_output tai {leak} '
                    '(golden_output la FORMAT thuan, 0 so duoc phep — threshold_source la MO TA, khong phai gia tri)')
    for c in (golden or {}).get('criteria') or []:
        cid = c.get('criterion_id', '?')
        det = c.get('detector') or {}
        if det.get('status') == 'exists':
            p = det.get('path')
            if not p or not (Path(REPO) / p).exists():
                errs.append(f'{cid}: DETECTOR-MA — detector.path KHONG ton tai: {p}')
    return errs


def check_distribution_spec(dist, bp4_flow, root=REPO):
    """Check 4. Tra ve list loi."""
    errs = []
    hops = _bp4_hops_by_num(bp4_flow)
    for key, hop_num in (('video', 8), ('publisher', 9)):
        block = (dist or {}).get(key) or {}
        hop = hops.get(hop_num) or {}
        bp4_via = hop.get('via') or {}
        if block.get('status') != bp4_via.get('status'):
            errs.append(f'{key}: DRIFT-BP4 status ({block.get("status")}) != BP4 hop {hop_num} ({bp4_via.get("status")})')
        if block.get('planned_path') != bp4_via.get('planned_path'):
            errs.append(f'{key}: DRIFT-BP4 planned_path lech BP4 hop {hop_num}')
        if block.get('status') == 'planned':
            _check_planned(key, block, errs)
    analytics = (dist or {}).get('analytics') or {}
    if analytics.get('status') == 'exists':
        p = analytics.get('path')
        if not p or not (Path(root) / p).exists():
            errs.append(f'analytics: TOOL-MA — path KHONG ton tai: {p}')
    return errs


def main():
    errs = []
    render = _load(D_RENDER, errs, 'render_chain')
    golden = _load(D_GOLDEN, errs, 'golden_output')
    dist = _load(D_DIST, errs, 'distribution_spec')
    bp4_flow = _load(D_BP4_FLOW, errs, 'bp4_runtime_flow')

    if None not in (render, golden, dist):
        for doc, label in ((render, 'render_chain'), (golden, 'golden_output'),
                           (dist, 'distribution_spec')):
            v = str((doc.get('meta') or {}).get('version'))
            if v != __version__:
                errs.append(f'{label}: version {v} != checker {__version__}')
        errs += check_render_chain(render, bp4_flow)
        errs += check_golden_output(golden)
        errs += check_distribution_spec(dist, bp4_flow)

    print(f'=== BP8 PRODUCTION CHECK v{__version__} ===')
    for e in errs:
        print(f'  [VIOLATION] {e}')
    n_st = len(((render or {}).get('stages')) or [])
    n_cr = len(((golden or {}).get('criteria')) or [])
    print(f'  stages: {n_st}/7 (mirror bp4 hop 3-9) · golden criteria: {n_cr}/8')
    print(f"=== {'FAIL — ' + str(len(errs)) + ' vi pham' if errs else 'PASS'} ===")
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
