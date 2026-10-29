// Lite mode: the distilled EfficientNet-B4-448 two-head student (+ the MobileNetV3 fundus gate)
// running fully in the browser with onnxruntime-web (wasm). Weights are not in git; they are
// downloaded once from a Hugging Face model repo (URLs configurable) and kept in the Cache API.
import { CLASSES, SEVERITY_INFO } from './classes.js';
import { LITE_DECODE, decodeExt } from './decode.js';
import { rgbaToRgb, studentInputs, gateInput } from './preprocess.js';

const HF_BASE = 'https://huggingface.co/slyviee/klcn-dr-student-lite/resolve/main';
export const LITE_MODEL_URL = (import.meta.env.VITE_LITE_MODEL_URL || `${HF_BASE}/student_effb4_twohead_448_fp32.onnx`).trim();
export const LITE_GATE_URL = (import.meta.env.VITE_LITE_GATE_URL || `${HF_BASE}/fundus_gate.onnx`).trim();
const CACHE_NAME = 'klcn-lite-models-v1';
export const GATE_THRESHOLD = 0.965;
export const LITE_TEST_NOTE = 'Mô hình Lite (student EfficientNet-B4-448 hai đầu ra, chưng cất từ ensemble) chạy ngay trên trình duyệt. TEST SCORE 0.6820 so với ensemble 0.6861 (API).';

let ortPromise = null;
let sessions = null;

async function loadOrt() {
  if (!ortPromise) {
    ortPromise = import('onnxruntime-web').then((ort) => {
      // The ORT wasm binary is bundled by Vite (dist/assets/*.wasm) and served by Vercel.
      ort.env.wasm.numThreads = (typeof crossOriginIsolated !== 'undefined' && crossOriginIsolated)
        ? Math.min(4, navigator.hardwareConcurrency || 1) : 1;
      return ort;
    });
  }
  return ortPromise;
}

