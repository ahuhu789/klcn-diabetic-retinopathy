import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_fscore_support, confusion_matrix

def optimize_thresholds_on_val(y_true, y_probs, y_mask=None, class_names=None, num_steps=81):
    """
    Finds optimal decision thresholds [0.1, 0.9] that maximize F1 on the validation set.
    Never uses test set for threshold selection.
    """
    N, C = y_probs.shape
    if y_mask is None:
        y_mask = np.ones_like(y_true)
        
    best_thresholds = np.full(C, 0.5)
    best_val_f1s = np.zeros(C)
    threshold_grid = np.linspace(0.1, 0.9, num_steps)
    
    for c in range(C):
        mask_c = y_mask[:, c] == 1
        if mask_c.sum() == 0 or (y_true[mask_c, c] == 1).sum() == 0:
            best_thresholds[c] = 0.5
            continue
            
        y_c = y_true[mask_c, c]
        probs_c = y_probs[mask_c, c]
        
        best_f1 = -1.0
        best_t = 0.5
        for t in threshold_grid:
            preds_c = (probs_c >= t).astype(int)
            p, r, f1, _ = precision_recall_fscore_support(y_c, preds_c, average='binary', zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_t = t
                
        best_thresholds[c] = best_t
        best_val_f1s[c] = best_f1
        
    return best_thresholds, best_val_f1s

def compute_multi_label_metrics(y_true, y_probs, thresholds, y_mask=None, class_names=None):
    """
    Computes Macro-F1, Micro-F1, Per-class Precision, Recall, F1, AUROC, AP, and Confusion Matrix.
    """
    N, C = y_probs.shape
    if y_mask is None:
        y_mask = np.ones_like(y_true)
    if class_names is None:
        class_names = [f"Class_{i}" for i in range(C)]
        
    y_preds = (y_probs >= thresholds).astype(int)
    
    class_results = []
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_tn = 0
    
    f1_list = []
    precision_list = []
    recall_list = []
    auroc_list = []
    ap_list = []
    
    for c in range(C):
        mask_c = y_mask[:, c] == 1
        y_c = y_true[mask_c, c].astype(int)
        probs_c = y_probs[mask_c, c]
        preds_c = y_preds[mask_c, c]
        
        n_pos = int((y_c == 1).sum())
        n_neg = int((y_c == 0).sum())
        
        if len(y_c) == 0:
            continue
            
        # Confusion matrix
        tn, fp, fn, tp = 0, 0, 0, 0
        if len(np.unique(y_c)) > 1:
            cm = confusion_matrix(y_c, preds_c, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()
        else:
            if y_c[0] == 1:
                tp = int((preds_c == 1).sum())
                fn = int((preds_c == 0).sum())
            else:
                tn = int((preds_c == 0).sum())
                fp = int((preds_c == 1).sum())
                
        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_tn += tn
        
        # Precision, Recall, F1
        p, r, f1, _ = precision_recall_fscore_support(y_c, preds_c, average='binary', zero_division=0)
        
        # AUROC & AP
        try:
            auroc = roc_auc_score(y_c, probs_c) if (n_pos > 0 and n_neg > 0) else np.nan
        except:
            auroc = np.nan
            
        try:
            ap = average_precision_score(y_c, probs_c) if n_pos > 0 else np.nan
        except:
            ap = np.nan
            
        f1_list.append(f1)
        precision_list.append(p)
        recall_list.append(r)
        if not np.isnan(auroc):
            auroc_list.append(auroc)
        if not np.isnan(ap):
            ap_list.append(ap)
            
        class_results.append({
            'Class': class_names[c],
            'Threshold': round(float(thresholds[c]), 4),
            'Support_Pos': n_pos,
            'Support_Neg': n_neg,
            'TP': tp,
            'FP': fp,
            'FN': fn,
            'TN': tn,
            'Precision': round(float(p), 4),
            'Recall': round(float(r), 4),
            'F1': round(float(f1), 4),
            'AUROC': round(float(auroc), 4) if not np.isnan(auroc) else "N/A",
            'AP': round(float(ap), 4) if not np.isnan(ap) else "N/A"
        })
        
    df_classes = pd.DataFrame(class_results)
    
    # Macro metrics
    macro_f1 = np.mean(f1_list) if len(f1_list) > 0 else 0.0
    macro_precision = np.mean(precision_list) if len(precision_list) > 0 else 0.0
    macro_recall = np.mean(recall_list) if len(recall_list) > 0 else 0.0
    mean_auroc = np.mean(auroc_list) if len(auroc_list) > 0 else np.nan
    mean_ap = np.mean(ap_list) if len(ap_list) > 0 else np.nan
    
    # Micro metrics
    micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0
    
    summary = {
        'Macro_F1': round(float(macro_f1), 4),
        'Micro_F1': round(float(micro_f1), 4),
        'Macro_Precision': round(float(macro_precision), 4),
        'Macro_Recall': round(float(macro_recall), 4),
        'Mean_AUROC': round(float(mean_auroc), 4) if not np.isnan(mean_auroc) else "N/A",
        'Mean_AP': round(float(mean_ap), 4) if not np.isnan(mean_ap) else "N/A",
        'Total_Evaluated_Annotations': int(total_tp + total_fp + total_fn + total_tn)
    }
    
    return summary, df_classes

def run_threshold_sensitivity(y_true, y_probs, y_mask=None, class_names=None):
    """Evaluates metrics across uniform thresholds 0.1 to 0.9 to analyze sensitivity."""
    C = y_probs.shape[1]
    if class_names is None:
        class_names = [f"Class_{i}" for i in range(C)]
        
    thresholds_to_test = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    sensitivity_records = []
    
    for t in thresholds_to_test:
        fixed_t = np.full(C, t)
        summary, _ = compute_multi_label_metrics(y_true, y_probs, fixed_t, y_mask, class_names)
        sensitivity_records.append({
            'Threshold': t,
            'Macro_F1': summary['Macro_F1'],
            'Micro_F1': summary['Micro_F1'],
            'Macro_Precision': summary['Macro_Precision'],
            'Macro_Recall': summary['Macro_Recall']
        })
        
    return pd.DataFrame(sensitivity_records)
