"""tools/dialogue_generator.py — D3 (TASK_G3_DIALOGUE.md), lop CORE orchestration MONG
(kien truc §CORE+OVERLAY): sinh 1 cau thoai ung vien cho passenger/driver DUNG voice
profile da khai, KHONG tu viet bang dialect/pronoun/age-slang moi (R211 - PHAN BIEN #11).

Luong bat buoc theo dung TASK (grep-able, giu nguyen thu tu):
  1. Tier1-completeness gate: dung dinh nghia MANDATORY_VOICE that cua
     dialog_voice_validator (region_dialect/hometown/pronoun_system) - thieu 1 trong 3 =
     raise Tier1IncompleteError. KHONG tu dinh nghia "tier1 day du" rieng (se la phantom
     coverage neu doi voi 4 field roster con thieu that o buoc 2).
  2. Field roster schema co nhung DU LIEU THAT con thieu (catchphrase/forbidden_words/
     dialogue_sample/speaking_speed - PHAN BIEN #7) -> SKIP dung field do, log vao
     reports/G3_MISSING_VOICE_FIELDS.md, KHONG bia placeholder.
  3. Goi dialog_voice_validator.validate_line()/validate_profile() (import + call THAT) tai
     diem sinh - FAIL thi loai bo/thu lai (toi da RETRY_LIMIT bien the mong), khong emit cau
     vi pham.
  4. Goi audit_dialogue_hierarchy.detect_pronoun_issues_in_quote() qua adapter mong (PHAN
     BIEN #2: ham nay nhan 1 quote string + passenger_name, KHONG can dung lai) - chan neu co
     issue severity HIGH.
  5. kind == 'recurring' (Bac tai / Nam) -> refuse cung mac dinh; CHI pass-through NGUYEN VAN
     Q1/Q2 (import hang so tu audit_driver_dialogue_context.py, KHONG go lai chuoi) khi
     scene_context khop dung trigger. Phu thuoc dialogue->world (bible/02) DA duoc D1B Phan A
     ky (dep__dialogue__world, world.reader da co 'dialogue') - buoc nay chay THAT, khong
     phai dry-run.
  6. Ghi output (helper write_episode_line) theo dung convention markdown-co-dau-ngoac-kep
     (extract_quotes() du quet duoc) - GHI VAO SANDBOX PATH RIENG (vd output/ep_g3_sample/),
     KHONG BAO GIO ghi de len 50 tap that da render/locked (an toan du lieu production).
  7. KHONG import module thuoc domain production/publisher (grep-able: 0 dong import nao
     nhac production/publisher trong file nay).

Cam tuyet doi: KHONG viet bang dialect/pronoun/age-slang moi trong file nay (R211).
"""
from __future__ import annotations
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import dialog_voice_validator as dvv  # noqa: E402
from audit_dialogue_hierarchy import detect_pronoun_issues_in_quote  # noqa: E402
from audit_driver_dialogue_context import (  # noqa: E402
    Q1_VARIANTS, Q2_VARIANTS, is_passenger_question)
from dialogue_manager import DialogueManager  # noqa: E402

SVHMP = Path(__file__).parent.parent
MISSING_VOICE_REPORT = SVHMP / 'reports' / 'G3_MISSING_VOICE_FIELDS.md'

# PHAN BIEN #7: 4 field tier_1_mandatory.voice (bible/37) schema co nhung du lieu THAT
# thieu tren CharacterProfile.voice (dataclass tools/character_manager.py khong co field
# forbidden_words/dialogue_sample/speaking_speed; catchphrase co field nhung du lieu roster
# hau nhu rong). Day la NO cua G2 - generator CHI duoc SKIP + log, KHONG tu dien.
OPTIONAL_VOICE_FIELDS = ('catchphrase', 'forbidden_words', 'dialogue_sample', 'speaking_speed')

RECURRING_KIND = 'recurring'
RETRY_LIMIT = 3


