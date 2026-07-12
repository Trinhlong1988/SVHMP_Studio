# G4 EVENT FINDINGS — máy đào ngược episode ĐÃ CÓ (TASK_G4_WORLD D2)

- Sinh bởi: `tools/event_ledger_miner.py` — 2026-07-12
- Tập quét: 50 (ep_01..ep_50)
- Route: **executor/Mr.Long xử lý**. Mọi finding kèm evidence ep:line — không suy luận.

## F1 — Nickname roster xuất hiện ngoài tập được gán (66 nickname)
(KHÔNG mặc định là lỗi — có thể là continuity xuyên tập CHỦ Ý. Cần người xác nhận chủ ý hay trùng âm tiết ngẫu nhiên.
GIỚI HẠN ĐÃ BIẾT: case ví dụ trong TASK ("Phong" ep_15 tái xuất ep_25) KHÔNG lọt vào danh sách này — "Phong" bị loại khỏi candidate vì trùng tên tắt của Khải Phong (nhân vật chính, ~mọi tập), còn "Hoài" (từ khác trong "Phong Hoài Đức") không xuất hiện lại trong ep_25 (chỉ có "Phong" được nhắc). Miner dựa trên tần suất âm tiết — không giải quyết được đồng tham chiếu (coreference) nhân vật qua đại từ/tên tắt trùng nhân vật chính.)

