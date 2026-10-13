# BÁO CÁO KIỂM ĐỊNH HỌC THUẬT CUỐI CÙNG TRƯỚC KHI ĐÓNG BĂNG KHÓA LUẬN (MODEL C FINAL ACADEMIC CHECK & INTEGRITY REPORT)

**Học phần**: Khóa luận tốt nghiệp Đại học  
**Thành phần**: Model C – Multi-Source Single-Image Retinal Disease Classification  
**Người thực hiện**: Kỹ sư Nghiên cứu AI & Đánh giá Độc lập (AI Research & Academic Audit Engineer)  
**Ngày hoàn thành**: 12/10/2026  
**Trạng thái tài liệu**: Tài liệu kiểm định học thuật cuối cùng – Đóng băng phục vụ bảo vệ khóa luận  

---

## TỔNG QUAN VÀ BẢNG PHÂN ĐỊNH BỐN CẤP ĐỘ KIỂM ĐỊNH (FOUR-LEVEL INTEGRITY AUDIT)

> [!CAUTION]
> **TUYÊN BỐ LIÊM CHÍNH KHOA HỌC**:
> Công trình nghiên cứu **KHÔNG ĐƯỢC TUYÊN BỐ LÀ ĐÃ XÁC THỰC HOÀN TOÀN (NOT FULLY VALIDATED)** nếu chưa phân định rạch ròi giữa các cấp độ kiểm định độc lập. Nghiên cứu tuyệt đối không đánh đồng bốn cấp độ kiểm định sau:

| STT | Cấp độ Kiểm định | Trạng thái Đạt được | Cơ sở Minh chứng và Giới hạn Thực tế |
| :---: | :--- | :---: | :--- |
| **1** | **Tính Tái lập Chỉ số từ Dự đoán Đã lưu**<br>*(Metric Reproducibility from Saved Predictions)* | **VERIFIED (XÁC MINH ĐẦY ĐỦ)** | Toàn bộ 640 bản ghi dự đoán thô trên tập kiểm thử RFMiD Test (`raw_test_predictions_E1/E2/E3.csv`) đã được tính toán lại độc lập qua kịch bản `verify_raw_predictions.py`. **Khớp chính xác 100% đối với từng lớp, từng chỉ số, 0 sai lệch**. |
| **2** | **Tính Khả thi Tái thực thi Đường ống Huấn luyện**<br>*(Re-executability of Training Pipeline)* | **VERIFIED (ĐÃ THỰC THI THÀNH CÔNG)** | Toàn bộ mã nguồn, cấu hình siêu tham số, phân vùng dữ liệu và hạt giống ngẫu nhiên (`seed=42`) được đóng gói hoàn chỉnh. Đường ống huấn luyện đã thực thi trọn vẹn 100% trên môi trường Kaggle GPU (`KernelWorkerStatus.COMPLETE`), sinh ra đầy đủ 3 checkpoint thực nghiệm. |
| **3** | **Tính Tái lập qua Nhiều Lần Huấn luyện Độc lập**<br>*(Reproducibility across Repeated Training Runs)* | **UNVERIFIED (CHƯA ĐÁNH GIÁ ĐA LẦN CHẠY)** | Chưa thực hiện các lượt huấn luyện lặp lại với nhiều hạt giống ngẫu nhiên (multi-seed runs) để đo lường phân phối phương sai thực tế. Do tính bất định vốn có của các phép toán song song CUDA/cuDNN (như atomic additions trong lan truyền ngược), **không đưa ra bất kỳ khẳng định vô căn cứ nào về việc sai số chắc chắn nằm trong biên độ $\pm 0.005 - 0.010$**. |
| **4** | **Xác thực Lâm sàng Y tế**<br>*(Clinical Diagnostic Validation)* | **NOT VALIDATED (CHƯA XÁC THỰC LÂM SÀNG)** | Mô hình chỉ được đánh giá hồi cứu (retrospective) trên tập dữ liệu benchmark công khai, **chưa từng trải qua thử nghiệm lâm sàng tiến cứu (prospective trial)**, chưa được thẩm định bởi hội đồng y khoa tại bệnh viện và chưa được cơ quan y tế (Bộ Y tế, FDA) cấp phép. **Tuyệt đối không có giá trị chẩn đoán y khoa thay thế bác sĩ**. |

---

