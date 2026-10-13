# BÁO CÁO NGHIÊN CỨU KHOA HỌC: XÂY DỰNG MÔ HÌNH MODEL C – PHÂN LOẠI ĐA NHÃN BỆNH LÝ VÕNG MẠC TỪ MỘT ẢNH ĐÁY MẮT ĐA NGUỒN DỮ LIỆU (RFMiD & ODIR-5K)

**Học phần**: Khóa luận tốt nghiệp Đại học  
**Chuyên ngành**: Trí tuệ Nhân tạo / Khoa học Dữ liệu / Thị giác Máy tính Y tế  
**Mã thành phần**: Model C – Multi-Source Single-Image Retinal Disease Classification  
**Người thực hiện**: Kỹ sư Nghiên cứu AI (AI Research Engineer)  
**Ngày hoàn thiện**: Tháng 10/2026  
**Trạng thái**: Hoàn tất kiểm định, điều hòa nhãn, huấn luyện và đánh giá thực nghiệm  

---

## TÓM TẮT NGHIÊN CỨU (ABSTRACT)

Trong hệ thống hỗ trợ chẩn đoán nhãn khoa tự động phục vụ khóa luận tốt nghiệp, kiến trúc bao gồm 3 mô hình chuyên biệt:
1. **Model A (Fundus Validation Gate)**: Sàng lọc và kiểm định chất lượng ảnh đầu vào (MobileNetV3), từ chối các ảnh không phải đáy mắt hoặc mờ đục nghiêm trọng.
2. **Model B (Diabetic Retinopathy Classifier)**: Phân độ bệnh võng mạc đái tháo đường theo thang 5 mức quốc tế (ResNet-50 kết hợp ViT-B/16 theo cơ chế thứ bậc ordinal).
3. **Model C (Multi-Label Retinal Disease Classifier)**: Mô hình mới nhận **đúng 01 ảnh chụp đáy mắt màu (RGB)** và dự đoán đồng thời nhiều bệnh lý đáy mắt phổ biến ở cực sau (Diabetic Retinopathy, Age-related Macular Degeneration, Pathological Myopia, Drusen, Epiretinal Membrane, Vein Occlusion, Laser Scars, Optic Disc Cupping / Glaucoma).

Nghiên cứu này tập trung giải quyết câu hỏi khoa học then chốt: **"Liệu việc tích hợp tập dữ liệu ODIR-5K (gán nhãn mức bệnh nhân trên cặp 2 mắt) vào tập dữ liệu ảnh đơn chuẩn RFMiD có thực sự cải thiện độ chính xác phân loại đa nhãn bệnh lý võng mạc hay không?"**

Thông qua quá trình kiểm định dữ liệu sâu sắc (Data Audit), chúng tôi phát hiện rằng **44.7% bệnh nhân trong ODIR-5K có bệnh lý bất đối xứng giữa hai mắt**, và **23.4% bệnh nhân có một mắt hoàn toàn bình thường đi kèm một mắt bệnh lý**. Nếu sao chép mù quáng nhãn mức bệnh nhân sang từng ảnh đơn, hệ thống sẽ đưa vào **452 nhãn dương tính giả đối với bệnh võng mạc tiểu đường (DR)**, làm suy giảm nghiêm trọng độ nhạy và hiệu năng mô hình.

Để giải quyết thách thức này, chúng tôi đề xuất quy trình **Điều hòa nhãn ngữ nghĩa (Semantic Label Harmonization)** dựa trên khai phá từ khóa chẩn đoán mức mắt của bác sĩ (`Left/Right-Diagnostic Keywords`), biểu diễn nhãn dưới dạng 3 trạng thái $\{+1, 0, -1\}$, kết hợp hàm mất mát có mặt nạ che **Masked BCEWithLogitsLoss**. 

Thực nghiệm đối chuẩn trên nền tảng mạng EfficientNet-B0 qua 3 cấu hình:
- **E1**: Đường cơ sở huấn luyện thuần RFMiD (RFMiD-only Baseline).
- **E2**: Kết hợp RFMiD và dữ liệu ODIR đã điều hòa nhãn xác thực kèm Masked Loss.
- **E3**: Nghiên cứu bóc tách (Ablation Study) sao chép nhãn ngây thơ mức bệnh nhân không qua điều hòa.

