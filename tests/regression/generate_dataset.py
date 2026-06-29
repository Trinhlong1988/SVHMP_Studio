"""Generate 50 positive + 50 negative regression dataset.

CRITICAL: Inject violations BEFORE metadata block (codeblock ```) so cut_metadata() KHÔNG strip them.
"""
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
GOLDEN = BASE / "output/ep_01/episode_golden_text.md"
POS_DIR = BASE / "tests/regression/positive"
NEG_DIR = BASE / "tests/regression/negative"

POS_DIR.mkdir(parents=True, exist_ok=True)
NEG_DIR.mkdir(parents=True, exist_ok=True)


def inject_before_metadata(text, snippet):
    """Inject snippet INSIDE main story body (right before next ## section after HOOK content).

    cut_metadata strips codeblock + ## SOUL/REVIEW/etc markers.
    Best inject point: inside HOOK section (between HOOK title and ## 2. SETUP).
    """
    # Find HOOK content area: after "## 1. HOOK" heading
    hook_start = text.find("## 1. HOOK")
    if hook_start < 0:
        # Fallback: inject after first ## section header
        h_idx = text.find("## ")
        if h_idx < 0:
            return text + "\n\n" + snippet + "\n"
        # Find end of that paragraph block
        next_section = text.find("\n## ", h_idx + 5)
        if next_section < 0:
            return text + "\n\n" + snippet + "\n"
        # Inject right before next section header
        return text[:next_section] + "\n\n" + snippet + "\n" + text[next_section:]
    # Inject inside HOOK — after first paragraph but before ## 2. SETUP
    setup_start = text.find("## 2. SETUP", hook_start)
    if setup_start < 0:
        # No SETUP marker, inject at end of HOOK area
        return text[:hook_start + 50] + "\n\n" + snippet + "\n" + text[hook_start + 50:]
    # Inject right before SETUP header
    return text[:setup_start] + "\n\n" + snippet + "\n\n---\n\n" + text[setup_start:]


def inject_after_payoff(text, snippet):
    """Inject AFTER PAYOFF section (after L444 DROPPED area). Used for R110 contradict tests."""
    payoff_start = text.find("## 5. PAYOFF")
    if payoff_start < 0:
        return inject_before_metadata(text, snippet)
    cliff_start = text.find("## 6. CLIFFHANGER", payoff_start)
    if cliff_start < 0:
        return text + "\n\n" + snippet + "\n"
    return text[:cliff_start] + snippet + "\n\n---\n\n" + text[cliff_start:]


def make_positive(idx, golden_text):
    """50 positive variants — micro modifications KHÔNG vi phạm rule."""
    variants = [
        lambda t: t.replace("rất lâu", "lâu lắm"),
        lambda t: t.replace("mưa đổ xuống", "mưa rơi xuống"),
        lambda t: t.replace("chậm dần", "chầm chậm dần"),
        lambda t: t.replace("im lìm", "yên ắng"),
        lambda t: t.replace("khoan thai", "thong dong"),
        lambda t: t.replace("nhẹ nhàng", "rất nhẹ"),
        lambda t: t.replace("êm xuống", "êm ái xuống"),
        lambda t: t.replace("rất xa", "rất xa xôi"),
        lambda t: t.replace("vào trong", "vào"),
        lambda t: t.replace("đã thành thói quen", "đã quen"),
    ]
    n = len(variants)
    text = golden_text
    for i in range(idx % n):
        text = variants[i](text)
    return text


