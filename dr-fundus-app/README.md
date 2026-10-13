# RetinaGuard AI: Hệ thống AI Sàng lọc & Phân độ Tổn thương Võng mạc Đáy mắt (3-Model Pipeline)

> **Khóa Luận Tốt Nghiệp Ngành Công Nghệ Thông Tin**  
> **Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT)**  
> **Đề tài:** Nghiên cứu Vision Transformer và ứng dụng phân loại mức độ bệnh võng mạc đái tháo đường từ ảnh đáy võng mạc mắt  
> **GVHD:** ThS. Trần Đình Toàn  
> **Sinh viên thực hiện:** Nguyễn Huy Thanh (2001230885), Nguyễn Cao Tấn Phúc (2001230680), Nguyễn Chí Thành (2001230898)

---

## 🏗️ 1. Tổng quan Kiến trúc Hệ thống (3-Model Decoupled Pipeline)

Hệ thống ứng dụng Web y tế toàn diện tích hợp 3 mô hình học sâu độc lập nhằm hỗ trợ sàng lọc và chẩn đoán tổn thương võng mạc từ ảnh chụp đáy mắt (fundus photography):

```text
                           [ Người dùng tải ảnh / Chọn ảnh mẫu ]
                                             │
                                             ▼
                     ┌───────────────────────────────────────────────┐
                     │         GIAI ĐOẠN 1: INPUT GATE (MODEL A)     │
                     │       MobileNetV3-Small (LiteRT / TFLite)     │
                     │          Ngưỡng an toàn nghiêm ngặt:          │
                     │                   τ* = 0.965                  │
                     └───────────────────────┬───────────────────────┘
                                             │
                             ┌───────────────┴───────────────┐
                             │                               │
                    [ < 0.965: REJECT ]             [ ≥ 0.965: ACCEPT ]
                             │                               │
                             ▼                               ▼
                 Từ chối & Dừng xử lý          Chuyển sang 2 Luồng Phân tích Độc lập
         (Bảo vệ hệ thống khỏi ảnh rác,                 (Decoupled Pipeline)
           ảnh selfie, phong cảnh, mờ)                       │
                                             ┌───────────────┴───────────────┐
                                             │                               │
                                             ▼                               ▼
     ┌───────────────────────────────────────────────┐   ┌───────────────────────────────────────────────┐
     │       GIAI ĐOẠN 2A: MODEL B (DR STAGING & XAI) │   │     GIAI ĐOẠN 2B: MODEL C (MULTI-LABEL RISK)  │
     │       Kiến trúc Lai: ViT-B/16 + ResNet-50     │   │      EfficientNet-B0 (Tập dữ liệu hài hòa)   │
     │           Hồi quy Thứ tự (Ordinal Loss)       │   │            RFMiD + ODIR-5K (Checkpointed)     │
     ├───────────────────────────────────────────────┤   ├───────────────────────────────────────────────┤
     │ - 5 Cấp độ bệnh võng mạc đái tháo đường (ICDR)│   │ - Cờ cảnh báo bất thường chung (RISK)         │
     │   • Cấp 0: Bình thường (No DR)                │   │ - Sàng lọc đồng thời 9 bệnh lý võng mạc khác: │
     │   • Cấp 1: Nhẹ (Mild NPDR)                    │   │   • DR (Diabetic Retinopathy)                 │
     │   • Cấp 2: Trung bình (Moderate NPDR)         │   │   • AMD (Thoái hóa hoàng điểm tuổi già)       │
     │   • Cấp 3: Nặng (Severe NPDR)                 │   │   • MH (Lỗ hoàng điểm)                        │
     │   • Cấp 4: Tăng sinh (Proliferative DR)       │   │   • DN (Tổn thương đĩa thị)                   │
     │ - Đồng thuận hội chẩn (Agreement: ViT vs CNN) │   │   • MYA (Cận thị bệnh lý)                     │
     │ - Dual Grad-CAM: Bản đồ nhiệt vùng chú ý      │   │   • BRVO/CRVO (Tắc tĩnh mạch võng mạc)        │
     │   • ViT Transformer Attention Attribution     │   │   • TSL (Xơ cứng mạch máu)                    │
     │   • ResNet-50 Layer-4 Feature Map             │   │   • ODC (Lõm gai thị sinh lý)                 │
     │ - Ngưỡng phân chia thứ tự tối ưu:             │   │ - Ngưỡng động riêng cho từng bệnh lý (τ_c)    │
     │   [0.9500, 1.6759, 2.0500, 3.2500]            │   │   được tinh chỉnh độc lập trên tập Validation │
     └───────────────────────────────────────────────┘   └───────────────────────────────────────────────┘
                                             │                               │
                                             └───────────────┬───────────────┘
                                                             │
                                                             ▼
                                             [ BẢNG ĐIỀU KHIỂN Y KHOA HIỆN ĐẠI ]
                                             - Tổng quan chẩn đoán & Chỉ số rủi ro
                                             - Đối sánh chi tiết phân độ Model B & XAI
                                             - Bảng kết quả 10 bệnh lý Model C & Ngưỡng τ
                                             - Khuyến nghị lâm sàng & Tuyên bố trách nhiệm
```