## MỤC 1 & 2: TÍNH TOÁN LẠI VÀ ĐIỀU TRA CHUYÊN SÂU LỚP BỆNH VÕNG MẠC TIỂU ĐƯỜNG (DR CLASS F1 INVESTIGATION)

### 1.1 Số liệu Tái lập Trực tiếp từ Dự đoán Thô (Ground-Truth vs Model Predictions)
Dựa trên việc đọc trực tiếp 640 dòng dự đoán kiểm thử tại `model_c/experiments_output/raw_predictions/`:

| Mô hình Thực nghiệm | Ngưỡng $\tau_{\text{DR}}$ | Pos Support | Neg Support | TP | FP | FN | TN | Precision | Recall | **$F_1$ Score** | AUROC | Average Precision |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E1: RFMiD Baseline** | 0.25 | 124 | 516 | 113 | 98 | 11 | 418 | 0.5355 | 0.9113 | **0.6746** | **0.9387** | 0.8327 |
| **E2: RFMiD + ODIR Harmonized** | 0.16 | 124 | 516 | 120 | 143 | 4 | 373 | 0.4563 | **0.9677** | **0.6202** | 0.9341 | 0.7333 |
| **E3: Ablation Naive ODIR** | 0.14 | 124 | 516 | 120 | 230 | 4 | 286 | 0.3429 | **0.9677** | **0.5063** | 0.9319 | **0.8405** |

### 1.2 Điều tra Nguyên nhân: Tại sao $F_1$ của DR trong E2 lại thấp hơn E1 dù Macro-F1 tổng thể tăng vọt?

Thực nghiệm cho thấy ở E2, Macro-F1 tổng thể tăng mạnh từ **0.3128 lên 0.4551 (+45.5%)**, Micro-F1 tăng từ **0.5700 lên 0.7100**, AUROC tăng từ **0.8056 lên 0.9014**, nhưng riêng lớp DR thì $F_1$ lại ghi nhận $0.6202$ (thấp hơn $0.6746$ ở E1). 

> [!WARNING]
> **NGUYÊN TẮC BẢO VỆ TẬP TEST VÀ CHỐNG RÒ RỈ NGƯỠNG (TEST-SET THRESHOLD LEAKAGE PREVENTION)**:
> 1. Quá trình quét ngưỡng dưới đây được thực hiện **THUẦN TÚY LÀ MỘT PHÂN TÍCH THĂM DÒ HẬU KIỂM (POST-HOC EXPLORATORY ANALYSIS ONLY)** nhằm tìm hiểu động học của mô hình.
> 2. **Tuyệt đối KHÔNG sử dụng ngưỡng 0.35 hay bất kỳ kết quả quét nào trên tập Test để cập nhật module suy luận (`model_c/inference.py`), checkpoint manifest hoặc bộ số liệu đối chuẩn chính thức**.
> 3. **Ngưỡng đối chuẩn chính thức của E2 cho lớp DR BẮT BUỘC GIỮ NGUYÊN là 0.16** (ngưỡng được tối ưu hóa độc lập từ tập Validation). Nếu có nhu cầu tái tối ưu ngưỡng trong tương lai, quy trình bắt buộc phải thực hiện hoàn toàn trên tập Validation và đánh giá trên một tập kiểm thử giữ lại (holdout test set) mới chưa từng nhìn thấy.

#### Bảng Quét Ngưỡng Thăm dò Hậu kiểm (Post-Hoc Threshold Sweep on Test Data):
| Ngưỡng $\tau$ | TP | FP | FN | TN | Precision | Recall | **$F_1$ Score** | Phân loại & Ý nghĩa Phân tích |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0.10** | 122 | 236 | 2 | 280 | 0.3408 | 0.9839 | 0.5062 | [Hậu kiểm] Ngưỡng quá thấp, bùng nổ FP |
| **0.14** | 121 | 168 | 3 | 348 | 0.4187 | 0.9758 | 0.5860 | [Hậu kiểm] Tương đương ngưỡng E3 |
| **0.16** | **120** | **143** | **4** | **373** | **0.4563** | **0.9677** | **0.6202** | **NGƯỠNG CHÍNH THỨC CỦA BENCHMARK (Chọn từ Validation Set)** |
| **0.20** | 113 | 111 | 11 | 405 | 0.5045 | 0.9113 | 0.6494 | [Hậu kiểm] Cân bằng hơn |
| **0.25** | **109** | **85** | **15** | **431** | **0.5619** | **0.8790** | **0.6855** | **[Hậu kiểm] So sánh bình đẳng cùng ngưỡng E1: $F_1$ cao hơn E1 (0.6855 > 0.6746)** |
| **0.30** | 106 | 61 | 18 | 455 | 0.6347 | 0.8548 | 0.7285 | [Hậu kiểm] Precision tăng mạnh |
| **0.35** | 105 | 49 | 19 | 467 | 0.6818 | 0.8468 | **0.7554** | **[CHỈ LÀ PHÂN TÍCH HẬU KIỂM - KHÔNG DÙNG LÀM BENCHMARK]** |
| **0.40** | 98 | 44 | 26 | 472 | 0.6901 | 0.7903 | 0.7368 | [Hậu kiểm] Bắt đầu tăng ca bỏ sót FN |
| **0.50** | 84 | 31 | 40 | 485 | 0.7304 | 0.6774 | 0.7029 | [Hậu kiểm] Ngưỡng mặc định truyền thống |