class Tier1IncompleteError(Exception):
    """Buoc 1: thieu 1 trong 3 field MANDATORY_VOICE that (dialog_voice_validator) -
    KHONG sinh cau rong/placeholder (R210)."""


class DialogueRefusedResult(dict):
    """Ket qua tra ve khi generator TU CHOI sinh (khac exception cung o buoc 1/5) - dung
    dict de D5 confusion-test doc status hang loat khong can try/except moi case."""


def _log_missing_fields(character_id: str, missing: list, report_path: Path = None):
    """report_path injectable (D3 test dung tmp_path) de KHONG lam ban report that bang
    id nhan vat gia lap tu mutation-test."""
    if not missing:
        return
    report_path = report_path or MISSING_VOICE_REPORT
    report_path.parent.mkdir(parents=True, exist_ok=True)
    line = f"- {character_id}: thieu {missing} (PHAN BIEN #7, no du lieu G2 - da SKIP, khong bia)\n"
    prev = report_path.read_text(encoding='utf-8') if report_path.exists() else (
        "# G3_MISSING_VOICE_FIELDS — log field tier_1_mandatory.voice con thieu du lieu that\n"
        "# (PHAN BIEN #7 TASK_G3_DIALOGUE.md) — generator SKIP, KHONG bia placeholder.\n\n")
    if line not in prev:
        report_path.write_text(prev + line, encoding='utf-8')


def _build_profile_dict(voice_profile: dict, age_range: str = '') -> tuple:
    """Rap dict cho dialog_voice_validator tu voice_profile (DialogueManager tra ve) +
    age_group (map truc tiep tu CharacterProfile.age_range da co san - KHONG bia gia tri
    moi, ELDERLY_AGE cua dvv da chua ca '51-65'/'66+' trung khop tu nhien).
    Tra ve (profile_dict, missing_optional_fields)."""
    missing = [f for f in OPTIONAL_VOICE_FIELDS if not voice_profile.get(f)]
    profile = {
        'region_dialect': voice_profile.get('region_dialect', ''),
        'hometown': voice_profile.get('hometown', ''),
        'pronoun_system': voice_profile.get('pronoun_system', ''),
        'particles': voice_profile.get('particles') or [],
        'forbidden_words': voice_profile.get('forbidden_words') or [],
        'age_group': age_range or '',
    }
    return profile, missing


def _candidate_variants(profile: dict, voice_profile: dict, scene_context: dict) -> list:
    """Sinh toi da RETRY_LIMIT bien the CAU DON GIAN tu CHINH du lieu nhan vat da khai
    (pronoun_system/particles/catchphrase neu co) + scene_context (beat/listener nhan tu
    NGOAI, khong tu bia - PHAN BIEN #9). KHONG dung bang tu vung/dialect moi - chi ghep
    chuoi tu field co san."""
    pronoun = (profile['pronoun_system'] or '').replace('/', ' ').split()
    pronoun = pronoun[0] if pronoun else ''
    particle = profile['particles'][0] if profile['particles'] else ''
    beat = (scene_context or {}).get('emotion_beat', '').strip()
    listener = (scene_context or {}).get('listener_call', '').strip()
    catchphrase = voice_profile.get('catchphrase') or ''

    variants = []
    if catchphrase:
        variants.append(catchphrase.strip())
    core = ' '.join(x for x in (pronoun.capitalize() if pronoun else '', listener, beat) if x).strip()
    if core:
        v = core if core.endswith(('.', '!', '?')) else core + '.'
        if particle and particle not in v:
            v = v.rstrip('.') + f' {particle}.'
        variants.append(v)
    # fallback toi gian nhat: chi pronoun + particle (van tu du lieu THAT cua nhan vat)
    if pronoun:
        fallback = pronoun.capitalize()
        if particle:
            fallback += f' {particle}'
        variants.append(fallback + '.')
    seen = set()
    out = []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out[:RETRY_LIMIT] or ['...']


