import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image

from app.schemas import PredictionResponse, DRPrediction
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

# Global model singletons
gate = None
classifier = None

@app.on_event("startup")
def startup_event():
    global gate, classifier
    print("Loading Fundus Gate model...")
    gate = FundusGate()
    print("Loading Diabetic Retinopathy Classifier...")
    classifier = DRClassifier()
    print("All models loaded successfully!")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "gate_loaded": gate is not None,
        "classifier_loaded": classifier is not None,
        "gate_threshold": gate.threshold if gate else 0.965
    }

@app.get("/api/samples")
def list_samples():
    if not os.path.exists(SAMPLES_DIR):
        return []
    samples = []
    for f in sorted(os.listdir(SAMPLES_DIR)):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            samples.append({
                "id": f,
                "filename": f,
                "url": f"/api/samples/{f}"
            })
    return samples

@app.get("/api/samples/{filename}")
def get_sample_image(filename: str):
    file_path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample image not found")
    return FileResponse(file_path)

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Tệp tải lên phải là định dạng hình ảnh (JPEG, PNG).")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể đọc hình ảnh: {str(e)}")

    # Giai doan 1: Fundus Gate (MobileNetV3)
    is_fundus, fundus_conf = gate.predict(image)

    if not is_fundus:
        return PredictionResponse(
            is_fundus=False,
            fundus_confidence=round(fundus_conf, 4),
            threshold=gate.threshold,
            message="Ảnh bị từ chối: Tỷ lệ nhận diện ảnh đáy mắt đạt {:.2f}%, thấp hơn ngưỡng quy định ({:.2f}%). Vui lòng tải lên ảnh chụp đáy võng mạc đạt tiêu chuẩn y khoa.".format(
                fundus_conf * 100, gate.threshold * 100
            ),
            dr_result=None
        )

    # Giai doan 2: DR Classifier (ResNet-50 + Grad-CAM)
    dr_data = classifier.predict(image)
    
    return PredictionResponse(
        is_fundus=True,
        fundus_confidence=round(fundus_conf, 4),
        threshold=gate.threshold,
        message="Ảnh đạt chuẩn đáy mắt ({:.2f}%). Đã hoàn tất phân độ tổn thương võng mạc đái tháo đường.".format(
            fundus_conf * 100
        ),
        dr_result=DRPrediction(**dr_data)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
