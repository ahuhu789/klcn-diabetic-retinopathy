import os
import io
import csv
import json
import base64

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import timm
import matplotlib
matplotlib.use("Agg")
import matplotlib.cm as cm

from app.decode import advanced_predict_one, blend_probs
from app.preprocess import ben_graham_uint8

CLASSES = [
    "0 - Không bệnh (No DR)",
    "1 - Nhẹ (Mild NPDR)",
    "2 - Trung bình (Moderate NPDR)",
    "3 - Nặng (Severe NPDR)",
    "4 - Tăng sinh (Proliferative DR)",
    "5 - Tổn thương không phải DR",
]

SEVERITY_INFO = {
    0: {
        "title": "Giai đoạn 0: Không phát hiện tổn thương bệnh võng mạc đái tháo đường",
        "badge": "Bình thường",
        "description": "Võng mạc không có dấu hiệu vi phình mạch hoặc xuất huyết thuộc thang DR.",
        "advice": "Tái khám định kỳ sau 12 tháng. Duy trì đường huyết và huyết áp ổn định.",
    },
    1: {
        "title": "Giai đoạn 1: Bệnh võng mạc đái tháo đường nhẹ (Mild NPDR)",
        "badge": "Mức độ nhẹ",
        "description": "Dấu hiệu phù hợp với vi phình mạch nhỏ ở mao mạch võng mạc.",
        "advice": "Kiểm tra lại đáy mắt sau 6–9 tháng. Theo dõi HbA1c và lipid máu.",
    },
    2: {
        "title": "Giai đoạn 2: Bệnh võng mạc đái tháo đường trung bình (Moderate NPDR)",
        "badge": "Mức độ trung bình",
        "description": "Nhiều vi phình mạch, xuất huyết dạng chấm hoặc ngọn lửa, có thể kèm xuất tiết.",
        "advice": "Khám chuyên khoa mắt sau 3–6 tháng. Cân nhắc chụp mạch huỳnh quang nếu nghi phù hoàng điểm.",
    },
    3: {
        "title": "Giai đoạn 3: Bệnh võng mạc đái tháo đường nặng (Severe NPDR)",
        "badge": "Mức độ nặng",
        "description": "Tổn thương nặng theo quy tắc 4-2-1: xuất huyết ở 4 góc phần tư hoặc tĩnh mạch chuỗi hạt.",
        "advice": "Nguy cơ tiến triển sang thể tăng sinh. Cần khám đáy mắt sớm để xem xét laser hoặc anti-VEGF.",
    },
    4: {
        "title": "Giai đoạn 4: Bệnh võng mạc đái tháo đường tăng sinh (Proliferative DR)",
        "badge": "Tăng sinh",
        "description": "Tân mạch dễ vỡ, có thể gây xuất huyết dịch kính hoặc bong võng mạc co kéo.",
        "advice": "Cần khám chuyên khoa mắt sớm. Đây không phải chỉ định phẫu thuật tự động từ một ảnh.",
    },
    5: {
        "title": "Lớp 5: Tổn thương võng mạc không thuộc thang DR",
        "badge": "Không phải DR",
        "description": "Ensemble gán ảnh vào nhóm tổn thương không phải bệnh võng mạc đái tháo đường. Lớp này là một nhóm chung, không nêu tên từng bệnh.",
        "advice": "Không đọc kết quả này như một chẩn đoán đục thủy tinh thể, glôcôm, AMD hay tắc mạch. Cần bác sĩ mắt xem ảnh.",
    },
}

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
IMG_SIZE = 256
NUM_CLASSES = 6
RESNET_FILENAME = "resnet50_hybrid_ordinal_best_score.pth"
VIT_FILENAME = "vit_b16_hybrid_ordinal_best_score.pth"

normalize = transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)


def build_resnet50(num_classes=NUM_CLASSES):
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def build_vit_b16(num_classes=NUM_CLASSES):
    return timm.create_model(
        "vit_base_patch16_224",
        pretrained=False,
        img_size=IMG_SIZE,
        num_classes=num_classes,
    )


def _load_state_dict(path, device):
    try:
        state = torch.load(path, map_location=device, weights_only=True)
    except TypeError:
        state = torch.load(path, map_location=device)
    if isinstance(state, dict) and "model_state" in state:
        state = state["model_state"]
    elif isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    if not isinstance(state, dict):
        raise RuntimeError(f"Checkpoint không phải state_dict: {os.path.basename(path)}")
    return {key.replace("module.", ""): value for key, value in state.items()}


class GradCAMResNet50:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self.target_layer.register_forward_hook(self._save_activation)
        self.target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate_heatmap(self, input_tensor, target_class):
        self.model.zero_grad(set_to_none=True)
        output = self.model(input_tensor)
        one_hot = torch.zeros_like(output)
        one_hot[0, int(target_class)] = 1.0
        output.backward(gradient=one_hot, retain_graph=False)
        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True)
        cam = torch.sum(weights * self.activations, dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=(IMG_SIZE, IMG_SIZE), mode="bilinear", align_corners=False)
        cam = cam.squeeze().detach().cpu().numpy()
        return _normalize_cam(cam)


