# BÁO CÁO HỆ THỐNG NHÂN VẬT SVHMP — "Tất cả về một con người"
_Lập 2026-07-01 · nền tảng cho phương án định danh nhân vật · số liệu từ `tools/character_manager.py --report` (không suy luận)_

---

## PHẦN A — HIỆN TRẠNG (bằng chứng, không suy luận)

### A1. Số lượng nhân vật — ĐÃ KHOÁ CHƯA?
| Nhóm | Số | Khoá? | Nguồn |
|---|---|---|---|
| Recurring (Bác tài + Nam) | 2 | ✅ KHOÁ | `bible/03` `no_other_recurring_characters: true` |
| Hành khách one-shot (roster) | 100 | ✅ framework_lock | `runtime/passenger_roster_100.yaml` |
| — gán tập | 88 (ep 2–89, trừ 73/90) | ✅ | `gen_100_passenger.assign_eps` |
| — spare backup | 12 | ✅ | `spare_pool` |
| **Nhân vật PHỤ trong mỗi truyện** (mẹ, người yêu, con, đồng nghiệp…) | **KHÔNG đếm / KHÔNG quản lý** | ❌ **HỞ** | — |

→ **Khoá NHÂN VẬT CHÍNH (protagonist-of-the-week), CHƯA khoá dàn phụ.** Mỗi tập Generator tự đẻ nhân vật phụ → nguy cơ trùng tên/mâu thuẫn/không nhất quán xuyên series.

### A2. Cân bằng / logic xuyên suốt?
| Trục | Phân bố thực | Đánh giá |
|---|---|---|
| Regret pillar | 32/24/20/14/10 | ✅ cân bằng (khoá bible/11) |
| Giới tính | nu 50 / nam 50 | ✅ cân bằng |
| Tuổi | 18-25=**29**, 26-35=27, 36-50=24, 51-65=14, **66+=6**, **<18 = 0** | ❌ LỆCH TRẺ + **thiếu trẻ em & người già** |
| Vùng miền/giọng | 100× chưa set | ❌ trống → dialogue **1 giọng đơn điệu** |
| Kiểu cái chết | không catalog | ❌ nguy cơ lặp |
| Hôn nhân / nghề / bối cảnh-thời điểm | không kiểm soát phân bố | ❌ chưa cân |
| Novelty regret (khoảng cách 6) | có, nhưng có window-warning | ⚠️ giới hạn rotation |

### A3. Gương mặt có ÁM ẢNH chưa?
**CHƯA.** `completeness = 0.0` — cả 100 hành khách **chưa có 1 trường ngoại hình/gương mặt/chi tiết ám ảnh nào**. Hiện chỉ là *tên + loại nuối tiếc + món đồ*. Với thể loại kinh dị, **ám ảnh = 1 chi tiết cụ thể, dị thường, lặp lại** (vd: người phụ nữ luôn vặn chiếc đồng hồ đã chết máy). Trường này **chưa tồn tại** → nhân vật đang "vô diện".

---

## PHẦN B — SCHEMA "TẤT CẢ VỀ MỘT CON NGƯỜI" (nghiên cứu sâu, tái dùng dự án khác)

Thiết kế **2 lớp** để vừa hợp SVHMP vừa mở rộng dự án khác:
- **LỚP LÕI (universal human)** — dùng cho MỌI dự án kể chuyện.
- **LỚP PHỦ (narrative overlay)** — riêng SVHMP (regret/chuyến xe).

