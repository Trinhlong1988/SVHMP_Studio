"""SVHMP — Pre-write enforcer (Mr.Long lệnh C).

BẮT BUỘC chạy TRƯỚC khi viết EP mới — enforce:
1. Word count target 2200-2900 (R39)
2. POV check guidelines (R47 - Khải Phong narrative = 'anh' NOT 'em')
3. Pronoun hierarchy (R48 - passenger dialogue đại từ theo age)
4. Section budget reminder

Usage: python tools/pre_write_enforcer.py --ep N
Output: ep_N_pre_write_brief.md
"""
import argparse
import sys
import yaml
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

PRE_WRITE_BRIEF_TEMPLATE = """# SVHMP PRE-WRITE BRIEF — EP{ep_num}

## BẮT BUỘC ĐỌC TRƯỚC VIẾT 1 CHỮ

### 1. WORD COUNT TARGET (R39 HARDLOCK)
- **Target: 2300-2500 từ** (15-17 phút TTS)
- **Hard floor: 2000 từ** (auto-block commit nếu dưới)
- **Hard ceiling: 2900 từ** (3200 nếu milestone)

### 2. SECTION BUDGET (PHẢI tuân thủ)
```
HOOK         → ~280 words  (bus arrives + passenger boards)
SETUP        → ~240 words  (Khải Phong observes)
INCIDENT     → ~240 words  (ghost glimpse + kim phút nhích 10)
REVEAL       → ~1050 words (passenger story, year breakdown)
PAYOFF       → ~270 words  (passenger disembarks + ghost manifest)
CLIFFHANGER  → ~320 words  (Khải Phong internal + driver foreshadow)
─────────────────────────────────────
TOTAL TARGET → ~2400 words
```

### 3. POV RULES (R47 + R48 HARDLOCK)
**Narrator 3rd person:**
- Khải Phong refer trong narrative = "**anh**" hoặc "**Khải Phong**"
- CẤM "em" cho Khải Phong ngoài quoted dialogue
- VÍ DỤ ĐÚNG: `"Khải Phong cố nhớ. Anh không nhớ rõ."`
- VÍ DỤ SAI: `"Khải Phong cố nhớ. Em không nhớ rõ."`

**Passenger dialogue đại từ:**
- Passenger tự xưng: "em" (younger than Khải Phong) hoặc "tôi" (older/same)
- Gọi Khải Phong: "anh"
- Gọi người đã mất (parent/spouse/sibling): theo age hierarchy
  - Chị Hạ Vy (lớn hơn Hải) = "chị"
  - Em gái = "em"
  - Bố/mẹ = "bố/mẹ"
- VÍ DỤ ĐÚNG: `Hải (22) nói: "Em yêu thầm CHỊ Hạ Vy"`
- VÍ DỤ SAI: `Hải nói: "Em yêu thầm Hạ Vy. Em biết EM có bạn trai"` (lẫn em)

### 4. ARC LOOKUP (auto-filled from bible/21)
{arc_info}

### 5. POST-WRITE GATE (PHẢI PASS trước commit)
```bash
python tools/post_render_gate.py --ep {ep_num}
# Phải PASS 11/11. Pre-commit hook R41 sẽ block nếu FAIL.
```

### 6. POV AUDIT (sau viết)
```bash
python tools/audit_pronoun_pov.py | grep EP{ep_num:02d}
# Phải 0 violations (không có "em" cho Khải Phong narrative)
```

---

## CHECKLIST TRƯỚC KHI VIẾT 1 CHỮ

- [ ] Đã đọc scaffold YAML này
- [ ] Đã hiểu word count 2300-2500 (không 1500!)
- [ ] Đã hiểu POV: Khải Phong narrative = "anh" KHÔNG "em"
- [ ] Đã hiểu passenger dialogue đại từ hierarchy
- [ ] Đã đọc bible/21 arc lookup
- [ ] Đã đọc prompts/ep_scaffold_template.md

**Vi phạm = R41 HARDLOCK block commit.**
"""

def get_arc_info(ep_num):
    """Quick arc lookup."""
    try:
        arc = yaml.safe_load((SVHMP / 'bible/21_series_arc_design.yaml').read_text(encoding='utf-8'))
        pillar = arc.get('pillar_interleave_ep01_50', {}).get(f'ep_{ep_num:02d}', '?')
        intensity_map = arc.get('intensity_level_per_ep', {})
        memory_arc = arc.get('quang_memory_arc', {})

        memory_text = '?'
        cliff_hint = '?'
        for k, v in memory_arc.items():
            if ep_num in v.get('eps', []):
                memory_text = v.get('fragment', '?')
                cliff_hint = v.get('cliffhanger_hint', '?')
                break

        milestone = ep_num in [10, 20, 30, 40, 50, 60, 70, 80, 90]
        callback = arc.get('callback_schedule_s1', {}).get(f'ep_{ep_num}', None)

        return f"""- Pillar (R33): **{pillar}**
- Memory M_X (R35): **{memory_text}**
- Cliffhanger hint: {cliff_hint}
- Callback (R36): {callback or 'none'}
- Milestone (R37): {'⭐ MILESTONE EP' if milestone else 'normal'}
- Intensity (R34): {'0.70 heightening' if 31 <= ep_num <= 60 else '0.55 warming'}"""
    except Exception as e:
        return f"  (Error loading bible/21: {e})"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int, required=True)
    args = parser.parse_args()

    arc_info = get_arc_info(args.ep)
    brief = PRE_WRITE_BRIEF_TEMPLATE.format(ep_num=args.ep, arc_info=arc_info)

    out = SVHMP / 'runtime' / f'ep_{args.ep:02d}_pre_write_brief.md'
    out.write_text(brief, encoding='utf-8')
    print(f"BRIEF SAVED: {out}")
    print()
    print(brief)
    return 0

if __name__ == '__main__':
    sys.exit(main())
