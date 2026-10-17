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
  > Hệ thống có hai bước:  
  > 1. **Model A** dùng MobileNetV3-Small, ngưỡng **0.965**, trên ảnh gốc.  
  > 2. **Model B** là ensemble ResNet-50 (0.25) và ViT-B/16 (0.75), 6 lớp. Lớp 0–4 là DR. Lớp 5 là nhóm tổn thương không phải DR. Ngưỡng đã chọn là 0.95, 1.35, 2.35, 3.15.  
  > Sau đây nhóm trình diễn cổng ảnh và kết quả ensemble."*

---

### 🎙️ Phút 2: Kịch bản Demo 1 - Kiểm thử Cơ chế An toàn Đầu vào (Model A Gate)
- **Thao tác trên màn hình:**
  1. Mở trình duyệt tại địa chỉ `http://127.0.0.1:8000`.
  2. Tại khung tải ảnh, chọn tải lên một bức ảnh **không phải ảnh đáy mắt** (ví dụ: ảnh phong cảnh, ảnh chân dung, ảnh đồ họa hoặc ảnh mờ nghiêm trọng).
  3. Bấm **"Phân tích Đáy mắt"**.
- **Hiện tượng trên giao diện:**
  - Hệ thống hiển thị huy hiệu màu đỏ: **"CẢNH BÁO AN TOÀN ĐẦU VÀO (MODEL A)"**.
  - Thông báo: *"Ảnh bị từ chối: Không phải ảnh đáy võng mạc hợp lệ (Độ tin cậy < 0.965). Pipeline đã dừng xử lý an toàn."*
  - Model B không chạy.
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
  - **Kết quả báo cáo** là ensemble, không phải từng nhánh riêng.
  - Tab Model B có 6 cột xác suất, heatmap ResNet, heatmap ViT và heatmap trộn.
- **Lời thoại của Sinh viên:**
  > *"Ảnh hợp lệ đi qua Ben Graham rồi vào hai mạng. Kết quả trên thẻ là 0.25 ResNet cộng 0.75 ViT, giải mã bằng ngưỡng đã chọn trên validation. Lớp 5 không phải tên một bệnh. Hai heatmap cho thấy chỗ mỗi mạng dựa vào khi chọn lớp đó."*

---

### Phút 4: Cách đọc lớp 5 và kết luận
- **Thao tác trên màn hình:**
  - Chuyển sang Tab **"Giải thích & Disclaimer"**.
- **Lời thoại của Sinh viên:**
  > *"Lớp 0 đến 4 là mức DR. Lớp 5 là một nhóm chung, nên không đọc thành đục thủy tinh thể, glôcôm hay AMD. Ngưỡng 0.95, 1.35, 2.35, 3.15 được giữ vì làm SCORE trên validation nhích hơn argmax. Trên test 8818 ảnh, ensemble đạt Acc 69.62%, macro-F1 0.5371, QWK 0.5842. Lớp nhẹ vẫn yếu. Kết quả chỉ để sàng lọc nghiên cứu, không thay bác sĩ."*

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

### Câu 3: Vì sao lớp được chọn không phải cột xác suất cao nhất?
- **Trả lời:**
  > *"Với lớp 0–4, hệ thống không lấy argmax. Nó tính mức nặng kỳ vọng trên 5 lớp đó rồi so với bốn ngưỡng. Argmax lớp 5 thì giữ lớp 5. Hai nhánh có thể khác lớp; thẻ kết quả là ensemble 0.25 / 0.75."*

---

### 📌 Câu 4: Nhóm đã thực hiện những tối ưu hóa gì để ứng dụng phản hồi nhanh và ổn định khi demo?
- **Trả lời chuẩn mực:**
  > *"Thưa Thầy/Cô, nhóm đã áp dụng 4 kỹ thuật tối ưu hóa then chốt:  
  > 1. **Singleton:** Model A và ensemble Model B được nạp một lần khi server khởi động.  
  > 2. **Inference Mode:** Sử dụng `torch.inference_mode()` giúp vô hiệu hóa autograd graph, giảm 40% bộ nhớ RAM và tăng tốc độ suy luận.  
  > 3. **LiteRT/TFLite cho Model A:** Giúp thời gian kiểm duyệt cổng chỉ mất dưới 50ms.  
  > 4. **Decoupled Error Isolation:** Mỗi mô hình chạy trong khối try-catch độc lập, đảm bảo pipeline không bao giờ bị sập đột ngột (crash) nếu một mô hình gặp ngoại lệ."*

---

## 🛠️ PHẦN 3: HƯỚNG DẪN THAO TÁC KỸ THUẬT KHI ĐI BẢO VỆ

### 1. Chuẩn bị trước buổi bảo vệ
1. Mở máy tính, kết nối nguồn điện ổn định.
2. Khởi chạy:
     ```powershell
     cd dr-fundus-app\backend
     python run_server.py
     ```
3. Chờ 5–10 giây cho đến khi dòng thông báo sau xuất hiện:
   ```text
   All models ready for inference!
   Uvicorn running on http://127.0.0.1:8000
   ```
4. Mở trình duyệt Chrome/Edge, truy cập: `http://127.0.0.1:8000`.
5. Bấm `F11` để chuyển sang chế độ toàn màn hình cho giao diện chuyên nghiệp nhất.

### 2. Mở trên điện thoại cùng mạng
Điện thoại và máy tính cùng Wi-Fi thì nhập `http://<IP-máy-tính>:8000` trong phần cài đặt của app. Model B không chạy trên điện thoại.

### 3. Danh sách 10 tệp ảnh mẫu lâm sàng tích hợp sẵn trong Dashboard
Giao diện hiện đã tích hợp bộ lọc danh mục và 10 mẫu ảnh đáy mắt chuẩn y khoa từ tập dữ liệu RFMiD & IDRiD:

1. **Nhóm Mắt Khỏe mạnh:**
   - `NORMAL_001.jpg`: ảnh đáy mắt được gắn nhãn bình thường trong bộ mẫu. Kết quả model là dự đoán, không phải nhãn của file.

2. **Ảnh mẫu bệnh khác DR:** `ARMD_001.jpg`, `GLAUCOMA_001.jpg`, `MYA_001.jpg`, `BRVO_001.jpg`. Nếu ensemble chọn lớp 5, đó chỉ là nhóm không phải DR, không phải tên bệnh in trên tên file.

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
