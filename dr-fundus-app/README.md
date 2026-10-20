# RetinaGuard AI: cổng ảnh đáy mắt và ensemble 6 lớp (Model B v3)

Model A kiểm tra ảnh gốc. Model B là ensemble có trọng số của ba mô hình v3:

| Nhánh | Kiến trúc (timm) | Ảnh vào | Trọng số | TEST SCORE đơn lẻ |
|---|---|---|---|---|
| ViT-B/16-384 v3 | `vit_base_patch16_384.augreg_in21k_ft_in1k` | 384 | 0.45 | 0.6507 |
| EfficientNet-B4-448 v3 | `tf_efficientnet_b4.ns_jft_in1k` | 448 | 0.40 | 0.6429 |
| EfficientNet-B4-448 hai đầu ra (Pha E) | `tf_efficientnet_b4.ns_jft_in1k` + `head_b` Linear(5) + `head_a` Linear(1) | 448 | 0.15 | 0.6363 |

Bộ v2 (ResNet-50 0.25 + ViT-B/16 256 0.75, ngưỡng `[0.95, 1.35, 2.35, 3.15]`) đã bị bỏ.

Lớp 0–4 là thang DR. Lớp 5 là nhóm tổn thương không phải DR, không nêu tên từng bệnh.

## Tiền xử lý và suy luận

Giống hệt huấn luyện (`app/preprocess.py`, `app/classifier.py`):

1. Đọc ảnh bằng OpenCV như kernel cache `nguynhuythanh/klcn-retinal-6class-bengraham512-cache` (cạnh dài > 2000 px thì đọc giảm 2 lần, > 4000 px giảm 4 lần).
2. Cắt nền tối (gray ≤ 10), resize 512, `4·ảnh − 4·GaussianBlur(σ = 20) + 128`, mặt nạ tròn 0.95 (nền 128), mã hóa JPEG q92 rồi đọc lại.
3. Mỗi nhánh: `Resize((s, s))` (384 hoặc 448), `ToTensor`, chuẩn hóa ImageNet; TTA = trung bình xác suất của ảnh và ảnh lật ngang.
4. Nhánh hai đầu ra: `p5 = sigmoid(A)`, `p0..4 = (1 − p5)·softmax(B)`.
5. `p = 0.45·p_ViT + 0.40·p_EffB4 + 0.15·p_twohead`; giải mã phân tầng: lớp 5 nếu `p5 > 0.50`, nếu không lấy `argmax(p[0:5])`.

Trọng số và t5 được chọn chỉ trên VAL (231 điểm simplex bước 0.05, cùng bộ tìm giải mã của Pha D). TEST chấm một lần, bootstrap theo bệnh nhân 1000 lần:

| Tập | Acc | macro-F1 | QWK_DR | SCORE | SCORE CI95 | QWK_DR EyePACS |
|---|---|---|---|---|---|---|
| VAL (n = 8796) | 0.7974 | 0.6219 | 0.7592 | 0.6906 | – | 0.7577 |
| TEST (n = 8818) | 0.7936 | 0.6151 | 0.7572 | 0.6861 | 0.6684–0.7035 | 0.7552 (CI95 0.7342–0.7756) |

SCORE = 0.5·macro-F1(6 lớp) + 0.5·QWK_DR, QWK_DR = kappa bậc hai của `argmax(p[:, :5])` trên nhãn thật 0–4.
So sánh ghép cặp trên TEST: so với D2 (ViT + EffB4) +0.0125 (CI95 +0.0063 đến +0.0183); so với D3 (4 mô hình có v2) −0.0006 (CI95 −0.0043 đến +0.0034), tức tương đương.

Đã kiểm tra trên 52 ảnh TEST gốc (tải lẻ từ Kaggle): xác suất của app lệch tối đa 0.0012 (ensemble) so với xác suất kernel Kaggle ghi ra, lớp giải mã trùng 52/52.

