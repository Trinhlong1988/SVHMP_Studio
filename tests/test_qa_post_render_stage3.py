"""Behavior test STAGE 3 post-render QA (TASK_AUDIT_HIGH_G2_G8 G8-2..G8-4).

Trước đây 3/4 check STAGE 3 (audit_spectrum/audit_boundary/audit_head_onset) + boundary ngưỡng
`noisy<=1` của qa_pause_silence.audit_array HOÀN TOÀN 0 test — đổi 1 hằng số ngưỡng vẫn xanh.
Test này gọi HÀM THẬT với audio tổng hợp có kiểm soát, assert CẢ HAI phía boundary (mutation-proof
cho ngưỡng: đổi toán tử so sánh làm ít nhất 1 assert vỡ) + source-assert hằng số ngưỡng gốc.

KHÔNG sửa source audio_qa (đã LOCKED g8/audio_qa) — chỉ thêm test.
"""
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import qa_post_render as qpr  # noqa: E402
import qa_pause_silence as qps  # noqa: E402

SR = 16000


# ---------- dựng audio tổng hợp xác định (deterministic, không random) ----------

def _const(ms, amp):
    return np.full(int(SR * ms / 1000), float(amp), dtype=np.float64)


def _clean_pause(ms=1400):
    """Khoảng lặng thật: mọi frame RMS < -55 (silence) + peak nội < -70 => CLEAN."""
    return _const(ms, 1e-6)