class GradCAMViT:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self.target_layer.register_forward_hook(self._save_activation)
        self.target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate_heatmap(self, input_tensor, target_class):
        self.model.zero_grad(set_to_none=True)
        output = self.model(input_tensor)
        one_hot = torch.zeros_like(output)
        one_hot[0, int(target_class)] = 1.0
        output.backward(gradient=one_hot, retain_graph=False)
        act = self.activations[:, 1:, :]
        grad = self.gradients[:, 1:, :]
        weights = torch.mean(grad, dim=1, keepdim=True)
        cam = torch.sum(weights * act, dim=-1)
        cam = F.relu(cam)
        side = int(round(cam.shape[1] ** 0.5))
        if side * side != cam.shape[1]:
            raise RuntimeError("ViT Grad-CAM không khớp lưới patch 16x16 của ảnh 256.")
        cam = cam.reshape(1, 1, side, side)
        cam = F.interpolate(cam, size=(IMG_SIZE, IMG_SIZE), mode="bilinear", align_corners=False)
        cam = cam.squeeze().detach().cpu().numpy()
        return _normalize_cam(cam)


def _normalize_cam(cam):
    cam_min, cam_max = float(cam.min()), float(cam.max())
    if cam_max > cam_min:
        return (cam - cam_min) / (cam_max - cam_min)
    return np.zeros_like(cam)