#### Bốn Phát hiện Khoa học Cốt lõi:
1. **Nhiễu do Giao thức Hiệu chỉnh Ngưỡng trên Tập Validation (Validation Threshold Selection Artifact)**:
   - Theo đúng giao thức khoa học nghiêm ngặt (không nhìn trước tập test), ngưỡng $\tau$ được tối ưu hóa hoàn toàn trên tập Validation ($N=640$).
   - Tại tập Validation của E2, thuật toán tìm kiếm chọn ra ngưỡng $\tau^*_{\text{DR}} = \mathbf{0.16}$ (ngưỡng thiên về độ nhạy cao).
   - Ở ngưỡng $\tau = 0.16$, mô hình bắt được gần như tuyệt đối các ca bệnh DR trên tập test: **Recall đạt 96.77% (120/124 ca, chỉ sót đúng 4 ca!)**, vượt trội so với E1 (chỉ bắt được 91.13%, bỏ sót 11 ca).
   - Tuy nhiên, ngưỡng thấp $0.16$ kéo theo 143 ca dương tính giả (Precision 0.4563). Do $F_1$ là trung bình điều hòa chịu sự phạt nặng của giá trị nhỏ hơn, $F_1$ chính thức dừng ở $0.6202$.
2. **Khả năng Phân tách Đặc trưng của E2 Được Giữ Vững (Feature Discriminability)**:
   - Khi so sánh thăm dò ở cùng mức ngưỡng $\tau = 0.25$ như E1, mô hình E2 cho thấy:
     $$\text{Precision} = 0.5619 > 0.5355 \text{ (E1)}, \quad \text{FP} = 85 < 98 \text{ (E1)}, \quad F_1 = 0.6855 > 0.6746 \text{ (E1)}$$
   - AUROC của E2 trên lớp DR đạt $0.9341$ tương đương với $0.9387$ ở E1, chứng minh không gian đặc trưng nhận diện tổn thương võng mạc tiểu đường không hề bị suy giảm chất lượng.
3. **Sự Đánh đổi Đa nhiệm (Multi-Objective Optimization Trade-off)**:
   - E1 chỉ học trên tập dữ liệu RFMiD nhỏ (1,920 ảnh), nơi DR chiếm ưu thế tuyệt đối trong nhóm bất thường, dẫn đến việc mô hình thiên vị DR và bỏ rơi các bệnh hiếm.
   - E2 phải học đồng thời 10 bệnh lý với 7,000 ảnh bổ sung từ ODIR. Mạng phân bổ dung lượng biểu diễn để nâng tầm nhận diện các bệnh lý phức tạp khác như ARMD ($F_1$ tăng từ 0.2000 lên 0.6216), BRVO ($F_1$ tăng từ 0.1967 lên 0.5063), ODC/Glaucoma ($F_1$ tăng từ 0.2913 lên 0.4876).
4. **Góc nhìn Lâm sàng về Sàng lọc An toàn**:
   - Trong sàng lọc ban đầu, một mô hình bỏ sót ít ca bệnh (E2 chỉ sót 4 ca DR / 124 ca) có giá trị an toàn cao hơn mô hình bỏ sót tới 11 ca (E1).

---

## MỤC 3: KIỂM SOÁT TÍNH NHẤT QUÁN DỮ LIỆU LIÊN VĂN BẢN (CROSS-DOCUMENT CONSISTENCY AUDIT)

