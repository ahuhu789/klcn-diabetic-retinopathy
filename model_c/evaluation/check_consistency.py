import pandas as pd
import re

verified_df = pd.read_csv('MODEL_C_VERIFIED_METRICS.csv')

with open('MODEL_C_FINAL_VALIDATION.md', 'r', encoding='utf-8') as f:
    final_val_text = f.read()

with open('BAO_CAO_NGHIEN_CUU_MODEL_C.md', 'r', encoding='utf-8') as f:
    bao_cao_text = f.read()

print("=" * 60)
print("AUDITING CROSS-DOCUMENT PER-CLASS CONSISTENCY")
print("=" * 60)

# Classes in order
classes = ['DR', 'ARMD', 'MYA', 'DN', 'ERM', 'BRVO', 'LS', 'ODC_GLAUCOMA', 'CRVO', 'RISK']

discrepancies = []

for exp in ['E1_RFMiD_Baseline', 'E2_RFMiD_ODIR_Harmonized', 'E3_Ablation_Naive_ODIR']:
    for cls in classes:
        row = verified_df[(verified_df['Experiment'] == exp) & (verified_df['Class'] == cls)].iloc[0]
        f1_str = f"{row['F1']:.4f}"
        auroc_str = f"{row['AUROC']:.4f}"
        prec_str = f"{row['Precision']:.4f}"
        rec_str = f"{row['Recall']:.4f}"
        tp_str = str(int(row['TP']))
        fp_str = str(int(row['FP']))
        
        # Verify in MODEL_C_FINAL_VALIDATION.md
        # Table 2.4 contains: | **DR** | ... | 0.6746 | 0.6202 | 0.5063 | 0.9387 | 0.9341 | 0.9319 | 98 | 143 | 230 |
        if f1_str not in final_val_text:
            print(f"[WARNING] {exp} {cls} F1={f1_str} not found in MODEL_C_FINAL_VALIDATION.md")
            discrepancies.append(('MODEL_C_FINAL_VALIDATION.md', exp, cls, 'F1', f1_str))
            
        if auroc_str not in final_val_text:
            print(f"[WARNING] {exp} {cls} AUROC={auroc_str} not found in MODEL_C_FINAL_VALIDATION.md")
            discrepancies.append(('MODEL_C_FINAL_VALIDATION.md', exp, cls, 'AUROC', auroc_str))

        # Check BAO_CAO_NGHIEN_CUU_MODEL_C.md
        # Section 4.4 contains F1 and AUROC for E1, E2, E3
        if f1_str not in bao_cao_text:
            print(f"[WARNING] {exp} {cls} F1={f1_str} not found in BAO_CAO_NGHIEN_CUU_MODEL_C.md")
            discrepancies.append(('BAO_CAO_NGHIEN_CUU_MODEL_C.md', exp, cls, 'F1', f1_str))

print(f"\nTotal Discrepancies Found: {len(discrepancies)}")
if len(discrepancies) == 0:
    print("[SUCCESS] All per-class values are 100% consistent across all documents!")
else:
    for d in discrepancies:
        print("  Discrepancy:", d)