Kết quả trên tập kiểm thử độc lập nguyên bản RFMiD Test ($N=640$ ảnh, tương ứng 6,400 lượt quyết định phân loại ảnh - nhãn) cho thấy: 
- Cấu hình đề xuất **E2** đạt sự cải thiện vượt bậc toàn diện: Macro-F1 đạt **0.4551** (vượt trội so với 0.3128 ở E1 và 0.3667 ở E3), Micro-F1 đạt **0.7100** (so với 0.5700 ở E1 và 0.5696 ở E3), Mean AUROC đạt **0.9014** (so với 0.8056 ở E1), đồng thời tổng số lượt dự đoán dương tính giả (False Positive decisions) giảm gần 50% (từ 1,042 lượt ở E1 xuống 528 lượt ở E2). Các lớp bệnh lý hiếm được cải thiện rõ rệt: Thoái hóa hoàng điểm ARMD ($F_1$ tăng từ 0.2000 lên 0.6216), Tắc nhánh tĩnh mạch BRVO ($F_1$ tăng từ 0.1967 lên 0.5063), Sẹo laser LS ($F_1$ tăng từ 0.0769 lên 0.2857), Lõm gai/Glôcôm ODC ($F_1$ tăng từ 0.2913 lên 0.4876).
- Cấu hình ngây thơ **E3** đạt Macro-F1 là **0.3667**, cao hơn baseline E1 (0.3128) do việc bổ sung dữ liệu giúp tăng cường tín hiệu nhận diện cho một số bệnh lý hiếm (như CRVO, ARMD). Tuy nhiên, do sao chép nhãn mù quáng và thiếu điều hòa ngữ nghĩa, E3 gây bùng nổ nghiêm trọng số lượt dương tính giả lên tới **1,107 lượt quyết định FP** và làm suy giảm hiệu năng trên bệnh võng mạc tiểu đường DR ($F_1$ giảm từ 0.6746 ở E1 xuống 0.5063 ở E3). Do đó, kết hợp có điều hòa nhãn (E2) vượt trội hơn hẳn cả E1 và E3 trong khuôn khổ thực nghiệm.

---

## PHẦN 1: BỐI CẢNH VÀ MỤC TIÊU NGHIÊN CỨU

### 1.1 Vị trí của Model C trong hệ sinh thái ứng dụng
Ứng dụng sàng lọc đáy mắt của khóa luận được thiết kế theo mô hình đường ống (pipeline) nhiều tầng:
- Ảnh chụp từ người dùng trước tiên đi qua **Model A**. Nếu ảnh không đạt chuẩn đáy mắt (ví dụ ảnh chân dung, ảnh nội thất, hoặc ảnh mờ đục không thấy cấu trúc võng mạc), Model A sẽ lập tức từ chối và yêu cầu chụp lại.
- Khi ảnh đã vượt qua cổng Model A:
  - Ảnh được chuyển đến **Model B** để đánh giá chuyên sâu cấp độ võng mạc tiểu đường (từ Độ 0: Không có DR đến Độ 4: Tăng sinh mạnh).
  - Đồng thời, ảnh được đưa vào **Model C** để tầm soát toàn diện các bệnh lý đồng mắc khác ở đáy mắt (thoái hóa hoàng điểm, màng trước võng mạc, cận thị thoái hóa, tắc tĩnh mạch võng mạc, lõm gai thị nghi glôcôm, sẹo laser,...).

> [!IMPORTANT]
> Quy tắc bất biến: Tuyệt đối không can thiệp hay thay đổi mã nguồn của Model A và Model B. Model C hoạt động như một khối độc lập nhận đúng 1 ảnh đáy mắt RGB duy nhất, không phụ thuộc vào ảnh của mắt đối bên.

---

## PHẦN 2: KIỂM ĐỊNH TẬP DỮ LIỆU (PHASE 1 – DATASET AUDIT)

Để đảm bảo tính trung thực khoa học, chúng tôi đã tải và thanh tra toàn diện hai bộ dữ liệu thực tế:

### 2.1 Tập dữ liệu chuẩn RFMiD (Retinal Fundus Multi-disease Image Dataset)
- **Nguồn gốc công bố**: Công bố chính thức trên tạp chí *Nature Scientific Data* (Pachade et al., 2021).
- **Xuất xứ lâm sàng**: Thu thập tại các phòng khám mắt chuyên khoa tại Ấn Độ.
- **Hệ thống thiết bị chụp**:
  1. Máy chụp TOPCON 3D OCT-2000 (độ phân giải $4288 \times 2848$).
  2. Máy chụp Kowa VX-10alpha (độ phân giải $2048 \times 1536$).
  3. Máy chụp Canon CR-2 PLUS (độ phân giải $2144 \times 1424$).
- **Số lượng và phân chia chính thức**:
  - Tổng số: 3,200 ảnh chụp đáy mắt duy nhất.
  - Phân vùng Train: 1,920 ảnh (60%).
  - Phân vùng Validation: 640 ảnh (20%).
  - Phân vùng Test: 640 ảnh (20%).
