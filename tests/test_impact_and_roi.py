import numpy as np

from bpa.impact_angle import polynomial_impact_angle_deg, traditional_impact_angle_deg
from bpa.probabilistic_roi import HeightPdfParams, estimate_volume_scaling_exponent, height_pdf, trajectory_passing_probability


def test_impact_models_return_finite_values():
    assert traditional_impact_angle_deg(2.0, 4.0) > 0
    assert np.isfinite(polynomial_impact_angle_deg(10.0))


def test_probabilistic_helpers():
    d = np.array([0.0, 0.2, 0.4])
    z = np.array([0.8, 1.0, 1.2])
    psi = trajectory_passing_probability(d, sigma=0.3)
    phi = height_pdf(z, HeightPdfParams(z0=1.0, sigma_core=0.1, sigma_tail=0.25))
    assert psi[0] >= psi[-1]
    assert phi.max() <= 1.0


def test_scaling_exponent_range():
    n = estimate_volume_scaling_exponent()
    assert 5.0 <= n <= 5.8
