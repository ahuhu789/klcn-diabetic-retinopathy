from typing import Optional, Dict
from pydantic import BaseModel


class DRPrediction(BaseModel):
    model_used: str
    stage: int
    stage_name: str
    badge: str
    confidence: float
    description: str
    advice: str
    benchmark_note: str
    probabilities: Dict[str, float]
    heatmap_base64: Optional[str] = None


class PredictionResponse(BaseModel):
    is_fundus: bool
    fundus_confidence: float
    threshold: float = 0.965
    message: str
    processing_time_ms: Optional[float] = None
    model_status: Optional[Dict[str, str]] = None
    dr_resnet: Optional[DRPrediction] = None
    dr_vit: Optional[DRPrediction] = None
    dr_result: Optional[DRPrediction] = None
    dr_error: Optional[str] = None
    clinical_disclaimer: Optional[str] = None


class SampleImageInfo(BaseModel):
    id: str
    filename: str
    name: str
    category: Optional[str] = "Khác"
    tag: Optional[str] = None
    badge_color: Optional[str] = "blue"
    description: Optional[str] = None
    url: Optional[str] = None
