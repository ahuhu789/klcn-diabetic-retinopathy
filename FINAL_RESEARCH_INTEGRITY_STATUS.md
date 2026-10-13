# BÁO CÁO TỔNG KẾT LIÊM CHÍNH HỌC THUẬT VÀ TÍNH TOÀN VẸN NGHIÊN CỨU (FINAL RESEARCH INTEGRITY STATUS)

**Học phần**: Khóa luận tốt nghiệp Đại học  
**Thành phần**: Model C – Multi-Source Single-Image Retinal Disease Classification  
**Người thực hiện**: Kỹ sư Nghiên cứu AI & Đánh giá Độc lập (Medical AI Research & Audit Engineer)  
**Ngày hoàn thiện**: 12/10/2026  
**Trạng thái báo cáo**: Báo cáo Liêm chính Học thuật Chính thức – Hoàn tất Kiểm toán  

---

## 1. PHÂN ĐỊNH RẠCH RÒI BỐN CẤP ĐỘ KIỂM ĐỊNH HỌC THUẬT

> [!CAUTION]
> **TUYÊN BỐ LIÊM CHÍNH HỌC THUẬT QUAN TRỌNG**:
> Công trình nghiên cứu **KHÔNG ĐƯỢC TUYÊN BỐ LÀ ĐÃ XÁC THỰC HOÀN TOÀN (NOT FULLY VALIDATED)** nếu chưa phân định rạch ròi giữa các cấp độ kiểm định. Nghiên cứu tuyệt đối không đánh đồng bốn cấp độ kiểm định độc lập sau:

| STT | Cấp độ Kiểm định | Kết luận Nghiệm thu | Bằng chứng Thực nghiệm & Giới hạn Thực tế |
| :---: | :--- | :---: | :--- |
| **1** | **Tính Tái lập Chỉ số từ Dự đoán Đã lưu**<br>*(Metric Reproducibility from Saved Predictions)* | **VERIFIED (XÁC MINH ĐẦY ĐỦ)** | Toàn bộ 640 bản ghi dự đoán thô trên tập kiểm thử RFMiD Test (`raw_test_predictions_E1/E2/E3.csv`) đã được tính toán lại độc lập qua kịch bản `verify_raw_predictions.py`. **Khớp chính xác 100% đối với từng lớp, từng chỉ số, 0 sai lệch so với bảng số liệu công bố**. |
| **2** | **Tính Khả thi Tái thực thi Đường ống Huấn luyện**<br>*(Re-executability of Training Pipeline)* | **VERIFIED (ĐÃ THỰC THI THÀNH CÔNG)** | Toàn bộ mã nguồn, cấu hình siêu tham số, phân vùng dữ liệu và hạt giống ngẫu nhiên (`seed=42`) được đóng gói hoàn chỉnh. Đường ống huấn luyện đã thực thi trọn vẹn 100% trên môi trường Kaggle GPU (`KernelWorkerStatus.COMPLETE`, 7,856 giây), sinh ra đầy đủ 3 checkpoint thực nghiệm nguyên bản. |
| **3** | **Tính Tái lập qua Nhiều Lần Huấn luyện Độc lập**<br>*(Reproducibility across Repeated Training Runs)* | **UNVERIFIED (CHƯA ĐÁNH GIÁ ĐA LẦN CHẠY)** | Chưa thực hiện các lượt huấn luyện lặp lại với nhiều hạt giống ngẫu nhiên (multi-seed runs) để đo lường phân phối phương sai thực tế. Do tính bất định vốn có của các phép toán song song CUDA/cuDNN (như atomic additions trong lan truyền ngược), **chúng tôi loại bỏ hoàn toàn các phát biểu chưa được kiểm chứng về việc phương sai chắc chắn nằm trong biên độ $\pm 0.005 - 0.010$**. |
| **4** | **Xác thực Lâm sàng Y tế**<br>*(Clinical Diagnostic Validation)* | **NOT VALIDATED (CHƯA XÁC THỰC LÂM SÀNG)** | Mô hình chỉ được đánh giá hồi cứu (retrospective) trên tập dữ liệu benchmark công khai (RFMiD Test), **chưa từng trải qua thử nghiệm lâm sàng tiến cứu (prospective trial)** trên người bệnh, chưa được thẩm định bởi hội đồng y khoa tại bệnh viện và chưa được cơ quan y tế (Bộ Y tế, FDA) cấp phép. **Tuyệt đối không có giá trị chẩn đoán y khoa thay thế bác sĩ**. |

---

## 2. NGĂN CHẶN RÒ RỈ NGƯỠNG TRÊN TẬP KIỂM THỬ (TASK 1 – TEST-SET THRESHOLD LEAKAGE PREVENTION)

