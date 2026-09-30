import os
import numpy as np
from PIL import Image

# Import LiteRT / TFLite interpreter
try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    try:
        from tflite_runtime.interpreter import Interpreter
    except ImportError:
        import tensorflow as tf
        Interpreter = tf.lite.Interpreter

class FundusGate:
    """
    MobileNetV3-Small binary classification gate.
    Outputs probability in [0, 1].
    Threshold: 0.965
    Input range: [0, 255] float32, size: (224, 224, 3)
    """
    def __init__(self, model_path: str = None, threshold: float = 0.965):
        self.threshold = threshold
        if model_path is None:
            # Default path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "fundus_gate.tflite")
        
        self.model_path = model_path
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Fundus Gate model file not found: {self.model_path}")
            
        self.interpreter = Interpreter(model_path=self.model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, image_pil: Image.Image) -> tuple[bool, float]:
        """
        Evaluate if the PIL image is a valid fundus photograph.
        Returns: (is_fundus, probability)
        """
        # Convert to RGB and resize to 224x224
        img = image_pil.convert("RGB").resize((224, 224), Image.Resampling.BILINEAR)
        
        # MobileNetV3 expects float32 in range [0, 255]
        img_array = np.array(img, dtype=np.float32)
        input_tensor = np.expand_dims(img_array, axis=0)

        # Set tensor & invoke
        self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)
        self.interpreter.invoke()
        
        # Get output probability
        output = self.interpreter.get_tensor(self.output_details[0]['index'])
        prob = float(output[0][0])
        
        is_fundus = bool(prob >= self.threshold)
        return is_fundus, prob
