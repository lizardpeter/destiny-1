import numpy as np
import pytest

from tools.d1_tower_family_e_animated_layer import exact_float32_weights


def test_exact_float32_weights_preserve_u8_over_255_without_renormalization():
    raw = np.array([
        [255, 0, 0, 0],
        [128, 64, 32, 31],
        [85, 85, 85, 0],
        [1, 1, 1, 252],
    ], dtype=np.uint8)

    got = exact_float32_weights(raw)
    expected = (raw.astype(np.float32) / np.float32(255.0)).astype('<f4')

    # The portable representation is the direct float32 encoding of each retail
    # U8 lane.  Do not alter those components to make a later sum exactly 1.0.
    assert np.array_equal(got.view(np.uint32), expected.view(np.uint32))
    assert np.all(np.sum(raw.astype(np.uint16), axis=1, dtype=np.uint16) == 255)

    sums = np.sum(got, axis=1, dtype=np.float32)
    assert sums[0] == np.float32(1.0)
    assert sums[1] == np.nextafter(np.float32(1.0), np.float32(2.0))
    assert float(sums[1] - np.float32(1.0)) == pytest.approx(1.1920928955078125e-07)


def test_exact_float32_weights_rejects_non_255_source_sum():
    raw = np.array([[128, 64, 32, 30]], dtype=np.uint8)
    with pytest.raises(ValueError, match='raw U8 weight sum drift'):
        exact_float32_weights(raw)


def test_exact_float32_weights_requires_four_lanes():
    raw = np.array([[255, 0, 0]], dtype=np.uint8)
    with pytest.raises(ValueError, match='Nx4'):
        exact_float32_weights(raw)