def make_negative(idx, golden_text):
    """50 negative — inject 1 violation TRƯỚC metadata."""
    # 8 rules × 5-6 variants each = 50
    violations = [
        # ====== R86 EOL diacritic (7) ======
        ("R86_001", lambda t: inject_before_metadata(t, "Câu thử nghiệm cũ.")),
        ("R86_002", lambda t: inject_before_metadata(t, "Anh ngồi đợi.")),
        ("R86_003", lambda t: inject_before_metadata(t, "Ghế số bảy.")),
        ("R86_004", lambda t: inject_before_metadata(t, "Vỏ ngọc trai sáng quá.")),
        ("R86_005", lambda t: inject_before_metadata(t, "Cô y tá nhẹ.")),
        ("R86_006", lambda t: inject_before_metadata(t, "Âm thanh khe khẽ.")),
        ("R86_007", lambda t: inject_before_metadata(t, "Một âm thanh nhẹ.")),
        # ====== R110 object contradict (4) ======
        ("R110_001", lambda t: t.replace("Anh gật một cái rất nhẹ", "Anh gật, tay vẫn ôm chiếc đồng hồ", 1)),
        ("R110_002", lambda t: inject_after_payoff(t, "Anh không hề cúi xuống nhặt nhưng tay vẫn ôm chiếc đồng hồ siết chặt.")),
        ("R110_003", lambda t: t.replace("rơi êm xuống nệm chiếc ghế bỏ trống số bảy", "rơi êm xuống nệm chiếc ghế nhưng tay vẫn ôm chiếc đồng hồ siết chặt", 1)),
        ("R110_004", lambda t: t.replace("trượt khỏi lòng tay", "trượt khỏi lòng tay rồi anh siết chặt", 1)),
        # ====== R111 phonetic phù phù (7) ======
        ("R111_001", lambda t: inject_before_metadata(t, "Anh thở ra một hơi dài.")),
        ("R111_002", lambda t: inject_before_metadata(t, "Máy bay tới nơi an toàn.")),
        ("R111_003", lambda t: inject_before_metadata(t, "Tóc cột cao vút.")),
        ("R111_004", lambda t: inject_before_metadata(t, "Hơi thở chậm lại từng nhịp.")),
        ("R111_005", lambda t: inject_before_metadata(t, "Vẫn còn nhớ kể lại bao giờ.")),
        ("R111_006", lambda t: inject_before_metadata(t, "Ngồi xuống ghế trống số bảy đó.")),
        ("R111_007", lambda t: inject_before_metadata(t, "Anh thở dài não nề.")),
        # ====== R113 action verb repeat (7) ======
        ("R113_001", lambda t: inject_before_metadata(t, "Bác tài liếc gương chiếu hậu một thoáng.\nBác tài liếc gương chiếu hậu thêm một lần.\nBác tài liếc gương chiếu hậu lâu hơn.")),
        ("R113_002", lambda t: inject_before_metadata(t, "Anh đưa mắt nhìn ra.\nAnh đưa mắt nhìn lên.\nAnh đưa mắt nhìn xuống.\nAnh đưa mắt nhìn ngang.")),
        ("R113_003", lambda t: inject_before_metadata(t, "Cô cúi đầu nhẹ.\nAnh cúi đầu chào.\nÔng cúi đầu lễ phép.")),
        ("R113_004", lambda t: inject_before_metadata(t, "Anh ngẩng đầu lên.\nÔng ngẩng đầu lên.\nCô ngẩng đầu lên.")),
        ("R113_005", lambda t: inject_before_metadata(t, "Anh nhìn xuống ngắm.\nÔng nhìn xuống ngắm.\nCô nhìn xuống ngắm.")),
        ("R113_006", lambda t: inject_before_metadata(t, "Anh quay đầu lại.\nÔng quay đầu lại.\nCô quay đầu lại.")),
        ("R113_007", lambda t: inject_before_metadata(t, "Gật đầu một cái.\nGật đầu một cái.\nGật đầu một cái.")),
        # ====== R117 fact missing (3) ======
        ("R117_001", lambda t: t.replace("Cầu Long Biên", "cây cầu nào đó", 999)),
        ("R117_002", lambda t: t.replace("Kennedy", "sân bay nào đó", 999)),
        ("R117_003", lambda t: t.replace("tám năm", "ba năm", 999).replace("8 năm", "3 năm", 999)),
        # ====== R128 anti-generic (7) ======
        ("R128_001", lambda t: inject_before_metadata(t, "Có lẽ vậy.\nCó lẽ thế.\nCó lẽ ngày mai.\nCó lẽ không bao giờ.\nCó lẽ lúc khác.")),
        ("R128_002", lambda t: inject_before_metadata(t, "Một cảm giác khó tả ập đến.")),
        ("R128_003", lambda t: inject_before_metadata(t, "Không ai biết rằng đêm đó có chuyện kỳ lạ.")),
        ("R128_004", lambda t: inject_before_metadata(t, "Trong khoảnh khắc ấy, mọi thứ dừng lại.")),
        ("R128_005", lambda t: inject_before_metadata(t, "Không hiểu sao thì thầm.\nKhông hiểu sao xảy ra.\nKhông hiểu sao lần nữa.")),
        ("R128_006", lambda t: inject_before_metadata(t, "Anh rùng mình lo lắng.\nCô rùng mình bất an.\nÔng rùng mình sợ hãi.")),
        ("R128_007", lambda t: inject_before_metadata(t, "Đột nhiên anh nhớ ra.\nĐột nhiên anh hiểu rồi.\nĐột nhiên anh thấy rõ.")),
        # ====== R141 SSOT drift (3) ======
        ("R141_001", lambda t: t.replace("Hắc Dạ Ký", "Hắc Vỹ Dạ", 999).replace("Hắc, Dạ, Ký", "Hắc, Vỹ, Dạ", 999)),
        ("R141_002", lambda t: t.replace("Cầu Long Biên", "Cầu Chương Dương", 999)),
        ("R141_003", lambda t: t.replace("bảy giờ mười phút", "tám giờ ba mươi", 999)),
        # ====== Mixed combo (12) ======
        ("MIX_001", lambda t: inject_before_metadata(t, "Đây là câu cũ. Có lẽ vậy.")),
        ("MIX_002", lambda t: inject_before_metadata(t, "Anh thở ra một hơi dài. Có lẽ thế.")),
        ("MIX_003", lambda t: t.replace("Hắc Dạ Ký", "Hắc Vỹ Dạ", 1).replace("Hắc, Dạ, Ký", "Hắc, Vỹ, Dạ", 1)),
        ("MIX_004", lambda t: t.replace("Cầu Long Biên", "cây cầu nào đó", 999)),
        ("MIX_005", lambda t: inject_before_metadata(t, "Bác tài đưa mắt thoáng.\nBác tài đưa mắt nhanh.\nBác tài đưa mắt khẽ.\nBác tài đưa mắt một lần.")),
        ("MIX_006", lambda t: inject_before_metadata(t, "Anh ngồi đợi. Có lẽ vậy.")),
        ("MIX_007", lambda t: inject_before_metadata(t, "Máy bay tới nơi an toàn. Anh thở ra một hơi.")),
        ("MIX_008", lambda t: inject_before_metadata(t, "Ghế số bảy. Anh đợi.")),
        ("MIX_009", lambda t: inject_before_metadata(t, "Có lẽ thế. Có lẽ vậy. Có lẽ không. Có lẽ vâng.")),
        ("MIX_010", lambda t: inject_before_metadata(t, "Đột nhiên anh đợi. Anh thở ra dài.")),
        ("MIX_011", lambda t: inject_before_metadata(t, "Vẫn còn nhớ kể lại bao giờ. Có lẽ thế.")),
        ("MIX_012", lambda t: inject_before_metadata(t, "Ghế trống số bảy đó. Tóc cột cao vút.")),
    ]
    name, fn = violations[idx]
    return name, fn(golden_text)


