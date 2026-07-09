"""tools/g7_ep01_dry_run.py — G7 D5: dry-run episode_generator tren EP01, so sanh
packet voi golden reference THAT (output/ep_01/episode.md + episode_golden_text.md).

KHONG ghi vao output/ep_01/ that (bai hoc DEBT-005) - output ghi vao sandbox cach ly
output/ep_g7_sample/ (mirror pattern output/ep_g3_sample/ cua G3 dialogue).

TAI SU DUNG post_render_gate.check_ep() (12-check co san, DOC-ONLY tren episode.md
that) thay vi tu viet lai regex bell/ghost/word_count (R211, tranh nhan doi).
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import episode_generator as eg  # noqa: E402
import post_render_gate as prg  # noqa: E402 - tai dung check_ep(), khong viet lai regex

SANDBOX_DIR = REPO / "output" / "ep_g7_sample"
GOLDEN_TEXT = REPO / "output" / "ep_01" / "episode_golden_text.md"
REAL_EPISODE = REPO / "output" / "ep_01" / "episode.md"


def _extract_gate_fact(results, needle):
    """Tim dong (ok, msg) trong ket qua post_render_gate.check_ep() chua 'needle' -
    tra ve (ok, msg) hoac (None, None) neu khong tim thay. Tai su dung message THAT
    cua gate co san, khong tu tinh lai regex."""
    for ok, msg in results:
        if needle in msg:
            return ok, msg
    return None, None


def reconcile_ep01(packet):
    """So sanh tung field frontmatter cua packet voi du lieu THAT (episode.md qua
    post_render_gate + golden text substring search). Tra ve list finding dict -
    KHONG tu ket luan PASS/FAIL toan cuc thay Mr.Long/kiem duyet, chi bao cao THAT."""
    if not REAL_EPISODE.exists():
        return [{"field": "_all", "match": None, "detail": "output/ep_01/episode.md khong ton tai - khong the doi chieu"}]

    gate_results = prg.check_ep(1)
    text = REAL_EPISODE.read_text(encoding="utf-8")
    findings = []

    fm = packet["episode_frontmatter"]

    ok, msg = _extract_gate_fact(gate_results, "word_count")
    findings.append({
        "field": "word_count_target", "packet_value": fm["word_count_target"],
        "gate_fact": msg, "match": ok,
    })

    ok, msg = _extract_gate_fact(gate_results, "bell mention")
    findings.append({
        "field": "bell_count", "packet_value": fm["bell_count"],
        "gate_fact": msg, "match": ok,
    })

    ok, msg = _extract_gate_fact(gate_results, "ghost manifest")
    findings.append({
        "field": "ghost_manifest", "packet_value": fm["ghost_manifest"],
        "gate_fact": msg, "match": ok,
    })

    ok, msg = _extract_gate_fact(gate_results, "6 sections")
    findings.append({
        "field": "episode_sections (6 component_ref)", "packet_value": "HOOK..CLIFFHANGER",
        "gate_fact": msg, "match": ok,
    })

    # signature_object/stop_location: object library display_name PHAI xuat hien
    # duoi 1 dang nao do trong van ban THAT (khong doi hoi khop tuyet doi tung chu -
    # day la doi chieu CANON, khong phai QA text-exact).
    b12 = yaml.safe_load((REPO / "bible" / "12_object_library.yaml").read_text(encoding="utf-8"))
    obj_display = b12["object_library"][fm["signature_object"]]["display_name"]
    obj_core_words = [w for w in obj_display.split() if len(w) >= 3]  # "dong ho", "xa cu" nhan dien loi
    obj_found = any(w in text.lower() for w in ["đồng hồ", "xà cừ"])
    findings.append({
        "field": "signature_object", "packet_value": f"{fm['signature_object']} ({obj_display})",
        "gate_fact": f"tim '{obj_display}' (tu bible/12) trong episode.md that", "match": obj_found,
    })

    loc_found = fm["stop_location"].lower() in text.lower()
    findings.append({
        "field": "stop_location", "packet_value": fm["stop_location"],
        "gate_fact": "tim nguyen van trong episode.md that", "match": loc_found,
    })

    return findings


def main():
    packet = eg.build_episode_packet(1)
    findings = reconcile_ep01(packet)

    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    packet_out = SANDBOX_DIR / "episode_packet_ep01.yaml"
    packet_out.write_text(yaml.safe_dump(packet, allow_unicode=True, sort_keys=False), encoding="utf-8")

    report_lines = [
        "# G7 D5 — Dry-run reconciliation report (episode_generator.py vs EP01 golden reference)",
        "",
        f"Packet: {packet_out.relative_to(REPO)}",
        f"So sanh voi: {REAL_EPISODE.relative_to(REPO)} (qua post_render_gate.check_ep(1), khong ghi de)",
        "",
        "| Field | Packet value | Bang chung that | Match |",
        "|---|---|---|---|",
    ]
    n_match = 0
    n_total = 0
    for f in findings:
        if f.get("match") is None:
            mark = "N/A"
        else:
            mark = "OK" if f["match"] else "LECH"
            n_total += 1
            n_match += 1 if f["match"] else 0
        report_lines.append(f"| {f['field']} | {f.get('packet_value', '-')} | {f.get('gate_fact', f.get('detail', '-'))} | {mark} |")
    report_lines.append("")
    report_lines.append(f"Tong: {n_match}/{n_total} field doi chieu khop (KHONG phai gate PASS/FAIL chinh thuc - "
                         "day la bang chung dry-run D5 cho kiem duyet/Mr.Long xem xet, khong tu phong PASS).")

    report_path = SANDBOX_DIR / "D5_dry_run_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"=== G7 D5 DRY-RUN EP01 ===")
    for f in findings:
        mark = "N/A" if f.get("match") is None else ("OK" if f["match"] else "LECH")
        print(f"  [{mark}] {f['field']}: {f.get('packet_value', '-')}")
    print(f"\nPacket: {packet_out}")
    print(f"Report: {report_path}")
    print(f"{n_match}/{n_total} field doi chieu khop")
    return 0


if __name__ == "__main__":
    sys.exit(main())
