# RetinaGuard Mobile: Ứng dụng Di động Sàng lọc & Phân độ Võng mạc Đáy mắt (3-Model AI)

> **Khóa Luận Tốt Nghiệp Ngành Công Nghệ Thông Tin**  
> **Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT)**  
> **Đề tài:** Nghiên cứu Vision Transformer và ứng dụng phân loại mức độ bệnh võng mạc đái tháo đường từ ảnh đáy võng mạc mắt  
> **GVHD:** ThS. Trần Đình Toàn  
> **Nhóm sinh viên:** Nguyễn Huy Thanh (2001230885), Nguyễn Cao Tấn Phúc (2001230680), Nguyễn Chí Thành (2001230898)  

---

## 📱 1. Giới thiệu Ứng dụng Di động (Mobile App Overview)

**RetinaGuard Mobile** là ứng dụng di động đa nền tảng (Flutter) được phát triển nhằm hiện thực hóa mô hình **Khám sàng lọc lưu động (Point-of-Care Screening)** và **Y tế từ xa (Tele-ophthalmology)** cho đề tài khóa luận tốt nghiệp:

- 📷 **Chụp ảnh trực tiếp từ Camera:** Tương thích với các bộ chuyển đổi kính soi đáy mắt cầm tay (Handheld Ophthalmoscope Smartphone Adapter) dùng cho trạm y tế tuyến cơ sở.
- 🖼️ **Nạp ảnh từ Thư viện & Bộ sưu tập 10 ảnh mẫu:** Tích hợp sẵn 10 mẫu ảnh đáy mắt chuẩn y khoa (Khỏe mạnh, Thoái hóa hoàng điểm AMD, Glaucoma, Cận thị thoái hóa MYA, Tắc tĩnh mạch BRVO, DR Cấp 1–4) để demo trước Hội đồng.
- 🛡️ **Model A - Input Safety Gate:** Kiểm duyệt ảnh đáy mắt với ngưỡng nghiêm ngặt $\tau = 0.965$. Tự động ngắt luồng xử lý nếu người dùng chụp nhầm ảnh không phải đáy mắt.
- 👁️ **Model B - DR Staging & XAI Dual Grad-CAM:** Phân loại 5 cấp độ bệnh võng mạc đái tháo đường (ICDR 0–4). Tích hợp trình xem tương tác bản đồ nhiệt Grad-CAM với thanh trượt **Opacity Blend Slider (0% – 100%)** và tính năng **Pinch-to-Zoom** phóng to tổn thương vi mạch.
- 🩺 **Model C - Retinal Multi-label Screening:** Sàng lọc đồng thời 10 bệnh lý võng mạc với hệ thống ngưỡng xác thực động ($\tau_c$).
- 📄 **Xuất Phiếu Kết Quả PDF Lâm Sàng:** Tự động tạo phiếu báo cáo kết quả A4 chuẩn thể thức HUIT (kèm ảnh gốc, ảnh Grad-CAM và khuyến nghị y khoa) để chia sẻ qua Zalo/Email hoặc in trực tiếp.
- 💾 **Lịch sử Ca khám Cục bộ:** Quản lý hồ sơ bệnh nhân đã khám ngay trên máy điện thoại.

---

## 🏗️ 2. Kiến trúc Ứng dụng (Clean Architecture & Riverpod)

```text
dr_fundus_mobile/
├── lib/
│   ├── main.dart                          # Entrypoint & Medical ThemeData
│   ├── core/
│   │   ├── constants/
│   │   │   ├── api_endpoints.dart         # Cấu hình Cloudflare Tunnel URL & Local IP
│   │   │   ├── app_colors.dart            # Bảng màu y khoa (Navy, Cyan, Emerald, Amber, Red)
│   │   │   └── clinical_constants.dart    # Từ điển 10 bệnh lý, thang ICDR 0-4, disclaimer
│   │   ├── network/
│   │   │   └── api_client.dart            # Dio HTTP Client (Multipart upload, ping health check)
│   │   ├── storage/
│   │   │   └── local_storage.dart         # SharedPreferences lưu lịch sử ca khám
│   │   └── utils/
│   │       └── pdf_report_generator.dart  # Tạo và in ấn phiếu kết quả PDF y khoa
│   ├── models/
│   │   ├── prediction_response.dart       # Mapping 1-1 với FastAPI Schema
│   │   ├── dr_prediction.dart             # Model B (5 giai đoạn & Grad-CAM base64)
│   │   ├── model_c_prediction.dart        # Model C (10 bệnh lý & ngưỡng tau)
│   │   ├── sample_image_info.dart         # 10 mẫu ảnh lâm sàng
│   │   └── screening_history_item.dart    # Hồ sơ ca khám lưu trữ
│   └── features/
│       ├── diagnosis/
│       │   ├── controllers/
│       │   │   └── diagnosis_controller.dart # Riverpod StateNotifier quản lý luồng chẩn đoán
│       │   ├── views/
│       │   │   ├── home_dashboard_screen.dart # Trang chủ: Camera, Gallery, 10 Mẫu ảnh
│       │   │   └── result_screen.dart         # Màn hình kết quả 4 Tab (Overview, DR & XAI, Model C, Disclaimer)
│       │   └── widgets/
│       │       ├── sample_carousel.dart       # Thanh chọn 10 ảnh mẫu kèm lọc danh mục
│       │       ├── model_a_gate_badge.dart    # Huy hiệu an toàn Model A Gate
│       │       ├── dr_stage_card.dart         # Thẻ phân độ DR & phân bố xác suất
│       │       ├── model_c_matrix_table.dart  # Ma trận 10 bệnh lý Model C kèm vạch ngưỡng tau
│       │       └── dual_gradcam_viewer.dart   # Trình xem Dual Grad-CAM có slider độ trong suốt
│       ├── history/
│       │   ├── controllers/
│       │   └── views/history_screen.dart      # Danh sách ca khám cũ & xuất lại PDF
│       └── settings/
│           ├── controllers/
│           └── views/server_settings_screen.dart # Màn hình cấu hình URL máy chủ & nút Ping Test
├── android/                               # Cấu hình Android (Camera & Internet permissions)
└── test/
    └── model_deserialization_test.dart    # Bộ kiểm thử tự động JSON Deserialization
```

