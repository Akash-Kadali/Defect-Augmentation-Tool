import cv2
import numpy as np

def paste_defect(base_img, defect_img, position, scale=1.0, angle=0):
    """
    Paste a defect with soft edges and strong center based on distance transform feathering.
    """

    if defect_img.shape[2] == 3:
        defect_img = cv2.cvtColor(defect_img, cv2.COLOR_BGR2BGRA)

    h, w = defect_img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, scale)
    transformed = cv2.warpAffine(defect_img, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    th, tw = transformed.shape[:2]

    y, x = map(int, map(round, position))
    y = np.clip(y, 0, base_img.shape[0] - th)
    x = np.clip(x, 0, base_img.shape[1] - tw)

    roi = base_img[y:y+th, x:x+tw].copy()
    defect_rgb = transformed[:, :, :3]
    alpha = transformed[:, :, 3].astype(np.float32) / 255.0

    # === Step 1: Estimate brightness
    brightness = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)[..., 2].mean()
    blend_strength = np.interp(brightness, [30, 255], [2.0, 1.1])
    feather_max = np.interp(brightness, [30, 255], [15, 6])  # falloff distance

    # === Step 2: Feather mask but keep strong center
    binary_mask = (alpha > 0.01).astype(np.uint8)
    dist = cv2.distanceTransform(binary_mask, cv2.DIST_L2, 5)
    max_dist = dist.max() or 1e-6

    # Strong center: everything inside radius gets full opacity
    center_mask = (dist >= feather_max).astype(np.float32)

    # Smooth edge: 1 at center, linearly fades to 0 at edge
    feather_edge = np.clip(dist / feather_max, 0, 1.0)
    feather_edge = np.clip(1.0 - feather_edge, 0, 1.0)

    # Combine: strong center (1.0), soft edge fade
    feather_alpha = np.maximum(center_mask, feather_edge) * alpha
    final_alpha = np.clip(feather_alpha * blend_strength, 0, 1.0)[..., None]

    # === Step 3: Blend onto ROI
    blended = (1 - final_alpha) * roi.astype(np.float32) + final_alpha * defect_rgb.astype(np.float32)
    base_img[y:y+th, x:x+tw, :3] = blended.astype(np.uint8)

    return base_img.astype(np.uint8)
