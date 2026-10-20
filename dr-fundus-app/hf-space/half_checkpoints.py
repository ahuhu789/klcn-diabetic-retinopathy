"""Store the large float32 weight tensors of the v3 checkpoints as float16.

Why: the free Space repo has a 1 GB storage cap (history included); the fp32
checkpoints (~486 MB) do not fit next to the older history, fp16 (~235 MB) does.
BatchNorm running stats, pos_embed / cls_token and small tensors stay float32.
load_state_dict() copies the values back into the float32 model, so inference
still runs in float32. Checked on the 52-image app-vs-Kaggle set: 52/52 identical
classes vs the fp32 checkpoints, max |dprob| 5e-4.

Usage: python half_checkpoints.py MODELS_DIR   (rewrites the .pth files in place)
"""
import os
import sys

import torch

FILES = ["vitb16_384_best.pth", "effb4_448_best.pth", "effb4_448_twohead_best.pth"]


def keep_fp32(key, tensor):
    return (not tensor.is_floating_point() or tensor.numel() < 4096
            or "running_" in key or "pos_embed" in key or "cls_token" in key)


def main(models_dir):
    for name in FILES:
        path = os.path.join(models_dir, name)
        sd = torch.load(path, map_location="cpu", weights_only=True)
        out = type(sd)((k, v if keep_fp32(k, v) else v.half()) for k, v in sd.items())
        torch.save(out, path)
        print(f"{name}: {os.path.getsize(path) / 1e6:.1f} MB")


if __name__ == "__main__":
    main(sys.argv[1])
