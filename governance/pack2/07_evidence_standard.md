# PACK 2 — 07_evidence_standard.md
> Enforce: output `tools/auditor.py` · Boss rule: "cấm báo cáo láo khi chưa show pass/fail".

## Mọi report BẮT BUỘC có (thiếu 1 = VÔ HIỆU)
1. **Commit hash** (`git rev-parse HEAD`)
2. **Branch**
3. **Commands executed** (lệnh thật)
4. **PASS/FAIL matrix** (từng gate + exit code)
5. **Final verdict** (SHIP/BLOCK_SHIP)
6. **Exit code**

## Cấp độ bằng chứng (mạnh → yếu)
`exit code máy` > `output lệnh + hash` > `log_ping/commit` > lời nói (KHÔNG chấp nhận đứng một mình).

## Nguồn phát chuẩn
`python tools/auditor.py` in đủ 6 trường trên. Report của Builder phải **dán nguyên** output này, không tóm tắt bịa.