---

## ⚡ 3. Hướng dẫn Cài đặt & Vận hành Flutter

### Bước 1: Cài đặt Flutter SDK trên Windows (Nếu máy chưa có)
1. Tải bản Flutter SDK mới nhất (dạng `.zip`) từ trang chủ chính thức:  
   👉 [https://docs.flutter.dev/get-started/install/windows/mobile](https://docs.flutter.dev/get-started/install/windows/mobile)
2. Giải nén vào thư mục ngắn, ví dụ: `C:\src\flutter`.
3. Thêm đường dẫn `C:\src\flutter\bin` vào biến môi trường **PATH** của Windows.
4. Mở PowerShell mới và kiểm tra:
   ```powershell
   flutter doctor
   ```

### Bước 2: Cài đặt Thư viện của Dự án
Di chuyển vào thư mục ứng dụng:
```powershell
cd c:\Users\thanh\Desktop\klcn\dr_fundus_mobile
flutter pub get
```

### Bước 3: Chạy Ứng dụng Thử nghiệm

#### Cách A: Chạy trên Thiết bị Android Thật (Khuyên dùng khi bảo vệ)
1. Trên điện thoại Android, vào **Cài đặt -> Giới thiệu điện thoại -> Chạm 7 lần vào "Số hiệu bản dựng"** để bật **Tùy chọn nhà phát triển**.
2. Bật tính năng **Gỡ lỗi qua USB (USB Debugging)**.
3. Cắm cáp USB nối điện thoại với laptop.
4. Chạy lệnh:
   ```powershell
   flutter run
   ```

#### Cách B: Chạy trên Môi trường Windows Desktop (Test nhanh trên Laptop)
```powershell
flutter run -d windows
```

#### Cách C: Đóng gói file APK Release để cài lên nhiều điện thoại
```powershell
flutter build apk --release
```
File APK cài đặt sẽ được tạo tại:  
`build/app/outputs/flutter-apk/app-release.apk`  
Bạn có thể copy file này sang điện thoại của Thầy/Cô hoặc bạn bè trong nhóm để cài đặt trực tiếp.

---

## 🌐 4. Cơ chế Kết nối Mạng với Backend AI

Ứng dụng mobile được trang bị màn hình **Cài đặt Máy chủ (Server Settings)** thông minh:

1. **Chế độ Mặc định (Cloudflare Tunnel - Toàn cầu):**  
   - URL: `https://followed-position-wisconsin-diesel.trycloudflare.com`  
   - **Ưu điểm:** Điện thoại chỉ cần bật 4G hoặc Wi-Fi bất kỳ là có thể gửi ảnh về laptop đang chạy backend.
2. **Chế độ Mạng Cục bộ (LAN IP):**  
   - Khi điện thoại và laptop cùng bắt chung mạng Wi-Fi phòng bảo vệ, bạn có thể nhập địa chỉ IP LAN của máy tính (ví dụ: `http://192.168.1.175:8000`).
   - Nhấn nút **"Kiểm tra kết nối"** để kiểm tra thời gian phản hồi (Ping latency ~50ms).
3. **Chế độ Máy ảo Android Emulator:**  
   - Sử dụng địa chỉ bridge `http://10.0.2.2:8000`.

---

## 🧪 5. Bộ Kiểm thử Tự động (Automated Tests)

Chạy kiểm thử độ tương thích giữa Data Models Dart và FastAPI schemas:
```powershell
cd c:\Users\thanh\Desktop\klcn\dr_fundus_mobile
flutter test
```
Bộ test kiểm tra:
- Khả năng parse JSON kết quả phân độ Model B Stage 3 & Dual Grad-CAM.
- Khả năng xử lý phản hồi từ chối an toàn của Model A Gate (ngưỡng 0.965).
- Khả năng parse danh mục 10 ảnh mẫu có tag và danh mục.
- Khả năng serialize / deserialize hồ sơ khám bệnh nhân.
