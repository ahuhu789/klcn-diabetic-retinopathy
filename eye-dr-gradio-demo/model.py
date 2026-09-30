import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np
import matplotlib.cm as cm

# 5 muc do benh vong mac tieu duong theo tieu chuan ICDR / EyePACS
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
        "advice": "Cap thiet: Can thiệp phau thuat cat dich kinh (Vitrectomy) hoac quang dong toan vong mac (PRP) ngay lap tuc de bao ton thi luc."
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
    """Xay dung kien truc ResNet-50 tuong thich checkpoint huan luyen."""
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model

def build_vit_b16(num_classes=5):
    """Xay dung kien truc ViT-B/16 qua timm tuong thich checkpoint huan luyen."""
    try:
        import timm
        model = timm.create_model('vit_base_patch16_224', pretrained=False, num_classes=num_classes)
        return model
    except Exception as e:
        print(f"Khong the khoi tao timm ViT-B/16: {e}")
        return None

class GradCAMResNet50:
    """Bo giai thich Grad-CAM cho ResNet-50 layer4."""
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

class GradCAMViT:
    """
    Bo giai thich Attention Attribution cho Vision Transformer (ViT-B/16).
    Dua tren phuong phap Transformer Attribution (Chefer et al. CVPR 2021)
    tich hop dao ham Attention va ma tran chu y cua token [CLS].
    """
    def __init__(self, model):
        self.model = model
        self.last_block = model.blocks[-1]
        # Dat fused_attn = False de trinh dien ro rang ma tran attention
        if hasattr(self.last_block.attn, "fused_attn"):
            self.last_block.attn.fused_attn = False
            
        self.attn_map = None
        def _attn_hook(module, inp, out):
            self.attn_map = out
            self.attn_map.retain_grad()
            
        # Hook truc tiep tren attn_drop cua block cuoi
        self.last_block.attn.attn_drop.register_forward_hook(_attn_hook)

    def generate_heatmap(self, input_tensor, target_class=None):
        self.model.zero_grad()
        output = self.model(input_tensor)
        
        if target_class is None:
            target_class = torch.argmax(output, dim=1).item()
            
        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1.0
        output.backward(gradient=one_hot, retain_graph=True)
        
        if self.attn_map is not None and self.attn_map.grad is not None:
            # self.attn_map: shape (B, H, N, N) voi N = 197 (CLS + 196 patches)
            grad = self.attn_map.grad
            relevance = (grad * self.attn_map).clamp(min=0)
            cls_relevance = relevance[:, :, 0, 1:].mean(dim=1) # (B, 196)
            
            # Raw attention tu CLS den cac patch
            raw_attn = self.attn_map[:, :, 0, 1:].mean(dim=1) # (B, 196)
            
            # Chuan hoa tung thanh phan
            rel_min, rel_max = cls_relevance.min(), cls_relevance.max()
            norm_rel = (cls_relevance - rel_min) / (rel_max - rel_min + 1e-8)
            
            raw_min, raw_max = raw_attn.min(), raw_attn.max()
            norm_raw = (raw_attn - raw_min) / (raw_max - raw_min + 1e-8)
            
            # Ket hop Relevancy gradient va Attention map
            combined = 0.5 * norm_rel + 0.5 * norm_raw
            H = W = int(196 ** 0.5) # 14
            cam = combined.reshape(1, 1, H, W)
            cam = F.interpolate(cam, size=(224, 224), mode='bilinear', align_corners=False)
            cam = cam.squeeze().detach().cpu().numpy()
            cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        else:
            cam = np.zeros((224, 224), dtype=np.float32)
            
        return cam, output.detach()

