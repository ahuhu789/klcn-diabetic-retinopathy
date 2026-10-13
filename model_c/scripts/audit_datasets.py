import os
import sys
import re
import pandas as pd
import numpy as np
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

def audit_rfmid():
    print("=" * 60)
    print("AUDITING RFMiD DATASET")
    print("=" * 60)
    
    train_path = "model_c/metadata/rfmid/RFMiD_Training_Labels.csv"
    val_path = "model_c/metadata/rfmid/RFMiD_Validation_Labels.csv"
    test_path = "model_c/metadata/rfmid/RFMiD_Testing_Labels.csv"
    
    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)
    
    print(f"Train samples: {len(df_train)}")
    print(f"Val samples:   {len(df_val)}")
    print(f"Test samples:  {len(df_test)}")
    print(f"Total samples: {len(df_train) + len(df_val) + len(df_test)}")
    
    # Columns
    cols = df_train.columns.tolist()
    disease_cols = cols[2:]  # excluding ID, Disease_Risk
    print(f"Total columns: {len(cols)}")
    print(f"ID and Risk columns: {cols[:2]}")
    print(f"Disease classes ({len(disease_cols)}): {disease_cols}")
    
    # Check for missing values in RFMiD
    print("\nMissing values in train:", df_train.isnull().sum().sum())
    print("Missing values in val:  ", df_val.isnull().sum().sum())
    print("Missing values in test: ", df_test.isnull().sum().sum())
    
    # Check disease risk vs diseases
    for split_name, df in [("Train", df_train), ("Val", df_val), ("Test", df_test)]:
        disease_sum = df[disease_cols].sum(axis=1)
        risk_1 = df[df["Disease_Risk"] == 1]
        risk_0 = df[df["Disease_Risk"] == 0]
        # Any normal (Disease_Risk==0) that has diseases?
        risk_0_with_disease = (risk_0[disease_cols].sum(axis=1) > 0).sum()
        # Any disease_risk==1 with no disease specified?
        risk_1_no_disease = (risk_1[disease_cols].sum(axis=1) == 0).sum()
        print(f"\n{split_name} split:")
        print(f"  Disease_Risk == 0 (Normal): {len(risk_0)} (with positive diseases: {risk_0_with_disease})")
        print(f"  Disease_Risk == 1 (Disease): {len(risk_1)} (with no specified disease column: {risk_1_no_disease})")
        print(f"  Mean diseases per image: {disease_sum.mean():.2f} (max: {disease_sum.max()}, min: {disease_sum.min()})")
        
    # Class frequencies across train, val, test
    freq_df = pd.DataFrame({
        "Train_Pos": df_train[disease_cols].sum(),
        "Val_Pos": df_val[disease_cols].sum(),
        "Test_Pos": df_test[disease_cols].sum(),
        "Total_Pos": df_train[disease_cols].sum() + df_val[disease_cols].sum() + df_test[disease_cols].sum()
    })
    freq_df["Train_Prevalence_%"] = (freq_df["Train_Pos"] / len(df_train) * 100).round(2)
    freq_df = freq_df.sort_values(by="Total_Pos", ascending=False)
    print("\nTop 15 diseases by frequency in RFMiD:")
    print(freq_df.head(15))
    print("\nBottom 10 diseases by frequency in RFMiD:")
    print(freq_df.tail(10))
    
    return df_train, df_val, df_test, freq_df


