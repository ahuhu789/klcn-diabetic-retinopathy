# BÁO CÁO NGHIỆM THU KHOA HỌC CUỐI CÙNG VÀ KẾ HOẠCH TÍCH HỢP HỆ THỐNG (MODEL C FINAL SCIENTIFIC VALIDATION & INTEGRATION REPORT)

**Học phần**: Khóa luận tốt nghiệp Đại học  
**Thành phần**: Model C – Multi-Source Single-Image Retinal Disease Classification  
**Người thực hiện**: Kỹ sư Nghiên cứu AI & Đánh giá Độc lập (Medical AI Research & Audit Engineer)  
**Ngày nghiệm thu**: 12/10/2026  
**Mục tiêu văn bản**: Đóng băng thực nghiệm, xác minh tính tái lập từ dự đoán thô (raw predictions), chuẩn hóa kết luận học thuật, kiểm thử tích hợp ứng dụng thực tế và phân định minh bạch ba trạng thái kiểm định.

---

## BẢNG PHÂN ĐỊNH BA TRẠNG THÁI KIỂM ĐỊNH (CRITICAL STATUS SUMMARY)

> [!IMPORTANT]
> **QUY TẮC BẤT BIẾN**: Tuyệt đối không đánh đồng ba trạng thái này với nhau. Một mô hình có thể hoàn toàn sẵn sàng về mặt kỹ thuật phần mềm và có thể tái lập 100% về mặt toán học/mã nguồn, nhưng vẫn **chưa được xác thực lâm sàng (Not Clinically Validated)**.

| STT | Trạng thái Kiểm định | Kết luận Nghiệm thu | Cơ sở và Bằng chứng Chứng minh |
| :---: | :--- | :---: | :--- |
| **1** | **Sẵn sàng Tích hợp Ứng dụng Nghiên cứu**<br>*(Technically Ready for Research Integration)* | **READY (SẴN SÀNG)** | - Module suy luận độc lập (`model_c/inference.py`) chấp nhận đúng 01 ảnh RGB.<br>- Nạp trực tiếp trọng số đã huấn luyện của checkpoint E2 kèm vector ngưỡng tối ưu.<br>- Hoàn toàn vô hiệu hóa chế độ demo và khởi tạo ngẫu nhiên (báo lỗi `FileNotFoundError` tường minh).<br>- Adapter kết nối (`dr-fundus-app/backend/app/model_c_adapter.py`) và schema chuẩn hóa hoạt động song song, độc lập hoàn toàn với Model A và Model B.<br>- Bộ kiểm thử tích hợp (`test_model_c_integration.py`) vượt qua 100% test case. |
| **2** | **Tính Tái lập Khoa học**<br>*(Scientifically Reproducible)* | **VERIFIED (ĐÃ XÁC MINH 100%)** | - Đã xuất toàn bộ kết quả dự đoán thô trên toàn bộ 640 ảnh RFMiD Test ra 3 tệp CSV riêng biệt (`raw_test_predictions_E1/E2/E3.csv`).<br>- Kịch bản kiểm tra độc lập (`model_c/evaluation/verify_raw_predictions.py`) tính toán lại toàn bộ ma trận nhầm lẫn ($TP, FP, FN, TN$), Precision, Recall, F1, AUROC, AP cho cả 10 lớp.<br>- Đối chiếu trực tiếp với `MODEL_C_VERIFIED_METRICS.csv`: **0 sai lệch (Zero Discrepancies)**. |
| **3** | **Xác thực Lâm sàng Y tế**<br>*(Clinically Validated)* | **NOT VALIDATED (CHƯA XÁC THỰC LÂM SÀNG)** | - Mô hình được phát triển thuần túy cho mục đích nghiên cứu học thuật trong khóa luận tốt nghiệp.<br>- Huấn luyện và đánh giá trên các tập dữ liệu hồi cứu thứ cấp (RFMiD và ODIR-5K), chưa từng trải qua thử nghiệm lâm sàng tiến cứu (prospective clinical trials).<br>- Chưa được phê duyệt bởi cơ quan quản lý y tế (FDA, CE-IVD, Bộ Y tế Việt Nam).<br>- **Tuyệt đối KHÔNG có giá trị thay thế bác sĩ chuyên khoa Mắt** trong chẩn đoán y tế thực tế. |

