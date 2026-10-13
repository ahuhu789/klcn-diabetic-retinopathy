# KỊCH BẢN THUYẾT TRÌNH BẢO VỆ KHÓA LUẬN & HƯỚNG DẪN DEMO ỨNG DỤNG
## Hệ thống AI Sàng lọc & Phân độ Tổn thương Võng mạc Đáy mắt (RetinaGuard AI)

> **Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT) - Khoa Công nghệ Thông tin**  
> **Đề tài:** Nghiên cứu Vision Transformer và ứng dụng phân loại mức độ bệnh võng mạc đái tháo đường từ ảnh đáy võng mạc mắt  
> **GVHD:** ThS. Trần Đình Toàn  
> **Sinh viên thực hiện:**  
> 1. Nguyễn Huy Thanh (MSSV: 2001230885 - Lớp: 14DHTH01)  
> 2. Nguyễn Cao Tấn Phúc (MSSV: 2001230680 - Lớp: 14DHTH03)  
> 3. Nguyễn Chí Thành (MSSV: 2001230898 - Lớp: 14DHTH01)  

---

## ⏱️ PHẦN 1: KỊCH BẢN THUYẾT TRÌNH DEMO TRƯỚC HỘI ĐỒNG (3 - 5 PHÚT)

### 🎙️ Phút 1: Giới thiệu Kiến trúc & Điểm mới của Ứng dụng
- **Lời thoại của Sinh viên:**
  > *"Kính thưa Thầy/Cô trong Hội đồng chấm khóa luận tốt nghiệp!  
  > Xuất phát từ thực trạng bệnh võng mạc đái tháo đường (Diabetic Retinopathy - DR) là nguyên nhân hàng đầu gây mù lòa có thể phòng ngừa được, nhóm chúng em đã nghiên cứu và phát triển hệ thống **RetinaGuard AI**.  
  > Thay vì chỉ xây dựng một mô hình phân loại đơn lẻ tiềm ẩn nhiều rủi ro khi triển khai lâm sàng, hệ thống của nhóm được thiết kế theo **Kiến trúc Khép kín 3 Mô hình Tách biệt (3-Model Decoupled Pipeline)** gồm:  
  > 1. **Model A (Input Gate):** Sử dụng MobileNetV3-Small với ngưỡng bảo vệ nghiêm ngặt **$\tau = 0.965$** để thẩm định ảnh đáy mắt hợp lệ.  
  > 2. **Model B (DR Staging & XAI):** Mô hình lai giữa **Vision Transformer (ViT-B/16)** và **ResNet-50** kết hợp kỹ thuật hồi quy thứ tự (Ordinal Loss), phân loại 5 giai đoạn bệnh theo thang chuẩn quốc tế ICDR, đồng thời cung cấp bản đồ nhiệt giải thích quyết định **Dual Grad-CAM**.  
  > 3. **Model C (Multi-label Screening):** Sử dụng EfficientNet-B0 huấn luyện trên tập dữ liệu liên nguồn hài hòa hóa (RFMiD + ODIR-5K) để đồng thời sàng lọc 10 bệnh lý võng mạc khác nhau với hệ thống ngưỡng xác thực động ($\tau_c$).  
  > Sau đây, nhóm em xin phép được trình diễn trực tiếp ứng dụng qua 3 kịch bản kiểm thử thực tế."*

---

### 🎙️ Phút 2: Kịch bản Demo 1 - Kiểm thử Cơ chế An toàn Đầu vào (Model A Gate)
- **Thao tác trên màn hình:**
  1. Mở trình duyệt tại địa chỉ `http://127.0.0.1:8000`.
  2. Tại khung tải ảnh, chọn tải lên một bức ảnh **không phải ảnh đáy mắt** (ví dụ: ảnh phong cảnh, ảnh chân dung, ảnh đồ họa hoặc ảnh mờ nghiêm trọng).
  3. Bấm **"Phân tích Đáy mắt"**.
- **Hiện tượng trên giao diện:**
  - Hệ thống hiển thị huy hiệu màu đỏ: **"CẢNH BÁO AN TOÀN ĐẦU VÀO (MODEL A)"**.
  - Thông báo: *"Ảnh bị từ chối: Không phải ảnh đáy võng mạc hợp lệ (Độ tin cậy < 0.965). Pipeline đã dừng xử lý an toàn."*
  - Toàn bộ kết quả phân độ Model B và Model C **hoàn toàn không được kích hoạt** (tránh sinh ra chẩn đoán giả).
