# TASK BP4 — RUNTIME + EVENT ARCHITECTURE (theo BP_PIPELINE_MASTER.md)

## MISSION
Dòng chảy runtime + event bus + state machine + memory chi tiết — FORMAT đã khai ở BP-C,
giờ đổ DATA.

## DELIVERABLES
1. `governance/blueprint/bp4/runtime_flow.yaml` — chuỗi render end-to-end (story_planner →
   decision_engine → generator → qa_runtime → tts → audio → production → video → publisher);
   mỗi hop: input/output artifact + status exists|planned (chuỗi tts→audio→production HIỆN CÓ
   THẬT quanh `tools/svhmp_v13_render.py` LOCKED — trỏ, không tả lại sai).
2. `governance/blueprint/bp4/event_bus.yaml` — events[]: event_id · emitter · chain[] có thứ tự.
   **LUẬT (phán quyết 3/7): mỗi hop trong chain PHẢI là domain HOẶC facet ĐÃ KHAI (BP2/BP3)**
   — hop lạ kiểu Music/Lighting phải map về facet của audio/video, không được bịa tên. Validator bắt.
   Chuỗi mẫu bắt buộc: ghost_appears (supernatural → world → character.emotion → dialogue →
   audio.sfx → qa_runtime → analytics).
3. `governance/blueprint/bp4/state_machines.yaml` — entity states (Ghost: dormant→watching→
   manifest→attack→released · Character-fear: normal→fear→panic→trauma→recovery ...);
   transitions[] (from·to·trigger_event — trigger PHẢI là event_id đã khai).
4. `governance/blueprint/bp4/memory_architecture.yaml` — mở rộng 6 scope BP-C thành chi tiết:
   scope · owner (domain đã khai) · store (path status) · retention · reader/writer theo BP3.
5. `governance/blueprint/bp4/00_runtime_event.md` (11-element).
6. Validator: hop hợp lệ · trigger là event thật · state machine không orphan-state ·
   memory owner/reader/writer khớp BP3 · dòng runtime chỉ chảy layer thấp→cao.
7. Negative test: hop lạ → FAIL · trigger ma → FAIL · state không đường vào → FAIL ·
   memory writer vượt BP3 → FAIL · runtime flow ngược layer → FAIL.

## MUTATION AUDIT SẼ BẮN
hop bịa (Lighting trần) · event trigger ma · state orphan · memory 2-writer · flow ngược.
STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.
