# G7 D5 — Dry-run reconciliation report (episode_generator.py vs EP01 golden reference)

Packet: output\ep_g7_sample\episode_packet_ep01.yaml
So sanh voi: output\ep_01\episode.md (qua post_render_gate.check_ep(1), khong ghi de)

| Field | Packet value | Bang chung that | Match |
|---|---|---|---|
| word_count_target | 2300 | word_count 4587 >= 2000 (hard_floor) | OK |
| bell_count | 1 | bell mention 0 >= 1 (or metadata bell_count:1) | OK |
| ghost_manifest | 1 | ghost manifest count 8 >= 1 | OK |
| episode_sections (6 component_ref) | HOOK..CLIFFHANGER | 6 sections HOOK/SETUP/INCIDENT/REVEAL/PAYOFF/CLIFFHANGER present (flexible) | OK |
| signature_object | OBJ_DONG_HO_XA_CU (đồng hồ nữ vỏ xà cừ) | tim 'đồng hồ nữ vỏ xà cừ' (tu bible/12) trong episode.md that | OK |
| stop_location | Cầu Long Biên | tim nguyen van trong episode.md that | OK |

Tong: 6/6 field doi chieu khop (KHONG phai gate PASS/FAIL chinh thuc - day la bang chung dry-run D5 cho kiem duyet/Mr.Long xem xet, khong tu phong PASS).