class DRInferenceEngine:
    """Quan ly nap trong so va suy luan cho ca ResNet-50 va ViT-B/16."""
    def __init__(self, device=None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device
            
        self.resnet_model = None
        self.resnet_cam = None
        self.vit_model = None
        self.vit_cam = None
        
        self._load_resnet()
        self._load_vit()

    def _load_resnet(self):
        try:
            self.resnet_model = build_resnet50(num_classes=5)
            # Uu tien checkpoint tu EyePACS baseline
            weights_paths = ["resnet50_ce_best.pth", "resnet50_baseline_best.pth"]
            loaded = False
            for wp in weights_paths:
                if os.path.exists(wp) and os.path.getsize(wp) > 1000:
                    state_dict = torch.load(wp, map_location=self.device)
                    clean = {k.replace("module.", ""): v for k, v in state_dict.items()}
                    self.resnet_model.load_state_dict(clean, strict=False)
                    print(f"Da nap trong so ResNet-50 tu: {wp}")
                    loaded = True
                    break
            if not loaded:
                print("Chua tim thay weights ResNet-50 cuc bo, thu tai tu HF Hub...")
                try:
                    from huggingface_hub import hf_hub_download
                    wp = hf_hub_download(repo_id="slyviee/klcn-resnet50-dr", filename="resnet50_baseline_best.pth")
                    state_dict = torch.load(wp, map_location=self.device)
                    clean = {k.replace("module.", ""): v for k, v in state_dict.items()}
                    self.resnet_model.load_state_dict(clean, strict=False)
                    print("Da nap trong so ResNet-50 tu HF Hub!")
                except Exception as e:
                    print(f"Khong the tai weights tu HF Hub: {e}")
                    
            self.resnet_model.to(self.device)
            self.resnet_model.eval()
            self.resnet_cam = GradCAMResNet50(self.resnet_model, self.resnet_model.layer4[-1])
        except Exception as e:
            print(f"Loi khi khoi tao ResNet-50: {e}")

    def _load_vit(self):
        try:
            self.vit_model = build_vit_b16(num_classes=5)
            if self.vit_model is None:
                return
            wp = "vit_b16_wce_best.pth"
            if os.path.exists(wp) and os.path.getsize(wp) > 1000:
                state_dict = torch.load(wp, map_location=self.device)
                clean = {k.replace("module.", ""): v for k, v in state_dict.items()}
                self.vit_model.load_state_dict(clean, strict=False)
                print(f"Da nap trong so ViT-B/16 tu: {wp}")
            else:
                print("Chua tim thay weights ViT-B/16 cuc bo, thu tai tu HF Hub...")
                try:
                    from huggingface_hub import hf_hub_download
                    wp_hf = hf_hub_download(repo_id="slyviee/klcn-vit-b16-dr", filename="vit_b16_wce_best.pth")
                    state_dict = torch.load(wp_hf, map_location=self.device)
                    clean = {k.replace("module.", ""): v for k, v in state_dict.items()}
                    self.vit_model.load_state_dict(clean, strict=False)
                    print("Da nap trong so ViT-B/16 tu HF Hub!")
                except Exception as e:
                    print(f"ViT-B/16 chua co weights tu HF Hub: {e}")
                    
            self.vit_model.to(self.device)
            self.vit_model.eval()
            self.vit_cam = GradCAMViT(self.vit_model)
        except Exception as e:
            print(f"Loi khi khoi tao ViT-B/16: {e}")

def render_probability_bars(probabilities):
    """
    Sinh ma HTML hien thi thanh phan tram xac suat truc quan,
    tranh loi schema OpenAPI cua gr.Label tren Gradio 5.
    """
    class_labels = [
        ("0 - Khong benh (No DR)", "#10b981"),
        ("1 - Nhe (Mild DR)", "#eab308"),
        ("2 - Trung binh (Moderate DR)", "#f97316"),
        ("3 - Nang (Severe DR)", "#ef4444"),
        ("4 - Tang sinh (Proliferative DR)", "#8b5cf6")
    ]
    max_idx = int(np.argmax(probabilities))
    
    html = """
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 14px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; margin-top: 6px;">
        <div style="font-size: 14px; font-weight: 600; color: #1f2937; margin-bottom: 12px;">Phan bo Xac suat 5 Cap do (%)</div>
    """
    for i, (name, color) in enumerate(class_labels):
        prob_val = probabilities[i] * 100
        is_max = (i == max_idx)
        font_weight = "600" if is_max else "400"
        highlight = f"background: {color}15; border-left: 3px solid {color}; padding-left: 8px;" if is_max else "padding-left: 8px;"
        
        html += f"""
        <div style="margin-bottom: 10px; {highlight}">
            <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 3px; font-weight: {font_weight}; color: #374151;">
                <span>{name}</span>
                <span>{prob_val:.1f}%</span>
            </div>
            <div style="background-color: #f3f4f6; border-radius: 4px; height: 8px; overflow: hidden;">
                <div style="background-color: {color}; width: {prob_val:.1f}%; height: 100%; border-radius: 4px;"></div>
            </div>
        </div>
        """
    html += "</div>"
    return html

def process_image_and_predict(image_pil, model_choice, engine):
    """
    Tien hanh tien xu ly, suy luan va giai thich Grad-CAM theo mo hinh duoc chon.
    """
    if image_pil is None:
        return None, None, "Vui long chon hoac tai len mot anh day mat vong mac.", "<div></div>"

    img_rgb = image_pil.convert("RGB")
    crop_transform = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224)
    ])
    img_cropped = crop_transform(img_rgb)
    img_np = np.array(img_cropped) / 255.0
    tensor_input = inference_transforms(img_rgb).unsqueeze(0).to(engine.device)

    # Chon mo hinh
    is_vit = "ViT" in model_choice
    if is_vit and engine.vit_model is not None and engine.vit_cam is not None:
        cam_mask, logits = engine.vit_cam.generate_heatmap(tensor_input)
        model_used = "Vision Transformer (ViT-B/16 Weighted CE)"
        benchmark_note = "Model Benchmark: Macro F1: 0.5117 | QWK: 0.6551"
    else:
        cam_mask, logits = engine.resnet_cam.generate_heatmap(tensor_input)
        model_used = "ResNet-50 (Baseline Cross-Entropy)"
        benchmark_note = "Model Benchmark: Macro F1: 0.5094 | QWK: 0.7072"

    probabilities = F.softmax(logits, dim=1).squeeze().cpu().numpy()
    pred_class_idx = int(np.argmax(probabilities))

    # Tron ban do nhiet Grad-CAM len anh goc
    import matplotlib
    if hasattr(matplotlib, "colormaps"):
        colormap = matplotlib.colormaps['jet']
    else:
        colormap = cm.get_cmap('jet')
    heatmap_colored = colormap(cam_mask)[:, :, :3]
    overlay = 0.55 * img_np + 0.45 * heatmap_colored
    overlay = np.clip(overlay, 0, 1)
    overlay_pil = Image.fromarray((overlay * 255).astype(np.uint8))

    info = SEVERITY_INFO[pred_class_idx]
    advice_card = f"""
### {info['title']}
- **Mo hinh suy luan:** `{model_used}`
- **Danh gia mo hinh:** `{benchmark_note}`
- **Muc do phan loai:** `{info['badge']}`
- **Mo ta ton thuong:** {info['description']}
- **Khuyen nghi lam sang:** {info['advice']}
"""
    prob_html = render_probability_bars(probabilities)

    return img_cropped, overlay_pil, advice_card, prob_html