### B1. Lớp LÕI — 7 chiều (nền tảng tài liệu)
| # | Chiều | Trường | Nền tài liệu |
|---|---|---|---|
| 1 | **Định danh** | id, tên, ngày sinh, tuổi chính xác, nhóm tuổi, giới, **sống/đã mất**, quê quán, nơi ở, dân tộc | hồ sơ nhân vật (character dossier) |
| 2 | **Thân thể** | vóc dáng, chiều cao, **màu da**, **tóc (dài/ngắn, màu, kiểu)**, **gương mặt (mắt, lông mày, má lúm đồng tiền, sẹo/nốt đặc biệt)**, xinh/xấu, sức khoẻ/khuyết tật, **HAUNTING_SIGNATURE (chi tiết ám ảnh)** | nguyên tắc "telling detail" trong kinh dị |
| 3 | **Trang phục/vật** | thường phục, **bộ đồ lúc chết**, giày dép, mũ, **trang sức**, món đồ biểu tượng | bible/12 object_library |
| 4 | **Tâm lý** | Big Five (O-C-E-A-N), khí chất, **sở trường**, **sở đoản/tật xấu**, sở thích, giá trị sống, nỗi sợ, **Muốn (Want) vs Cần (Need)**, **Vết thương/Ghost + Niềm tin sai/Lie** | Big Five (OCEAN); K.M. Weiland Ghost→Lie→Want→Need; Negative Trait Thesaurus |
| 5 | **Giọng & Đối thoại** ⭐ | **vùng giọng (Bắc/Trung/Nam+phụ)**, **xưng hô**, tiểu từ cuối câu (nhé/nghen/hỉ…), register (trang trọng/dân dã/suồng sã), từ địa phương, học vấn→độ phức tạp từ, tật nói, câu cửa miệng, tốc độ, ref mẫu giọng TTS | ngôn ngữ học xã hội; Proust questionnaire (voice) |
| 6 | **Nền tảng xã hội** | nghề nghiệp, học vấn/trường, giai tầng, **hôn nhân**, tôn giáo, cấu trúc gia đình | sociology of character |
| 7 | **Quan hệ** | đồ thị quan hệ (họ hàng/bạn/đồng nghiệp/kẻ thù) + trạng thái | relationship map (bible/03 đã dùng cho Nam) |

### B2. Lớp PHỦ — SVHMP narrative
regret pillar + sub_archetype + regret_label · **nỗi đau (pain)** · **cái chết (type/thời điểm/nơi)** · signature_setting · **bối cảnh–thời điểm–hoàn cảnh** · arc/reveal · novelty_hash · assigned_ep · vai (chính/phụ) · status.

### B3. Vì sao GIỌNG gắn QUÊ HƯƠNG là "cực kỳ quan trọng" (Boss đúng)
Tiếng Việt 3 vùng khác **từ vựng + tiểu từ + xưng hô** (không chỉ accent): _má/mẹ_, _chén/bát_, _vô/vào_, _nghen/nhé/hỉ_, _tui/tôi/tao_. Nhân vật quê Huế nói khác người Sài Gòn. **Không khoá quê → dialogue giả, lệch vai.** ⇒ trường `voice.hometown + region_dialect + pronoun_system + particles` phải set TRƯỚC khi sinh thoại.

---

## PHẦN C — ĐÃ XÂY (code, chạy được)
`tools/character_manager.py` — class `CharacterProfile` + `VoiceProfile` + `CharacterRegistry`:
- Load 100 passenger + 2 recurring, **tái dùng** roster + bible/03 + bible/23 (KHÔNG đẻ lại tên).
- `get/filter/by_ep/distribution/validate_names/enrich/completeness_report/save_enriched`.
- CLI `--report / --completeness / --char <id>`. Đã cho số liệu Phần A.

---

## PHẦN D — PHƯƠNG ÁN (đề xuất, chờ Boss duyệt — R1 Mr.Long authority)

| Phase | Việc | Ra sản phẩm |
|---|---|---|
| **1. Khoá schema** | Lock 2 lớp trên | `bible/37_character_profile_schema.yaml` |
| **2. Thư viện nền** | Catalog để cân bằng + chống lặp | `bible/38_death_library` (kiểu chết), `bible/39_dialect_voice` (3 vùng × xưng hô/tiểu từ/từ vựng), `haunting_detail_catalog` |
| **3. Cân bằng phân bố** | Thêm quota: tuổi (thêm **trẻ em + người già**), vùng giọng, kiểu chết, nghề, hôn nhân | mở rộng `gen_100_passenger` + target mới |
| **4. Enrich + Gate** | Generator điền trường mở rộng; QA chặn render nếu focal char thiếu (completeness < ngưỡng) + thiếu haunting_signature + lệch giọng-quê | `character_manager.enrich` + QA gate mới |
| **5. Dàn phụ** | Đăng ký nhân vật phụ mỗi tập (chống trùng/mâu thuẫn) | mở rộng roster (secondary cast) |

**Quyết định cần Boss chốt:** (a) khoá 100 hay mở thêm dàn phụ có kiểm soát? (b) bổ sung **trẻ em/người già** vào phân bố tuổi? (c) chốt 3 vùng giọng + quota? (d) mức "completeness gate" để 1 tập được render?
