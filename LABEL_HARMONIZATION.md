# LABEL HARMONIZATION FRAMEWORK: RFMiD AND ODIR-5K

**Project**: Model C – Multi-Source Single-Image Retinal Disease Classification  
**Target Architecture**: Single-Image Multi-Label Classifier  
**Status**: Formal Medical Engineering Specification  

---

## 1. Principles of Label Harmonization

Combining clinical fundus datasets from distinct origins requires strict semantic alignment and uncertainty handling:

1. **Granularity Congruence**: Model C processes **one fundus image** as input. Supervised targets must describe pathology present in that specific eye image.
2. **Zero False Negative Hallucination**: An eye diagnosed with one disease (e.g., Cataract) cannot be assumed disease-free for other retinal conditions unless a comprehensive fundus examination confirmed a normal retina.
3. **Tri-State Label Encoding**:
   - $y_{i, c} = 1$: Pathology $c$ is **verified present**.
   - $y_{i, c} = 0$: Pathology $c$ is **verified absent** (confirmed healthy normal retina).
   - $y_{i, c} = -1$: Pathology $c$ is **unverified / missing** (clinician did not confirm presence or absence).
4. **Supervised Loss Masking**: The loss for pathology $c$ on image $i$ is weighted by a binary mask $m_{i, c} \in \{0, 1\}$, where $m_{i, c} = 1$ if $y_{i, c} \in \{0, 1\}$ and $m_{i, c} = 0$ if $y_{i, c} = -1$.

---

## 2. Harmonized Multi-Label Disease Schema

The unified disease taxonomy focuses on common, clinically critical retinal pathologies shared across RFMiD and verified eye keywords in ODIR-5K:

| Unified Label ID | Unified Code | Full Medical Name | ICD-10 Ref | Clinical Description |
| :---: | :--- | :--- | :--- | :--- |
| **0** | **DR** | Diabetic Retinopathy | E11.3 | Microvascular damage to the retina caused by diabetes mellitus (microaneurysms, hemorrhages, hard/soft exudates, neovascularization). |
| **1** | **ARMD** | Age-related Macular Degeneration | H35.31 | Degeneration of the macula presenting as dry (drusen, geographic atrophy) or wet (choroidal neovascularization, fluid). |
| **2** | **MYA** | Pathological Myopia | H44.2 | High myopia characterized by structural changes such as posterior staphyloma, lacquer cracks, chorioretinal atrophy, or Fuchs spots. |
| **3** | **DN** | Drusen | H35.32 | Discrete extracellular yellow-white deposits between retinal pigment epithelium and Bruch's membrane. |
| **4** | **ERM** | Epiretinal Membrane | H35.37 | Fibrocellular tissue proliferation over the internal limiting membrane, causing retinal wrinkling or distortion. |
| **5** | **BRVO** | Branch Retinal Vein Occlusion | H34.83 | Obstruction of a tributary retinal vein leading to intraretinal hemorrhages and edema confined to a venous tributary sector. |
| **6** | **LS** | Laser Scars / Photocoagulation | Z98.89 | Well-demarcated circular chorioretinal pigmented or atrophic scars resulting from prior laser therapy. |
| **7** | **ODC_GLAUCOMA** | Optic Disc Cupping / Glaucoma | H40.1 | Enlargement of optic cup-to-disc ratio ($CDR \ge 0.6$), neuroretinal rim thinning, or confirmed glaucomatous optic neuropathy. |
| **8** | **CRVO** | Central Retinal Vein Occlusion | H34.81 | Widespread retinal hemorrhages in all four quadrants ("blood and thunder" appearance) due to central vein obstruction. |
| **9** | **RISK** | Any Retinal Disease / Risk | R93.8 | Binary flag: $0$ for verified healthy fundus, $1$ for presence of any confirmed pathological lesion. |

---

## 3. Detailed Per-Class Mapping Specifications

### 3.1 Diabetic Retinopathy (`DR`)

- **Original RFMiD Label**: Column `DR` (Image-level binary: 0 or 1).
- **Original ODIR Data**:
  - Patient column `D` (Diabetes). **Rejected for direct assignment.**
  - Eye keywords: `mild nonproliferative retinopathy`, `moderate non proliferative retinopathy`, `severe nonproliferative retinopathy`, `proliferative diabetic retinopathy`, `diabetic retinopathy`.
- **Unified Label**: `DR`
- **Annotation Granularity**: Image-level.
- **Evidence Supporting Mapping**: Ophthalmologists explicitly characterized non-proliferative (NPDR) and proliferative (PDR) diabetic retinopathy in the eye keywords. Both match the International Clinical Diabetic Retinopathy Disease Severity Scale.
- **Filtering Rules**:
  - Keywords matching DR terms $\rightarrow y_{\text{DR}} = 1, m_{\text{DR}} = 1$.
  - Keyword `normal fundus` $\rightarrow y_{\text{DR}} = 0, m_{\text{DR}} = 1$.
  - Keyword contains `suspected diabetic retinopathy` $\rightarrow y_{\text{DR}} = -1, m_{\text{DR}} = 0$ (masked out).
  - Patient has $D=1$ but eye has non-DR pathology without DR noted $\rightarrow y_{\text{DR}} = -1, m_{\text{DR}} = 0$.