- 'Bách' (PAS_0136/freeform_ep35, gán ep_35) — xuất hiện thêm: ep_07, ep_15, ep_36
- 'Bính' (PAS_0082, gán ep_71) — xuất hiện thêm: ep_23, ep_34
- 'Băng' (PAS_0081, gán ep_70) — xuất hiện thêm: ep_09
- 'Bằng' (PAS_0073, gán ep_62) — xuất hiện thêm: ep_30
- 'Châu' (PAS_0022, gán ep_11) — xuất hiện thêm: ep_48
- 'Chín' (PAS_0144/freeform_ep43, gán ep_43) — xuất hiện thêm: ep_28
- 'Chương' (PAS_0114/freeform_ep13, gán ep_13) — xuất hiện thêm: ep_14, ep_50
- 'Cúc' (PAS_0025, gán ep_14) — xuất hiện thêm: ep_13, ep_16, ep_19
- 'Cảnh' (PAS_0072, gán ep_61) — xuất hiện thêm: ep_36, ep_39
- 'Cần' (PAS_0133/freeform_ep32, gán ep_32) — xuất hiện thêm: ep_17, ep_48, ep_49
- 'Diễm' (PAS_0015, gán ep_04) — xuất hiện thêm: ep_36
- 'Duy' (PAS_0116/freeform_ep15, gán ep_15) — xuất hiện thêm: ep_29, ep_46
- 'Hiếu' (PAS_0038, gán ep_27) — xuất hiện thêm: ep_45, ep_46
- 'Hiền' (PAS_0031, gán ep_20) — xuất hiện thêm: ep_21
- 'Hoàn' (PAS_0075, gán ep_64) — xuất hiện thêm: ep_18, ep_20
- 'Hoàng' (PAS_0014, gán ep_03) — xuất hiện thêm: ep_31, ep_44, ep_50
- 'Huy' (PAS_0032, gán ep_21) — xuất hiện thêm: ep_22
- 'Hương' (PAS_0039, gán ep_28) — xuất hiện thêm: ep_07, ep_14, ep_34
- 'Hạnh' (PAS_0029, gán ep_18) — xuất hiện thêm: ep_38
- 'Hậu' (PAS_0047, gán ep_36) — xuất hiện thêm: ep_48, ep_49
- 'Hằng' (PAS_0017, gán ep_06) — xuất hiện thêm: ep_27, ep_42
- 'Khang' (PAS_0032, gán ep_21) — xuất hiện thêm: ep_07, ep_10, ep_18
- 'Khoa' (PAS_0040, gán ep_29) — xuất hiện thêm: ep_41, ep_47
- 'Khôi' (PAS_0049, gán ep_38) — xuất hiện thêm: ep_12, ep_21
- 'Lam' (PAS_0079, gán ep_68) — xuất hiện thêm: ep_35
- 'Liêm' (PAS_0075, gán ep_64) — xuất hiện thêm: ep_48
- 'Liễu' (PAS_0027, gán ep_16) — xuất hiện thêm: ep_21
- 'Ly' (PAS_0055, gán ep_44) — xuất hiện thêm: ep_28
- 'Lâm' (PAS_0014, gán ep_03) — xuất hiện thêm: ep_18, ep_26
- 'Lý' (PAS_0095, gán ep_85) — xuất hiện thêm: ep_22, ep_23, ep_49
- 'Lộc' (PAS_0057, gán ep_46) — xuất hiện thêm: ep_24, ep_27, ep_29
- 'Mạnh' (PAS_0084, gán ep_74) — xuất hiện thêm: ep_46
- 'Nga' (PAS_0043, gán ep_32) — xuất hiện thêm: ep_29
- 'Nhuệ' (PAS_0093, gán ep_83) — xuất hiện thêm: ep_11
- 'Nhân' (PAS_0059, gán ep_48) — xuất hiện thêm: ep_22, ep_38
- 'Pháp' (PAS_0078, gán ep_67) — xuất hiện thêm: ep_11
- 'Phát' (PAS_0048, gán ep_37) — xuất hiện thêm: ep_01, ep_09
- 'Quan' (PAS_0088, gán ep_78) — xuất hiện thêm: ep_02, ep_03, ep_35
- 'Quân' (PAS_0068, gán ep_57) — xuất hiện thêm: ep_26, ep_35, ep_45
- 'Sa' (PAS_0089, gán ep_79) — xuất hiện thêm: ep_36
- 'Sơn' (PAS_0044, gán ep_33) — xuất hiện thêm: ep_09, ep_17, ep_50
- 'Thi' (PAS_0099, gán ep_89) — xuất hiện thêm: ep_08
- 'Thu' (PAS_0076, gán ep_65) — xuất hiện thêm: ep_11
- 'Thơ' (PAS_0130/freeform_ep29, gán ep_29) — xuất hiện thêm: ep_48, ep_49
- 'Thương' (PAS_0128/freeform_ep27, gán ep_27) — xuất hiện thêm: ep_32
- 'Thịnh' (PAS_0090, gán ep_80) — xuất hiện thêm: ep_07
- 'Thục' (PAS_0120/freeform_ep19, gán ep_19) — xuất hiện thêm: ep_06
- 'Toàn' (PAS_0062, gán ep_51) — xuất hiện thêm: ep_17, ep_37
- 'Trinh' (PAS_0045, gán ep_34) — xuất hiện thêm: ep_39
- 'Triệu' (PAS_0067, gán ep_56) — xuất hiện thêm: ep_37
- 'Trà' (PAS_0076, gán ep_65) — xuất hiện thêm: ep_20
- 'Trâm' (PAS_0113/freeform_ep12, gán ep_12) — xuất hiện thêm: ep_41
- 'Trí' (PAS_0023, gán ep_12) — xuất hiện thêm: ep_35, ep_36, ep_45
- 'Tuấn' (PAS_0016, gán ep_05) — xuất hiện thêm: ep_12, ep_36, ep_46
- 'Tâm' (PAS_0073, gán ep_62) — xuất hiện thêm: ep_15, ep_20, ep_28
- 'Tín' (PAS_0065, gán ep_54) — xuất hiện thêm: ep_11
- 'Tỉnh' (PAS_0080, gán ep_69) — xuất hiện thêm: ep_25
- 'Vi' (PAS_0035, gán ep_24) — xuất hiện thêm: ep_07
- 'Vân' (PAS_0069, gán ep_58) — xuất hiện thêm: ep_10, ep_49
- 'Vượng' (PAS_0118/freeform_ep17, gán ep_17) — xuất hiện thêm: ep_07
- 'Xuân' (PAS_0134/freeform_ep33, gán ep_33) — xuất hiện thêm: ep_17, ep_25, ep_42
- 'Yến' (PAS_0039, gán ep_28) — xuất hiện thêm: ep_16, ep_23, ep_31
- 'Đài' (PAS_0148/freeform_ep47, gán ep_47) — xuất hiện thêm: ep_43
- 'Đàn' (PAS_0129/freeform_ep28, gán ep_28) — xuất hiện thêm: ep_48
- 'Đào' (PAS_0027, gán ep_16) — xuất hiện thêm: ep_17, ep_29
- 'Đăng' (PAS_0040, gán ep_29) — xuất hiện thêm: ep_04

