"""
Model C Adapter for dr-fundus-app Backend
Provides a decoupled interface to Model C (Multi-Source Single-Image Retinal Disease Classification).
Loads strictly from verified E2 checkpoint. Demo mode and random initialization are disabled.
"""

import os
import sys
from PIL import Image

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from model_c.inference import RetinalDiseaseInference, DEFAULT_CHECKPOINT

class ModelCAdapter:
    """
    Adapter singleton wrapping Model C for seamless, decoupled integration with dr-fundus-app.
    Guarantees independent execution from Model A and Model B.
    """
    def __init__(self, checkpoint_path=None):
        ckpt = checkpoint_path or DEFAULT_CHECKPOINT
        if not os.path.exists(ckpt):
            raise FileNotFoundError(
                f"[CRITICAL ERROR] Model C checkpoint missing at '{ckpt}'. "
                "Production inference requires the verified trained checkpoint."
            )
        self.engine = RetinalDiseaseInference(checkpoint_path=ckpt)
        self.model_version = "1.0.0-E2-Harmonized"

    def predict(self, image: Image.Image) -> dict:
        """
        Accepts: PIL RGB Fundus Image
        Returns: Standardized Model C dictionary
        """
        return self.engine.predict(image)

