import os
import sys
import argparse
import time
import json
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from torchvision import transforms

# Ensure model_c is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from model_c.models.model import RetinalMultiLabelClassifier
from model_c.losses.masked_loss import MaskedBCEWithLogitsLoss
from model_c.evaluation.metrics import compute_multi_label_metrics, optimize_thresholds_on_val

CLASS_NAMES = ['DR', 'ARMD', 'MYA', 'DN', 'ERM', 'BRVO', 'LS', 'ODC_GLAUCOMA', 'CRVO', 'RISK']

def main():
    parser = argparse.ArgumentParser(description="Model C Training & Evaluation Pipeline")
    parser.add_argument("--exp", type=str, default="E1", choices=["E1", "E2", "E3"], help="Experiment configuration")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--metadata_path", type=str, default="model_c/data/unified_retinal_multilabel_metadata.csv")
    parser.add_argument("--output_dir", type=str, default="model_c/experiments/output")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running Experiment {args.exp} on device: {device}")
    
    if not os.path.exists(args.metadata_path):
        print(f"Metadata file not found: {args.metadata_path}")
        return

    df_meta = pd.read_csv(args.metadata_path)
    df_rf_train = df_meta[(df_meta['source_dataset'] == 'RFMiD') & (df_meta['split'] == 'train')]
    df_rf_val = df_meta[(df_meta['source_dataset'] == 'RFMiD') & (df_meta['split'] == 'val')]
    df_rf_test = df_meta[(df_meta['source_dataset'] == 'RFMiD') & (df_meta['split'] == 'test')]
    df_odir_supp = df_meta[df_meta['split'] == 'train_odir_supplement']

    print(f"Loaded splits: RFMiD Train={len(df_rf_train)}, Val={len(df_rf_val)}, Test={len(df_rf_test)}, ODIR Supp={len(df_odir_supp)}")
    print(f"Experiment setup {args.exp} initialized successfully!")

if __name__ == "__main__":
    main()
