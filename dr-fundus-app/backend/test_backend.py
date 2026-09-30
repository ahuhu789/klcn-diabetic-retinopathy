import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.gate import FundusGate
from app.classifier import DRClassifier

print("--- 1. Testing FundusGate ---")
gate = FundusGate()
sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
sample_files = [f for f in os.listdir(sample_dir) if f.endswith(".jpg")]
if sample_files:
    test_img_path = os.path.join(sample_dir, sample_files[0])
    img = Image.open(test_img_path)
    is_fundus, conf = gate.predict(img)
    print(f"Sample fundus test ({sample_files[0]}): is_fundus={is_fundus}, confidence={conf:.4f}")
    assert is_fundus, "Fundus sample should be accepted by gate!"

    # Test non-fundus dummy image (pure white noise / solid black)
    dummy_img = Image.new("RGB", (224, 224), color=(255, 0, 0))
    is_fundus_dummy, conf_dummy = gate.predict(dummy_img)
    print(f"Red dummy image test: is_fundus={is_fundus_dummy}, confidence={conf_dummy:.4f}")
    assert not is_fundus_dummy, "Solid red image should be rejected by gate!"

print("--- 2. Testing DRClassifier ---")
classifier = DRClassifier()
res = classifier.predict(img)
print(f"DR Diagnosis Result: Stage {res['stage']} ({res['badge']}), Confidence={res['confidence']:.4f}")
print(f"Heatmap base64 length: {len(res['heatmap_base64'])}")
print("All backend tests PASSED successfully!")
