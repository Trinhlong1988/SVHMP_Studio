"""SVHMP — Character Manager (Boss 1/7): quan ly nhan vat theo CLASS, dinh danh id +
day du truong, LOGIC, khong suy luan.

Nguyen tac tich hop (KHONG lam lai cai da co):
- Sinh/quan ly TEN: da co `tools/build_name_pool.py` + `tools/gen_100_passenger.py` + bible/23.
  -> Manager nay CHI CONSUME roster da sinh, KHONG generate ten. Chi VALIDATE theo bible/23 + ENRICH truong.
- Skeleton roster: `runtime/passenger_roster_100.yaml` (core fields).
- Recurring: `bible/03_character_bible.yaml` (CHAR_DRIVER + CHAR_NAM — da dinh danh day du).
- Truong MO RONG (Boss 1/7): physical/attire/personality/voice/background/death/relationships.
  Voice+quehuong+noio CUC KY QUAN TRONG -> chi phoi SINH DIALOG (giong dia phuong, xung ho, tu vung).

CLI: python tools/character_manager.py --report | --completeness | --char PAS_0013
"""
from __future__ import annotations
import argparse
import sys
from dataclasses import dataclass, field, asdict, fields as dc_fields
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(__file__).parent.parent


# ── VOICE / DIALOGUE PROFILE (Boss nhan manh: chi phoi SINH DIALOG) ──
@dataclass
class VoiceProfile:
    region_dialect: str = ""        # bac | trung | nam (+sub: nam_saigon, trung_hue, bac_hanoi...)
    hometown: str = ""              # QUE HUONG -> goc giong dia phuong
    residence: str = ""             # NOI O hien tai -> co the pha giong / tu vung
    pronoun_system: str = ""        # xung ho: toi|tui|tao|minh|con|em|qua|... (theo vung+tuoi+vai)
    particles: list = field(default_factory=list)   # nhe|nghen|he|ha|a|hen|... (tieu tu cuoi cau theo vung)
    register: str = ""              # trang_trong | dan_da | suong_sa
    lexicon_markers: list = field(default_factory=list)  # tu dia phuong dac trung (ma/me, chen/bat, vo/vao)
    speech_tics: list = field(default_factory=list)      # tat noi / lap tu / ngat quang
    catchphrase: str = ""
    education_level: str = ""       # anh huong do phuc tap tu vung + cach dat cau
    pace: str = ""                  # nhanh | cham | deu
    voice_sample_ref: str = ""      # tro toi mau giong TTS (neu voice dialogue rieng)


