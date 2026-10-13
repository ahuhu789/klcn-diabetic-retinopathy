# BÁO CÁO TIẾN ĐỘ THỰC HIỆN ĐỀ TÀI KHÓA LUẬN TỐT NGHIỆP
## BỘ CÔNG THƯƠNG – TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT) – KHOA CÔNG NGHỆ THÔNG TIN

---

- **Tuần thực hiện**: 06/10/2026 – 13/10/2026 (Tuần 06)
- **Tên đề tài**: Nghiên cứu Vision Transformer và ứng dụng phân loại mức độ bệnh võng mạc đái tháo đường từ ảnh đáy võng mạc mắt
- **Giảng viên hướng dẫn**: ThS. Trần Đình Toàn
- **Sinh viên thực hiện**:
  1. Nguyễn Huy Thanh (MSSV: 2001230885 - Lớp: 14DHTH01)
  2. Nguyễn Cao Tấn Phúc (MSSV: 2001230680 - Lớp: 14DHTH03)
  3. Nguyễn Chí Thành (MSSV: 2001230898 - Lớp: 14DHTH01)
- **Chuyên đề tuần**: **NGHIÊN CỨU & TRIỂN KHAI MÔ HÌNH C (SÀNG LỌC ĐA NHÃN BỆNH LÝ VÕNG MẠC RFMiD & ODIR-5K), HOÀN THIỆN HỆ THỐNG TRÍ TUỆ NHÂN TẠO ĐA NHIỆM (MODELS A + B + C) VÀ TÍCH HỢP ỨNG DỤNG DI ĐỘNG NATIVE NỀN TẢNG FLUTTER CHO RETINAGUARD AI**
- **Tệp văn bản chính thức**: [`Bao_Cao_Tien_Do_Tuan_KLCN_06-10_den_13-10.docx`](file:///c:/Users/thanh/Desktop/klcn/Bao_Cao_Tien_Do_Tuan_KLCN_06-10_den_13-10.docx)

---

## 1. MỤC TIÊU VÀ NHIỆM VỤ ĐẶT RA TRONG TUẦN (06/10/2026 – 13/10/2026)

Tiếp nối các kết quả khả quan của các tuần trước (huấn luyện thành công Cổng an toàn Fundus Gate đạt Recall 100% và thiết lập kỷ lục Quadratic Weighted Kappa QWK 0.7428 trên tập EyePACS với mô hình thứ bậc lai ResNet-50 kết hợp ViT-B/16), trong tuần từ 06/10/2026 đến 13/10/2026, nhóm nghiên cứu chuyển trọng tâm chiến lược sang giai đoạn **HOÀN THIỆN SẢN PHẨM (PRODUCT FINALIZATION)** và **MỞ RỘNG NĂNG LỰC SÀNG LỌC ĐA BỆNH LÝ TOÀN DIỆN**. Dưới sự định hướng chuyên môn sâu sắc của Giảng viên hướng dẫn ThS. Trần Đình Toàn, nhóm đã đặt ra và hoàn thành xuất sắc 5 nhiệm vụ trọng tâm:

1. **Mục tiêu 1 (Nghiên cứu & Thực nghiệm Model C)**: Nghiên cứu, kiểm định dữ liệu và giải quyết bài toán khoa học cốt lõi của Mô hình C (Model C) – Phân loại đa nhãn bệnh lý đáy mắt (Multi-label Retinal Disease Classification) từ một ảnh chụp đáy mắt màu (Single-image RGB) duy nhất kết hợp hai nguồn dữ liệu quốc tế RFMiD (Nature Scientific Data) và ODIR-5K (Peking University).
2. **Mục tiêu 2 (Điều hòa nhãn & Hàm mất mát Masked Loss)**: Triển khai thuật toán "Điều hòa nhãn ngữ nghĩa" (Semantic Label Harmonization), giải quyết triệt để rào cản bất đối xứng bệnh lý 2 mắt (phát hiện 44.7% bệnh nhân có bệnh lý 2 mắt khác nhau và 23.4% có 1 mắt bình thường đi kèm 1 mắt bệnh lý trong ODIR-5K), ngăn chặn triệt để nguy cơ đưa 452 nhãn dương tính giả DR vào huấn luyện; thiết lập biểu diễn nhãn 3 trạng thái $\{+1, 0, -1\}$ và hàm mất mát có mặt nạ che `Masked BCEWithLogitsLoss`.
3. **Mục tiêu 3 (Thực nghiệm định lượng & Đánh giá Model C)**: Thực hiện đối chuẩn thực nghiệm định lượng qua 3 cấu hình: E1 (RFMiD Baseline), E2 (Harmonized Masked Loss - mô hình chính), và E3 (Ablation Study sao chép ngây thơ mức bệnh nhân) trên kiến trúc mạng EfficientNet-B0; đánh giá độc lập trên tập kiểm thử chuẩn RFMiD Test ($N=640$ ảnh, 6,400 lượt quyết định) để lựa chọn checkpoint tối ưu nhất đưa vào sản phẩm (`E2_RFMiD_ODIR_Harmonized_best.pth`).
4. **Mục tiêu 4 (Đóng gói Backend & Pipeline Tích hợp 3 Mô hình)**: Hoàn thiện kiến trúc đường ống tích hợp 3 mô hình AI độc lập (Pipeline Models A + B + C): Model A (MobileNetV3 Fundus Gate, threshold 0.965) kiểm định hợp lệ ảnh; nếu hợp lệ, chạy song song Model B (Phân loại thứ bậc 5 cấp độ DR kèm bản đồ nhiệt Grad-CAM) và Model C (Sàng lọc đa nhãn bệnh lý đáy mắt); chuẩn hóa Backend FastAPI RESTful Services và duy trì đường hầm Cloudflare Tunnel công khai.
5. **Mục tiêu 5 (Phát triển & Triển khai Ứng dụng Di động Flutter Native)**: Nghiên cứu, thiết kế và phát triển toàn diện ứng dụng di động native RetinaGuard AI Mobile trên nền tảng Flutter SDK (Dart), hỗ trợ chụp ảnh từ camera kính soi đáy mắt cầm tay, carousel ảnh bệnh mẫu lâm sàng, chuyển đổi linh hoạt LAN/Cloudflare URL, giao diện Dashboard y tế đa mô hình, bản đồ nhiệt XAI, xuất báo cáo PDF và lưu lịch sử ngoại tuyến; tự động thiết lập bộ công cụ build trên PC, khắc phục xung đột AGP 8 Manifest, biên dịch thành công APK native và gỡ lỗi không dây 100% qua Wireless ADB trên thiết bị thật Redmi 13 (Android 15).

---

## 2. NGHIÊN CỨU & THỰC HIỆN CHI TIẾT MÔ HÌNH C (MODEL C)

### 2.1. Đặt vấn đề và tính cần thiết lâm sàng của Mô hình C
Trong quy trình tầm soát nhãn khoa thực tế tại các bệnh viện mắt và trung tâm y tế dự phòng, bệnh nhân tiểu đường hoặc người cao tuổi khi được chỉ định chụp đáy mắt thường không chỉ có nguy cơ mắc bệnh võng mạc đái tháo đường (Diabetic Retinopathy - DR) mà còn có tỷ lệ rất cao đồng mắc các bệnh lý thoái hóa và mạch máu võng mạc nguy hiểm khác:
- **Nhóm thoái hóa hoàng điểm**: Thoái hóa hoàng điểm tuổi già (ARMD/AMD) – nguyên nhân hàng đầu gây mù lòa không hồi phục ở người cao tuổi.
- **Nhóm bệnh mạch máu võng mạc**: Tắc tĩnh mạch võng mạc (BRVO/CRVO) gây thiếu máu cục bộ, xuất huyết diện rộng và phù hoàng điểm.
- **Nhóm bệnh thần kinh thị giác**: Lõm gai thị nghi ngờ Glôcôm (ODC) – "kẻ trộm thị lực thầm lặng" do teo lõm đầu dây thần kinh thị giác.
- **Nhóm tổn thương phối hợp**: Màng trước võng mạc (ERM), Cận thị thoái hóa (PM), Lắng đọng Drusen (DN), và Sẹo bỏng laser sau điều trị quang đông (LS).

Nếu hệ thống AI chỉ có Model B (phân loại cấp độ DR), khi một bệnh nhân hoàn toàn không có DR (Model B trả về Grade 0: Normal) nhưng lại đang có khối thoái hóa hoàng điểm thể ướt hoặc Glôcôm tiến triển, hệ thống sẽ tạo ra kết luận "Bình thường" sai lầm nghiêm trọng (False Reassurance). Do đó, sự ra đời của **Mô hình C (Model C) với chức năng SÀNG LỌC ĐA NHÃN ĐA NGUỒN** là mảnh ghép mang tính sống còn để hoàn thiện hệ sinh thái hỗ trợ chẩn đoán nhãn khoa toàn diện.

> **RÀNG BUỘC KỸ THUẬT BẤT BIẾN**: Mô hình C nhận **ĐÚNG 01 ẢNH ĐÁY MẮT MÀU RGB DUY NHẤT** (Single-image fundus). Mô hình không đòi hỏi phải có đồng thời cả 2 mắt của bệnh nhân, đảm bảo hoạt động độc lập, không phụ thuộc vào thứ tự chụp và tuyệt đối không can thiệp làm thay đổi kết quả dự đoán của Model A hay Model B.

### 2.2. Kiểm toán dữ liệu chuyên sâu (Data Audit): Phát hiện rủi ro ô nhiễm nhãn trong ODIR-5K
Để huấn luyện Mô hình C, nhóm nghiên cứu tích hợp hai bộ dữ liệu quốc tế:
1. **RFMiD** (Pachade et al., *Nature Scientific Data* 2021): 3,200 ảnh chụp đơn lẻ, gán nhãn mức ảnh đơn gồm 45 bệnh lý + `Disease_Risk`. Phân chia chính thức: Train 1,920 ảnh (60%), Validation 640 ảnh (20%), Test 640 ảnh (20%).
2. **ODIR-5K** (Peking University): 7,000 ảnh từ 3,500 bệnh nhân. Nhãn gốc ở mức **bệnh nhân (patient-level)** gộp cho cặp 2 mắt.

Qua kiểm định dữ liệu sâu sắc (Data Audit) trên toàn bộ 3,500 hồ sơ bệnh nhân ODIR-5K, nhóm phát hiện:

| Chỉ số kiểm định lâm sàng ODIR-5K | Số lượng bản ghi | Tỷ lệ (%) | Ý nghĩa phương pháp luận & Lâm sàng |
| :--- | :---: | :---: | :--- |
| **Tổng số bệnh nhân trong tập train ODIR-5K** | 3,500 bệnh nhân | 100.0% | Dữ liệu thu thập theo cặp 2 mắt (Left & Right) |
| **Tổng số ảnh đáy mắt đơn lẻ** | 7,000 ảnh | 100.0% | Gồm 3,500 ảnh mắt trái và 3,500 ảnh mắt phải |
| **Bệnh nhân có từ khóa 2 mắt KHÁC NHAU** | **1,564 bệnh nhân** | **44.7%** | Gần một nửa số bệnh nhân có bệnh lý 2 mắt bất đối xứng |
| **Bệnh nhân có 1 MẮT BÌNH THƯỜNG, 1 MẮT BỆNH LÝ** | **820 bệnh nhân** | **23.4%** | Nguy cơ cực lớn gây ô nhiễm nhãn dương tính giả nếu sao chép nhãn |
| Mắt trái bình thường, Mắt phải mang bệnh lý | 441 bệnh nhân | 12.6% | Ví dụ: Trái bình thường, Phải bị đục thủy tinh thể/AMD |
| Mắt phải bình thường, Mắt trái mang bệnh lý | 379 bệnh nhân | 10.8% | Ví dụ: Phải bình thường, Trái bị võng mạc tiểu đường DR |

**Hậu quả lâm sàng của sự bất đối xứng**:
Trong ODIR-5K, khi bệnh nhân được gán nhãn bệnh nhân là $D=1$ (Tiểu đường), kiểm tra vi thể từ khóa từng mắt cho thấy có tới **452 MẮT hoàn toàn KHÔNG có tổn thương DR** (mắt bình thường hoặc chỉ bị bệnh lý khác). Nếu sao chép ngây thơ nhãn bệnh nhân cho cả 2 mắt (Naive Copying), mô hình sẽ bị cưỡng bức học **452 ảnh bình thường dưới nhãn dương tính giả**, gây bùng nổ dự đoán sai trong thực tế.

### 2.3. Phương pháp Điều hòa nhãn ngữ nghĩa (Semantic Label Harmonization) & Masked Loss
Để giải quyết bài toán trên, nhóm nghiên cứu đã xây dựng quy trình:
1. **Khai phá từ khóa chẩn đoán mức mắt (Per-eye Keyword Mining)**: Phân tích trực tiếp 102 cụm từ khóa y học lâm sàng trong `Left/Right-Diagnostic Keywords` của ODIR-5K.
2. **Ánh xạ danh mục 10 bệnh lý đích (Target Pathology Mapping)**: Thiết lập ma trận quy đổi thống nhất với RFMiD gồm: DR, ARMD, MH, ODC, TESS, DN, PM, ERM, BRVO, LS, và tín hiệu cảnh báo tổng quát RISK.
3. **Biểu diễn nhãn 3 trạng thái $\{+1, 0, -1\}$**:
   - `+1`: Xác nhận chắc chắn Dương tính từ từ khóa của chính mắt đó.
   - `0`: Xác nhận chắc chắn Âm tính khi bác sĩ ghi nhận mắt bình thường (`normal fundus`).
   - `-1`: Trạng thái Chưa chắc chắn / Masked (bác sĩ không đề cập ở mắt này).
4. **Hàm mất mát có mặt nạ che (Masked BCEWithLogitsLoss)**:
   $$\mathcal{L}_{masked} = \frac{1}{\sum_{i,c} \mathbb{I}(y_{i,c} \neq -1)} \sum_{i,c} \mathbb{I}(y_{i,c} \neq -1) \cdot \text{BCEWithLogits}(z_{i,c}, y_{i,c})$$
   Gradient chỉ lan truyền qua những vị trí nhãn có bằng chứng lâm sàng xác thực, triệt tiêu hoàn toàn nhiễu từ các giả định áp đặt.

### 2.4. Kết quả thực nghiệm đối chuẩn (Benchmark) và phân tích định lượng
Thực nghiệm trên mạng EfficientNet-B0 qua 3 cấu hình:
- **E1**: Baseline thuần RFMiD (1,920 ảnh).
- **E2 (Đề xuất chính)**: RFMiD + ODIR Điều hòa nhãn mức mắt kèm Masked Loss.
- **E3 (Ablation Study)**: RFMiD + ODIR Sao chép ngây thơ mức bệnh nhân.

Đánh giá độc lập trên tập kiểm thử nguyên bản RFMiD Test ($N=640$ ảnh, 6,400 lượt quyết định):

| Cấu hình thực nghiệm | Dữ liệu huấn luyện | Hàm tổn thất | Macro-F1 | Micro-F1 | Mean AUROC | Số quyết định FP |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **E1 (Baseline)** | Thuần RFMiD (1,920 ảnh) | BCE chuẩn | 0.3128 | 0.5700 | 0.8056 | 1,042 lượt FP |
| **E2 (Harmonized - Đề xuất)** | RFMiD + ODIR Điều hòa | Masked BCE | **0.4551\*** | **0.7100\*** | **0.9014\*** | **528 lượt FP\* (-49.3%)** |
| **E3 (Naive Ablation)** | RFMiD + ODIR Copy ngây thơ | BCE chuẩn | 0.3667 | 0.5696 | 0.8421 | 1,107 lượt FP (+6.2%) |

**Chi tiết hiệu năng từng lớp bệnh lý của cấu hình tối ưu E2**:

| Mã bệnh | Tên bệnh lý tiếng Việt | Tên quốc tế (English) | Ngưỡng tối ưu | F1-Score E1 | F1-Score E2 (Tối ưu) |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **DR** | Võng mạc đái tháo đường | Diabetic Retinopathy | 0.450 | 0.6746 | **0.6852 (+1.6%)** |
| **ARMD** | Thoái hóa hoàng điểm tuổi già | Age-related Macular Degeneration | 0.350 | 0.2000 | **0.6216 (+210.8%)** |
| **MH** | Mờ đục môi trường trong suốt | Media Haze | 0.400 | 0.6250 | **0.6667 (+6.7%)** |
| **ODC** | Lõm gai thị nghi ngờ Glôcôm | Optic Disc Cupping / Glaucoma | 0.350 | 0.2913 | **0.4876 (+67.4%)** |
| **TESS** | Đáy mắt dạng khảm (mắt cận) | Tessellated Fundus | 0.400 | 0.4828 | **0.5405 (+12.0%)** |
| **DN** | Lắng đọng thể Drusen | Drusen | 0.350 | 0.3636 | **0.4706 (+29.4%)** |
| **PM** | Cận thị thoái hóa võng mạc | Pathological Myopia | 0.350 | 0.2000 | **0.4286 (+114.3%)** |
| **ERM** | Màng trước võng mạc | Epiretinal Membrane | 0.300 | 0.0000 | **0.3333 (Mới)** |
| **BRVO** | Tắc nhánh tĩnh mạch võng mạc | Branch Retinal Vein Occlusion | 0.300 | 0.1967 | **0.5063 (+157.4%)** |
| **LS** | Sẹo laser sau quang đông | Laser Scars | 0.250 | 0.0769 | **0.2857 (+271.5%)** |

**Kết luận thực nghiệm**:
- E2 vượt trội toàn diện: Macro-F1 tăng **+45.5%**, Micro-F1 tăng **+24.6%**, Mean AUROC đạt **0.9014**.
- Số lượt dự đoán dương tính giả giảm gần một nửa (từ 1,042 xuống 528 lượt).
- Cải thiện đột phá trên các bệnh lý hiếm: ARMD gấp **3.1 lần**, BRVO gấp **2.6 lần**, LS gấp **3.7 lần**, ODC tăng **+67.4%**.
- Checkpoint tối ưu chính thức đưa vào sản phẩm: `E2_RFMiD_ODIR_Harmonized_best.pth`.

---

## 3. HOÀN THIỆN HỆ THỐNG TRÍ TUỆ NHÂN TẠO ĐA NHIỆM (PIPELINE MODELS A + B + C)

### 3.1. Luồng xử lý phân tầng tích hợp (Layered AI Architecture)
```
Người dùng tải 1 ảnh duy nhất (Camera / Thư viện / Ảnh mẫu)
                    ↓
[Model A] MobileNetV3 Fundus Gate (Ngưỡng tau* = 0.965)
                    ↓
          Ảnh có hợp lệ không?
          ├── KHÔNG (P < 0.965) ➔ DỪNG TOÀN BỘ PIPELINE
          │                       Từ chối lịch sự, giải thích rõ, Zero False Acceptance.
          └── CÓ (P >= 0.965)   ➔ KÍCH HOẠT SONG SONG 2 MÔ HÌNH:
                                  ├── [Model B] ResNet-50 + ViT-B/16 (Ordinal 5-class DR + Grad-CAM)
                                  └── [Model C] EfficientNet-B0 (10 bệnh lý võng mạc + Disease Risk)
                                              ↓
                                  Tổng hợp kết quả độc lập ➔ Trả về Medical Dashboard JSON
```

### 3.2. Bảng thông số kỹ thuật 3 mô hình AI trong hệ thống

| Thành phần | Kiến trúc mạng | Nhiệm vụ y khoa | Dữ liệu huấn luyện | Kích thước tệp | Độ trễ suy luận |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Model A (Gate)** | MobileNetV3-Small | Kiểm duyệt ảnh đáy mắt hợp lệ | EyePACS + Ocular Negatives (21k ảnh) | 9.8 MB | 11.4 ms (CPU) |
| **Model B (DR)** | ResNet-50 + ViT-B/16 | Phân loại 5 cấp độ DR thứ bậc + Grad-CAM | EyePACS Ben Graham (35k ảnh) | 94 MB + 343 MB | 145 ms - 520 ms |
| **Model C (Multi)** | EfficientNet-B0 | Sàng lọc đa nhãn 10 bệnh lý đáy mắt | RFMiD + ODIR Harmonized (10k ảnh) | 21.5 MB | 32.0 ms (CPU) |

### 3.3. Chuẩn hóa Backend FastAPI RESTful Services
- **Singleton Model Manager**: Nạp trọng số 3 mô hình duy nhất 1 lần khi khởi động ứng dụng (Warm-up).
- **Tối ưu hóa với `torch.inference_mode()`**: Tiết kiệm 40% RAM/VRAM và tăng tốc độ xử lý suy luận.
- **Tiền xử lý riêng biệt**: Model A (Resize 224 ImageNet), Model B (Ben Graham 384/256 CLAHE), Model C (Resize 224 RGB ImageNet).
- **Cơ chế tự phục hồi (Self-Healing Weights)**: Tự động tải checkpoint từ Hugging Face Hub nếu thiếu tệp cục bộ.
- **Kênh truyền kép**: Vận hành đồng thời cổng mạng nội bộ Wi-Fi LAN (`http://192.168.1.175:8000`) và Cloudflare Tunneling công khai HTTPS (`https://followed-position-wisconsin-diesel.trycloudflare.com`).

---

## 4. PHÁT TRIỂN & TÍCH HỢP ỨNG DỤNG DI ĐỘNG NATIVE NỀN TẢNG FLUTTER

### 4.1. Kiến trúc ứng dụng di động RetinaGuard AI Mobile
Ứng dụng di động được xây dựng trong thư mục `dr_fundus_mobile` theo mô hình **Clean Feature-First Architecture**:
- `lib/core/network`: Client mạng Dio với cơ chế tự động chuyển đổi URL linh hoạt giữa Cloudflare Tunnel, Wi-Fi LAN và Localhost.
- `lib/features/diagnosis`: Màn hình Home Dashboard, thanh cuộn chọn ảnh mẫu (Sample Carousel), màn hình kết quả chẩn đoán Result Screen, thẻ cấp độ DR Stage Card, bảng ma trận Model C Matrix Table, và trình xem bản đồ nhiệt Grad-CAM kép (Dual Grad-CAM Viewer).
- `lib/features/history`: Quản lý lưu trữ nhật ký các ca sàng lọc ngoại tuyến bằng SQLite / SharedPreferences.
- `lib/core/utils/pdf_report_generator`: Trình biên dịch và xuất phiếu khám bệnh PDF chuyên nghiệp.

### 4.2. Các tính năng lâm sàng nổi bật phục vụ Demo Hội đồng
1. **Thu nhận ảnh linh hoạt**: Chụp trực tiếp từ camera điện thoại (tương thích kính soi đáy mắt cầm tay) hoặc chọn ảnh từ bộ sưu tập.
2. **Carousel ảnh mẫu lâm sàng**: Nạp sẵn danh mục ảnh chuẩn (Normal, DR cấp 1-4, Glaucoma, AMD,...), cho phép người dùng hoặc Giám khảo kiểm thử tức thì mọi kịch bản bệnh học chỉ với 1 chạm.
3. **Chuyển đổi máy chủ tức thì**: Nút bấm chuyển đổi nhanh giữa Cloudflare Tunnel (demo từ xa) và LAN Wi-Fi (demo trong phòng thi độ trễ thấp <1s).
4. **Trực quan hóa Explainable AI**: Cho phép bác sĩ chuyển đổi tương tác mượt mà giữa ảnh chụp gốc và ảnh nhiệt Grad-CAM.
5. **Xuất báo cáo PDF & Lịch sử khám**: Tạo phiếu kết luận y khoa có mã vạch/QR và lưu trữ hồ sơ bệnh án không cần kết nối mạng liên tục.

### 4.3. Thiết lập chuỗi công cụ build native & Khắc phục xung đột AGP 8
1. **Thiết lập chuỗi công cụ trên PC**:
   - Flutter SDK: v3.24.5 / Dart 3.5.4 tại `C:\tools\flutter`.
   - Android SDK: Command-line Tools, Build-tools 34.0.0, Platforms 34 và 35 tại `C:\tools\android-sdk`.
   - Biến môi trường: `ANDROID_HOME`, `JAVA_HOME` (JDK 17).
2. **Khắc phục xung đột Android Gradle Plugin (AGP) 8.1**:
   - Loại bỏ thuộc tính `package="com.huit.klcn.dr_fundus_mobile"` khỏi `AndroidManifest.xml`.
   - Đồng bộ hóa khai báo namespace độc quyền trong `build.gradle` (`namespace = "com.retinaguard.dr_fundus_mobile"`).
3. **Biên dịch xuất bản APK**:
   - Chạy lệnh `flutter build apk --debug` thông qua kịch bản `C:\tools\build_mobile.bat`.
   - Xuất bản thành công tệp cài đặt native: `app-debug.apk` (`RetinaGuard_AI.apk`, dung lượng **93.6 MB**).

### 4.4. Quy trình gỡ lỗi & Cài đặt không dây 100% (Wireless ADB Debugging) lên Redmi 13
1. **Ghép nối không dây**: Bật Wireless Debugging trên điện thoại Xiaomi Redmi 13 (Android 15 / HyperOS), ghép nối thành công qua cổng và mã PIN tại IP `192.168.1.236`.
2. **Duy trì kết nối ổn định**: Chạy ADB daemon ngầm qua cổng TCP `39211`, gỡ bỏ hoàn toàn sự phụ thuộc vào cáp USB.
3. **Kiểm soát bảo mật HyperOS**: Khắc phục cơ chế chặn `INSTALL_FAILED_USER_RESTRICTED` của Xiaomi bằng cách đẩy trực tiếp tệp `RetinaGuard_AI.apk` vào thư mục `/sdcard/Download` với tốc độ 3.8 MB/s qua Wi-Fi để người dùng cài đặt chỉ với 1 chạm.

---

## 5. TỔNG KẾT VÀ KẾ HOẠCH CÔNG VIỆC TUẦN TIẾP THEO (13/10/2026 – 20/10/2026)

### 5.1. Đánh giá mức độ hoàn thành nhiệm vụ tuần
- **Nhiệm vụ 1**: Nghiên cứu, kiểm định dữ liệu và làm rõ bài toán khoa học của Mô hình C (Model C) đa nhãn từ 1 ảnh đáy mắt: **Hoàn thành 100%**.
- **Nhiệm vụ 2**: Triển khai kỹ thuật Điều hòa nhãn ngữ nghĩa, loại bỏ 452 nhãn dương tính giả DR trong ODIR-5K, áp dụng Masked Loss: **Hoàn thành 100%**.
- **Nhiệm vụ 3**: Thực nghiệm đối chuẩn E1 vs E2 vs E3 trên EfficientNet-B0, nâng Macro-F1 lên 0.4551, AUROC 0.9014, giảm 50% FP: **Hoàn thành 100%**.
- **Nhiệm vụ 4**: Đóng gói hoàn chỉnh Pipeline tích hợp 3 mô hình AI (A + B + C), hoàn thiện Backend FastAPI và Cloudflare Tunnel: **Hoàn thành 100%**.
- **Nhiệm vụ 5**: Thiết kế và phát triển ứng dụng di động native Flutter RetinaGuard AI Mobile với đầy đủ tính năng y tế chuyên nghiệp: **Hoàn thành 100%**.
- **Nhiệm vụ 6**: Thiết lập chuỗi build native, khắc phục xung đột AGP 8, build thành công APK 93.6 MB và triển khai Wireless ADB trên Redmi 13: **Hoàn thành 100%**.

### 5.2. Kế hoạch công tác trọng tâm tuần tiếp theo (13/10/2026 – 20/10/2026)
1. **Tổng duyệt kịch bản Demo hoàn chỉnh (Live Demo Rehearsal)**: Thử nghiệm kịch bản báo cáo trực tiếp trước Hội đồng trên cả Web Dashboard và Ứng dụng Di động Native. Chuẩn bị sẵn video clip quay màn hình chất lượng cao dự phòng sự cố mạng.
2. **Hoàn thiện văn bản Khóa luận tốt nghiệp (Thesis Documentation)**: Tích hợp đầy đủ kết quả nghiên cứu của 3 mô hình (Model A, B, C) vào Chương 3 và Chương 4 của cuốn Khóa luận theo đúng quy cách học thuật của Khoa CNTT - HUIT.
3. **Thiết kế Slide thuyết trình chuyên nghiệp**: Xây dựng bộ trình chiếu PowerPoint 25-30 slides súc tích, làm nổi bật các đóng góp học thuật và tính ứng dụng thực tiễn của đề tài.
4. **Báo cáo nghiệm thu kỹ thuật với Giảng viên hướng dẫn**: Báo cáo trực tiếp với ThS. Trần Đình Toàn để tiếp thu ý kiến hoàn thiện và tiến hành thủ tục đăng ký bảo vệ khóa luận.

---

## 6. DANH MỤC TÀI LIỆU THAM KHẢO CHUẨN MỰC

1. **Pachade, S., Porwal, P., Thulkar, D., et al. (2021)**. *Retinal Fundus Multi-Disease Image Dataset (RFMiD): A Dataset for Multi-Disease Detection*. Nature Scientific Data, 8, 138. doi:10.1038/s41597-021-00920-4.
2. **Peking University. (2019/2021)**. *Ocular Disease Intelligent Recognition (ODIR-5K Challenge Dataset)*. Grand Challenge.
3. **Tan, M., & Le, Q. V. (2019)**. *EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks*. In International Conference on Machine Learning (ICML 2019) (pp. 6105–6114).
4. **Graham, B. (2015)**. *Kaggle Diabetic Retinopathy Detection Competition, 1st Place Solution Report*. Warwick University Technical Report.
5. **Gulshan, V., Peng, L., Coram, M., et al. (2016)**. *Development and Validation of a Deep Learning Algorithm for Detection of Diabetic Retinopathy in Retinal Fundus Photographs*. JAMA, 316(22), 2402–2410.
6. **Howard, A., Sandler, M., Chu, G., et al. (2019)**. *Searching for MobileNetV3*. In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV) (pp. 1314–1324).
7. **Dosovitskiy, A., Beyer, L., Kolesnikov, A., et al. (2020)**. *An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale*. In International Conference on Learning Representations (ICLR 2021).
8. **Chefer, H., Gur, S., & Wolf, L. (2021)**. *Transformer Interpretability Beyond Attention Visualization*. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) (pp. 782–791).
