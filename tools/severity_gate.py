"""SVHMP — SEVERITY GATE (PACK2 06, Boss 2/7).
Luat: CHI 'Critical' chan promotion (BLOCK). Major/Minor/Info = report, khong tu chan
(chong spam chan). Findings: list[dict{severity}] hoac list[str].
"""
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SEVERITIES = ['Critical', 'Major', 'Minor', 'Info']
BLOCKING = {'Critical'}


def _sev(f):
    return (f.get('severity') if isinstance(f, dict) else f)


def gate(findings):
    """-> (verdict, exit_code). Bat ky Critical -> ('BLOCK', 1). Tach ra de test R214."""
    bad = [f for f in findings if _sev(f) not in SEVERITIES]
    if bad:
        raise ValueError(f"severity khong hop le: {[_sev(f) for f in bad]}")
    crit = [f for f in findings if _sev(f) in BLOCKING]
    return ('BLOCK', 1) if crit else ('PASS', 0)


if __name__ == '__main__':
    # demo: doc severity tu argv, in verdict
    verdict, ec = gate([{'severity': s} for s in sys.argv[1:]])
    print(f"severity_gate({sys.argv[1:]}) -> {verdict} (exit {ec})")
    sys.exit(ec)
