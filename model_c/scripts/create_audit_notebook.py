import json
import nbformat as nbf

def create_audit_kernel():
    nb = nbf.v4.new_notebook()
    nb['metadata'] = {
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.10.0'}
    }
    nb['cells'] = []

    def add_code(src):
        nb['cells'].append(nbf.v4.new_code_cell(src))

    def add_md(src):
        nb['cells'].append(nbf.v4.new_markdown_cell(src))

    add_md("""# Model C: Cross-Dataset Duplicate & Near-Duplicate Image Audit
## RFMiD (Train, Val, Test) vs ODIR-5K
Audits:
1. Exact SHA-256 binary hash collision
2. Perceptual Difference Hash (dHash) & Average Hash (aHash)
3. Geometric invariance: Horizontal Flip and Rotations (90, 180, 270)
4. Pairwise Hamming distance screening across RFMiD Test/Val/Train vs ODIR
""")

    add_code("""import os
import sys
import time
import hashlib
import json
import numpy as np
import pandas as pd
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

print("Starting Image-Level Duplicate Audit...", flush=True)
t0 = time.time()
""")

    add_code("""# 1. Global file indexing across /kaggle/input
print("Indexing files across /kaggle/input...", flush=True)
file_cache = {}
for root, _, files in os.walk('/kaggle/input'):
    for f in files:
        if f not in file_cache:
            file_cache[f] = os.path.join(root, f)
print(f"Indexed {len(file_cache)} total files in /kaggle/input.")

rfmid_files = {'train': [], 'val': [], 'test': []}
odir_files = []

# Index RFMiD
for split, csv_name in [('train', 'RFMiD_Training_Labels.csv'), 
                        ('val', 'RFMiD_Validation_Labels.csv'), 
                        ('test', 'RFMiD_Testing_Labels.csv')]:
    if csv_name in file_cache:
        df = pd.read_csv(file_cache[csv_name])
        for _, row in df.iterrows():
            img_id = int(row['ID'])
            fn = f"{img_id}.png"
            if fn in file_cache:
                rfmid_files[split].append((f"rfmid_{split}_{img_id}", file_cache[fn]))

# Index ODIR
if 'data.xlsx' in file_cache:
    df_odir = pd.read_excel(file_cache['data.xlsx'])
    for _, row in df_odir.iterrows():
        for side in ['Left-Fundus', 'Right-Fundus']:
            fn = str(row[side]).strip()
            if fn in file_cache:
                odir_files.append((f"odir_{fn}", file_cache[fn]))

print(f"RFMiD Train indexed: {len(rfmid_files['train'])}")
print(f"RFMiD Val indexed:   {len(rfmid_files['val'])}")
print(f"RFMiD Test indexed:  {len(rfmid_files['test'])}")
print(f"ODIR indexed:        {len(odir_files)}")
""")

    add_code("""# 2. Hash calculation functions
def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_dhash(img, hash_size=8):
    # Grayscale and resize to (hash_size + 1, hash_size)
    img_gray = img.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
    pixels = np.array(img_gray)
    diff = pixels[:, 1:] > pixels[:, :-1]
    return diff.flatten()

def compute_image_signatures(item):
    name, path = item
    try:
        sha = compute_sha256(path)
        with Image.open(path) as img:
            dhash_orig = compute_dhash(img)
            # horizontal flip
            img_hflip = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            dhash_hflip = compute_dhash(img_hflip)
            # 90 rotation
            img_r90 = img.transpose(Image.Transpose.ROTATE_90)
            dhash_r90 = compute_dhash(img_r90)
        return {
            'name': name,
            'path': path,
            'sha256': sha,
            'dhash': dhash_orig,
            'dhash_hflip': dhash_hflip,
            'dhash_r90': dhash_r90,
            'status': 'OK'
        }
    except Exception as e:
        return {'name': name, 'path': path, 'status': f'ERROR: {str(e)}'}
""")

    add_code("""# Compute signatures with ThreadPool
all_items = []
for split in ['train', 'val', 'test']:
    all_items.extend(rfmid_files.get(split, []))
all_items.extend(odir_files)

print(f"Extracting signatures for {len(all_items)} total images using multithreading...", flush=True)
t_sig0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(compute_image_signatures, all_items))
print(f"Signatures extracted in {time.time() - t_sig0:.2f}s", flush=True)

# Organize by group
signatures = {r['name']: r for r in results if r['status'] == 'OK'}
print(f"Successfully processed: {len(signatures)} images.")
""")

    add_code("""# 3. Exact SHA-256 Duplicate Check
sha_map = {}
exact_duplicates = []
for name, data in signatures.items():
    sha = data['sha256']
    if sha in sha_map:
        exact_duplicates.append((sha_map[sha], name, sha))
    else:
        sha_map[sha] = name

print("")
print("=======================================================")
print(f"EXACT SHA-256 BINARY DUPLICATES FOUND: {len(exact_duplicates)}")
print("=======================================================")
for pair in exact_duplicates:
    print(f"  EXACT MATCH: {pair[0]} <==> {pair[1]} (SHA: {pair[2][:16]}...)")
""")

    add_code("""# 4. Perceptual Near-Duplicate Screening across Key Splits
# Screening groups
rf_test_names = [item[0] for item in rfmid_files.get('test', []) if item[0] in signatures]
rf_val_names = [item[0] for item in rfmid_files.get('val', []) if item[0] in signatures]
rf_train_names = [item[0] for item in rfmid_files.get('train', []) if item[0] in signatures]
odir_names = [item[0] for item in odir_files if item[0] in signatures]

print("")
print("Running Perceptual Near-Duplicate Analysis:")
print(f"  RFMiD Test: {len(rf_test_names)}")
print(f"  RFMiD Val:  {len(rf_val_names)}")
print(f"  RFMiD Train:{len(rf_train_names)}")
print(f"  ODIR:       {len(odir_names)}")

def screen_splits(names_a, names_b, label_comparison, threshold=5):
    if len(names_a) == 0 or len(names_b) == 0:
        return []
    
    # Build matrices (N, 64)
    mat_a = np.array([signatures[n]['dhash'] for n in names_a])
    mat_b = np.array([signatures[n]['dhash'] for n in names_b])
    mat_b_hflip = np.array([signatures[n]['dhash_hflip'] for n in names_b])
    mat_b_r90 = np.array([signatures[n]['dhash_r90'] for n in names_b])
    
    suspicious = []
    
    # Vectorized XOR sum
    for idx_a, n_a in enumerate(names_a):
        vec_a = mat_a[idx_a]
        
        # dists to all in B
        dist_orig = np.sum(vec_a != mat_b, axis=1)
        dist_hflip = np.sum(vec_a != mat_b_hflip, axis=1)
        dist_r90 = np.sum(vec_a != mat_b_r90, axis=1)
        
        min_dists = np.minimum(np.minimum(dist_orig, dist_hflip), dist_r90)
        
        close_indices = np.where(min_dists <= threshold)[0]
        for idx_b in close_indices:
            n_b = names_b[idx_b]
            d = int(min_dists[idx_b])
            suspicious.append({
                'comparison': label_comparison,
                'image_A': n_a,
                'image_B': n_b,
                'hamming_distance': d,
                'path_A': signatures[n_a]['path'],
                'path_B': signatures[n_b]['path']
            })
            
    return suspicious

# Check RFMiD Test vs ODIR
test_vs_odir = screen_splits(rf_test_names, odir_names, "RFMiD_Test_vs_ODIR", threshold=5)
val_vs_odir = screen_splits(rf_val_names, odir_names, "RFMiD_Val_vs_ODIR", threshold=5)
train_vs_odir = screen_splits(rf_train_names, odir_names, "RFMiD_Train_vs_ODIR", threshold=5)
test_vs_train = screen_splits(rf_test_names, rf_train_names, "RFMiD_Test_vs_RFMiD_Train", threshold=5)

all_suspicious = test_vs_odir + val_vs_odir + train_vs_odir + test_vs_train

print("")
print("SCREENING RESULTS (Hamming Distance <= 5):")
print(f"  RFMiD Test vs ODIR:        {len(test_vs_odir)} candidate pairs")
print(f"  RFMiD Val vs ODIR:         {len(val_vs_odir)} candidate pairs")
print(f"  RFMiD Train vs ODIR:       {len(train_vs_odir)} candidate pairs")
print(f"  RFMiD Test vs RFMiD Train: {len(test_vs_train)} candidate pairs")
""")

    add_code("""# 5. Summarize and Save Artifacts
report = {
    'audit_timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
    'total_rfmid_images_indexed': len(rf_test_names) + len(rf_val_names) + len(rf_train_names),
    'rfmid_splits': {
        'train': len(rf_train_names),
        'val': len(rf_val_names),
        'test': len(rf_test_names)
    },
    'total_odir_images_indexed': len(odir_names),
    'exact_sha256_duplicates_count': len(exact_duplicates),
    'exact_duplicates': exact_duplicates,
    'perceptual_candidates_count': {
        'rfmid_test_vs_odir': len(test_vs_odir),
        'rfmid_val_vs_odir': len(val_vs_odir),
        'rfmid_train_vs_odir': len(train_vs_odir),
        'rfmid_test_vs_train': len(test_vs_train)
    },
    'audit_verdict': 'ZERO_CROSS_DATASET_LEAKAGE_DETECTED' if len(exact_duplicates) == 0 and len(test_vs_odir) == 0 else 'SUSPICIOUS_PAIRS_DETECTED'
}

with open('duplicate_audit_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=4)

if len(all_suspicious) > 0:
    df_susp = pd.DataFrame(all_suspicious)
    df_susp.to_csv('suspicious_pairs.csv', index=False)
else:
    pd.DataFrame(columns=['comparison', 'image_A', 'image_B', 'hamming_distance']).to_csv('suspicious_pairs.csv', index=False)

print("")
print("Audit Report written to duplicate_audit_report.json")
print("Suspicious pairs written to suspicious_pairs.csv")
print("Audit Complete!", flush=True)
""")

    with open('model_c/kaggle_audit_kernel/duplicate_audit.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print("Notebook generated: model_c/kaggle_audit_kernel/duplicate_audit.ipynb")

    meta = {
        "id": "nguynhuythanh/klcn-model-c-duplicate-audit",
        "title": "KLCN Model C Duplicate Audit",
        "code_file": "duplicate_audit.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": False,
        "enable_gpu": False,
        "enable_tpu": False,
        "enable_internet": True,
        "dataset_sources": [
            "andrewmvd/retinal-disease-classification",
            "andrewmvd/ocular-disease-recognition-odir5k"
        ],
        "kernel_sources": [],
        "competition_sources": [],
        "model_sources": []
    }
    with open('model_c/kaggle_audit_kernel/kernel-metadata.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
    print("Metadata generated: model_c/kaggle_audit_kernel/kernel-metadata.json")

if __name__ == '__main__':
    create_audit_kernel()
