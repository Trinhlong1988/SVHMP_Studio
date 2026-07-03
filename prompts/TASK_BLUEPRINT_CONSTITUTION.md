# TASK: Build SYSTEM_BLUEPRINT_CONSTITUTION v1.0 (BP-C — Mr.Long duyệt 3/7)

Repo: SVHMP_Studio · Governance v1.0 LOCKED · Roadmap: `governance/master_roadmap.md` (phương án mới 3/7).

## ROLE: CMD_BUILD only
**MUST NOT:** self-PASS · self-FREEZE · tạo tag · đổi promotion_status→locked · sửa semantics P1-P5 đã lock · bypass registry/test · audit trên dirty tree · **tạo stub/vaporware để qua test**.
**MAY:** thêm doc blueprint mới · registry/file_index/manifest entry cho file blueprint · tool/test validate blueprint.

## GOAL
Tạo bộ LUẬT quy định SYSTEM_BLUEPRINT v1.0 phải được xây + audit thế nào (chưa xây bản vẽ — đó là phase BP sau khi BP-C freeze).

## DELIVERABLES
- `governance/blueprint/00_system_blueprint_constitution.md`
- `governance/blueprint/01_required_documents.md`  (danh mục ~20 doc phase BP phải sinh)
- `governance/blueprint/02_domain_contract.md`
- `governance/blueprint/03_dependency_rules.md`
- `governance/blueprint/04_blueprint_audit_gate.md`
- `tools/blueprint_constitution_check.py` + `tests/test_blueprint_constitution.py`
- registry/file_index/manifest entries (giữ 0/0/0)

## DOMAIN INVENTORY — KHOÁ TRƯỚC (bước 1, trước mọi thiết kế manager)
Character · Dialogue · World · Timeline · Event · **Supernatural (độc lập — CẤM giấu trong World/Event/StoryPlanner)** · Culture · Belief · Ritual · Location · Weather · Memory · Story Planner · Generator · QA Runtime · TTS · Audio · Video · Publisher.

## MỖI DOMAIN CONTRACT PHẢI ĐỊNH NGHĨA (12 mục)
responsibility · non-responsibility · source-of-truth · manager · schema · validator · reader · writer · lifecycle · dependencies · forbidden dependencies · audit rule.

## MEMORY RULE — memory phải có owner + scope
global · series · episode · character · event · supernatural.

## ⚠️ QUY TẮC CHỐNG LẶP LỖI (bắt buộc — từ bài học pack4/hook-env)
1. **exists | planned:** mọi manager/schema/validator trong contract khai status.
   `blueprint_constitution_check.py` FAIL khi khai `exists` mà path KHÔNG tồn tại (khai láo);
   KHÔNG FAIL vì `planned` (Video/Publisher/StoryPlanner... chưa có code — khai planned là trung thực).
2. **RECONCILE — KHÔNG REBUILD:** Character (bible/37 + character_manager wired render + R205/R206)
   và QA Runtime (pack5: R188-191, waiver, watch) ĐÃ TỒN TẠI — contract phải TRỎ tới chúng
   (exists), luật G2/G8 = audit + vá gap. Cấm nhân đôi module (01_builder Forbidden).
3. **DOC BAR:** 5 doc đủ 11-element + 0 placeholder (TODO/TBD/FIXME/DRAFT).
   `test_blueprint_constitution.py` enforce như khuôn `test_pack5_docs.py`
   (exist+nonempty · 11-element · no-placeholder · reference-real-enforcer).
4. **R200:** commit qua worktree riêng · pull --rebase trước · log_ping + push sau · KHÔNG --no-verify.
5. Test spawn git (nếu có) PHẢI scrub env `GIT_*` (lesson hook-env 2/7; conftest đã miễn dịch toàn cục — không được gỡ).

## NEGATIVE TESTS bắt buộc (behavioral, không chỉ text-check)
missing required domain → FAIL · khai exists-láo → FAIL · missing schema/validator (khai exists) → FAIL ·
wrong dependency direction → FAIL · Supernatural gộp vào World → FAIL · Memory không owner → FAIL ·
candidate tự-lock → FAIL (promotion_guard đã chặn — test trỏ tới nó) · missing audit gate → FAIL.

## PROMOTION
Blueprint Constitution = `candidate`. Builder KHÔNG lock/tag — Mr.Long ký sau audit adversarial của kiểm duyệt.

## VERIFICATION (dán lệnh + exit-code + tail)
```
python tools/architecture_registry_check.py            # 0/0/0
python tools/blueprint_constitution_check.py           # exit 0
python -m pytest tests/ -q                             # all pass
python tools/cmd_pipeline_gate.py --ref origin/main --skip-build
# Kỳ vọng ARCH + QA PASS. (RELEASE chấm pack đã lock — không áp blueprint candidate.)
```

## OUTPUT — Builder Report
commit hash · branch · changed files · commands + exact output + exit codes · registry summary ·
tests summary · known limitations · risks. Ký `reports/build_report.md` (local, không commit).
Dòng cuối duy nhất: `READY FOR AUDIT = YES` hoặc `READY FOR AUDIT = NO`.