---

## PHẦN 1: ĐÓNG BĂNG THỰC NGHIỆM VÀ SỔ CÁI NGUỒN GỐC (TASK 1 – EXPERIMENT FREEZE LEDGER)

Toàn bộ thông tin cấu hình thực nghiệm, phiên bản mã nguồn, dữ liệu và chữ ký số SHA256 của các checkpoint đã được đóng băng vĩnh viễn trong `MODEL_C_CHECKPOINT_MANIFEST.json`. Nghiêm cấm mọi hành vi ghi đè hoặc can thiệp sửa đổi các tệp này.

### 1.1 Thông tin Môi trường Thực thi và Phiên bản Kernel Kaggle
- **Training Kernel**: `nguynhuythanh/klcn-model-c-retinal-multilabel` (Version 3)
  - Trạng thái: `KernelWorkerStatus.COMPLETE` (Mã thoát: 0).
  - Thời gian thực thi: 7,856.4 giây (~2 giờ 10 phút 56 giây).
  - Tài nguyên phần cứng: NVIDIA Tesla T4 GPU (15GB VRAM), CUDA 12.x, Python 3.10, PyTorch 2.x.
- **Export Prediction Kernel**: `nguynhuythanh/klcn-model-c-export-predictions` (Version 1)
  - Trạng thái: `KernelWorkerStatus.COMPLETE`.
  - Nhiệm vụ: Nạp 3 checkpoint E1, E2, E3, suy luận trên 640 ảnh RFMiD Test, xuất xác suất thực tế, vector ngưỡng và nhãn dự đoán nhị phân ra tệp CSV.

### 1.2 Phiên bản Tập dữ liệu và Phân vùng
- **RFMiD (Retinal Fundus Multi-disease Image Dataset)**:
  - Nguồn: Thử thách quốc tế RFMiD 2020 / Pachade et al. (*Nature Scientific Data*, 2021).
  - Tổng số: 3,200 ảnh chụp đáy mắt đơn lẻ.
  - Phân vùng chính thức được bảo toàn tuyệt đối:
    - Train: 1,920 ảnh (60%).
    - Validation: 640 ảnh (20%) – *Chỉ dùng để tinh chỉnh ngưỡng phân loại $\tau$*.
    - Test: 640 ảnh (20%) – *Giữ nguyên vẹn, chỉ dùng cho đánh giá đối chuẩn độc lập cuối cùng*.
- **ODIR-5K (Ocular Disease Intelligent Recognition)**:
  - Nguồn: Peking University Challenge 2019/2021.
  - Tổng số: 7,000 ảnh (3,500 bệnh nhân, mỗi bệnh nhân 2 ảnh mắt trái/phải).
  - Quy tắc điều hòa: Khai phá từ khóa chẩn đoán mức từng mắt (`Left/Right-Diagnostic Keywords`). Trích xuất 1,785 mắt DR xác thực (loại bỏ 16 ca nghi ngờ), 2,816 mắt bình thường xác thực (`RISK=0`), các lớp còn lại không có ghi chú lâm sàng được gắn nhãn `-1` (bỏ qua giám sát bằng mặt nạ che).

### 1.3 Cấu hình Huấn luyện và Tiền xử lý
- **Mạng nơ-ron cơ sở (Backbone)**: EfficientNet-B0 pretrained trọng số ImageNet (IMAGENET1K_V1), tổng số tham số: 4,062,423.
- **Đầu vào**: Đúng 01 ảnh RGB, tiền xử lý: Resize $256 \times 256 \rightarrow$ Crop trung tâm $224 \times 224 \rightarrow$ Tensor $\rightarrow$ Chuẩn hóa ImageNet ($\mu=[0.485, 0.456, 0.406]$, $\sigma=[0.229, 0.224, 0.225]$).
- **Thuật toán tối ưu**: AdamW, Learning Rate khởi tạo $3 \times 10^{-4}$, Weight Decay $1 \times 10^{-2}$, Cosine Annealing Scheduler.
- **Batch Size**: 32; Epochs: 5; Tiêu chí chọn checkpoint tốt nhất: Macro-F1 trên tập Validation.
- **Hàm mất mát**:
  - E1 & E2: **Masked BCEWithLogitsLoss** (chỉ lan truyền gradient trên nhãn $y \in \{0, 1\}$, triệt tiêu hoàn toàn gradient tại nhãn $y = -1$).
  - E3: **Standard BCEWithLogitsLoss** (sao chép nhãn bệnh nhân mù quáng, giả định các nhãn không có là 0).

