"""Model B v3: weighted 3-branch ensemble, 6 classes (DR 0-4 + class 5 'other').

Branches (all trained on the Ben Graham 512 cache, EMA weights, best VAL SCORE):
- ViT-B/16-384 v3   timm vit_base_patch16_384.augreg_in21k_ft_in1k, 6 logits, softmax
- EffB4-448 v3      timm tf_efficientnet_b4.ns_jft_in1k, 6 logits, softmax
- EffB4-448 two-head (Phase E): backbone num_classes=0 + head_b Linear(5) + head_a Linear(1);
  p5 = sigmoid(A), p0..4 = (1 - p5) * softmax(B)
Each branch: Resize((s, s)) of the 512 cache image, ToTensor, ImageNet normalize,
TTA = mean of the probabilities of the image and its horizontal flip (as in train.py).
Ensemble p = sum_i w_i p_i, then the decode locked on VAL (models/model_b_locked.json).
"""
import base64
import io
import json
import os

import matplotlib
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

matplotlib.use("Agg")
import matplotlib.cm as cm  # noqa: E402

from app.decode import blend_probs, decode_record  # noqa: E402
from app.preprocess import cache512_from_bytes, cache512_from_pil  # noqa: E402

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
NUM_CLASSES = 6
LOCKED_SPEC = "model_b_locked.json"


class TwoHeadNet(nn.Module):
    """Same module layout as Phase E train.py so the state_dict loads with strict=True."""

    def __init__(self, backbone):
        super().__init__()
        self.backbone = backbone
        feat = backbone.num_features
        self.head_b = nn.Linear(feat, 5)
        self.head_a = nn.Linear(feat, 1)

    def forward(self, x):
        f = self.backbone(x)
        return torch.cat([self.head_b(f), self.head_a(f)], dim=1)


def twohead_probs(logits):
    logits = logits.float()
    p5 = torch.sigmoid(logits[:, 5:6])
    return torch.cat([(1.0 - p5) * torch.softmax(logits[:, :5], dim=1), p5], dim=1)


def build_branch_model(arch, kind):
    import timm

    if kind == "twohead":
        return TwoHeadNet(timm.create_model(arch, pretrained=False, num_classes=0))
    if arch.startswith("vit_"):
        return timm.create_model(arch, pretrained=False, num_classes=NUM_CLASSES, img_size=384)
    return timm.create_model(arch, pretrained=False, num_classes=NUM_CLASSES)


def _load_state_dict(path, device):
    try:
        state = torch.load(path, map_location=device, weights_only=True)
    except TypeError:
        state = torch.load(path, map_location=device)
    if isinstance(state, dict):
        for key in ("ema_state", "model_state", "state_dict"):
            if key in state and isinstance(state[key], dict):
                state = state[key]
                break
    if not isinstance(state, dict):
        raise RuntimeError(f"Checkpoint không phải state_dict: {os.path.basename(path)}")
    return {key.replace("module.", "", 1) if key.startswith("module.") else key: value for key, value in state.items()}


def _normalize_cam(cam):
    cam_min, cam_max = float(cam.min()), float(cam.max())
    if cam_max > cam_min:
        return (cam - cam_min) / (cam_max - cam_min)
    return np.zeros_like(cam)


class GradCAM:
    """Grad-CAM on one layer. CNN: 4D activation (B, C, H, W). ViT: tokens (B, N, C),
    patch tokens after the prefix tokens are reshaped to a square grid (24 x 24 for 384/16)."""

    def __init__(self, model, target_layer, kind, prefix_tokens=1):
        self.model = model
        self.kind = kind
        self.prefix_tokens = prefix_tokens
        self.activations = None
        self.gradients = None
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, inputs, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def heatmap(self, input_tensor, target_class, out_size):
        self.model.zero_grad(set_to_none=True)
        with torch.enable_grad():
            logits = self.model(input_tensor)
            # Two-head: column 5 is the other-disease logit (head A); 0-4 are head B logits.
            score = logits[0, int(target_class)]
            score.backward()
        act, grad = self.activations, self.gradients
        if act.dim() == 4:
            weights = grad.mean(dim=(2, 3), keepdim=True)
            cam = F.relu((weights * act).sum(dim=1, keepdim=True))
        else:
            act = act[:, self.prefix_tokens:, :]
            grad = grad[:, self.prefix_tokens:, :]
            weights = grad.mean(dim=1, keepdim=True)
            cam = F.relu((weights * act).sum(dim=-1))
            side = int(round(cam.shape[1] ** 0.5))
            if side * side != cam.shape[1]:
                raise RuntimeError("ViT Grad-CAM: số patch không tạo lưới vuông.")
            cam = cam.reshape(1, 1, side, side)
        cam = F.interpolate(cam, size=(out_size, out_size), mode="bilinear", align_corners=False)
        self.model.zero_grad(set_to_none=True)
        return _normalize_cam(cam.squeeze().detach().cpu().numpy())