- **Lời thoại của Sinh viên:**
  > *"Như Thầy/Cô đang quan sát, khi người dùng vô tình hoặc cố ý tải lên một hình ảnh không đạt chuẩn y khoa, Model A ngay lập tức nhận diện với độ tin cậy thấp hơn ngưỡng an toàn 0.965 và ngắt pipeline ngay lập tức.  
  > Cơ chế này giải quyết triệt để vấn đề 'Garbage In - Garbage Out' trong các hệ thống AI y tế, giúp ngăn ngừa các chẩn đoán sai lệch chết người và tiết kiệm tài nguyên tính toán cho máy chủ."*

---

### 🎙️ Phút 3: Kịch bản Demo 2 - Phân độ DR & Giải thích Quyết định XAI (Model B)
- **Thao tác trên màn hình:**
  1. Trong danh mục ảnh mẫu hoặc tải lên tệp: Chọn ảnh đáy mắt bệnh nhân có tổn thương đái tháo đường (ví dụ ảnh mẫu: `IDRiD_001.jpg`).
  2. Bấm **"Phân tích Đáy mắt"**.
  3. Sau khoảng 2 giây, giao diện hiển thị kết quả phân tích toàn diện.
  4. Nhấp vào Tab **"Model B: Phân độ DR & XAI"**.
- **Hiện tượng trên giao diện:**
  - **Trạng thái Model A:** Pass (Độ tin cậy đạt 1.0000 >= 0.965).
  - **Kết quả Model B:** Xác định bệnh nhân ở **Giai đoạn 3: Mức độ Nặng (Tiền tăng sinh - Severe NPDR)**.
  - **Hội chẩn ViT vs ResNet:** Hiển thị chi tiết so sánh dự đoán giữa nhánh Transformer và nhánh CNN.
  - **Dual Grad-CAM Heatmaps:** Hiển thị song song:
    - *Bản đồ nhiệt ViT Attention Attribution:* Tập trung các vùng chú ý toàn cục theo cơ chế Self-Attention.
    - *Bản đồ nhiệt ResNet Convolution:* Chỉ điểm các vùng vi phình mạch, xuất huyết dạng chấm và xuất tiết cứng trên võng mạc.
  - **Biểu đồ phân bố xác suất:** Trực quan hóa 5 mức độ từ Bình thường (Cấp 0) đến Tăng sinh (Cấp 4).
- **Lời thoại của Sinh viên:**
  > *"Đối với ảnh đáy mắt hợp lệ, Model A thông qua và kích hoạt 2 mô hình phân tích.  
  > Tại Tab Model B, hệ thống phân loại chính xác bệnh nhân ở Giai đoạn 3 (Nặng). Điểm nổi bật là công nghệ **Explainable AI (XAI)** với cơ chế Dual Grad-CAM:  
  > Bên trái là bản đồ nhiệt từ Vision Transformer, phản ánh sự liên kết ngữ cảnh không gian giữa các vùng tổn thương; bên phải là bản đồ từ ResNet-50 chỉ rõ vị trí các ổ xuất huyết và vi phình mạch.  
  > Nhờ đó, bác sĩ lâm sàng không chỉ nhận được một con số vô cảm từ 'hộp đen' AI mà có thể trực tiếp đối chiếu, kiểm tra cơ sở mà mô hình dựa vào để đưa ra quyết định."*

---

### 🎙️ Phút 4: Kịch bản Demo 3 - Sàng lọc Đa bệnh lý Võng mạc Đồng thời (Model C)
- **Thao tác trên màn hình:**
  1. Chuyển sang Tab **"Model C: Sàng lọc Đa bệnh lý"**.
  2. Quan sát khung cảnh báo tổng quan và bảng dữ liệu 10 bệnh lý.
- **Hiện tượng trên giao diện:**
  - **Banner Rủi ro Tổng thể (Overall Disease Risk):** Hiển thị cờ đỏ cảnh báo: *"PHÁT HIỆN DẤU HIỆU BỆNH LÝ TRÊN VÕNG MẠC"* (kèm ghi chú: Đây là cờ sàng lọc chung từ tập dữ liệu RFMiD, không phải tên bệnh giải phẫu).
  - **Danh sách nhãn phát hiện:** Thẻ chip đỏ hiển thị bệnh lý được phát hiện: `Diabetic Retinopathy` (Xác suất 96.07% vượt ngưỡng $\tau = 0.16$).
  - **Bảng ma trận 10 bệnh lý võng mạc:** Hiển thị đầy đủ tên y khoa, mã quốc tế, mô tả tiếng Việt, thanh xác suất trực quan và vạch chỉ báo ngưỡng xác thực $\tau_c$ (Validation Thresholds) cho từng bệnh lý (DR, AMD, MH, DN, MYA, BRVO, TSL, ODC,...).
