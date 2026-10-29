"""Python reference for the Lite (student) path, used by the JS/Dart parity checks.

Mirrors /workspace/kg/v4_distill/export/export_torch_onnx.py exactly:
raw bytes -> app/preprocess.cache512_from_bytes (Ben Graham 512 + JPEG q92 round trip)
-> torchvision Resize((448,448)) -> ToTensor -> ImageNet Normalize -> ONNX fp32 student,
flip TTA (mean of x and hflip(x)) -> 6 probs -> hier_ext decode {w1 1.5, t5 0.45, t5n 0.75}.
Gate: PIL RGB resize 224 bilinear, float [0,255] NHWC -> fundus_gate.onnx.

usage: python python_reference.py STUDENT.onnx GATE.onnx OUT.json img1 [img2 ...]
"""
import io, json, os, sys
import numpy as np
from PIL import Image
from torchvision import transforms
import onnxruntime as ort

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))
from app.preprocess import cache512_from_bytes  # noqa: E402

DECODE = {"w1": 1.5, "t5": 0.45, "t5n": 0.75}
MEAN = [0.485, 0.456, 0.406]; STD = [0.229, 0.224, 0.225]


def decode(p, rec=DECODE):
    """Same as kg/v4_distill/eval/decode_ext.py decode() for a single vector."""
    q = np.asarray(p, dtype=np.float64).copy(); q[1] *= rec["w1"]; q = q / q.sum()
    g = int(np.argmax(q[:5])); thr = rec["t5n"] if g == 0 else rec["t5"]
    return (5 if q[5] > thr else g), q


def main():
    student, gate, out = sys.argv[1:4]
    s = ort.InferenceSession(student, providers=["CPUExecutionProvider"])
    gs = ort.InferenceSession(gate, providers=["CPUExecutionProvider"])
    tf = transforms.Compose([transforms.Resize((448, 448)), transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
    rows = []
    for f in sys.argv[4:]:
        raw = open(f, "rb").read()
        x = tf(cache512_from_bytes(raw)).unsqueeze(0).numpy()
        np.save(out + "." + os.path.basename(f) + ".input.npy", x)
        p = (s.run(None, {"input": x})[0] + s.run(None, {"input": np.ascontiguousarray(x[:, :, :, ::-1])})[0])[0] / 2
        cls, q = decode(p)
        gi = np.asarray(Image.open(io.BytesIO(raw)).convert("RGB").resize((224, 224), Image.BILINEAR), dtype=np.float32)[None]
        gp = float(gs.run(None, {gs.get_inputs()[0].name: gi})[0].reshape(-1)[0])
        rows.append(dict(file=os.path.basename(f), probs=[float(v) for v in p], q=[float(v) for v in q], cls=cls, gate=gp))
        print(rows[-1]["file"], cls, np.round(p, 4).tolist(), "gate %.4f" % gp)
    # decode unit vectors (edge cases around w1 / t5 / t5n)
    rng = np.random.default_rng(0)
    vecs = [[0.5, 0.1, 0.1, 0.1, 0.1, 0.1], [0.30, 0.25, 0.1, 0.05, 0.0, 0.30], [0.2, 0.15, 0.1, 0.0, 0.0, 0.55],
            [0.1, 0.1, 0.1, 0.1, 0.1, 0.5], [0.3, 0.21, 0.0, 0.0, 0.0, 0.49], [0.15, 0.05, 0.0, 0.0, 0.0, 0.8],
            [0.2, 0.0, 0.0, 0.0, 0.0, 0.8], [0.4, 0.3, 0.3, 0.0, 0.0, 0.0]]
    vecs += [list(v) for v in rng.dirichlet(np.ones(6) * 0.5, 40)]
    dec = [dict(p=[float(x) for x in v], cls=decode(v)[0], q=[float(x) for x in decode(v)[1]]) for v in vecs]
    json.dump(dict(decode=DECODE, images=rows, decode_cases=dec), open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
