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

### Hệ thống ứng dụng (RetinaGuard AI)

Web nằm trong `dr-fundus-app/`. App Flutter nằm trong `dr_fundus_mobile/`.

1. **Model A – cổng ảnh đáy mắt (MobileNetV3-Small):**
   - Nhìn ảnh gốc. Ngưỡng giữ **0.965**. Ảnh không phải đáy mắt thì Model B không chạy.

2. **Model B – ensemble 6 lớp v3 (ViT-B/16-384 0.45 + EfficientNet-B4-448 0.40 + EfficientNet-B4-448 hai đầu ra 0.15):**
   - Ba checkpoint EMA tốt nhất theo SCORE trên VAL, lấy từ output các kernel Kaggle riêng tư `klcn-retinal-6class-v3-vitb16-384`, `klcn-retinal-6class-v3-effb4-448` (version 3) và `klcn-retinal-6class-v3-e-twohead`. Bộ v2 (ResNet-50 + ViT-B/16 256) đã bỏ.
   - Lớp 0–4 là thang DR. Lớp 5 là nhóm tổn thương không phải DR, không nêu tên từng bệnh.
   - Tiền xử lý giống bộ cache huấn luyện `klcn-retinal-6class-bengraham512-cache`: cắt nền tối (tol 10), resize 512, Ben Graham (hệ số 4, Gaussian σ = 20), mặt nạ tròn 0.95, JPEG q92; mỗi nhánh resize về 384 (ViT) hoặc 448 (EffB4), chuẩn hóa ImageNet, TTA lật ngang.
   - Xác suất ensemble = 0.45·ViT + 0.40·EffB4 + 0.15·EffB4 hai đầu ra. Giải mã phân tầng: lớp 5 nếu p5 > 0.50, nếu không lấy argmax của lớp 0–4. Trọng số và t5 được khóa trên VAL (231 điểm simplex, bước 0.05), TEST chấm một lần.
   - VAL (n = 8796): SCORE 0.6906. TEST (n = 8818): Acc 79.36%, macro-F1 0.6151, QWK_DR 0.7572, SCORE 0.6861 (CI95 0.6684–0.7035), QWK_DR EyePACS 0.7552 (CI95 0.7342–0.7756). SCORE = 0.5·macro-F1(6 lớp) + 0.5·QWK_DR; QWK_DR tính bằng argmax(p[:, :5]) trên nhãn thật 0–4.
   - Grad-CAM của từng nhánh lấy lớp do ensemble giải mã (EffB4: lớp `bn2`; ViT: token patch của khối cuối). Heatmap ensemble là tổng có trọng số 0.45 / 0.40 / 0.15.
   - Cấu hình khóa nằm ở `dr-fundus-app/backend/models/model_b_locked.json`.

3. **Web:** React. Ba tab: tổng quan, Model B, giải thích. FastAPI phục vụ API tại cổng 8000. Bản `frontend/dist` được mount tại `/` nếu đã build.

4. **Mobile:** Model A chạy bằng ONNX trên máy. Model B gọi server. Phiếu PDF liệt kê 6 lớp của ensemble.

---

## ⚡ Hướng dẫn Chạy Nhanh Ứng dụng trên Windows

Đặt ba file sau vào `dr-fundus-app/backend/models/` (không commit; `.gitignore` chặn mọi `*.pth`, ViT khoảng 345MB):

| File | Kernel Kaggle (riêng tư, tài khoản nguynhuythanh) |
|---|---|
| `vitb16_384_best.pth` | `nguynhuythanh/klcn-retinal-6class-v3-vitb16-384` |
| `effb4_448_best.pth` | `nguynhuythanh/klcn-retinal-6class-v3-effb4-448` (version 3) |
| `effb4_448_twohead_best.pth` | `nguynhuythanh/klcn-retinal-6class-v3-e-twohead` |

Tải bằng Kaggle CLI (cần `kaggle.json` của tài khoản sở hữu kernel trong `%USERPROFILE%\.kaggle\`). Chạy từng lệnh trong PowerShell:

```powershell
pip install -U kaggle
cd dr-fundus-app\backend\models
kaggle kernels output nguynhuythanh/klcn-retinal-6class-v3-vitb16-384 -p . --file-pattern 'vitb16_384_best\.pth$'
kaggle kernels output nguynhuythanh/klcn-retinal-6class-v3-effb4-448/3 -p . --file-pattern 'effb4_448_best\.pth$'
kaggle kernels output nguynhuythanh/klcn-retinal-6class-v3-e-twohead -p . --file-pattern 'effb4_448_twohead_best\.pth$'
Get-FileHash .\*.pth -Algorithm SHA256
```

SHA256 đúng được ghi trong `model_b_locked.json` (trường `sha256` của từng nhánh). Không có `--file-pattern` thì lệnh sẽ tải cả `*_last.pth` (có optimizer, rất lớn).

Chạy backend:

```powershell
cd dr-fundus-app\backend
pip install -r requirements.txt
python run_server.py
```

- Web: [http://127.0.0.1:8000](http://127.0.0.1:8000) khi đã có `frontend/dist`, hoặc `npm run dev` trong `frontend`.
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Kiểm tra giải mã, không cần GPU: `python test_decode.py`
- Kiểm tra đầy đủ (cần ba checkpoint): `python test_backend.py`, sau đó `python test_app_e2e.py`

---

## 📚 Danh mục Tài liệu & Báo cáo Nghiên cứu trong Repository

- `Bao_Cao_Tien_Do_Tuan_KLCN_28-09_den_05-10.docx`, `Bao_Cao_Tien_Do_Tuan_KLCN_06-10_den_13-10.docx`, `Bao_Cao_Tien_Do_Tuan_KLCN_13-10_den_20-10.docx`: báo cáo tiến độ tuần (`Bao_Cao_Tien_Do_Tuan_KLCN.docx` là bản đầu).
- `dr-fundus-app/README.md`: cách chạy backend và chỗ đặt checkpoint.
- `dr_fundus_mobile/README.md`: app Flutter. Model B cần server. Không cần adb nếu chạy `flutter run -d windows`.