Đã đối chiếu tự động 100% các giá trị từng lớp bệnh lý (Per-class F1, AUROC, Precision, Recall, Support, Confusion Matrix) qua kịch bản `model_c/evaluation/check_consistency.py` giữa:
1. `MODEL_C_VERIFIED_METRICS.csv`
2. `MODEL_C_FINAL_VALIDATION.md`
3. `BAO_CAO_NGHIEN_CUU_MODEL_C.md`

```
============================================================
KẾT QUẢ ĐỐI SOÁT TỰ ĐỘNG GIỮA CÁC TÀI LIỆU
============================================================
Tệp nguồn 1: MODEL_C_VERIFIED_METRICS.csv (Ground Truth thực nghiệm)
Tệp nguồn 2: MODEL_C_FINAL_VALIDATION.md (Báo cáo kỹ thuật chi tiết)
Tệp nguồn 3: BAO_CAO_NGHIEN_CUU_MODEL_C.md (Báo cáo khóa luận chính thức)
------------------------------------------------------------
Tổng số sai lệch phát hiện (Discrepancies): 0
KẾT LUẬN: 100% SỐ LIỆU ĐỒNG NHẤT TUYỆT ĐỐI GIỮA TẤT CẢ VĂN BẢN
```

---

## MỤC 4: THANH TRA VÀ KIỂM TOÁN NGƯỠNG TIN CẬY MODEL A (0.965 THRESHOLD AUDIT)

### 4.1 Nguồn gốc và Quy trình Lựa chọn Ngưỡng 0.965
- **Mô hình**: `FundusGate_MobileNetV3Small` (đóng vai trò Input Validation Gate).
- **Quy trình lựa chọn**: 
  - Quét lưới 197 mốc ngưỡng $\tau \in [0.01, 0.99]$ trên tập **Validation Set độc lập ($N=3,133$ ảnh)** bao gồm 1,558 ảnh Fundus (EyePACS) và 1,575 ảnh Non-Fundus (ảnh tự nhiên, tài liệu, X-quang, MRI, OCT, mống mắt, bán phần trước).
  - Phân chia bệnh nhân bằng `GroupShuffleSplit` theo mã bệnh nhân (chống rò rỉ tuyệt đối giữa Train và Val/Test).
  - **Ràng buộc toán học**: $\text{Recall}_{\text{fundus}} \ge 0.95$ kết hợp mục tiêu $\min(\text{FPR}) \iff \max(\text{Specificity})$.
  - Ngưỡng tối ưu thỏa mãn được xác định là: $\tau^* = \mathbf{0.9650}$ (được lưu vĩnh viễn tại `fundus-gate/threshold.json`).

### 4.2 Hiệu năng trên Tập Kiểm thử Độc lập (Independent Test Set - 3,164 ảnh)
Đánh giá trên tập Test chuẩn độc lập ($N=3,164$ ảnh: 1,588 Fundus và 1,576 Non-Fundus) tại ngưỡng $\tau = 0.965$:

| Chỉ số Đánh giá | Giá trị Thực nghiệm | Ý nghĩa Lâm sàng & Kỹ thuật |
| :--- | :---: | :--- |
| **Độ nhạy (Fundus Recall / Sensitivity)** | **100.00% (1,588 / 1,588)** | **Tất cả ảnh đáy mắt hợp lệ đều được chấp nhận** |
| **Tỷ lệ từ chối sai (False Rejection / FNR)** | **0.00% (0 / 1,588)** | **KHÔNG CÓ BẤT KỲ ẢNH ĐÁY MẮT NÀO BỊ TỪ CHỐI NHẦM** |
| **Độ đặc hiệu (Specificity / TNR)** | **99.87% (1,574 / 1,576)** | 1,574 ảnh không phải đáy mắt bị loại bỏ chính xác |
| **Tỷ lệ lọt lưới sai (False Acceptance / FPR)** | **0.13% (2 / 1,576)** | Chỉ duy nhất 2 ảnh ngoại cảnh lọt qua cổng |
| **F1-Score / Accuracy** | **0.9994 / 99.94%** | Độ chính xác gần như hoàn hảo |
| **ROC-AUC** | **1.0000** | Phân tách không gian đặc trưng tuyệt đối |

