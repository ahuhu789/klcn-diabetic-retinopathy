import os
import sys
import re
import json
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

UNIFIED_CLASSES = [
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

def build_rfmid_records():
    records = []
    
    splits = [
        ('train', 'model_c/metadata/rfmid/RFMiD_Training_Labels.csv', 'Training_Set/Training_Set/Training'),
        ('val', 'model_c/metadata/rfmid/RFMiD_Validation_Labels.csv', 'Evaluation_Set/Evaluation_Set/Validation'),
        ('test', 'model_c/metadata/rfmid/RFMiD_Testing_Labels.csv', 'Test_Set/Test_Set/Test')
    ]
    
    for split_name, csv_path, img_dir in splits:
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            img_id = int(row['ID'])
            record = {
                'image_id': f"rfmid_{img_id}",
                'filename': f"{img_id}.png",
                'image_path': f"{img_dir}/{img_id}.png",
                'source_dataset': 'RFMiD',
                'original_patient_id': f"rfmid_{img_id}",
                'patient_group_id': f"rfmid_{img_id}",
                'eye_side': 'unknown',
                'raw_diagnostics': 'RFMiD_multi_label_annotations',
                'annotation_source': 'RFMiD_specialist_verified',
                'split': split_name
            }
            
            # Target mapping
            record['DR'] = int(row['DR'])
            record['ARMD'] = int(row['ARMD'])
            record['MYA'] = int(row['MYA'])
            record['DN'] = int(row['DN'])
            record['ERM'] = int(row['ERM'])
            record['BRVO'] = int(row['BRVO'])
            record['LS'] = int(row['LS'])
            record['ODC_GLAUCOMA'] = int(row['ODC'])
            record['CRVO'] = int(row['CRVO'])
            record['RISK'] = int(row['Disease_Risk'])
            
            # Mask (RFMiD is fully verified positive or negative across all annotated classes)
            for c in UNIFIED_CLASSES:
                record[f'mask_{c}'] = 1
                
            records.append(record)
            
    return records

def parse_odir_eye(kw_str, p_row, eye_side, filename):
    kw = str(kw_str).strip()
    kw_l = kw.lower()
    
    # Check severe quality defect
    severe_defects = ['no fundus image', 'anterior segment image', 'image offset', 'optic disk photographically invisible']
    if any(d in kw_l for d in severe_defects):
        return None  # Drop unusable image
        
    targets = {c: -1 for c in UNIFIED_CLASSES}
    masks = {f'mask_{c}': 0 for c in UNIFIED_CLASSES}
    
    is_normal = (kw_l == 'normal fundus')
    
    if is_normal:
        # Verified healthy retina: all conditions verified absent (0)
        for c in UNIFIED_CLASSES:
            targets[c] = 0
            masks[f'mask_{c}'] = 1
        targets['RISK'] = 0
        masks['mask_RISK'] = 1
    else:
        # Abnormal retina
        targets['RISK'] = 1
        masks['mask_RISK'] = 1
        
        # 1. DR
        dr_kws = ['mild nonproliferative retinopathy', 'moderate non proliferative retinopathy', 
                  'severe nonproliferative retinopathy', 'proliferative diabetic retinopathy', 
                  'severe proliferative diabetic retinopathy', 'diabetic retinopathy']
        if any(d in kw_l for d in dr_kws):
            targets['DR'] = 1
            masks['mask_DR'] = 1
        elif 'suspected diabetic retinopathy' in kw_l or 'suspicious diabetic retinopathy' in kw_l:
            targets['DR'] = -1
            masks['mask_DR'] = 0
            
        # 2. ARMD
        amd_kws = ['dry age-related macular degeneration', 'wet age-related macular degeneration', 'age-related macular degeneration']
        if any(a in kw_l for a in amd_kws):
            targets['ARMD'] = 1
            masks['mask_ARMD'] = 1
            
        # 3. MYA
        mya_kws = ['pathological myopia', 'myopia retinopathy', 'myopic retinopathy', 'myopic maculopathy']
        if any(m in kw_l for m in mya_kws):
            targets['MYA'] = 1
            masks['mask_MYA'] = 1
            
        # 4. DN
        if 'drusen' in kw_l:
            targets['DN'] = 1
            masks['mask_DN'] = 1
            
        # 5. ERM
        if 'epiretinal membrane' in kw_l or 'macular epiretinal membrane' in kw_l:
            targets['ERM'] = 1
            masks['mask_ERM'] = 1
            
        # 6. BRVO
        if 'branch retinal vein occlusion' in kw_l:
            targets['BRVO'] = 1
            masks['mask_BRVO'] = 1
            
        # 7. LS
        ls_kws = ['laser spot', 'post retinal laser surgery', 'post laser photocoagulation', 'fundus laser photocoagulation spots']
        if any(l in kw_l for l in ls_kws):
            targets['LS'] = 1
            masks['mask_LS'] = 1
            
        # 8. ODC_GLAUCOMA
        if 'glaucoma' in kw_l and 'suspected' not in kw_l:
            targets['ODC_GLAUCOMA'] = 1
            masks['mask_ODC_GLAUCOMA'] = 1
        elif 'suspected glaucoma' in kw_l:
            targets['ODC_GLAUCOMA'] = -1
            masks['mask_ODC_GLAUCOMA'] = 0
            
        # 9. CRVO
        if 'central retinal vein occlusion' in kw_l:
            targets['CRVO'] = 1
            masks['mask_CRVO'] = 1

    p_id = int(p_row['ID'])
    record = {
        'image_id': f"odir_{filename.replace('.jpg', '')}",
        'filename': filename,
        'image_path': f"ODIR-5K/ODIR-5K/Training Images/{filename}",
        'source_dataset': 'ODIR',
        'original_patient_id': f"odir_{p_id}",
        'patient_group_id': f"odir_patient_{p_id}",
        'eye_side': eye_side,
        'raw_diagnostics': kw,
        'annotation_source': 'ODIR_eye_keyword_harmonized',
        'split': 'train_odir_supplement'
    }
    record.update(targets)
    record.update(masks)
    return record

def build_odir_records():
    xl_path = 'model_c/metadata/odir/data.xlsx'
    df = pd.read_excel(xl_path)
    records = []
    dropped_count = 0
    
    for _, row in df.iterrows():
        # Left eye
        rec_left = parse_odir_eye(row['Left-Diagnostic Keywords'], row, 'left', row['Left-Fundus'])
        if rec_left is not None:
            records.append(rec_left)
        else:
            dropped_count += 1
            
        # Right eye
        rec_right = parse_odir_eye(row['Right-Diagnostic Keywords'], row, 'right', row['Right-Fundus'])
        if rec_right is not None:
            records.append(rec_right)
        else:
            dropped_count += 1
            
    print(f"ODIR parsed {len(records)} valid eyes (dropped {dropped_count} due to severe defect/non-fundus).")
    return records

def generate_unified_dataset():
    os.makedirs('model_c/data', exist_ok=True)
    rf_records = build_rfmid_records()
    od_records = build_odir_records()
    
    all_records = rf_records + od_records
    df_unified = pd.DataFrame(all_records)
    
    out_csv = 'model_c/data/unified_retinal_multilabel_metadata.csv'
    df_unified.to_csv(out_csv, index=False)
    print(f"Saved unified metadata to {out_csv} (Total records: {len(df_unified)})")
    
    # Generate Comprehensive Summary Report
    print("\n" + "=" * 70)
    print("UNIFIED DATASET AUDIT & CLASS DISTRIBUTION REPORT")
    print("=" * 70)
    
    split_summary = df_unified.groupby(['source_dataset', 'split']).size()
    print("\nSplit breakdown:")
    print(split_summary)
    
    print("\nClass Statistics across Splits:")
    summary_rows = []
    
    for c in UNIFIED_CLASSES:
        for split_name in ['train', 'val', 'test', 'train_odir_supplement']:
            sub = df_unified[df_unified['split'] == split_name]
            pos = (sub[c] == 1).sum()
            neg = (sub[c] == 0).sum()
            unv = (sub[c] == -1).sum()
            msk = (sub[f'mask_{c}'] == 1).sum()
            summary_rows.append({
                'Class': c,
                'Split': split_name,
                'Total_Samples': len(sub),
                'Verified_Pos (1)': pos,
                'Verified_Neg (0)': neg,
                'Unverified (-1)': unv,
                'Masked_In_Loss (mask=1)': msk,
                'Pos_Prevalence_%': round(pos / len(sub) * 100, 2) if len(sub) > 0 else 0
            })
            
    df_sum = pd.DataFrame(summary_rows)
    df_sum_pivot = df_sum.pivot(index='Class', columns='Split', values=['Verified_Pos (1)', 'Verified_Neg (0)', 'Unverified (-1)'])
    
    # Save statistics report
    df_sum.to_csv('model_c/data/class_statistics_report.csv', index=False)
    print("\nClass Statistics Saved to model_c/data/class_statistics_report.csv")
    
    # Print concise table for primary training comparison: RFMiD train vs Supplementary ODIR
    print("\nComparison: RFMiD Train (N=1920) vs ODIR Supplement (N=6970):")
    comp_df = pd.DataFrame({
        'RFMiD_Train_Pos': [((df_unified['split'] == 'train') & (df_unified[c] == 1)).sum() for c in UNIFIED_CLASSES],
        'RFMiD_Train_Neg': [((df_unified['split'] == 'train') & (df_unified[c] == 0)).sum() for c in UNIFIED_CLASSES],
        'ODIR_Supp_Pos': [((df_unified['split'] == 'train_odir_supplement') & (df_unified[c] == 1)).sum() for c in UNIFIED_CLASSES],
        'ODIR_Supp_Neg': [((df_unified['split'] == 'train_odir_supplement') & (df_unified[c] == 0)).sum() for c in UNIFIED_CLASSES],
        'ODIR_Supp_Unv': [((df_unified['split'] == 'train_odir_supplement') & (df_unified[c] == -1)).sum() for c in UNIFIED_CLASSES]
    }, index=UNIFIED_CLASSES)
    print(comp_df.to_string())
    
    return df_unified

if __name__ == '__main__':
    generate_unified_dataset()
