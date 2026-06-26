"""
SVHMP Bible Consumer Mapping Audit — F3.2 round 14
Fix B2 (bible consumer mapping not verified).

Parse mỗi prompt file, find which bibles it references.
Cross-check với bible header "# Loaded by: ..." declaration.
Report mismatches.
"""
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP_ROOT = Path(__file__).parent.parent
PROMPTS = SVHMP_ROOT / 'prompts'
BIBLES = SVHMP_ROOT / 'bible'


def extract_bible_refs_from_prompt(prompt_path: Path) -> set:
    """Find all bible/NN_*.yaml references in a prompt file."""
    content = prompt_path.read_text(encoding='utf-8')
    # Match bible/NN_filename.yaml
    refs = set(re.findall(r'bible[\\/](\d{2})_([\w_]+)\.yaml', content))
    # Convert to bible_NN format
    return {f"{num}_{name}" for num, name in refs}


def extract_loaded_by_from_bible(bible_path: Path) -> set:
    """Parse '# Loaded by: ...' header line from bible YAML comment."""
    content = bible_path.read_text(encoding='utf-8')
    # Match "# Loaded by: X / Y / Z" line
    m = re.search(r'^#\s*Loaded by:\s*(.+?)$', content, re.MULTILINE)
    if not m:
        return set()
    consumers_str = m.group(1).strip()
    # Parse: "Generator (...) / QA Lock (...) / TTS Director (...)"
    consumers = set()
    for part in re.split(r'[/+]', consumers_str):
        part = part.strip()
        # Extract name before "(": "Generator (write..." → "generator"
        name_m = re.match(r'^([\w_-]+)', part.lower().replace('lock', '').replace('director', '').strip())
        if name_m:
            consumers.add(name_m.group(1).rstrip(' _-'))
    return consumers


def normalize_prompt_name(prompt_file: str) -> str:
    """director.md → director, qa.md → qa"""
    return prompt_file.replace('.md', '').lower()


def main():
    print("=" * 75)
    print("SVHMP BIBLE CONSUMER MAPPING AUDIT (F3.2 round 14, fix B2)")
    print("=" * 75)

    # Map: prompt → bibles referenced
    prompt_refs = {}
    for p in sorted(PROMPTS.glob('*.md')):
        prompt_name = normalize_prompt_name(p.name)
        refs = extract_bible_refs_from_prompt(p)
        prompt_refs[prompt_name] = refs

    # Map: bible → declared consumers (from "Loaded by:" header)
    bible_declared = {}
    for b in sorted(BIBLES.glob('*.yaml')):
        consumers = extract_loaded_by_from_bible(b)
        bible_name = b.stem  # "00_constitution"
        bible_declared[bible_name] = consumers

    # Report 1: Per-prompt bible references
    print("\n## PROMPTS — bibles each prompt references")
    print("-" * 75)
    for prompt_name, refs in prompt_refs.items():
        sorted_refs = sorted(refs)
        print(f"  {prompt_name:20s} ({len(refs):2d} refs): {sorted_refs[:6]}{'...' if len(refs) > 6 else ''}")

    # Report 2: Per-bible declared consumers
    print("\n## BIBLES — declared consumers (from '# Loaded by:' header)")
    print("-" * 75)
    no_header_count = 0
    for bible_name, consumers in bible_declared.items():
        if not consumers:
            print(f"  {bible_name:50s} (NO 'Loaded by:' header — UNDECLARED)")
            no_header_count += 1
        else:
            print(f"  {bible_name:50s} {sorted(consumers)}")

    # Report 3: Mismatches — bible declared X but X doesn't reference it
    print("\n## MISMATCHES — bible declared by X but X doesn't reference bible")
    print("-" * 75)
    mismatches = 0
    for bible_name, declared in bible_declared.items():
        bible_num_name = bible_name  # "00_constitution"
        for consumer_prompt in declared:
            # Try match consumer name to prompt files
            prompt_refs_for_consumer = None
            for pname in prompt_refs:
                if consumer_prompt in pname or pname in consumer_prompt:
                    prompt_refs_for_consumer = prompt_refs[pname]
                    break
            if prompt_refs_for_consumer is None:
                continue  # consumer name không match prompt
            if bible_num_name not in prompt_refs_for_consumer:
                print(f"  {bible_name} declares consumer '{consumer_prompt}' but {consumer_prompt}.md không ref bible này")
                mismatches += 1

    if mismatches == 0:
        print("  (no mismatches)")

    # Report 4: Bibles referenced by NO prompt (potentially unused)
    print("\n## UNUSED BIBLES — không prompt nào reference")
    print("-" * 75)
    all_referenced = set()
    for refs in prompt_refs.values():
        all_referenced.update(refs)
    unused = []
    for b in BIBLES.glob('*.yaml'):
        if b.stem not in all_referenced:
            unused.append(b.stem)
    if unused:
        for u in sorted(unused):
            print(f"  {u} — KHÔNG prompt nào ref (verify intentional)")
    else:
        print("  (all bibles referenced by at least 1 prompt)")

    # Summary
    print("\n" + "=" * 75)
    print(f"SUMMARY:")
    print(f"  Prompts audited: {len(prompt_refs)}")
    print(f"  Bibles audited: {len(bible_declared)}")
    print(f"  Bibles without 'Loaded by:' header: {no_header_count}")
    print(f"  Mismatches (declared but not referenced): {mismatches}")
    print(f"  Unused bibles: {len(unused)}")
    print("=" * 75)
    sys.exit(0 if mismatches == 0 else 1)


if __name__ == '__main__':
    main()