/** fetch with progress, served from the Cache API after the first download. */
async function fetchModel(url, onProgress) {
  let cache = null;
  try { cache = await caches.open(CACHE_NAME); } catch { cache = null; }
  if (cache) {
    const hit = await cache.match(url);
    if (hit) { onProgress?.(1, true); return new Uint8Array(await hit.arrayBuffer()); }
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Không tải được mô hình Lite (${res.status}) từ ${url}`);
  const total = Number(res.headers.get('content-length')) || 0;
  const reader = res.body.getReader();
  const chunks = []; let got = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value); got += value.length;
    if (total) onProgress?.(got / total, false);
  }
  const buf = new Uint8Array(got); let off = 0;
  for (const c of chunks) { buf.set(c, off); off += c.length; }
  if (cache) {
    try { await cache.put(url, new Response(buf, { headers: { 'content-type': 'application/octet-stream' } })); } catch { /* quota */ }
  }
  onProgress?.(1, false);
  return buf;
}

export async function isLiteCached() {
  try {
    const cache = await caches.open(CACHE_NAME);
    return Boolean(await cache.match(LITE_MODEL_URL)) && Boolean(await cache.match(LITE_GATE_URL));
  } catch { return false; }
}

/** onProgress({stage: 'gate'|'student'|'init', fraction, cached}) */
export async function loadLiteModels(onProgress) {
  if (sessions) return sessions;
  const ort = await loadOrt();
  const gateBuf = await fetchModel(LITE_GATE_URL, (f, cached) => onProgress?.({ stage: 'gate', fraction: f, cached }));
  const studentBuf = await fetchModel(LITE_MODEL_URL, (f, cached) => onProgress?.({ stage: 'student', fraction: f, cached }));
  onProgress?.({ stage: 'init', fraction: 1 });
  const opts = { executionProviders: ['wasm'], graphOptimizationLevel: 'all' };
  const gate = await ort.InferenceSession.create(gateBuf, opts);
  const student = await ort.InferenceSession.create(studentBuf, opts);
  sessions = { ort, gate, student };
  return sessions;
}

async function fileToRgb(file) {
  // createImageBitmap applies EXIF orientation like cv2.imdecode does.
  const bmp = await createImageBitmap(file, { colorSpaceConversion: 'none', premultiplyAlpha: 'none' });
  const canvas = new OffscreenCanvas(bmp.width, bmp.height);
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(bmp, 0, 0);
  const { data } = ctx.getImageData(0, 0, bmp.width, bmp.height);
  bmp.close?.();
  return rgbaToRgb(data, canvas.width, canvas.height);
}

/** JPEG q92 encode/decode round trip (the training cache was stored as JPEG q92). */
async function jpegRoundtrip(img) {
  const canvas = new OffscreenCanvas(img.width, img.height);
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  const rgba = new Uint8ClampedArray(img.width * img.height * 4);
  for (let i = 0; i < img.width * img.height; i++) {
    rgba[i * 4] = img.data[i * 3]; rgba[i * 4 + 1] = img.data[i * 3 + 1]; rgba[i * 4 + 2] = img.data[i * 3 + 2]; rgba[i * 4 + 3] = 255;
  }
  ctx.putImageData(new ImageData(rgba, img.width, img.height), 0, 0);
  const blob = await canvas.convertToBlob({ type: 'image/jpeg', quality: 0.92 });
  return fileToRgb(blob);
}

function rgbToDataUrl(img) {
  const canvas = document.createElement('canvas');
  canvas.width = img.width; canvas.height = img.height;
  const rgba = new Uint8ClampedArray(img.width * img.height * 4);
  for (let i = 0; i < img.width * img.height; i++) {
    rgba[i * 4] = img.data[i * 3]; rgba[i * 4 + 1] = img.data[i * 3 + 1]; rgba[i * 4 + 2] = img.data[i * 3 + 2]; rgba[i * 4 + 3] = 255;
  }
  canvas.getContext('2d').putImageData(new ImageData(rgba, img.width, img.height), 0, 0);
  return canvas.toDataURL('image/jpeg', 0.9);
}

const tick = () => new Promise((r) => setTimeout(r, 0));

/** Runs gate + student on a File and returns an object shaped like the API PredictionResponse. */
export async function predictLite(file, onProgress) {
  const { ort, gate, student } = await loadLiteModels(onProgress);
  const t0 = performance.now();
  const img = await fileToRgb(file);
  await tick();
  const gName = gate.inputNames[0];
  const gOut = await gate.run({ [gName]: new ort.Tensor('float32', gateInput(img), [1, 224, 224, 3]) });
  const fundusConf = Number(gOut[gate.outputNames[0]].data[0]);
  const base = {
    mode: 'lite',
    threshold: GATE_THRESHOLD,
    fundus_confidence: fundusConf,
    model_status: { model_a: 'lite (trên trình duyệt)', model_b: 'lite (student EffB4-448)' },
    clinical_disclaimer: 'Kết quả từ mô hình Lite chạy trên trình duyệt chỉ hỗ trợ sàng lọc, không thay thế kết luận của bác sĩ chuyên khoa mắt.',
    dr_branches: [],
  };
  if (fundusConf < GATE_THRESHOLD) {
    return { ...base, is_fundus: false, processing_time_ms: Math.round(performance.now() - t0),
      message: `Ảnh bị từ chối: không phải ảnh đáy mắt hợp lệ (độ tin cậy ${(fundusConf * 100).toFixed(2)}% < ${(GATE_THRESHOLD * 100).toFixed(1)}%).` };
  }
  await tick();
  const { input, inputFlipped, cache512 } = await studentInputs(img, jpegRoundtrip);
  await tick();
  const sName = student.inputNames[0]; const oName = student.outputNames[0];
  const a = (await student.run({ [sName]: new ort.Tensor('float32', input, [1, 3, 448, 448]) }))[oName].data;
  const b = (await student.run({ [sName]: new ort.Tensor('float32', inputFlipped, [1, 3, 448, 448]) }))[oName].data;
  const probs = Array.from(a, (v, i) => (v + b[i]) / 2);
  const { stage, q } = decodeExt(probs);
  const info = SEVERITY_INFO[String(stage)];
  const dr = {
    model_used: 'Lite: EfficientNet-B4-448 hai đầu ra (student, ONNX trên trình duyệt)',
    stage, stage_name: info.title, badge: info.badge, description: info.description, advice: info.advice,
    confidence: Number(q[stage].toFixed(4)),
    benchmark_note: `${LITE_TEST_NOTE} | decode hier_ext w1=${LITE_DECODE.w1} t5=${LITE_DECODE.t5} t5n=${LITE_DECODE.t5n} (xác suất hiển thị đã nhân w1 lớp 1 rồi chuẩn hóa)`,
    probabilities: Object.fromEntries(CLASSES.map((c, i) => [c, Number(q[i].toFixed(4))])),
    raw_probabilities: Object.fromEntries(CLASSES.map((c, i) => [c, Number(probs[i].toFixed(4))])),
    heatmap_base64: null, branch: 'lite_student', weight: 1.0, decode: { ...LITE_DECODE },
    preprocessed_base64: rgbToDataUrl(cache512),
  };
  return { ...base, is_fundus: true, processing_time_ms: Math.round(performance.now() - t0),
    message: `Ảnh đáy mắt hợp lệ (Model A trên trình duyệt: ${(fundusConf * 100).toFixed(2)}%). Đã chạy mô hình Lite.`,
    dr_result: dr };
}
