import os
import sys
import re
import json
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

# RFMiD disease code mapping to full medical names and categories
RFMID_CLASS_MAP = {
    'DR': 'Diabetic Retinopathy',
    'ARMD': 'Age-related Macular Degeneration',
    'MH': 'Media Haze',
    'DN': 'Drusen',
    'MYA': 'Myopia',
    'BRVO': 'Branch Retinal Vein Occlusion',
    'TSLN': 'Tessellated Fundus',
    'ERM': 'Epiretinal Membrane',
    'LS': 'Laser Scars',
    'MS': 'Macular Scars',
    'CSR': 'Central Serous Chorioretinopathy',
    'ODC': 'Optic Disc Cupping',
    'CRVO': 'Central Retinal Vein Occlusion',
    'TV': 'Tortuous Vessels',
    'AH': 'Asteroid Hyalosis',
    'ODP': 'Optic Disc Pallor',
    'ODE': 'Optic Disc Edema',
    'ST': 'Shunt Vessels',
    'AION': 'Anterior Ischemic Optic Neuropathy',
    'PT': 'Parafoveal Telangiectasia',
    'RT': 'Retinal Traction',
    'RS': 'Retinitis Pigmentosa',
    'CRS': 'Chorioretinal Scars',
    'EDN': 'Early Drusen',
    'RPEC': 'Retinal Pigment Epithelium Changes',
    'MHL': 'Macular Hole',
    'RP': 'Retinal Pigmentation',
    'CWS': 'Cotton Wool Spots',
    'CB': 'Coloboma',
    'ODPM': 'Optic Disc Pit Maculopathy',
    'PRH': 'Preretinal Hemorrhage',
    'MNF': 'Myelinated Nerve Fibers',
    'HR': 'Hemorrhagic Retinopathy',
    'CRAO': 'Central Retinal Artery Occlusion',
    'TD': 'Tilted Disc',
    'CME': 'Cystoid Macular Edema',
    'PTCR': 'Post-trabeculectomy Chorioretinal Rupture',
    'CF': 'Choroidal Folds',
    'VH': 'Vitreous Hemorrhage',
    'MCA': 'Macroaneurysm',
    'VS': 'Vasculitis',
    'BRAO': 'Branch Retinal Artery Occlusion',
    'PLQ': 'Plaque',
    'HPED': 'Hemorrhagic Pigment Epithelial Detachment',
    'CL': 'Collateral Vessels'
}

def analyze_rfmid():
    df_train = pd.read_csv('model_c/metadata/rfmid/RFMiD_Training_Labels.csv')
    df_val = pd.read_csv('model_c/metadata/rfmid/RFMiD_Validation_Labels.csv')
    df_test = pd.read_csv('model_c/metadata/rfmid/RFMiD_Testing_Labels.csv')
    
    classes = list(RFMID_CLASS_MAP.keys())
    
    stats = []
    for c in classes:
        t_pos = int(df_train[c].sum())
        v_pos = int(df_val[c].sum())
        te_pos = int(df_test[c].sum())
        total = t_pos + v_pos + te_pos
        stats.append({
            'code': c,
            'name': RFMID_CLASS_MAP[c],
            'train_pos': t_pos,
            'val_pos': v_pos,
            'test_pos': te_pos,
            'total_pos': total,
            'train_prev_pct': round(t_pos / len(df_train) * 100, 2),
            'val_prev_pct': round(v_pos / len(df_val) * 100, 2),
            'test_prev_pct': round(te_pos / len(df_test) * 100, 2)
        })
        
    stats_df = pd.DataFrame(stats).sort_values(by='total_pos', ascending=False)
    
    # Co-occurrence in Train
    corr = df_train[classes].corr()
    top_cooccur = []
    for i in range(len(classes)):
        for j in range(i+1, len(classes)):
            c1, c2 = classes[i], classes[j]
            both = ((df_train[c1] == 1) & (df_train[c2] == 1)).sum()
            if both >= 10:
                top_cooccur.append((c1, c2, both, round(corr.loc[c1, c2], 3)))
    top_cooccur.sort(key=lambda x: -x[2])
    
    return stats_df, top_cooccur, len(df_train), len(df_val), len(df_test)

