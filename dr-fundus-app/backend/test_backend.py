import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.gate import FundusGate
from app.classifier import DRClassifier

print("--- 1. Testing FundusGate ---")
gate = FundusGate()
sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
sample_files = sorted(f for f in os.listdir(sample_dir) if f.endswith(".jpg"))
assert sample_files, "no sample images"
test_img_path = os.path.join(sample_dir, sample_files[0])
img = Image.open(test_img_path).convert("RGB")
is_fundus, conf = gate.predict(img)
print(f"Sample fundus test ({sample_files[0]}): is_fundus={is_fundus}, confidence={conf:.4f}")
assert is_fundus, "Fundus sample should be accepted by gate!"
dummy_img = Image.new("RGB", (224, 224), color=(255, 0, 0))
is_fundus_dummy, conf_dummy = gate.predict(dummy_img)
print(f"Red dummy image test: is_fundus={is_fundus_dummy}, confidence={conf_dummy:.4f}")
assert not is_fundus_dummy, "Solid red image should be rejected by gate!"

print("--- 2. Testing DRClassifier (Model B v3) ---")
classifier = DRClassifier()
assert classifier.ready, classifier.load_error
assert [b.key for b in classifier.branches] == ["vit3", "effb4", "e_twohead"]
for name in sample_files:
    path = os.path.join(sample_dir, name)
    with open(path, "rb") as handle:
        raw = handle.read()
    _, branch_probs, ens = classifier.predict_probs(Image.open(path), raw_bytes=raw)
    for key, probs in branch_probs.items():
        assert probs.shape == (6,) and abs(float(probs.sum()) - 1.0) < 1e-4 and probs.min() >= 0, (name, key, probs)
    assert abs(float(ens.sum()) - 1.0) < 1e-4
    print(f"{name:18s} ens=" + " ".join(f"{v:.3f}" for v in ens))

res = classifier.predict(img, raw_bytes=open(test_img_path, "rb").read())
primary = res["dr_result"]
print(f"Ensemble stage {primary['stage']} ({primary['badge']}), confidence={primary['confidence']:.4f}")
assert primary["stage"] in range(6)
assert len(primary["probabilities"]) == 6
assert primary["heatmap_base64"].startswith("data:image/jpeg;base64,")
assert len(res["dr_branches"]) == 3
for branch in res["dr_branches"]:
    assert branch["heatmap_base64"].startswith("data:image/jpeg;base64,"), branch["branch"]
    assert branch["stage"] in range(6)
assert res["dr_resnet"] is None
# The fallback path (decoded PIL image, no file bytes) must give nearly the same probabilities.
_, _, ens_pil = classifier.predict_probs(img)
_, _, ens_raw = classifier.predict_probs(img, raw_bytes=open(test_img_path, "rb").read())
print("max |PIL path - bytes path| =", float(np.abs(ens_pil - ens_raw).max()))
print("All backend tests PASSED successfully!")