# ── CHARACTER PROFILE (id + toan bo truong) ──
@dataclass
class CharacterProfile:
    # --- CORE: KHOP field roster hien co (khong doi ten) ---
    id: str
    char_name: str = ""
    gender: str = ""                # nu | nam
    age_range: str = ""             # 18-25 | 26-35 | 36-50 | 51-65 | 66+
    display_name: str = ""
    pillar: str = ""                # bible/11 regret pillar
    regret_sub_archetype: str = ""
    regret_label: str = ""
    signature_object: str = ""      # bible/12
    signature_setting: str = ""     # bible/13
    assigned_ep: object = None
    novelty_hash: object = None
    narrative_hook: str = "TBD by Generator"
    status: str = "framework_lock"  # trang thai FRAMEWORK (khong phai song/chet)
    kind: str = "passenger"         # passenger | recurring

    # --- EXTENDED (Boss 1/7): dinh danh day du ---
    dob: str = ""                   # ngay/thang/nam sinh
    age_exact: object = None        # tuoi chinh xac (khi ep chot)
    life_status: str = ""           # song | da_mat(hon) — trang thai SONG/CHET (khac 'status')
    physical: dict = field(default_factory=dict)      # build, skin(mau da), hair{length,color,style}, face{dimple(num dong tien),eyebrows(long may),marks(diem dac biet)}, beauty(xinh/xau), description
    attire: dict = field(default_factory=dict)        # clothing(trang phuc), shoes(giay dep), hat(mu), jewelry(trang suc)
    personality: dict = field(default_factory=dict)   # traits(tinh cach), so_truong(strengths), so_doan(weaknesses), hobbies(so thich), fear, temperament
    voice: VoiceProfile = field(default_factory=VoiceProfile)
    background: dict = field(default_factory=dict)    # occupation(nghe), marital_status(hon nhan), school(truong), hometown(que), residence(noi o), family
    death: dict = field(default_factory=dict)         # type(cai chet), pain(noi dau), time_of_loss
    relationships: list = field(default_factory=list) # [{who, relation, status}] — ho hang/ban be/dong nghiep

    # --- 6 MODULE mo rong (phan bien.txt) — tai dung du an dai hoi ---
    lifecycle: dict = field(default_factory=dict)     # created, first_ep, last_ep, locked, dead, reincarnated, reusable
    state_by_episode: dict = field(default_factory=dict)  # STATE dong theo tap (vui/so/bi thuong/say...) — khac identity
    story_memory: dict = field(default_factory=dict)  # su kien: ai biet / ai chua / khan gia biet / nguoi ke chua lo
    suspense_profile: dict = field(default_factory=dict)  # muc bi an/am anh/hoi tiec/cam dong/so hai (SVHMP)

    # nhom truong MO RONG dung do completeness
    EXT_GROUPS = ('physical', 'attire', 'personality', 'voice', 'background', 'death',
                  'relationships', 'dob', 'life_status', 'lifecycle', 'state_by_episode',
                  'story_memory', 'suspense_profile')

    def completeness(self) -> float:
        filled = 0
        for g in self.EXT_GROUPS:
            v = getattr(self, g)
            if g == 'voice':
                v = {k: x for k, x in asdict(self.voice).items() if x}
            if v:
                filled += 1
        return round(filled / len(self.EXT_GROUPS), 2)

    def missing_ext(self) -> list:
        out = []
        for g in self.EXT_GROUPS:
            v = getattr(self, g)
            if g == 'voice':
                v = {k: x for k, x in asdict(self.voice).items() if x}
            if not v:
                out.append(g)
        return out


