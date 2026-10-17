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

2. **Model B – ensemble 6 lớp (ResNet-50 0.25 + ViT-B/16 0.75):**
   - Checkpoint `*_best_score.pth` của kernel `klcn-retinal-6class-v2-hybrid-14ep-early` (version 4).
   - Lớp 0–4 là thang DR. Lớp 5 là nhóm tổn thương không phải DR, không nêu tên từng bệnh.
   - Ảnh đi qua Ben Graham 256 (cắt nền tối, hệ số 4, Gaussian σ = 10, mặt nạ tròn 0.95) rồi chuẩn hóa ImageNet.
   - Nếu argmax là lớp 5 thì kết quả là lớp 5. Ngược lại, mức DR là giá trị kỳ vọng của 5 lớp đầu, cắt bởi `[0.95, 1.35, 2.35, 3.15]`.
   - Test khóa, n = 8818: Acc 69.62%, macro-F1 0.5371, QWK 0.5842, SCORE 0.5607.
   - Grad-CAM của từng nhánh lấy lớp đã giải mã. Heatmap ensemble là trộn 0.25 / 0.75.

3. **Web:** React. Ba tab: tổng quan, Model B, giải thích. FastAPI phục vụ API tại cổng 8000. Bản `frontend/dist` được mount tại `/` nếu đã build.

4. **Mobile:** Model A chạy bằng ONNX trên máy. Model B gọi server. Phiếu PDF liệt kê 6 lớp của ensemble.

---

## ⚡ Hướng dẫn Chạy Nhanh Ứng dụng trên Windows

Đặt hai file sau vào `dr-fundus-app/backend/models/` (không commit, ViT vượt 100MB):

- `resnet50_hybrid_ordinal_best_score.pth`
- `vit_b16_hybrid_ordinal_best_score.pth`

```powershell
cd dr-fundus-app\backend
pip install -r requirements.txt
python run_server.py
```

- Web: [http://127.0.0.1:8000](http://127.0.0.1:8000) khi đã có `frontend/dist`, hoặc `npm run dev` trong `frontend`.
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Kiểm tra giải mã, không cần GPU: `python test_decode.py`

---

## 📚 Danh mục Tài liệu & Báo cáo Nghiên cứu trong Repository

- `DEMO_GUIDE.md`: kịch bản demo web.
- `dr-fundus-app/README.md`: cách chạy backend và chỗ đặt checkpoint.
- `dr_fundus_mobile/README.md`: app Flutter. Model B cần server. Không cần adb nếu chạy `flutter run -d windows`.