def verify_positive_no_violation(text):
    """Run R86 + R113 + R128 against text. Return True if clean."""
    import tempfile, subprocess, sys, shutil
    BASE_PATH = BASE
    EPISODE_PATH = BASE_PATH / "output/ep_01/episode.md"
    BACKUP_PATH = EPISODE_PATH.with_suffix(".md.posverify_bak")
    shutil.copy(EPISODE_PATH, BACKUP_PATH)
    EPISODE_PATH.write_text(text, encoding="utf-8")
    subprocess.run([sys.executable, str(BASE_PATH / "tools/tts_adapter_pre_render.py"), "--ep", "1", "--apply"],
                   capture_output=True, timeout=30)
    clean = True
    for tool in ["qa_eol_diacritic.py", "qa_repeat_action.py", "qa_anti_generic.py", "qa_continuity.py", "qa_phonetic_safe.py"]:
        r = subprocess.run([sys.executable, str(BASE_PATH / "tools" / tool)],
                           capture_output=True, text=True, timeout=30, cwd=str(BASE_PATH),
                           encoding="utf-8", errors="ignore")
        if r.returncode != 0:
            clean = False
            break
    shutil.copy(BACKUP_PATH, EPISODE_PATH)
    BACKUP_PATH.unlink()
    return clean


def make_positive_safe(idx, golden_text):
    """Try variants until clean. Fallback to golden."""
    text = make_positive(idx, golden_text)
    if verify_positive_no_violation(text):
        return text
    # Retry with different variant index
    for offset in range(1, 11):
        alt = make_positive((idx + offset) % 10, golden_text)
        if verify_positive_no_violation(alt):
            return alt
    # Fallback: return original golden
    return golden_text


def main():
    golden = GOLDEN.read_text(encoding="utf-8")

    # Cleanup old samples
    for f in POS_DIR.glob("*.md"): f.unlink()
    for f in NEG_DIR.glob("*.md"): f.unlink()

    print("[WRITER] Generating 50 positive samples WITH self-verify (reject violators)...")
    rejected = 0
    for i in range(50):
        text = make_positive_safe(i, golden)
        if text == golden:
            rejected += 1
        (POS_DIR / f"pos_{i:03d}.md").write_text(text, encoding="utf-8")
    print(f"  ✓ {len(list(POS_DIR.glob('*.md')))} positive samples (fallback golden: {rejected})")

    print("[WRITER] Generating 50 negative samples (inject TRƯỚC metadata)...")
    for i in range(50):
        name, text = make_negative(i, golden)
        (NEG_DIR / f"neg_{i:03d}_{name}.md").write_text(text, encoding="utf-8")
    print(f"  ✓ {len(list(NEG_DIR.glob('*.md')))} negative samples")


if __name__ == "__main__":
    main()
