# RetinaGuard Mobile: cổng ảnh trên máy và ensemble 6 lớp trên server

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
- **Model A trên máy:** ONNX `assets/models/fundus_gate.onnx`, ngưỡng 0.965. Ảnh không phải đáy mắt thì không gọi server.
- **Model B trên server:** ensemble 6 lớp v3, ViT-B/16-384 0.45 + EfficientNet-B4-448 0.40 + EfficientNet-B4-448 hai đầu ra 0.15, giải mã phân tầng t5 = 0.50 (TEST SCORE 0.6861, QWK_DR 0.7572). App không chạy Model B khi mất mạng.
- Heatmap (ensemble và từng nhánh) và phiếu PDF lấy từ kết quả server. Lớp 5 là nhóm không phải DR.
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
│   │   │   ├── api_endpoints.dart         # Máy chủ local mặc định và các preset URL
│   │   │   ├── app_colors.dart            # Bảng màu y khoa (Navy, Cyan, Emerald, Amber, Red)
│   │   │   └── clinical_constants.dart    # Lớp 0-5, trọng số ensemble v3, t5 = 0.50
│   │   ├── network/
│   │   │   └── api_client.dart            # Dio HTTP Client (Multipart upload, ping health check)
│   │   ├── storage/
│   │   │   └── local_storage.dart         # SharedPreferences lưu lịch sử ca khám
│   │   └── utils/
│   │       └── pdf_report_generator.dart  # Tạo và in ấn phiếu kết quả PDF y khoa
│   ├── models/
│   │   ├── prediction_response.dart       # Mapping 1-1 với FastAPI Schema
│   │   ├── dr_prediction.dart             # Kết quả 6 lớp, Grad-CAM, nhánh và trọng số
│   │   ├── sample_image_info.dart         # Ảnh mẫu lâm sàng
│   │   └── screening_history_item.dart    # Hồ sơ ca khám lưu trữ
│   └── features/
│       ├── diagnosis/
│       │   ├── controllers/
│       │   │   └── diagnosis_controller.dart # Riverpod StateNotifier quản lý luồng chẩn đoán
│       │   ├── views/
│       │   │   ├── home_dashboard_screen.dart # Trang chủ: Camera, Gallery, 10 Mẫu ảnh
│       │   │   └── result_screen.dart         # Tổng quan, Model B, giải thích
│       │   └── widgets/
│       │       ├── sample_carousel.dart       # Thanh chọn 10 ảnh mẫu kèm lọc danh mục
│       │       ├── model_a_gate_badge.dart    # Huy hiệu an toàn Model A Gate
│       │       ├── dr_stage_card.dart         # Thẻ ensemble 6 lớp và lớp của 3 nhánh
│       │       └── dual_gradcam_viewer.dart   # Heatmap ensemble / ViT / EffB4 / EffB4 hai đầu ra
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
cd dr_fundus_mobile
flutter pub get
```

### Bước 3: Chạy Ứng dụng Thử nghiệm

#### Cách A: Máy Windows, không cần adb
```powershell
flutter run -d windows
```

#### Cách B: Điện thoại Android khi máy đã có adb
Bật gỡ lỗi USB, cắm cáp, rồi `flutter run`. Máy không có adb thì cài file APK build ở máy khác.

#### Cách C: Đóng gói file APK
```powershell
flutter build apk --release
```
File APK cài đặt sẽ được tạo tại:  
`build/app/outputs/flutter-apk/app-release.apk`  
Bạn có thể copy file này sang điện thoại của Thầy/Cô hoặc bạn bè trong nhóm để cài đặt trực tiếp.

---

## 🌐 4. Cơ chế Kết nối Mạng với Backend AI

Màn hình **Cài đặt máy chủ** chọn nơi gửi ảnh cho Model B. Mặc định là `http://127.0.0.1:8000`, tức backend local đang nạp ensemble 6 lớp. Model B không chạy trên điện thoại.

1. **Localhost:** app Windows nói chuyện với backend trên cùng máy.
2. **LAN:** điện thoại và máy tính cùng Wi-Fi thì nhập IP của máy tính, ví dụ `http://192.168.1.175:8000`, rồi bấm kiểm tra kết nối.
3. **Android Emulator:** dùng `http://10.0.2.2:8000`.

Hugging Face Space và tunnel Cloudflare cũ không phục vụ bộ trọng số này. Backend cần ba checkpoint v3 trong `dr-fundus-app/backend/models/` (xem `dr-fundus-app/README.md`).

Phản hồi `/api/predict` của server v3 có thêm `dr_branches`, `dr_effb4`, `dr_twohead`, `ensemble_weights`; `dr_resnet` luôn `null`. App vẫn đọc được lịch sử cũ có `dr_resnet`.

---

## 🧪 5. Bộ Kiểm thử Tự động (Automated Tests)

Chạy kiểm thử độ tương thích giữa Data Models Dart và FastAPI schemas:
```powershell
cd dr_fundus_mobile
flutter test
```
Bộ test kiểm tra:
- Khả năng parse JSON kết quả Model B v3: ensemble, 3 nhánh, trọng số, khóa xác suất dạng `"3 - Nặng (Severe NPDR)"`.
- Khả năng xử lý phản hồi từ chối an toàn của Model A Gate (ngưỡng 0.965).
- Khả năng parse danh mục 10 ảnh mẫu có tag và danh mục.
- Khả năng serialize / deserialize hồ sơ khám bệnh nhân.
