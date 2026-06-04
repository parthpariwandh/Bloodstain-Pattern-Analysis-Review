"""Dimensionless-number and physics helper utilities for BPA."""

from __future__ import annotations

import math


def weber_number(rho: float, velocity: float, diameter: float, surface_tension: float) -> float:
    """Compute Weber number We = rho*U^2*D/sigma."""
    return rho * velocity * velocity * diameter / surface_tension


def reynolds_number(rho: float, velocity: float, diameter: float, viscosity: float) -> float:
    """Compute Reynolds number Re = rho*U*D/mu."""
    return rho * velocity * diameter / viscosity


def ohnesorge_number(reynolds: float, weber: float) -> float:
    """Compute Oh = sqrt(We)/Re."""
    return math.sqrt(weber) / reynolds


def impact_angle_balthazard(width: float, length: float) -> float:
    """Classical impact angle approximation alpha = arcsin(W/L) in radians."""
    ratio = min(1.0, max(0.0, width / length))
    return math.asin(ratio)