## F2 — Mâu thuẫn số học tuổi/mốc thời gian TRONG PHẠM VI GẦN NHAU (±3 dòng, 4 tập)
(ỨNG VIÊN cần người xem lại — KHÔNG khẳng định là lỗi thật. Đã xác nhận có false-positive kiểu "mất X năm trước, Y tuổi... trước sinh nhật (Y+1) tuổi" — văn phong "gần tròn tuổi" không phải mâu thuẫn số học, máy chưa phân biệt được. Window hẹp quanh mốc "X năm trước" giảm nhiễu gộp-nhiều-nhân-vật so với bản đầu (35→4 tập), nhưng vẫn cần người xác nhận từng ca.)

- ep_10:143 'ba mươi năm trước': tuổi gần đó = [16, 46] (không cùng khớp 1 mốc qua ±30)
- ep_36:131 'hai mươi năm trước': tuổi gần đó = [8, 20] (không cùng khớp 1 mốc qua ±20)
- ep_38:131 'mười bảy năm trước': tuổi gần đó = [17, 18] (không cùng khớp 1 mốc qua ±17)
- ep_49:123 'mười lăm năm trước': tuổi gần đó = [20, 27] (không cùng khớp 1 mốc qua ±15)

## F3 — signature_object KHÔNG có trong bible/12 object_library (36 tập)
(PHÁT HIỆN THẬT khi build G4, khớp RFC đã ghi nhận trước đó — bible/12 thiếu nhóm gương/kính + hoa cúc + văn bản/nghề nghiệp. Route: RFC bible/12 mở rộng, Mr.Long duyệt.)

- ep_11: 'OBJ_VONG_CO_SAO'
- ep_13: 'OBJ_HOA_CUC_KHO'
- ep_14: 'OBJ_KHAN_QUANG_THEU_CUC'
- ep_15: 'OBJ_GUONG_VO'
- ep_16: 'OBJ_CHAU_CUC'
- ep_17: 'OBJ_USB'
- ep_19: 'OBJ_VONG_HOA_CUC'
- ep_20: 'OBJ_SO_TAY'
- ep_21: 'OBJ_ANH_MO'
- ep_22: 'OBJ_SACH_'
- ep_23: 'OBJ_THU_TU_CHOI'
- ep_24: 'OBJ_VO_VIET'
- ep_25: 'OBJ_KINH_NHO'
- ep_26: 'OBJ_THUOC_T'
- ep_27: 'OBJ_ANH_CHUNG'
- ep_29: 'OBJ_THE_HIEN_MAU'
- ep_30: 'OBJ_BANG_TOT_NGHIEP'
- ep_31: 'OBJ_CHAU_CUC_THANG_TU'
- ep_32: 'OBJ_CHAN_DAN_DO'
- ep_33: 'OBJ_VE_TAU_DIEN'
- ep_34: 'OBJ_HUONG_TRAM'
- ep_35: 'OBJ_MANH_GUONG'
- ep_36: 'OBJ_TAM_ANH'
- ep_37: 'OBJ_BIEN_SO'
- ep_38: 'OBJ_HOP_QUA'
- ep_39: 'OBJ_TO_COM'
- ep_40: 'OBJ_GIAY_KTS'
- ep_41: 'OBJ_DIEN_THOAI'
- ep_43: 'OBJ_GIAY_CONG_DAN'
- ep_44: 'OBJ_KHUC_CHE'
- ep_45: 'OBJ_MANH_GUONG'
- ep_46: 'OBJ_TUI_VAI_CAT'
- ep_47: 'OBJ_VE_MAY_BAY'
- ep_48: 'OBJ_DAN_GUITAR'
- ep_49: 'OBJ_KHAN_TAY'
- ep_50: 'OBJ_THIEP_CUOI'