def generate_line(character_id: str, scene_context: dict = None, manager: DialogueManager = None,
                   missing_report_path: Path = None) -> dict:
    """Entry point chinh. scene_context: {'emotion_beat':.., 'listener_call':.., 'ep_n':..,
    'driver_trigger_window': [str,...]} - TAT CA nhan tu ngoai, generator KHONG tu tinh
    ratio thoai/narration (PHAN BIEN #9, viec cua decision_engine/G6).
    missing_report_path: cho phep test/batch tro log sang noi khac (mac dinh
    reports/G3_MISSING_VOICE_FIELDS.md that cua repo)."""
    scene_context = scene_context or {}
    manager = manager or DialogueManager()
    c = manager.registry.get(character_id)
    if c is None:
        return DialogueRefusedResult(status='ERROR', reason='CHARACTER_NOT_FOUND',
                                      character_id=character_id)

    if c.kind == RECURRING_KIND:
        return _generate_recurring(c, scene_context)

    ctx = manager.get_dialogue_context(character_id, scene_context.get('ep_n'))
    voice_profile = ctx['voice_profile'] or {}

    # ---- buoc 1: Tier1-completeness gate (dung dinh nghia THAT cua dvv.MANDATORY_VOICE) ----
    profile, missing_optional = _build_profile_dict(voice_profile, c.age_range)
    mandatory_issues = [i for i in dvv.validate_profile(profile) if i['code'] == 'MISSING_MANDATORY']
    if mandatory_issues:
        raise Tier1IncompleteError(
            f"{character_id} thieu MANDATORY_VOICE: {[i['field'] for i in mandatory_issues]}")

    # ---- buoc 2: field optional thieu du lieu that -> SKIP + log (PHAN BIEN #7) ----
    _log_missing_fields(character_id, missing_optional, missing_report_path)

    # ---- buoc 3 + retry: goi validate_line/validate_profile THAT, loai neu vi pham ----
    profile_issues = dvv.validate_profile(profile)
    non_mandatory_profile_issues = [i for i in profile_issues if i['code'] != 'MISSING_MANDATORY']
    if non_mandatory_profile_issues:
        return DialogueRefusedResult(status='REFUSED', reason='PROFILE_INVALID',
                                      character_id=character_id, issues=non_mandatory_profile_issues,
                                      missing_optional_fields=missing_optional)

    candidates = _candidate_variants(profile, voice_profile, scene_context)
    last_issues = []
    for cand in candidates:
        line_issues = dvv.validate_line(profile, cand)
        if line_issues:
            last_issues = line_issues
            continue
        # ---- buoc 4: adapter pronoun-ambiguity (PHAN BIEN #2 - goi truc tiep, KHONG copy VN_NAMES) ----
        pronoun_issues = detect_pronoun_issues_in_quote(cand, passenger_name=c.char_name)
        high_pronoun = [i for i in pronoun_issues if i.get('severity') == 'HIGH']
        if high_pronoun:
            last_issues = high_pronoun
            continue
        return DialogueRefusedResult(status='OK', character_id=character_id, line=cand,
                                      issues=[], missing_optional_fields=missing_optional,
                                      attempts=candidates.index(cand) + 1)
    return DialogueRefusedResult(status='REFUSED', reason='VALIDATOR_REJECTED',
                                  character_id=character_id, issues=last_issues,
                                  missing_optional_fields=missing_optional,
                                  attempts=len(candidates))