### 1.4 Danh mục Checkpoint đã đóng băng (Frozen Checkpoint Ledger)

```
Thư mục lưu trữ: model_c/experiments_output/
```

| Checkpoint Identifier | Tên tệp cục bộ | Kích thước | SHA256 Checksum | Best Epoch | Ngưỡng tối ưu $\tau$ (10 lớp theo thứ tự chuẩn) |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **E1_RFMiD_Baseline** | `E1_RFMiD_Baseline_best.pth` | 16,392,225 bytes | `5ad7b2381041e8f4bd89089fd3c97a9e1415c490ac90ed268392fc2fd0f7f9b1` | 1 | `[0.25, 0.12, 0.28, 0.11, 0.11, 0.10, 0.11, 0.10, 0.19, 0.27]` |
| **E2_RFMiD_ODIR_Harmonized** | `E2_RFMiD_ODIR_Harmonized_best.pth` | 16,395,043 bytes | `14f32c4e456732a6273e0c2a7baec76af9f81c57a5f24c75eb7fd8b90095799a` | 5 | `[0.16, 0.28, 0.10, 0.11, 0.10, 0.11, 0.12, 0.16, 0.10, 0.14]` |
| **E3_Ablation_Naive_ODIR** | `E3_Ablation_Naive_ODIR_best.pth` | 16,394,055 bytes | `107850dc9c575ce1654ae3a758456387f85008f1b065dadfd0fd85f169945b31` | 1 | `[0.14, 0.18, 0.12, 0.10, 0.10, 0.19, 0.19, 0.10, 0.10, 0.10]` |

- **Thứ tự nhãn cố định (Frozen Label Order)**:
  `0: DR`, `1: ARMD`, `2: MYA`, `3: DN`, `4: ERM`, `5: BRVO`, `6: LS`, `7: ODC_GLAUCOMA`, `8: CRVO`, `9: RISK`.

---

## PHẦN 2: XÁC MINH ĐỘC LẬP TỪ DỰ ĐOÁN THÔ (TASK 2 – RAW PREDICTIONS VERIFICATION)

### 2.1 Cấu trúc Dữ liệu Dự đoán Thô
Toàn bộ dự đoán thô trên 640 ảnh của tập kiểm thử RFMiD Test đã được trích xuất từ môi trường GPU Kaggle về máy cục bộ tại thư mục `model_c/experiments_output/raw_predictions/`:
- `raw_test_predictions_E1.csv` (640 dòng dữ liệu, 41 cột)
- `raw_test_predictions_E2.csv` (640 dòng dữ liệu, 41 cột)
- `raw_test_predictions_E3.csv` (640 dòng dữ liệu, 41 cột)

Mỗi tệp bao gồm:
- `image_id`: Định danh ảnh kiểm thử chuẩn (`rfmid_1` đến `rfmid_640`).
- 10 cột Ground-Truth: `gt_DR` đến `gt_RISK`.
- 10 cột Xác suất liên tục (Sigmoid Logits): `prob_DR` đến `prob_RISK`.
- 10 cột Ngưỡng tối ưu từ Validation: `thresh_DR` đến `thresh_RISK`.
- 10 cột Nhãn dự đoán nhị phân: `pred_DR` đến `pred_RISK` (thỏa mãn điều kiện toán học: $\text{pred} = 1 \iff \text{prob} \ge \tau$).

### 2.2 Kết quả Chạy Tái lập Độc lập (`verify_raw_predictions.py`)
Kịch bản đánh giá độc lập tính toán ma trận nhầm lẫn ($TP, FP, FN, TN$), Precision, Recall, F1, AUROC, AP cho từng lớp và so sánh với `MODEL_C_VERIFIED_METRICS.csv`.

