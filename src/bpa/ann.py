"""ANN model for maximum spreading ratio β_max.

Implements Eq. (9) from page 9 of Pariwandh (2026) with exact coefficients
provided in the review prompt.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass

logger = logging.getLogger(__name__)

ANN_INPUT_RANGES = {
    'Re': (9.0, 15860.0),
    'We': (1.1, 2055.0),
    'theta_rad': (0.10, 2.83),
    'ra_nm': (1.3, 6200.0),
}

LEGACY_BLIND_TEST_TABLE = [
    {'model': 'ANN (Eq. 9)', 'r2': 0.996, 'mse': 0.004},
    {'model': 'Madejski', 'r2': 0.918, 'mse': 0.086},
    {'model': 'Pasandideh-Fard', 'r2': 0.927, 'mse': 0.079},
    {'model': 'Jones', 'r2': 0.901, 'mse': 0.097},
    {'model': 'Collings', 'r2': 0.874, 'mse': 0.124},
    {'model': 'Chandra & Avedisian', 'r2': 0.842, 'mse': 0.156},
    {'model': 'Mao', 'r2': 0.887, 'mse': 0.115},
]


def _normalize(x: float, xmin: float, xmax: float) -> float:
    """Normalize to [-1, 1] using x̄ = 2*(x-xmin)/(xmax-xmin)-1."""
    return 2.0 * (x - xmin) / (xmax - xmin) - 1.0


def _tansig(u: float) -> float:
    """Transfer function form used in Eq. (9)."""
    return 2.0 / (1.0 + math.exp(-2.0 * u)) - 1.0


def predict_beta_max(Re: float, We: float, theta_rad: float, ra_nm: float) -> float:
    """Predict maximum spreading ratio β_max.

    Implements Eq. (9) from page 9 of Pariwandh (2026):
    Bloodstain Pattern Analysis: A Multidisciplinary Review of Fluid Dynamics,
    Machine Learning, and Image Processing Approaches.

    Args:
        Re: Reynolds number.
        We: Weber number.
        theta_rad: Impact angle in radians.
        ra_nm: Surface roughness (Ra) in nanometers.

    Returns:
        Predicted β_max.
    """
    re_n = _normalize(Re, *ANN_INPUT_RANGES['Re'])
    we_n = _normalize(We, *ANN_INPUT_RANGES['We'])
    th_n = _normalize(theta_rad, *ANN_INPUT_RANGES['theta_rad'])
    ra_n = _normalize(ra_nm, *ANN_INPUT_RANGES['ra_nm'])

    h1 = _tansig(-4.994 * re_n + 3.162 * we_n + 8.644 * ra_n + 3.432 * th_n + 8.834)
    h2 = _tansig(-1.432 * re_n + 0.205 * we_n - 2.603 * ra_n - 1.433 * th_n + 3.759)
    h3 = _tansig(-2.762 * re_n + 2.216 * we_n + 8.644 * ra_n + 5.613 * th_n + 6.711)
    h4 = _tansig(-0.921 * re_n - 0.436 * we_n - 0.049 * ra_n - 0.003 * th_n - 2.442)

    beta_max = (0.3601 * h1 - 2.0401 * h2 - 0.4037 * h3 - 4.3533 * h4) - 2.4024
    logger.debug('Predicted beta_max=%s for inputs Re=%s We=%s theta=%s ra=%s', beta_max, Re, We, theta_rad, ra_nm)
    return beta_max


def ovat_sensitivity(base_re: float, base_we: float, base_theta: float, base_ra: float, delta: float = 0.1) -> dict[str, float]:
    """One-variable-at-a-time sensitivity around a baseline point."""

    baseline = predict_beta_max(base_re, base_we, base_theta, base_ra)
    effects: dict[str, float] = {}
    variables = {
        'Re': (base_re, ANN_INPUT_RANGES['Re']),
        'We': (base_we, ANN_INPUT_RANGES['We']),
        'theta_rad': (base_theta, ANN_INPUT_RANGES['theta_rad']),
        'ra_nm': (base_ra, ANN_INPUT_RANGES['ra_nm']),
    }
    for key, (value, limits) in variables.items():
        span = limits[1] - limits[0]
        shifted = min(limits[1], max(limits[0], value + delta * span))
        args = {
            'Re': base_re,
            'We': base_we,
            'theta_rad': base_theta,
            'ra_nm': base_ra,
        }
        args[key] = shifted
        effects[key] = abs(predict_beta_max(**args) - baseline)

    return effects
