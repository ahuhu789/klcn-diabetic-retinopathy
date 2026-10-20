"""Ben Graham 512 preprocessing for Model B (v3).

This reproduces the training cache built by the private Kaggle kernel
nguynhuythanh/klcn-retinal-6class-bengraham512-cache (bg_worker.py):

1. Decode with OpenCV. If the long edge is > 4000 px the file is read with
   IMREAD_REDUCED_COLOR_4, if > 2000 px with IMREAD_REDUCED_COLOR_2; if the
   reduced image is still > 2000 px it is resized by the same factor with
   INTER_AREA. BGR is converted to RGB.
2. Crop rows/columns whose gray value is <= 10 (tol 10).
3. cv2.resize to 512 x 512 (default INTER_LINEAR).
4. 4 * image - 4 * GaussianBlur(sigma=20) + 128.
5. Pixels outside a circle of radius 0.95 * min(cx, cy) are set to 128.
6. Saved as JPEG quality 92 with PIL. We do the same encode/decode round trip
   so the model sees the same JPEG artefacts as in training.

Each branch then resizes the 512 image to its own input size with
torchvision Resize((s, s)) on the PIL image, exactly as in train.py.
The gate (Model A) still sees the original RGB image.
"""

import io

import numpy as np
from PIL import Image

CACHE_SIZE = 512
SIGMA_X = 20.0
JPEG_QUALITY = 92
CROP_TOL = 10


def _cv2():
    import cv2

    return cv2


def decode_like_cache(raw_bytes):
    """Decode raw file bytes the way the cache worker read files from disk."""
    cv2 = _cv2()
    buf = np.frombuffer(raw_bytes, dtype=np.uint8)
    # Header size via PIL, like _header_size() in the cache worker.
    with Image.open(io.BytesIO(raw_bytes)) as probe:
        width, height = probe.size
    long_edge = max(height, width)
    factor = 4 if long_edge > 4000 else (2 if long_edge > 2000 else 1)
    flag = cv2.IMREAD_COLOR
    if factor == 2:
        flag = cv2.IMREAD_REDUCED_COLOR_2
    elif factor == 4:
        flag = cv2.IMREAD_REDUCED_COLOR_4
    img = cv2.imdecode(buf, flag)
    if img is None:
        raise ValueError("OpenCV could not decode the image")
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    if factor > 1 and max(img.shape[:2]) > 2000:
        img = cv2.resize(img, (max(1, img.shape[1] // factor), max(1, img.shape[0] // factor)), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def reduce_like_cache(image_rgb):
    """Fallback when only a decoded RGB array is available (no file bytes)."""
    cv2 = _cv2()
    image = np.asarray(image_rgb)
    long_edge = max(image.shape[:2])
    factor = 4 if long_edge > 4000 else (2 if long_edge > 2000 else 1)
    if factor > 1:
        image = cv2.resize(image, (max(1, image.shape[1] // factor), max(1, image.shape[0] // factor)), interpolation=cv2.INTER_AREA)
    return image


def crop_image_from_gray(image, tol=CROP_TOL):
    cv2 = _cv2()
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mask = gray > tol
    if not np.any(mask):
        return image
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    rmin, rmax, cmin, cmax = int(rows[0]), int(rows[-1]), int(cols[0]), int(cols[-1])
    if rmax > rmin and cmax > cmin:
        return image[rmin : rmax + 1, cmin : cmax + 1]
    return image


def ben_graham_uint8(image_rgb, target_size=CACHE_SIZE, sigma_x=SIGMA_X, tol=CROP_TOL):
    cv2 = _cv2()
    image = np.asarray(image_rgb)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Ben Graham expects an RGB image")
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    image = crop_image_from_gray(image, tol)
    if image.shape[0] < 2 or image.shape[1] < 2:
        raise ValueError("Ben Graham crop produced an empty image")
    resized = cv2.resize(image, (int(target_size), int(target_size)))
    enhanced = cv2.addWeighted(resized, 4, cv2.GaussianBlur(resized, (0, 0), float(sigma_x)), -4, 128)
    enhanced = np.array(enhanced, copy=True)
    out_h, out_w = enhanced.shape[:2]
    center_x, center_y = out_w // 2, out_h // 2
    radius = int(min(center_x, center_y) * 0.95)
    circle = np.zeros((out_h, out_w), dtype=np.uint8)
    cv2.circle(circle, (center_x, center_y), radius, 255, -1)
    enhanced[circle == 0] = 128
    return enhanced


def jpeg_roundtrip(image_uint8, quality=JPEG_QUALITY):
    buffer = io.BytesIO()
    Image.fromarray(image_uint8).save(buffer, format="JPEG", quality=int(quality))
    buffer.seek(0)
    with Image.open(buffer) as im:
        return im.convert("RGB")


def cache512_from_bytes(raw_bytes):
    """Raw upload bytes -> PIL RGB 512 image identical in recipe to the training cache."""
    return jpeg_roundtrip(ben_graham_uint8(decode_like_cache(raw_bytes)))


def cache512_from_pil(image_pil):
    """Decoded PIL image -> PIL RGB 512 (used when no raw bytes are available)."""
    rgb = reduce_like_cache(np.asarray(image_pil.convert("RGB")))
    return jpeg_roundtrip(ben_graham_uint8(rgb))
