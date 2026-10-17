# RetinaGuard AI: cổng ảnh đáy mắt và ensemble 6 lớp

Model A kiểm tra ảnh gốc. Model B là ensemble ResNet-50 (0.25) và ViT-B/16 (0.75) của lần train `klcn-retinal-6class-v2-hybrid-14ep-early` version 4.

Lớp 0–4 là thang DR. Lớp 5 là nhóm tổn thương không phải DR, không nêu tên từng bệnh. Ảnh của Model B đi qua Ben Graham 256 rồi chuẩn hóa ImageNet. Nếu argmax là lớp 5 thì kết quả là lớp 5. Ngược lại, mức DR là giá trị kỳ vọng của 5 lớp đầu, cắt bởi `[0.95, 1.35, 2.35, 3.15]`.

Test khóa, n = 8818: Acc 69.62%, macro-F1 0.5371, QWK 0.5842, SCORE 0.5607.

## Checkpoint

Đặt hai file này vào `backend/models/`. Git bỏ qua `*.pth` vì ViT khoảng 330MB.

- `resnet50_hybrid_ordinal_best_score.pth`
- `vit_b16_hybrid_ordinal_best_score.pth`

Không nạp trọng số 5 lớp cũ. Thiếu file thì `/api/health` trả `classifier_loaded: false` và `/api/predict` ghi lý do vào `dr_error`.

`ordinal_thresholds.csv` và `model_b_locked.json` đã là số của lần train này.

## Chạy

```powershell
cd dr-fundus-app\backend
pip install -r requirements.txt
python run_server.py
```

- API: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health
- Giao diện đã build: http://127.0.0.1:8000 nếu có `frontend/dist`
- Giao diện dev: trong `frontend`, `npm install` rồi `npm run dev`

```powershell
python test_decode.py
```

`test_decode.py` không cần GPU. `test_app_e2e.py` cần torch, timm, opencv và hai checkpoint.

## API

`POST /api/predict` nhận `file` (JPEG, PNG, WEBP, tối đa 25MB).

- `dr_result`: ensemble, lớp 0–5, heatmap trộn
- `dr_resnet`, `dr_vit`: từng nhánh, cùng quy tắc giải mã, heatmap riêng
- `dr_error`: lý do khi Model B không chạy

`GET /api/health` có `classifier_loaded`, `num_classes`, `ensemble_resnet_weight`, `ensemble_vit_weight`, `ordinal_thresholds`.

## Cấu trúc

```text
backend/app/gate.py          Model A, ảnh gốc
backend/app/preprocess.py    Ben Graham cho Model B
backend/app/decode.py        giải mã 6 lớp
backend/app/classifier.py    ensemble và Grad-CAM
frontend/src/App.jsx         tổng quan, Model B, giải thích
```

Kết quả chỉ phục vụ nghiên cứu khóa luận và không thay kết luận của bác sĩ mắt.
