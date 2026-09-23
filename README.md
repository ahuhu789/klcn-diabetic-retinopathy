# Nghiên cứu Vision Transformer và Ứng dụng Phân loại Mức độ Bệnh Tiểu đường từ Ảnh Đáy Võng mạc Mắt

## Khóa Luận Tốt Nghiệp - Ngành Công nghệ Thông tin
**Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT) - Khoa Công nghệ Thông tin**

---

### Thông tin Chung
- **Đề tài:** Nghiên cứu Vision Transformer và ứng dụng phân loại mức độ bệnh tiểu đường từ ảnh đáy võng mạc mắt
- **Giảng viên hướng dẫn:** ThS. Trần Đình Toàn
- **Sinh viên thực hiện:**
  1. Nguyễn Huy Thanh – MSSV: 2001230885 – Lớp: 14DHTH01
  2. Nguyễn Cao Tấn Phúc – MSSV: 2001230680 – Lớp: 14DHTH03
  3. Nguyễn Chí Thành – MSSV: 2001230898 – Lớp: 14DHTH01
- **Thời gian thực hiện:** Tháng 09/2026

---

### Danh mục Tài liệu trong Repository
- `Bao_Cao_Tien_Do_Tuan_KLCN.docx`: Tệp Báo cáo tiến độ tuần khóa luận tốt nghiệp chi tiết, chuẩn thể thức văn bản HUIT (Times New Roman 13pt, lề chuẩn 3.5 - 2.5 - 2.5 - 2.5 cm, kèm 2 trang bìa chính và phụ).
- `xai_comparison.png`: Hình ảnh đối sánh Explainable AI (XAI) giữa ảnh gốc tiền xử lý, bản đồ nhiệt Grad-CAM trên ResNet-50 và Transformer Attention Heatmap trên ViT-B/16.

---

### Tóm tắt Nội dung Báo cáo Tuần Thực nghiệm
1. **Huấn luyện mô hình trên Kaggle:**
   - Bộ dữ liệu huấn luyện: EyePACS (Diabetic Retinopathy Detection - Resized) gồm 5 mức độ bệnh (ICDR 0–4).
   - Mô hình CNN Baseline: ResNet-50 (`resnet50_ce_best.pth`, Best QWK: 0.7072, Best Val Loss: 0.5530).
   - Mô hình Vision Transformer: ViT-B/16 (`vit_b16_wce_best.pth`, Best Macro-F1: 0.5117, Best QWK: 0.6551).
   - Hội chẩn Lai (Ensemble): Dự kiến đạt Macro-F1: 0.5420, QWK: 0.7350.
2. **Triển khai ứng dụng Demo trực tuyến:**
   - Không gian Hugging Face Space: [slyviee/klcn-diabetic-retinopathy](https://huggingface.co/spaces/slyviee/klcn-diabetic-retinopathy)
   - URL ứng dụng trực tiếp: [https://slyviee-klcn-diabetic-retinopathy.hf.space](https://slyviee-klcn-diabetic-retinopathy.hf.space)
   - Model Weights Hub: [slyviee/klcn-vit-b16-dr](https://huggingface.co/slyviee/klcn-vit-b16-dr)
3. **Giải quyết bài toán kỹ thuật:**
   - Khắc phục lỗi tương thích OpenAPI boolean schema trên Gradio 5.20.
   - Nghiên cứu và hiện thực hóa thành công thuật toán **Transformer Attribution kết hợp Self-Attention Map** (Chefer et al., CVPR 2021) cho Vision Transformer.
   - Chuẩn hóa liêm chính dữ liệu học thuật: Khẳng định EyePACS là tập dữ liệu huấn luyện duy nhất, ảnh IDRiD chỉ phục vụ kiểm thử giao diện.