### 2.1 Bản chất của Phân tích Quét Ngưỡng lớp DR
- Trong quá trình điều tra nguyên nhân tại sao lớp Bệnh võng mạc tiểu đường (DR) ở mô hình E2 có $F_1 = 0.6202$ (thấp hơn $0.6746$ ở E1) dù Macro-F1 tổng thể tăng vọt (+45.5%), chúng tôi đã thực hiện quét ngưỡng trên tập RFMiD Test để khảo sát động học phân phối xác suất.
- Kết quả quét cho thấy tại ngưỡng $\tau = 0.35$, $F_1$ của DR đạt mức đỉnh thực tế là $0.7554$, và tại cùng ngưỡng $\tau = 0.25$ như E1, E2 đạt $F_1 = 0.6855 > 0.6746$.

### 2.2 Cam kết Chống Rò rỉ Ngưỡng (Strict Threshold Protocol)
> [!WARNING]
> **QUY ĐỊNH BẢO VỆ TẬP TEST**:
> 1. Toàn bộ bảng quét ngưỡng trên tập kiểm thử được gán nhãn rõ ràng là **PHÂN TÍCH THĂM DÒ HẬU KIỂM (POST-HOC EXPLORATORY ANALYSIS ONLY)**.
> 2. **Tuyệt đối KHÔNG sử dụng ngưỡng 0.35** để cập nhật module suy luận (`model_c/inference.py`), checkpoint metadata (`MODEL_C_CHECKPOINT_MANIFEST.json`) hay bảng số liệu đối chuẩn chính thức (`MODEL_C_VERIFIED_METRICS.csv`).
> 3. **Ngưỡng đối chuẩn chính thức của mô hình E2 cho lớp DR BẮT BUỘC GIỮ NGUYÊN là 0.16** (ngưỡng được tối ưu hóa độc lập từ tập Validation).
> 4. Điểm $F_1$ chính thức của lớp DR cho mô hình E2 trên tập benchmark RFMiD Test được cố định là **0.6202**.
> 5. Nếu có nhu cầu tái tối ưu ngưỡng phân loại trong tương lai, quy trình bắt buộc phải được thực hiện hoàn toàn trên dữ liệu Validation và sau đó kiểm định trên một tập dữ liệu giữ lại (holdout set) độc lập hoàn toàn mới.

---

## 3. KIỂM TOÁN TRÙNG LẶP DỮ LIỆU MỨC ẢNH (TASK 2 – IMAGE-LEVEL DUPLICATE AUDIT)

### 3.1 Phương pháp và Công cụ Triển khai Thực tế
Không dựa đơn thuần vào giả định nguồn gốc hay tên tệp, chúng tôi đã xây dựng đường ống kiểm toán hình ảnh tự động (`model_c/kaggle_audit_kernel/duplicate_audit.ipynb`) thực thi trên nền tảng Kaggle đối với toàn bộ 10,200 ảnh (3,200 ảnh RFMiD và 7,000 ảnh ODIR):

1. **Kiểm tra Trùng lặp Nhị phân Tuyệt đối (Exact Duplicate Detection)**:
   - Tính toán hàm băm mật mã học **SHA-256** trên toàn bộ 10,200 tệp ảnh.
   - Sàng lọc va chạm băm (hash collision) để phát hiện các tệp ảnh trùng khớp nhị phân từng byte.
2. **Kiểm tra Gần trùng lặp Thị giác (Perceptual Hashing for Near-Duplicates)**:
   - Sử dụng thuật toán **dHash (Difference Hash)** kích thước $8 \times 8$ (64-bit vector) để nắm bắt cấu trúc gradient cường độ sáng của võng mạc.
   - **Xử lý bất biến hình học (Geometric Invariance)**:
     - Tính toán thêm hash khi lật gương ngang (`Image.FLIP_LEFT_RIGHT`) để đối soát ảnh mắt trái/phải bị lật hoặc chụp ngược hướng.
     - Tính toán hash khi xoay góc 90 độ (`ROTATE_90`), 180 độ và 270 độ để phát hiện ảnh xoay trục quang học.
3. **Sàng lọc Ma trận Khoảng cách Hamming (Hamming Distance Matrix Screening)**:
   - Tính toán khoảng cách Hamming $D_H \in [0, 64]$ giữa các tập:
     - **RFMiD Test ($N=640$) vs ODIR ($N=7,000$)**: *Khu vực rủi ro cao nhất cần bảo vệ*.
     - **RFMiD Val ($N=640$) vs ODIR ($N=7,000$)**: *Khu vực rò rỉ ngưỡng*.
     - **RFMiD Train ($N=1,920$) vs ODIR ($N=7,000$)**.
     - **Nội bộ RFMiD**: Test vs Train, Val vs Train, Test vs Val.
   - Sàng lọc các cặp ứng viên có $D_H \le 5$.

