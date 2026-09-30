---
title: KLCN Diabetic Retinopathy Detection
emoji: 👁
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.20.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: AI Chan doan vong mac tieu duong voi ResNet-50 va ViT-B16
---

# He thong AI Chan doan Phan do Benh Vong mac Dai thao duong (Diabetic Retinopathy)

Du an nghien cuu va ung dung thuc nghiem phuc vu Khoa luan Tot nghiep Cu nhan Cong nghe Thong tin.

## Tong quan
- **Bo du lieu huan luyen:** EyePACS (Diabetic Retinopathy Detection - Resized) gom 5 cap do benh theo tieu chuan quoc te ICDR:
  - 0 - Khong benh (No DR)
  - 1 - Nhe (Mild DR)
  - 2 - Trung binh (Moderate DR)
  - 3 - Nang (Severe DR)
  - 4 - Tang sinh (Proliferative DR)
- **Kien truc mo hinh:**
  - ResNet-50 (Baseline Cross-Entropy Loss)
  - Vision Transformer ViT-B/16 (Weighted Cross-Entropy Loss)
- **Co che giai thich mo hinh (Explainable AI):**
  - Grad-CAM (tren CNN ResNet-50) va Transformer Attribution & Attention Map (tren ViT-B/16) truc quan hoa vung ton thuong tren day mat (vi phinh mach, xuat huyet, xuat tiet).
- **Thuoc do danh gia trong tam:**
  - **Quadratic Weighted Kappa (QWK):** Thuoc do danh gia do tuong dong co tinh trong so phat bac hai sai lech thu bac.
  - **Macro-F1 Score:** Danh gia can bang tren tap du lieu mat can bang phan lop nghiem trong.

## Cac tinh nang cua Demo
1. **Chan doan lam sang va Heatmap:** Cho phep chon giua ResNet-50 va ViT-B/16, nap anh day mat tu bo anh kiem thu (hoac tai anh len tu thiet bi) de suy luan xac suat 5 cap do va xuat ban do nhiet truc quan hoa ton thuong.
2. **Bao cao Thuoc do va So sanh Hieu nang:** Bang thong ke chi tiet ket qua thuc nghiem qua cac Epoch tu Notebook EyePACS Baseline, bieu do so sanh Macro-F1 / Loss va ma tran nham lan tren tap EyePACS.
