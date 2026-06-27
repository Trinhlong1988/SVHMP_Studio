# SVHMP PRE-WRITE BRIEF — EP51

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
- Pillar (R33): **?**
- Memory M_X (R35): **Khải Phong nhớ mình đã không giữ lời**
- Cliffhanger hint: Khải Phong đã không đón Hà đêm đó
- Callback (R36): none
- Milestone (R37): normal
- Intensity (R34): 0.70 heightening

### 5. POST-WRITE GATE (PHẢI PASS trước commit)
```bash
python tools/post_render_gate.py --ep 51
# Phải PASS 11/11. Pre-commit hook R41 sẽ block nếu FAIL.
```

### 6. POV AUDIT (sau viết)
```bash
python tools/audit_pronoun_pov.py | grep EP51
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