---

## 🩺 2. Chi tiết 3 Mô hình AI

| Thành phần | Kiến trúc & Backbone | Trọng số Checkpoint | Nhiệm vụ chính | Ngưỡng quyết định / Tham số |
| :--- | :--- | :--- | :--- | :--- |
| **Model A (Gate)** | MobileNetV3-Small | `fundus_gate.tflite` (3.7 MB) | Kiểm duyệt ảnh đáy mắt hợp lệ, loại trừ ảnh nhiễu, ảnh phong cảnh, ảnh selfie | $\tau = 0.965$ (Khóa cứng, không hạ ngưỡng) |
| **Model B (DR Staging)** | Hybrid Ordinal Ensemble: ViT-B/16 + ResNet-50 | `vit_b16_hybrid_ordinal_best_qwk.pth`<br>`resnet50_hybrid_ordinal_best_qwk.pth` | Phân độ 5 cấp độ bệnh võng mạc đái tháo đường (ICDR 0–4), sinh bản đồ nhiệt Grad-CAM | Ngưỡng thứ tự: `[0.95, 1.6759, 2.05, 3.25]` |
| **Model C (Multi-label)** | EfficientNet-B0 | `model_c_best_checkpoint.pth` (E2 Checkpoint) | Sàng lọc đa bệnh lý võng mạc đồng thời trên 1 ảnh đáy mắt (10 nhãn) | Ngưỡng xác thực (Validation calibrated): `DR: 0.16, AMD: 0.28, MH: 0.28,...` |

### Nguyên tắc Decoupled (Tách biệt độc lập) giữa Model B và Model C:
- **Model B** giải bài toán **Ordinal Staging (Xếp hạng thứ tự 5 mức độ nghiêm trọng)** chuyên sâu về tổn thương tiểu đường.
- **Model C** giải bài toán **Multi-label Binary Screening (Sàng lọc phát hiện đa bệnh lý võng mạc)** trên dữ liệu RFMiD + ODIR-5K.
- Hai mô hình được thiết kế chạy song song độc lập. Kết quả chẩn đoán của Model B không bị ghi đè hoặc phụ thuộc vào Model C và ngược lại. Nếu một mô hình gặp sự cố phân tích, mô hình còn lại vẫn trả kết quả an toàn đến bác sĩ.

---

## 📁 3. Cấu trúc Thư mục Ứng dụng

