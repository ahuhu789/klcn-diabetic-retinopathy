import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image

from typing import List, Optional, Dict, Any
from app.schemas import PredictionResponse, DRPrediction, SampleImageInfo
from app.gate import FundusGate
from app.classifier import DRClassifier

app = FastAPI(
    title="Fundus Gate & Diabetic Retinopathy API",
    description="Model A fundus gate plus a 6-class ensemble ViT-B/16-384 v3 + EfficientNet-B4-448 v3 + EfficientNet-B4-448 two-head",
    version="3.0.0"
)

# CORS configuration.
# The API is public (no auth, no cookies), so the default allows every origin
# (Vercel production + *.vercel.app previews, localhost dev, Flutter web).
# Set CORS_ORIGINS="https://a.example,https://b.example" to restrict it.
_cors_env = os.environ.get("CORS_ORIGINS", "*").strip()
_cors_origins = ["*"] if _cors_env in ("", "*") else [o.strip() for o in _cors_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=None if _cors_origins == ["*"] else r"https://.*\.vercel\.app|http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400,
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")

# Global model singletons with thread-safe / lazy loading
gate = None
classifier = None

def get_gate():
    global gate
    if gate is None:
        print("Initializing Fundus Gate model (Model A)...", flush=True)
        gate = FundusGate()
    return gate

def get_classifier():
    global classifier
    if classifier is None:
        print("Initializing 6-class DR ensemble (Model B)...", flush=True)
        classifier = DRClassifier()
    return classifier

@app.on_event("startup")
def startup_event():
    print("Pre-loading models on application startup...", flush=True)
    get_gate()
    get_classifier()
    print("Startup finished.", flush=True)

@app.get("/api/health")
def health_check():
    g = get_gate()
    c = get_classifier()
    ready = bool(c is not None and c.ready)
    return {
        "status": "healthy" if ready else "degraded",
        "gate_loaded": g is not None,
        "classifier_loaded": ready,
        "num_classes": 6,
        "model_b_version": "v3",
        "ensemble_weights": c.weights if c else None,
        "ensemble_vit_weight": (c.weights.get("vit3") if c else None),
        "decode": c.decode if c else None,
        "branches": [
            {"key": b.key, "label": b.label, "arch": b.arch, "img_size": b.img_size,
             "weight": b.weight, "checkpoint": b.checkpoint}
            for b in (c.branches if c else [])
        ],
        "classifier_error": None if ready else (c.load_error if c else "classifier unavailable"),
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

    current_status = {
        "model_a": "ready" if gate_inst is not None else "unavailable",
        "model_b": "ready" if (classifier_inst is not None and classifier_inst.ready) else "unavailable",
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
            clinical_disclaimer=official_disclaimer
        )

    dr_data = None
    dr_err = None
    if classifier_inst is not None and classifier_inst.ready:
        try:
            dr_data = classifier_inst.predict(image, raw_bytes=contents)
        except Exception as exc:
            dr_err = f"Không thể hoàn tất phân loại 6 lớp (Model B): {exc}"
    else:
        detail = classifier_inst.load_error if classifier_inst is not None else ""
        dr_err = detail or "Mô hình 6 lớp (Model B) chưa được nạp."

    total_elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return PredictionResponse(
        is_fundus=True,
        fundus_confidence=round(fundus_conf, 4),
        threshold=gate_inst.threshold,
        processing_time_ms=total_elapsed_ms,
        model_status=current_status,
        message=(
            "Ảnh đạt chuẩn đáy mắt ({:.2f}%). Đã chạy ensemble 6 lớp {}.".format(
                fundus_conf * 100, classifier_inst.ensemble_label()
            )
            if dr_data
            else "Ảnh đạt chuẩn đáy mắt ({:.2f}%), nhưng Model B không trả được kết quả. {}".format(
                fundus_conf * 100, dr_err or ""
            )
        ),
        dr_result=DRPrediction(**dr_data["dr_result"]) if (dr_data and dr_data.get("dr_result")) else None,
        dr_branches=[DRPrediction(**b) for b in dr_data["dr_branches"]] if (dr_data and dr_data.get("dr_branches")) else None,
        dr_vit=DRPrediction(**dr_data["dr_vit"]) if (dr_data and dr_data.get("dr_vit")) else None,
        dr_effb4=DRPrediction(**dr_data["dr_effb4"]) if (dr_data and dr_data.get("dr_effb4")) else None,
        dr_twohead=DRPrediction(**dr_data["dr_twohead"]) if (dr_data and dr_data.get("dr_twohead")) else None,
        dr_resnet=None,
        ensemble_weights=classifier_inst.weights if dr_data else None,
        dr_error=dr_err,
        clinical_disclaimer=official_disclaimer
    )

# Tự động mount giao diện React (nếu đã build dist)
from fastapi.staticfiles import StaticFiles
FRONTEND_DIST = os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
else:
    # API-only deployment (e.g. Hugging Face Space): answer "/" with a small index.
    @app.get("/")
    def root_index():
        return {
            "service": app.title,
            "version": app.version,
            "endpoints": ["/api/health", "/api/samples", "/api/samples/{filename}", "/api/predict", "/docs"],
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

