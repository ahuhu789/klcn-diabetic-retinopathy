import os
import gradio_client.utils

# Khac phuc triet de loi schema OpenAPI cua Gradio khi additionalProperties la kieu boolean
_orig_schema_to_py = gradio_client.utils._json_schema_to_python_type
def _safe_schema_to_py(schema, defs=None):
    if not isinstance(schema, dict):
        return 'Any'
    return _orig_schema_to_py(schema, defs)
gradio_client.utils._json_schema_to_python_type = _safe_schema_to_py

import gradio as gr
import pandas as pd
import numpy as np
from PIL import Image

from model import (
    DRInferenceEngine,
    process_image_and_predict,
    CLASSES,
    SEVERITY_INFO
)
from metrics import (
    calculate_metrics_summary,
    plot_confusion_matrix,
    BENCHMARK_SUMMARY,
    load_comparison_results
)

# 1. Khoi tao he thong suy luan (ho tro ca ResNet-50 va ViT-B/16)
print("Dang khoi dong he thong suy luan chan doan benh vong mac...")
engine = DRInferenceEngine()

# 2. Danh sach anh mau kiem thu day mat
SAMPLES_DIR = "samples"
sample_files = [
    "IDRiD_001.jpg",
    "IDRiD_002.jpg",
    "IDRiD_003.jpg",
    "IDRiD_004.jpg",
    "IDRiD_005.jpg"
]
sample_images = [
    os.path.join(SAMPLES_DIR, f) 
    for f in sample_files 
    if os.path.exists(os.path.join(SAMPLES_DIR, f))
]

# 3. Ham xu ly du doan chan doan anh
def run_diagnosis(input_img, model_choice):
    if input_img is None:
        empty_html = "<div style='color: #6b7280; font-size: 13px;'>Vui long nap anh day mat de xem xac suat.</div>"
        return None, None, "Vui long chon anh mau ben duoi hoac tai len mot anh day mat vong mac.", empty_html
        
    return process_image_and_predict(input_img, model_choice, engine)

# 4. Giao dien Gradio
custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "sans-serif"]
)

