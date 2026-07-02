"""SVHMP — Domain Manifest generator (Boss 2/7): moi domain 1 file source-of-truth.
Gop registry.domains + file_index -> governance/manifests/<domain>_manifest.yaml.
"""
import sys
from pathlib import Path
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml

SVHMP = Path(__file__).parent.parent


def main():
    reg = yaml.safe_load((SVHMP / 'governance' / 'architecture_registry.yaml').read_text(encoding='utf-8'))
    idx = yaml.safe_load((SVHMP / 'governance' / 'file_index.yaml').read_text(encoding='utf-8'))
    own = reg.get('ownership_matrix', {})

    dom_files = defaultdict(list)
    dom_tier = {}
    for f, i in idx['files'].items():
        dom_files[i['domain']].append(f)
        dom_tier[i['domain']] = i.get('tier')

    outdir = SVHMP / 'governance' / 'manifests'
    outdir.mkdir(parents=True, exist_ok=True)
    made = []
    for dom, files in sorted(dom_files.items()):
        regdom = (reg.get('domains') or {}).get(dom, {})
        owner = next((o for o, paths in own.items()
                      if any(dom in str(p) or f'{dom}' == str(p) for p in paths)), 'UNASSIGNED')
        manifest = {
            'domain': dom,
            'tier': dom_tier.get(dom),
            'owner': owner,
            'promotion_status': regdom.get('promotion_status', 'candidate'),
            'source_of_truth': regdom.get('source_of_truth', []),
            'data_contract': regdom.get('data_contract'),
            'files': sorted(files),
            'file_count': len(files),
        }
        (outdir / f'{dom}_manifest.yaml').write_text(
            yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding='utf-8')
        made.append((dom, len(files)))

    print("=== DOMAIN MANIFESTS ===")
    for d, n in made:
        print(f"  {d:26}: {n} file  -> governance/manifests/{d}_manifest.yaml")
    print(f"  Tong: {len(made)} domain manifest")


if __name__ == '__main__':
    main()
