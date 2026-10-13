import os
import io
import base64
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np
import pandas as pd
import timm
import matplotlib
matplotlib.use('Agg')
import matplotlib.cm as cm

# 5 cap do benh vong mac theo tieu chuan ICDR / EyePACS
CLASSES = [
    "0 - Khong benh (No DR)",
    "1 - Nhe (Mild DR)",
    "2 - Trung binh (Moderate DR)",
    "3 - Nang (Severe DR)",
    "4 - Tang sinh (Proliferative DR)"
]

SEVERITY_INFO = {
    0: {
        "title": "Giai doan 0: Khong phat hien ton thuong benh vong mac (No DR)",
        "badge": "Binh thuong",
        "description": "Vong mac hoan toan binh thuong, khong co dau hieu vi phinh mach hoac xuat huyet.",
        "advice": "Tai kham dinh ky sau 12 thang. Duy tri duong huyet va huyet ap o muc on dinh."
    },
    1: {
        "title": "Giai doan 1: Benh vong mac dai thao duong nhe (Mild NPDR)",
        "badge": "Muc do Nhe",
        "description": "Xuat hien vi phinh mach nho (microaneurysms) o cac mao mach vong mac.",
        "advice": "Kiem tra lai day mat sau 6 - 9 thang. Quan ly chat che chi so HbA1c va lipid mau."
    },
    2: {
        "title": "Giai doan 2: Benh vong mac dai thao duong trung binh (Moderate NPDR)",
        "badge": "Muc do Trung binh",
        "description": "Xuat hien nhieu vi phinh mach, xuat huyet hinh cham hoac ngon lua, kem xuat tiet cung va xuat tiet mem.",
        "advice": "Kham chuyen khoa nhan sau 3 - 6 thang. Can chup mach huynh quang day mat neu co nghi ngo phu hoang diem."
    },
    3: {
        "title": "Giai doan 3: Benh vong mac dai thao duong nang (Severe NPDR)",
        "badge": "Muc do Nang (Tien tang sinh)",
        "description": "Ton thuong nghiem trong theo quy tac 4-2-1: Xuat huyet vong mac tai 4 goc phan tu hoac xoan tinh mach tai 2 goc.",
        "advice": "Nguy co cao tien trien sang the tang sinh. Can can thiep quang dong laser hoac tiem noi nhan Anti-VEGF kip thoi."
    },
    4: {
        "title": "Giai doan 4: Benh vong mac dai thao duong tang sinh (Proliferative DR)",
        "badge": "Muc do Nguy hiem (Tang sinh)",
        "description": "Hinh thanh tan mach bat thuong de vo gay xuat huyet dich kinh hoac bong vong mac co keo.",
        "advice": "Cap thiet: Can thiep phau thuat cat dich kinh (Vitrectomy) hoac quang dong toan vong mac (PRP) ngay lap tuc de bao ton thi luc."
    }
}

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
IMG_SIZE = 256

inference_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
])

def build_resnet50(num_classes=5):
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model

def build_vit_b16(num_classes=5):
    return timm.create_model(
        'vit_base_patch16_224',
        pretrained=False,
        img_size=IMG_SIZE,
        num_classes=num_classes
    )

class GradCAMResNet50:
    """
    Grad-CAM for CNN architecture (ResNet-50 layer4).
    Extracts high-resolution convolutional feature map activations and gradients.
    """
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

    def generate_heatmap(self, input_tensor, target_class=None):
        self.model.zero_grad()
        output = self.model(input_tensor)
        
        if target_class is None:
            target_class = torch.argmax(output, dim=1).item()
            
        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1.0
        output.backward(gradient=one_hot, retain_graph=True)
        
        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True)
        cam = torch.sum(weights * self.activations, dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=(IMG_SIZE, IMG_SIZE), mode='bilinear', align_corners=False)
        cam = cam.squeeze().cpu().numpy()
        
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)
            
        return cam, output.detach()

class GradCAMViT:
    """
    Grad-CAM for Vision Transformer (ViT-B/16).
    Extracts Self-Attention block patch tokens, gradients, and projects attention to 2D image coordinates.
    """
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

    def generate_heatmap(self, input_tensor, target_class=None):
        self.model.zero_grad()
        output = self.model(input_tensor)
        
        if target_class is None:
            target_class = torch.argmax(output, dim=1).item()
            
        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1.0
        output.backward(gradient=one_hot, retain_graph=True)
        
        # Patch tokens are at index 1: (excluding CLS token at 0)
        act = self.activations[:, 1:, :]   # (1, 256, 768)
        grad = self.gradients[:, 1:, :]     # (1, 256, 768)
        
        weights = torch.mean(grad, dim=1, keepdim=True) # (1, 1, 768) channel importance
        cam = torch.sum(weights * act, dim=-1)           # (1, 256) spatial patch importance
        cam = F.relu(cam)
        
        h = w = int(np.sqrt(cam.shape[1])) # 16x16 patch grid
        cam = cam.reshape(1, 1, h, w)
        cam = F.interpolate(cam, size=(IMG_SIZE, IMG_SIZE), mode='bilinear', align_corners=False)
        cam = cam.squeeze().cpu().numpy()
        
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)
            
        return cam, output.detach()

