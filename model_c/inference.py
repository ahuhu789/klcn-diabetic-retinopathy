import os
import sys
import json
import torch
import numpy as np
from PIL import Image
from torchvision import transforms

sys.stdout.reconfigure(encoding='utf-8')

# Add workspace directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from model_c.models.model import RetinalMultiLabelClassifier

CLASS_NAMES = ['DR', 'ARMD', 'MYA', 'DN', 'ERM', 'BRVO', 'LS', 'ODC_GLAUCOMA', 'CRVO', 'RISK']

DISEASE_METADATA = {
    'DR': {'name': 'Diabetic Retinopathy', 'desc': 'Tổn thương vi mạch võng mạc do đái tháo đường'},
    'ARMD': {'name': 'Age-related Macular Degeneration', 'desc': 'Thoái hóa hoàng điểm do tuổi tác'},
    'MYA': {'name': 'Pathological Myopia', 'desc': 'Cận thị thoái hóa võng mạc / gai thị'},
    'DN': {'name': 'Drusen', 'desc': 'Lắng đọng chất hyaline dưới võng mạc'},
    'ERM': {'name': 'Epiretinal Membrane', 'desc': 'Màng trước võng mạc / co kéo hoàng điểm'},
    'BRVO': {'name': 'Branch Retinal Vein Occlusion', 'desc': 'Tắc nhánh tĩnh mạch võng mạc'},
    'LS': {'name': 'Laser Scars', 'desc': 'Sẹo quang đông laser sau điều trị'},
    'ODC_GLAUCOMA': {'name': 'Optic Disc Cupping / Glaucoma', 'desc': 'Lõm gai thị sinh lý lớn hoặc biến đổi glôcôm'},
    'CRVO': {'name': 'Central Retinal Vein Occlusion', 'desc': 'Tắc tĩnh mạch trung tâm võng mạc'},
    'RISK': {'name': 'General Disease Risk', 'desc': 'Tín hiệu phát hiện tổn thương bệnh lý võng mạc bất thường'}
}

DEFAULT_CHECKPOINT = os.path.join(parent_dir, "model_c", "experiments_output", "E2_RFMiD_ODIR_Harmonized_best.pth")

class RetinalDiseaseInference:
    """
    Model C Inference Engine
    Strict Production Mode: Must load verified trained checkpoint.
    Demo mode and random initialization are strictly disabled.
    """
    def __init__(self, checkpoint_path=None, device=None):
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
            
        self.num_classes = len(CLASS_NAMES)
        self.model = RetinalMultiLabelClassifier(num_classes=self.num_classes, pretrained=False)
        
        # Enforce checkpoint presence
        ckpt_path = checkpoint_path or DEFAULT_CHECKPOINT
        if not os.path.exists(ckpt_path):
            raise FileNotFoundError(
                f"[CRITICAL ERROR] Trained checkpoint not found at: '{ckpt_path}'. "
                "Demo mode and random initialization are disabled per scientific audit protocol."
            )
            
        ckpt = torch.load(ckpt_path, map_location=self.device)
        state_dict = ckpt['model_state_dict'] if 'model_state_dict' in ckpt else ckpt
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()
        
        # Load verified validation thresholds from checkpoint
        if 'thresholds' in ckpt and ckpt['thresholds'] is not None:
            self.thresholds = np.array(ckpt['thresholds'])
            self.threshold_source = f"Trained checkpoint epoch {ckpt.get('epoch', 'unknown')} validation-optimized"
        else:
            raise ValueError(f"Checkpoint at '{ckpt_path}' is missing calibrated threshold vector.")
            
        self.checkpoint_epoch = ckpt.get('epoch', None)
        self.checkpoint_val_macro_f1 = ckpt.get('val_macro_f1', None)
        self.checkpoint_path = ckpt_path
        
        # Standard fundus image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image_input):
        """
        Accepts:
            image_input: PIL.Image, numpy.ndarray, or file path str to a single fundus image.
        Returns:
            dict containing multi-label predictions, probabilities, and research disclaimer.
        """
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise FileNotFoundError(f"Input image not found: '{image_input}'")
            image = Image.open(image_input).convert('RGB')
        elif isinstance(image_input, np.ndarray):
            image = Image.fromarray(image_input).convert('RGB')
        elif isinstance(image_input, Image.Image):
            image = image_input.convert('RGB')
        else:
            raise ValueError("Input must be a PIL Image, numpy array, or valid file path string.")
            
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.inference_mode():
            logits = self.model(tensor)
            probs = torch.sigmoid(logits).squeeze(0).cpu().numpy()
            
        predictions = {}
        detected_diseases = []
        
        for idx, c in enumerate(CLASS_NAMES):
            prob = float(probs[idx])
            thresh = float(self.thresholds[idx])
            is_pos = bool(prob >= thresh)
            
            meta = DISEASE_METADATA.get(c, {'name': c, 'desc': ''})
            predictions[c] = {
                'disease_name': meta['name'],
                'vietnamese_desc': meta['desc'],
                'probability': round(prob, 4),
                'threshold': round(thresh, 4),
                'detected': is_pos
            }
            
            if is_pos and c != 'RISK':
                detected_diseases.append({
                    'code': c,
                    'name': meta['name'],
                    'vietnamese_desc': meta['desc'],
                    'confidence_pct': round(prob * 100, 2),
                    'probability': round(prob, 4),
                    'threshold': round(thresh, 4)
                })
                
        is_disease_risk = bool(
            probs[CLASS_NAMES.index('RISK')] >= self.thresholds[CLASS_NAMES.index('RISK')] 
            or len(detected_diseases) > 0
        )
        
        return {
            'model_name': 'Model C – Multi-Source Retinal Multi-Label Classifier',
            'model_version': '1.0.0-E2-Harmonized',
            'input_type': 'Single Fundus Image (RGB)',
            'overall_disease_risk': is_disease_risk,
            'detected_diseases': detected_diseases,
            'num_detected_conditions': len(detected_diseases),
            'full_probabilities': predictions,
            'checkpoint_meta': {
                'path': self.checkpoint_path,
                'epoch': self.checkpoint_epoch,
                'val_macro_f1': self.checkpoint_val_macro_f1,
                'threshold_source': self.threshold_source
            },
            'clinical_disclaimer': (
                "CẢNH BÁO Y KHOA: Đây là mô hình nghiên cứu khoa học phục vụ khóa luận tốt nghiệp (Model C). "
                "Kết quả dự đoán KHÔNG có giá trị chẩn đoán lâm sàng thay thế bác sĩ chuyên khoa mắt."
            )
        }

if __name__ == "__main__":
    print("Testing strict Model C inference loading from E2 checkpoint...")
    engine = RetinalDiseaseInference()
    sample_img = "dr-fundus-app/backend/samples/IDRiD_001.jpg"
    res = engine.predict(sample_img)
    print("Checkpoint loaded from:", res['checkpoint_meta']['path'])
    print("Epoch:", res['checkpoint_meta']['epoch'])
    print("Validation Macro-F1:", res['checkpoint_meta']['val_macro_f1'])
    print("Overall Risk:", res['overall_disease_risk'])
    print("Detected diseases:", res['detected_diseases'])
    print("Test passed successfully without fallback!")
