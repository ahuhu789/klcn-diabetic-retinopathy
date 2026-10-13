from typing import Optional, Dict, List, Any
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

class ModelCConditionItem(BaseModel):
    code: str
    name: str
    vietnamese_desc: str
    confidence_pct: float
    probability: Optional[float] = None
    threshold: Optional[float] = None

class ModelCPrediction(BaseModel):
    model_name: str
    model_version: str
    input_type: str
    overall_disease_risk: bool
    num_detected_conditions: int
    detected_diseases: List[ModelCConditionItem]
    full_probabilities: Dict[str, Any]
    checkpoint_meta: Dict[str, Any]
    clinical_disclaimer: str

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
    model_c_result: Optional[ModelCPrediction] = None
    model_c_error: Optional[str] = None
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