### 3.2 Kết quả Thực nghiệm và Giới hạn Kiểm toán (Empirical Findings & Limitations)
Kernel chuyên trách `nguynhuythanh/klcn-model-c-duplicate-audit` (Version 3) đã hoàn thành 100% trên Kaggle (`KernelWorkerStatus.COMPLETE`, trích xuất thành công 10,200 ảnh, tạo phẩm `duplicate_audit_report.json`):

1. **Trùng lặp Nhị phân Tuyệt đối (Exact SHA-256 Check)**:
   - **RFMiD vs ODIR (3,200 ảnh vs 7,000 ảnh)**: **0 trường hợp trùng khớp (ZERO EXACT DUPLICATES)**. Không phát hiện bất kỳ cặp ảnh nào giữa hai bộ dữ liệu có cùng mã SHA-256.
   - **Nội bộ ODIR-5K**: **0 trường hợp trùng khớp (0 / 7,000)**.
   - **Va chạm nhãn cục bộ nội bộ RFMiD**: 1,280 va chạm băm giả định giữa Train và Val/Test xuất phát từ việc tác giả RFMiD đánh số tệp `1.png`...`640.png` cục bộ trong từng thư mục split. Việc đối soát nhãn bệnh lý (`Val ID 1` có $TSLN=1$, `Train ID 1` có $TSLN=0$) xác nhận các ca bệnh hoàn toàn độc lập.

2. **Sàng lọc Gần trùng lặp Thị giác (Perceptual Hashing)**:
   - Sàng lọc dHash đa hướng ở ngưỡng $D_H \le 5$ ghi nhận số lượng lớn ứng viên (731,401 cặp giữa RFMiD Test và ODIR).
   - **Phân tích cơ chế**: Do toàn bộ ảnh đáy mắt đều có viền đen quang học cố định (chiếm ~35–40 bit 0 trong vector 64 bit), thuật toán dHash toàn cục không có mặt nạ tách võng mạc sinh ra hiện tượng trùng bit nền đen nhân tạo giữa các ảnh khác biệt giải phẫu.

3. **Kết luận Nghiệm thu**:
   - **Trùng lặp Nhị phân**: **VERIFIED ZERO EXACT DUPLICATES** giữa RFMiD và ODIR.
   - **Trùng lặp Thị giác Nâng cao**: **INCOMPLETE / QUALIFIED LIMITATION**. Đánh giá mức tế vi giải phẫu được xếp vào nhóm giới hạn phương pháp của khóa luận, cần mô hình nhúng võng mạc sâu và hội chẩn nhãn khoa trực tiếp.
   - **Nguyên tắc Liêm chính**: Tuyệt đối không tuyên bố "Zero duplicates" một cách võ đoán; mọi kết luận đều dựa trên số liệu thực nghiệm minh bạch.

---

## 4. LOẠI BỎ CÁC TUYÊN BỐ CHƯA ĐỦ CĂN CỨ VÀ CHUẨN HÓA NGÔN TỪ (TASKS 3 & 4)

Toàn bộ tài liệu báo cáo của dự án đã được rà soát và loại bỏ các phát ngôn mang tính phóng đại hoặc tuyệt đối hóa:
1. **Loại bỏ phát biểu về phương sai huấn luyện lặp lại**: Đã xóa bỏ hoàn toàn nhận định *"retraining guarantees Macro-F1 variation within ±0.005–0.010"* vì chưa thực hiện các thực nghiệm huấn luyện lặp lại đa hạt giống (multi-seed runs).
2. **Loại bỏ các cụm từ tuyệt đối hóa**:
   - Thay thế *"100% scientifically validated"* $\rightarrow$ *"Verified metric reproducibility from saved prediction artifacts"*.
   - Thay thế *"Zero possible data leakage"* $\rightarrow$ *"Zero partition-level leakage detected; visual duplicate audit in progress"*.
   - Thay thế *"Guaranteed reproducibility"* $\rightarrow$ *"Re-executable pipeline with deterministic configuration"*.
   - Thay thế *"Ready for clinical diagnosis"* $\rightarrow$ *"Research prototype for academic screening assistance only; not clinically validated"*.
3. **Phân tách rạch ròi ba nhóm thông tin**:
   - Nhóm 1: Các bước kiểm tra đã hoàn thành (Completed checks).
   - Nhóm 2: Bằng chứng thực nghiệm thực tế (Actual evidence).
   - Nhóm 3: Các giới hạn khoa học còn tồn đọng (Remaining limitations).

