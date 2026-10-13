import os
import nbformat as nbf

def create_eval_notebook():
    nb = nbf.v4.new_notebook()
    nb['metadata'] = {
        'kernelspec': {
            'display_name': 'Python 3',
            'language': 'python',
            'name': 'python3'
        },
        'language_info': {
            'name': 'python',
            'version': '3.10.0'
        }
    }
    nb['cells'] = []

    def add_code(source):
        nb['cells'].append(nbf.v4.new_code_cell(source))

    # Cell 1: Imports
    add_code("""import os
import time
import json
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.models import efficientnet_b0

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Evaluation running on: {device}", flush=True)

UNIFIED_CLASSES = ['DR', 'ARMD', 'MYA', 'DN', 'ERM', 'BRVO', 'LS', 'ODC_GLAUCOMA', 'CRVO', 'RISK']
NUM_CLASSES = len(UNIFIED_CLASSES)
""")

    # Cell 2: Model definition
    add_code("""class RetinalMultiLabelClassifier(nn.Module):
    def __init__(self, num_classes=10, dropout=0.3):
        super().__init__()
        self.backbone = efficientnet_b0(weights=None)
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout, inplace=True),
            nn.Linear(in_features, num_classes)
        )
    def forward(self, x):
        return self.backbone(x)
""")

    # Cell 3: Locate files
    add_code("""# Locate test CSV and images
file_cache = {}
for root, _, files in os.walk('/kaggle/input'):
    for f in files:
        if f not in file_cache:
            file_cache[f] = os.path.join(root, f)

print(f"Total indexed input files: {len(file_cache)}", flush=True)

test_csv_path = file_cache.get('RFMiD_Testing_Labels.csv')
print(f"Test CSV path: {test_csv_path}", flush=True)
df_test = pd.read_csv(test_csv_path)
print(f"Loaded {len(df_test)} test records", flush=True)

class TestDataset(Dataset):
    def __init__(self, df, transform):
        self.df = df
        self.transform = transform
        
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_id = int(row['ID'])
        fn = f"{img_id}.png"
        img_path = file_cache.get(fn)
        image = Image.open(img_path).convert('RGB')
        tensor = self.transform(image)
        
        # Targets
        targets = [
            int(row['DR']), int(row['ARMD']), int(row['MYA']), int(row['DN']), int(row['ERM']),
            int(row['BRVO']), int(row['LS']), int(row['ODC']), int(row['CRVO']), int(row['Disease_Risk'])
        ]
        return tensor, torch.tensor(targets, dtype=torch.float32), f"rfmid_{img_id}"

eval_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

test_dataset = TestDataset(df_test, eval_transform)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=2)
""")

    # Cell 4: Evaluate & Export Raw Predictions for E1, E2, E3
    add_code("""checkpoints = {
    'E1': file_cache.get('E1_RFMiD_Baseline_best.pth'),
    'E2': file_cache.get('E2_RFMiD_ODIR_Harmonized_best.pth'),
    'E3': file_cache.get('E3_Ablation_Naive_ODIR_best.pth')
}

for exp_id, ckpt_p in checkpoints.items():
    print(f"\\nEvaluating {exp_id} using {ckpt_p}...", flush=True)
    ckpt = torch.load(ckpt_p, map_location=device)
    model = RetinalMultiLabelClassifier(num_classes=NUM_CLASSES, dropout=0.3).to(device)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()
    
    thresholds = np.array(ckpt['thresholds'])
    print(f"Applied thresholds: {[round(t, 4) for t in thresholds]}", flush=True)
    
    all_img_ids = []
    all_targets = []
    all_probs = []
    
    with torch.no_grad():
        for images, targets, img_ids in test_loader:
            images = images.to(device)
            logits = model(images)
            probs = torch.sigmoid(logits).cpu().numpy()
            all_probs.append(probs)
            all_targets.append(targets.numpy())
            all_img_ids.extend(img_ids)
            
    all_probs = np.concatenate(all_probs, axis=0)
    all_targets = np.concatenate(all_targets, axis=0)
    all_preds = (all_probs >= thresholds).astype(int)
    
    # Build detailed raw predictions DataFrame
    rows = []
    for i in range(len(all_img_ids)):
        r = {'image_id': all_img_ids[i]}
        # Ground truth
        for c_idx, c in enumerate(UNIFIED_CLASSES):
            r[f'gt_{c}'] = int(all_targets[i, c_idx])
        # Probabilities
        for c_idx, c in enumerate(UNIFIED_CLASSES):
            r[f'prob_{c}'] = round(float(all_probs[i, c_idx]), 6)
        # Thresholds
        for c_idx, c in enumerate(UNIFIED_CLASSES):
            r[f'thresh_{c}'] = round(float(thresholds[c_idx]), 4)
        # Binary predictions
        for c_idx, c in enumerate(UNIFIED_CLASSES):
            r[f'pred_{c}'] = int(all_preds[i, c_idx])
        rows.append(r)
        
    df_raw = pd.DataFrame(rows)
    out_csv = f"raw_test_predictions_{exp_id}.csv"
    df_raw.to_csv(out_csv, index=False)
    print(f"Saved {len(df_raw)} raw predictions to {out_csv}", flush=True)
    
print("\\nAll raw test predictions exported successfully!", flush=True)
""")

    os.makedirs('model_c/kaggle_eval_kernel', exist_ok=True)
    nb_path = 'model_c/kaggle_eval_kernel/export_raw_predictions.ipynb'
    with open(nb_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Created eval notebook at {nb_path}")

if __name__ == '__main__':
    create_eval_notebook()
