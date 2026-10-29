// "v2 + val-tuned decode" (hier_ext) for the Lite student, identical to
// kg/v4_distill/eval/decode_ext.py decode():
//   q = p with q[1] *= w1, renormalised;  g = argmax(q[0:5]) (first index on ties);
//   class 5 if q[5] > (g == 0 ? t5n : t5), else g.
export const LITE_DECODE = Object.freeze({ family: 'hier_ext', w1: 1.5, t5: 0.45, t5n: 0.75 });

export function reweight(p, w1 = LITE_DECODE.w1) {
  const q = p.map(Number); q[1] *= w1;
  const s = q.reduce((a, b) => a + b, 0);
  return q.map((v) => v / s);
}

export function decodeExt(p, rec = LITE_DECODE) {
  if (!p || p.length !== 6) throw new Error('expected 6 class probabilities');
  const q = reweight(p, rec.w1 ?? 1.0);
  let g = 0;
  for (let i = 1; i < 5; i++) if (q[i] > q[g]) g = i;
  const thr = g === 0 ? (rec.t5n ?? rec.t5) : rec.t5;
  return { stage: q[5] > thr ? 5 : g, q };
}
