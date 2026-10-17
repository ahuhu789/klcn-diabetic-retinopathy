"""Ben Graham crop used by the training cache. Model B only.

The gate still sees the original RGB image. This matches cache_kernel:
crop pixels darker than 10, resize to 256 with linear interpolation, then
4 * image - 4 * GaussianBlur(sigma=10) + 128, and fill outside a circle of
radius 0.95 * min(cx, cy) with 128.
"""

import numpy as np


def ben_graham_uint8(image_rgb, target_size=256, sigma_x=10, tol=10):
    import cv2

    image = np.asarray(image_rgb)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Ben Graham expects an RGB image")
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mask = gray > tol
    if np.any(mask):
        rows = np.where(mask.any(axis=1))[0]
        cols = np.where(mask.any(axis=0))[0]
        rmin, rmax = int(rows[0]), int(rows[-1])
        cmin, cmax = int(cols[0]), int(cols[-1])
        if rmax > rmin and cmax > cmin:
            image = image[rmin : rmax + 1, cmin : cmax + 1]
    if image.shape[0] < 2 or image.shape[1] < 2:
        raise ValueError("Ben Graham crop produced an empty image")

    resized = cv2.resize(image, (int(target_size), int(target_size)))
    blurred = cv2.GaussianBlur(resized, (0, 0), float(sigma_x))
    enhanced = cv2.addWeighted(resized, 4, blurred, -4, 128)
    enhanced = np.array(enhanced, copy=True)
    out_h, out_w = enhanced.shape[:2]
    center_x, center_y = out_w // 2, out_h // 2
    radius = int(min(center_x, center_y) * 0.95)
    circle = np.zeros((out_h, out_w), dtype=np.uint8)
    cv2.circle(circle, (center_x, center_y), radius, 255, -1)
    enhanced[circle == 0] = 128
    return enhanced