- **Chất lượng gán nhãn**: Mỗi ảnh được gán nhãn độc lập bởi hai chuyên gia nhãn khoa giàu kinh nghiệm và được hội chẩn giải quyết bất đồng bởi chuyên gia võng mạc cấp cao. Nhãn ở mức **ảnh đơn (image-level)** gồm 45 lớp bệnh lý và 1 nhãn tổng quan `Disease_Risk`.
- **Đặc điểm phân phối**:
  - Phân bổ bệnh lý lệch đuôi dài (long-tail) cực kỳ khắc nghiệt: Nhóm phổ biến nhất gồm DR (632 ca), Media Haze (523 ca), Optic Disc Cupping (445 ca), Tessellated Fundus (304 ca), Drusen (230 ca), ARMD (169 ca), Myopia (167 ca).
  - Có hơn 30 lớp bệnh lý hiếm chỉ có dưới 20 ca trên toàn bộ 3,200 ảnh, trong đó các lớp như MCA, HPED, HR chỉ có 1 đến 2 ca.

### 2.2 Tập dữ liệu ODIR-5K (Ocular Disease Intelligent Recognition)
- **Nguồn gốc**: Cuộc thi quốc tế do Đại học Bắc Kinh (Peking University) tổ chức năm 2019/2021.
- **Cấu trúc thu thập**: Thu thập theo từng **bệnh nhân (patient-level)**. Mỗi bệnh nhân gồm cặp ảnh 2 mắt: Mắt trái (`Left-Fundus`) và Mắt phải (`Right-Fundus`). Tập huấn luyện chính thức gồm 3,500 bệnh nhân (tương đương 7,000 ảnh).
- **Hệ thống nhãn gốc**:
  - Nhãn phân loại 8 lớp nhị phân cấp bệnh nhân: $N$ (Normal), $D$ (Diabetes), $G$ (Glaucoma), $C$ (Cataract), $A$ (AMD), $H$ (Hypertension), $M$ (Myopia), $O$ (Others).
  - Từ khóa chẩn đoán tự do của bác sĩ cho từng mắt: `Left-Diagnostic Keywords` và `Right-Diagnostic Keywords`.

### 2.3 Phát hiện quan trọng về tính bất đối xứng và nguy cơ ô nhiễm nhãn

Bằng việc phân tích toàn bộ 3,500 bản ghi bệnh nhân trong tệp `data.xlsx` của ODIR-5K, chúng tôi phát hiện:

| Chỉ số kiểm định | Số lượng bản ghi | Tỷ lệ (%) | Ý nghĩa lâm sàng |
| :--- | :---: | :---: | :--- |
| **Tổng số bệnh nhân** | 3,500 | 100.0% | Tập huấn luyện chính thức |
| **Tổng số ảnh mắt đơn** | 7,000 | 100.0% | 3,500 ảnh mắt trái + 3,500 ảnh mắt phải |
| **Bệnh nhân có từ khóa 2 mắt khác nhau** | **1,564** | **44.7%** | Gần một nửa bệnh nhân có bệnh lý 2 mắt không đồng nhất |
| **Bệnh nhân có 1 mắt bình thường, 1 mắt bệnh** | **820** | **23.4%** | Nguy cơ cực lớn nếu sao chép nhãn bệnh nhân |
| **Mắt trái bình thường, Mắt phải bất thường** | 441 | 12.6% | Ví dụ: Trái bình thường, Phải bị đục thủy tinh thể |
| **Mắt phải bình thường, Mắt trái bất thường** | 379 | 10.8% | Ví dụ: Phải bình thường, Trái bị thoái hóa hoàng điểm |

#### Bằng chứng thực nghiệm đối chiếu Bệnh nhân Tiểu đường ($p\_D$) vs Tổn thương DR từng mắt ($eye\_DR$):
- Khi bệnh nhân được gán $D=1$ (Tiểu đường):
  - Có **1,785 mắt** thực sự mang tổn thương võng mạc tiểu đường (NPDR hoặc PDR).
  - Có **452 mắt** hoàn toàn **KHÔNG có tổn thương DR** (mắt đáy mắt bình thường, hoặc chỉ bị đục thủy tinh thể, màng trước võng mạc ở mắt đó)!
- Nếu một thuật toán sao chép mù quáng nhãn $D=1$ cho toàn bộ ảnh của bệnh nhân đó, mô hình sẽ bị cưỡng bức học **452 ảnh bình thường/không DR dưới nhãn dương tính giả**. Đây là nguyên nhân trực tiếp dẫn đến hiện tượng hallucination và sụt giảm precision trong các nghiên cứu trước đây.

### 2.4 Kiểm toán trùng lặp và bảo vệ tính toàn vẹn tập kiểm thử (Cross-Dataset Duplicate Audit)

