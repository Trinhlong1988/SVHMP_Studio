# SVHMP Studio — Hắc Dạ Ký

Vietnamese narrative horror audiobook pipeline (IndexTTS2 + BigVGAN + bible-driven QA).

- **Channel**: **Hắc Dạ Ký** (`@hacdaky`) — chuyện kể từ cõi vô hình
- **Series 1**: "Chuyến xe cuối cùng về đâu" (90 EPs planned)
- **Latest**: Round 20.3 (2026-07-01) — R199 tail pathology hardlock + A/B test

## Session-start protocol cho CMD Claude mới

**BẮT BUỘC** theo đúng thứ tự. Không skip, không đảo.

1. **Clone** — `git clone https://github.com/Trinhlong1988/SVHMP_Studio.git`
2. **`ONBOARDING.md`** — 516 lines. Full context: R_SUPREME governance, TTS params, spec structure, backup chain.
3. **`CLAUDE.md`** — TỐI THƯỢNG (R_SUPREME + R196/R197/R198/R199) + session start protocol.
4. **`bible/00_constitution.yaml`** — R_SUPREME R1-R10 + R40-R199 (60+ rules).
5. **`BUGS_FIXED.md`** — B1-B40 bug catalog trước khi touch code.
6. **`VERSION.md`** — so last_known_version, mismatch → re-read changed artifacts.
7. **Memory** (nếu chạy trên máy Mr.Long): `C:\Users\Administrator\.claude\projects\C--Users-Administrator\memory\MEMORY.md`.

## Voice sample (checked into repo)

- **Path**: `assets/voice_samples/NNG_narration_sample_19062026.wav`
- **Size**: 1.08 MB, 22050 Hz mono, 13.52s
- **SHA256**: `e38fc1b5ad4ede27178c05ef7537edad3b4e71ff5baa9d92cedcc87fa57cd77c`
- **Purpose**: Voice reference for IndexTTS2 zero-shot cloning (narrator anonymous Hắc Dạ Ký storyteller)
- **Referenced by**: All 6 spec files `output/ep_01/sections/spec_*.json` field `sample_prompt`

Note: **Không dùng "Khánh An"** — legacy anchor name đã disabled từ v13b + delete session 1/7.

## Quick reference

| What | Where |
|---|---|
| TTS render entry | `tools/svhmp_v13_render.py` |
| Spec files EP01 | `output/ep_01/sections/spec_*.json` (6 sections, 193 chunks) |
| SSOT episode text | `output/ep_01/episode.md` |
| Voice sample ref | `assets/voice_samples/NNG_narration_sample_19062026.wav` |
| R198 cap_peak hardlock | `tools/cap_peak.py` |
| R197 FULL_TEXT_GATE | `tools/svhmp_preflight_qa.py` |
| R199 tail trim v1 vs v2 | `tools/ab_test_tail_trim_v1_vs_v2.py` |
| Voice QA suite | `tools/qa_boundary_artifact.py`, `qa_breath_artifact.py`, `qa_prosody_collapse.py`, `qa_onset_artifact.py`, `qa_dialogue_identity.py` |
| Audit reports | `runtime/audits/*.md`, `*.json` |

## Environment (máy Mr.Long)

| Component | Path |
|---|---|
| IndexTTS2 code | `~/index-tts/` (upstream `github.com/index-tts/index-tts`) |
| Vietnamese weights | `~/index-tts/checkpoints-vi/` (dinhthuan HuggingFace) |
| Python venv | `~/index-tts/.venv/Scripts/python.exe` |
| Env var required | `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` |
| Working directory | `~/index-tts` (khi run render) |

## TTS params LOCKED

```python
GEN_KWARGS = {
    'do_sample': True,
    'top_p': 0.5, 'top_k': 5, 'temperature': 0.3,
    'length_penalty': 1.0,
    'num_beams': 5, 'repetition_penalty': 10.0,   # DEFEND — rp<10 gây silent overgenerate 20s trail
    'max_mel_tokens': 1500,   # limit runaway (case #2 R199)
}
emo_alpha = 0.65
interval_silence = 200
max_text_tokens_per_segment = 400
seed = 42 + chunk_index   # session 1/7 change (chống robotic onset)
USE_ANCHOR = False        # narrator Hắc Dạ Ký anonymous
```

## R_SUPREME cheatsheet

- **R1** No autonomous action | **R2** Permission first (4 Q) | **R3** PV mode: render/QA/reports ONLY
- **R4** Bug class extend > create | **R5** User bug = process failure → analyze first, fix later
- **R6** PASS declaration qualify | **R7** Read→Diff→Proposal→Approval→Backup→Patch→Regression→Production
- **R8** Baseline protection | **R9** Evidence first | **R10** Uncertainty → STOP

**Mr.Long = ONLY authority. Claude = Engineering Executor NOT autonomous.**

## R199 tail pathology (session 1/7 — codified 09:00)

3 case tail artifact:
- **#1** Đuôi rác burst -21 dB after ~0.5s silence gap (6 legacy hits)
- **#2** Runaway generation 20-30s silent trail (T4.B/C AB test confirm)
- **#3** `aggressive_trim_tail(search_ms=600)` structural hole

Fix Tầng 1: `tools/ab_test_tail_trim_v1_vs_v2.py`
- v2 = full-scan + gap qualifier + main voice run detection
- Regression 8 chunks: 2/2 runaway fixed, 0 over-trim warnings
- PENDING Mr.Long approve → apply v2 to production render script

Full report: `runtime/audits/R199_TAIL_PATHOLOGY_REPORT.md`

## Section tempo profile (session 1/7)

| Section | Narration | Dialogue |
|---|---|---|
| HOOK (Tò Mò) | 0.97 | 0.97 |
| SETUP (Bất An) | 1.00 | 1.00 |
| INCIDENT (Đồng Cảm) | 1.00 | 1.03 |
| REVEAL (Nghẹn) | 0.97 | 0.97 |
| PAYOFF (Dư Âm) | 0.95 | 0.95 |
| CLIFFHANGER (Cycle Horror) | 0.92 | 0.92 |

## EP01 chunks per section (post-1/7 merge)

| Section | Chunks | Pause range | Dialogue |
|---|---|---|---|
| HOOK | 13 | 1500ms | 0 |
| SETUP | 36 | 1200–1500 | 0 |
| INCIDENT | 44 | 300–1800 | 20 |
| REVEAL | 51 | 300–1500 | 18 |
| PAYOFF | 30 | 1500–2000 | 2 |
| CLIFFHANGER | 19 | 500–2800 | 1 |
| **TOTAL** | **193** | | 41 |

## Multi-CMD realtime sync protocol

CMD khác pull + push → em phải rebase, không được force push. Workflow:

```bash
# Trước khi work
git pull --rebase origin main

# Sau khi commit
git push origin main
# → nếu bị reject: git pull --rebase → resolve conflict → push lại
```

Conflict resolution theo baseline lock R8 — bên nào có evidence rõ hơn thắng, KHÔNG guess.

## Latest release history

- **Round 20.3 (1/7)** — R199 tail pathology + A/B test v1 vs v2 tail trim
- **Round 20.2 (1/7)** — Voice sample checked into repo + relative path
- **Round 20.1 (1/7)** — Spec rebuild v2 + AB tests + ONBOARDING doc
- **Round 19.34 (30/6)** — R198 cap_peak wire vào svhmp_v13_render

Old README (Phase 1 architecture 2026-06-19): `LEGACY_README_2026_06_19.md`.

## License

Private repo. Contact Mr.Long (`Trinhlong1988`) for access.
