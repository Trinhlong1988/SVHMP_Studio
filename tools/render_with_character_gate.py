"""G2 audit-fix (G2-6, 2026-07): CHARACTER_GATE tach rieng khoi file LOCKED
tools/svhmp_v13_render.py (TASK_G2_CHARACTER.md dong 32-33 cam sua file do —
"bat qua flag/wrapper"). Truoc day gate chen thang vao giua main() cua file
LOCKED (commit 8dbcecc) — vi pham rang buoc, audit doc lap (CMD_AUDIT_G2.md
G2-6) bat duoc.

Wrapper nay: chay CHARACTER_GATE truoc (WARN-default, --strict-characters ->
BLOCK exit 2, cung logic/single-source voi svhmp_preflight_qa.py qua
character_manager.episode_completeness + render_gate_lines), roi goi
svhmp_v13_render.py NHU SUBPROCESS (khong sua/import truc tiep noi bo file
LOCKED) voi --spec/--output truyen nguyen.

Dung thay svhmp_v13_render.py truc tiep khi can gate:
  uv run --no-sync python tools/render_with_character_gate.py \
    --spec <spec.json> --output <out.wav> [--strict-characters] [--char-threshold 0.5]
"""
import argparse
import os
import subprocess
import sys

_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _TOOLS_DIR)


def run_character_gate(spec_path, ep_num, strict, threshold):
    """Tra True neu render duoc phep tiep tuc (WARN hoac PASS), False neu BLOCK
    (strict + co char duoi nguong). KHONG bao gio raise — loi gate = WARN skip,
    giong hanh vi cu trong svhmp_v13_render.py (try/except bao boc)."""
    try:
        from character_manager import CharacterRegistry
        cg = CharacterRegistry().episode_completeness(ep_num, threshold)
        if not cg['total']:
            print(f"[gate] CHARACTER_GATE ep{ep_num}: no roster char mapped - skip", flush=True)
            return True
        mode = 'STRICT' if strict else 'WARN'
        print(f"[gate] CHARACTER_GATE:{mode} ep{ep_num}: {cg['total']} char, "
              f"{len(cg['below'])} below {threshold}", flush=True)
        warns, blocks = CharacterRegistry.render_gate_lines(cg, strict)
        for w in warns:
            print(f"[gate]   [WARN] {w}", flush=True)
        if blocks:
            for b in blocks:
                print(f"[gate]   [BLOCK] {b}", flush=True)
            print("[gate] !!! CHARACTER_GATE STRICT FAIL - RENDER BLOCKED", flush=True)
            return False
        return True
    except Exception as e:
        print(f"[gate] CHARACTER_GATE WARN: skipped ({type(e).__name__}: {e})", flush=True)
        return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--strict-characters', action='store_true',
                     help='CHARACTER_GATE: BLOCK render neu char trong ep duoi threshold')
    ap.add_argument('--char-threshold', type=float, default=0.5,
                     help='CHARACTER_GATE: nguong completeness (default 0.5)')
    args = ap.parse_args()

    import re
    ep_match = re.search(r'ep_(\d+)', args.output)
    ep_num = int(ep_match.group(1)) if ep_match else 1

    if not run_character_gate(args.spec, ep_num, args.strict_characters, args.char_threshold):
        sys.exit(2)

    render_script = os.path.join(_TOOLS_DIR, 'svhmp_v13_render.py')
    result = subprocess.run(
        [sys.executable, render_script, '--spec', args.spec, '--output', args.output])
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
