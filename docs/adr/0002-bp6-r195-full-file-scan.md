# ADR-0002: R195 anti-hardcode scan toan file thay vi tung knob rieng le

**Status:** Accepted (theo lenh Mr.Long 4/7/2026, commit `660e4bd`)
**Date:** 2026-07-04

## Boi canh

BP6 `decision_contract.yaml` dinh nghia 12 "knob" (thong so dieu khien sinh noi
dung) — luat R195 cam so (int/float) hardcode nam ngoai `valid_range`, bat buoc moi
so phai duoc calibrate tu du lieu golden thay vi ghi cung trong contract.

`tools/bp6_decision_check.py` ban dau chi goi ham quet `_numeric_leaks()` **tren
tung dict knob rieng le** (`_numeric_leaks(k, kid)` cho moi `k` trong `knobs[]`).
Deep-audit 4/7 phat hien: cach nay bo sot HOAN TOAN so hardcode nam **ngoai** danh
sach `knobs[]` — vi du trong `meta`, `rules`, hoac bat ky section moi nao them sau
nay. Day la lo hong that (khong phai gia thuyet): file `decision_io.yaml` (schema
thuan, dung ke cho `io`) truoc do **khong duoc quet chut nao**, nen so hardcode co
the lot 100% qua gate ma khong ai biet.

## Quyet dinh

Doi `_numeric_leaks()` sang goi **tu document root** (`contract` toan bo, khong
phai tung `k`), quet **de quy toan bo cay** — bat ca so nam trong `knobs[]` LAN
`meta`/`rules`/section tuong lai. Ap dung tuong tu cho `decision_io.yaml` voi
`allowed_keys=set()` (schema thuan, **0 so duoc phep** o bat ky dau, khac voi
`contract` cho phep so duoi `valid_range`).

## He qua

- Tich cuc: dong hoan toan lo hong "chi quet trong pham vi da biet truoc" — bat ke
  ai them section moi vao 2 file BP6 sau nay, R195 van bat duoc so hardcode lac cho
  ngay tu lan chay dau, khong can nho cap nhat danh sach quet.
- Bai hoc tong quat (ap dung ca noi khac trong repo, xem `docs/ENVIRONMENT_GOTCHAS.md`
  G8 — cung tinh than): **tool quet-vi-pham quet theo "vi tri da biet" se luon bo sot
  vi tri moi phat sinh** — nen quet tu goc cay/toan file, roi loai tru CO CHU DICH
  (allowlist ro rang), thay vi liet ke "cho can quet" roi hy vong danh sach do day du.
- Khong lam thay doi 12-knob hien co hay valid_range da khai — thuan tuy sua PHAM VI
  quet, khong sua schema/logic nghiep vu.
