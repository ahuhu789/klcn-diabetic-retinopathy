# Nghiên cứu Vision Transformer và Ứng dụng Phân loại Mức độ Bệnh Võng mạc Đái tháo đường từ Ảnh Đáy Võng mạc Mắt

## Khóa Luận Tốt Nghiệp - Ngành Công nghệ Thông tin
**Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT) - Khoa Công nghệ Thông tin**

---

### 🎓 Thông tin Đề tài
- **Đề tài:** Nghiên cứu Vision Transformer và ứng dụng phân loại mức độ bệnh võng mạc đái tháo đường từ ảnh đáy võng mạc mắt
- **Giảng viên hướng dẫn:** ThS. Trần Đình Toàn
- **Sinh viên thực hiện:**
  1. Nguyễn Huy Thanh – MSSV: 2001230885 – Lớp: 14DHTH01
  2. Nguyễn Cao Tấn Phúc – MSSV: 2001230680 – Lớp: 14DHTH03
  3. Nguyễn Chí Thành – MSSV: 2001230898 – Lớp: 14DHTH01
- **Thời gian thực hiện:** 2026

---

### 🌟 Hệ thống Ứng dụng Hoàn chỉnh (RetinaGuard AI - 3-Model Decoupled Pipeline)

Ứng dụng web y tế toàn diện đã được hiện thực hóa và đóng gói hoàn chỉnh trong thư mục [`dr-fundus-app/`](file:///c:/Users/thanh/Desktop/klcn/dr-fundus-app):

1. **Model A – Fundus Validation Gate (MobileNetV3-Small LiteRT):**
   - Kiểm duyệt chất lượng ảnh đầu vào, từ chối ảnh không phải đáy mắt với ngưỡng an toàn nghiêm ngặt **$\tau = 0.965$**.
   - Bảo vệ hệ thống khỏi dữ liệu rác và ngắt pipeline ngay lập tức nếu ảnh không đạt chuẩn.

2. **Model B – DR Severity Classification & Explainable AI (ViT-B/16 + ResNet-50 Hybrid Ordinal):**
   - Phân loại 5 cấp độ bệnh võng mạc đái tháo đường theo thang chuẩn quốc tế ICDR (0: Bình thường, 1: Nhẹ, 2: Trung bình, 3: Nặng, 4: Tăng sinh).
   - Huấn luyện theo hàm mất mát hồi quy thứ tự (Ordinal Loss) với bộ ngưỡng phân cách tối ưu: `[0.9500, 1.6759, 2.0500, 3.2500]`.
   - Sinh bản đồ nhiệt **Dual Grad-CAM**: ViT Transformer Attention Rollout và ResNet Convolution Feature Attribution giúp bác sĩ đối chiếu vùng tổn thương vi mạch thực tế.

3. **Model C – Retinal Multi-label Screening (EfficientNet-B0 Harmonized):**
   - Huấn luyện trên tập dữ liệu đa nguồn đã qua xử lý hài hòa hóa nhãn (RFMiD + ODIR-5K, E2 Checkpoint).
   - Cảnh báo cờ rủi ro tổng quát (**Overall Disease Risk**) và sàng lọc đồng thời 9 bệnh lý võng mạc khác nhau (DR, AMD, MH, DN, MYA, BRVO, TSL, ODC,...).
   - Áp dụng hệ thống ngưỡng quyết định động ($\tau_c$) được tối ưu hóa độc lập trên tập Validation.

4. **Giao diện Bảng Điều khiển Web Y khoa (Modern Medical AI Dashboard):**
   - Giao diện trực quan chuẩn lâm sàng (React + Vite, Tailwind-style design, Plus Jakarta Sans).
   - 4 tab chuyên biệt: Tổng quan Chẩn đoán, Phân độ Model B & XAI, Sàng lọc Đa bệnh lý Model C, Giải thích kiến trúc & Tuyên bố trách nhiệm y khoa.
   - Bản build tĩnh được FastAPI phục vụ trực tiếp tại cổng `http://127.0.0.1:8000`.

5. **Ứng dụng Di động Đa nền tảng (RetinaGuard Mobile - Flutter App):**
   - Đóng gói hoàn chỉnh trong thư mục [`dr_fundus_mobile/`](file:///c:/Users/thanh/Desktop/klcn/dr_fundus_mobile).
   - Hỗ trợ chụp camera trực tiếp qua kính soi đáy mắt cầm tay hoặc chọn từ 10 mẫu ảnh bệnh lý lâm sàng.
   - Trình xem tương tác **Dual Grad-CAM Opacity Blend Slider** (0% - 100%) và phóng to tổn thương vi mạch (Pinch-to-zoom).
   - Tự động xuất phiếu kết quả sàng lọc chuẩn A4 file PDF kèm hình ảnh và khuyến nghị lâm sàng.
   - Kết nối linh hoạt tới Backend qua Cloudflare Tunnel toàn cầu hoặc mạng nội bộ LAN.

---

## ⚡ Hướng dẫn Chạy Nhanh Ứng dụng trên Windows

```powershell
# Di chuyển vào thư mục backend
cd c:\Users\thanh\Desktop\klcn\dr-fundus-app\backend

# Cài đặt thư viện phụ thuộc (nếu chưa có)
pip install -r requirements.txt

# Khởi động ứng dụng (All-in-One: FastAPI + React Dashboard)
python run_server.py
```
- **Truy cập Giao diện Web:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Tài liệu API Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Kiểm thử tự động E2E:** `python test_app_e2e.py` (7/7 test cases Passed)

---

## 📚 Danh mục Tài liệu & Báo cáo Nghiên cứu trong Repository

- **[`DEMO_GUIDE.md`](file:///c:/Users/thanh/Desktop/klcn/DEMO_GUIDE.md):** Kịch bản thuyết trình bảo vệ 3–5 phút trước Hội đồng, hướng dẫn demo trực tiếp 3 kịch bản, và bộ câu hỏi Q&A phản biện chuẩn bị sẵn.
- **[`dr-fundus-app/README.md`](file:///c:/Users/thanh/Desktop/klcn/dr-fundus-app/README.md):** Tài liệu hướng dẫn kỹ thuật chi tiết của ứng dụng Web.
- **[`BAO_CAO_NGHIEN_CUU_MODEL_C.md`](file:///c:/Users/thanh/Desktop/klcn/BAO_CAO_NGHIEN_CUU_MODEL_C.md):** Báo cáo khoa học chính thức về quá trình nghiên cứu, hài hòa nhãn và huấn luyện Model C.
- **[`MODEL_C_FINAL_ACADEMIC_CHECK.md`](file:///c:/Users/thanh/Desktop/klcn/MODEL_C_FINAL_ACADEMIC_CHECK.md):** Báo cáo kiểm toán liêm chính khoa học, tái lập kết quả thực nghiệm và kiểm tra trùng lặp dữ liệu.
- **[`DATASET_AUDIT.md`](file:///c:/Users/thanh/Desktop/klcn/DATASET_AUDIT.md):** Báo cáo kiểm định 2 tập dữ liệu võng mạc RFMiD và ODIR-5K.
- **[`LABEL_HARMONIZATION.md`](file:///c:/Users/thanh/Desktop/klcn/LABEL_HARMONIZATION.md):** Bảng ánh xạ hài hòa nhãn bệnh học mắt từ cấp độ bệnh nhân sang cấp độ từng mắt.
