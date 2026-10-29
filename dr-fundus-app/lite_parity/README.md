# Lite mode parity checks

The Lite mode runs the distilled student (EfficientNet-B4-448, two heads, distilled from the
3-model ensemble; TEST SCORE 0.6820 vs ensemble 0.6861) on the device:

| App | Runtime | Model file |
|-----|---------|------------|
| Web (`frontend/src/lite/`) | onnxruntime-web (wasm) | ONNX fp32, 70.2 MB, lazy-loaded from `https://huggingface.co/slyviee/klcn-dr-student-lite` and kept in the browser Cache API |
| Mobile (`dr_fundus_mobile/lib/core/lite/`) | tflite_flutter | TFLite fp16, 35.2 MB, bundled asset `assets/models/student_effb4_twohead_448_fp16.tflite` |

Both mirror `kg/v4_distill/export/export_torch_onnx.py` and `eval/decode_ext.py`:

1. Model A gate on the original image (PIL resize 224 bilinear, [0,255], threshold 0.965).
2. `backend/app/preprocess.py`: crop gray > 10, cv2 resize 512, `4*img - 4*GaussianBlur(σ=20) + 128`,
   circle mask r = 0.95·256, JPEG q92 round trip (OpenCV fixed-point resize and bit-exact Gaussian are reproduced exactly).
3. torchvision `Resize((448,448))` (PIL bilinear with antialias, fixed point), ImageNet mean/std.
4. Flip TTA: mean of the probabilities of x and hflip(x). Output = 6 probs `[(1-p5)·softmax(head_b), p5]`.
5. Decode hier_ext `{w1: 1.5, t5: 0.45, t5n: 0.75}`: q = p with q1 ×= 1.5, renormalised;
   g = argmax(q0..q4); class 5 if q5 > (g == 0 ? 0.75 : 0.45), else g. Displayed probabilities are q.

## Run

```bash
# 1) Python reference (needs numpy, pillow, opencv-python-headless, torchvision, onnxruntime)
python python_reference.py STUDENT.onnx ../../dr_fundus_mobile/assets/models/fundus_gate.onnx /tmp/lite/ref.json img1.jpg img2.jpg ...
# 2) Web path in node (same JS modules as the browser) + decode unit test
npm install
node decode_parity.mjs /tmp/lite/ref.json
node node_parity.mjs STUDENT.onnx ../../dr_fundus_mobile/assets/models/fundus_gate.onnx /tmp/lite/ref.json img1.jpg ...
# 3) Dart path: decode test (uses test/fixtures/lite_ref.json) and preprocessing parity
cd ../../dr_fundus_mobile && flutter test test/lite_decode_test.dart
LITE_PARITY_DIR=/tmp/lite LITE_PARITY_IMAGES="img1.jpg img2.jpg" flutter test test/lite_preprocess_parity_test.dart
python ../dr-fundus-app/lite_parity/tflite_on_dart_inputs.py student_fp16.tflite /tmp/lite
```

## Results (2026-10-30, 16 images: 10 app samples + 6 EyePACS)

* Decode: 64/64 cases identical in JS and Dart (`ref.json`).
* Web (node, onnxruntime-node, ONNX fp32): 16/16 classes identical. Input tensor is bit-identical to
  Python for images ≤ 2000 px; for larger images (IDRiD 4288 px) OpenCV's DCT-scaled JPEG decode
  (IMREAD_REDUCED_COLOR_2/4) is approximated by a box average (mean |Δinput| ≈ 0.02).
* Web in headless Chrome (vite preview): 6/6 tested images same class as Python.
* Dart preprocessing + TFLite fp16: 16/16 classes identical (mean |Δinput| 0.018–0.036; the pure-Dart
  JPEG codec differs slightly from libjpeg).
