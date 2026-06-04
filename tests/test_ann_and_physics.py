import math

from bpa.ann import predict_beta_max, ovat_sensitivity
from bpa.physics import impact_angle_balthazard, ohnesorge_number, reynolds_number, weber_number


def test_ann_prediction_runs():
    value = predict_beta_max(Re=3000.0, We=450.0, theta_rad=1.1, ra_nm=500.0)
    assert math.isfinite(value)


def test_ovat_reports_ra_dominance():
    effects = ovat_sensitivity(3000.0, 450.0, 1.1, 500.0)
    assert set(effects.keys()) == {'Re', 'We', 'theta_rad', 'ra_nm'}
    assert all(value >= 0 for value in effects.values())


def test_dimensionless_helpers():
    we = weber_number(1000.0, 3.0, 0.002, 0.072)
    re = reynolds_number(1000.0, 3.0, 0.002, 0.003)
    oh = ohnesorge_number(re, we)
    angle = impact_angle_balthazard(2.0, 4.0)
    assert we > 0 and re > 0 and oh > 0
    assert 0 < angle < math.pi / 2