def render_heatmap_overlay(cam_mask, img_np):
    colormap = matplotlib.colormaps["jet"] if hasattr(matplotlib, "colormaps") else cm.get_cmap("jet")
    heatmap_colored = colormap(cam_mask)[:, :, :3]
    overlay = np.clip(0.55 * img_np + 0.45 * heatmap_colored, 0, 1)
    buffered = io.BytesIO()
    Image.fromarray((overlay * 255).astype(np.uint8)).save(buffered, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")


def _metric_note(prefix, row, n_test):
    if not row:
        return ""
    text = (
        f"{prefix} | TEST n={n_test} | Acc {100.0 * float(row['acc']):.2f}% | "
        f"Macro-F1 {float(row['macro_f1']):.4f} | QWK_DR {float(row['qwk_dr']):.4f} | SCORE {float(row['score']):.4f}"
    )
    ci = row.get("score_ci95")
    if ci:
        text += f" (CI95 {float(ci[0]):.4f}–{float(ci[1]):.4f})"
    return text


class Branch:
    def __init__(self, spec, device):
        self.key = spec["key"]
        self.label = spec["label"]
        self.arch = spec["arch"]
        self.kind = spec["kind"]
        self.img_size = int(spec["img_size"])
        self.weight = float(spec["weight"])
        self.checkpoint = spec["checkpoint"]
        self.decode = spec["decode"]
        self.test = spec.get("test", {})
        self.device = device
        self.model = None
        self.cam = None
        self.transform = transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ])

    def load(self, models_dir):
        path = os.path.join(models_dir, self.checkpoint)
        model = build_branch_model(self.arch, self.kind)
        model.load_state_dict(_load_state_dict(path, self.device), strict=True)
        model.to(self.device).eval()
        self.model = model
        if self.arch.startswith("vit_"):
            self.cam = GradCAM(model, model.blocks[-1].norm1, "vit", getattr(model, "num_prefix_tokens", 1))
        else:
            net = model.backbone if self.kind == "twohead" else model
            self.cam = GradCAM(model, net.bn2, "cnn")

    def probs(self, tensor):
        """TTA: average of the probabilities of the image and its horizontal flip."""
        acc = None
        with torch.no_grad():
            for view in (tensor, torch.flip(tensor, dims=[3])):
                out = self.model(view).float()
                prob = twohead_probs(out) if self.kind == "twohead" else torch.softmax(out, dim=1)
                acc = prob if acc is None else acc + prob
        return (acc / 2.0).squeeze(0).cpu().numpy().astype(np.float64)