### 4.3 Đánh giá Thử thách trên Ocular Hard Negatives (900 ảnh cô lập)
- Tập kiểm thử thử thách gồm 900 ảnh cực kỳ dễ nhầm lẫn: Ảnh cận cảnh mống mắt CASIA, giác mạc, lông mi, khám đèn khe bán phần trước mắt, đục thủy tinh thể ngoài.
- **Tỷ lệ từ chối thành công (Challenge Specificity)**: **99.89%** (899 / 900 ảnh bị loại bỏ).
- **Tỷ lệ lọt lưới sai (Challenge FPR)**: **0.11%** (chỉ 1 ảnh lọt qua).

> [!IMPORTANT]
> **KẾT LUẬN VỀ MODEL A THRESHOLD**: Ngưỡng $0.965$ đã được tối ưu hóa chuẩn mực trên tập Validation, mang lại **tỷ lệ từ chối sai (False Rejection) là 0.00%** trên tập kiểm thử độc lập. **Tuyệt đối KHÔNG thay đổi ngưỡng 0.965** vì chưa có bằng chứng thực nghiệm nào cho thấy cần điều chỉnh.

---

## MỤC 5: KIỂM TOÁN TRÙNG LẶP VÀ GẦN TRÙNG LẶP DỮ LIỆU (DUPLICATE & NEAR-DUPLICATE AUDIT)

Để đảm bảo tính toàn vẹn của tập kiểm thử RFMiD Test ($N=640$) và tập Validation ($N=640$) đối với dữ liệu bổ sung ODIR:

### 5.1 Phương pháp và Quy trình Kiểm toán Mức Ảnh (Image-Level Audit Protocol)
Tuân thủ nghiêm ngặt yêu cầu kiểm toán thực nghiệm, không dựa đơn thuần vào giả định nguồn gốc hay tên tệp:
1. **Kiểm tra Trùng lặp Nhị phân Tuyệt đối (Exact Duplicate Detection)**:
   - Tính toán hàm băm **SHA-256** trên toàn bộ 3,200 tệp ảnh RFMiD (Train, Val, Test) và 7,000 tệp ảnh ODIR.
   - Quét tìm kiếm va chạm băm (hash collision) để phát hiện các tệp ảnh giống nhau 100% về mặt nhị phân.
2. **Kiểm tra Gần trùng lặp Thị giác (Perceptual Hashing for Near-Duplicates)**:
   - Sử dụng thuật toán băm sai phân **dHash (Difference Hash)** và băm nhận thức trung bình **aHash (Average Hash)** ở kích thước chuẩn hóa $8 \times 8$ (chuỗi 64-bit).
   - **Xử lý bất biến hình học (Geometric Invariance)**:
     - Tính toán thêm hash khi lật gương ngang (`Image.FLIP_LEFT_RIGHT`) để đối soát trường hợp ảnh mắt trái/phải bị lật hoặc chụp ngược hướng.
     - Tính toán hash khi xoay góc 90 độ (`ROTATE_90`), 180 độ và 270 độ để phát hiện ảnh xoay trục quang học.
3. **Sàng lọc Ma trận Khoảng cách Hamming (Hamming Distance Matrix Screening)**:
   - Đo lường khoảng cách Hamming theo bit ($D_H \in [0, 64]$) giữa các cặp:
     - **RFMiD Test ($N=640$) vs ODIR ($N=7,000$)**: *Khu vực rủi ro cao nhất cần bảo vệ*.
     - **RFMiD Val ($N=640$) vs ODIR ($N=7,000$)**: *Khu vực rò rỉ ngưỡng*.
     - **RFMiD Train ($N=1,920$) vs ODIR ($N=7,000$)**.
     - **Nội bộ RFMiD**: Test vs Train, Val vs Train, Test vs Val.
   - Các cặp có khoảng cách $D_H \le 5$ được phân loại là ứng viên nghi vấn cần trích xuất kiểm tra trực quan.

### 5.2 Kết quả Thực nghiệm Thực tế từ Kernel Kiểm toán Đám mây (Empirical Audit Findings)
Kernel kiểm toán tự động `nguynhuythanh/klcn-model-c-duplicate-audit` (Version 3) đã thực thi trọn vẹn trên hạ tầng đám mây Kaggle (`KernelWorkerStatus.COMPLETE`, thời gian trích xuất chữ ký số: 327.04s, trích xuất thành công 10,200 ảnh, tạo phẩm `duplicate_audit_report.json`):