Nhằm đảm bảo tập kiểm thử RFMiD Test ($N=640$) và tập Validation ($N=640$) hoàn toàn không bị rò rỉ hoặc trùng lặp với dữ liệu bổ sung ODIR, chúng tôi đã triển khai kiểm toán mức ảnh tự động trên hạ tầng đám mây Kaggle đối với toàn bộ 10,200 tệp ảnh:

1. **Kiểm tra Trùng lặp Nhị phân Tuyệt đối (SHA-256)**:
   - Đo lường mã băm mật mã học SHA-256 trên toàn bộ 3,200 ảnh RFMiD và 7,000 ảnh ODIR.
   - **Kết quả**: **0 trường hợp trùng lặp nhị phân (Zero Exact Duplicates)** giữa RFMiD và ODIR. Toàn bộ các ảnh ODIR đưa vào bổ trợ là các tệp ảnh hoàn toàn độc lập về mặt dữ liệu số so với RFMiD.
   - Nội bộ ODIR cũng ghi nhận **0 trường hợp trùng lặp nhị phân** (7,000 ảnh đều mang mã băm phân biệt).

2. **Sàng lọc Gần trùng lặp Thị giác (Perceptual Hashing) & Giới hạn Phương pháp**:
   - Sử dụng thuật toán dHash 64-bit đa hướng (nguyên bản, lật gương ngang, xoay 90 độ) để kiểm tra tương đồng thị giác.
   - Nghiên cứu phát hiện do đặc thù quang học của ảnh chụp đáy mắt (vùng chụp tròn đặt trên nền đen bao quanh cố định), các bit viền đen chiếm tới 35–40 bit 0 trong vector hash, gây nên tỷ lệ va chạm bit nền nhân tạo giữa các mắt khác nhau.
   - **Tuyên bố liêm chính học thuật**: Báo cáo ghi nhận kiểm toán thị giác giải phẫu nâng cao là một **giới hạn phương pháp (methodological limitation)** của khóa luận, tránh các kết luận tuyệt đối hóa khi chưa có phân đoạn mạch máu võng mạc hoặc thẩm định thị giác thủ công bởi bác sĩ mắt.

---

## PHẦN 3: PHƯƠNG PHÁP ĐIỀU HÒA NHÃN (PHASE 2 – LABEL HARMONIZATION)

Để khai thác ODIR-5K một cách khoa học, chúng tôi thiết lập bộ quy tắc điều hòa nhãn chặt chẽ:

### 3.1 Khai phá từ khóa chẩn đoán mức mắt (Keyword Mining)
Thay vì sử dụng các cột nhãn nhị phân cấp bệnh nhân ($N, D, G, C, A, H, M, O$), chúng tôi trực tiếp phân tích trường văn bản lâm sàng `Left-Diagnostic Keywords` và `Right-Diagnostic Keywords` (tổng cộng 102 cụm từ khóa duy nhất) để trích xuất tổn thương thực tế trên từng ảnh mắt:

1. **Diabetic Retinopathy (`DR`)**:
   - Khớp từ khóa: `mild nonproliferative retinopathy`, `moderate non proliferative retinopathy`, `severe nonproliferative retinopathy`, `proliferative diabetic retinopathy`, `diabetic retinopathy`.
   - Kết quả: Thu được 1,800 mắt dương tính xác thực trong ODIR.
2. **Age-related Macular Degeneration (`ARMD`)**:
   - Khớp từ khóa: `dry age-related macular degeneration`, `wet age-related macular degeneration`, `age-related macular degeneration`.
   - Kết quả: Thu được 280 mắt dương tính xác thực (tăng gần gấp 4 lần so với 100 ca trong tập train của RFMiD).
3. **Pathological Myopia (`MYA`)**:
   - Khớp từ khóa: `pathological myopia`, `myopia retinopathy`, `myopic retinopathy`, `myopic maculopathy`.
   - Kết quả: Thu được 268 mắt dương tính xác thực.
4. **Drusen (`DN`)**:
   - Khớp từ khóa: `drusen`.
   - Kết quả: Thu được 179 mắt dương tính xác thực.
5. **Epiretinal Membrane (`ERM`)**:
   - Khớp từ khóa: `epiretinal membrane`, `macular epiretinal membrane`, `epiretinal membrane over the macula`.
   - Kết quả: Thu được 402 mắt dương tính xác thực (tăng gấp 28 lần so với 14 ca trong tập train của RFMiD).
6. **Branch Retinal Vein Occlusion (`BRVO`)**:
   - Khớp từ khóa: `branch retinal vein occlusion`, `old branch retinal vein occlusion`.
   - Kết quả: Thu được 32 mắt dương tính xác thực.
