// End-to-end parity of the web Lite path in node: same JS preprocessing + decode as the
// browser (frontend/src/lite/*.js), ONNX fp32 student via onnxruntime-node, compared with
// python_reference.py output (ref.json and the saved *.input.npy tensors).
// usage: node node_parity.mjs STUDENT.onnx GATE.onnx ref.json img1 [img2 ...]
import fs from 'node:fs';
import path from 'node:path';
import ort from 'onnxruntime-node';
import sharp from 'sharp';
import { studentInputs, gateInput } from '../frontend/src/lite/preprocess.js';
import { decodeExt } from '../frontend/src/lite/decode.js';

const [studentPath, gatePath, refPath, ...imgs] = process.argv.slice(2);
const ref = JSON.parse(fs.readFileSync(refPath, 'utf8'));

async function decodeRgb(buf) {
  const { data, info } = await sharp(buf).removeAlpha().toColourspace('srgb').raw().toBuffer({ resolveWithObject: true });
  return { data: new Uint8Array(data), width: info.width, height: info.height };
}
async function jpegRoundtrip(img) {
  const jpg = await sharp(Buffer.from(img.data), { raw: { width: img.width, height: img.height, channels: 3 } })
    .jpeg({ quality: 92, chromaSubsampling: '4:2:0' }).toBuffer();
  return decodeRgb(jpg);
}
function readNpy(file) {
  const b = fs.readFileSync(file); const hl = b.readUInt16LE(8);
  return new Float32Array(b.buffer.slice(b.byteOffset + 10 + hl, b.byteOffset + b.length));
}

const s = await ort.InferenceSession.create(studentPath);
const g = await ort.InferenceSession.create(gatePath);
let agree = 0; const rows = [];
for (const f of imgs) {
  const name = path.basename(f); const r = ref.images.find((x) => x.file === name);
  const img = await decodeRgb(fs.readFileSync(f));
  const { input, inputFlipped } = await studentInputs(img, jpegRoundtrip);
  const run = async (x) => (await s.run({ input: new ort.Tensor('float32', x, [1, 3, 448, 448]) })).probs.data;
  const a = await run(input), b = await run(inputFlipped);
  const p = Array.from(a, (v, i) => (v + b[i]) / 2);
  const { stage } = decodeExt(p);
  const gname = g.inputNames[0];
  const gp = (await g.run({ [gname]: new ort.Tensor('float32', gateInput(img), [1, 224, 224, 3]) }))[g.outputNames[0]].data[0];
  let inDiff = NaN;
  const npy = refPath + '.' + name + '.input.npy';
  if (fs.existsSync(npy)) { const x = readNpy(npy); let d = 0; for (let i = 0; i < x.length; i++) d += Math.abs(x[i] - input[i]); inDiff = d / x.length; }
  const maxP = Math.max(...p.map((v, i) => Math.abs(v - r.probs[i])));
  const ok = stage === r.cls; agree += ok;
  rows.push({ file: name, py: r.cls, js: stage, ok, max_abs_prob: +maxP.toFixed(4), mean_abs_input: +inDiff.toFixed(4), gate_py: +r.gate.toFixed(4), gate_js: +gp.toFixed(4) });
}
console.table(rows);
console.log(`class agreement ${agree}/${imgs.length}`);
fs.writeFileSync(refPath.replace(/\.json$/, '') + '.node_parity.json', JSON.stringify({ agree, n: imgs.length, rows }, null, 1));
process.exit(agree === imgs.length ? 0 : 1);
