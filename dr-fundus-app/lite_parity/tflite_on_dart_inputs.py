"""Run the TFLite fp16 student on the NHWC tensors written by the Dart parity test
(dr_fundus_mobile/test/lite_preprocess_parity_test.dart) and compare decoded classes
with python_reference.py.  usage: python tflite_on_dart_inputs.py MODEL.tflite DIR [ref.json]"""
import json, os, sys
import numpy as np
try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    import tensorflow as tf
    Interpreter = tf.lite.Interpreter

model, d = sys.argv[1], sys.argv[2]
ref = json.load(open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(d, "ref.json")))
it = Interpreter(model_path=model); it.allocate_tensors()
ii, oo = it.get_input_details()[0]["index"], it.get_output_details()[0]["index"]

def run(x):
    it.set_tensor(ii, x.reshape(1, 448, 448, 3)); it.invoke(); return it.get_tensor(oo)[0].astype(np.float64)

def decode(p, w1=1.5, t5=0.45, t5n=0.75):
    q = p.copy(); q[1] *= w1; q /= q.sum(); g = int(np.argmax(q[:5]))
    return 5 if q[5] > (t5n if g == 0 else t5) else g

agree, rows = 0, []
for r in ref["images"]:
    f = os.path.join(d, "dart.%s.nhwc.f32" % r["file"])
    if not os.path.exists(f): continue
    a = run(np.fromfile(f, np.float32)); b = run(np.fromfile(os.path.join(d, "dart.%s.flip.nhwc.f32" % r["file"]), np.float32))
    p = (a + b) / 2; c = decode(p); agree += c == r["cls"]
    rows.append(dict(file=r["file"], py=r["cls"], dart_tflite=c, max_abs_prob=round(float(np.abs(p - r["probs"]).max()), 4)))
    print(rows[-1])
print("class agreement %d/%d" % (agree, len(rows)))
json.dump(dict(agree=agree, n=len(rows), rows=rows), open(os.path.join(d, "dart_tflite_parity.json"), "w"), indent=1)