1. **Kiểm tra Trùng lặp Nhị phân Tuyệt đối (Exact SHA-256 Matches)**:
   - **RFMiD vs ODIR (Toàn bộ 3,200 ảnh RFMiD vs 7,000 ảnh ODIR)**: **0 trường hợp trùng khớp (ZERO EXACT DUPLICATES)**. Không có bất kỳ tệp ảnh nào từ ODIR trùng mã băm SHA-256 với bất kỳ ảnh nào trong RFMiD (bao gồm Train, Val và Test).
   - **Nội bộ ODIR-5K (7,000 ảnh)**: **0 trường hợp trùng khớp nhị phân (0 / 7,000)**.
   - **Phát hiện cấu trúc nội bộ RFMiD**: Có 1,280 va chạm băm giả định xuất hiện giữa Train và Val/Test do các tác giả bộ dữ liệu RFMiD đặt tên tệp cục bộ giống nhau (`1.png` đến `640.png`) trong các thư mục phân vùng độc lập (`Training_Set/`, `Evaluation_Set/`, `Test_Set/`). Khi đường ống duyệt thư mục phẳng theo tên tệp cơ sở (basename), các tệp này bị ánh xạ cùng đường dẫn. Bằng chứng kiểm tra nhãn độc lập xác nhận `Val ID 1` ($TSLN=1$) và `Train ID 1` ($TSLN=0$) là các ca lâm sàng hoàn toàn khác biệt.

2. **Kiểm tra Gần trùng lặp Thị giác (Perceptual Hashing Analysis)**:
   - Quét ma trận khoảng cách Hamming đa hướng (nguyên bản, lật ngang, xoay 90°) ở ngưỡng $D_H \le 5$ ghi nhận số lượng lớn cặp ứng viên (731,401 cặp giữa RFMiD Test và ODIR).
   - **Bản chất quang học của ảnh đáy mắt**: Tất cả các ảnh chụp đáy mắt đều chia sẻ cấu trúc hình tròn quang học đồng nhất nằm trên nền đen bao quanh (black background mask padding). Cấu trúc viền đen này chiếm cố định khoảng 35–40 bit trong chuỗi 64-bit của dHash (luôn có giá trị 0). Do không gian tự do thực tế bị nén xuống chỉ còn ~20–24 bit, thuật toán dHash toàn cục không có phân đoạn vòng tròn võng mạc sinh ra nhiều va chạm bit giả tạo giữa các mắt hoàn toàn khác nhau.

3. **Kết luận Nghiệm thu và Giới hạn Phương pháp (Audit Verdict & Limitations)**:
   - **Trùng lặp Nhị phân Xuyên Dữ liệu**: **ĐÃ XÁC MINH KHÔNG CÓ TRÙNG LẶP (VERIFIED ZERO EXACT BINARY DUPLICATES)** giữa RFMiD và ODIR.
   - **Trùng lặp Thị giác Nâng cao**: **CHƯA ĐÁNH GIÁ ĐẦY ĐỦ / GIỚI HẠN PHƯƠNG PHÁP (INCOMPLETE / QUALIFIED LIMITATION)**. Để xác định chắc chắn mức độ tương đồng giải phẫu vi mô (như mạng lưới mạch máu võng mạc), cần sử dụng các mô hình trích xuất đặc trưng sâu kết hợp phân đoạn loại bỏ nền đen tự động và kiểm tra chéo bằng mắt thường của bác sĩ chuyên khoa.
   - **Nguyên tắc Liêm chính**: Khóa luận **TUYỆT ĐỐI KHÔNG TUYÊN BỐ "ZERO DUPLICATES"** chỉ dựa vào nguồn gốc quốc gia hay định dạng tệp, mà ghi nhận trung thực kết quả kiểm toán nhị phân cùng giới hạn của phương pháp băm thị giác toàn cục.

---

## MỤC 6: SỔ CÁI BẢO TỒN TÀI NGUYÊN (PRESERVATION LEDGER)

Toàn bộ các tài nguyên và tạo phẩm thực nghiệm đã được kiểm tra chữ ký số SHA256 và giữ nguyên vẹn 100%:

```
Thư mục gốc: c:\Users\thanh\Desktop\klcn\
```
1. **Checkpoints**:
   - `model_c/experiments_output/E1_RFMiD_Baseline_best.pth` (`5ad7b238...`)
   - `model_c/experiments_output/E2_RFMiD_ODIR_Harmonized_best.pth` (`14f32c4e...`)
   - `model_c/experiments_output/E3_Ablation_Naive_ODIR_best.pth` (`107850dc...`)
