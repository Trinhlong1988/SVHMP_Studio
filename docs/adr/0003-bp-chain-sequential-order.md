# ADR-0003: Thu tu tuan tu BP0-BP9 (khong build song song giua cac tang)

**Status:** Accepted (Mr.Long duyet 3/7/2026, `governance/master_roadmap.md`)
**Date:** 2026-07-04

## Boi canh

Truoc BP-chain, du an tung "phinh huu co" — nhieu the he `audit_*`/`auto_fix_*`/
`rewrite_ep*`/`qa_*` code truoc, quan ly sau, dan den 186 file UNMAPPED (deep-audit
2/7) vi khong co Tier-0 governance lam nen truoc khi xay domain. Rui ro goc: "code
truoc, quan sau" lam mat source-of-truth, de trung module.

Blueprint duoc chia thanh 9+1 tang (BP0 Constitution -> BP1 Core Architecture ->
BP2 Domain -> BP3 Ownership -> BP4 Runtime -> BP5 Validation -> BP6 Decision ->
BP7 Narrative -> BP8 Production -> BP9 Compliance), moi tang co checker rieng
(`tools/bpN_*_check.py`) va phai duoc Mr.Long **lock** (promotion_status: locked +
tag `bpN-*-v1.0`) truoc khi tang ke tiep chinh thuc bat dau.

## Quyet dinh

Xay TUAN TU theo dependency that giua cac tang (khong phai thu tu tuy chon):
- BP1 (kien truc/graph/interface) phai xong truoc vi moi tang sau deu tham chieu
  domain/interface da khai o day.
- BP2 (domain/facet registry) dua tren BP1 (graph domain), BP3 (ownership matrix)
  dua tren BP2 (coverage facet 2 chieu) — sai thu tu se khong co gi de doi chieu.
- BP4 (runtime/event/state-machine) dua tren BP2+BP3 (hop phai la domain/facet da
  khai, memory scope khop owner BP3).
- BP5 (validation suite) la "1 cua" GOI lai bp0-bp4 — bat buoc bp0-bp4 phai co
  TRUOC de goi, khong the lam song song.
- BP6 (decision knobs) -> BP7 (narrative) -> BP8 (production) -> BP9 (compliance):
  moi tang tieu thu dau ra tang truoc (decision dieu khien narrative, narrative la
  input production, production la doi tuong compliance kiem duyet truoc xuat ban) —
  dao thu tu se tao ra tang sau khong co gi de kiem/dieu khien.
- Nghi thuc: pack N+1 chi duoc claim/build SAU KHI pack N co chu ky Mr.Long
  (promotion_status: locked). Vi pham nghi thuc nay (build truoc khi pack truoc
  duoc khoa) da tung xay ra 1 lan (BP7 claim khi BP6 con `candidate`) — khong phai
  va cham (khong ai tranh), nhung lech quy trinh, ghi nhan tai
  `docs/ENVIRONMENT_GOTCHAS.md` G6.

## He qua

- Tich cuc: tu BP1 den BP9, moi tang deu co checker + test mutation rieng, audit
  0 MISSING/DUP/UNMAPPED lien tuc — khong con lap lai kieu "186 file unmapped" nhu
  truoc BP-chain.
- Chi phi: thu tu tuan tu cham hon build song song tu do, nhung doi lai moi tang co
  nen tang chac de doi chieu (BP3 doi chieu duoc BP2, BP4 doi chieu duoc BP2+BP3...).
  Amendment khi con `candidate` la re; sua sau khi da `locked` dat hon nhieu (bai hoc
  BP-C: 1 vong audit truoc khi lock bat duoc ca Decision Layer/Lifecycle thieu).
- Con no: G6 (chan build-truoc-khi-pack-truoc-duoc-khoa) hien chi la ky luat tu giac
  cua nguoi/session, chua co `build_claim.py` tu dong kiem "pack lien truoc trong
  chuoi MASTER da locked chua" truoc khi cho claim pack ke tiep.