- **Confidence**: **High (95%)** when derived from keyword; **Low (50%)** if derived from patient column.
- **Limitations**: RFMiD lumps all DR grades into binary 1; ODIR keywords distinguish grades. Harmonized target is binary positive for any DR.

---

### 3.2 Age-related Macular Degeneration (`ARMD`)

- **Original RFMiD Label**: Column `ARMD`.
- **Original ODIR Data**:
  - Patient column `A` (AMD).
  - Eye keywords: `dry age-related macular degeneration`, `wet age-related macular degeneration`, `age-related macular degeneration`.
- **Unified Label**: `ARMD`
- **Annotation Granularity**: Image-level.
- **Evidence Supporting Mapping**: Clinical diagnosis of dry or wet AMD involves macular drusen, pigmentary abnormalities, or choroidal neovascularization, completely concordant between both datasets.
- **Filtering Rules**:
  - Keywords matching AMD terms $\rightarrow y_{\text{ARMD}} = 1, m_{\text{ARMD}} = 1$.
  - Keyword `normal fundus` $\rightarrow y_{\text{ARMD}} = 0, m_{\text{ARMD}} = 1$.
  - All other non-normal eyes without explicit AMD mention $\rightarrow y_{\text{ARMD}} = -1, m_{\text{ARMD}} = 0$.
- **Confidence**: **High (95%)**.
- **Limitations**: Both dry and wet subtypes are pooled into a single category.

---

### 3.3 Pathological Myopia (`MYA`)

- **Original RFMiD Label**: Column `MYA` (Myopia).
- **Original ODIR Data**:
  - Patient column `M` (Myopia).
  - Eye keywords: `pathological myopia`, `myopia retinopathy`, `myopic retinopathy`, `myopic maculopathy`.
- **Unified Label**: `MYA`
- **Annotation Granularity**: Image-level.
- **Evidence Supporting Mapping**: High myopia causes distinct posterior pole fundus changes (chorioretinal atrophy, tilted disc, staphyloma) recognizable on fundus photography.
- **Filtering Rules**:
  - Keywords matching myopia retinopathy/pathological myopia $\rightarrow y_{\text{MYA}} = 1, m_{\text{MYA}} = 1$.
  - Keyword `normal fundus` $\rightarrow y_{\text{MYA}} = 0, m_{\text{MYA}} = 1$.
  - Other abnormal eyes $\rightarrow y_{\text{MYA}} = -1, m_{\text{MYA}} = 0$.
- **Confidence**: **High (92%)**.
- **Limitations**: Simple refractive myopia without retinal degenerative changes may not show visible fundus abnormalities; ODIR keywords focus on pathological/retinopathy manifestations.

---

### 3.4 Drusen (`DN`)

- **Original RFMiD Label**: Column `DN` (Drusen).
- **Original ODIR Data**: Eye keywords containing `drusen`.
- **Unified Label**: `DN`
- **Annotation Granularity**: Image-level.
- **Evidence Supporting Mapping**: Drusen appear as pale yellow discrete deposits under the sensory retina. Both datasets annotate drusen as an independent anatomical feature.
- **Filtering Rules**:
  - Keyword contains `drusen` $\rightarrow y_{\text{DN}} = 1, m_{\text{DN}} = 1$.
  - Keyword `normal fundus` $\rightarrow y_{\text{DN}} = 0, m_{\text{DN}} = 1$.
  - Other abnormal eyes $\rightarrow y_{\text{DN}} = -1, m_{\text{DN}} = 0$.
- **Confidence**: **High (90%)**.
- **Limitations**: In RFMiD, early drusen is also tagged as `EDN`. Unified `DN` captures all classic drusen.

---

### 3.5 Epiretinal Membrane (`ERM`)

- **Original RFMiD Label**: Column `ERM`.
- **Original ODIR Data**: Eye keywords `epiretinal membrane`, `macular epiretinal membrane`, `epiretinal membrane over the macula`.
- **Unified Label**: `ERM`
- **Annotation Granularity**: Image-level.
- **Evidence Supporting Mapping**: ERM manifests as a glistening or reflective cellophane-like sheet over the macula with vascular tortuosity or macular pucker.
- **Filtering Rules**:
  - Keyword contains `epiretinal membrane` $\rightarrow y_{\text{ERM}} = 1, m_{\text{ERM}} = 1$.
  - Keyword contains `suspected macular epimacular membrane` $\rightarrow y_{\text{ERM}} = -1, m_{\text{ERM}} = 0$.
  - Keyword `normal fundus` $\rightarrow y_{\text{ERM}} = 0, m_{\text{ERM}} = 1$.
  - Other abnormal eyes $\rightarrow y_{\text{ERM}} = -1, m_{\text{ERM}} = 0$.