def analyze_odir():
    xl_path = 'model_c/metadata/odir/data.xlsx'
    df = pd.read_excel(xl_path)
    
    # 3500 patients -> 7000 eyes
    eye_records = []
    for idx, row in df.iterrows():
        p_id = row['ID']
        age = row['Patient Age']
        sex = row['Patient Sex']
        
        # Left eye
        eye_records.append({
            'patient_id': p_id,
            'eye_side': 'left',
            'filename': row['Left-Fundus'],
            'keywords': str(row['Left-Diagnostic Keywords']).strip(),
            'p_N': row['N'], 'p_D': row['D'], 'p_G': row['G'], 'p_C': row['C'],
            'p_A': row['A'], 'p_H': row['H'], 'p_M': row['M'], 'p_O': row['O']
        })
        # Right eye
        eye_records.append({
            'patient_id': p_id,
            'eye_side': 'right',
            'filename': row['Right-Fundus'],
            'keywords': str(row['Right-Diagnostic Keywords']).strip(),
            'p_N': row['N'], 'p_D': row['D'], 'p_G': row['G'], 'p_C': row['C'],
            'p_A': row['A'], 'p_H': row['H'], 'p_M': row['M'], 'p_O': row['O']
        })
        
    df_eyes = pd.DataFrame(eye_records)
    
    # Keyword analysis for disease mapping
    # 1. DR (Diabetic Retinopathy)
    dr_patterns = [
        'mild nonproliferative retinopathy',
        'moderate non proliferative retinopathy',
        'severe nonproliferative retinopathy',
        'proliferative diabetic retinopathy',
        'severe proliferative diabetic retinopathy',
        'diabetic retinopathy'
    ]
    def has_dr(kw):
        kw_l = kw.lower()
        if 'suspected' in kw_l or 'suspicious' in kw_l:
            return 0.5  # uncertain
        return 1.0 if any(p in kw_l for p in dr_patterns) else 0.0
        
    # 2. ARMD / AMD
    amd_patterns = [
        'dry age-related macular degeneration',
        'wet age-related macular degeneration',
        'age-related macular degeneration'
    ]
    def has_amd(kw):
        kw_l = kw.lower()
        return 1.0 if any(p in kw_l for p in amd_patterns) else 0.0

    # 3. MYA (Myopia)
    mya_patterns = [
        'pathological myopia',
        'myopia retinopathy',
        'myopic retinopathy',
        'myopic maculopathy'
    ]
    def has_mya(kw):
        kw_l = kw.lower()
        return 1.0 if any(p in kw_l for p in mya_patterns) else 0.0

    # 4. DN (Drusen)
    def has_dn(kw):
        kw_l = kw.lower()
        return 1.0 if 'drusen' in kw_l else 0.0

    # 5. ERM (Epiretinal Membrane)
    def has_erm(kw):
        kw_l = kw.lower()
        if 'suspected' in kw_l:
            return 0.5
        return 1.0 if ('epiretinal membrane' in kw_l or 'macular epiretinal membrane' in kw_l) else 0.0

    # 6. BRVO
    def has_brvo(kw):
        kw_l = kw.lower()
        return 1.0 if 'branch retinal vein occlusion' in kw_l else 0.0

    # 7. CRVO
    def has_crvo(kw):
        kw_l = kw.lower()
        return 1.0 if 'central retinal vein occlusion' in kw_l else 0.0

    # 8. LS (Laser Scars)
    ls_patterns = ['laser spot', 'post retinal laser surgery', 'post laser photocoagulation', 'fundus laser photocoagulation spots']
    def has_ls(kw):
        kw_l = kw.lower()
        return 1.0 if any(p in kw_l for p in ls_patterns) else 0.0

    # 9. TSLN (Tessellated fundus)
    def has_tsln(kw):
        kw_l = kw.lower()
        return 1.0 if 'tessellated fundus' in kw_l else 0.0

    # 10. Glaucoma (Related to RFMiD ODC / Optic Disc Cupping)
    def has_glaucoma(kw):
        kw_l = kw.lower()
        if 'suspected' in kw_l:
            return 0.5
        return 1.0 if 'glaucoma' in kw_l else 0.0

    # 11. Normal fundus
    def is_normal(kw):
        kw_l = kw.lower()
        return kw_l == 'normal fundus'

    # Apply mappings
    df_eyes['eye_DR'] = df_eyes['keywords'].apply(has_dr)
    df_eyes['eye_AMD'] = df_eyes['keywords'].apply(has_amd)
    df_eyes['eye_MYA'] = df_eyes['keywords'].apply(has_mya)
    df_eyes['eye_DN'] = df_eyes['keywords'].apply(has_dn)
    df_eyes['eye_ERM'] = df_eyes['keywords'].apply(has_erm)
    df_eyes['eye_BRVO'] = df_eyes['keywords'].apply(has_brvo)
    df_eyes['eye_CRVO'] = df_eyes['keywords'].apply(has_crvo)
    df_eyes['eye_LS'] = df_eyes['keywords'].apply(has_ls)
    df_eyes['eye_TSLN'] = df_eyes['keywords'].apply(has_tsln)
    df_eyes['eye_GLAUCOMA'] = df_eyes['keywords'].apply(has_glaucoma)
    df_eyes['eye_NORMAL'] = df_eyes['keywords'].apply(is_normal)

    # Cross check Patient-level vs Eye-level for D vs DR:
    p_d_eye_dr = df_eyes.groupby('p_D')['eye_DR'].value_counts()
    
    # Quality flags: lens dust, low quality, etc.
    def is_low_quality(kw):
        kw_l = kw.lower()
        return any(q in kw_l for q in ['low image quality', 'no fundus image', 'anterior segment image', 'image offset', 'optic disk photographically invisible'])
    
    df_eyes['low_quality'] = df_eyes['keywords'].apply(is_low_quality)
    
    return df, df_eyes, p_d_eye_dr

if __name__ == '__main__':
    stats_df, top_cooccur, n_tr, n_va, n_te = analyze_rfmid()
    print("Top RFMiD Classes:")
    print(stats_df.head(15)[['code', 'name', 'total_pos', 'train_pos', 'train_prev_pct']].to_string(index=False))
    
    print("\nTop Co-occurring disease pairs in RFMiD Train:")
    for c1, c2, both, r in top_cooccur[:10]:
        print(f"  {c1} + {c2}: {both} images (Pearson r = {r})")
        
    df_xl, df_eyes, p_d_eye_dr = analyze_odir()
    print("\nODIR Cross-tabulation: Patient Diabetes (p_D) vs Eye-level DR (eye_DR):")
    print(p_d_eye_dr)
    
    print("\nODIR Eye-level Verified Counts:")
    for col in ['eye_DR', 'eye_AMD', 'eye_MYA', 'eye_DN', 'eye_ERM', 'eye_BRVO', 'eye_CRVO', 'eye_LS', 'eye_TSLN', 'eye_GLAUCOMA', 'eye_NORMAL']:
        pos = (df_eyes[col] == 1.0).sum()
        unc = (df_eyes[col] == 0.5).sum()
        print(f"  {col:<15}: Positive = {pos:>5}, Uncertain = {unc:>3}")
        
    print(f"\nODIR Low Quality / Non-Fundus Eyes: {df_eyes['low_quality'].sum()}")
