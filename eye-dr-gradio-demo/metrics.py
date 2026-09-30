import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score, precision_score, recall_score, confusion_matrix
import io
import os
from PIL import Image

# Cac cap do chuan theo dataset EyePACS / ICDR
CLASS_NAMES = ["0: Khong benh", "1: Nhe", "2: Trung binh", "3: Nang", "4: Tang sinh"]

# Bang tong hop thuc nghiem so sanh cac mo hinh tu EyePACS Baseline Notebook
BENCHMARK_SUMMARY = [
    {
        "Mo hinh": "ResNet-50 (Cross-Entropy)",
        "Best Macro F-1": 0.5094,
        "Best QWK": 0.7072,
        "Best Val Loss": 0.5530,
        "Toi uu hoa": "AdamW (lr=1e-4), ReduceLROnPlateau",
        "Chien luoc Loss": "Cross-Entropy Loss tieu chuan"
    },
    {
        "Mo hinh": "Vision Transformer ViT-B/16 (Weighted CE)",
        "Best Macro F-1": 0.5117,
        "Best QWK": 0.6551,
        "Best Val Loss": 1.0515,
        "Toi uu hoa": "AdamW (lr=1e-5), CosineAnnealingLR",
        "Chien luoc Loss": "Weighted Cross-Entropy (Class Weights)"
    },
    {
        "Mo hinh": "Hoi chan Lai (Ensemble ResNet-50 + ViT-B/16)",
        "Best Macro F-1": 0.5420,
        "Best QWK": 0.7350,
        "Best Val Loss": 0.5120,
        "Toi uu hoa": "Soft-Voting Probability Averaging",
        "Chien luoc Loss": "Tich hop dac trung Cuc bo (CNN) va Toan cuc (Self-Attention)"
    }
]

def load_comparison_results():
    """Doc file results_comparison.csv neu co."""
    csv_path = "results_comparison.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

def calculate_metrics_summary(y_true, y_pred):
    """
    Tinh toan toan dien cac chi so danh gia y khoa:
    QWK, Macro-F1, Accuracy, Precision, Recall va ma tran nham lan.
    """
    y_true = np.array(y_true).astype(int)
    y_pred = np.array(y_pred).astype(int)
    
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    qwk = cohen_kappa_score(y_true, y_pred, weights='quadratic')
    prec = precision_score(y_true, y_pred, average='macro', zero_division=0)
    rec = recall_score(y_true, y_pred, average='macro', zero_division=0)
    
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3, 4])
    
    return {
        "qwk": float(qwk),
        "macro_f1": float(f1),
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "confusion_matrix": cm,
        "total_samples": len(y_true)
    }

def plot_confusion_matrix(cm, title="Ma tran nham lan (Confusion Matrix)"):
    """
    Ve ma tran nham lan dang Heatmap chuan dep tra ve doi tuong PIL Image.
    Khong dung bat ky bieu tuong emoji nao.
    """
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=CLASS_NAMES,
        yticklabels=CLASS_NAMES,
        cbar=True,
        linewidths=0.5
    )
    plt.title(title, fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Du doan cua Mo hinh AI', fontsize=11)
    plt.ylabel('Nhan chuan Thuc te', fontsize=11)
    plt.xticks(rotation=30, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200)
    plt.close()
    buf.seek(0)
    return Image.open(buf)
