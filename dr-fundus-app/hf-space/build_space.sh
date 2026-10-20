#!/usr/bin/env bash
# Assemble the Hugging Face Space build dir from the backend + the v3 checkpoints.
# Usage: build_space.sh OUT_DIR CKPT_ROOT   (checkpoints are NOT in git)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$HERE/../backend"
OUT="${1:?out dir}"; CKPT="${2:?ckpt root with vit/ effb4/ e/}"
rm -rf "$OUT"; mkdir -p "$OUT/models"
cp "$HERE/README.md" "$HERE/Dockerfile" "$HERE/requirements.txt" "$HERE/.gitattributes" "$OUT/"
printf '__pycache__/\n*.py[cod]\n' > "$OUT/.gitignore"
cp -r "$BACKEND/app" "$OUT/app" && find "$OUT/app" -name __pycache__ -prune -exec rm -rf {} +
cp -r "$BACKEND/samples" "$OUT/samples"
cp "$BACKEND"/models/{model_b_locked.json,ensemble_weight_search_v3.csv,decode_v3.csv,fundus_gate.tflite} "$OUT/models/"
cp "$CKPT/vit/vitb16_384_best.pth" "$CKPT/effb4/effb4_448_best.pth" "$CKPT/e/effb4_448_twohead_best.pth" "$OUT/models/"
(cd "$OUT/models" && sha256sum *.pth)
# Free Space storage cap is 1 GB: store large weights as fp16 (see half_checkpoints.py).
PY="${PYTHON:-python3}"
"$PY" "$HERE/half_checkpoints.py" "$OUT/models"
(cd "$OUT/models" && sha256sum *.pth)
