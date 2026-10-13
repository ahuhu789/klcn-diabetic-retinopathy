import os
import json
import nbformat as nbf

def create_notebook():
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

    def add_md(source):
        nb['cells'].append(nbf.v4.new_markdown_cell(source))

    # Cell 1: Markdown title
    add_md("""# Model C: Multi-Source Single-Image Retinal Disease Classification
## Experiments E1 (RFMiD Baseline), E2 (Harmonized RFMiD+ODIR), E3 (Ablation)
**Undergraduate Thesis Research**
- **Model Architecture**: Pretrained EfficientNet-B0 Backbone
- **Input**: Exactly ONE RGB Fundus Image
- **Loss**: Masked BCEWithLogitsLoss
- **Evaluation**: Macro-F1, Micro-F1, Per-class F1, AUROC, AP, Confusion Matrices
- **Protocol**: Threshold tuning on Validation ONLY; Evaluated on untouched RFMiD Test set.
""")

    # Cell 2: Imports & Environment Check
    add_code("""import os
import sys
import re
import time
import json
import random
import numpy as np
import pandas as pd
from PIL import Image
from collections import Counter
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)

# Seed for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
if torch.cuda.is_available():
    print(f"Device Name: {torch.cuda.get_device_name(0)}")
""")

    # Cell 3: Find dataset paths
    add_code("""# Locate datasets in Kaggle input or local fallback
RFMID_INPUT_DIR = None
ODIR_INPUT_DIR = None

for root, dirs, files in os.walk('/kaggle/input'):
    if 'RFMiD_Training_Labels.csv' in files:
        RFMID_INPUT_DIR = root
    if 'data.xlsx' in files and 'ODIR' in root.upper():
        ODIR_INPUT_DIR = root

# Fallback searches if needed
if RFMID_INPUT_DIR is None:
    for candidate in [
        '/kaggle/input/retinal-disease-classification',
        '/kaggle/input/retinal-fundus-multi-disease-rfmid',
        'model_c/metadata/rfmid'
    ]:
        if os.path.exists(candidate):
            RFMID_INPUT_DIR = candidate
            break

if ODIR_INPUT_DIR is None:
    for candidate in [
        '/kaggle/input/ocular-disease-recognition-odir5k',
        '/kaggle/input/odir5k-classification',
        'model_c/metadata/odir'
    ]:
        if os.path.exists(candidate):
            ODIR_INPUT_DIR = candidate
            break

print(f"RFMiD Input Dir: {RFMID_INPUT_DIR}")
print(f"ODIR Input Dir:  {ODIR_INPUT_DIR}")
""")

    # Cell 4: Class definitions and Harmonization Logic
    add_code("""UNIFIED_CLASSES = [
    'DR',            # Diabetic Retinopathy
    'ARMD',          # Age-related Macular Degeneration
    'MYA',           # Pathological Myopia
    'DN',            # Drusen
    'ERM',           # Epiretinal Membrane
    'BRVO',          # Branch Retinal Vein Occlusion
    'LS',            # Laser Scars
    'ODC_GLAUCOMA',  # Optic Disc Cupping / Glaucoma
    'CRVO',          # Central Retinal Vein Occlusion
    'RISK'           # Disease Risk / Any pathology
]
NUM_CLASSES = len(UNIFIED_CLASSES)
print(f"Target Multi-label Classes ({NUM_CLASSES}): {UNIFIED_CLASSES}")
""")

    # Cell 5: Build Unified Metadata with Fast File Index
    add_code("""print("Building file index from /kaggle/input...", flush=True)
t_idx_0 = time.time()
file_cache = {}
for root, _, files in os.walk('/kaggle/input'):
    for f in files:
        if f not in file_cache:
            file_cache[f] = os.path.join(root, f)
print(f"Indexed {len(file_cache)} files in {time.time() - t_idx_0:.2f}s", flush=True)

def find_file_cached(filename):
    return file_cache.get(filename, None)

def build_datasets_dataframe():
    records = []
    
    # 1. RFMiD (Official Splits)
    rf_train_csv = find_file_cached('RFMiD_Training_Labels.csv') or 'model_c/metadata/rfmid/RFMiD_Training_Labels.csv'
    rf_val_csv = find_file_cached('RFMiD_Validation_Labels.csv') or 'model_c/metadata/rfmid/RFMiD_Validation_Labels.csv'
    rf_test_csv = find_file_cached('RFMiD_Testing_Labels.csv') or 'model_c/metadata/rfmid/RFMiD_Testing_Labels.csv'
    
    for split_name, csv_p in [('train', rf_train_csv), ('val', rf_val_csv), ('test', rf_test_csv)]:
        df = pd.read_csv(csv_p)
        for _, row in df.iterrows():
            img_id = int(row['ID'])
            fn = f"{img_id}.png"
            img_path = find_file_cached(fn)
            
            rec = {
                'image_id': f"rfmid_{img_id}",
                'image_path': img_path,
                'source': 'RFMiD',
                'patient_group': f"rfmid_{img_id}",
                'split': split_name,
                'DR': int(row['DR']),
                'ARMD': int(row['ARMD']),
                'MYA': int(row['MYA']),
                'DN': int(row['DN']),
                'ERM': int(row['ERM']),
                'BRVO': int(row['BRVO']),
                'LS': int(row['LS']),
                'ODC_GLAUCOMA': int(row['ODC']),
                'CRVO': int(row['CRVO']),
                'RISK': int(row['Disease_Risk'])
            }
            for c in UNIFIED_CLASSES:
                rec[f'mask_{c}'] = 1
            records.append(rec)
            
    print(f"Loaded RFMiD records: {len(records)}", flush=True)
    
    # 2. ODIR (Eye-Keyword Harmonized)
    odir_xlsx = find_file_cached('data.xlsx') or 'model_c/metadata/odir/data.xlsx'
    df_odir = pd.read_excel(odir_xlsx)
    
    odir_added = 0
    severe_defects = ['no fundus image', 'anterior segment image', 'image offset', 'optic disk photographically invisible']
    
    for _, row in df_odir.iterrows():
        p_id = int(row['ID'])
        
        for eye_side, fn_col, kw_col in [('left', 'Left-Fundus', 'Left-Diagnostic Keywords'), 
                                         ('right', 'Right-Fundus', 'Right-Diagnostic Keywords')]:
            fn = str(row[fn_col]).strip()
            kw = str(row[kw_col]).strip()
            kw_l = kw.lower()
            
            if any(d in kw_l for d in severe_defects):
                continue
                
            img_path = find_file_cached(fn)
            
            targets = {c: -1 for c in UNIFIED_CLASSES}
            masks = {f'mask_{c}': 0 for c in UNIFIED_CLASSES}
            
            if kw_l == 'normal fundus':
                for c in UNIFIED_CLASSES:
                    targets[c] = 0
                    masks[f'mask_{c}'] = 1
                targets['RISK'] = 0
                masks['mask_RISK'] = 1
            else:
                targets['RISK'] = 1
                masks['mask_RISK'] = 1
                
                # DR
                dr_kws = ['mild nonproliferative retinopathy', 'moderate non proliferative retinopathy', 
                          'severe nonproliferative retinopathy', 'proliferative diabetic retinopathy', 
                          'severe proliferative diabetic retinopathy', 'diabetic retinopathy']
                if any(d in kw_l for d in dr_kws):
                    targets['DR'] = 1
                    masks['mask_DR'] = 1
                    
                # ARMD
                amd_kws = ['dry age-related macular degeneration', 'wet age-related macular degeneration', 'age-related macular degeneration']
                if any(a in kw_l for a in amd_kws):
                    targets['ARMD'] = 1
                    masks['mask_ARMD'] = 1
                    
                # MYA
                mya_kws = ['pathological myopia', 'myopia retinopathy', 'myopic retinopathy', 'myopic maculopathy']
                if any(m in kw_l for m in mya_kws):
                    targets['MYA'] = 1
                    masks['mask_MYA'] = 1
                    
                # DN
                if 'drusen' in kw_l:
                    targets['DN'] = 1
                    masks['mask_DN'] = 1
                    
                # ERM
                if 'epiretinal membrane' in kw_l or 'macular epiretinal membrane' in kw_l:
                    targets['ERM'] = 1
                    masks['mask_ERM'] = 1
                    
                # BRVO
                if 'branch retinal vein occlusion' in kw_l:
                    targets['BRVO'] = 1
                    masks['mask_BRVO'] = 1
                    
                # LS
                ls_kws = ['laser spot', 'post retinal laser surgery', 'post laser photocoagulation', 'fundus laser photocoagulation spots']
                if any(l in kw_l for l in ls_kws):
                    targets['LS'] = 1
                    masks['mask_LS'] = 1
                    
                # ODC_GLAUCOMA
                if 'glaucoma' in kw_l and 'suspected' not in kw_l:
                    targets['ODC_GLAUCOMA'] = 1
                    masks['mask_ODC_GLAUCOMA'] = 1
                    
                # CRVO
                if 'central retinal vein occlusion' in kw_l:
                    targets['CRVO'] = 1
                    masks['mask_CRVO'] = 1
                    
            rec = {
                'image_id': f"odir_{fn.replace('.jpg', '')}",
                'image_path': img_path,
                'source': 'ODIR',
                'patient_group': f"odir_patient_{p_id}",
                'split': 'train_odir_supplement'
            }
            rec.update(targets)
            rec.update(masks)
            
            # Naive targets for E3 ablation
            rec['naive_DR'] = int(row['D'])
            rec['naive_ARMD'] = int(row['A'])
            rec['naive_MYA'] = int(row['M'])
            rec['naive_GLAUCOMA'] = int(row['G'])
            rec['naive_NORMAL'] = int(row['N'])
            
            records.append(rec)
            odir_added += 1
            
    print(f"Loaded ODIR records: {odir_added}", flush=True)
    df_all = pd.DataFrame(records)
    return df_all

df_meta = build_datasets_dataframe()
print(f"Total unified records: {len(df_meta)}", flush=True)
print(df_meta.groupby(['source', 'split']).size(), flush=True)
""")

    # Cell 6: PyTorch Dataset Class
    add_code("""class RetinalFundusDataset(Dataset):
    def __init__(self, df, transform=None, is_naive_ablation=False):
        self.df = df.reset_index(drop=True)
        self.transform = transform
        self.is_naive_ablation = is_naive_ablation
        self.classes = UNIFIED_CLASSES
        
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = row['image_path']
        
        # Load image safely
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            # Fallback black image if missing/corrupt
            image = Image.new('RGB', (224, 224), color=0)
            
        if self.transform:
            image = self.transform(image)
            
        if self.is_naive_ablation and row['source'] == 'ODIR':
            # E3 Ablation: Naive patient-level label copying without masking
            targets = []
            masks = []
            for c in self.classes:
                if c == 'DR':
                    val = row['naive_DR']
                elif c == 'ARMD':
                    val = row['naive_ARMD']
                elif c == 'MYA':
                    val = row['naive_MYA']
                elif c == 'ODC_GLAUCOMA':
                    val = row['naive_GLAUCOMA']
                elif c == 'RISK':
                    val = 0 if row['naive_NORMAL'] == 1 else 1
                else:
                    val = 0  # Naively assumes unannotated classes are negative
                targets.append(val)
                masks.append(1.0)
            targets = torch.tensor(targets, dtype=torch.float32)
            masks = torch.tensor(masks, dtype=torch.float32)
        else:
            # E1 / E2: Harmonized targets and masks
            targets = torch.tensor([row[c] for c in self.classes], dtype=torch.float32)
            masks = torch.tensor([row[f'mask_{c}'] for c in self.classes], dtype=torch.float32)
            
        return image, targets, masks, row['image_id']

# Transforms
train_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.RandomResizedCrop(224, scale=(0.85, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

eval_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
""")

    # Cell 7: Model Architecture & Masked BCE Loss
    add_code("""class RetinalMultiLabelClassifier(nn.Module):
    def __init__(self, num_classes=10, dropout=0.3):
        super().__init__()
        self.backbone = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT)
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout, inplace=True),
            nn.Linear(in_features, num_classes)
        )
        
    def forward(self, x):
        return self.backbone(x)

class MaskedBCEWithLogitsLoss(nn.Module):
    def __init__(self, pos_weight=None):
        super().__init__()
        self.pos_weight = pos_weight

    def forward(self, logits, targets, mask):
        mask = mask.float()
        clean_targets = torch.clamp(targets.float(), min=0.0, max=1.0)
        pos_weight_tensor = self.pos_weight.to(logits.device) if self.pos_weight is not None else None
        
        bce_unreduced = F.binary_cross_entropy_with_logits(
            logits, clean_targets, pos_weight=pos_weight_tensor, reduction="none"
        )
        masked_bce = bce_unreduced * mask
        active_elements = mask.sum().clamp(min=1.0)
        return masked_bce.sum() / active_elements
""")

    # Cell 8: Validation & Evaluation Engine
    add_code("""def optimize_thresholds(y_true, y_probs, y_mask):
    N, C = y_probs.shape
    best_thresholds = np.full(C, 0.5)
    best_f1s = np.zeros(C)
    grid = np.linspace(0.1, 0.9, 81)
    
    for c in range(C):
        m = y_mask[:, c] == 1
        if m.sum() == 0 or (y_true[m, c] == 1).sum() == 0:
            continue
        y_c = y_true[m, c]
        p_c = y_probs[m, c]
        
        best_f1 = -1.0
        best_t = 0.5
        for t in grid:
            preds = (p_c >= t).astype(int)
            _, _, f1, _ = precision_recall_fscore_support(y_c, preds, average='binary', zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_t = t
        best_thresholds[c] = best_t
        best_f1s[c] = best_f1
    return best_thresholds, best_f1s

def evaluate_model(model, loader, device, thresholds=None):
    model.eval()
    all_logits = []
    all_targets = []
    all_masks = []
    
    with torch.no_grad():
        for images, targets, masks, _ in loader:
            images = images.to(device)
            logits = model(images)
            all_logits.append(logits.cpu())
            all_targets.append(targets.cpu())
            all_masks.append(masks.cpu())
            
    all_logits = torch.cat(all_logits, dim=0).numpy()
    all_targets = torch.cat(all_targets, dim=0).numpy()
    all_masks = torch.cat(all_masks, dim=0).numpy()
    all_probs = 1.0 / (1.0 + np.exp(-all_logits))
    
    # If thresholds not provided, optimize them
    if thresholds is None:
        thresholds, _ = optimize_thresholds(all_targets, all_probs, all_masks)
        
    y_preds = (all_probs >= thresholds).astype(int)
    
    # Compute metrics
    C = len(UNIFIED_CLASSES)
    f1_list, prec_list, rec_list, auroc_list, ap_list = [], [], [], [], []
    class_rows = []
    total_tp, total_fp, total_fn, total_tn = 0, 0, 0, 0
    
    for c in range(C):
        m = all_masks[:, c] == 1
        y_c = all_targets[m, c].astype(int)
        p_c = all_probs[m, c]
        pr_c = y_preds[m, c]
        
        n_pos = int((y_c == 1).sum())
        n_neg = int((y_c == 0).sum())
        
        tn, fp, fn, tp = 0, 0, 0, 0
        if len(np.unique(y_c)) > 1:
            cm = confusion_matrix(y_c, pr_c, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()
        elif len(y_c) > 0:
            if y_c[0] == 1:
                tp = int((pr_c == 1).sum())
                fn = int((pr_c == 0).sum())
            else:
                tn = int((pr_c == 0).sum())
                fp = int((pr_c == 1).sum())
                
        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_tn += tn
        
        p, r, f1, _ = precision_recall_fscore_support(y_c, pr_c, average='binary', zero_division=0)
        
        try:
            auroc = roc_auc_score(y_c, p_c) if (n_pos > 0 and n_neg > 0) else np.nan
        except:
            auroc = np.nan
        try:
            ap = average_precision_score(y_c, p_c) if n_pos > 0 else np.nan
        except:
            ap = np.nan
            
        f1_list.append(f1)
        prec_list.append(p)
        rec_list.append(r)
        if not np.isnan(auroc): auroc_list.append(auroc)
        if not np.isnan(ap): ap_list.append(ap)
        
        class_rows.append({
            'Class': UNIFIED_CLASSES[c],
            'Threshold': round(float(thresholds[c]), 4),
            'Pos_Support': n_pos,
            'Neg_Support': n_neg,
            'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn,
            'Precision': round(float(p), 4),
            'Recall': round(float(r), 4),
            'F1': round(float(f1), 4),
            'AUROC': round(float(auroc), 4) if not np.isnan(auroc) else None,
            'AP': round(float(ap), 4) if not np.isnan(ap) else None
        })
        
    macro_f1 = np.mean(f1_list)
    macro_p = np.mean(prec_list)
    macro_r = np.mean(rec_list)
    mean_auroc = np.mean(auroc_list) if len(auroc_list) > 0 else 0.0
    mean_ap = np.mean(ap_list) if len(ap_list) > 0 else 0.0
    
    micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = 2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) > 0 else 0.0
    
    summary = {
        'Macro_F1': round(float(macro_f1), 4),
        'Micro_F1': round(float(micro_f1), 4),
        'Macro_Precision': round(float(macro_p), 4),
        'Macro_Recall': round(float(macro_r), 4),
        'Mean_AUROC': round(float(mean_auroc), 4),
        'Mean_AP': round(float(mean_ap), 4),
        'Total_TP': int(total_tp), 'Total_FP': int(total_fp),
        'Total_FN': int(total_fn), 'Total_TN': int(total_tn)
    }
    
    return summary, pd.DataFrame(class_rows), thresholds, all_probs, all_targets, all_masks
""")

    # Cell 9: Trainer Function
    add_code("""def train_experiment(exp_name, train_df, val_df, epochs=10, batch_size=32, lr=3e-4, is_naive=False):
    print(f"\\n{'='*70}")
    print(f"STARTING EXPERIMENT: {exp_name}")
    print(f"Training Samples: {len(train_df)} | Validation Samples: {len(val_df)}")
    print(f"{'='*70}")
    
    train_dataset = RetinalFundusDataset(train_df, transform=train_transform, is_naive_ablation=is_naive)
    val_dataset = RetinalFundusDataset(val_df, transform=eval_transform, is_naive_ablation=False)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)
    
    model = RetinalMultiLabelClassifier(num_classes=NUM_CLASSES, dropout=0.3).to(device)
    loss_fn = MaskedBCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    
    best_val_macro_f1 = -1.0
    best_thresholds = np.full(NUM_CLASSES, 0.5)
    best_model_path = f"{exp_name}_best.pth"
    history = []
    
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        n_batches = 0
        t0 = time.time()
        
        for images, targets, masks, _ in train_loader:
            images = images.to(device)
            targets = targets.to(device)
            masks = masks.to(device)
            
            optimizer.zero_grad()
            logits = model(images)
            loss = loss_fn(logits, targets, masks)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            n_batches += 1
            
        scheduler.step()
        train_loss /= max(1, n_batches)
        elapsed = time.time() - t0
        
        # Validation evaluation & threshold tuning
        val_summary, _, val_t, _, _, _ = evaluate_model(model, val_loader, device, thresholds=None)
        
        print(f"Epoch {epoch:02d}/{epochs:02d} [{elapsed:.1f}s] | Train Loss: {train_loss:.4f} | "
              f"Val Macro-F1: {val_summary['Macro_F1']:.4f} | Val Micro-F1: {val_summary['Micro_F1']:.4f} | "
              f"Val AUROC: {val_summary['Mean_AUROC']:.4f}", flush=True)
              
        history.append({
            'epoch': epoch,
            'train_loss': train_loss,
            'val_macro_f1': val_summary['Macro_F1'],
            'val_micro_f1': val_summary['Micro_F1'],
            'val_auroc': val_summary['Mean_AUROC']
        })
        
        if val_summary['Macro_F1'] > best_val_macro_f1:
            best_val_macro_f1 = val_summary['Macro_F1']
            best_thresholds = val_t
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'thresholds': val_t.tolist(),
                'val_macro_f1': val_summary['Macro_F1'],
                'history': history
            }, best_model_path)
            
    print(f"Best Val Macro-F1 for {exp_name}: {best_val_macro_f1:.4f}", flush=True)
    return best_model_path, best_thresholds, history
""")

    # Cell 10: Run E1, E2, E3
    add_code("""# Prepare datasets for E1, E2, E3
df_rf_train = df_meta[(df_meta['source'] == 'RFMiD') & (df_meta['split'] == 'train')].copy()
df_rf_val = df_meta[(df_meta['source'] == 'RFMiD') & (df_meta['split'] == 'val')].copy()
df_rf_test = df_meta[(df_meta['source'] == 'RFMiD') & (df_meta['split'] == 'test')].copy()
df_odir_supp = df_meta[df_meta['split'] == 'train_odir_supplement'].copy()

# E1: RFMiD-only baseline
e1_path, e1_thresh, e1_hist = train_experiment(
    exp_name="E1_RFMiD_Baseline",
    train_df=df_rf_train,
    val_df=df_rf_val,
    epochs=10,
    batch_size=32,
    lr=3e-4,
    is_naive=False
)

# E2: RFMiD + Harmonized ODIR with Masked BCE Loss
df_e2_train = pd.concat([df_rf_train, df_odir_supp], ignore_index=True)
e2_path, e2_thresh, e2_hist = train_experiment(
    exp_name="E2_RFMiD_ODIR_Harmonized",
    train_df=df_e2_train,
    val_df=df_rf_val,
    epochs=10,
    batch_size=32,
    lr=3e-4,
    is_naive=False
)

# E3: Ablation (RFMiD + Naive ODIR without masking, blind patient labels)
e3_path, e3_thresh, e3_hist = train_experiment(
    exp_name="E3_Ablation_Naive_ODIR",
    train_df=df_e2_train,
    val_df=df_rf_val,
    epochs=10,
    batch_size=32,
    lr=3e-4,
    is_naive=True
)
""")

    # Cell 11: Final Evaluation on Untouched RFMiD Test Set
    add_code("""print("\\n" + "="*80)
print("FINAL BENCHMARK EVALUATION ON UNTOUCHED RFMiD TEST SET (N=640)")
print("="*80)

test_dataset = RetinalFundusDataset(df_rf_test, transform=eval_transform)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=2)

results_summary = {}
per_class_dfs = {}

for exp_name, ckpt_path in [
    ("E1: RFMiD-only Baseline", e1_path),
    ("E2: RFMiD + ODIR Harmonized", e2_path),
    ("E3: Ablation Naive ODIR", e3_path)
]:
    ckpt = torch.load(ckpt_path, map_location=device)
    model = RetinalMultiLabelClassifier(num_classes=NUM_CLASSES, dropout=0.3).to(device)
    model.load_state_dict(ckpt['model_state_dict'])
    thresh = np.array(ckpt['thresholds'])
    
    summary, class_df, _, probs, targets, masks = evaluate_model(model, test_loader, device, thresholds=thresh)
    results_summary[exp_name] = summary
    per_class_dfs[exp_name] = class_df
    class_df.to_csv(f"{exp_name.split(':')[0].strip()}_test_per_class.csv", index=False)
    
df_comparison = pd.DataFrame(results_summary).T
print("\\nOverall Test Benchmark Comparison:")
print(df_comparison[['Macro_F1', 'Micro_F1', 'Macro_Precision', 'Macro_Recall', 'Mean_AUROC', 'Mean_AP']].to_string())
df_comparison.to_csv("experiment_benchmark_comparison.csv")

with open("benchmark_summary.json", "w") as f:
    json.dump(results_summary, f, indent=4)
""")

    # Cell 12: Detailed Per-Class Comparison and Differences
    add_code("""# Compute Delta (E2 - E1) per class
df_e1_cls = per_class_dfs["E1: RFMiD-only Baseline"].set_index('Class')
df_e2_cls = per_class_dfs["E2: RFMiD + ODIR Harmonized"].set_index('Class')
df_e3_cls = per_class_dfs["E3: Ablation Naive ODIR"].set_index('Class')

delta_df = pd.DataFrame({
    'E1_F1': df_e1_cls['F1'],
    'E2_F1': df_e2_cls['F1'],
    'E3_F1': df_e3_cls['F1'],
    'Delta_E2_minus_E1': (df_e2_cls['F1'] - df_e1_cls['F1']).round(4),
    'E1_AUROC': df_e1_cls['AUROC'],
    'E2_AUROC': df_e2_cls['AUROC'],
    'E3_AUROC': df_e3_cls['AUROC'],
    'Delta_AUROC': (df_e2_cls['AUROC'] - df_e1_cls['AUROC']).round(4)
})

print("\\n" + "="*80)
print("PER-CLASS PERFORMANCE COMPARISON & DELTA (E2 vs E1 vs E3):")
print("="*80)
print(delta_df.to_string())
delta_df.to_csv("per_class_delta_comparison.csv")
""")

    # Cell 13: Sensitivity Analysis & Plotting
    add_code("""# Save summary visualization
plt.figure(figsize=(10, 6))
bar_width = 0.25
classes_idx = np.arange(len(UNIFIED_CLASSES))

plt.bar(classes_idx - bar_width, df_e1_cls['F1'], width=bar_width, label='E1: RFMiD Only', color='#4A90E2')
plt.bar(classes_idx, df_e2_cls['F1'], width=bar_width, label='E2: Harmonized (Ours)', color='#50E3C2')
plt.bar(classes_idx + bar_width, df_e3_cls['F1'], width=bar_width, label='E3: Naive Ablation', color='#E94E77')

plt.xlabel('Retinal Disease Class', fontsize=12, fontweight='bold')
plt.ylabel('Test F1-Score', fontsize=12, fontweight='bold')
plt.title('Multi-Label Classification Performance Across Experimental Setups (Test Set N=640)', fontsize=14, fontweight='bold')
plt.xticks(classes_idx, UNIFIED_CLASSES, rotation=30)
plt.ylim(0, 1.0)
plt.legend(fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("f1_comparison_chart.png", dpi=300)
plt.show()
print("Saved performance comparison chart to f1_comparison_chart.png")
""")

    os.makedirs('model_c/kaggle_kernel', exist_ok=True)
    nb_path = 'model_c/kaggle_kernel/model_c_experiments.ipynb'
    with open(nb_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Created Kaggle notebook at {nb_path} with {len(nb['cells'])} cells.")

if __name__ == '__main__':
    create_notebook()
