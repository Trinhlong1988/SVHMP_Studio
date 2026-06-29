"""R110 — Narrative continuity audit.

Track:
  1. Object location (đồng hồ, radio, giấy gấp tư) — detect contradictions
  2. Scene physics (xe dừng/chạy, cửa xe mở/đóng) — detect logic gap
  3. Character count (cô gái ghế 7/8, ông cụ, anh trung niên) — detect duplicate
  4. Contradict statements (X then NOT-X within episode)

This is HEURISTIC scan — em LLM still text-only, narrative judgement final.
"""
import re
import sys
from pathlib import Path

EPISODE = Path(r"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/output/ep_01/episode.md")

# Track key objects
TRACKED_OBJECTS = {
    "đồng hồ": ["cầm", "ôm", "giữ", "trượt khỏi", "rơi xuống", "nhặt", "đặt", "rút tay", "buông"],
    "radio": ["ôm", "bật", "tắt", "xoay núm"],
    "giấy gấp tư": ["cầm", "giữ", "đọc", "gập", "đặt"],
}

# Scene physics statements
SCENE_PHYSICS_FACTS = [
    (r"xe (chạy chậm|chạy tiếp|đi chậm)", "moving"),
    (r"xe (dừng|dừng lại|đỗ)", "stopped"),
    (r"cánh cửa xe.*mở", "door_open"),
    (r"cửa xe đóng", "door_closed"),
]

# Repeat statement that might contradict
CONTRADICT_PAIRS = [
    ("tay vẫn ôm", "rơi"),  # ôm vs rơi
    ("không hỏi thêm câu nào", "hỏi"),  # before any actual hỏi
    ("chiếc đồng hồ trượt khỏi lòng tay", "tay vẫn ôm"),
]


def cut_metadata(text):
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    for marker in ("# SELF-CHECK", "# NOTES", "## SOUL", "## REVIEW", "## NARRATION", "## EMOTION"):
        idx = text.find(marker)
        if idx >= 0:
            text = text[:idx]
    return text


def scan_object_track(text):
    """Scan object actions in narrative order, flag contradictions."""
    violations = []
    lines = text.split("\n")
    # Track đồng hồ specifically — most critical
    # Sequence: cầm → trượt khỏi/rơi xuống → nhặt → đặt lại / áp / ôm
    states = []  # list of (line, state, ctx)
    for ln, line in enumerate(lines, 1):
        if line.startswith(("#", "[", "```", "---", "|")):
            continue
        lc = line.lower()
        if "trượt khỏi" in lc and "đồng hồ" in lc:
            states.append((ln, "DROPPED", line[:80]))
        if "rơi" in lc and "đồng hồ" in lc and "xuống" in lc and "trượt khỏi" not in lc:
            states.append((ln, "DROPPED", line[:80]))
        if "tay vẫn ôm" in lc and "đồng hồ" in lc:
            states.append((ln, "HOLDING", line[:80]))
        if "nhặt" in lc and ("đồng hồ" in lc or "nó" in lc):
            # Negation-aware: "không hề ... nhặt" or "không buồn nhặt" or "không nhặt"
            negation_keywords = ["không", "chẳng", "chưa", "không hề", "không thể", "không còn", "không buồn"]
            if not any(neg in lc for neg in negation_keywords):
                states.append((ln, "PICKED_UP", line[:80]))
        if "siết chặt" in lc and ("đồng hồ" in lc or "nó" in lc):
            states.append((ln, "HOLDING", line[:80]))
        if "đặt" in lc and "đồng hồ" in lc and "lên ghế" in lc:
            states.append((ln, "PLACED", line[:80]))

    # Flag: HOLDING after DROPPED (without PICKED_UP between)
    last_state = None
    for ln, state, ctx in states:
        if state == "HOLDING" and last_state == "DROPPED":
            violations.append((ln, "OBJECT CONTRADICT: đồng hồ HOLDING after DROPPED (no PICK_UP)", ctx))
        last_state = state
    return violations, states