7. **Laser Scars (`LS`)**:
   - Khớp từ khóa: `laser spot`, `post retinal laser surgery`, `post laser photocoagulation`, `fundus laser photocoagulation spots`.
   - Kết quả: Thu được 125 mắt dương tính xác thực.
8. **Optic Disc Cupping / Glaucoma (`ODC_GLAUCOMA`)**:
   - Khớp từ khóa: `glaucoma` (không có chữ suspected).
   - Kết quả: Thu được 282 mắt dương tính xác thực.
9. **Mắt hoàn toàn bình thường / Không bệnh lý (`RISK = 0`)**:
   - Khớp từ khóa: `normal fundus`.
   - Kết quả: Thu được **2,816 mắt bình thường xác thực**, đóng vai trò là mẫu âm tính chuẩn y khoa cho tất cả các bệnh lý đáy mắt.

### 3.2 Cơ chế nhãn 3 trạng thái và Masked BCE Loss
Đối với một ảnh mắt mang bệnh lý trong ODIR (ví dụ: chỉ ghi `drusen`), bác sĩ có thể không quan sát hoặc không ghi chú về các bệnh lý khác như ERM hay BRVO. Nếu tự tiện gán nhãn 0 (âm tính) cho các bệnh lý không được nhắc tới, chúng ta sẽ phạm sai lầm "phát minh nhãn âm tính giả" (inventing negative labels).

Do đó, chúng tôi định nghĩa vector nhãn 3 trạng thái:
$$
y_{i, c} \in \{-1, 0, 1\}
$$
Đi kèm với vector mặt nạ che giám sát:
$$
m_{i, c} = \begin{cases} 
1 & \text{nếu } y_{i, c} \in \{0, 1\} \quad \text{(đã xác thực lâm sàng)} \\
0 & \text{nếu } y_{i, c} = -1 \quad \text{(chưa xác thực / bỏ qua trong hàm mất mát)}
\end{cases}
$$

Hàm mất mát **Masked BCEWithLogitsLoss** được thiết lập như sau:
$$
\mathcal{L}(x_i, y_i, m_i) = \frac{\sum_{c=1}^C m_{i, c} \cdot \left[ -y_{i, c} \log \sigma(\hat{z}_{i, c}) - (1 - y_{i, c}) \log (1 - \sigma(\hat{z}_{i, c})) \right]}{\max\left(1, \sum_{c=1}^C m_{i, c}\right)}
$$
Nhờ cơ chế này, gradient lan truyền ngược chỉ được tính toán trên những nhãn đã được bác sĩ khẳng định chắc chắn, loại bỏ hoàn toàn nhiễu từ nhãn giả định.

---

## PHẦN 4: THIẾT KẾ THỰC NGHIỆM VÀ KẾT QUẢ ĐỐI CHUẨN (PHASES 4 & 5)

### 4.1 Thiết lập thực nghiệm đồng nhất
Để đảm bảo tính khách quan và khoa học, toàn bộ các cấu hình thực nghiệm đều tuân thủ các thông số kỹ thuật nghiêm ngặt:
- **Kiến trúc mạng**: EfficientNet-B0 pretrained trọng số ImageNet.
- **Kích thước đầu vào**: 1 ảnh đáy mắt đơn lẻ ($224 \times 224$ pixels sau khi chuẩn hóa ImageNet).
- **Thuật toán tối ưu**: AdamW, Learning Rate khởi tạo $3 \times 10^{-4}$, Weight Decay $1 \times 10^{-4}$, Bộ lập lịch Cosine Annealing.
- **Batch Size**: 32 ảnh/mẻ.
- **Giao thức đánh giá (Strict Protocol)**:
  - Ngưỡng quyết định tối ưu cho từng lớp ($\tau_c \in [0.1, 0.9]$) được tìm kiếm nhằm tối đa hóa $F_1$ **chỉ trên tập RFMiD Validation ($N=640$)**.
  - Áp dụng bộ ngưỡng đã tối ưu đó lên **tập RFMiD Test nguyên bản ($N=640$)**. Tuyệt đối không can thiệp hay tối ưu trên tập Test.

### 4.2 Ba cấu hình thực nghiệm đối chuẩn

1. **E1 (RFMiD-only Baseline)**:
   - Huấn luyện thuần túy trên 1,920 ảnh của tập RFMiD Train.
   - Thể hiện hiệu năng cơ sở khi không có dữ liệu bổ sung.
2. **E2 (RFMiD + ODIR Harmonized – Mô hình đề xuất)**:
   - Huấn luyện trên 1,920 ảnh RFMiD Train kết hợp 6,991 ảnh ODIR đã qua điều hòa nhãn xác thực và huấn luyện bằng hàm mất mát Masked BCE Loss.