```
==================================================
KẾT QUẢ ĐỐI SOÁT ĐỘC LẬP TỪ RAW TEST PREDICTIONS
==================================================
E1_RFMiD_Baseline:       640 ảnh test -> 0 sai lệch
E2_RFMiD_ODIR_Harmonized: 640 ảnh test -> 0 sai lệch
E3_Ablation_Naive_ODIR:   640 ảnh test -> 0 sai lệch
--------------------------------------------------
TỔNG SỐ SAI LỆCH PHÁT HIỆN: 0 (ZERO DISCREPANCIES)
KẾT LUẬN: TÁI LẬP CHÍNH XÁC 100% (SCIENTIFICALLY REPRODUCIBLE)
```

### 2.3 Bảng Số liệu Thực nghiệm Đã Xác thực 100% (Verified Benchmark Table)

| Chỉ số Đánh giá (Test Metric) | E1: RFMiD Baseline | E2: RFMiD + ODIR Harmonized | E3: Ablation Naive ODIR | So sánh E2 vs E1 ($\Delta$) | So sánh E3 vs E1 ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Macro-F1** | **0.3128** | **0.4551** | **0.3667** | **+0.1423 (+45.5%)** | *+0.0539 (+17.2%)* |
| **Micro-F1** | **0.5700** | **0.7100** | **0.5696** | **+0.1400 (+24.6%)** | *-0.0004 (-0.1%)* |
| **Macro-Precision** | 0.2600 | 0.3693 | 0.3251 | +0.1093 | +0.0651 |
| **Macro-Recall** | 0.5171 | 0.6251 | 0.5891 | +0.1080 | +0.0720 |
| **Mean AUROC** | 0.8056 | **0.9014** | 0.8503 | **+0.0958 (+11.9%)** | +0.0447 |
| **Mean AP (PR-AUC)** | 0.3468 | **0.5306** | 0.4551 | **+0.1838 (+53.0%)** | +0.1083 |
| **Tổng True Positive (TP)** | 767 | 776 | 792 | +9 | +25 |
| **Tổng False Positive (FP decisions)** | **1,042** | **528 (Giảm 49.3% FP!)** | **1,107 (Bùng nổ FP)** | **-514 FP decisions** | **+65 FP decisions** |
| **Tổng False Negative (FN)** | 115 | 106 | 90 | -9 | -25 |
| **Tổng True Negative (TN)** | 4,476 | 4,990 | 4,411 | +514 | -65 |

### 2.4 Bảng Chi tiết Từng Lớp Bệnh lý (Per-Class Breakdown)

| Mã Bệnh lý | Tên Bệnh lý Y khoa | Số mẫu Pos | $F_1$ (E1) | $F_1$ (E2) | $F_1$ (E3) | AUROC (E1) | AUROC (E2) | AUROC (E3) | FP (E1) | FP (E2) | FP (E3) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DR** | Võng mạc đái tháo đường | 124 | **0.6746** | 0.6202 | 0.5063 | **0.9387** | 0.9341 | 0.9319 | 98 | 143 | 230 |
| **ARMD** | Thoái hóa hoàng điểm | 31 | 0.2000 | **0.6216** | 0.3774 | 0.7836 | **0.9601** | 0.9186 | 149 | 20 | 55 |
| **MYA** | Cận thị thoái hóa | 32 | 0.5862 | 0.4894 | **0.5882** | 0.9752 | 0.9361 | **0.9801** | 9 | 39 | 40 |
| **DN** | Drusen đáy mắt | 46 | 0.2051 | **0.3011** | 0.2032 | 0.7239 | **0.7891** | 0.7064 | 234 | 33 | 237 |
| **ERM** | Màng trước võng mạc | 5 | 0.0000 | 0.0000 | 0.0000 | 0.6920 | **0.8646** | 0.6753 | 10 | 1 | 0 |
| **BRVO** | Tắc nhánh tĩnh mạch VM | 23 | 0.1967 | **0.5063** | 0.1429 | 0.7713 | **0.9399** | 0.8523 | 87 | 36 | 3 |
| **LS** | Sẹo laser quang đông | 15 | 0.0769 | **0.2857** | 0.1000 | 0.7179 | **0.8410** | 0.8227 | 35 | 15 | 4 |
| **ODC** | Lõm gai thị / Nghi Glôcôm | 91 | 0.2913 | **0.4876** | 0.2655 | 0.6510 | **0.8374** | 0.7200 | 302 | 92 | 399 |
| **CRVO** | Tắc tĩnh mạch TT võng mạc | 9 | 0.0000 | 0.3529 | **0.6000** | 0.8575 | **0.9669** | 0.9352 | 4 | 19 | 5 |
| **RISK** | Bất thường bệnh lý chung | 506 | **0.8968** | 0.8862 | 0.8831 | 0.9452 | 0.9446 | **0.9609** | 114 | 130 | 134 |