def _noisy_pause(ms=1400):
    """Frame vẫn 'silence' (RMS thấp) nhưng có 1 spike nội => peak >= -55 => NOISY."""
    a = _const(ms, 1e-6)
    a[len(a) // 2] = 0.004  # 20*log10(0.004) ≈ -48 dB (>= -55) tại giữa pause (ngoài margin 100ms)
    return a


def _voice(ms=400, amp=0.1):
    """Đoạn 'có tiếng' RMS ≈ -20 dB (> -55) — ngăn cách/kết thúc pause, onset đạt mức voice."""
    return _const(ms, amp)


def make_pause_audio(n_clean=0, n_noisy=0):
    parts = [_voice()]
    for _ in range(n_clean):
        parts += [_clean_pause(), _voice()]
    for _ in range(n_noisy):
        parts += [_noisy_pause(), _voice()]
    return np.concatenate(parts), SR


# ---------- G8-2: qa_pause_silence.audit_array boundary noisy<=1 (R96 v3.3) ----------

def test_audit_array_noisy_boundary_0_1_pass_2_fail():
    """0 noisy -> PASS; 1 noisy -> PASS (R96 tolerance); 2 noisy -> FAIL. Đây là mutation-proof
    của ngưỡng noisy<=1: đổi thành ==0 làm case 1 vỡ; đổi thành <=2 làm case 2 vỡ."""
    a0, _ = make_pause_audio(n_clean=2, n_noisy=0)
    a1, _ = make_pause_audio(n_clean=1, n_noisy=1)
    a2, _ = make_pause_audio(n_clean=0, n_noisy=2)
    r0 = qps.audit_array(a0, SR)
    r1 = qps.audit_array(a1, SR)
    r2 = qps.audit_array(a2, SR)
    assert r0["noisy"] == 0 and r0["pass"] is True
    assert r1["noisy"] == 1 and r1["pass"] is True, "noisy==1 PHẢI PASS (R96 v3.3) — nếu FAIL là regress về noisy==0"
    assert r2["noisy"] == 2 and r2["pass"] is False, "noisy==2 PHẢI FAIL — nếu PASS là ngưỡng bị nới quá"


def test_audit_array_threshold_source_is_noisy_le_1():
    """Source-guard: hằng số ngưỡng trong audit_array PHẢI là `noisy <= 1` (không phải ==0 / <=2)."""
    src = (REPO / "tools" / "qa_pause_silence.py").read_text(encoding="utf-8")
    m = re.search(r"def audit_array\(.*?return\s*\{.*?\}", src, re.DOTALL)
    assert m, "không tìm thấy audit_array()"
    assert re.search(r'"pass":\s*noisy\s*<=\s*1', m.group(0)), "ngưỡng pass phải là noisy<=1 (R96 v3.3)"


def test_audit_pause_delegates_same_verdict():
    """qa_post_render.audit_pause (delegate) cho verdict KHỚP audit_array trên cùng audio."""
    a1, _ = make_pause_audio(n_clean=1, n_noisy=1)
    a2, _ = make_pause_audio(n_clean=0, n_noisy=2)
    assert qpr.audit_pause(a1, SR)["pass"] is True
    assert qpr.audit_pause(a2, SR)["pass"] is False
    # map key downstream đúng cấu trúc
    keys = set(qpr.audit_pause(a1, SR))
    assert keys == {"total", "clean", "noisy", "pass"}


# ---------- G8-3: audit_spectrum ----------

def test_audit_spectrum_pass_and_fail_bands():
    # audit_spectrum tra numpy.bool_ -> dung truthy (khong dung `is True`)
    good = _const(500, 0.1)  # RMS = peak = -20 dB
    r = qpr.audit_spectrum(good, SR)
    assert r["pass_rms"] and r["pass_peak"] and r["pass"]
    # quá nhỏ: RMS < -25 -> fail rms
    quiet = _const(500, 0.01)  # -40 dB
    assert not qpr.audit_spectrum(quiet, SR)["pass_rms"]
    # clip: peak > -0.1 dB
    clip = _const(500, 0.999)  # ~ -0.009 dB
    rc = qpr.audit_spectrum(clip, SR)
    assert not rc["pass_peak"] and not rc["pass"]


# ---------- G8-3: audit_boundary (click detect, delta > 0.8, pass < 10 clicks) ----------

def test_audit_boundary_clean_pass_and_clicks_fail():
    clean = _const(500, 0.05)  # np.diff = 0 -> 0 click
    assert qpr.audit_boundary(clean, SR)["click_count"] == 0
    assert qpr.audit_boundary(clean, SR)["pass"] is True
    # tạo >=10 click: xen kẽ +0.9/-0.9 => mỗi bước |delta|=1.8 > 0.8
    clicky = np.zeros(200)
    clicky[1:41:2] = 0.9
    clicky[2:41:2] = -0.9
    rb = qpr.audit_boundary(clicky, SR)
    assert rb["click_count"] >= 10 and rb["pass"] is False


def test_audit_boundary_boundary_9_pass_10_fail():
    """Boundary chính xác: 9 click PASS, 10 click FAIL (mutation-proof cho `< 10`)."""
    def with_clicks(n):
        # [0,1,0,1,...] dài n+1 -> đúng n diff, mỗi |diff|=1.0 > 0.8 => đúng n click, không dư.
        a = np.zeros(n + 1)
        a[1::2] = 1.0
        return a
    assert qpr.audit_boundary(with_clicks(9), SR)["click_count"] == 9
    assert qpr.audit_boundary(with_clicks(9), SR)["pass"] is True
    assert qpr.audit_boundary(with_clicks(10), SR)["click_count"] == 10
    assert qpr.audit_boundary(with_clicks(10), SR)["pass"] is False


# ---------- G8-4: audit_head_onset (R88 -28dB/120ms, ratio slow<=0.25) ----------

def test_audit_head_onset_fast_pass_slow_fail():
    # onset nhanh: voice 0.1 (-20dB) ngay sau pause -> đạt -28dB trong 120ms -> 0 slow
    fast = np.concatenate([_voice(), _clean_pause(), _voice()])
    rf = qpr.audit_head_onset(fast, SR)
    assert rf["checked"] >= 1 and rf["slow_onsets"] == 0 and rf["pass"] is True
    # onset chậm: sau pause là ramp 300ms ở 0.01 (-40dB < -28dB) -> slow; ratio 1.0 > 0.25 -> FAIL
    slow = np.concatenate([_voice(), _clean_pause(), _const(300, 0.01), _voice()])
    rs = qpr.audit_head_onset(slow, SR)
    assert rs["checked"] >= 1 and rs["slow_onsets"] >= 1 and rs["pass"] is False


def test_audit_head_onset_default_params_are_r88():
    """Banner/hành vi = R88 (-28dB/120ms), KHÔNG phải R87b (-20dB/50ms). Guard chống đổi ngầm default."""
    import inspect
    sig = inspect.signature(qpr.audit_head_onset)
    assert sig.parameters["voice_thr_db"].default == -28
    assert sig.parameters["max_onset_ms"].default == 120