- **Lời thoại của Sinh viên:**
  > *"Tiếp theo, tại Tab Model C, hệ thống cung cấp góc nhìn **Sàng lọc Đa bệnh lý (Multi-label Screening)**.  
  > Trong thực tế lâm sàng, một bệnh nhân tiểu đường hoàn toàn có thể mắc kèm các bệnh lý mắt khác như thoái hóa hoàng điểm (AMD) hoặc xơ cứng mạch máu võng mạc (TSL).  
  > Model C giúp sàng lọc đồng thời 10 bệnh lý. Đặc biệt, hệ thống áp dụng hệ thống **Ngưỡng quyết định động ($\tau_c$)** được tối ưu hóa độc lập trên tập Validation thay vì dùng ngưỡng mặc định 0.5. Ví dụ với bệnh DR, ngưỡng phát hiện tối ưu là 0.16; với AMD là 0.28. Việc hiển thị trực quan vạch ngưỡng giúp bác sĩ dễ dàng đánh giá biên độ an toàn của dự đoán."*

---

### 🎙️ Phút 5: Lý giải Tính Độc lập (Decoupling) & Kết luận
- **Thao tác trên màn hình:**
  - Chuyển sang Tab **"Giải thích & Disclaimer"**.
- **Lời thoại của Sinh viên:**
  > *"Thưa Thầy/Cô, một đóng góp kỹ thuật quan trọng của nhóm là thiết kế kiến trúc **Decoupled Pipeline**:  
  > - Model B giải bài toán **Xếp hạng thứ tự (Ordinal Staging)** chuyên biệt 5 cấp độ của riêng bệnh võng mạc đái tháo đường.  
  > - Model C giải bài toán **Sàng lọc nhị phân đa nhãn (Multi-label Screening)** trên tập dữ liệu tổng hợp RFMiD + ODIR-5K.  
  > Hai mô hình hoạt động trên hai không gian bài toán toán học khác nhau. Nhóm chủ động tách biệt luồng xử lý và xử lý ngoại lệ độc lập, đảm bảo rằng sự cố của một mô hình không làm sập toàn bộ hệ thống, và kết quả của hai mô hình không can thiệp, không làm sai lệch tính liêm chính khoa học của nhau.  
  > Cuối cùng, hệ thống luôn hiển thị Tuyên bố miễn trừ trách nhiệm y khoa, định vị sản phẩm là công cụ hỗ trợ sàng lọc sơ bộ cho bác sĩ, không thay thế chẩn đoán chuyên sâu.  
  > Nhóm em xin chân thành cảm ơn Quý Thầy/Cô và rất mong nhận được những góp ý quý báu!"*

---

## ❓ PHẦN 2: BỘ CÂU HỎI THƯỜNG GẶP CỦA HỘI ĐỒNG (Q&A DEFENSE PREPARATION)

### 📌 Câu 1: Tại sao nhóm chọn ngưỡng Model A là 0.965 mà không dùng 0.5 hay 0.9?
- **Trả lời chuẩn mực:**
  > *"Thưa Thầy/Cô, ngưỡng $\tau = 0.965$ được nhóm tối ưu hóa dựa trên đường cong ROC và PR trên tập kiểm nghiệm độc lập bao gồm cả ảnh đáy mắt chuẩn và tập ảnh ngoại lai (Out-of-Distribution - OOD) như ảnh chụp da, ảnh nội soi, ảnh chụp tự nhiên và ảnh đáy mắt mờ hỏng nặng.  
  > Trong y tế, chi phí rủi ro của việc 'chấp nhận nhầm ảnh rác' (False Positive của cổng kiểm duyệt) là rất lớn vì sẽ dẫn đến chẩn đoán sai lệch ở các mô hình sau. Với ngưỡng 0.965, mô hình đạt độ nhạy trên 99% đối với ảnh đáy mắt hợp lệ đồng thời loại bỏ triệt để 100% các mẫu ảnh không liên quan. Nhóm duy trì cố định ngưỡng này để bảo đảm tính an toàn tuyệt đối cho hệ thống."*

---