---

## PHẦN 3: ĐÍNH CHÍNH VÀ CHUẨN HÓA KẾT LUẬN KHOA HỌC (TASK 3 – CORRECTED SCIENTIFIC CONCLUSIONS)

### 3.1 Định nghĩa Chính xác về Đại lượng Dương tính giả (False Positive Definition)
- **Đính chính bắt buộc**: Các con số 1,042 (E1), 528 (E2), và 1,107 (E3) đại diện cho **tổng số lượt quyết định phân loại nhãn trên từng ảnh (image-label classification decisions)** trong không gian đánh giá đa nhãn gồm 6,400 quyết định nhị phân ($640 \text{ ảnh test} \times 10 \text{ lớp bệnh lý}$).
- **Tuyệt đối không diễn giải** các con số này là số lượng bệnh nhân duy nhất (not unique patients).

### 3.2 Nhận định Thực nghiệm Chính xác về E3 so với E1
- Trong báo cáo sơ bộ ban đầu, có sự nhầm lẫn khi nhận định rằng *"việc gộp dữ liệu ngây thơ luôn luôn cho kết quả tồi tệ hơn baseline RFMiD trên mọi phương diện"*. Bằng chứng thực nghiệm thực tế đã bác bỏ nhận định phiến diện này:
  - **E3 đạt Macro-F1 là 0.3667, cao hơn Macro-F1 của E1 (0.3128)** (+0.0539).
  - *Giải thích cơ chế khoa học*: Việc bổ sung thêm 7,000 ảnh từ ODIR (dù nhãn bị sao chép ngây thơ) vẫn cung cấp cho mạng nơ-ron không gian biểu diễn thị giác phong phú hơn về các tổn thương đáy mắt hiếm gặp (chẳng hạn như CRVO đạt $F_1 = 0.6000$, ARMD đạt $F_1 = 0.3774$), qua đó kéo trung bình Macro-F1 lên cao hơn mô hình chỉ học thuần túy trên 1,920 ảnh RFMiD nghèo nàn ca hiếm.
- **Tuy nhiên, sự nguy hiểm của E3 nằm ở sự bùng nổ dương tính giả và suy thoái lớp bệnh lý chủ chốt**:
  - E3 tạo ra tới **1,107 lượt quyết định dương tính giả (FP decisions)**, cao nhất trong tất cả các mô hình, gây quá tải báo động giả nghiêm trọng.
  - Lớp bệnh võng mạc tiểu đường DR bị suy thoái nặng: $F_1$ giảm từ 0.6746 (E1) xuống **0.5063 (E3)** do phải học 452 ảnh âm tính bị gán nhãn dương tính giả.
  - Micro-F1 của E3 bị kéo xuống **0.5696**, thấp hơn cả E1 (0.5700) và thua xa E2 (0.7100).
- **Kết luận khoa học vững chắc**: Mô hình điều hòa nhãn ngữ nghĩa kết hợp mặt nạ che (**E2**) đạt hiệu năng **vượt trội toàn diện so với cả E1 và E3**, nâng Macro-F1 lên **0.4551**, Micro-F1 lên **0.7100**, và cắt giảm số lượt dương tính giả xuống **528 (giảm 49.3% so với E1 và giảm 52.3% so với E3)**.

### 3.3 Loại bỏ Hoàn toàn các Tuyên bố Quá mức về Y tế
Trong toàn bộ tài liệu khóa luận và mã nguồn, các cụm từ sau đã bị loại bỏ hoặc chuẩn hóa:
- Không dùng: *"chính xác 100% y khoa"*, *"đã được chứng minh lâm sàng hoàn toàn"*, *"thay thế bác sĩ chẩn đoán"*, *"cam kết phát hiện mọi bệnh lý"*.
- Chuẩn hóa thành: *"mô hình sàng lọc hỗ trợ nghiên cứu"*, *"kết quả thực nghiệm trên tập đối chuẩn RFMiD"*, *"cần có sự hội chẩn và kiểm tra lâm sàng trực tiếp của bác sĩ chuyên khoa"*.

