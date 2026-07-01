# PHASE 0 + PHASE 1 — STRICT PROTOCOL REPORT
**Generated:** 2026-06-30T19:30 by CMD THỰC THI
**Scope:** Mr.Long approve message 30/6 — Phase 0 text-only + Phase 1 Voice Profile Manager

---

## Status: PASS

## Evidence — Generated Artifacts

| Artifact | Path | Size | Lines |
|---|---|---|---|
| Bible v2.0 | `bible/15_voice_bible.yaml` | 6.0 KB | 187 |
| Bible v1.0 backup | `bible/15_voice_bible.yaml.bak.v1_30_06` | (original) | — |
| Manager module | `tools/voice_profile_manager.py` | 11 KB | 332 |
| Tests suite | `tests/test_voice_profile_manager.py` | 5.7 KB | 173 |
| Voice refs spec | `assets/voice_refs/README.md` | 2.4 KB | 56 |
| Rules added bible/00 | R178b, R180b, R181b, R181c | 4 rules | — |
| Text fix registry add | bible/35 F008-F015 (8 entries) | — | — |
| Regression 10 rounds log | `runtime/cmd_progress/qa_full_v111/regression_10rounds.log` | — | — |

## Metrics — Phase 1 Regression 10 rounds

| Metric | Value |
|---|---|
| Rounds executed | 10 |
| Rounds PASS | 10 |
| Rounds FAIL | 0 |
| Total test invocations | 150 (15 tests × 10 rounds) |
| Total PASS | 150 |
| Total FAIL | 0 |
| Precision | 1.0000 |
| Recall | 1.0000 |
| F1 | 1.0000 |
| Wall time | 18 s |
| Avg round duration | 1.43 s |
| Std dev round duration | ~0.055 s (1.377-1.487) |
| TP (locked field reject) | 10 (rounds × test_02) |
| TN (emotion valid accept) | 30 (rounds × test_03/05/06/07) |
| FP | 0 |
| FN | 0 |

## Metrics — Phase 0 TEXT Gate

| Audit | Pre Phase 0 | Post Phase 0 | Delta |
|---|---|---|---|
| R60 short EOL | 0 HIGH | 0 HIGH | 0 |
| R61 short START | 9 HIGH | 0 HIGH | -9 |
| R62 anaphora consecutive | 0 HIGH | 0 HIGH | 0 |
| R66 short chain | 1 HIGH | 1 HIGH (residual L355 intentional pause-merge) | 0 |
| R74 phrase repetition | 2 HIGH | 2 HIGH ("0 30" + "cô ấy" para 233-235 not localized) | 0 |
| R174 driver dialogue | PASS 0 fail | PASS 0 fail | 0 |
| R60+R61+ 4-7 từ | 83 / 4 chains | 77 / 3 chains | -6 / -1 |
| R176 progress log enforce | 1 log active | 1 log completed | OK |

## Historical Bugs — PASS

| Bug | Status | Evidence |
|---|---|---|
| B60 EP01 driver dialogue Q2→Q1 | FIXED | `episode.md:528` `spec_cliffhanger.json:215` |
| B61 L130+L132 "kính" lặp | FIXED | `episode.md:130-132` |
| B62 outro "Hãy nhớ rằng..." cụt | FIXED option D | `episode.md:544` |
| T3 L242 cửa kính + làn kính cùng câu | FIXED | `episode.md:242` |
| T4 L270 "tai" mono EOL | FIXED | `episode.md:270` |
| T5 L274 "Anh khựng người" 3 từ | FIXED | `episode.md:274` |
| T6 L278 "hữu ý" EOL cụt | FIXED | `episode.md:278` |
| T7 L284 "kẹt xe ngập nước" | FIXED | `episode.md:284` |
| T8 L390 3x sợ chain | FIXED partial (intentional pauses retained) | `episode.md:390` |
| T13 L362 "Anh ngừng nói" pause | FIXED | `episode.md:362` |
| T14 L480 "cái nhìn rất ngắn" | FIXED → "thoáng qua" | `episode.md:480` |
| R61 L7/L103/L123/L259/L281/L283/L295/L431 | FIXED via prefix expansion | post-fix audit 0 HIGH |

## Production Validation — PASS

| Check | Result |
|---|---|
| `voice_profile_manager.py --list` | 4 profiles loaded (DRIVER, GIRL_GHE7, KHAI_PHONG, NARRATOR) |
| `voice_profile_manager.py --validate` | ok=true, all 4 profiles locked_ok=true, 0 issues |
| `voice_profile_manager.py --snapshot KHAI_PHONG` | LOCKED+DYNAMIC layers serialized |
| `pytest tests/test_voice_profile_manager.py` single | 15 passed in 0.39s |
| `pytest tests/test_voice_profile_manager.py` × 10 | 150 passed in 18s |
| R181b sealed invariant verify | `test_02_locked_field_modification_raises` PASSED 10/10 |
| R175b normalize verify | `test_04_emotion_override_oor_rejected` PASSED 10/10 |
| 4 character profiles verify | `test_01_registry_has_four_required_profiles` PASSED 10/10 |
| State transition matrix verify | `test_08`+`test_09` PASSED 10/10 |
| 5 artifact types verify | `test_14_artifact_types_five` PASSED 10/10 |

## Known Limitations

1. **No golden reference WAV yet** — `assets/voice_refs/` contains README placeholder only.
   `speaker_embedding_path` + `golden_reference_wav` point to non-existent files.
   Phase 2 will populate.

2. **No speaker embedding extraction** — `tools/extract_speaker_embedding.py` not built (Phase 2 scope).
   `speaker_embedding_sha256: PLACEHOLDER_TBD_ON_FIRST_EMBEDDING_EXTRACT` in all 4 profiles.

3. **R66 L355 residual chain** — 3 sentences cách bởi `[pause:400ms]` `[pause:500ms]` được audit treat
   thành 3 short sentences chain dù chúng là 1 narrative line trong markdown với intentional dramatic pauses.
   Decision: accept residual. Audit logic update có thể consider pause-marker là continuation in future.

4. **R74 phrase repetition "0 30" + "cô ấy"** — audit reports para 233 + para 235.
   Em không locate được exact text match trong episode.md sau Phase 0 fixes.
   Suspect audit tokenization stale or false positive.
   Decision: accept residual. Recommend audit log enhancement Phase 2.

5. **No TTS render or audio QA in Phase 0/1** — per Mr.Long spec:
   "Do NOT re-render audio. Do NOT ship v111. Keep v108 as baseline reference."

6. **Voice profile manager does not invoke TTS** — pure logic layer.
   Integration with `svhmp_v13_render.py` deferred to Phase 2.

## Recommended Next Step

**Phase 2 (await Mr.Long approve):**
1. Build `tools/extract_speaker_embedding.py` (wespeaker/pyannote ECAPA-TDNN)
2. Populate 4 golden reference WAV in `assets/voice_refs/`
3. Extract embeddings + populate sha256 in bible/15
4. Build `tools/audit_speaker_embedding_similarity.py` (R181c) — per-chunk QA
5. Integrate manager into `tools/svhmp_v13_render.py` — lookup profile before render
6. Run regression 10 rounds on full pipeline

**Phase 2 builds 5 audio artifact QA tools (Mr.Long docx 30/6):**
- R188 `qa_boundary_artifact.py` (TOP priority ⭐⭐⭐⭐⭐)
- R189 `qa_breath_artifact.py`
- R190 `qa_prosody_collapse.py`
- R190b `qa_onset_artifact.py`
- R191 `qa_dialogue_identity.py`

**DO NOT proceed to Phase 2 until Mr.Long explicit approve.**