- **Confidence**: **High (93%)**.
- **Limitations**: Mild cellophane maculopathy can be subtle on non-OCT fundus photography.

---

### 3.6 Branch Retinal Vein Occlusion (`BRVO`)

- **Original RFMiD Label**: Column `BRVO`.
- **Original ODIR Data**: Eye keywords `branch retinal vein occlusion`, `old branch retinal vein occlusion`.
- **Unified Label**: `BRVO`
- **Annotation Granularity**: Image-level.
- **Evidence Supporting Mapping**: Sectoral retinal hemorrhages and cotton wool spots following the distribution of an obstructed branch vein.
- **Filtering Rules**:
  - Keyword contains `branch retinal vein occlusion` $\rightarrow y_{\text{BRVO}} = 1, m_{\text{BRVO}} = 1$.
  - Keyword `normal fundus` $\rightarrow y_{\text{BRVO}} = 0, m_{\text{BRVO}} = 1$.
  - Other abnormal eyes $\rightarrow y_{\text{BRVO}} = -1, m_{\text{BRVO}} = 0$.
- **Confidence**: **High (95%)**.
- **Limitations**: Both acute and old/quiescent BRVO are included.

---

### 3.7 Laser Scars (`LS`)

- **Original RFMiD Label**: Column `LS` (Laser Scars).
- **Original ODIR Data**: Eye keywords `laser spot`, `post retinal laser surgery`, `post laser photocoagulation`, `fundus laser photocoagulation spots`.
- **Unified Label**: `LS`
- **Annotation Granularity**: Image-level.
- **Evidence Supporting Mapping**: Circular, atrophic spots with hyperpigmented borders resulting from panretinal or focal photocoagulation. Highly distinctive artificial fundus feature.
- **Filtering Rules**:
  - Keyword contains laser terms $\rightarrow y_{\text{LS}} = 1, m_{\text{LS}} = 1$.
  - Keyword `normal fundus` $\rightarrow y_{\text{LS}} = 0, m_{\text{LS}} = 1$.
  - Other abnormal eyes $\rightarrow y_{\text{LS}} = -1, m_{\text{LS}} = 0$.
- **Confidence**: **Very High (98%)**.
- **Limitations**: None; distinctive morphological signature.

---

### 3.8 Optic Disc Cupping & Glaucoma (`ODC_GLAUCOMA`)

- **Original RFMiD Label**: Column `ODC` (Optic Disc Cupping).
- **Original ODIR Data**: Eye keywords `glaucoma`, `suspected glaucoma`.
- **Unified Label**: `ODC_GLAUCOMA`
- **Annotation Granularity**: Image-level.
- **Evidence Supporting Mapping**: ODC measures structural cup-to-disc ratio enlargement, the direct anatomic manifestation of glaucomatous optic nerve head damage.
- **Filtering Rules**:
  - RFMiD: `ODC == 1` $\rightarrow 1$, `ODC == 0` $\rightarrow 0$.
  - ODIR: Keyword `glaucoma` $\rightarrow 1$; `suspected glaucoma` $\rightarrow -1$ (masked); `normal fundus` $\rightarrow 0$.
  - Other abnormal eyes $\rightarrow -1$.
- **Confidence**: **Moderate (80%)**.
- **Limitations**: Physiological large cupping without functional glaucoma loss exists; conversely early glaucoma with normal cup is possible. Documented as a surrogate mapping.

---

## 4. Mathematical Formulation of Masked Multi-Label Loss

For an input fundus image $x_i$, let $\hat{z}_i \in \mathbb{R}^C$ denote the model's raw output logits for $C$ classes, and $\hat{p}_{i, c} = \sigma(\hat{z}_{i, c})$ denote the predicted probability.

The ground truth vector is $y_i \in \{-1, 0, 1\}^C$, and the binary mask is $m_i \in \{0, 1\}^C$:
$$
m_{i, c} = \begin{cases} 
1 & \text{if } y_{i, c} \in \{0, 1\} \\
0 & \text{if } y_{i, c} = -1 
\end{cases}
$$

The **Masked Binary Cross-Entropy Loss with Logits** for sample $i$ is:
$$
\mathcal{L}(x_i, y_i, m_i) = \frac{\sum_{c=1}^C m_{i, c} \cdot \left[ -y_{i, c} \log \sigma(\hat{z}_{i, c}) - (1 - y_{i, c}) \log (1 - \sigma(\hat{z}_{i, c})) \right]}{\max\left(1, \sum_{c=1}^C m_{i, c}\right)}
$$

To prevent positive class starvation on severely imbalanced classes, positive class weights $w_c = \frac{N_{\text{neg}, c}}{N_{\text{pos}, c}}$ can be optionally applied to positive terms.
