"""
Model C - Independent Raw Prediction Metric Recalculator & Audit Tool
Evaluates raw test predictions (640 RFMiD test images) across E1, E2, E3.
Computes TP, FP, FN, TN, Precision, Recall, F1, AUROC, AP per class and macro/micro metrics.
Compares computed metrics against MODEL_C_VERIFIED_METRICS.csv to verify 100% reproducibility.
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix

sys.stdout.reconfigure(encoding='utf-8')

CLASSES = ['DR', 'ARMD', 'MYA', 'DN', 'ERM', 'BRVO', 'LS', 'ODC_GLAUCOMA', 'CRVO', 'RISK']

EXP_FILES = {
    'E1_RFMiD_Baseline': 'model_c/experiments_output/raw_predictions/raw_test_predictions_E1.csv',
    'E2_RFMiD_ODIR_Harmonized': 'model_c/experiments_output/raw_predictions/raw_test_predictions_E2.csv',
    'E3_Ablation_Naive_ODIR': 'model_c/experiments_output/raw_predictions/raw_test_predictions_E3.csv'
}

def verify_predictions(verified_csv_path='MODEL_C_VERIFIED_METRICS.csv'):
    if not os.path.exists(verified_csv_path):
        raise FileNotFoundError(f"Verified metrics file not found: {verified_csv_path}")
        
    verified_df = pd.read_csv(verified_csv_path)
    all_match = True
    discrepancies = []
    
    summary_results = {}

    for exp_name, file_path in EXP_FILES.items():
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Raw prediction file not found: {file_path}")
            
        raw_df = pd.read_csv(file_path)
        print(f"\n==================================================")
        print(f"VERIFYING EXPERIMENT: {exp_name} ({len(raw_df)} images)")
        print(f"==================================================")
        
        if len(raw_df) != 640:
            print(f"[ERROR] Row count mismatch: {len(raw_df)} != 640")
            all_match = False
            
        all_gt = []
        all_pred = []
        all_prob = []
        class_f1s = []
        class_precs = []
        class_recs = []
        class_aurocs = []
        class_aps = []
        total_fp = 0
        total_tp = 0
        total_fn = 0
        total_tn = 0
        
        for cls in CLASSES:
            gt = raw_df[f'gt_{cls}'].values
            prob = raw_df[f'prob_{cls}'].values
            thresh = float(raw_df[f'thresh_{cls}'].values[0])
            pred = raw_df[f'pred_{cls}'].values
            
            # Check threshold consistency
            pred_expected = (prob >= thresh).astype(int)
            assert np.array_equal(pred, pred_expected), f"Prediction column inconsistent with prob >= thresh for {cls}"
            
            tn, fp, fn, tp = confusion_matrix(gt, pred, labels=[0, 1]).ravel()
            pos_supp = int(np.sum(gt == 1))
            neg_supp = int(np.sum(gt == 0))
            
            total_fp += fp
            total_tp += tp
            total_fn += fn
            total_tn += tn
            
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
            
            auroc = roc_auc_score(gt, prob)
            ap = average_precision_score(gt, prob)
            
            class_f1s.append(f1)
            class_precs.append(prec)
            class_recs.append(rec)
            class_aurocs.append(auroc)
            class_aps.append(ap)
            
            all_gt.append(gt)
            all_pred.append(pred)
            
            # Verify against verified_df
            v_match = verified_df[(verified_df['Experiment'] == exp_name) & (verified_df['Class'] == cls)]
            if len(v_match) == 0:
                print(f"[ERROR] Class {cls} not found in verified CSV for {exp_name}")
                all_match = False
                continue
            v_row = v_match.iloc[0]
            
            checks = [
                ('Threshold', thresh, v_row['Threshold']),
                ('Pos_Support', pos_supp, v_row['Pos_Support']),
                ('Neg_Support', neg_supp, v_row['Neg_Support']),
                ('TP', tp, v_row['TP']),
                ('FP', fp, v_row['FP']),
                ('FN', fn, v_row['FN']),
                ('TN', tn, v_row['TN']),
                ('Precision', round(prec, 4), round(v_row['Precision'], 4)),
                ('Recall', round(rec, 4), round(v_row['Recall'], 4)),
                ('F1', round(f1, 4), round(v_row['F1'], 4)),
                ('AUROC', round(auroc, 4), round(v_row['AUROC'], 4)),
                ('AP', round(ap, 4), round(v_row['AP'], 4)),
            ]
            
            for name, calc, exp in checks:
                if abs(calc - exp) > 0.0001:
                    print(f"  [DISCREPANCY] {cls} {name}: calculated={calc}, manifest={exp}")
                    discrepancies.append((exp_name, cls, name, calc, exp))
                    all_match = False
                    
            print(f"  {cls:14s} | F1: {f1:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | AUROC: {auroc:.4f} | TP: {tp:3d} | FP: {fp:3d}")

        macro_f1 = np.mean(class_f1s)
        macro_prec = np.mean(class_precs)
        macro_rec = np.mean(class_recs)
        mean_auroc = np.mean(class_aurocs)
        mean_ap = np.mean(class_aps)
        
        # Standard Multi-Label Micro-F1: 2*TP / (2*TP + FP + FN)
        micro_prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        micro_rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        micro_f1 = 2 * total_tp / (2 * total_tp + total_fp + total_fn) if (2 * total_tp + total_fp + total_fn) > 0 else 0.0
        
        summary_results[exp_name] = {
            'Macro-F1': macro_f1,
            'Micro-F1': micro_f1,
            'Macro-Prec': macro_prec,
            'Macro-Rec': macro_rec,
            'Mean AUROC': mean_auroc,
            'Mean AP': mean_ap,
            'Total_FP': total_fp,
            'Total_TP': total_tp,
            'Total_FN': total_fn,
            'Total_TN': total_tn,
        }
        
        print(f"\n--- {exp_name} Summary ---")
        print(f"  Macro-F1:     {macro_f1:.4f}")
        print(f"  Micro-F1:     {micro_f1:.4f}")
        print(f"  Macro-Prec:   {macro_prec:.4f}")
        print(f"  Macro-Rec:    {macro_rec:.4f}")
        print(f"  Mean AUROC:   {mean_auroc:.4f}")
        print(f"  Mean AP:      {mean_ap:.4f}")
        print(f"  Total FP decisions across 640 images: {total_fp}")
        
    print("\n==================================================")
    print(f"FINAL AUDIT VERIFICATION RESULT")
    print(f"==================================================")
    print(f"Total Discrepancies Found: {len(discrepancies)}")
    if all_match:
        print("[SUCCESS] All class metrics, counts, AUROC, AP, and thresholds match 100% exactly.")
        print("Status: SCIENTIFICALLY REPRODUCIBLE (VERIFIED)")
    else:
        print("[FAILURE] Discrepancies detected.")
        print("Status: NOT VERIFIED")
        
    return all_match, summary_results

if __name__ == '__main__':
    verify_predictions()