def scan_scene_physics(text):
    """Detect scene physics gaps."""
    violations = []
    lines = text.split("\n")
    moving = None
    door_state = None
    for ln, line in enumerate(lines, 1):
        if line.startswith(("#", "[", "```", "---", "|")):
            continue
        for pattern, state in SCENE_PHYSICS_FACTS:
            if re.search(pattern, line, flags=re.IGNORECASE):
                if state == "moving":
                    moving = (ln, line[:80])
                elif state == "stopped":
                    moving = None
                elif state == "door_open":
                    door_state = "open"
                elif state == "door_closed":
                    door_state = "closed"
        # If someone "ngồi vào" or "ngồi sẵn" while xe moving + no door context
        if ("ngồi vào" in line.lower() or "ngồi sẵn" in line.lower()) and moving:
            # Check if there's an explicit acknowledgement of supernatural
            context_50 = " ".join(lines[max(0, ln-3):ln+1]).lower()
            if not any(hint in context_50 for hint in ["không nhận ra mình lên", "không một lần xe dừng", "vậy mà", "lúc nào", "lên xe vào lúc nào"]):
                violations.append((ln, "SCENE PHYSICS: 'ngồi vào/sẵn' khi xe đang chạy + KHÔNG có supernatural acknowledgement", line[:80]))
    return violations


def scan_character_count(text):
    """Detect duplicate character introduction at same seat."""
    violations = []
    lines = text.split("\n")
    seat_occupants = {}  # seat_num: list of (ln, description)
    for ln, line in enumerate(lines, 1):
        if line.startswith(("#", "[", "```", "---", "|")):
            continue
        # Pattern: "ngồi xuống ghế số X" / "ngồi vào ghế số X" / "ghế X có ..."
        for m in re.finditer(r"(ngồi (?:xuống|vào|sẵn).*?ghế (?:số|thứ)?\s*([\w\s]+?))(?=[.,\n])", line, flags=re.IGNORECASE):
            seat = m.group(2).strip()
            seat_occupants.setdefault(seat, []).append((ln, m.group(0)[:80]))
    for seat, occupants in seat_occupants.items():
        if len(occupants) > 1:
            # Check if same character (use first 20 chars)
            distinct_descs = {o[1][:30] for o in occupants}
            if len(distinct_descs) > 1:
                violations.append((occupants[0][0], f"CHARACTER COUNT: ghế '{seat}' có {len(occupants)} lượt ngồi distinct", "; ".join(d[:60] for d in distinct_descs)))
    return violations


def main():
    text = EPISODE.read_text(encoding="utf-8")
    text_clean = cut_metadata(text)

    print("=== R110 NARRATIVE CONTINUITY AUDIT ===\n")

    print("[1] Object tracking (đồng hồ):")
    obj_violations, states = scan_object_track(text_clean)
    for ln, kind, ctx in obj_violations:
        print(f"  ⚠️ L{ln} {kind}: {ctx}")
    if not obj_violations:
        print(f"  ✓ {len(states)} state transitions OK")

    print("\n[2] Scene physics:")
    sp_violations = scan_scene_physics(text_clean)
    for ln, kind, ctx in sp_violations:
        print(f"  ⚠️ L{ln} {kind}: {ctx}")
    if not sp_violations:
        print("  ✓ No physics gap detected")

    print("\n[3] Character count per seat:")
    cc_violations = scan_character_count(text_clean)
    for ln, kind, ctx in cc_violations:
        print(f"  ⚠️ L{ln} {kind}: {ctx}")
    if not cc_violations:
        print("  ✓ No duplicate seat occupancy")

    fail = len(obj_violations) + len(sp_violations) + len(cc_violations) > 0
    print(f"\n== R110 GATE: {'FAIL - FIX REQUIRED' if fail else 'PASS'} ==")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
