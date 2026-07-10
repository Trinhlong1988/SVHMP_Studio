"""SVHMP — G4 D1: TIMELINE CHECK (TASK_G4_WORLD, đóng nợ R84_temporal_anchor_for_events).

Đọc mốc thời gian mỗi tập -> đối chiếu xuyên tập + hiểu lịch âm cơ bản (rằm
tháng 7, Tết) để đối chiếu không khí/hành vi có khớp mùa không.

RECONCILE (RÀNG BUỘC TASK — KHÔNG nhân đôi tool):
- Tái sử dụng tools/event_ledger_miner.py cho phần trích temporal_mentions +
  F2 conflict-window-hẹp (KHÔNG viết lại logic mine).
- KHÔNG gọi tools/qa_fact_check.py: đã kiểm chứng hàm check_facts() của tool đó
  HARDCODE hoàn toàn cho EP01 (không đọc tham số facts, không tổng quát hoá cho
  tập khác) — gọi nó cho tập khác sẽ luôn trả kết quả rác. Ghi rõ finding này
  thay vì "gọi cho có" (R9 evidence-first — không giả vờ reconcile khi thực tế
  không dùng được).
- Lịch âm: KHÔNG tìm thấy bảng chuyển đổi âm-dương lịch nào trong Cultural KB
  đã verify trong repo (governance/evidence_schema_cultural_kb.yaml + proposals/
  cultural_kb_evidence_sample.yaml — chỉ có phong tục/tín ngưỡng + căn cứ pháp
  lý, KHÔNG có bảng lịch). Rằm tháng 7 (Vu Lan) và Tết là tri thức phổ thông
  định danh (15 tháng 7 âm lịch / mùng 1 tháng 1 âm lịch) — KHÔNG cần "verified"
  kiểu SVAF evidence schema (khác hẳn tuyên bố tôn giáo/pháp lý nhạy cảm ở BP9).
  Check ở đây CHỈ khớp TỪ KHÓA văn bản ("rằm tháng 7"/"Tết"/"Vu Lan") với mô tả
  mùa/thời tiết literal trong CÙNG đoạn — không suy luận ngày dương lịch cụ thể.

Exit 0 = PASS khi 0 M1 xuyên-tập — CHỈ M1 chặn exit code. M4 lệch mùa + F2 nội bộ
CHỈ in WARN/ứng viên, KHÔNG ảnh hưởng exit vì chưa đủ tin cậy để hard-fail (khớp
main() dòng ~252 fail=bool(M1) + docstring hàm audit_lunar_season_mismatch "WARN khong
FAIL"; xem module docstring event_ledger_miner). Exit 1 = có mâu thuẫn xuyên tập M1 rõ ràng.
(Sửa docstring 10/7 audit MEDIUM/LOW #9 — bản cũ ghi "0 M4 CHẮC CHẮN" gây hiểu nhầm M4 chặn exit.)
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from event_ledger_miner import mine, episode_files, ROSTER  # noqa: E402

SVHMP = Path(__file__).parent.parent

# Dong bo voi F2 (event_ledger_miner.MAX_LINE_WINDOW_FOR_SAME_REFERENT) — cua so
# hep quanh 1 lan nhac ten de gom tuoi/years_ago CUNG 1 nguoi, tranh gop nham
# nhan vat khac gan do (bai hoc F2: window rong = 70% tap flag sai).
MAX_LINE_WINDOW_FOR_EXACT_NAME = 3

# Tu khoa lich am PHO THONG (dinh danh, khong can nguon rieng — khac cau tra
# nhay cam BP9). Mua/thoi tiet KY VONG di kem — chi canh bao (WARN) neu mo ta
# mua ro rang MAU THUAN, KHONG hard-fail (calibrate nguong tu golden — TASK M4).
LUNAR_SEASON_HINTS = {
    'rằm tháng 7': {'expect_season_words': ['mưa', 'âm u', 'se lạnh', 'thu'],
                    'contradict_words': ['nắng gắt', 'oi bức', 'nóng hầm hập']},
    'vu lan': {'expect_season_words': ['mưa', 'âm u', 'thu'],
              'contradict_words': ['nắng gắt', 'oi bức']},
    'tết': {'expect_season_words': ['lạnh', 'rét', 'se lạnh', 'mưa phùn'],
           'contradict_words': ['nắng gắt', 'oi bức', 'nóng hầm hập']},
}


def check_arithmetic_consistency_across_episodes(ages_by_ep, years_ago_by_ep):
    """Ham THUAN (khong phu thuoc I/O) — day la logic that cua M1, test duoc
    bang mutation voi du lieu DA XAC NHAN cung 1 nguoi (synthetic). Tra ve
    True neu ton tai it nhat 1 cach chon tuoi/tap khop nhau qua years_ago
    (hoac bang nhau) — False neu KHONG co to hop nao khop (mau thuan that)."""
    all_years_ago = set()
    for v in years_ago_by_ep.values():
        all_years_ago |= v
    eps_sorted = sorted(ages_by_ep)
    if len(eps_sorted) < 2:
        return True
    base_ep = eps_sorted[0]
    for other_ep in eps_sorted[1:]:
        compatible = any(
            abs(a1 - a2) == 0 or abs(a1 - a2) in all_years_ago
            for a1 in ages_by_ep[base_ep] for a2 in ages_by_ep[other_ep])
        if not compatible:
            return False
    return True


def _load_full_char_names(roster_path=None):
    """Ten NHAN VAT DAY DU (ca cum char_name NGUYEN VAN, vd 'Phong Hoài Đức')
    tu roster -> danh sach ten -> [(pas_id, assigned_ep), ...]. Day la lop MOI,
    HEP HON _load_nickname_candidates cua F1 (F1 tach TUNG TU rieng le trong
    char_name ra lam ung vien nickname/fuzzy — chinh dieu nay gay 16 false-
    positive lich su, xem G4_REPORT.md muc 3). O day KHONG tach tu: chi lay
    CA CUM ten nguyen van lam khoa so sanh literal, exact, case-sensitive."""
    roster = yaml.safe_load(Path(roster_path or ROSTER).read_text(encoding='utf-8'))
    out = {}
    for p in roster['passengers']:
        name = (p.get('char_name') or '').strip()
        if len(name.split()) < 2:
            continue   # KHONG phai "full name" that (vd ho don le 'Nguyễn' trong spare_pool draft) — bo qua
        out.setdefault(name, []).append((p['id'], p.get('assigned_ep')))
    return out


def _find_full_name_line_hits(output_root, full_names):
    """Quet THAN BAI moi tap (episode.md) tim CA CUM ten nhan vat day du xuat
    hien LITERAL (case-sensitive, khop nguyen cum — dung word-boundary Unicode
    nhu event_ledger_miner._load_nickname_candidates/nickname_hits, KHONG tach
    tu, KHONG suy luan biet danh). Tra ve: ten -> {ep: [line_no, ...]}."""
    hits = {}
    for ep, path in episode_files(output_root):
        lines = path.read_text(encoding='utf-8').splitlines()
        for name in full_names:
            pattern = re.compile(r'(?<![\wÀ-ỹ])' + re.escape(name) + r'(?![\wÀ-ỹ])')
            found = [i for i, ln in enumerate(lines, 1) if pattern.search(ln)]
            if found:
                hits.setdefault(name, {})[ep] = found
    return hits


def find_exact_name_cross_episode_conflicts(mined, output_root=None, roster_path=None):
    """M1 LOP MOI, HEP HON F1 (theo TASK sua loi): chi coi la DU TIN CAY de
    hard-fail khi CA HAI dieu kien dung dong thoi:
      (a) CUNG 1 CUM TEN NHAN VAT DAY DU xuat hien LITERAL (case-sensitive,
          full-name match, KHONG suy luan/fuzzy/biet danh nhu F1) o >=2 tap
          KHAC NHAU; VA
      (b) check_arithmetic_consistency_across_episodes() (ham thuan, da
          mutation-test) phat hien mau thuan so hoc THAT giua cac moc
          tuoi/years_ago nam GAN (+-3 dong, dong bo F2) moi lan nhac ten do
          trong tung tap.
    KHONG ap dung logic nay len F1 (fuzzy tu-don/nickname) — F1 van CHI la
    ung vien can nguoi xem lai (nguyen nhan 16 false-positive cu neu dung lam
    hard-fail, xem G4_REPORT.md), KHONG duoc lap lai loi do o day."""
    full_names = _load_full_char_names(roster_path)
    if not full_names:
        return []
    hits = _find_full_name_line_hits(output_root, full_names)
    scans = mined['scans']
    violations = []
    for name, per_ep_lines in sorted(hits.items()):
        eps_with_hit = sorted(per_ep_lines)
        if len(eps_with_hit) < 2:
            continue   # (a) chua thoa: chi 1 tap nhac ten nay
        ages_by_ep, years_ago_by_ep = {}, {}
        for ep in eps_with_hit:
            if ep not in scans:
                continue
            hit_lines = per_ep_lines[ep]
            temporal = scans[ep]['temporal_mentions']
            ages = {t['value'] for t in temporal if t['kind'] == 'age' and any(
                abs(t['line'] - hl) <= MAX_LINE_WINDOW_FOR_EXACT_NAME for hl in hit_lines)}
            years_ago = {t['value'] for t in temporal if t['kind'] == 'years_ago' and any(
                abs(t['line'] - hl) <= MAX_LINE_WINDOW_FOR_EXACT_NAME for hl in hit_lines)}
            # CHI coi la "moc thoi gian" hop le neu co CA age VA years_ago GAN
            # nhau (cap doi that — dung mau vi du TASK '21 tuoi... muoi nam
            # truoc'). Neu tap chi co 1 trong 2 (vd chi co age le, khong co
            # years_ago di kem) -> KHONG du de lam "temporal anchor", bo qua
            # tap do (tranh false-positive kieu F2 cu: 2 tuoi khac nhau xuat
            # hien gan 1 ten nhung KHONG co phep tinh nao lien ket — do la
            # trung hop 2 nguoi/boi canh khac nhau, khong phai mau thuan that;
            # da xac nhan case that 'Hạ Nhi' tren du lieu that gay bao dong
            # gia truoc khi them dieu kien nay).
            if ages and years_ago:
                ages_by_ep[ep] = ages
                years_ago_by_ep[ep] = years_ago
        if len(ages_by_ep) < 2:
            continue   # khong du >=2 tap co CAP tuoi+years_ago hop le gan ten nay de doi chieu that
        if not check_arithmetic_consistency_across_episodes(ages_by_ep, years_ago_by_ep):
            violations.append({
                'exact_name': name,
                'episodes': eps_with_hit,
                'ages_by_ep': {e: sorted(v) for e, v in ages_by_ep.items()},
                'years_ago_by_ep': {e: sorted(v) for e, v in years_ago_by_ep.items()},
                'evidence': (f"'{name}' xuat hien literal (exact, case-sensitive) o "
                            f"{['ep_%02d' % e for e in eps_with_hit]} — tuoi/moc gan ten do "
                            f"({ {e: sorted(v) for e, v in ages_by_ep.items()} }) khong khop qua "
                            f"years_ago ({ {e: sorted(v) for e, v in years_ago_by_ep.items()} })"),
            })
    return violations


def check_cross_episode_M1(mined, output_root=None, roster_path=None):
    """M1 tren DU LIEU THAT: F1 (nickname collision, tach tu-don) la UNG VIEN
    CHUA XAC NHAN cung 1 nguoi (tu dong xac nhan 'chủ ý hay trùng âm tiết ngẫu
    nhiên' — xem event_ledger_miner docstring) — KHONG duoc dung lam nguon
    FAIL cung, giu nguyen quyet dinh nay (tranh lap lai 16 false-positive cu).

    BUG DA SUA (xem reports/G4_FIX_TIMELINE_CROSSEP.md): ham nay TRUOC DAY bo
    qua tham so `mined`, return [] VO DIEU KIEN — nen KHONG BAO GIO bat duoc
    mau thuan xuyen tap du ro rang den dau. Fix: them 1 lop MOI, HEP HON F1 —
    exact literal full-name match (khong fuzzy) + xac nhan mau thuan so hoc
    THAT qua check_arithmetic_consistency_across_episodes(). Tren du lieu that
    hien tai (50 tap, one-shot-only bible/03) -> case tin cay nay hiem/0 la
    DUNG (chua thay ten day du nao xuat hien lai VOI mau thuan so hoc that
    trong text that) — khong phai tool yeu, la gioi han THAT (xem honest_caveat
    trong report: bien the ten/biet danh/dai tu van can D3 ky moi xu ly duoc).
    """
    return find_exact_name_cross_episode_conflicts(mined, output_root, roster_path)


def check_lunar_season_from_files(output_root=None):
    """M4: cum tu-khoa lich am + mo ta mua MAU THUAN ro rang trong CUNG doan
    van ban (proximity ~500 ky tu). Quet truc tiep file (can full text, khac
    event_ledger_miner chi giu temporal_mentions da trich, khong nhan doi logic
    do). WARN (khong FAIL) — nguong calibrate tu golden theo TASK."""
    root = output_root or (SVHMP / 'output')
    warns = []
    for d in sorted(root.glob('ep_*')):
        m = re.fullmatch(r'ep_(\d+)', d.name)
        f = d / 'episode.md'
        if not (m and f.exists()):
            continue
        ep = int(m.group(1))
        text = f.read_text(encoding='utf-8').lower()
        for phrase, cfg in LUNAR_SEASON_HINTS.items():
            idx = text.find(phrase)
            if idx < 0:
                continue
            window = text[max(0, idx - 500):idx + 500]
            hit_contradict = [w for w in cfg['contradict_words'] if w in window]
            if hit_contradict:
                warns.append(f"ep_{ep:02d}: nhắc '{phrase}' nhưng mô tả mùa "
                            f"mâu thuẫn ({hit_contradict}) trong đoạn gần đó")
    return warns


def check_qa_fact_check_reconcile_note():
    """RECONCILE finding (khong phai check that) — ghi lai lam sao da xac minh
    qa_fact_check.py KHONG the tai su dung tong quat."""
    return ["qa_fact_check.py::check_facts() HARDCODE cho EP01 (khong doc tham "
            "so facts, khong tong quat hoa) — KHONG goi duoc cho tap khac. "
            "Ghi nhan finding, KHONG phai loi cua D1."]


def run(output_root=None):
    mined = mine(output_root)
    m1 = check_cross_episode_M1(mined, output_root)
    m4_warns = check_lunar_season_from_files(output_root)
    f2_candidates = mined['findings']['F2_internal_age_arithmetic_conflict']
    reconcile_notes = check_qa_fact_check_reconcile_note()
    return {
        'M1_cross_episode_violations': m1,
        'M4_lunar_season_warns': m4_warns,
        'F2_candidates_for_human_review': f2_candidates,
        'reconcile_notes': reconcile_notes,
        'episodes_scanned': mined['episodes_scanned'],
    }


def main():
    result = run()
    print("=== TIMELINE CHECK (G4 D1) ===")
    print(f"  episodes scanned: {len(result['episodes_scanned'])}")
    for note in result['reconcile_notes']:
        print(f"  [RECONCILE] {note}")
    for v in result['M1_cross_episode_violations']:
        print(f"  [FAIL] M1: {v}")
    for w in result['M4_lunar_season_warns']:
        print(f"  [WARN] M4: {w}")
    print(f"  F2 candidates (người xem lại, không hard-fail): "
          f"{len(result['F2_candidates_for_human_review'])} tập")
    fail = bool(result['M1_cross_episode_violations'])
    print(f"=== {'FAIL' if fail else 'PASS'} ===")
    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