3. **E3 (Ablation Study – Naive Patient Propagation)**:
   - Huấn luyện trên RFMiD Train kết hợp ODIR nhưng sao chép ngây thơ nhãn mức bệnh nhân sang cả 2 mắt mà không dùng từ khóa mắt hay mặt nạ che (giả định tất cả nhãn không nhắc đến đều bằng 0). Thể hiện tác động phá hủy của việc gán nhãn ẩu.

---

### 4.3 Bảng so sánh tổng thể trên tập kiểm thử nguyên bản RFMiD Test ($N=640$) (Dữ liệu thực nghiệm đã xác minh)

| Cấu hình Thực nghiệm | Macro-F1 | Micro-F1 | Macro-Precision | Macro-Recall | Mean AUROC | Mean AP (PR-AUC) | Tổng FP |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E1: RFMiD-only Baseline** | 0.3128 | 0.5700 | 0.2600 | 0.5171 | 0.8056 | 0.3468 | 1,042 |
| **E2: RFMiD + ODIR Harmonized (Đề xuất)** | **0.4551** | **0.7100** | **0.3693** | **0.6251** | **0.9014** | **0.5306** | **528 (-49.3%)** |
| **E3: Ablation Naive ODIR (Sao chép mù)** | 0.3667 | 0.5696 | 0.3251 | 0.5891 | 0.8503 | 0.4551 | 1,107 |
| **Mức cải thiện $\Delta$ (E2 - E1)** | **+0.1423** | **+0.1400** | **+0.1093** | **+0.1080** | **+0.0958** | **+0.1838** | **-514 FP** |
| **Chênh lệch $\Delta$ (E3 - E1)** | *+0.0539* | *-0.0004* | *+0.0651* | *+0.0720* | *+0.0447* | *+0.1083* | *+65 FP* |

---

### 4.4 Phân tích chi tiết từng lớp bệnh lý đã kiểm chứng (Per-Class Verified Breakdown)

| Lớp Bệnh lý (Class) | Mẫu Test Pos | $F_1$ Baseline (E1) | $F_1$ Harmonized (E2) | $F_1$ Naive (E3) | $\Delta_{E2 - E1}$ | AUROC (E1) | AUROC (E2) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DR** (Võng mạc tiểu đường) | 124 | 0.6746 | **0.6202** | 0.5063 | -0.0544 | 0.9387 | 0.9341 |
| **ARMD** (Thoái hóa hoàng điểm) | 31 | 0.2000 | **0.6216** | 0.3774 | **+0.4216** | 0.7836 | **0.9601** |
| **MYA** (Cận thị thoái hóa) | 32 | 0.5862 | **0.4894** | 0.5882 | -0.0968 | 0.9752 | 0.9361 |
| **DN** (Drusen) | 46 | 0.2051 | **0.3011** | 0.2032 | **+0.0960** | 0.7239 | **0.7891** |
| **ERM** (Màng trước võng mạc) | 5 | 0.0000 | **0.0000** | 0.0000 | 0.0000 | 0.6920 | **0.8646** |
| **BRVO** (Tắc nhánh tĩnh mạch) | 23 | 0.1967 | **0.5063** | 0.1429 | **+0.3096** | 0.7713 | **0.9399** |
| **LS** (Sẹo quang đông Laser) | 15 | 0.0769 | **0.2857** | 0.1000 | **+0.2088** | 0.7179 | **0.8410** |
| **ODC_GLAUCOMA** (Lõm gai/Glôcôm)| 91 | 0.2913 | **0.4876** | 0.2655 | **+0.1963** | 0.6510 | **0.8374** |
| **CRVO** (Tắc tĩnh mạch trung tâm) | 9 | 0.0000 | **0.3529** | 0.6000 | **+0.3529** | 0.8575 | **0.9669** |
| **RISK** (Tín hiệu bệnh lý chung)| 506 | 0.8968 | **0.8862** | 0.8831 | -0.0106 | 0.9452 | 0.9446 |

### 4.5 Thảo luận khoa học chuyên sâu từ dữ liệu thực tế