```text
dr-fundus-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI server (Thread-safe singletons, Static React SPA mount, Error handling)
│   │   ├── gate.py              # Runner kiểm duyệt ảnh Model A (MobileNetV3 LiteRT/TFLite)
│   │   ├── classifier.py        # Runner phân độ Model B (ViT-B/16 & ResNet-50 Hybrid + Dual Grad-CAM)
│   │   ├── schemas.py           # Pydantic schemas (Enriched metadata, latency, clinical disclaimer)
│   │   └── __init__.py
│   ├── model_c/
│   │   ├── inference.py         # Runner phân tích Model C (EfficientNet-B0 inference mode)
│   │   └── __init__.py
│   ├── models/                  # Thư mục lưu trữ trọng số mô hình đã được xác thực
│   │   ├── fundus_gate.tflite
│   │   ├── resnet50_hybrid_ordinal_best_qwk.pth
│   │   ├── vit_b16_hybrid_ordinal_best_qwk.pth
│   │   └── model_c_best_checkpoint.pth
│   ├── samples/                 # Tập ảnh mẫu đáy mắt lâm sàng (IDRiD, Messidor, ODIR)
│   ├── run_server.py            # Entry point khởi động uvicorn server
│   ├── test_app_e2e.py          # Bộ kiểm thử tự động toàn diện 7 kịch bản End-to-End
│   ├── requirements.txt         # Danh sách thư viện Python phụ thuộc
│   └── Dockerfile               # Cấu hình containerization cho triển khai Cloud
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Medical AI Dashboard (4 tab: Tổng quan, Model B & XAI, Model C, Disclaimer)
│   │   ├── index.css            # Stylesheet y tế chuẩn mực (Plus Jakarta Sans, Dark/Light accents, Responsive)
│   │   └── main.jsx
│   ├── dist/                    # Bản build production của Frontend (được FastAPI phục vụ tại root /)
│   ├── package.json             # Cấu hình Node.js & Vite
│   ├── vite.config.js           # Reverse proxy /api -> http://127.0.0.1:8000
│   └── vercel.json              # Cấu hình deployment Vercel
│
└── README.md                    # Tài liệu hướng dẫn kỹ thuật chi tiết
```

---

## 🚀 4. Hướng dẫn Cài đặt & Vận hành trên Windows

### Bước 1: Môi trường Tiên quyết
- **Python:** 3.10 hoặc 3.11 (64-bit).
- **Node.js:** v18 trở lên (nếu muốn build lại frontend).
- **Git**

### Bước 2: Cài đặt Thư viện Backend
Mở PowerShell hoặc Command Prompt tại thư mục dự án:
```powershell
cd c:\Users\thanh\Desktop\klcn\dr-fundus-app\backend
pip install -r requirements.txt
```

### Bước 3: Khởi động Ứng dụng Toàn diện (All-in-One Serving)
FastAPI đã được tích hợp để tự động phục vụ giao diện React Dashboard đã build sẵn tại thư mục `frontend/dist`. Bạn chỉ cần khởi động backend:
```powershell
cd c:\Users\thanh\Desktop\klcn\dr-fundus-app\backend
python run_server.py
```
Hoặc:
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- **Giao diện Web Ứng dụng (Dashboard):** Truy cập ngay tại trình duyệt: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Tài liệu API Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Kiểm tra trạng thái (Health Check):** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Bước 4: Công khai ra Internet qua Cloudflare Tunnel (Tùy chọn)
Để chia sẻ đường link demo trực tiếp ra ngoài Internet (cho Hội đồng xem trên điện thoại/laptop):
1. Nhấp đúp vào tệp `start_public_tunnel.bat` ở thư mục gốc (hoặc chạy `..\tools\cloudflared.exe tunnel --url http://127.0.0.1:8000`).
2. Cloudflare sẽ cấp một URL HTTPS bảo mật miễn phí dạng `https://<random>.trycloudflare.com` kết nối trực tiếp đến ứng dụng của bạn.

---

## 🧪 5. Kiểm thử Tự động Toàn diện (E2E Automated Testing)

Dự án đi kèm bộ kiểm thử tự động `test_app_e2e.py` bao phủ toàn bộ 7 kịch bản quan trọng:
1. `test_01_health_check`: Kiểm tra trạng thái 3 mô hình đã nạp và ngưỡng Model A = 0.965.
2. `test_02_samples_catalog`: Xác thực danh mục ảnh đáy mắt lâm sàng có sẵn.
3. `test_03_frontend_static_serving`: Xác thực giao diện HTML SPA được phục vụ tại `/`.
4. `test_04_valid_fundus_prediction`: Kiểm tra pipeline hoàn chỉnh trên ảnh đáy mắt hợp lệ (Model A pass, Model B dự đoán giai đoạn ICDR, Model C sàng lọc 10 bệnh lý, đo thời gian xử lý).
5. `test_05_non_fundus_rejection`: Kiểm tra cơ chế tự bảo vệ: Ảnh không phải đáy mắt bị từ chối ngay lập tức, Model B và C không bị kích hoạt.
6. `test_06_corrupted_file_handling`: Kiểm tra tải lên tệp tin hỏng (Trả về HTTP 400 rõ ràng, không làm crash server).
7. `test_07_consecutive_uploads`: Kiểm tra độ ổn định khi gửi nhiều ảnh liên tiếp (không rò rỉ bộ nhớ GPU/RAM).

