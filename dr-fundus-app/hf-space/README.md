---
title: KLCN Diabetic Retinopathy Detection
emoji: 👁
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
short_description: Fundus gate + 6-class v3 ensemble (ViT-B/16 + EffB4) API
---

# RetinaGuard AI API (Model B v3)

FastAPI backend of the KLCN thesis project, served on port 7860 (CPU).

- Model A: fundus gate (MobileNetV3, TFLite, threshold 0.965) on the raw image.
- Model B v3: Ben Graham 512 preprocessing, then ensemble ViT-B/16-384 (0.45) +
  EfficientNet-B4-448 (0.40) + EfficientNet-B4-448 two-head (0.15), horizontal-flip TTA,
  hierarchical decode, Grad-CAM heatmaps.

Endpoints: `GET /api/health`, `GET /api/samples`, `GET /api/samples/{filename}`,
`POST /api/predict` (multipart field `file`), `GET /docs`.

Research use only. Not a substitute for an ophthalmologist.
