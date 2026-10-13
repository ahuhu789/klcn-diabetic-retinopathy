# DATASET AUDIT REPORT: RFMiD & ODIR-5K FOR MULTI-LABEL RETINAL DISEASE CLASSIFICATION

**Project**: Model C – Multi-Source Single-Image Retinal Disease Classification  
**Researcher**: AI Research Engineer (Medical Computer Vision & Dataset Harmonization)  
**Date**: October 2026  
**Status**: Completed & Verified  

---

## 1. Executive Summary

This audit assesses the viability of integrating **RFMiD** (Retinal Fundus Multi-disease Image Dataset) and **ODIR-5K** (Ocular Disease Intelligent Recognition) to train **Model C**, an EfficientNet-B0-based single-image multi-label retinal disease classifier. Model C complements the existing pipeline:
- **Model A**: Input validation gate (MobileNetV3 fundus vs non-fundus screening).
- **Model B**: Five-grade diabetic retinopathy staging (ResNet-50 + ViT-B/16 hybrid ordinal).
- **Model C**: Multi-label retinal disease classification across common posterior pole pathologies.

### Core Audit Findings
1. **RFMiD** provides high-quality, image-level, specialist-verified multi-label annotations across 45 disease categories and a binary `Disease_Risk` flag. Its official partitions (1,920 train, 640 validation, 640 test) provide an untouched benchmark.
2. **ODIR-5K** was collected at the **patient level** (paired left and right fundus images) with 8 broad diagnostic classes ($N, D, G, C, A, H, M, O$). **Crucially, 44.7% of patients exhibit asymmetric bilateral diagnoses, and 23.4% of patients have one completely normal eye paired with an abnormal eye.**
3. **Severe Annotation Leakage Risk**: Blindly copying patient-level labels (e.g., Patient Diabetes $D=1$) to both eyes introduces **452 false positive DR annotations** in the training set alone, corrupting single-image training.
4. **Feasibility of Eye-Level Harmonization**: By mining doctor-annotated **eye-specific diagnostic keywords** (`Left-Diagnostic Keywords`, `Right-Diagnostic Keywords`), we can extract verified positive labels for key pathologies (Diabetic Retinopathy, AMD, Pathological Myopia, Drusen, Epiretinal Membrane, BRVO, Laser Scars) and verified negatives from confirmed `normal fundus` images.
5. **Missing Label Policy**: Pathologies unmentioned in abnormal eyes cannot be assumed negative ($0$). They must be encoded as missing/unverified ($-1$) and ignored via a binary `label_mask` using **Masked BCEWithLogitsLoss**.

---

## 2. Dataset Provenance & Usage Conditions

| Attribute | RFMiD (Primary Dataset) | ODIR-5K (Supplementary Dataset) |
| :--- | :--- | :--- |
| **Full Name** | Retinal Fundus Multi-disease Image Dataset | Ocular Disease Intelligent Recognition (5,000 patients) |
| **Original Publication** | Pachade et al., *Scientific Data* (Nature), 2021 | Li et al., Peking University International Competition, 2019 / 2021 |
| **Origin / Geography** | Multiple eye clinics across India | Multi-center hospital consortium, China (Shangping, etc.) |
| **Fundus Camera Systems** | 1. TOPCON 3D OCT-2000<br>2. Kowa VX-10alpha<br>3. Canon CR-2 PLUS | Canon, Zeiss, Kowa fundus camera models |
| **Original Resolutions** | $4288 \times 2848$, $2048 \times 1536$, $2144 \times 1424$ | Diverse ($512 \times 512$ up to $2500 \times 2000$) |
| **Public License** | CC BY 4.0 (Attribution) | Academic Research Use Only (ODIR Challenge) |
| **Primary Structure** | Single fundus image per entry | Paired stereoscopic/bilateral images per patient |
| **Dataset Size** | 3,200 images total | 3,500 training patients (7,000 images), 1,000 test patients |
| **Official Partitions** | Train: 1,920 (60%) \| Val: 640 (20%) \| Test: 640 (20%) | Official Train: 3,500 patients \| Off-site test: 1,000 patients |

