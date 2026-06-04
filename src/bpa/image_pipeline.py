"""Image-processing pipeline for bloodstain feature extraction.

Implements the steps summarized on pp.22-24 of Pariwandh (2026):
background subtraction, thresholding, morphology, 8-connectivity labeling,
local and global feature extraction.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import ndimage as ndi
from skimage import exposure, filters, measure, morphology
from skimage.color import rgb2gray
from skimage.draw import ellipse


@dataclass
class LocalFeature:
    label: int
    area: float
    impact_angle_deg: float
    convex_hull_irregularity: float
    tail_to_body_ratio: float
    inscribed_circle_irregularity: float


def _to_gray(image: np.ndarray) -> np.ndarray:
    if image.ndim == 3:
        return rgb2gray(image)
    return image.astype(float)


def background_subtraction(image: np.ndarray, background: np.ndarray | None = None) -> np.ndarray:
    gray = _to_gray(image)
    if background is None:
        background = np.median(gray) * np.ones_like(gray)
    subtracted = gray - _to_gray(background)
    subtracted = exposure.rescale_intensity(subtracted, out_range=(0.0, 1.0))
    return subtracted


def segment(image: np.ndarray, method: str = 'otsu') -> np.ndarray:
    threshold = filters.threshold_otsu(image) if method == 'otsu' else filters.threshold_triangle(image)
    return image > threshold


def remove_tails(mask: np.ndarray, radius: int = 1) -> np.ndarray:
    selem = morphology.disk(radius)
    cleaned = morphology.binary_erosion(mask, selem)
    cleaned = morphology.binary_dilation(cleaned, selem)
    cleaned = morphology.remove_small_objects(cleaned, 3)
    return cleaned


def label_8_connected(mask: np.ndarray) -> np.ndarray:
    return measure.label(mask.astype(np.uint8), connectivity=2)


def _inscribed_radius(component_mask: np.ndarray) -> float:
    dist = ndi.distance_transform_edt(component_mask)
    return float(np.max(dist))


def extract_local_features(labeled: np.ndarray) -> list[LocalFeature]:
    features: list[LocalFeature] = []
    for region in measure.regionprops(labeled):
        if region.major_axis_length <= 0:
            continue
        ratio = min(1.0, max(0.0, region.minor_axis_length / region.major_axis_length))
        angle_deg = math.degrees(math.asin(ratio))
        convex_hull_irregularity = (region.convex_area - region.area) / max(region.convex_area, 1.0)

        minr, minc, maxr, maxc = region.bbox
        bbox_area = float((maxr - minr) * (maxc - minc))
        tail_to_body_ratio = max(0.0, (bbox_area - region.area) / max(region.area, 1.0))

        comp = region.image.astype(bool)
        radius = _inscribed_radius(comp)
        circle_area = math.pi * radius * radius if radius > 0 else 1.0
        inscribed_irregularity = abs(region.area - circle_area) / max(region.area, 1.0)

        features.append(
            LocalFeature(
                label=region.label,
                area=float(region.area),
                impact_angle_deg=angle_deg,
                convex_hull_irregularity=float(convex_hull_irregularity),
                tail_to_body_ratio=float(tail_to_body_ratio),
                inscribed_circle_irregularity=float(inscribed_irregularity),
            )
        )
    return features


def extract_global_features(labeled: np.ndarray, pixel_to_cm: float = 0.1) -> dict[str, float | list[float]]:
    regions = [r for r in measure.regionprops(labeled) if r.area > 0]
    if not regions:
        return {
            'linearity_r2': 0.0,
            'gamma_angles_deg': [],
            'convex_hull_circularity': 0.0,
            'element_density_per_cm2': 0.0,
        }

    centroids = np.array([r.centroid[::-1] for r in regions])
    x = centroids[:, 0]
    y = centroids[:, 1]
    coeffs = np.polyfit(x, y, 3)
    y_hat = np.polyval(coeffs, x)
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else 1.0

    gamma_angles = [float((np.degrees(r.orientation) + 180.0) % 180.0) for r in regions]

    all_mask = labeled > 0
    hull = morphology.convex_hull_image(all_mask)
    hull_area = float(np.sum(hull))
    hull_perimeter = float(measure.perimeter(hull, neighborhood=8))
    circularity = (4 * math.pi * hull_area) / (hull_perimeter**2) if hull_perimeter > 0 else 0.0

    h, w = labeled.shape
    area_cm2 = (h * pixel_to_cm) * (w * pixel_to_cm)
    density = len(regions) / area_cm2 if area_cm2 > 0 else 0.0

    return {
        'linearity_r2': r2,
        'gamma_angles_deg': gamma_angles,
        'convex_hull_circularity': float(circularity),
        'element_density_per_cm2': float(density),
    }


def analyze_pattern(image: np.ndarray, background: np.ndarray | None = None) -> dict[str, Any]:
    sub = background_subtraction(image, background)
    seg = segment(sub, method='otsu')
    cleaned = remove_tails(seg)
    labeled = label_8_connected(cleaned)
    local = extract_local_features(labeled)
    global_features = extract_global_features(labeled)

    angles = [f.impact_angle_deg for f in local]
    elliptical = [f for f in local if 35 <= f.impact_angle_deg <= 65]

    return {
        'count': len(local),
        'elliptical_percent': 100.0 * len(elliptical) / len(local) if local else 0.0,
        'mean_angle_deg': float(np.mean(angles)) if angles else 0.0,
        'std_angle_deg': float(np.std(angles)) if angles else 0.0,
        'local_features': local,
        'global_features': global_features,
        'labels': labeled,
    }


def generate_synthetic_pattern(seed: int = 42, shape: tuple[int, int] = (640, 640), n_elements: int = 420) -> np.ndarray:
    """Generate synthetic bloodstain-like ellipses for notebook demonstrations."""
    rng = np.random.default_rng(seed)
    image = np.zeros(shape, dtype=float)
    cols = int(np.ceil(np.sqrt(n_elements)))
    rows = int(np.ceil(n_elements / cols))
    ys = np.linspace(20, shape[0] - 20, rows)
    xs = np.linspace(20, shape[1] - 20, cols)

    placed = 0
    for cy in ys:
        for cx in xs:
            if placed >= n_elements:
                break
            maj = rng.uniform(4, 8)
            minr = max(1, maj * np.sin(np.deg2rad(rng.normal(48.0, 17.3))))
            rr, cc = ellipse(
                int(cy),
                int(cx),
                minr,
                maj,
                rotation=float(rng.uniform(0, np.pi)),
                shape=shape,
            )
            image[rr, cc] = 1.0
            placed += 1
        if placed >= n_elements:
            break

    return image
