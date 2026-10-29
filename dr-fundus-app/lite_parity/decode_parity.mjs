// Unit test: JS decodeExt vs the Python decode on the vectors stored in ref.json (decode_cases).
import fs from 'node:fs';
import { decodeExt } from '../frontend/src/lite/decode.js';
const ref = JSON.parse(fs.readFileSync(process.argv[2] || 'ref.json', 'utf8'));
let bad = 0;
for (const c of ref.decode_cases) {
  const { stage, q } = decodeExt(c.p);
  const dq = Math.max(...q.map((v, i) => Math.abs(v - c.q[i])));
  if (stage !== c.cls || dq > 1e-9) { bad++; console.log('MISMATCH', c, stage, dq); }
}
for (const im of ref.images) if (decodeExt(im.probs).stage !== im.cls) { bad++; console.log('MISMATCH image', im.file); }
console.log(`decode cases ${ref.decode_cases.length + ref.images.length}, mismatches ${bad}`);
process.exit(bad ? 1 : 0);
