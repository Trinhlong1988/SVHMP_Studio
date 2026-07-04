# ADR-0001: Co che PACK CLAIM chong 2 builder cung xay 1 pack

**Status:** Accepted (Mr.Long ky 4/7/2026, MASTER luat 11)
**Date:** 2026-07-04

## Boi canh

Nhieu phien Claude Code (CMD_BUILD, G2_EXECUTOR, kiem duyet...) chay song song tren
cung 1 repo, khong thay nhau (moi phien = terminal rieng). Truoc khi co co che nay,
xay ra 2 va cham that trong 3-4/7:
- **BP6 ban A vs ban B**: 2 phien cung build `bp6_decision` doc lap, ra 2 ket qua
  khac nhau, phai trong tai thu cong (Mr.Long chon ban A, luu ban B lam tham khao).
- **G2 flip-ceremony C5**: tuong tu, 2 huong xu ly cung 1 pack xung dot nhau.

Khong co ledger dung chung nao de 1 phien biet pack minh sap dong da co nguoi giu
chua — chi co the phat hien SAU khi da lam xong va dam nhau.

## Quyet dinh

Them `tools/build_claim.py` (`claim` / `release` / `status`) + ledger
`runtime/build_claim.yaml` (**co track git**, khong phai file cuc bo per-may):
- Truoc khi dong bat ky file nao trong 1 pack: `claim <pack_id> <session>` — exit 0
  moi duoc lam, exit 1 = pack co chu, di viec khac.
- Sau khi push verified: `release <pack_id> <session>`.
- Claim/release PHAI commit+push NGAY (khong de local) de phien khac thay qua git.
- Re-claim cung ten session = idempotent (khong chan) — nhung 2 INSTANCE that dung
  chung 1 ten session van co the dam nhau (da xay ra 1 lan, xem BUGS_FIXED tuong ung).

## He qua

- Tich cuc: tu 4/7 tro di, moi lan claim/release deu co dau vet git (thoi gian,
  session, trang thai) — kiem duyet doi chieu duoc, khong con va cham am tham.
- Con no: co che moi chan "2 nguoi giua 1 pack", CHUA chan "build pack N+1 truoc khi
  pack N duoc Mr.Long LOCK chinh thuc" (nghi thuc chuoi MASTER) — ghi trong
  `docs/ENVIRONMENT_GOTCHAS.md` G6, chua co enforcer may tu dong.
- Xung dot con lai (nhieu phien cung sua `runtime/build_claim.yaml` gan nhau ve thoi
  gian) van phai resolve tay khi rebase — quy uoc: giu CA HAI khoi, uu tien
  `status: released` khi lech trang thai giua 2 ban.