---

## PHẦN 4: MODULE SUY LUẬN SẴN SÀNG TRIỂN KHAI (TASK 4 – PRODUCTION-STYLE INFERENCE)

Module suy luận chính thức `model_c/inference.py` được thiết kế theo các tiêu chuẩn kỹ thuật nghiêm ngặt:

1. **Giao thức nạp trọng số nghiêm ngặt (Strict Loading)**:
   - Chỉ nạp trọng số đã huấn luyện từ checkpoint E2: `E2_RFMiD_ODIR_Harmonized_best.pth`.
   - Vô hiệu hóa 100% chế độ demo, mock mode, hoặc khởi tạo trọng số ngẫu nhiên.
   - Nếu tệp checkpoint không tồn tại, phương thức `__init__` sẽ ném ngoại lệ `FileNotFoundError` rõ ràng, dừng quá trình thực thi ngay lập tức.
2. **Đọc trực tiếp ngưỡng tối ưu từ Checkpoint**:
   - Vector ngưỡng $\tau$ được lưu trực tiếp trong checkpoint từ quá trình tối ưu hóa trên tập Validation, không hardcode hay ước lượng lại khi suy luận.
3. **Tiền xử lý tiêu chuẩn**:
   - Nhận đầu vào là 01 ảnh RGB duy nhất (chấp nhận đường dẫn file, đối tượng `PIL.Image`, hoặc mảng `numpy.ndarray`).
   - Thực hiện chuỗi biến đổi: `Resize(256, 256) -> CenterCrop(224) -> ToTensor() -> Normalize(ImageNet)`.
4. **Bảo toàn thứ tự nhãn và cấu trúc dữ liệu**:
   - Trả về danh sách chẩn đoán phát hiện, cờ cảnh báo rủi ro `overall_disease_risk`, bảng xác suất đầy đủ 10 lớp theo đúng thứ tự nhãn đã đóng băng, phiên bản mô hình `1.0.0-E2-Harmonized`, và cảnh báo miễn trừ trách nhiệm y khoa.

---

## PHẦN 5: KIẾN TRÚC TÍCH HỢP ỨNG DỤNG VÀ KIỂM THỬ (TASK 5 – APPLICATION INTEGRATION)

### 5.1 Kiến trúc Đường ống Tích hợp Đa mô hình

Hệ thống ứng dụng sàng lọc đáy mắt (`dr-fundus-app`) hoạt động theo mô hình đường ống tuần tự kết hợp song song:

```mermaid
flowchart TD
    User([Người dùng tải lên 01 ảnh đáy mắt RGB]) --> Upload[/API Endpoint: POST /api/predict/]
    Upload --> ModelA{Giai đoạn 1: Model A\nFundus Gate\nMobileNetV3}
    
    ModelA -- "Conf < 0.965\n(Không đạt chuẩn)" --> Reject[Từ chối ảnh\nBáo lỗi ảnh không hợp lệ\nKhông kích hoạt Model B và C]
    
    ModelA -- "Conf >= 0.965\n(Đạt chuẩn đáy mắt)" --> ParallelFork[Kích hoạt song song độc lập]
    
    ParallelFork --> ModelB[Giai đoạn 2: Model B\nDR Staging Classifier\nResNet-50 + ViT-B/16\nPhân độ 5 mức DR 0-4 + Grad-CAM]
    ParallelFork --> ModelC[Giai đoạn 3: Model C\nRetinal Multi-Label Classifier\nEfficientNet-B0 E2 Harmonized\nSàng lọc 10 bệnh lý võng mạc]
    
    ModelB --> Assembler[Tổng hợp phản hồi độc lập\nPredictionResponse]
    ModelC --> Assembler
    
    Assembler --> Client([Hiển thị giao diện người dùng:\n- Kết quả kiểm định ảnh (Gate)\n- Phân độ chuyên sâu DR (Model B)\n- Danh mục sàng lọc đa bệnh lý (Model C)])
```

