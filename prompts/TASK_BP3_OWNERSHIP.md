# TASK BP3 — OWNERSHIP + DEPENDENCY (theo BP_PIPELINE_MASTER.md)

## MISSION
Ma trận sở hữu FACET máy-kiểm-được: trả lời "Emotion ai own?" bằng máy, không bằng tranh luận.
**LUẬT VÀNG: 1 facet = ĐÚNG 1 writer-domain** (mirror "bible writer = mr_long").

## DELIVERABLES
1. `governance/blueprint/bp3/facet_ownership_matrix.yaml` (deliverable hoãn từ BP1):
   validator_version · source_constitution_version · facets[]: facet_id (PHẢI tồn tại trong
   bp2/domain_specs.yaml — drift = FAIL) · owning_domain · readable_by[] · writable_by[]
   (⊆ {owning_domain, mr_long}) · forbidden_writers[] · lifecycle · owner_artifact.
2. `governance/blueprint/bp3/dependency_detail.yaml` — vì SAO từng dep tồn tại (dep_id ·
   from · to · reason 1 dòng · data_flow read|write) — NHẤT QUÁN với blueprint_domains
   dependencies + bp1 dependency_graph (3 nguồn phải khớp, lệch = FAIL).
3. `governance/blueprint/bp3/00_ownership.md` (11-element).
4. Validator: 1-facet-1-writer · facet_id khớp BP2 · readable/writable chỉ chứa domain đã khai ·
   dep 3-nguồn-khớp · writable ngoài owner = FAIL.
5. Negative test: facet 2 writer → FAIL · facet ma (không có trong BP2) → FAIL ·
   writable_by chứa domain lạ → FAIL · dep lệch blueprint_domains → FAIL.

## GHI CHÚ NGỮ NGHĨA (đã phán quyết, không mở lại)
Emotion: owner=character; dialogue/story_planner/decision_engine = read-only.
Bible files: writer duy nhất = mr_long. Narration = facet của dialogue.

## MUTATION AUDIT SẼ BẮN
2-writer · facet ma · dep 3-nguồn lệch · writable leo thang · matrix thiếu facet BP2 đã khai.
STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.