### 📌 Câu 2: Làm thế nào nhóm tính toán được Grad-CAM cho Vision Transformer (ViT-B/16) khi ViT không có các lớp tích chập Convolutional Layers?
- **Trả lời chuẩn mực:**
  > *"Thưa Thầy/Cô, đối với CNN như ResNet-50, Grad-CAM truyền thống tính toán đạo hàm của điểm số dự đoán theo các feature maps của lớp tích chập cuối cùng (layer4).  
  > Tuy nhiên, với Vision Transformer, kiến trúc dựa trên cơ chế Multi-Head Self-Attention. Nhóm đã áp dụng phương pháp **Transformer Attribution kết hợp Attention Rollout** (theo nghiên cứu của Chefer et al., CVPR 2021). Nhóm trích xuất ma trận Attention Weights tại khối Transformer Block cuối cùng, kết hợp với gradient của token chẩn đoán `[CLS]` đối với từng attention map, sau đó nhân ma trận và chuẩn hóa để chiếu ngược lại không gian các patch ảnh $16 \times 16$, từ đó tái tạo bản đồ nhiệt phân giải cao phản ánh đúng vùng chú ý của Transformer."*

---

### 📌 Câu 3: Tại sao cùng là bệnh võng mạc đái tháo đường (DR) nhưng xác suất ở Model B và Model C lại khác nhau? Có mâu thuẫn không?
- **Trả lời chuẩn mực:**
  > *"Dạ thưa Thầy/Cô, hai chỉ số này hoàn toàn không mâu thuẫn vì đại diện cho hai bài toán toán học khác nhau:  
  > 1. **Model B là mô hình Ordinal Classification:** Đầu ra là phân bố xác suất có điều kiện trên 5 cấp độ tăng dần (từ Cấp 0 đến Cấp 4) nhằm xác định mức độ nặng của bệnh nhân đã hoặc nghi ngờ mắc DR.  
  > 2. **Model C là mô hình Multi-label Binary Classification:** Đầu ra là xác suất sigmoid độc lập cho nhãn DR trong bối cảnh sàng lọc tổng quát giữa nhiều bệnh lý võng mạc khác nhau.  
  > Việc hiển thị độc lập hai kết quả này giúp bác sĩ có góc nhìn đối sánh khách quan: Model C đóng vai trò 'bộ lọc cảnh báo' phát hiện có DR, còn Model B đóng vai trò 'thước đo chuyên sâu' phân định chính xác mức độ tổn thương của bệnh nhân."*

---

### 📌 Câu 4: Nhóm đã thực hiện những tối ưu hóa gì để ứng dụng phản hồi nhanh và ổn định khi demo?
- **Trả lời chuẩn mực:**
  > *"Thưa Thầy/Cô, nhóm đã áp dụng 4 kỹ thuật tối ưu hóa then chốt:  
  > 1. **Singleton Caching:** Cả 3 mô hình (Model A, B, C) được khởi tạo và nạp sẵn vào bộ nhớ RAM duy nhất 1 lần khi server khởi động, không reload lại qua mỗi request.  
  > 2. **Inference Mode:** Sử dụng `torch.inference_mode()` giúp vô hiệu hóa autograd graph, giảm 40% bộ nhớ RAM và tăng tốc độ suy luận.  
  > 3. **LiteRT/TFLite cho Model A:** Giúp thời gian kiểm duyệt cổng chỉ mất dưới 50ms.  
  > 4. **Decoupled Error Isolation:** Mỗi mô hình chạy trong khối try-catch độc lập, đảm bảo pipeline không bao giờ bị sập đột ngột (crash) nếu một mô hình gặp ngoại lệ."*

---

## 🛠️ PHẦN 3: HƯỚNG DẪN THAO TÁC KỸ THUẬT KHI ĐI BẢO VỆ

### 1. Chuẩn bị trước buổi bảo vệ
1. Mở máy tính, kết nối nguồn điện ổn định.
2. Khởi chạy ứng dụng:
   - Cách 1 (Nhanh nhất): Nhấp đúp vào tệp `start_full_app.bat` ở thư mục gốc.
   - Cách 2: Chạy lệnh trong terminal:
     ```powershell
     cd c:\Users\thanh\Desktop\klcn\dr-fundus-app\backend
     python run_server.py
     ```
3. Chờ 5–10 giây cho đến khi dòng thông báo sau xuất hiện:
   ```text
   All models ready for inference!
   Uvicorn running on http://127.0.0.1:8000
   ```
4. Mở trình duyệt Chrome/Edge, truy cập: `http://127.0.0.1:8000`.
5. Bấm `F11` để chuyển sang chế độ toàn màn hình cho giao diện chuyên nghiệp nhất.

