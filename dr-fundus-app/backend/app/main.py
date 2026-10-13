import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image

from typing import List, Optional, Dict, Any
from app.schemas import PredictionResponse, DRPrediction, ModelCPrediction, SampleImageInfo
from app.gate import FundusGate
from app.classifier import DRClassifier

app = FastAPI(
    title="Fundus Gate & Diabetic Retinopathy API",
    description="2-Stage Pipeline: Input Validation Gate (MobileNetV3) + DR Severity Staging (ResNet-50 + Grad-CAM)",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")

# Global model singletons with thread-safe / lazy loading
gate = None
classifier = None
model_c = None

def get_gate():
    global gate
    if gate is None:
        print("Initializing Fundus Gate model (Model A)...", flush=True)
        gate = FundusGate()
    return gate

def get_classifier():
    global classifier
    if classifier is None:
        print("Initializing DR Severity Classifier (Model B)...", flush=True)
        classifier = DRClassifier()
    return classifier

def get_model_c():
    global model_c
    if model_c is None:
        print("Initializing Multi-Source Retinal Multi-Label Classifier (Model C)...", flush=True)
        try:
            from app.model_c_adapter import ModelCAdapter
            model_c = ModelCAdapter()
            print("Model C initialized successfully!", flush=True)
        except Exception as e:
            print(f"Warning: Model C could not be initialized: {e}", flush=True)
            model_c = None
    return model_c

@app.on_event("startup")
def startup_event():
    print("Pre-loading models on application startup...", flush=True)
    get_gate()
    get_classifier()
    get_model_c()
    print("All models ready for inference!", flush=True)

@app.get("/api/health")
def health_check():
    g = get_gate()
    c = get_classifier()
    mc = get_model_c()
    return {
        "status": "healthy",
        "gate_loaded": g is not None,
        "classifier_loaded": c is not None,
        "model_c_loaded": mc is not None,
        "gate_threshold": g.threshold if g else 0.965
    }

SAMPLE_METADATA = {
    "NORMAL_001.jpg": {
        "name": "Mắt Khỏe mạnh (Bình thường)",
        "category": "Khỏe mạnh",
        "tag": "Bình thường",
        "badge_color": "emerald",
        "description": "Ảnh đáy võng mạc bình thường, không có tổn thương mạch máu, hoàng điểm và gai thị nguyên vẹn."
    },
    "ARMD_001.jpg": {
        "name": "Thoái hóa Hoàng điểm Tuổi già (AMD)",
        "category": "Bệnh võng mạc khác",
        "tag": "AMD",
        "badge_color": "amber",
        "description": "Tổn thương thoái hóa hoàng điểm, kèm Drusen và biến đổi tế bào biểu mô sắc tố võng mạc."
    },
    "GLAUCOMA_001.jpg": {
        "name": "Glaucoma / Lõm đĩa thị (ODC)",
        "category": "Bệnh võng mạc khác",
        "tag": "Glaucoma / ODC",
        "badge_color": "purple",
        "description": "Tỷ lệ lõm gai thị Cup-to-Disc mở rộng, gợi ý tổn thương teo gai thị giác do bệnh glôcôm."
    },
    "MYA_001.jpg": {
        "name": "Cận thị Bệnh lý (Pathological Myopia)",
        "category": "Bệnh võng mạc khác",
        "tag": "Cận thị (MYA)",
        "badge_color": "blue",
        "description": "Biến dạng trục nhãn cầu, thoái hóa hắc võng mạc và liềm cận thị điển hình quanh gai thị."
    },
    "BRVO_001.jpg": {
        "name": "Tắc Nhánh Tĩnh mạch Võng mạc (BRVO)",
        "category": "Bệnh võng mạc khác",
        "tag": "Tắc mạch (BRVO)",
        "badge_color": "rose",
        "description": "Xuất huyết dạng ngọn lửa và phù nề dọc theo phân nhánh tĩnh mạch thái dương bị tắc nghẽn."
    },
    "IDRiD_001.jpg": {
        "name": "Võng mạc Tiểu đường Nặng (Stage 3)",
        "category": "Đái tháo đường (DR)",
        "tag": "DR Cấp 3 (Nặng)",
        "badge_color": "red",
        "description": "Nhiều xuất huyết võng mạc sâu, xuất tiết cứng và vi phình mạch lan tỏa ở 4 góc phần tư."
    },
    "IDRiD_002.jpg": {
        "name": "Võng mạc Tiểu đường Vừa (Stage 2)",
        "category": "Đái tháo đường (DR)",
        "tag": "DR Cấp 2 (Vừa)",
        "badge_color": "orange",
        "description": "Vi phình mạch vi tuần hoàn kèm rải rác xuất tiết và xuất huyết đốm nhẹ."
    },
    "IDRiD_003.jpg": {
        "name": "Võng mạc Tiểu đường Tăng sinh (Stage 4)",
        "category": "Đái tháo đường (DR)",
        "tag": "DR Cấp 4 (Tăng sinh)",
        "badge_color": "red",
        "description": "Hình thành tân mạch võng mạc (Neovascularization), xuất huyết dịch kính nghiêm trọng."
    },
    "IDRiD_004.jpg": {
        "name": "Võng mạc Tiểu đường Nhẹ (Stage 1)",
        "category": "Đái tháo đường (DR)",
        "tag": "DR Cấp 1 (Nhẹ)",
        "badge_color": "amber",
        "description": "Giai đoạn khởi phát: chỉ xuất hiện các nốt vi phình mạch nhỏ (Microaneurysms) đơn độc."
    },
    "IDRiD_005.jpg": {
        "name": "Võng mạc Tiểu đường Tiền Tăng sinh",
        "category": "Đái tháo đường (DR)",
        "tag": "DR Nghi ngờ cao",
        "badge_color": "red",
        "description": "Tổn thương vi mạch tiến triển mạnh, thiếu máu võng mạc diện rộng."
    }
}

@app.get("/api/samples", response_model=List[SampleImageInfo])
def list_samples():
    if not os.path.exists(SAMPLES_DIR):
        return []
    samples = []
    
    # Priority order for showcase
    priority_order = [
        "NORMAL_001.jpg",
        "ARMD_001.jpg",
        "GLAUCOMA_001.jpg",
        "MYA_001.jpg",
        "BRVO_001.jpg",
        "IDRiD_001.jpg",
        "IDRiD_002.jpg",
        "IDRiD_003.jpg",
        "IDRiD_004.jpg",
        "IDRiD_005.jpg"
    ]
    
    existing_files = set(os.listdir(SAMPLES_DIR))
    ordered_files = [f for f in priority_order if f in existing_files]
    # Add any extra files not in priority order
    for f in sorted(existing_files):
        if f not in ordered_files and f.lower().endswith(('.jpg', '.jpeg', '.png')):
            ordered_files.append(f)
            
    for f in ordered_files:
        meta = SAMPLE_METADATA.get(f, {
            "name": f,
            "category": "Khác",
            "tag": "Mẫu",
            "badge_color": "blue",
            "description": "Ảnh đáy võng mạc lâm sàng."
        })
        samples.append(SampleImageInfo(
            id=f,
            filename=f,
            name=meta["name"],
            category=meta["category"],
            tag=meta["tag"],
            badge_color=meta["badge_color"],
            description=meta["description"],
            url=f"/api/samples/{f}"
        ))
    return samples

@app.get("/api/samples/{filename}")
def get_sample_image(filename: str):
    file_path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample image not found")
    return FileResponse(file_path)

import time
from PIL import Image, ImageOps

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...)):
    start_time = time.perf_counter()
    
    # 1. Validate file format
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    content_type = (file.content_type or "").lower()
    
    if not (content_type.startswith("image/") or file_ext in allowed_extensions):
        raise HTTPException(
            status_code=400, 
            detail="Tệp tải lên không hợp lệ. Vui lòng chọn tệp hình ảnh định dạng JPEG, PNG hoặc WEBP."
        )
    
    # 2. Read and validate file size (Limit: 25MB)
    MAX_FILE_SIZE = 25 * 1024 * 1024
    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Kích thước tệp vượt quá giới hạn cho phép (tối đa 25MB)."
            )
        if len(contents) == 0:
            raise HTTPException(
                status_code=400,
                detail="Tệp tải lên rỗng (0 bytes). Vui lòng chọn lại ảnh hợp lệ."
            )
        
        # 3. Open image & normalize orientation
        raw_image = Image.open(io.BytesIO(contents))
        image = ImageOps.exif_transpose(raw_image).convert("RGB")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400, 
            detail="Không thể giải mã dữ liệu hình ảnh. Tệp có thể đã bị hỏng hoặc không đúng định dạng."
        )

    # Retrieve model singletons via lazy/cached accessors
    gate_inst = get_gate()
    classifier_inst = get_classifier()
    model_c_inst = get_model_c()

    # Status tracking for models
    current_status = {
        "model_a": "ready" if gate_inst is not None else "unavailable",
        "model_b": "ready" if classifier_inst is not None else "unavailable",
        "model_c": "ready" if model_c_inst is not None else "unavailable"
    }

    # Giai doan 1: Fundus Gate (Model A: MobileNetV3)
    if gate_inst is None:
        raise HTTPException(
            status_code=503, 
            detail="Hệ thống xác thực ảnh đáy mắt (Model A) hiện không khả dụng."
        )
        
    try:
        is_fundus, fundus_conf = gate_inst.predict(image)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Đã xảy ra lỗi trong quá trình xác thực ảnh đáy mắt (Model A)."
        )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    official_disclaimer = (
        "Ứng dụng được phát triển phục vụ nghiên cứu khóa luận tốt nghiệp. "
        "Kết quả từ mô hình AI chỉ mang tính chất hỗ trợ sàng lọc và không thay thế kết luận của bác sĩ chuyên khoa mắt."
    )

    if not is_fundus:
        return PredictionResponse(
            is_fundus=False,
            fundus_confidence=round(fundus_conf, 4),
            threshold=gate_inst.threshold,
            processing_time_ms=elapsed_ms,
            model_status=current_status,
            message="Ảnh bị từ chối: Tỷ lệ nhận diện ảnh đáy mắt đạt {:.2f}%, thấp hơn ngưỡng quy định ({:.2f}%). Vui lòng tải lên ảnh chụp đáy võng mạc đạt tiêu chuẩn y khoa.".format(
                fundus_conf * 100, gate_inst.threshold * 100
            ),
            dr_result=None,
            model_c_result=None,
            clinical_disclaimer=official_disclaimer
        )

    # Giai doan 2: DR Classifier (Model B: ResNet-50 & ViT-B/16)
    dr_data = None
    dr_err = None
    if classifier_inst is not None:
        try:
            dr_data = classifier_inst.predict(image)
        except Exception as e:
            dr_err = "Không thể hoàn tất phân độ DR (Model B): Đã xảy ra sự cố nội bộ trong quá trình suy luận."
    else:
        dr_err = "Mô hình phân độ DR (Model B) chưa được nạp hoặc không khả dụng."

    # Giai doan 3: Multi-Label Retinal Classifier (Model C: E2 Harmonized)
    model_c_data = None
    model_c_err = None
    if model_c_inst is not None:
        try:
            model_c_data = model_c_inst.predict(image)
        except Exception as e:
            model_c_err = "Không thể hoàn tất sàng lọc đa bệnh lý võng mạc (Model C): Sự cố nội bộ trong quá trình suy luận."
    else:
        model_c_err = "Mô hình sàng lọc đa bệnh lý võng mạc (Model C) chưa được nạp hoặc không khả dụng."

    total_elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return PredictionResponse(
        is_fundus=True,
        fundus_confidence=round(fundus_conf, 4),
        threshold=gate.threshold,
        processing_time_ms=total_elapsed_ms,
        model_status=current_status,
        message="Ảnh đạt chuẩn đáy mắt ({:.2f}%). Đã hoàn tất phân độ DR (Model B) và sàng lọc đa bệnh lý võng mạc (Model C).".format(
            fundus_conf * 100
        ),
        dr_resnet=DRPrediction(**dr_data["dr_resnet"]) if (dr_data and dr_data.get("dr_resnet")) else None,
        dr_vit=DRPrediction(**dr_data["dr_vit"]) if (dr_data and dr_data.get("dr_vit")) else None,
        dr_result=DRPrediction(**dr_data["dr_result"]) if (dr_data and dr_data.get("dr_result")) else None,
        dr_error=dr_err,
        model_c_result=ModelCPrediction(**model_c_data) if model_c_data else None,
        model_c_error=model_c_err,
        clinical_disclaimer=official_disclaimer
    )

# Tự động mount giao diện React (nếu đã build dist)
from fastapi.staticfiles import StaticFiles
FRONTEND_DIST = os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

