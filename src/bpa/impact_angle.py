"""Impact-angle estimation models following Joris et al. (2014)."""

from __future__ import annotations

import math

IMPACT_ANGLE_COMPARISON_TABLE = [
    {'method': 'Ellipse (inverse-sine)', 'rmse_deg': 4.8, 'within_2deg_percent': 38.0},
    {'method': 'ABSM polynomial (3rd order)', 'rmse_deg': 1.9, 'within_2deg_percent': 84.0},
]


def traditional_impact_angle_deg(minor_axis: float, major_axis: float) -> float:
    """Traditional angle from ellipse fitting: alpha = asin(minor/major)."""
    ratio = min(1.0, max(0.0, minor_axis / major_axis))
    return math.degrees(math.asin(ratio))


def polynomial_impact_angle_deg(s: float) -> float:
    """ABSM polynomial from p.15: alpha(s)=-0.05s^3 +0.85s^2 -8.46s +30.2."""
    return -0.05 * s**3 + 0.85 * s**2 - 8.46 * s + 30.2