### 2. Công khai Ứng dụng qua Cloudflare Tunnel (Cho Hội đồng mở trên Smartphone/Laptop)
Để Thầy/Cô trong Hội đồng có thể quét mã QR hoặc truy cập trực tiếp từ điện thoại/laptop cá nhân:
1. Nhấp đúp vào tệp `start_public_tunnel.bat` ở thư mục gốc (hoặc chạy `tools\cloudflared.exe tunnel --url http://127.0.0.1:8000`).
2. Màn hình console sẽ xuất hiện đường link bảo mật HTTPS công khai dạng:
   ```text
   https://<ten-mien-ngau-nhien>.trycloudflare.com
   ```
3. Chia sẻ đường dẫn này để người khác truy cập demo trực tiếp từ mọi nơi trên Internet mà không cần mở cổng router hay mua tên miền.

### 3. Danh sách 10 tệp ảnh mẫu lâm sàng tích hợp sẵn trong Dashboard
Giao diện hiện đã tích hợp bộ lọc danh mục và 10 mẫu ảnh đáy mắt chuẩn y khoa từ tập dữ liệu RFMiD & IDRiD:

1. **Nhóm Mắt Khỏe mạnh:**
   - `NORMAL_001.jpg`: Đáy mắt người bình thường, không tổn thương (Model A Pass, Model B Stage 0, Model C Không phát hiện rủi ro).

2. **Nhóm Bệnh lý Võng mạc Khác (Sàng lọc qua Model C):**
   - `ARMD_001.jpg`: Thoái hóa hoàng điểm tuổi già (Model C phát hiện chính xác **ARMD** và **Drusen**).
   - `GLAUCOMA_001.jpg`: Lõm gai thị / Biến đổi glôcôm (Model C phát hiện chính xác **Optic Disc Cupping / Glaucoma**).
   - `MYA_001.jpg`: Cận thị bệnh lý thoái hóa võng mạc (Model C phát hiện chính xác **Pathological Myopia** với độ tin cậy 88%).
   - `BRVO_001.jpg`: Tắc nhánh tĩnh mạch võng mạc (Model C phát hiện chính xác **Branch Retinal Vein Occlusion**).

3. **Nhóm Bệnh Võng mạc Đái tháo đường (Phân độ chuyên sâu qua Model B & XAI):**
   - `IDRiD_001.jpg`: Tổn thương võng mạc tiểu đường nặng (Stage 3 - Severe NPDR).
   - `IDRiD_002.jpg`: Tổn thương võng mạc tiểu đường vừa (Stage 2 - Moderate NPDR).
   - `IDRiD_003.jpg`: Tổn thương võng mạc tiểu đường tăng sinh (Stage 4 - PDR).
   - `IDRiD_004.jpg`: Tổn thương võng mạc tiểu đường nhẹ (Stage 1 - Mild NPDR).
   - `IDRiD_005.jpg`: Tổn thương tiến triển nghi ngờ cao.

4. **Kiểm thử Model A (Safety Gate):**
   - Có thể tải lên bất kỳ ảnh nào không phải đáy mắt (ảnh chụp mặt, phong cảnh, đồ vật) để chứng minh tính năng tự ngắt an toàn của Model A ở ngưỡng 0.965.

---

### 4. Hướng dẫn Trình diễn Ứng dụng Di động (RetinaGuard Mobile App Demo)
Nếu bạn mang theo điện thoại thông minh cài ứng dụng **RetinaGuard Mobile**:
1. **Mở ứng dụng trên điện thoại:** Icon *RetinaGuard AI*.
2. **Kiểm tra trạng thái kết nối:** Huy hiệu trên cùng hiển thị độ trễ xanh lá `~50ms` (kết nối trực tiếp qua Cloudflare Tunnel hoặc LAN IP).
3. **Thao tác ấn tượng trước Hội đồng:**
   - Dùng ngón tay cuộn chọn nhanh qua **10 mẫu ảnh bệnh lý** (Thoái hóa hoàng điểm, Glaucoma, Cận thị, DR 1-4).
   - Nhấn **"Phân tích Toàn diện"** -> Ứng dụng hiển thị hiệu ứng quét võng mạc và trả về kết quả trong 2 giây.
   - Chuyển sang Tab **"Model B: DR & XAI"**, dùng thanh trượt **Độ phủ Heatmap (Opacity Slider)** kéo qua lại từ 0% đến 100% để hội đồng thấy rõ tổn thương vi mạch hiện ra trên ảnh đáy mắt thật.
   - Nhấn icon **Toàn màn hình** để dùng 2 ngón tay phóng to (Pinch-to-zoom) từng ổ xuất huyết.
   - Nhấn icon **Xuất PDF** ở góc trên để tạo ngay Phiếu kết quả lâm sàng chuẩn A4 và chia sẻ trực tiếp.