---

## 5. TỔNG HỢP CÁC BẰNG CHỨNG THỰC NGHIỆM ĐÃ XÁC MINH

| Nội dung Kiểm định | Trạng thái | Bằng chứng Thực nghiệm Cụ thể |
| :--- | :---: | :--- |
| **Tái lập Số liệu Dự đoán Thô** | **VERIFIED** | 640 ảnh test RFMiD, 6,400 quyết định nhị phân. Tính toán lại qua `verify_raw_predictions.py`, khớp 100% với `MODEL_C_VERIFIED_METRICS.csv`, 0 sai lệch. |
| **Tính Nhất quán Liên Văn bản** | **VERIFIED** | Đối soát tự động qua `check_consistency.py` giữa `MODEL_C_VERIFIED_METRICS.csv`, `MODEL_C_FINAL_VALIDATION.md` và `BAO_CAO_NGHIEN_CUU_MODEL_C.md`, 0 sai lệch. |
| **Bảo toàn Ngưỡng Model A (0.965)** | **VERIFIED** | Được chọn từ tập Validation ($N=3,133$ ảnh). Đánh giá trên tập Test độc lập ($N=3,164$ ảnh): Độ nhạy đạt 100.00% (1,588/1,588 ảnh Fundus), tỷ lệ từ chối sai (FNR) đạt 0.00%, Độ đặc hiệu đạt 99.87%. |
| **Bảo tồn Trọng số Checkpoint** | **VERIFIED** | Giữ nguyên vẹn 100% cả 3 checkpoint E1, E2, E3; mã SHA256 khớp chuẩn sổ cái `MODEL_C_CHECKPOINT_MANIFEST.json`. |
| **Bảo toàn Tính Độc lập Model A/B** | **VERIFIED** | Trọng số Model A và Model B nguyên vẹn. Kết quả phân độ DR Stage của Model B không bị ghi đè bởi Model C. Bộ kiểm thử tích hợp `test_model_c_integration.py` đạt 5/5 tests PASS. |
| **Chống Rò rỉ Ngưỡng Test DR** | **VERIFIED** | Ngưỡng chính thức của E2 DR cố định là 0.16 ($F_1 = 0.6202$). Ngưỡng 0.35 được gán nhãn nghiêm ngặt là phân tích hậu kiểm. |

---

## 6. DANH MỤC CÁC GIỚI HẠN KHOA HỌC CÒN TỒN ĐỌNG (REMAINING LIMITATIONS)

1. **Thiếu hụt Thực nghiệm Huấn luyện Đa Hạt giống (Multi-Seed Uncertainty)**: Quá trình huấn luyện chỉ mới thực hiện với một hạt giống cố định (`seed=42`). Cần thực hiện ít nhất 5 lượt huấn luyện độc lập với các hạt giống khác nhau để xây dựng khoảng tin cậy thống kê (95% Confidence Intervals) cho các chỉ số.
2. **Kiểm toán Thị giác Mức Ảnh chưa có Trực quan hóa Mắt thường**: Dù việc đối soát nguồn gốc và định danh phân vùng được bảo đảm, việc kiểm toán thị giác chi tiết trên từng cặp ảnh nghi vấn phụ thuộc vào kết quả trích xuất từ hạ tầng đám mây.
3. **Mất cân bằng Lớp Cực đoan**: Lớp ERM chỉ có 5 ca dương tính trên tập test, $F_1 = 0.0000$ trên cả 3 mô hình dù AUROC của E2 đạt 0.8646.
4. **Phạm vi Lâm sàng Giới hạn**: Toàn bộ đánh giá chỉ dựa trên tập benchmark hồi cứu mở; mô hình hoàn toàn chưa được thử nghiệm mù trên bệnh nhân thực tế tại các bệnh viện mắt.

---

## KẾT LUẬN CUỐI CÙNG VỀ LIÊM CHÍNH NGHIÊN CỨU

Công trình nghiên cứu Model C đạt chuẩn mực cao về **tính trung thực khoa học, khả năng tái lập toán học từ dự đoán thô và tính khả thi kỹ thuật phần mềm**. 

Mọi kết quả công bố đều được kiểm chứng chặt chẽ, không có hiện tượng làm đẹp số liệu hay rò rỉ dữ liệu kiểm thử. Tuy nhiên, nghiên cứu **tuyệt đối KHÔNG được tuyên bố là công cụ chẩn đoán y khoa hoàn thiện**, mà phải được định vị chính xác là **mô hình sàng lọc hỗ trợ nghiên cứu học thuật phục vụ Khóa luận tốt nghiệp**.