def audit_odir():
    print("\n" + "=" * 60)
    print("AUDITING ODIR-5K DATASET")
    print("=" * 60)
    
    xl_path = "model_c/metadata/odir/data.xlsx"
    df_xl = pd.read_excel(xl_path)
    
    print(f"Total patient records in data.xlsx: {len(df_xl)}")
    print(f"Columns: {df_xl.columns.tolist()}")
    
    patient_label_cols = ["N", "D", "G", "C", "A", "H", "M", "O"]
    print("\nPatient-level label distribution in data.xlsx:")
    print(df_xl[patient_label_cols].sum())
    
    # Check discrepancy between Left and Right diagnostic keywords
    print("\nSample patient-level vs eye-level keyword comparison (First 8 patients):")
    for i in range(8):
        row = df_xl.iloc[i]
        p_labels = [col for col in patient_label_cols if row[col] == 1]
        print(f"ID {row['ID']} (Age {row['Patient Age']}, {row['Patient Sex']}):")
        print(f"  Patient Labels: {p_labels}")
        print(f"  Left Eye  ({row['Left-Fundus']}):  Keyword = '{row['Left-Diagnostic Keywords']}'")
        print(f"  Right Eye ({row['Right-Fundus']}): Keyword = '{row['Right-Diagnostic Keywords']}'")
    
    # Let's inspect asymmetry: How often do Left and Right keywords differ?
    different_keywords = (df_xl["Left-Diagnostic Keywords"] != df_xl["Right-Diagnostic Keywords"]).sum()
    print(f"\nAsymmetry: {different_keywords} / {len(df_xl)} patients ({different_keywords/len(df_xl)*100:.1f}%) have DIFFERENT Left vs Right keywords!")
    
    # How often is one eye 'normal' while the patient has a disease label?
    left_normal = df_xl["Left-Diagnostic Keywords"].str.contains("normal fundus", case=False, na=False)
    right_normal = df_xl["Right-Diagnostic Keywords"].str.contains("normal fundus", case=False, na=False)
    
    left_norm_right_abnorm = (left_normal & ~right_normal).sum()
    right_norm_left_abnorm = (~left_normal & right_normal).sum()
    print(f"Patients with Left normal but Right abnormal: {left_norm_right_abnorm}")
    print(f"Patients with Right normal but Left abnormal: {right_norm_left_abnorm}")
    print(f"Total discordant normal/abnormal eyes: {left_norm_right_abnorm + right_norm_left_abnorm} ({ (left_norm_right_abnorm + right_norm_left_abnorm)/len(df_xl)*100:.1f}%)")
    
    # Let's inspect full_df.csv
    full_path = "model_c/metadata/odir/full_df.csv"
    if os.path.exists(full_path):
        df_full = pd.read_csv(full_path)
        print(f"\nfull_df.csv samples: {len(df_full)}")
        print(f"full_df columns: {df_full.columns.tolist()}")
        print(df_full[["ID", "filename", "Left-Diagnostic Keywords", "Right-Diagnostic Keywords", "labels", "target"]].head(5))
        
        # Check how full_df constructed labels: Did it just copy patient labels to single images?
        print("\nChecking if full_df copied patient labels blindly:")
        sample_diff = df_full[df_full["Left-Diagnostic Keywords"] != df_full["Right-Diagnostic Keywords"]].head(5)
        for _, r in sample_diff.iterrows():
            print(f"Image {r['filename']} (Patient {r['ID']}): Left='{r['Left-Diagnostic Keywords']}' | Right='{r['Right-Diagnostic Keywords']}' | Assigned Labels={r['labels']}")
            
    # Collect all unique diagnostic keywords in ODIR
    all_keywords = []
    for kws in df_xl["Left-Diagnostic Keywords"].dropna().tolist() + df_xl["Right-Diagnostic Keywords"].dropna().tolist():
        # keywords can be separated by commas, semicolons, or Chinese commas
        tokens = [t.strip() for t in re.split(r'[,，;；]', str(kws)) if t.strip()]
        all_keywords.extend(tokens)
    
    keyword_counts = Counter(all_keywords)
    print(f"\nTotal unique diagnostic keywords in ODIR: {len(keyword_counts)}")
    print("Top 30 most common diagnostic keywords in ODIR:")
    for kw, cnt in keyword_counts.most_common(30):
        print(f"  {kw:<45}: {cnt}")
        
    return df_xl, keyword_counts

if __name__ == "__main__":
    audit_rfmid()
    audit_odir()