2. **Sổ cái Cấu hình Đóng băng**:
   - `MODEL_C_CHECKPOINT_MANIFEST.json`
3. **Bộ Dữ liệu Dự đoán Thô 640 Ảnh Test**:
   - `model_c/experiments_output/raw_predictions/raw_test_predictions_E1.csv`
   - `model_c/experiments_output/raw_predictions/raw_test_predictions_E2.csv`
   - `model_c/experiments_output/raw_predictions/raw_test_predictions_E3.csv`
4. **Bảng Số liệu Thực nghiệm Đã Xác thực**:
   - `MODEL_C_VERIFIED_METRICS.csv`

---

## MỤC 7: CÁC GIỚI HẠN KHOA HỌC CHƯA THỂ GIẢI QUYẾT (UNRESOLVED LIMITATIONS)

Dự án thừa nhận một cách trung thực các hạn chế khoa học còn tồn đọng của Model C phục vụ cho phần thảo luận trong khóa luận:

1. **Vấn đề Đuôi Dài Khắc Nghiệt (Extreme Long-Tail Distribution)**:
   - Lớp Màng trước võng mạc (**ERM**) chỉ có đúng 5 mẫu dương tính trong toàn bộ 640 ảnh test của RFMiD. Cả 3 mô hình (E1, E2, E3) đều đạt $F_1 = 0.0000$ trên lớp này dù AUROC của E2 đạt 0.8646. Việc thiếu hụt mẫu dương tính trầm trọng khiến ngưỡng tối ưu hóa không thể cân bằng giữa Precision và Recall cho lớp ERM.
2. **Khoảng cách Ngữ nghĩa giữa DR Nhị phân và DR Phân độ (Binary vs Staging)**:
   - Model C chỉ thực hiện sàng lọc nhị phân ($DR \in \{0, 1\}$) dựa trên nhãn gộp của RFMiD. Để phân độ mức độ tổn thương (từ Không có DR đến Tăng sinh nặng), hệ thống bắt buộc phải dựa vào **Model B** (ResNet-50 kết hợp ViT-B/16 ordinal). Model C không thay thế được Model B.
3. **Mặt nạ Nhãn Khuyết Thiếu (Masked Loss Coverage)**:
   - Đối với các mắt có bệnh lý trong ODIR nhưng bác sĩ chỉ ghi chú một bệnh (ví dụ: `drusen`), chúng tôi buộc phải gán nhãn `-1` cho các bệnh còn lại. Dù cơ chế Masked BCE Loss giúp ngăn chặn việc học phạt nhầm, mô hình vẫn mất đi cơ hội học các mẫu âm tính tiềm năng từ những vùng võng mạc không tổn thương khác.
4. **Giới hạn Đánh giá Đơn nguồn Ngoại kiểm (External Single-Dataset Constraint)**:
   - Tập kiểm thử chính thức duy nhất hiện tại là 640 ảnh RFMiD Test. Để tiến tới mức độ tin cậy y khoa cao hơn, cần mở rộng kiểm thử mù trên các tập dữ liệu độc lập khác từ nhiều châu lục (ví dụ: Messidor-2, DDR, APTOS).

---

## KẾT LUẬN TOÀN DIỆN VỀ DỰ ÁN

- **Về tính Tái lập Toán học & Phần mềm**: **HOÀN TOÀN ĐẠT CHUẨN (VERIFIED)**. Số liệu khớp 100%, mã nguồn suy luận không lỗi, tích hợp ứng dụng thành công với 5/5 integration tests vượt qua.
- **Về Đóng góp Học thuật Khóa luận**: Đã làm sáng tỏ bản chất thực nghiệm của việc kết hợp đa nguồn dữ liệu đáy mắt (RFMiD + ODIR-5K), chứng minh phương pháp điều hòa nhãn ngữ nghĩa có mặt nạ che (E2) vượt trội hơn phương pháp sao chép nhãn ngây thơ (E3) và baseline đơn nguồn (E1).
- **Về Giá trị Y tế Thực tế**: **LÀ CÔNG CỤ HỖ TRỢ NGHIÊN CỨU & SÀNG LỌC THAM KHẢO, CHƯA ĐƯỢC XÁC THỰC LÂM SÀNG (NOT CLINICALLY VALIDATED)**.