class CharacterRegistry:
    """Quan ly toan bo nhan vat: load roster + recurring, get/filter/distribution/validate/enrich.
    KHONG sinh ten (da co gen_100_passenger + bible/23) — chi consume + validate + bo sung."""

    def __init__(self, roster_path: Path = None, char_bible_path: Path = None):
        import yaml
        self._yaml = yaml
        self.roster_path = Path(roster_path or SVHMP / 'runtime' / 'passenger_roster_100.yaml')
        self.char_bible_path = Path(char_bible_path or SVHMP / 'bible' / '03_character_bible.yaml')
        self.chars: dict[str, CharacterProfile] = {}
        self._load()

    # ---------- LOAD ----------
    def _load(self):
        core_names = {f.name for f in dc_fields(CharacterProfile)
                      if f.name not in ('voice',) and not f.name.isupper()}
        # passengers
        if self.roster_path.exists():
            data = self._yaml.safe_load(self.roster_path.read_text(encoding='utf-8')) or {}
            for p in data.get('passengers', []):
                self.chars[p['id']] = self._from_dict(p, core_names, kind='passenger')
        # recurring (bible/03) — da dinh danh day du
        if self.char_bible_path.exists():
            cb = self._yaml.safe_load(self.char_bible_path.read_text(encoding='utf-8')) or {}
            for cid, cd in (cb.get('characters') or {}).items():
                self.chars[cid] = self._recurring_from_dict(cid, cd)

    def _from_dict(self, p: dict, core_names: set, kind: str) -> CharacterProfile:
        kw = {k: v for k, v in p.items() if k in core_names}
        kw['id'] = p['id']; kw['kind'] = kind
        prof = CharacterProfile(**kw)
        v = p.get('voice')
        if isinstance(v, dict):
            prof.voice = VoiceProfile(**{k: x for k, x in v.items()
                                         if k in {f.name for f in dc_fields(VoiceProfile)}})
        for g in ('physical', 'attire', 'personality', 'background', 'death',
                  'lifecycle', 'state_by_episode', 'story_memory', 'suspense_profile'):
            if isinstance(p.get(g), dict):
                setattr(prof, g, p[g])
        if isinstance(p.get('relationships'), list):
            prof.relationships = p['relationships']
        return prof

    def _recurring_from_dict(self, cid: str, cd: dict) -> CharacterProfile:
        """Map bible/03 recurring (visual/personality/relationship_map) vao CharacterProfile."""
        vis = cd.get('visual', {}) or {}
        prof = CharacterProfile(
            id=cid, char_name=cd.get('display_name', cid), kind='recurring',
            display_name=cd.get('display_name', cid),
            age_range=str(vis.get('age') or vis.get('age_appearance', '')),
            narrative_hook=cd.get('role', ''), status='recurring_lock', life_status='',
        )
        prof.physical = {k: vis[k] for k in ('build', 'face', 'skin', 'hair') if k in vis}
        prof.attire = {k: vis[k] for k in ('clothing', 'hands') if k in vis}
        if cd.get('personality'):
            prof.personality = dict(cd['personality'])
        prof.voice = VoiceProfile(voice_sample_ref=vis.get('voice', ''))
        rmap = cd.get('relationship_map') or cd.get('relationship_to_73') or []
        prof.relationships = [{'raw': r} for r in rmap] if isinstance(rmap, list) else []
        return prof

    # ---------- QUERY ----------
    def get(self, cid: str) -> CharacterProfile | None:
        return self.chars.get(cid)

    def all(self, kind: str = None) -> list:
        return [c for c in self.chars.values() if kind is None or c.kind == kind]

    def by_name(self, name: str) -> list:
        return [c for c in self.chars.values() if c.char_name == name]

    def by_ep(self, ep: int) -> list:
        return [c for c in self.chars.values() if c.assigned_ep == ep]

    def filter(self, **kw) -> list:
        return [c for c in self.chars.values()
                if all(getattr(c, k, None) == v for k, v in kw.items())]

    # ---------- DISTRIBUTION (kiem soat phan bo xuyen du an) ----------
    def distribution(self) -> dict:
        pas = self.all('passenger')
        def cnt(attr):
            return dict(Counter(getattr(c, attr) or '?' for c in pas))
        return {
            'total_passenger': len(pas),
            'total_recurring': len(self.all('recurring')),
            'by_pillar': cnt('pillar'),
            'by_gender': cnt('gender'),
            'by_age_range': cnt('age_range'),
            'by_region_dialect': dict(Counter((c.voice.region_dialect or '?') for c in pas)),
            'by_life_status': cnt('life_status'),
            'elderly_66plus': sum(1 for c in pas if c.age_range == '66+'),
            'youth_18_25': sum(1 for c in pas if c.age_range == '18-25'),
        }

    # ---------- VALIDATE NAMING (reuse bible/23 rules — QA enforce, KHONG sinh) ----------
    def validate_names(self) -> list:
        issues = []
        seen_words = {}
        for c in self.all('passenger'):
            words = c.char_name.split()
            if len(words) < 2:
                issues.append(f"{c.id} '{c.char_name}': rule_01 <2 am tiet")
            if 'Nam' in words:
                issues.append(f"{c.id} '{c.char_name}': rule_04 trung word recurring 'Nam'")
            for w in words:
                if w in seen_words and seen_words[w] != c.id:
                    issues.append(f"{c.id} '{c.char_name}': rule_02 word '{w}' trung {seen_words[w]}")
                seen_words[w] = c.id
        return issues

    # ---------- ENRICH (bo sung truong mo rong, co validate) ----------
    def enrich(self, cid: str, **fields):
        c = self.chars[cid]
        for k, v in fields.items():
            if k == 'voice' and isinstance(v, dict):
                for vk, vv in v.items():
                    if vk in {f.name for f in dc_fields(VoiceProfile)}:
                        setattr(c.voice, vk, vv)
            elif hasattr(c, k):
                setattr(c, k, v)
            else:
                raise KeyError(f"CharacterProfile khong co truong '{k}'")
        return c

    def completeness_report(self) -> dict:
        pas = self.all('passenger')
        if not pas:
            return {'avg': 0.0, 'fully_defined': 0, 'skeleton_only': 0}
        comps = [c.completeness() for c in pas]
        miss = Counter()
        for c in pas:
            for m in c.missing_ext():
                miss[m] += 1
        return {
            'avg_completeness': round(sum(comps) / len(comps), 2),
            'fully_defined': sum(1 for x in comps if x >= 0.99),
            'skeleton_only': sum(1 for x in comps if x == 0.0),
            'most_missing': dict(miss.most_common()),
        }

    @staticmethod
    def render_gate_lines(cg: dict, strict: bool) -> tuple:
        """Format ket qua episode_completeness() cho render gate (single-source,
        preflight + test deu goi). Return (warn_lines, block_issues):
        strict=True -> char duoi nguong thanh block_issues (CHAN render);
        strict=False -> chi warn_lines (WARN, KHONG chan)."""
        warns, blocks = [], []
        for c in cg.get('below', []):
            msg = (f'CHAR {c["id"]} "{c["name"]}" '
                   f'completeness={c["completeness"]} missing={c["missing"][:5]}')
            (blocks if strict else warns).append(msg)
        return warns, blocks

    def episode_completeness(self, ep: int, threshold: float = 0.5) -> dict:
        """G2 render-gate helper: Character DoD-completeness cho 1 episode.
        Tra ve char trong ep + danh sach char DUOI nguong (skeleton). Preflight
        (svhmp_preflight_qa) dung de WARN/BLOCK render. Single-source: preflight
        va test deu goi ham nay, KHONG nhan doi logic."""
        chars = self.by_ep(ep)
        below = [
            {'id': c.id, 'name': c.char_name,
             'completeness': c.completeness(), 'missing': c.missing_ext()}
            for c in chars if c.completeness() < threshold
        ]
        return {'ep': ep, 'total': len(chars), 'threshold': threshold, 'below': below}

    def save_enriched(self, out_path: Path):
        """Ghi roster DA ENRICH ra file rieng (khong de len skeleton goc)."""
        pas = []
        for c in self.all('passenger'):
            d = asdict(c)
            d.pop('kind', None)
            d['voice'] = {k: v for k, v in asdict(c.voice).items() if v}
            pas.append(d)
        Path(out_path).write_text(
            self._yaml.safe_dump({'schema_version': 2, 'source': str(self.roster_path.name),
                                  'passengers': pas}, allow_unicode=True, sort_keys=False),
            encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description='SVHMP Character Manager')
    ap.add_argument('--report', action='store_true', help='distribution + naming validate')
    ap.add_argument('--completeness', action='store_true', help='do day du profile')
    ap.add_argument('--char', type=str, help='in 1 nhan vat theo id')
    args = ap.parse_args()

    reg = CharacterRegistry()
    print(f"Loaded: {len(reg.all('passenger'))} passenger + {len(reg.all('recurring'))} recurring")

    if args.char:
        c = reg.get(args.char)
        if not c:
            print(f"Khong tim thay {args.char}"); sys.exit(1)
        import json
        print(json.dumps(asdict(c), ensure_ascii=False, indent=2, default=str))
        print(f"completeness={c.completeness()}  missing={c.missing_ext()}")
        return

    if args.report or not (args.completeness):
        d = reg.distribution()
        print("\n=== DISTRIBUTION (kiem soat phan bo) ===")
        for k, v in d.items():
            print(f"  {k}: {v}")
        ni = reg.validate_names()
        print(f"\n=== NAMING (bible/23 reuse): {len(ni)} issue ===")
        for i in ni[:10]:
            print(f"  - {i}")

    if args.completeness or args.report:
        cr = reg.completeness_report()
        print("\n=== COMPLETENESS (day du profile mo rong) ===")
        for k, v in cr.items():
            print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
