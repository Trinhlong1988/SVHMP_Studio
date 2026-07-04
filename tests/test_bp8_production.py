"""BP8 — mutation battery cho bp8_production_check (đòn audit báo trước TASK_BP8).

Mutation TASK sẽ bắn: tool má trong stage exists → FAIL · render_chain lệch
runtime_flow → FAIL · khai gate "auto-caption" không tồn tại → FAIL · ngưỡng
hardcode → FAIL. Mỗi negative assert MARKER cụ thể (bài học: test phải cắn).

pytest-func FLAT -> collect trong `pytest tests/` và ci_gate.
"""
import copy
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from blueprint_constitution_check import load_yaml_no_dup  # noqa: E402
from bp8_production_check import (  # noqa: E402
    check_render_chain, check_golden_output, check_distribution_spec,
    D_RENDER, D_GOLDEN, D_DIST, D_BP4_FLOW)

RENDER = load_yaml_no_dup(D_RENDER.read_text(encoding='utf-8'))
GOLDEN = load_yaml_no_dup(D_GOLDEN.read_text(encoding='utf-8'))
DIST = load_yaml_no_dup(D_DIST.read_text(encoding='utf-8'))
BP4_FLOW = load_yaml_no_dup(D_BP4_FLOW.read_text(encoding='utf-8'))
CLI = REPO / 'tools' / 'bp8_production_check.py'


# ---------- POSITIVE (reality anchor: data thật) ----------

def test_cli_exit_zero_on_real_data():
    r = subprocess.run([sys.executable, str(CLI)], capture_output=True,
                       text=True, encoding='utf-8')
    assert r.returncode == 0, f'checker phai PASS tren data bp8 that:\n{r.stdout}'


def test_real_render_chain_zero_violations():
    assert check_render_chain(RENDER, BP4_FLOW) == []


def test_real_golden_output_zero_violations():
    assert check_golden_output(GOLDEN) == []


def test_real_distribution_spec_zero_violations():
    assert check_distribution_spec(DIST, BP4_FLOW) == []


def test_real_7_stages_machine_counted():
    assert len(RENDER['stages']) == 7


def test_real_8_golden_criteria_machine_counted():
    assert len(GOLDEN['criteria']) == 8


# ---------- MUTATIONS (đòn TASK báo trước — mỗi cái phải CẮN) ----------

def _mut_render():
    return copy.deepcopy(RENDER)


def _mut_golden():
    return copy.deepcopy(GOLDEN)


def _mut_dist():
    return copy.deepcopy(DIST)


def test_mut_tool_ma_in_exists_stage_bites():
    """Đòn TASK: tool má trong stage exists → FAIL."""
    r = _mut_render()
    tts = next(s for s in r['stages'] if s['stage_id'] == 'tts')
    tts['tool']['path'] = 'tools/khong_ton_tai_dau.py'
    errs = check_render_chain(r, BP4_FLOW)
    assert any('DRIFT-BP4' in e or 'TOOL-MA' in e for e in errs), errs


def test_mut_render_chain_drift_domain_bites():
    """Đòn TASK: render_chain lệch runtime_flow (đổi domain) → FAIL."""
    r = _mut_render()
    aud = next(s for s in r['stages'] if s['stage_id'] == 'audio')
    aud['stage_id'] = 'audio_fake'
    errs = check_render_chain(r, BP4_FLOW)
    assert any('DRIFT-BP4 domain' in e for e in errs), errs


def test_mut_render_chain_drift_hop_number_bites():
    r = _mut_render()
    tts = next(s for s in r['stages'] if s['stage_id'] == 'tts')
    tts['bp4_hop'] = 99
    errs = check_render_chain(r, BP4_FLOW)
    assert any('bp4_hop 99 KHONG ton tai' in e for e in errs), errs


def test_mut_render_chain_drift_io_bites():
    r = _mut_render()
    qa = next(s for s in r['stages'] if s['stage_id'] == 'qa_runtime')
    qa['output'] = 'output_bia_dat'
    errs = check_render_chain(r, BP4_FLOW)
    assert any('DRIFT-BP4 output' in e for e in errs), errs


def test_mut_gate_unknown_khai_bites():
    """Đòn TASK: khai gate 'auto-caption' không tồn tại (path ma) → FAIL."""
    r = _mut_render()
    tts = next(s for s in r['stages'] if s['stage_id'] == 'tts')
    tts['gate'].append({'gate_id': 'AUTO_CAPTION', 'desc': 'khong ton tai',
                        'enforcement_mode': 'automated',
                        'wired_evidence': {'status': 'exists', 'path': 'tools/auto_caption_khong_ton_tai.py'}})
    errs = check_render_chain(r, BP4_FLOW)
    assert any('GATE-MA' in e and 'auto_caption' in e for e in errs), errs


def test_mut_gate_named_not_enforced_bites():
    """automated nhưng thiếu grep_evidence -> named != enforced FAIL."""
    r = _mut_render()
    tts = next(s for s in r['stages'] if s['stage_id'] == 'tts')
    tts['gate'].append({'gate_id': 'FAKE_AUTO', 'desc': 'bia automated khong bang chung',
                        'enforcement_mode': 'automated',
                        'wired_evidence': {'status': 'exists', 'path': 'tools/svhmp_v13_render.py'}})
    errs = check_render_chain(r, BP4_FLOW)
    assert any('NAMED-KHONG-ENFORCED' in e and 'FAKE_AUTO' in e for e in errs), errs


def test_mut_invalid_enforcement_mode_bites():
    r = _mut_render()
    tts = next(s for s in r['stages'] if s['stage_id'] == 'tts')
    tts['gate'][0]['enforcement_mode'] = 'semi_auto_ma'
    errs = check_render_chain(r, BP4_FLOW)
    assert any('enforcement_mode' in e and 'semi_auto_ma' in e for e in errs), errs


def test_mut_planned_missing_metadata_bites():
    r = _mut_render()
    video = next(s for s in r['stages'] if s['stage_id'] == 'video')
    del video['tool']['blocking_dependency']
    errs = check_render_chain(r, BP4_FLOW)
    assert any('video.tool' in e and 'blocking_dependency' in e for e in errs), errs


def test_mut_golden_hardcode_threshold_bites():
    """Đòn TASK: ngưỡng hardcode trong golden_output → FAIL."""
    g = _mut_golden()
    g['criteria'][0]['min_loudness_db'] = -16
    errs = check_golden_output(g)
    assert any('R195-HARDCODE' in e and 'min_loudness_db' in e for e in errs), errs


def test_mut_golden_hardcode_nested_bites():
    g = _mut_golden()
    g['meta']['sample_count'] = 90
    errs = check_golden_output(g)
    assert any('R195-HARDCODE' in e and 'sample_count' in e for e in errs), errs


def test_mut_golden_detector_ma_bites():
    g = _mut_golden()
    g['criteria'][0]['detector']['path'] = 'tools/khong_ton_tai_detector.py'
    errs = check_golden_output(g)
    assert any('DETECTOR-MA' in e for e in errs), errs


def test_mut_distribution_video_drift_bites():
    d = _mut_dist()
    d['video']['planned_path'] = 'tools/video_builder_khac.py'
    errs = check_distribution_spec(d, BP4_FLOW)
    assert any('video: DRIFT-BP4 planned_path' in e for e in errs), errs


def test_mut_distribution_analytics_tool_ma_bites():
    d = _mut_dist()
    d['analytics']['path'] = 'tools/analytics_khong_ton_tai.py'
    errs = check_distribution_spec(d, BP4_FLOW)
    assert any('analytics: TOOL-MA' in e for e in errs), errs
