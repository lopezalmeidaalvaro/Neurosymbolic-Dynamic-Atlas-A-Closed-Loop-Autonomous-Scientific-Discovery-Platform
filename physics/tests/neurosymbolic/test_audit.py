import numpy as np

from neurosymbolic.audit import linear_cka


def test_linear_cka_random_activations_is_bounded():
    rng = np.random.default_rng(123)
    x = rng.normal(size=(64, 8))
    y = rng.normal(size=(64, 12))

    value = linear_cka(x, y)

    assert 0.0 <= value <= 1.0