---

## 3. Annotation Granularity & Verification

### 3.1 RFMiD (Image-Level Ground Truth)
- Every image was reviewed by two independent ophthalmological experts, with disagreements arbitrated by a senior retinal specialist.
- **Labels provided**:
  - `ID`: Image identifier (1 to 3,200).
  - `Disease_Risk`: Binary indicator ($0$ = normal/healthy retina, $1$ = disease detected).
  - 45 binary pathology columns: $0$ = absent, $1$ = present.
- **Verification of Consistency**:
  - All 669 normal images across Train/Val/Test have strictly `0` across all 45 disease columns.
  - All 2,531 abnormal images have `Disease_Risk == 1` and at least one positive disease column.
  - No missing cells or NaN values exist in the official CSV files.

### 3.2 ODIR-5K (Patient-Level vs Eye-Level Breakdown)
The official tabular file (`data.xlsx`) provides:
- Patient demographics: `ID`, `Patient Age`, `Patient Sex`.
- Image references: `Left-Fundus`, `Right-Fundus`.
- Clinician entries: `Left-Diagnostic Keywords`, `Right-Diagnostic Keywords`.
- Patient-level binary categories:
  - $N$: Normal
  - $D$: Diabetes
  - $G$: Glaucoma
  - $C$: Cataract
  - $A$: Age-related Macular Degeneration (AMD)
  - $H$: Hypertension
  - $M$: Pathological Myopia
  - $O$: Other diseases / abnormalities

### 3.3 Quantitative Audit of Bilateral Asymmetry in ODIR-5K

| Metric | Sample Count | Percentage | Clinical Significance |
| :--- | :--- | :--- | :--- |
| **Total Patient Records** | 3,500 | 100.0% | Complete official training cohort |
| **Total Fundus Images** | 7,000 | 100.0% | 3,500 Left eyes + 3,500 Right eyes |
| **Discordant Left vs Right Keywords** | **1,564** | **44.7%** | Nearly half of patients have different eye conditions |
| **One Eye Normal, One Eye Abnormal** | **820** | **23.4%** | Direct risk of false positives if patient label propagated |
| **Left Normal, Right Abnormal** | 441 | 12.6% | E.g., Left eye normal, Right eye proliferative DR |
| **Right Normal, Left Abnormal** | 379 | 10.8% | E.g., Right eye normal, Left eye mature cataract |

#### Empirical Cross-Tabulation: Patient Diabetes ($p\_D$) vs Eye-Level Diabetic Retinopathy ($eye\_DR$)
Evaluating the 7,000 eyes in ODIR:
- **Patient $D=0$ (Non-diabetic)**:
  - Confirmed $eye\_DR = 0$: 4,710 eyes (100.0% specificity).
  - Uncertain / suspected: 34 eyes.
  - Confirmed $eye\_DR = 1$: 0 eyes.
- **Patient $D=1$ (Diabetic)**:
  - Confirmed $eye\_DR = 1$ (Mild, Mod, Severe NPDR, PDR): **1,785 eyes**.
  - **No visible DR lesions ($eye\_DR = 0$)**: **452 eyes**!
  - Uncertain / suspected DR: 19 eyes.

> [!CAUTION]
> If a naive preprocessing script assigns $DR = 1$ to all images of diabetic patients, **452 non-DR images (6.5% of the dataset)** receive a false positive ground truth label. This severely hurts model precision and calibration.

---

## 4. Class Distribution & Imbalance Analysis

### 4.1 RFMiD Prevalence & Long-Tail Distribution

