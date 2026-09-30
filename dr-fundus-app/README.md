# RetinaGuard AI: Hệ thống AI Sàng lọc & Phân độ Võng mạc Đái tháo đường

Hệ thống ứng dụng Web Full-stack khép kín 2 giai đoạn (Two-Stage Pipeline) kết hợp kiểm duyệt ảnh đáy mắt (Input Gate) và phân độ tổn thương võng mạc (Diabetic Retinopathy Staging).

---

## 🏗️ Kiến trúc Hệ thống (Architecture)

```text
               [ Người dùng tải ảnh lên / Ảnh mẫu ]
                                 │
                                 ▼
         ┌────────────────────────────────────────────────┐
         │       GIAI ĐOẠN 1: FUNDUS GATE (MobileNetV3)   │
         │   Kiểm tra tính hợp lệ của ảnh đáy mắt          │
         │   Ngưỡng an toàn tối ưu: τ* = 0.965            │
         └───────────────────────┬────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
        [ < 0.965: REJECT ]             [ ≥ 0.965: PASS ]
                 │                               │
                 ▼                               ▼
       Thông báo từ chối:         ┌───────────────────────────────┐
    "Không phải ảnh đáy mắt,      │ GIAI ĐOẠN 2: DR CLASSIFIER    │
  vui lòng tải ảnh đạt chuẩn y tế"│ Phân loại 5 cấp độ (ResNet-50)│
                                  │ Sinh bản đồ nhiệt Grad-CAM    │
                                  └──────────────┬────────────────┘
                                                 │
                                                 ▼
                                  [ Báo cáo Chẩn đoán Chi tiết ]
                                  - Cấp độ bệnh (0 đến 4)
                                  - Mô tả tổn thương & lời khuyên
                                  - Biểu đồ phân bố xác suất
                                  - Heatmap chú ý vùng tổn thương
```

---

## 📁 Cấu trúc Thư mục

```text
dr-fundus-app/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI REST API (Endpoints: /api/predict, /api/samples, /api/health)
│   │   ├── gate.py           # Fundus Gate Runner (MobileNetV3 qua LiteRT/TFLite)
│   │   ├── classifier.py     # DR Classifier Runner (ResNet-50 + Grad-CAM Engine)
│   │   └── schemas.py        # Pydantic Response/Request models
│   ├── models/
│   │   ├── fundus_gate.tflite # Trọng số Fundus Gate (1.9MB - 3.7MB)
│   │   └── resnet50_ce_best.pth # Trọng số ResNet-50 phân độ DR (94MB)
│   ├── samples/              # Tập ảnh mẫu kiểm nghiệm đáy mắt lâm sàng
│   ├── Dockerfile            # Container build cho Backend (Render / Railway / GCP)
│   ├── requirements.txt      # Thư viện Python phụ thuộc
│   └── test_backend.py       # Script kiểm tra tích hợp cả 2 mô hình
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Giao diện y khoa hiện đại, hiển thị kết quả 2 giai đoạn & Grad-CAM
│   │   ├── index.css         # Clinical UI Theme (Plus Jakarta Sans)
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js        # Cấu hình proxy /api -> backend:8000
│   └── vercel.json           # Cấu hình rewrite SPA cho Vercel deployment
└── README.md
```

---

## 🚀 Hướng dẫn Chạy Cục bộ (Local Development)

### 1. Khởi động Backend (FastAPI)
```bash
cd backend
# Cài đặt thư viện (nếu chưa có)
pip install -r requirements.txt

# Khởi chạy server API tại port 8000
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

### 2. Khởi động Frontend (React + Vite)
```bash
cd frontend
# Cài đặt node modules
npm install

# Khởi chạy dev server tại port 5173
npm run dev
```
Truy cập giao diện tại: `http://localhost:5173`

---

## 🌐 Hướng dẫn Triển khai Cloud (Deployment)

### Backend (Render / Railway / Fly.io)
1. Kết nối Git repo với **Render** hoặc **Railway**.
2. Chọn thư mục gốc là `backend`.
3. Sử dụng Dockerfile có sẵn (`backend/Dockerfile`) hoặc môi trường Python 3.11 với lệnh chạy:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Frontend (Vercel / Netlify)
1. Kết nối Git repo với **Vercel**.
2. Đặt `Root Directory` là `frontend`.
3. Cài đặt biến môi trường:
   - `VITE_API_URL` (nếu tách biệt domain backend).
4. Deploy tự động thông qua file cấu hình `vercel.json`.
