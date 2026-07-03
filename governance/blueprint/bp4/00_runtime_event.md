# BP4 — 00_runtime_event.md — Runtime + Event Architecture
> Enforce: `tools/bp4_runtime_check.py` · chứng thực: `tests/test_bp4_runtime.py` · data: `governance/blueprint/bp4/runtime_flow.yaml` + `governance/blueprint/bp4/event_bus.yaml` + `governance/blueprint/bp4/state_machines.yaml` + `governance/blueprint/bp4/memory_architecture.yaml`.

**Mission:** Dòng chảy vận hành của Studio thành DATA máy-kiểm: 9 hop render end-to-end, 8 event chuẩn, 4 state machine, 6 memory scope chi tiết — FORMAT đã khai ở BP-C, giờ đổ data.
**Purpose:** Khóa "cái gì chảy đi đâu khi nào" trước khi G-phase code: generator không thể nhận input ngoài flow, hồn ma không thể đổi trạng thái ngoài transitions, sự kiện không thể chạm hop chưa khai.
**Scope:** Runtime flow (story_planner→…→publisher) · event bus · state machines (ghost/character_fear/character_life/voice_state) · memory 6 scope. KHÔNG viết engine (tier-2), KHÔNG sửa render LOCKED.
**Authority:** BP0 v2.0 + BP1-BP3 LOCKED = nguồn luật; phán quyết 3/7: hop = domain HOẶC facet ĐÃ KHAI. Đổi flow/event/state = RFC + Mr.Long.
**Responsibilities:** `runtime_flow`: 9 hop layer TĂNG strictly, 5 hop `exists` trỏ tool THẬT (scaffold+preflight+v13_render+audio_qa+final_verify — chuỗi tts→audio→production HIỆN CÓ quanh render LOCKED, chỉ trỏ), 4 hop planned 5-metadata. `event_bus`: 8 event, mỗi hop ∈ inventory hoặc `domain.facet_id` BP2 (Music/SFX map về DOMAIN `audio` — audio chưa có facet inventory vì BP2 chỉ phủ 13 domain tầng thấp; Lighting không tồn tại trong hệ audio-first). `state_machines`: trigger PHẢI là event_id đã khai; `character_life` map trực tiếp facet `story_arc_personal` (BP2b); `voice_state` dùng 6 state THẬT bible/15 (SoT exists, key resolve máy). `memory_architecture`: 6 scope khớp BP0 exact, writers ⊆ {owner, mr_long} (BP3), readers ⊆ reader grant BP0.
**Workflow:** sửa data → `bp4_runtime_check.py` exit 0 → pytest mutation → commit R200 → audit 7 bước → Mr.Long ký.
**Mandatory Rules:** (1) Runtime flow CHỈ chảy layer thấp→cao (ngược = FAIL). (2) Hop lạ = FAIL — map về domain/facet thật, không bịa tên. (3) Trigger ma = FAIL. (4) State không đường vào (trừ initial) = ORPHAN FAIL. (5) Memory owner/store drift so BP0 = FAIL; writer vượt {owner, mr_long} = FAIL. (6) DUP-KEY loader + version cross-check 4 file.
**PASS Criteria:** `bp4_runtime_check.py` exit 0 + mutation battery xanh trong `pytest tests/` (ENFORCED qua ci_gate).
**FAIL Criteria:** hop bịa / trigger ma / orphan state / memory 2-writer / flow ngược layer → exit 1.
**Examples:** thêm hop `lighting` vào ghost_appears → FAIL "hop la"; trigger `ghost_dances` → EVENT-MA; thêm state `possessed` không transition vào → ORPHAN; writer episode_memory += dialogue → VUOT BP3.
**Promotion Rules:** `bp4_runtime: candidate` — Builder không lock/tag; Mr.Long ký sau audit (reconcile `governance/constitution/00_constitution.md`).

## Ghi chú semantics (kiểm duyệt phán khi audit)
Event chain = luồng PHẢN ỨNG sự kiện (notification), KHÁC data-read grant: `ghost_appears: supernatural → world` nghĩa world-context phản ứng (khung cảnh đổi), không phải world "đọc dữ liệu" supernatural — nên KHÔNG áp rule reader-grant của `formats.event` BP0 (rule đó dành cho events khai TRONG blueprint_domains, hiện rỗng); BP4 dùng luật phán quyết 3/7 (hop = domain/facet đã khai). Nếu kiểm duyệt phán ngược, sửa chain theo reader-grant là 1 lần chạy validator.
