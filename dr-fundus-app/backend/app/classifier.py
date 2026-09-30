import os
import io
import base64
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np
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

inference_transforms = transforms.Compose([
    transforms.Resize(224),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
])

def build_resnet50(num_classes=5):
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model

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
        cam = F.interpolate(cam, size=(224, 224), mode='bilinear', align_corners=False)
        cam = cam.squeeze().cpu().numpy()
        
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)
            
        return cam, output.detach()

class DRClassifier:
    def __init__(self, model_path: str = None, device: str = None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
            
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if model_path is None:
            model_path = os.path.join(base_dir, "models", "resnet50_ce_best.pth")
            
        self.model_path = model_path
        self.resnet_model = build_resnet50(num_classes=5)
        
        loaded = False
        # Check local path first
        weights_candidates = [
            self.model_path,
            os.path.join(base_dir, "models", "resnet50_ce_best.pth"),
            os.path.join(base_dir, "models", "resnet50_baseline_best.pth")
        ]
        for wp in weights_candidates:
            if wp and os.path.exists(wp) and os.path.getsize(wp) > 1000:
                state_dict = torch.load(wp, map_location=self.device)
                clean = {k.replace("module.", ""): v for k, v in state_dict.items()}
                self.resnet_model.load_state_dict(clean, strict=False)
                print(f"Loaded ResNet-50 weights from local file: {wp}")
                loaded = True
                break

        if not loaded:
            print("Local weights not found. Auto-downloading ResNet-50 from Hugging Face Hub (slyviee/klcn-resnet50-dr)...")
            try:
                from huggingface_hub import hf_hub_download
                downloaded_path = hf_hub_download(
                    repo_id="slyviee/klcn-resnet50-dr",
                    filename="resnet50_baseline_best.pth"
                )
                state_dict = torch.load(downloaded_path, map_location=self.device)
                clean = {k.replace("module.", ""): v for k, v in state_dict.items()}
                self.resnet_model.load_state_dict(clean, strict=False)
                print(f"Successfully loaded ResNet-50 weights from HF Hub cache: {downloaded_path}")
                loaded = True
            except Exception as e:
                print(f"Warning: Could not auto-download weights from Hugging Face Hub: {e}")
            
        self.resnet_model.to(self.device)
        self.resnet_model.eval()
        self.grad_cam = GradCAMResNet50(self.resnet_model, self.resnet_model.layer4[-1])

    def predict(self, image_pil: Image.Image) -> dict:
        img_rgb = image_pil.convert("RGB")
        crop_transform = transforms.Compose([
            transforms.Resize(224),
            transforms.CenterCrop(224)
        ])
        img_cropped = crop_transform(img_rgb)
        img_np = np.array(img_cropped) / 255.0
        
        tensor_input = inference_transforms(img_rgb).unsqueeze(0).to(self.device)
        
        # Heatmap & output
        cam_mask, logits = self.grad_cam.generate_heatmap(tensor_input)
        probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()
        pred_class = int(np.argmax(probs))
        
        # Colormap overlay
        if hasattr(matplotlib, "colormaps"):
            colormap = matplotlib.colormaps['jet']
        else:
            colormap = cm.get_cmap('jet')
            
        heatmap_colored = colormap(cam_mask)[:, :, :3]
        overlay = 0.55 * img_np + 0.45 * heatmap_colored
        overlay = np.clip(overlay, 0, 1)
        overlay_pil = Image.fromarray((overlay * 255).astype(np.uint8))
        
        # Convert overlay to base64
        buffered = io.BytesIO()
        overlay_pil.save(buffered, format="JPEG", quality=90)
        heatmap_b64 = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        info = SEVERITY_INFO[pred_class]
        prob_dict = {CLASSES[i]: float(probs[i]) for i in range(len(CLASSES))}
        
        return {
            "model_used": "ResNet-50 (Baseline Cross-Entropy)",
            "stage": pred_class,
            "stage_name": info["title"],
            "badge": info["badge"],
            "confidence": float(probs[pred_class]),
            "description": info["description"],
            "advice": info["advice"],
            "benchmark_note": "Macro F1: 0.5094 | QWK: 0.7072",
            "probabilities": prob_dict,
            "heatmap_base64": heatmap_b64
        }