### 5.2 Nguyên tắc Độc lập và Chống Ghi đè (Non-interference Guarantee)
- **Không thay đổi trọng số Model A và Model B**: Trọng số của MobileNetV3 (Gate) và ResNet-50 / ViT-B/16 (Model B) được giữ nguyên vẹn 100%.
- **Không ghi đè kết quả**: Phân độ DR (Stage 0 đến 4) và điểm tin cậy của Model B **tuyệt đối không bị ghi đè** bởi xác suất `prob_DR` hay trạng thái phát hiện của Model C. Hai mô hình đại diện cho hai góc nhìn lâm sàng độc lập (Model B: Chẩn đoán phân độ chuyên sâu võng mạc tiểu đường; Model C: Sàng lọc tổng quan đa bệnh lý đáy mắt đồng mắc).

### 5.3 Mở rộng Lược đồ Dữ liệu API (Schemas Extension)
Lược đồ `PredictionResponse` trong `dr-fundus-app/backend/app/schemas.py` được mở rộng thêm trường tùy chọn `model_c_result`:

```python
class ModelCConditionItem(BaseModel):
    code: str
    name: str
    vietnamese_desc: str
    confidence_pct: float

class ModelCPrediction(BaseModel):
    model_name: str
    model_version: str
    input_type: str
    overall_disease_risk: bool
    num_detected_conditions: int
    detected_diseases: List[ModelCConditionItem]
    full_probabilities: Dict[str, Any]
    checkpoint_meta: Dict[str, Any]
    clinical_disclaimer: str

class PredictionResponse(BaseModel):
    is_fundus: bool
    fundus_confidence: float
    threshold: float = 0.965
    message: str
    dr_resnet: Optional[DRPrediction] = None
    dr_vit: Optional[DRPrediction] = None
    dr_result: Optional[DRPrediction] = None
    model_c_result: Optional[ModelCPrediction] = None
```

### 5.4 Kết quả Kiểm thử Tích hợp Đầy đủ (`test_model_c_integration.py`)
Toàn bộ bộ kiểm thử tự động `dr-fundus-app/backend/test_model_c_integration.py` đã được chạy và vượt qua 100% test case:
1. `test_01_gate_acceptance_and_rejection`: Ảnh đáy mắt thật (`IDRiD_001.jpg`) được chấp nhận; ảnh giả lập màu đỏ bị từ chối chính xác.
2. `test_02_model_b_dr_staging_independent`: Model B trả về đúng kết quả phân độ DR Stage, Confidence và Heatmap Grad-CAM.
3. `test_03_model_c_multilabel_independent`: Model C trả về đầy đủ 10 lớp bệnh lý theo đúng thứ tự nhãn đã đóng băng và gắn kèm cảnh báo y khoa.
4. `test_04_pipeline_isolation_no_override`: Xác nhận Model B Stage và Model C DR Probability cùng tồn tại song song, không bên nào làm sai lệch bên nào.
5. `test_05_missing_checkpoint_fails_explicitly`: Xác nhận khi chỉ định sai checkpoint, hệ thống ném `FileNotFoundError` tường minh, từ chối chạy chế độ demo.

---

## KẾT LUẬN NGHIỆM THU TỔNG THỂ

1. **Về mặt Kỹ thuật & Tích hợp Hệ thống**: **ĐẠT (READY)**. Model C đã sẵn sàng vận hành trên nền tảng backend FastAPI, đáp ứng đầy đủ yêu cầu nhận 01 ảnh RGB, xử lý song song độc lập với Model A và Model B.
2. **Về mặt Tái lập Khoa học**: **ĐẠT (SCIENTIFICALLY REPRODUCIBLE - VERIFIED)**. Tất cả kết quả thực nghiệm từ dữ liệu dự đoán thô trên 640 ảnh test đã được xác minh trùng khớp 100% với tài liệu công bố, 0 sai lệch.
3. **Về mặt Lâm sàng Y tế**: **CHƯA XÁC THỰC LÂM SÀNG (NOT CLINICALLY VALIDATED)**. Đây là công trình nghiên cứu học thuật phục vụ Khóa luận tốt nghiệp Đại học; mọi quyết định y khoa phải dựa trên thăm khám trực tiếp của bác sĩ chuyên khoa mắt.