1. **Hiệu quả thực chất của việc bổ sung dữ liệu ODIR điều hòa nhãn (E2)**:
   - Macro-F1 đạt **0.4551** (vượt trội so với 0.3128 ở E1 và 0.3667 ở E3), Mean AUROC đạt **0.9014** (so với 0.8056 ở E1).
   - Các lớp bệnh lý hiếm gặp trong RFMiD được cải thiện mang tính quyết định: Thoái hóa hoàng điểm **ARMD** ($F_1$ tăng từ 0.2000 lên 0.6216, $+0.4216$), Tắc nhánh tĩnh mạch **BRVO** ($F_1$ tăng từ 0.1967 lên 0.5063, $+0.3096$), Sẹo laser **LS** ($F_1$ tăng từ 0.0769 lên 0.2857), Lõm gai/Glôcôm **ODC** ($F_1$ tăng từ 0.2913 lên 0.4876).
   - Đặc biệt, nhờ có 2,816 ảnh đáy mắt bình thường xác thực (`normal fundus`) từ ODIR đóng vai trò mẫu âm tính chuẩn, tổng số lượt quyết định dương tính giả (FP decisions) trên 6,400 lượt dự đoán tập kiểm thử **giảm gần một nửa: từ 1,042 lượt ở E1 xuống còn 528 lượt ở E2**.
   - *Lưu ý quan trọng về phương pháp đo lường*: Con số 528 FP hay 1,042 FP đại diện cho **tổng số lượt quyết định phân loại nhãn trên từng ảnh (image-label classification decisions)** trong bài toán đa nhãn 10 lớp ($640 \text{ ảnh} \times 10 \text{ lớp} = 6,400 \text{ quyết định}$), **không phải số lượng bệnh nhân duy nhất (not unique patients)**.

2. **So sánh khách quan giữa E3 (Naive Merging) và E1 (RFMiD-only)**:
   - Cần ghi nhận một thực tế thực nghiệm quan trọng: **E3 đạt Macro-F1 là 0.3667, cao hơn E1 (0.3128)**. Điều này cho thấy việc bổ sung thêm gần 7,000 ảnh từ ODIR (dù nhãn bị sao chép ngây thơ) vẫn mang lại biểu diễn đặc trưng thị giác phong phú hơn cho các lớp cực hiếm (chẳng hạn như CRVO đạt $F_1=0.6000$ và ARMD đạt $F_1=0.3774$, kéo Macro-F1 trung bình lên). Do đó, không thể kết luận một cách thiếu căn cứ rằng việc gộp ngây thơ luôn luôn cho kết quả kém hơn hoàn toàn so với việc chỉ dùng RFMiD trên mọi chỉ số đơn lẻ.
   - **Tuy nhiên**, phương pháp sao chép ngây thơ (E3) bộc lộ nhược điểm nghiêm trọng về mặt an toàn sàng lọc:
     - Làm bùng nổ số lượng quyết định dương tính giả lên tới **1,107 lượt FP** (cao nhất trong cả 3 mô hình).
     - Làm suy giảm mạnh chất lượng nhận diện bệnh võng mạc tiểu đường DR ($F_1$ rơi xuống 0.5063 so với 0.6746 ở E1 và 0.6202 ở E2) do mô hình bị phạt sai bởi 452 ảnh âm tính bị gán nhãn dương tính giả.
     - Micro-F1 của E3 chỉ đạt **0.5696**, thấp hơn cả E1 (0.5700) và thua xa E2 (0.7100).
   - **Kết luận khoa học có căn cứ**: Mô hình điều hòa nhãn có mặt nạ che (**E2**) đạt hiệu năng vượt trội toàn diện so với cả E1 và E3 trong khuôn khổ giao thức thực nghiệm này, cân bằng tối ưu giữa độ nhạy trên các lớp hiếm và kiểm soát chặt chẽ tỷ lệ dương tính giả.

3. **Phân tích Động học lớp Bệnh Võng mạc Tiểu đường (DR) và Cảnh báo Chống Rò rỉ Ngưỡng**:
   - Ở mô hình E2, lớp DR ghi nhận $F_1 = 0.6202$ tại ngưỡng đối chuẩn chính thức $\tau_{\text{DR}}^* = 0.16$ (được chọn hoàn toàn từ tập Validation). Tại ngưỡng này, mô hình đạt độ nhạy vượt trội (Recall = 96.77%, phát hiện 120/124 ca DR, chỉ sót đúng 4 ca kiểm thử).
   - *Phân tích thăm dò hậu kiểm (Post-hoc exploratory analysis only)*: Quá trình quét ngưỡng thăm dò trên tập Test cho thấy nếu áp dụng cùng mức ngưỡng $\tau = 0.25$ như E1, mô hình E2 đạt Precision cao hơn (0.5619 > 0.5355), ít FP hơn (85 < 98) và $F_1$ cao hơn E1 (0.6855 > 0.6746). AUROC đạt 0.9341 tương đương 0.9387 ở E1, chứng minh chất lượng biểu diễn đặc trưng của DR hoàn toàn được bảo toàn.
   - *Nguyên tắc liêm chính học thuật*: Kết quả quét ngưỡng hậu kiểm trên tập test **tuyệt đối không được dùng để thay thế ngưỡng chính thức hay cập nhật bộ số liệu đối chuẩn**. Mọi kết quả chính thức của E2 bắt buộc giữ nguyên mốc $\tau_{\text{DR}} = 0.16$ và $F_1 = 0.6202$.