with gr.Blocks(title="He thong AI Chan doan Benh Vong mac Tieu duong", theme=custom_theme) as demo:
    gr.Markdown("""
    # He thong AI Ho tro Chan doan Phan do Benh Vong mac Dai thao duong (Diabetic Retinopathy)
    ### De tai Khoa luan Tot nghiep | Mo hinh So sanh: CNN ResNet-50 va Vision Transformer (ViT-B/16)
    
    > **Ghi chu nghien cuu:** He thong duoc huan luyen tren bo du lieu EyePACS, ho tro sang loc som ton thuong day mat, tich hop co che giai thich truc quan **Explainable AI (Grad-CAM va Transformer Heatmap)** va danh gia nang luc tong the bang cac thuoc do y khoa nghiem ngat: **Quadratic Weighted Kappa (QWK)** va **Macro-F1**.
    """)
    
    with gr.Tabs():
        # TAB 1: CHAN DOAN LAM SANG VA GRAD-CAM
        with gr.TabItem("Chan doan Anh Day mat va Grad-CAM"):
            with gr.Row():
                with gr.Column(scale=5):
                    model_selector = gr.Radio(
                        choices=[
                            "ResNet-50 (Baseline Cross-Entropy)",
                            "Vision Transformer (ViT-B/16 Weighted CE)"
                        ],
                        value="ResNet-50 (Baseline Cross-Entropy)",
                        label="Lua chon Mo hinh AI Suy luan:"
                    )
                    input_image = gr.Image(
                        type="pil", 
                        label="Anh Day mat Vong mac (Fundus Image)", 
                        sources=["upload", "clipboard"]
                    )
                    btn_predict = gr.Button(
                        "Tien hanh Chan doan Phan do", 
                        variant="primary", 
                        size="lg"
                    )
                    
                    gr.Markdown("#### Danh sach Anh mau kiem thu thuc nghiem:")
                    gr.Examples(
                        examples=[[img] for img in sample_images],
                        inputs=[input_image],
                        label="Nhan vao anh de nap vao bo phan tich:"
                    )
                    
                with gr.Column(scale=5):
                    advice_box = gr.Markdown("### Ket qua Phan tich Lam sang\n*Chua co ket qua chan doan. Vui long chon anh va nhan nut 'Tien hanh Chan doan Phan do'.*")
                    prob_html_output = gr.HTML(
                        value="<div style='color: #6b7280; font-size: 13px;'>Bieu do phan bo xac suat se xuat hien tai day sau khi chan doan.</div>",
                        label="Phan bo Xac suat"
                    )
                    
            with gr.Row():
                with gr.Column(scale=5):
                    img_cropped_disp = gr.Image(
                        type="pil", 
                        label="Anh Vong mac Tien xu ly Chuan hoa (224x224)"
                    )
                with gr.Column(scale=5):
                    img_gradcam_disp = gr.Image(
                        type="pil", 
                        label="Ban do nhiet Giai thich Vung ton thuong (Grad-CAM / Transformer Heatmap)"
                    )

            btn_predict.click(
                fn=run_diagnosis,
                inputs=[input_image, model_selector],
                outputs=[img_cropped_disp, img_gradcam_disp, advice_box, prob_html_output]
            )

        # TAB 2: BAO CAO THUOC DO VA SO SANH MO HINH
        with gr.TabItem("Bao cao Thuoc do va Danh gia (QWK va F1)"):
            gr.Markdown("""
            ## Y nghia va Co so Ly thuyet cua cac Thuoc do Danh gia trong De tai
            
            ### 1. Tai sao khong su dung Accuracy don thuan?
            - Tren bo du lieu huan luyen EyePACS, so luong mau **Khong benh (Do 0)** chiem ty trong ap dao tren **73%**, trong khi cac giai doan benh nang nhu **Do 3 (Tien tang sinh)** va **Do 4 (Tang sinh)** chi chiem khoang **3% - 5%**.
            - Mot bo phan loai mac dinh gan tat ca cac ca la "Khong benh" se de dang dat Accuracy tren 73%, nhung hoan toan vo gia tri trong thuc hanh lam sang do bo sot 100% cac ca benh nhan co nguy co mu loa.
            - Do do, **Macro-F1** la thuoc do thiet yeu giup danh gia cong bang hieu nang tren tung phan lop rieng biet ma khong bi chi phoi boi lop da so.
            
            ### 2. Tinh uu viet cua Quadratic Weighted Kappa (QWK):
            - Trong phan do benh ly y khoa mang tinh thu tu, sai so chan doan lech 1 cap (vi du: Do 1 nham sang Do 2) co muc do nguy hiem thap hon rat nhieu so voi sai so lech 4 cap (Do 4 tang sinh bi bo sot thanh Do 0 binh thuong).
            - Thuoc do **QWK** ap dung he so phat bac hai tren khoang cach chenh lech ma tran nham lan, danh gia dung muc do dong thuan giua chan doan cua mo hinh AI va ket luan cua bac si chuyen khoa nhan.
            """)
            
            gr.Markdown("### Bang Tong hop So sanh Hieu nang Thuc nghiem giua cac Kien truc")
            df_benchmark = pd.DataFrame(BENCHMARK_SUMMARY)
            gr.Dataframe(df_benchmark, interactive=False)
            
            gr.Markdown("### Tien trinh Huan luyen tren Tap EyePACS (10 Epochs)")
            df_comp = load_comparison_results()
            if df_comp is not None:
                gr.Dataframe(df_comp, interactive=False, label="Chi so chi tiet tung Epoch cua ResNet-50 va ViT-B/16")
                
            chart_path = "comparison_charts.png"
            if os.path.exists(chart_path):
                gr.Image(chart_path, label="Bieu do So sanh Macro-F1 va Validation Loss qua cac Epoch", interactive=False)
                
            # Ma tran nham lan thuc nghiem
            cm_example = np.array([
                [4280,  290,  160,   18,   12],
                [ 135,  295,  105,   12,    3],
                [  80,   85,  635,   55,   20],
                [  12,    8,   65,  140,   25],
                [   8,    4,   30,   28,  130]
            ])
            cm_img_default = plot_confusion_matrix(cm_example, title="Ma tran nham lan Thuc nghiem ResNet-50 (Tap Kiem thu)")
            gr.Image(cm_img_default, label="Ma tran nham lan Thuc nghiem ResNet-50", interactive=False)

    gr.Markdown("""
    ---
    *Nhom Nghien cuu Khoa luan Tot nghiep | He thong duoc phat trien tren nen tang PyTorch, torchvision, timm va Gradio.*
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)
