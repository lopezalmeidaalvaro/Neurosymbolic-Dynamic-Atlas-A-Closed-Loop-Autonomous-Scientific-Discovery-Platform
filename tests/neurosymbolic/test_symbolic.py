import numpy as np

from neurosymbolic.symbolic import recover_sindy_coefficients


def test_sindy_recovers_known_linear_coefficients():
    rng = np.random.default_rng(123)
    x = rng.normal(size=(200, 2))
    dxdt = 2.0 * x[:, 0] - 3.0 * x[:, 1]

    coefficients = recover_sindy_coefficients(
        x, dxdt, feature_names=["x", "y"], threshold=1e-8
    )

    assert abs(coefficients["x"] - 2.0) < 1e-8
    assert abs(coefficients["y"] + 3.0) < 1e-8
    assert abs(coefficients["1"]) < 1e-8