def render_heatmap_overlay(cam_mask, img_np):
    if hasattr(matplotlib, "colormaps"):
        colormap = matplotlib.colormaps["jet"]
    else:
        colormap = cm.get_cmap("jet")
    heatmap_colored = colormap(cam_mask)[:, :, :3]
    overlay = np.clip(0.55 * img_np + 0.45 * heatmap_colored, 0, 1)
    overlay_pil = Image.fromarray((overlay * 255).astype(np.uint8))
    buffered = io.BytesIO()
    overlay_pil.save(buffered, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")


def _pct(value):
    return f"{100.0 * float(value):.2f}%"


def _metric_note(prefix, row, n_test):
    return (
        f"{prefix} | test n={n_test} | Acc {_pct(row['acc'])} | "
        f"Macro-F1 {float(row['macro_f1']):.4f} | QWK {float(row['qwk_dr']):.4f}"
    )


class DRClassifier:
    """6-class ResNet-50 + ViT-B/16 ensemble from the locked v2 run.

    Reported result is 0.25 * ResNet + 0.75 * ViT, then the SCORE thresholds.
    There is no fallback to the older 5-class Hugging Face weights.
    """

    def __init__(self, device=None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.models_dir = os.path.join(base_dir, "models")
        self.ready = False
        self.load_error = ""
        self.thresholds = [0.95, 1.35, 2.35, 3.15]
        self.resnet_weight = 0.25
        self.vit_weight = 0.75
        self.n_test = 8818
        self.test_argmax = {}
        self.test_ensemble = {}
        self.resnet_model = None
        self.vit_model = None
        self.grad_cam_resnet = None
        self.grad_cam_vit = None
        self._read_locked_spec()
        self._read_thresholds()
        try:
            self._load_models()
        except Exception as exc:
            self.ready = False
            self.load_error = str(exc)
            print(f"Model B was not loaded: {exc}", flush=True)

    def _read_locked_spec(self):
        path = os.path.join(self.models_dir, "model_b_locked.json")
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as handle:
            spec = json.load(handle)
        self.resnet_weight = float(spec["ensemble_resnet_weight"])
        self.vit_weight = float(spec["ensemble_vit_weight"])
        self.thresholds = [float(v) for v in spec["thresholds"]]
        self.n_test = int(spec.get("n_test", self.n_test))
        self.test_argmax = spec.get("test_argmax", {})
        self.test_ensemble = spec.get("test_ensemble_threshold", {})

    def _read_thresholds(self):
        path = os.path.join(self.models_dir, "ordinal_thresholds.csv")
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) == 4 and "threshold" in rows[0]:
            self.thresholds = [float(row["threshold"]) for row in rows]
            print(f"Loaded ordinal thresholds: {self.thresholds}", flush=True)

    def _load_models(self):
        resnet_path = os.path.join(self.models_dir, RESNET_FILENAME)
        vit_path = os.path.join(self.models_dir, VIT_FILENAME)
        missing = [
            name for name, path in ((RESNET_FILENAME, resnet_path), (VIT_FILENAME, vit_path))
            if not (os.path.exists(path) and os.path.getsize(path) > 1000)
        ]
        if missing:
            raise RuntimeError(
                "Thiếu checkpoint Model B trong backend/models: " + ", ".join(missing)
                + ". Hai file best_score của lần train 6 lớp không được thay bằng trọng số 5 lớp."
            )
        resnet = build_resnet50(NUM_CLASSES)
        resnet.load_state_dict(_load_state_dict(resnet_path, self.device), strict=True)
        resnet.to(self.device)
        resnet.eval()
        vit = build_vit_b16(NUM_CLASSES)
        vit.load_state_dict(_load_state_dict(vit_path, self.device), strict=True)
        vit.to(self.device)
        vit.eval()
        self.resnet_model = resnet
        self.vit_model = vit
        self.grad_cam_resnet = GradCAMResNet50(resnet, resnet.layer4[-1])
        self.grad_cam_vit = GradCAMViT(vit, vit.blocks[-1].norm1)
        self.ready = True
        print(
            f"Loaded 6-class ensemble ResNet {self.resnet_weight:.2f} / ViT {self.vit_weight:.2f}",
            flush=True,
        )

    def _pack(self, model_used, stage, probs, heatmap, benchmark_note):
        info = SEVERITY_INFO[int(stage)]
        return {
            "model_used": model_used,
            "stage": int(stage),
            "stage_name": info["title"],
            "badge": info["badge"],
            "confidence": round(float(probs[int(stage)]), 4),
            "description": info["description"],
            "advice": info["advice"],
            "benchmark_note": benchmark_note,
            "probabilities": {CLASSES[i]: round(float(probs[i]), 4) for i in range(NUM_CLASSES)},
            "heatmap_base64": heatmap,
        }

    def predict(self, image_pil):
        if not self.ready:
            raise RuntimeError(self.load_error or "Model B chưa được nạp.")
        enhanced = ben_graham_uint8(np.asarray(image_pil.convert("RGB")), target_size=IMG_SIZE)
        display = enhanced.astype(np.float32) / 255.0
        tensor = transforms.ToTensor()(Image.fromarray(enhanced))
        tensor = normalize(tensor).unsqueeze(0).to(self.device)

        with torch.no_grad():
            probs_resnet = F.softmax(self.resnet_model(tensor), dim=1).squeeze(0).detach().cpu().numpy()
            probs_vit = F.softmax(self.vit_model(tensor), dim=1).squeeze(0).detach().cpu().numpy()
        probs_ensemble = np.asarray(
            blend_probs(probs_resnet, probs_vit, self.resnet_weight, self.vit_weight),
            dtype=np.float64,
        )
        stage_resnet = advanced_predict_one(probs_resnet, self.thresholds)
        stage_vit = advanced_predict_one(probs_vit, self.thresholds)
        stage_ensemble = advanced_predict_one(probs_ensemble, self.thresholds)

        cam_resnet = self.grad_cam_resnet.generate_heatmap(tensor, stage_resnet)
        cam_vit = self.grad_cam_vit.generate_heatmap(tensor, stage_vit)
        cam_ensemble = _normalize_cam(
            self.resnet_weight * cam_resnet + self.vit_weight * cam_vit
        )
        heat_resnet = render_heatmap_overlay(cam_resnet, display)
        heat_vit = render_heatmap_overlay(cam_vit, display)
        heat_ensemble = render_heatmap_overlay(cam_ensemble, display)

        resnet_row = self.test_argmax.get("resnet", {})
        vit_row = self.test_argmax.get("vit", {})
        ensemble_row = self.test_ensemble or {}
        note_resnet = _metric_note("Test argmax ResNet-50", resnet_row, self.n_test) if resnet_row else ""
        note_vit = _metric_note("Test argmax ViT-B/16", vit_row, self.n_test) if vit_row else ""
        note_ensemble = ""
        if ensemble_row:
            note_ensemble = (
                _metric_note("Test ensemble ngưỡng SCORE", ensemble_row, self.n_test)
                + f" | SCORE {float(ensemble_row['score']):.4f}"
                + f" | trọng số ResNet {self.resnet_weight:.2f} / ViT {self.vit_weight:.2f}"
                + f" | ngưỡng {self.thresholds}"
            )

        dr_resnet = self._pack(
            "ResNet-50 (trọng số 0.25 trong ensemble)",
            stage_resnet,
            probs_resnet,
            heat_resnet,
            note_resnet,
        )
        dr_vit = self._pack(
            "ViT-B/16 (trọng số 0.75 trong ensemble)",
            stage_vit,
            probs_vit,
            heat_vit,
            note_vit,
        )
        dr_result = self._pack(
            f"Ensemble ResNet {self.resnet_weight:.2f} + ViT {self.vit_weight:.2f}",
            stage_ensemble,
            probs_ensemble,
            heat_ensemble,
            note_ensemble,
        )
        return {"dr_resnet": dr_resnet, "dr_vit": dr_vit, "dr_result": dr_result}
