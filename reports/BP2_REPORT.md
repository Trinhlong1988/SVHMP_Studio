# BP2 DOMAIN ARCHITECTURE — REPORT (Builder, TASK_BP2_DOMAIN theo BP_PIPELINE_MASTER)

**Executive verdict: PASS** (phạm vi Builder — verdict máy = exit-code; Builder không tự PASS pipeline).

- Source commit khi build: `118206e` (BP1 locked, tag `bp1-core-v1.0`) · BP0 v2.0 LOCKED tag `blueprint-constitution-v2.0`
- Builder: CMD_BUILD · 2026-07-03

## Bảng deliverable
| File | Vai trò |
|---|---|
| `governance/blueprint/bp2/domain_specs.yaml` | 13 domain × facets/entities/invariants — 58 facet, facet_id duy nhất toàn cục |
| `governance/blueprint/bp2/00_domain_architecture.md` | doc 11-element mỏng |
| `tools/bp2_domain_check.py` | validator v1.0.0 — SoT path+KEY resolve máy, ENFORCER-MA, PLANNED HONESTY |
| `tests/test_bp2_domain.py` | 15 case (5 positive + 10 mutation) |
| `reports/BP2_REPORT.md` | file này |

## Bảng validation
| Check | Kết quả |
|---|---|
| 13/13 domain block (canon 8 + character/object/dialogue/event + story_planner) | PASS |
| 58 facet_id duy nhất toàn cục — 1 facet đúng 1 domain | PASS |
| 44 facet `exists`: path Test-Path + KEY resolve THẬT bằng máy (bible/37: `tier_1_mandatory.*`, `critical_groups.*`, `modules_v2.character_state`, `balance_targets`; bible/02: `facts/world_rules/permanent_locks/symbols/spoiler_rule`; bible/11: `pillars/variety_rules`; bible/12: `object_library/selection_rules/...`; bible/13: `setting_library/...`; bible/15: `states/state_transitions/profiles/dynamic_fields/artifact_types`; bible/06: `signature_phrases/diction_preferences`; bible/01: hook/cliffhanger/bimodal/reveal_pause/ghost_manifest/negative_space) | PASS |
| 14 facet `planned` đủ 5-metadata, milestone thuộc BP0, planned_path chưa tồn tại | PASS |
| Invariants: enforcer `exists` đều Test-Path (dialog_voice_validator · story_consistency_validator · character_manager · character_balance_report · build_name_pool · svhmp_preflight_qa); enforcer chưa có = planned trung thực | PASS |
| DUP-KEY loader + VERSION khớp checker/BP0 | PASS |

## Bảng mutation (đòn audit báo trước — tự bắn hết)
| Đòn | Kết quả |
|---|---|
| facet 2 domain (nhét facet character sang dialogue) | FAIL đúng ✅ TRUNG 2 domain |
| SoT giả (path không tồn tại) | FAIL đúng ✅ khai lao/phantom |
| SoT key giả (`tier_1_mandatory.khong_co_key_nay`) | FAIL đúng ✅ khai key lao |
| domain canon thiếu block (xóa supernatural) | FAIL đúng ✅ |
| domain thiếu facets (ritual rỗng) | FAIL đúng ✅ |
| invariant trỏ enforcer ma | FAIL đúng ✅ ENFORCER-MA |
| domain lạ (`music`) | FAIL đúng ✅ DOMAIN-LA |
| planned thiếu metadata | FAIL đúng ✅ PLANNED HONESTY |
| dup-key YAML · version lệch | FAIL đúng ✅ |

## Drift check
0 file code domain mới (chỉ 1 validator + 1 test) · 0 content artifact · BP0/BP1 không sửa · bản vá registry chỉ thêm mapping + `bp2_domain: candidate`.

## Known limitations
1. Facet inventory = khởi điểm ĐÓNG cho 13 domain tầng thấp; runtime domains (generator→analytics) chưa có facet block — thuộc pack sau theo chain (BP3+ khi cần ownership).
2. OBSERVATION (không mâu thuẫn cứng, không sửa BP0): `bible/01_narrative_structure.yaml` bản chất là structure kể chuyện — BP2 dùng cho story_planner facets (đúng TASK); trục thời gian thật của timeline vẫn planned (đúng BP0 reason).
3. `key` với ký tự tiếng Việt (`cliffhanger_pool_ngan_lung_triết_lý`) — checker resolve OK (UTF-8), lưu ý khi grep tay.
4. 14 facet planned đều neo bible/38-43 đề xuất — đổi số khi Mr.Long đặt tên khác (rẻ, metadata).

## Next recommendation
Audit 7 bước → Mr.Long ký lock BP2 (`bp2-domain-v1.0`) → theo MASTER chain tự chạy `TASK_BP3_OWNERSHIP` (facet inventory 58 đã sẵn làm input cho ownership matrix 1-facet-1-writer).

Final status: **READY_FOR_AUDIT**