def _generate_recurring(c, scene_context: dict) -> dict:
    """Buoc 5: Bac tai/Nam - refuse cung mac dinh, CHI pass-through nguyen van Q1/Q2 khi
    trigger khop (subject to D1B Phan A - DA KY, chay THAT khong con dry-run)."""
    window = scene_context.get('driver_trigger_window') or []
    wants = (scene_context.get('driver_target') or '').upper()
    if wants == 'Q1':
        return DialogueRefusedResult(status='RECURRING_PASSTHROUGH', character_id=c.id,
                                      line=Q1_VARIANTS[0], rule='R174_Q1_no_trigger_required')
    if wants == 'Q2':
        has_trigger = any(is_passenger_question(w) for w in window[-3:])
        if has_trigger:
            return DialogueRefusedResult(status='RECURRING_PASSTHROUGH', character_id=c.id,
                                          line=Q2_VARIANTS[0], rule='R174_Q2_trigger_confirmed')
        return DialogueRefusedResult(status='RECURRING_REFUSED', character_id=c.id,
                                      reason='Q2_NO_TRIGGER_IN_3_PRECEDING')
    return DialogueRefusedResult(status='RECURRING_REFUSED', character_id=c.id,
                                  reason='RECURRING_CHARACTER_DEFAULT_REFUSE')


def write_episode_line(root: Path, ep_n, line: str, header_kv: dict = None) -> Path:
    """Buoc 6: ghi 1 dong markdown dung convention output/ep_*/episode.md (co dau ngoac
    kep de extract_quotes() quet duoc) - GOI Y dung cho smoke-test/sandbox (tmp_path hoac
    output/ep_g3_sample/), KHONG BAO GIO trỏ vao 50 tap that da locked.

    ep_n chap nhan ca so nguyen (zero-pad nhu 50 tap that, vd 1 -> 'ep_01') LAN chuoi tuy y
    khong phai so (dung nguyen van, vd 'g3_sample' -> 'ep_g3_sample') - phuc vu G3-7 (dong
    kiem duyet 5/7): can 1 thu muc sandbox TEN CHU (khong phai so) de KHONG BAO GIO trung
    voi bat ky so tap that/tuong lai nao (hien 50 tap, roadmap toi 90) du co ep_n nao duoc dung.

    GUARD (10/7, per Mr.Long authorization - TASK_AUDIT_CRITICAL_G3_G5.md Bug #1, CMD_AUDIT
    phat hien docstring cam ket "KHONG BAO GIO tro vao 50 tap that" nhung code khong enforce):
    raise ValueError neu root la thu muc production that (SVHMP/'output') VA ep_n la so
    (int/chuoi toan chu so) - to hop nay se ghi de tap da locked. 2 to hop hop le cu (tmp_path
    bat ky ep_n; root production + ep_n chuoi non-numeric) KHONG doi hanh vi."""
    header_kv = header_kv or {'g3_sandbox': 'true'}
    try:
        ep_label = f'{int(ep_n):02d}'
        ep_n_is_numeric = True
    except (TypeError, ValueError):
        ep_label = str(ep_n)
        ep_n_is_numeric = False
    if ep_n_is_numeric and Path(root).resolve() == (SVHMP / 'output').resolve():
        raise ValueError(
            "write_episode_line() KHONG duoc goi voi ep_n so + root production "
            f"(root={root}, ep_n={ep_n!r}) - se ghi de tap that da locked. Dung ep_n dang "
            "chuoi non-numeric cho sandbox (vd 'g3_sample'), hoac golden_lock neu that su "
            "can ghi tap that (xem tests/_golden_lock.py)."
        )
    ep_dir = Path(root) / f'ep_{ep_label}'
    ep_dir.mkdir(parents=True, exist_ok=True)
    header = '\n'.join(f'{k}: {v}' for k, v in header_kv.items())
    text = f"```\n{header}\n```\n\"{line}\"\n"
    out = ep_dir / 'episode.md'
    out.write_text(text, encoding='utf-8')
    return out


if __name__ == '__main__':
    import json
    dm = DialogueManager()
    demo_id = next((c.id for c in dm.registry.all('passenger') if c.assigned_ep), None)
    if demo_id:
        result = generate_line(demo_id, {'emotion_beat': 'nhớ nhà', 'listener_call': 'Mẹ ơi'}, dm)
        print(json.dumps(dict(result), ensure_ascii=False, indent=2))