## Checkpoint

Đặt ba file vào `backend/models/`. Git bỏ qua `*.pth`.

| File | Nguồn (output kernel Kaggle riêng tư) |
|---|---|
| `vitb16_384_best.pth` | `nguynhuythanh/klcn-retinal-6class-v3-vitb16-384` |
| `effb4_448_best.pth` | `nguynhuythanh/klcn-retinal-6class-v3-effb4-448` version 3 |
| `effb4_448_twohead_best.pth` | `nguynhuythanh/klcn-retinal-6class-v3-e-twohead` |

```powershell
cd dr-fundus-app\backend\models
kaggle kernels output nguynhuythanh/klcn-retinal-6class-v3-vitb16-384 -p . --file-pattern 'vitb16_384_best\.pth$'
kaggle kernels output nguynhuythanh/klcn-retinal-6class-v3-effb4-448/3 -p . --file-pattern 'effb4_448_best\.pth$'
kaggle kernels output nguynhuythanh/klcn-retinal-6class-v3-e-twohead -p . --file-pattern 'effb4_448_twohead_best\.pth$'
```

Mỗi file là `state_dict` EMA (không có tiền tố `module.`). Thiếu file thì `/api/health` trả `classifier_loaded: false` và `/api/predict` ghi lý do vào `dr_error`.

File trong `backend/models/` được commit:

- `model_b_locked.json`: trọng số, giải mã, kích thước ảnh, tên checkpoint, SHA256, kernel nguồn, số liệu VAL/TEST.
- `ensemble_weight_search_v3.csv`: giải mã tốt nhất trên VAL cho từng điểm trọng số (231 dòng).
- `decode_v3.csv`: giải mã khóa của ensemble và của từng nhánh khi đứng riêng.
- `fundus_gate.tflite`: Model A (không đổi).

## Chạy

```powershell
cd dr-fundus-app\backend
pip install -r requirements.txt
python run_server.py
```

- API: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health
- Giao diện đã build: http://127.0.0.1:8000 nếu có `frontend/dist`
- Giao diện dev: trong `frontend`, chạy `npm install` rồi `npm run dev`

```powershell
python test_decode.py
python test_backend.py
python test_app_e2e.py
```

`test_decode.py` không cần torch. `test_backend.py` và `test_app_e2e.py` cần torch, timm, opencv và ba checkpoint. Trên CPU 8 luồng, một ảnh mất khoảng 0.6 s nếu không tính Grad-CAM và khoảng 2 s nếu có Grad-CAM ba nhánh.

## API

`POST /api/predict` nhận `file` (JPEG, PNG, WEBP, tối đa 25MB).

- `dr_result`: ensemble, lớp 0–5, heatmap trộn theo trọng số
- `dr_branches`: danh sách ba nhánh (`branch` = `vit3`, `effb4`, `e_twohead`; có `weight`, `decode`, heatmap riêng); lớp của mỗi nhánh dùng giải mã khóa của nhánh đó khi đứng riêng
- `dr_vit`, `dr_effb4`, `dr_twohead`: cùng nội dung, truy cập theo tên
- `dr_resnet`: luôn `null` (giữ để client cũ không lỗi)
- `ensemble_weights`, `dr_error`

`GET /api/health` có `classifier_loaded`, `num_classes`, `model_b_version`, `ensemble_weights`, `decode`, `branches`.

## Cấu trúc

```text
backend/app/gate.py          Model A, ảnh gốc
backend/app/preprocess.py    Ben Graham 512 giống cache huấn luyện
backend/app/decode.py        giải mã 6 lớp (argmax6 / hierarchical / hierarchical_ordinal)
backend/app/classifier.py    3 nhánh, TTA, ensemble và Grad-CAM
frontend/src/App.jsx         tổng quan, Model B, giải thích
```

Kết quả chỉ phục vụ nghiên cứu khóa luận và không thay kết luận của bác sĩ mắt.