**Chạy bộ kiểm thử:**
```powershell
cd c:\Users\thanh\Desktop\klcn\dr-fundus-app\backend
python test_app_e2e.py
```
Kết quả mong đợi: `Ran 7 tests in ~27s. OK.`

---

## 📡 6. Danh mục REST API Endpoints

### 1. `GET /api/health`
Kiểm tra tính sẵn sàng của 3 mô hình trong RAM:
```json
{
  "status": "healthy",
  "gate_loaded": true,
  "classifier_loaded": true,
  "model_c_loaded": true,
  "gate_threshold": 0.965
}
```

### 2. `GET /api/samples`
Lấy danh mục 10 ảnh đáy mắt chuẩn y khoa phân theo nhóm bệnh (Khỏe mạnh, Bệnh võng mạc khác, Tiểu đường DR):
```json
[
  {
    "id": "NORMAL_001.jpg",
    "filename": "NORMAL_001.jpg",
    "name": "Mắt Khỏe mạnh (Bình thường)",
    "category": "Khỏe mạnh",
    "tag": "Bình thường",
    "badge_color": "emerald",
    "description": "Ảnh đáy võng mạc bình thường, không có tổn thương mạch máu, hoàng điểm và gai thị nguyên vẹn.",
    "url": "/api/samples/NORMAL_001.jpg"
  },
  {
    "id": "ARMD_001.jpg",
    "filename": "ARMD_001.jpg",
    "name": "Thoái hóa Hoàng điểm Tuổi già (AMD)",
    "category": "Bệnh võng mạc khác",
    "tag": "AMD",
    "badge_color": "amber",
    "description": "Tổn thương thoái hóa hoàng điểm, kèm Drusen và biến đổi tế bào biểu mô sắc tố võng mạc.",
    "url": "/api/samples/ARMD_001.jpg"
  }
]
```

### 3. `POST /api/predict`
Tải lên một ảnh (`multipart/form-data`) để phân tích qua 3 mô hình:
- **Tham số:** `file`: Binary image file (`.jpg`, `.jpeg`, `.png`, `.webp`, tối đa 25MB).
- **Phản hồi:** Trả về đối tượng `PredictionResponse` chứa:
  - `is_fundus`: Kết quả kiểm duyệt từ Model A.
  - `fundus_confidence`: Điểm tin cậy Model A.
  - `dr_result`: Kết quả phân độ DR từ Model B (Stage 0–4, xác suất, mô tả, khuyến nghị).
  - `dr_resnet` & `dr_vit`: Kết quả chi tiết từng backbone kèm `heatmap_base64` (Dual Grad-CAM).
  - `model_c_result`: Kết quả sàng lọc từ Model C (Overall Disease Risk, danh sách bệnh lý phát hiện, bảng 10 bệnh lý kèm ngưỡng).
  - `processing_time_ms`: Tổng thời gian xử lý pipeline tính bằng mili-giây.
  - `clinical_disclaimer`: Tuyên bố miễn trừ trách nhiệm y khoa chính thức.

---

## ⚖️ 7. Tuyên bố Miễn trừ Trách nhiệm Y khoa (Clinical Disclaimer)

> **CẢNH BÁO QUAN TRỌNG:**  
> Hệ thống phần mềm và các mô hình học sâu (Model A, Model B, Model C) được phát triển trong khuôn khổ **Khóa luận Tốt nghiệp Đại học ngành Công nghệ Thông tin** nhằm mục đích nghiên cứu học thuật, đối sánh thực nghiệm và hỗ trợ sàng lọc sơ bộ.  
> 
> Hệ thống **KHÔNG PHẢI LÀ THIẾT BỊ Y TẾ ĐƯỢC CẤP PHÉP CHÍNH THỨC** và kết quả dự đoán **KHÔNG THAY THẾ CHO KẾT LUẬN CHẨN ĐOÁN CỦA BÁC SĨ CHUYÊN KHOA MẮT**. Mọi quyết định can thiệp hoặc điều trị trên lâm sàng bắt buộc phải dựa trên thăm khám trực tiếp bởi bác sĩ nhãn khoa kết hợp với các kỹ thuật cận lâm sàng chuyên sâu (OCT, FFA).
