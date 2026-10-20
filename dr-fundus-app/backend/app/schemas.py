from typing import Any, Dict, List, Optional

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
    # v3: which branch produced this result ("ensemble", "vit3", "effb4", "e_twohead"),
    # its ensemble weight and the decode that turned the probabilities into a class.
    branch: Optional[str] = None
    weight: Optional[float] = None
    decode: Optional[Dict[str, Any]] = None


class PredictionResponse(BaseModel):
    is_fundus: bool
    fundus_confidence: float
    threshold: float = 0.965
    message: str
    processing_time_ms: Optional[float] = None
    model_status: Optional[Dict[str, str]] = None
    # Reported result: 3-model ensemble with the VAL-locked decode.
    dr_result: Optional[DRPrediction] = None
    # Branches of the ensemble, in the order of model_b_locked.json.
    dr_branches: Optional[List[DRPrediction]] = None
    dr_vit: Optional[DRPrediction] = None
    dr_effb4: Optional[DRPrediction] = None
    dr_twohead: Optional[DRPrediction] = None
    # Deprecated: the v2 ResNet-50 branch was removed. Always null; kept so old clients still parse.
    dr_resnet: Optional[DRPrediction] = None
    ensemble_weights: Optional[Dict[str, float]] = None
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