def render_heatmap_overlay(cam_mask: np.ndarray, img_np: np.ndarray) -> str:
    """Combines 2D CAM mask [0, 1] with RGB normalized image [0, 1] using Jet colormap."""
    if hasattr(matplotlib, "colormaps"):
        colormap = matplotlib.colormaps['jet']
    else:
        colormap = cm.get_cmap('jet')
        
    heatmap_colored = colormap(cam_mask)[:, :, :3]
    overlay = 0.55 * img_np + 0.45 * heatmap_colored
    overlay = np.clip(overlay, 0, 1)
    overlay_pil = Image.fromarray((overlay * 255).astype(np.uint8))
    
    buffered = io.BytesIO()
    overlay_pil.save(buffered, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

class DRClassifier:
    """
    Diabetic Retinopathy Dual Staging Engine:
    - ResNet-50 Standalone (CNN - Local Pathology Focus + Grad-CAM)
    - ViT-B/16 Standalone (Vision Transformer - Global Self-Attention Focus + Grad-CAM)
    - Zero Leakage: Evaluated on Patient-stratified split
    - Optimal Ordinal Thresholding for both models
    """
    def __init__(self, device: str = None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
            
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(base_dir, "models")
        
        # 1. Nạp ngưỡng cắt Ordinal Thresholds tối ưu
        self.thresholds = [0.95, 1.6759, 2.05, 3.25]
        thresh_csv = os.path.join(models_dir, "ordinal_thresholds.csv")
        if os.path.exists(thresh_csv):
            try:
                tdf = pd.read_csv(thresh_csv)
                if "threshold" in tdf.columns and len(tdf) == 4:
                    self.thresholds = [round(float(v), 4) for v in tdf["threshold"].values]
                    print(f"Loaded Optimal Ordinal Thresholds from CSV: {self.thresholds}")
            except Exception as e:
                print(f"Using default ordinal thresholds {self.thresholds}: {e}")
        
        # 2. Khởi tạo & nạp trọng số ResNet-50 Hybrid Ordinal
        self.resnet_model = build_resnet50(num_classes=5)
        r50_candidates = [
            os.path.join(models_dir, "resnet50_hybrid_ordinal_best_qwk.pth"),
            os.path.join(models_dir, "resnet50_ce_best.pth"),
            os.path.join(models_dir, "resnet50_baseline_best.pth")
        ]
        r50_loaded = False
        for wp in r50_candidates:
            if wp and os.path.exists(wp) and os.path.getsize(wp) > 1000:
                state_dict = torch.load(wp, map_location=self.device)
                clean = {k.replace("module.", ""): v for k, v in state_dict.items()}
                self.resnet_model.load_state_dict(clean, strict=False)
                print(f"Loaded ResNet-50 model from: {os.path.basename(wp)}")
                r50_loaded = True
                break
        
        if not r50_loaded:
            print("Downloading ResNet-50 from Hugging Face Hub (slyviee/klcn-resnet50-dr)...")
            try:
                from huggingface_hub import hf_hub_download
                downloaded_path = hf_hub_download(
                    repo_id="slyviee/klcn-resnet50-dr",
                    filename="resnet50_baseline_best.pth"
                )
                state_dict = torch.load(downloaded_path, map_location=self.device)
                clean = {k.replace("module.", ""): v for k, v in state_dict.items()}
                self.resnet_model.load_state_dict(clean, strict=False)
                print("Loaded ResNet-50 from HF Hub cache.")
            except Exception as e:
                print(f"Warning: could not load ResNet-50: {e}")

        self.resnet_model.to(self.device)
        self.resnet_model.eval()
        self.grad_cam_resnet = GradCAMResNet50(self.resnet_model, self.resnet_model.layer4[-1])

        # 3. Khởi tạo & nạp trọng số ViT-B/16 Hybrid Ordinal
        self.vit_model = None
        self.vit_loaded = False
        self.grad_cam_vit = None
        vit_path = os.path.join(models_dir, "vit_b16_hybrid_ordinal_best_qwk.pth")
        if os.path.exists(vit_path) and os.path.getsize(vit_path) > 1000:
            try:
                self.vit_model = build_vit_b16(num_classes=5)
                vit_ckpt = torch.load(vit_path, map_location=self.device)
                self.vit_model.load_state_dict(vit_ckpt, strict=False)
                self.vit_model.to(self.device)
                self.vit_model.eval()
                self.grad_cam_vit = GradCAMViT(self.vit_model, self.vit_model.blocks[-1].norm1)
                self.vit_loaded = True
                print("Loaded ViT-B/16 Hybrid Ordinal model successfully! (Grad-CAM ViT Enabled)")
            except Exception as e:
                print(f"Note: ViT-B/16 could not be loaded ({e}).")

    def predict(self, image_pil: Image.Image) -> dict:
        img_rgb = image_pil.convert("RGB")
        
        # Tiền xử lý khớp với kích thước huấn luyện 256x256
        crop_transform = transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE))
        ])
        img_cropped = crop_transform(img_rgb)
        img_np = np.array(img_cropped) / 255.0
        
        tensor_input = inference_transforms(img_rgb).unsqueeze(0).to(self.device)
        levels = np.arange(5, dtype=np.float32)
        
        # ============================================================
        # 1. MO HINH RESNET-50 (CNN) - TACH BIET HOAN TOAN
        # ============================================================
        cam_mask_r50, logits_r50 = self.grad_cam_resnet.generate_heatmap(tensor_input)
        probs_r50 = F.softmax(logits_r50, dim=1).squeeze().detach().cpu().numpy()
        
        exp_sev_r50 = float(np.sum(probs_r50 * levels))
        pred_stage_r50 = int(np.digitize(exp_sev_r50, self.thresholds))
        pred_stage_r50 = min(max(pred_stage_r50, 0), 4)
        
        heatmap_r50_b64 = render_heatmap_overlay(cam_mask_r50, img_np)
        info_r50 = SEVERITY_INFO[pred_stage_r50]
        prob_dict_r50 = {CLASSES[i]: round(float(probs_r50[i]), 4) for i in range(len(CLASSES))}
        
        dr_resnet = {
            "model_used": "ResNet-50 (CNN Architecture)",
            "stage": pred_stage_r50,
            "stage_name": info_r50["title"],
            "badge": info_r50["badge"],
            "confidence": round(float(probs_r50[pred_stage_r50]), 4),
            "description": info_r50["description"],
            "advice": info_r50["advice"],
            "benchmark_note": f"QWK: 0.6352 | Accuracy: 74.22% | Macro-F1: 0.4904 (Ngưỡng Ordinal: {self.thresholds})",
            "probabilities": prob_dict_r50,
            "heatmap_base64": heatmap_r50_b64
        }
        
        # ============================================================
        # 2. MO HINH VISION TRANSFORMER VIT-B/16 - TACH BIET HOAN TOAN
        # ============================================================
        dr_vit = None
        if self.vit_loaded and self.vit_model is not None and self.grad_cam_vit is not None:
            cam_mask_vit, logits_vit = self.grad_cam_vit.generate_heatmap(tensor_input)
            probs_vit = F.softmax(logits_vit, dim=1).squeeze().detach().cpu().numpy()
            
            exp_sev_vit = float(np.sum(probs_vit * levels))
            pred_stage_vit = int(np.digitize(exp_sev_vit, self.thresholds))
            pred_stage_vit = min(max(pred_stage_vit, 0), 4)
            
            heatmap_vit_b64 = render_heatmap_overlay(cam_mask_vit, img_np)
            info_vit = SEVERITY_INFO[pred_stage_vit]
            prob_dict_vit = {CLASSES[i]: round(float(probs_vit[i]), 4) for i in range(len(CLASSES))}
            
            dr_vit = {
                "model_used": "Vision Transformer ViT-B/16 (Self-Attention Architecture)",
                "stage": pred_stage_vit,
                "stage_name": info_vit["title"],
                "badge": info_vit["badge"],
                "confidence": round(float(probs_vit[pred_stage_vit]), 4),
                "description": info_vit["description"],
                "advice": info_vit["advice"],
                "benchmark_note": f"QWK: 0.6972 | Accuracy: 78.54% | Macro-F1: 0.5335 (Ngưỡng Ordinal: {self.thresholds})",
                "probabilities": prob_dict_vit,
                "heatmap_base64": heatmap_vit_b64
            }
            
        # dr_result tra ve ViT neu co, neu khong thi ResNet de duy tri tuong thich nguoc
        primary_result = dr_vit if dr_vit is not None else dr_resnet
        
        return {
            "dr_resnet": dr_resnet,
            "dr_vit": dr_vit,
            "dr_result": primary_result
        }