| Rank | Code | Pathology Full Name | Train Pos (N=1920) | Val Pos (N=640) | Test Pos (N=640) | Total Pos (N=3200) | Train Prev (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **DR** | Diabetic Retinopathy | 376 | 132 | 124 | 632 | 19.58% |
| **2** | **MH** | Media Haze | 317 | 102 | 104 | 523 | 16.51% |
| **3** | **ODC** | Optic Disc Cupping | 282 | 72 | 91 | 445 | 14.69% |
| **4** | **TSLN**| Tessellated Fundus | 186 | 65 | 53 | 304 | 9.69% |
| **5** | **DN** | Drusen | 138 | 46 | 46 | 230 | 7.19% |
| **6** | **ARMD**| Age-related Macular Degeneration | 100 | 38 | 31 | 169 | 5.21% |
| **7** | **MYA** | Myopia | 101 | 34 | 32 | 167 | 5.26% |
| **8** | **BRVO**| Branch Retinal Vein Occlusion | 73 | 23 | 23 | 119 | 3.80% |
| **9** | **ODP** | Optic Disc Pallor | 65 | 26 | 24 | 115 | 3.39% |
| **10**| **ODE** | Optic Disc Edema | 58 | 21 | 17 | 96 | 3.02% |
| **11**| **LS**  | Laser Scars | 47 | 17 | 15 | 79 | 2.45% |
| **12**| **RS**  | Retinitis Pigmentosa | 43 | 14 | 14 | 71 | 2.24% |
| **13**| **CSR** | Central Serous Chorioretinopathy | 37 | 11 | 13 | 61 | 1.93% |
| **14**| **CRS** | Chorioretinal Scars | 32 | 11 | 11 | 54 | 1.67% |
| **15**| **CRVO**| Central Retinal Vein Occlusion | 28 | 8 | 9 | 45 | 1.46% |
| ...  | ...  | *(30 rare classes)* | < 25 each | < 8 each | < 8 each | < 35 each | < 1.0% |

### 4.2 ODIR Eye-Level Keyword Sample Yield

Mined from 7,000 eye keywords:
- `normal fundus`: 2,816 eyes (verified negative for all retinal lesions).
- `diabetic retinopathy` (NPDR + PDR): 1,785 eyes (verified DR positive).
- `epiretinal membrane`: 402 eyes (verified ERM positive).
- `age-related macular degeneration` (dry + wet): 280 eyes (verified AMD positive).
- `glaucoma` / glaucomatous changes: 282 eyes (verified glaucoma positive).
- `pathological myopia`: 268 eyes (verified MYA positive).
- `drusen`: 179 eyes (verified DN positive).
- `laser spots / photocoagulation`: 125 eyes (verified LS positive).
- `branch retinal vein occlusion`: 32 eyes (verified BRVO positive).
- `central retinal vein occlusion`: 13 eyes (verified CRVO positive).

---

## 5. Image Quality & Artifact Screening

### ODIR Artifacts Identified
- `lens dust`: 408 eyes (dust spots on optical lens; non-pathological artifact).
- `refractive media opacity`: 63 eyes (severe cataract or vitreous haze preventing clear retinal view).
- `low image quality`: 21 eyes (out of focus, under-exposed).
- `anterior segment image`: 2 eyes (camera focused on cornea/iris instead of retina).
- `no fundus image`: 1 eye (blank/corrupt capture).

**Action**: Images flagged with `no fundus image`, `anterior segment image`, or ungradable quality are excluded from supervised training to prevent spurious gradient signals.

---

## 6. Official Partition Integrity & Anti-Leakage Protocol

1. **RFMiD Test Set (Untouched Guarantee)**:
   - RFMiD Testing set ($N=640$) is reserved exclusively for final model benchmarking.
   - It is never exposed during training, validation, or threshold tuning.
2. **Patient Grouping**:
   - In ODIR, both left and right eye images belonging to patient `ID` are assigned to `patient_group_id = odir_<ID>`.
   - When splitting ODIR into training and auxiliary validation, Group-K-Fold partitioning is strictly enforced so bilateral images of the same patient never cross splits.
3. **RFMiD Validation Set**:
   - Official RFMiD Validation set ($N=640$) is used for hyperparameter tuning and optimal threshold search.