class DRClassifier:
    """Model B v3: weighted ensemble ViT-B/16-384 v3 + EffB4-448 v3 + EffB4-448 two-head."""

    def __init__(self, device=None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.models_dir = os.path.join(base_dir, "models")
        self.ready = False
        self.load_error = ""
        self.spec = {}
        self.branches = []
        self.decode = {}
        self.n_test = 8818
        try:
            self._read_locked_spec()
            self._load_models()
        except Exception as exc:
            self.ready = False
            self.load_error = str(exc)
            print(f"Model B was not loaded: {exc}", flush=True)

    @property
    def weights(self):
        return {branch.key: branch.weight for branch in self.branches}

    def _read_locked_spec(self):
        path = os.path.join(self.models_dir, LOCKED_SPEC)
        with open(path, "r", encoding="utf-8") as handle:
            self.spec = json.load(handle)
        self.decode = self.spec["ensemble"]["decode"]
        self.n_test = int(self.spec.get("n_test", self.n_test))
        self.branches = [Branch(item, self.device) for item in self.spec["branches"]]
        total = sum(branch.weight for branch in self.branches)
        if abs(total - 1.0) > 1e-6:
            raise RuntimeError(f"Tổng trọng số ensemble phải bằng 1, đang là {total}")

    def _load_models(self):
        missing = [
            b.checkpoint for b in self.branches
            if not (os.path.exists(os.path.join(self.models_dir, b.checkpoint))
                    and os.path.getsize(os.path.join(self.models_dir, b.checkpoint)) > 1000)
        ]
        if missing:
            raise RuntimeError(
                "Thiếu checkpoint Model B trong backend/models: " + ", ".join(missing)
                + ". Tải từ output các kernel Kaggle ghi trong models/model_b_locked.json (xem README)."
            )
        for branch in self.branches:
            branch.load(self.models_dir)
        self.ready = True
        print("Loaded Model B v3 ensemble " + ", ".join(f"{b.label} {b.weight:.2f}" for b in self.branches), flush=True)

    def ensemble_label(self):
        return " + ".join(f"{b.label} {b.weight:.2f}" for b in self.branches)

    def decode_text(self):
        d = self.decode
        text = f"{d['family']} t5={d['t5']}"
        if d.get("thresholds"):
            text += f" ngưỡng {d['thresholds']}"
        return text

    def _pack(self, model_used, stage, probs, heatmap, benchmark_note, branch=None, weight=None, decode=None):
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
            "branch": branch,
            "weight": weight,
            "decode": decode,
        }

    def preprocess(self, image_pil=None, raw_bytes=None):
        if raw_bytes is not None:
            try:
                return cache512_from_bytes(raw_bytes)
            except Exception:
                pass
        return cache512_from_pil(image_pil)

    def predict_probs(self, image_pil=None, raw_bytes=None):
        """Probabilities only (no Grad-CAM). Returns (cache512 PIL, {key: probs}, ensemble probs)."""
        if not self.ready:
            raise RuntimeError(self.load_error or "Model B chưa được nạp.")
        img512 = self.preprocess(image_pil, raw_bytes)
        branch_probs = {}
        for branch in self.branches:
            tensor = branch.transform(img512).unsqueeze(0).to(self.device)
            branch_probs[branch.key] = branch.probs(tensor)
        ens = np.asarray(blend_probs([branch_probs[b.key] for b in self.branches], [b.weight for b in self.branches]), dtype=np.float64)
        return img512, branch_probs, ens

    def predict(self, image_pil, raw_bytes=None, with_heatmaps=True):
        img512, branch_probs, ens = self.predict_probs(image_pil, raw_bytes)
        stage = decode_record(ens, self.decode)
        display = np.asarray(img512, dtype=np.float32) / 255.0
        out_size = display.shape[0]
        cams, results = {}, {}
        for branch in self.branches:
            probs = branch_probs[branch.key]
            b_stage = decode_record(probs, branch.decode)
            heat = None
            if with_heatmaps:
                # Grad-CAM of every branch targets the class decoded by the ensemble,
                # so the blended map explains the reported result.
                tensor = branch.transform(img512).unsqueeze(0).to(self.device)
                cams[branch.key] = branch.cam.heatmap(tensor, stage, out_size)
                heat = render_heatmap_overlay(cams[branch.key], display)
            results[branch.key] = self._pack(
                f"{branch.label} (trọng số {branch.weight:.2f} trong ensemble)",
                b_stage, probs, heat,
                _metric_note(f"{branch.label} đơn lẻ", branch.test, self.n_test),
                branch=branch.key, weight=branch.weight, decode=branch.decode,
            )
        heat_ens = None
        if with_heatmaps:
            blended = sum(b.weight * cams[b.key] for b in self.branches)
            heat_ens = render_heatmap_overlay(_normalize_cam(blended), display)
        dr_result = self._pack(
            "Ensemble " + self.ensemble_label(),
            stage, ens, heat_ens,
            _metric_note("Ensemble 3 mô hình (khóa trên VAL)", self.spec["ensemble"].get("test", {}), self.n_test)
            + f" | decode {self.decode_text()}",
            branch="ensemble", weight=1.0, decode=self.decode,
        )
        return {
            "dr_result": dr_result,
            "dr_branches": [results[b.key] for b in self.branches],
            "dr_vit": results.get("vit3"),
            "dr_effb4": results.get("effb4"),
            "dr_twohead": results.get("e_twohead"),
            "dr_resnet": None,
        }