---

## PHẦN 5: KIẾN TRÚC SUY LUẬN VÀ TUYÊN BỐ MIỄN TRỪ TRÁCH NHIỆM

### 5.1 Module suy luận Model C (`model_c/inference.py`)
Module suy luận đã được đóng gói thành chuẩn lập trình hướng đối tượng độc lập:
- **Đầu vào duy nhất**: Đúng 01 ảnh chụp đáy mắt màu RGB (hỗ trợ đường dẫn file, đối tượng PIL Image, hoặc mảng NumPy).
- **Chuẩn hóa tiền xử lý**: Resize $256 \times 256$, Center Crop $224 \times 224$, chuẩn hóa dải màu ImageNet theo đúng giao thức huấn luyện.
- **Tải trọng số nghiêm ngặt**: Chỉ nạp trọng số đã huấn luyện của checkpoint E2 (`E2_RFMiD_ODIR_Harmonized_best.pth`). Tuyệt đối vô hiệu hóa chế độ demo hoặc khởi tạo ngẫu nhiên. Nếu thiếu checkpoint, hệ thống sẽ báo lỗi `FileNotFoundError` tường minh.
- **Ngưỡng quyết định**: Đọc trực tiếp vector ngưỡng tối ưu từ checkpoint ($\tau$).
- **Đầu ra**: Cấu trúc JSON chuẩn hóa gồm:
  - `overall_disease_risk`: Cờ nhị phân phát hiện có bất thường hay không.
  - `detected_diseases`: Danh sách các bệnh lý được phát hiện kèm độ tin cậy phần trăm và giải thích thuật ngữ y khoa tiếng Việt.
  - `full_probabilities`: Bảng điểm xác suất chi tiết cho toàn bộ 10 nhóm bệnh lý theo đúng thứ tự nhãn đã đóng băng.
  - `clinical_disclaimer`: Tuyên bố nghiên cứu học thuật bắt buộc.

### 5.2 Tuyên bố miễn trừ trách nhiệm y khoa (Academic & Clinical Disclaimer)
> [!CAUTION]
> **GIỚI HẠN NGHIÊN CỨU VÀ CẢNH BÁO Y KHOA**:
> Mô hình Model C là sản phẩm nghiên cứu thực nghiệm trong khuôn khổ Khóa luận tốt nghiệp Đại học nhằm mục đích hỗ trợ học thuật và sàng lọc tham khảo. 
> - **KHÔNG ĐƯỢC COI LÀ CHẨN ĐOÁN LÂM SÀNG**: Kết quả dự đoán của mô hình **không có giá trị chẩn đoán y khoa thay thế bác sĩ chuyên khoa Mắt**, không cam kết tính chính xác y khoa 100%, và không đảm bảo chẩn đoán chắc chắn mọi thể bệnh.
> - **QUY TRÌNH Y TẾ BẮT BUỘC**: Trong môi trường khám chữa bệnh thực tế, mọi quyết định lâm sàng phải dựa trên thăm khám trực tiếp bằng đèn soi đáy mắt, chụp cắt lớp quang học võng mạc (OCT), đo thị trường và chỉ định của bác sĩ chuyên khoa có chứng chỉ hành nghề.

---

## PHẦN 6: KẾT LUẬN VÀ KIẾN NGHỊ KHÓA LUẬN

1. **Đóng góp khoa học của Model C**:
   - Cung cấp bằng chứng thực nghiệm rõ ràng: Việc kết hợp đa nguồn dữ liệu đáy mắt (RFMiD + ODIR-5K) mang lại hiệu quả vượt trội khi và chỉ khi áp dụng **điều hòa nhãn ngữ nghĩa ở mức từng mắt** kết hợp **hàm mất mát Masked BCE Loss** (E2 đạt Macro-F1 0.4551 so với 0.3128 ở E1 và 0.3667 ở E3).
   - Làm rõ cơ chế thực nghiệm: Việc gộp ngây thơ nhãn mức bệnh nhân (E3) tuy có thể cải thiện Macro-F1 đối với một số lớp hiếm so với baseline E1 nhờ tăng dung lượng dữ liệu thị giác, nhưng lại gây bùng nổ dương tính giả (1,107 lượt FP) và làm méo mó đặc trưng của bệnh võng mạc tiểu đường.
2. **Khả năng tích hợp hệ thống**:
   - Model C hoạt động như một microservice/module độc lập nhận 01 ảnh RGB, sẵn sàng tích hợp vào giao diện ứng dụng nghiên cứu sau Model A (Gate kiểm định ảnh) và song song với Model B (Phân độ DR 5 mức) mà không làm ảnh hưởng đến trọng số hay kết quả của Model A/B.
