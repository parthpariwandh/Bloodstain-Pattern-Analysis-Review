"""Probabilistic 3-D region-of-origin utilities (Attinger et al., 2019)."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class HeightPdfParams:
    z0: float
    sigma_core: float
    sigma_tail: float


def trajectory_passing_probability(distance: np.ndarray, sigma: float) -> np.ndarray:
    """Compute ψ_ik ~ exp(-d^2/(2σ^2))."""
    return np.exp(-(distance**2) / (2.0 * sigma * sigma))


def height_pdf(z: np.ndarray, params: HeightPdfParams) -> np.ndarray:
    """Compute ϕ_ik(z) with Gaussian tails around central origin height z0."""
    core = np.exp(-((z - params.z0) ** 2) / (2.0 * params.sigma_core**2))
    tails = np.exp(-((z - params.z0) ** 2) / (2.0 * params.sigma_tail**2))
    return np.where(np.abs(z - params.z0) <= params.sigma_core, core, tails)


def joint_likelihood(psi_values: list[np.ndarray], phi_values: list[np.ndarray]) -> np.ndarray:
    """Joint likelihood for multiple stains: product_i ψ_i * ϕ_i."""
    if not psi_values or not phi_values:
        raise ValueError('psi_values and phi_values must be non-empty')
    likelihood = np.ones_like(psi_values[0], dtype=float)
    for psi, phi in zip(psi_values, phi_values, strict=False):
        likelihood *= psi * phi
    total = float(np.sum(likelihood))
    return likelihood / total if total > 0 else likelihood


EXPERIMENTAL_PATTERNS = [
    {'pattern': 'HP 31', 'x0_m': 0.40, 'v_ro_m3': 0.008, 'error_cm': 6.3},
    {'pattern': 'HP 7', 'x0_m': 0.45, 'v_ro_m3': 0.014, 'error_cm': 5.5},
    {'pattern': 'HP 53', 'x0_m': 0.50, 'v_ro_m3': 0.025, 'error_cm': 7.2},
    {'pattern': 'HP 11', 'x0_m': 0.55, 'v_ro_m3': 0.039, 'error_cm': 4.9},
    {'pattern': 'HP 24', 'x0_m': 0.60, 'v_ro_m3': 0.066, 'error_cm': 8.1},
    {'pattern': 'HP 21', 'x0_m': 0.65, 'v_ro_m3': 0.101, 'error_cm': 6.8},
    {'pattern': 'C9', 'x0_m': 0.70, 'v_ro_m3': 0.154, 'error_cm': 9.4},
]


def estimate_volume_scaling_exponent() -> float:
    """Estimate exponent n in V_RO ~ x0^n for the experimental table."""
    x = np.array([row['x0_m'] for row in EXPERIMENTAL_PATTERNS])
    v = np.array([row['v_ro_m3'] for row in EXPERIMENTAL_PATTERNS])
    slope, _ = np.polyfit(np.log(x), np.log(v), 1)
    return float(slope)
