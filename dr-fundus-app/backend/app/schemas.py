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
    dr_result: Optional[DRPrediction] = None

class SampleImageInfo(BaseModel):
    id: str
    filename: str
    name: str
